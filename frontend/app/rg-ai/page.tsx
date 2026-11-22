"use client";

import React, { useState, useRef, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "motion/react";
import {
  Bot,
  Globe,
  ChevronDown,
  ChevronUp,
  PanelLeftClose,
  PanelLeftOpen,
  Plus,
} from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { pageContainerVariants, snappyTransition } from "@/lib/motionTokens";
import { BrowserConnectionCard } from "@/components/browser/BrowserConnectionCard";
import {
  rgAiService,
  RequestStatusResponse,
} from "@/services/rgAiService";
import { ApiClientError } from "@/services/apiClient";
import { conversationRepository } from "@/services/conversationRepository";
import {
  ChatMessage,
  Conversation,
  ConversationSummary,
  ResponseEnvelope,
} from "@/types/rgAi";
import { ConversationSidebar } from "@/components/rg-ai/ConversationSidebar";
import { MessageList } from "@/components/rg-ai/MessageList";
import { MessageComposer } from "@/components/rg-ai/MessageComposer";
import { PromptTemplateModal } from "@/components/rg-ai/PromptTemplateModal";

export default function RgAiPage() {
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [inputValue, setInputValue] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [activeRequestId, setActiveRequestId] = useState<string | null>(null);
  const [showBrowserCard, setShowBrowserCard] = useState(false);
  const [isSidebarOpenMobile, setIsSidebarOpenMobile] = useState(false);
  const [isSidebarCollapsedDesktop, setIsSidebarCollapsedDesktop] = useState(false);
  const [isTemplateModalOpen, setIsTemplateModalOpen] = useState(false);

  const pollingRef = useRef<NodeJS.Timeout | null>(null);

  // Load conversations on mount and sanitize any stale pending messages
  useEffect(() => {
    let isMounted = true;
    (async () => {
      const list = await conversationRepository.list();
      if (!isMounted) return;
      setConversations(list);

      const sanitize = async (c: Conversation): Promise<Conversation> => {
        let changed = false;
        const messages = c.messages.map((m) => {
          if (m.status === "processing" || m.status === "queued") {
            changed = true;
            return {
              ...m,
              status: "failed" as const,
              content:
                m.content ||
                "Analysis was interrupted when the app or server restarted. Click Retry to re-run your prompt.",
              error: {
                code: "REQUEST_INTERRUPTED",
                message: "Previous request was interrupted. Please retry.",
              },
            };
          }
          return m;
        });
        if (changed) {
          const updated = { ...c, messages };
          await conversationRepository.save(updated);
          return updated;
        }
        return c;
      };

      const activeId = conversationRepository.getActiveId();
      if (activeId) {
        const conv = await conversationRepository.get(activeId);
        if (conv && isMounted) {
          const cleanConv = await sanitize(conv);
          setCurrentConversation(cleanConv);
          return;
        }
      }

      if (list.length > 0) {
        const first = await conversationRepository.get(list[0].id);
        if (first && isMounted) {
          const cleanFirst = await sanitize(first);
          setCurrentConversation(cleanFirst);
          conversationRepository.setActiveId(cleanFirst.id);
          return;
        }
      }

      const newConv = await conversationRepository.create("New Analysis");
      if (isMounted) {
        setCurrentConversation(newConv);
        const updatedList = await conversationRepository.list();
        setConversations(updatedList);
      }
    })();

    return () => {
      isMounted = false;
    };
  }, []);

  // Clean up polling interval on unmount
  useEffect(() => {
    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
        pollingRef.current = null;
      }
    };
  }, []);

  // Pre-populate input if navigated with ?prompt=...
  useEffect(() => {
    if (typeof window !== "undefined") {
      const searchParams = new URLSearchParams(window.location.search);
      const promptParam = searchParams.get("prompt");
      if (promptParam) {
        const timer = setTimeout(() => {
          setInputValue(promptParam);
        }, 0);
        return () => clearTimeout(timer);
      }
    }
  }, []);

  const handleSelectConversation = async (id: string) => {
    if (isProcessing) return;
    const conv = await conversationRepository.get(id);
    if (conv) {
      setCurrentConversation(conv);
      conversationRepository.setActiveId(conv.id);
    }
  };

  const handleNewChat = async () => {
    if (isProcessing) return;
    const newConv = await conversationRepository.create("New Analysis");
    setCurrentConversation(newConv);
    const list = await conversationRepository.list();
    setConversations(list);
    setInputValue("");
  };

  const handleRenameConversation = async (id: string, newTitle: string) => {
    await conversationRepository.rename(id, newTitle);
    const list = await conversationRepository.list();
    setConversations(list);
    if (currentConversation && currentConversation.id === id) {
      setCurrentConversation((prev) => (prev ? { ...prev, title: newTitle } : null));
    }
  };

  const handleDeleteConversation = async (id: string) => {
    await conversationRepository.delete(id);
    const list = await conversationRepository.list();
    setConversations(list);

    if (currentConversation && currentConversation.id === id) {
      if (list.length > 0) {
        const nextConv = await conversationRepository.get(list[0].id);
        setCurrentConversation(nextConv);
        conversationRepository.setActiveId(list[0].id);
      } else {
        const newConv = await conversationRepository.create("New Analysis");
        setCurrentConversation(newConv);
        setConversations(await conversationRepository.list());
      }
    }
  };

  const handleCancelActiveRequest = async (targetRequestId?: string) => {
    const rid = targetRequestId || activeRequestId;
    if (!rid) return;

    try {
      try {
        await rgAiService.cancelRequest(rid);
      } catch (err: unknown) {
        // If 404 (request not found on server, e.g. after restart), ignore as it is already gone
        const isNotFound = err instanceof ApiClientError && err.status === 404;
        if (!isNotFound) {
          console.warn("Server cancel request error:", err);
        }
      }
    } finally {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
        pollingRef.current = null;
      }
      setIsProcessing(false);
      setActiveRequestId(null);

      if (currentConversation) {
        const updatedMessages: ChatMessage[] = currentConversation.messages.map((m) =>
          m.requestId === rid || (!m.requestId && m.status === "processing")
            ? {
                ...m,
                status: "cancelled",
                content: "Analysis request was cancelled by user.",
              }
            : m
        );
        const updatedConv: Conversation = {
          ...currentConversation,
          messages: updatedMessages,
        };
        setCurrentConversation(updatedConv);
        await conversationRepository.save(updatedConv);
      }
    }
  };

  const pollRequestStatus = useCallback(
    (requestId: string, convId: string) => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
      }

      const check = async () => {
        try {
          const res: RequestStatusResponse = await rgAiService.getStatus(requestId);

          const isTerminal =
            res.status === "completed" ||
            res.status === "failed" ||
            res.status === "cancelled" ||
            res.status === "integration_unavailable";

          if (isTerminal) {
            if (pollingRef.current) {
              clearInterval(pollingRef.current);
              pollingRef.current = null;
            }
            setIsProcessing(false);
            setActiveRequestId(null);

            let finalContent = "";
            let envelope: ResponseEnvelope | null = null;

            if (res.status === "completed" && res.result) {
              // Check if result is already a canonical ResponseEnvelope
              if (res.result.type && res.result.data) {
                envelope = {
                  success: true,
                  type: String(res.result.type),
                  schema_version: String(res.result.schema_version || "1.0"),
                  request_id: requestId,
                  data: res.result.data,
                  warnings: res.result.warnings || null,
                  disclaimer:
                    res.result.disclaimer ||
                    "RG AI is an educational and market intelligence platform. All intelligence reports are algorithmic research outputs.",
                  execution_metadata:
                    (res.result.execution_metadata as Record<string, unknown>) || null,
                };
                finalContent = "Analysis successfully generated and validated.";
              } else if (res.result.content) {
                // If content is raw JSON string, attempt to parse into envelope
                try {
                  const parsed = JSON.parse(res.result.content);
                  if (parsed && typeof parsed === "object" && (parsed.type || parsed.stock_name)) {
                    envelope = {
                      success: true,
                      type: parsed.type || "stock_analysis",
                      schema_version: "1.0",
                      request_id: requestId,
                      data: parsed.data || parsed,
                      disclaimer:
                        parsed.disclaimer ||
                        "RG AI is an educational and market intelligence platform.",
                    };
                    finalContent = "Analysis verified.";
                  } else {
                    finalContent = res.result.content;
                  }
                } catch {
                  finalContent = res.result.content;
                }
              }
            } else if (res.status === "integration_unavailable") {
              finalContent =
                "Direct ChatGPT website scraping and undocumented private API execution are disabled in strict adherence to security and compliance boundaries.\n\nPlease open the Chrome Session drawer to interact directly with the Indian Stock Market GPT inside your persistent authenticated browser session.";
            } else if (res.status === "failed") {
              if (res.error?.code === "LOGIN_REQUIRED") {
                finalContent =
                  "Authentication Required: ChatGPT session is not logged in. Please open the Chrome Session drawer, log into ChatGPT, and click 'Confirm Login' before submitting analysis prompts.";
              } else if (res.error?.code === "BROWSER_UNAVAILABLE") {
                finalContent =
                  "Browser Session Offline: Managed Chrome instance is not running. Please launch the browser from the Chrome Session drawer.";
              } else {
                finalContent = `Execution Error (${res.error?.code || "FAILED"}): ${
                  res.error?.message || "Request orchestration encountered an error."
                }`;
              }
            } else if (res.status === "cancelled") {
              finalContent = "Analysis request was cancelled.";
            }

            setCurrentConversation((prev) => {
              if (!prev || prev.id !== convId) return prev;
              const updated: ChatMessage[] = prev.messages.map((m) =>
                m.requestId === requestId
                  ? {
                      ...m,
                      status: res.status,
                      content: finalContent,
                      envelope,
                      error: res.error || undefined,
                    }
                  : m
              );
              const nextConv: Conversation = { ...prev, messages: updated };
              conversationRepository.save(nextConv);
              return nextConv;
            });

            const list = await conversationRepository.list();
            setConversations(list);
          } else {
            // In-flight progress update
            setCurrentConversation((prev) => {
              if (!prev || prev.id !== convId) return prev;
              const updated: ChatMessage[] = prev.messages.map((m) =>
                m.requestId === requestId
                  ? {
                      ...m,
                      status: res.status,
                      metadata: {
                        ...m.metadata,
                        queuePosition: res.queue_position || undefined,
                      },
                    }
                  : m
              );
              return { ...prev, messages: updated };
            });
          }
        } catch (err: unknown) {
          const isNotFound =
            (err instanceof ApiClientError && err.status === 404) ||
            (err instanceof Error && err.message.toLowerCase().includes("not found"));

          if (isNotFound) {
            if (pollingRef.current) {
              clearInterval(pollingRef.current);
              pollingRef.current = null;
            }
            setIsProcessing(false);
            setActiveRequestId(null);

            setCurrentConversation((prev) => {
              if (!prev || prev.id !== convId) return prev;
              const updated: ChatMessage[] = prev.messages.map((m) =>
                m.requestId === requestId
                  ? {
                      ...m,
                      status: "failed",
                      content:
                        "Request session expired or server was restarted. Please click Retry to re-run your analysis.",
                      error: {
                        code: "REQUEST_NOT_FOUND",
                        message: "Request session was not found on the server.",
                      },
                    }
                  : m
              );
              const nextConv: Conversation = { ...prev, messages: updated };
              conversationRepository.save(nextConv);
              return nextConv;
            });

            const list = await conversationRepository.list();
            setConversations(list);
            return;
          }

          console.error("Status polling error:", err);
        }
      };

      check();
      pollingRef.current = setInterval(check, 1200);
    },
    []
  );

  const handleSendPrompt = async (textToSend?: string) => {
    const query = (textToSend || inputValue).trim();
    if (!query || isProcessing) return;

    let conv = currentConversation;
    if (!conv) {
      conv = await conversationRepository.create("New Analysis");
      setCurrentConversation(conv);
      const list = await conversationRepository.list();
      setConversations(list);
    }

    const timeLabel = new Date().toLocaleTimeString("en-IN", {
      hour: "2-digit",
      minute: "2-digit",
    });

    const userMessage: ChatMessage = {
      id: `user_${Date.now()}_${Math.random().toString(36).substring(2, 8)}`,
      sender: "user",
      content: query,
      timestamp: timeLabel,
    };

    // If conversation is brand new, auto-generate title from first prompt
    let nextTitle = conv.title;
    if (conv.messages.length === 0 || conv.title === "New Analysis") {
      nextTitle = query.slice(0, 32).trim() || "Analysis";
    }

    const optimisticConv: Conversation = {
      ...conv,
      title: nextTitle,
      messages: [...conv.messages, userMessage],
    };

    setCurrentConversation(optimisticConv);
    await conversationRepository.save(optimisticConv);
    setInputValue("");
    setIsProcessing(true);

    try {
      const submission = await rgAiService.submitPrompt(query, conv.id);
      setActiveRequestId(submission.request_id);

      const aiMessage: ChatMessage = {
        id: `ai_${Date.now()}_${Math.random().toString(36).substring(2, 8)}`,
        sender: "rg_ai",
        requestId: submission.request_id,
        status: submission.status,
        content: `Queued at position ${submission.queue_position}... waiting for execution slot.`,
        timestamp: timeLabel,
        metadata: {
          queuePosition: submission.queue_position,
        },
      };

      const withAiConv: Conversation = {
        ...optimisticConv,
        messages: [...optimisticConv.messages, aiMessage],
      };

      setCurrentConversation(withAiConv);
      await conversationRepository.save(withAiConv);
      const list = await conversationRepository.list();
      setConversations(list);

      pollRequestStatus(submission.request_id, conv.id);
    } catch (err: unknown) {
      setIsProcessing(false);
      setActiveRequestId(null);

      // Preserve user prompt in draft input if submission failed
      setInputValue(query);

      const errorMessage =
        err instanceof Error
          ? err.message
          : "Unable to enqueue analysis request. Please verify backend connection.";

      const errorMsg: ChatMessage = {
        id: `err_${Date.now()}_${Math.random().toString(36).substring(2, 8)}`,
        sender: "rg_ai",
        content: `Submission Failed: ${errorMessage}`,
        status: "failed",
        timestamp: timeLabel,
      };

      const failedConv: Conversation = {
        ...optimisticConv,
        messages: [...optimisticConv.messages, errorMsg],
      };

      setCurrentConversation(failedConv);
      await conversationRepository.save(failedConv);
    }
  };

  const handleSelectTemplate = (prompt: string) => {
    setInputValue(prompt);
  };

  return (
    <motion.div
      variants={pageContainerVariants}
      initial="hidden"
      animate="visible"
      className="mx-auto flex h-[calc(100vh-8.5rem)] max-w-7xl flex-col space-y-3"
    >
      {/* Top Header Bar */}
      <div className="flex items-center justify-between border-b border-[#E8EAE4] pb-2">
        <div className="flex items-center gap-2.5">
          {/* Mobile sidebar toggle button */}
          <button
            onClick={() => setIsSidebarOpenMobile(true)}
            className="md:hidden rounded-lg p-1.5 text-[#777D76] hover:bg-[#E8EAE4] hover:text-[#20251F] cursor-pointer"
            aria-label="Open conversation history"
          >
            <PanelLeftOpen className="h-5 w-5" />
          </button>

          {/* Desktop sidebar toggle button */}
          <button
            onClick={() => setIsSidebarCollapsedDesktop(!isSidebarCollapsedDesktop)}
            className="hidden md:inline-flex rounded-lg p-1.5 text-[#777D76] hover:bg-[#E8EAE4] hover:text-[#20251F] cursor-pointer"
            title={isSidebarCollapsedDesktop ? "Expand history" : "Collapse history"}
          >
            {isSidebarCollapsedDesktop ? (
              <PanelLeftOpen className="h-4 w-4" />
            ) : (
              <PanelLeftClose className="h-4 w-4" />
            )}
          </button>

          <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-[#176B45] text-white shadow-xs">
            <Bot className="h-4 w-4" />
          </div>

          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-sm sm:text-base font-semibold text-[#20251F] truncate max-w-[200px] sm:max-w-md">
                {currentConversation?.title || "RG AI Intelligence"}
              </h1>
              <Badge variant="accent">Phase 6 Chat</Badge>
            </div>
            <p className="hidden sm:block text-[10px] text-[#777D76]">
              Verified Indian Stock Market Intelligence • Persistent Browser Automation
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Chrome Session Drawer Trigger */}
          <Button
            size="sm"
            variant="outline"
            onClick={() => setShowBrowserCard(!showBrowserCard)}
            className="text-xs h-8"
          >
            <Globe className="h-3.5 w-3.5 mr-1.5 text-[#176B45]" />
            <span className="hidden sm:inline">Chrome Session</span>
            {showBrowserCard ? (
              <ChevronUp className="h-3 w-3 ml-1 text-[#777D76]" />
            ) : (
              <ChevronDown className="h-3 w-3 ml-1 text-[#777D76]" />
            )}
          </Button>

          {/* New Chat Quick Action */}
          <Button
            size="sm"
            variant="outline"
            onClick={handleNewChat}
            disabled={isProcessing}
            className="text-xs h-8"
          >
            <Plus className="h-3.5 w-3.5 sm:mr-1 text-[#176B45]" />
            <span className="hidden sm:inline">New Analysis</span>
          </Button>
        </div>
      </div>

      {/* Chrome Session Panel Drawer */}
      <AnimatePresence>
        {showBrowserCard && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={snappyTransition}
            className="overflow-hidden"
          >
            <BrowserConnectionCard />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Conversational Workspace (Split View) */}
      <Card className="flex flex-1 overflow-hidden p-0 relative border-[#E8EAE4]">
        {/* Left: Conversation History Sidebar (Desktop) */}
        {!isSidebarCollapsedDesktop && (
          <div className="hidden md:flex w-72 shrink-0 border-r border-[#E8EAE4] bg-[#F8F8F5]">
            <ConversationSidebar
              conversations={conversations}
              activeId={currentConversation?.id || null}
              onSelectConversation={handleSelectConversation}
              onNewChat={handleNewChat}
              onRenameConversation={handleRenameConversation}
              onDeleteConversation={handleDeleteConversation}
            />
          </div>
        )}

        {/* Mobile Slide-Over Drawer for Sidebar */}
        <AnimatePresence>
          {isSidebarOpenMobile && (
            <div className="fixed inset-0 z-50 flex md:hidden">
              <div
                className="fixed inset-0 bg-black/40 backdrop-blur-xs"
                onClick={() => setIsSidebarOpenMobile(false)}
              />
              <motion.div
                initial={{ x: "-100%" }}
                animate={{ x: 0 }}
                exit={{ x: "-100%" }}
                transition={snappyTransition}
                className="relative z-10 w-4/5 max-w-xs h-full bg-[#F8F8F5] shadow-xl"
              >
                <ConversationSidebar
                  conversations={conversations}
                  activeId={currentConversation?.id || null}
                  onSelectConversation={handleSelectConversation}
                  onNewChat={handleNewChat}
                  onRenameConversation={handleRenameConversation}
                  onDeleteConversation={handleDeleteConversation}
                  onCloseMobile={() => setIsSidebarOpenMobile(false)}
                />
              </motion.div>
            </div>
          )}
        </AnimatePresence>

        {/* Right / Main: Chat Thread & Composer */}
        <div className="flex flex-1 flex-col overflow-hidden bg-[#FFFFFF]">
          {/* Messages Timeline */}
          <MessageList
            messages={currentConversation?.messages || []}
            onSelectPrompt={(p) => setInputValue(p)}
            onRetry={(p) => handleSendPrompt(p)}
            onCancelRequest={handleCancelActiveRequest}
            onOpenChromeDrawer={() => setShowBrowserCard(true)}
          />

          {/* Prompt Composer */}
          <MessageComposer
            value={inputValue}
            onChange={setInputValue}
            onSubmit={() => handleSendPrompt()}
            onCancel={isProcessing ? () => handleCancelActiveRequest() : undefined}
            onOpenTemplates={() => setIsTemplateModalOpen(true)}
            isProcessing={isProcessing}
          />
        </div>
      </Card>

      {/* Prompt Template Selector Modal */}
      <PromptTemplateModal
        isOpen={isTemplateModalOpen}
        onClose={() => setIsTemplateModalOpen(false)}
        onSelectTemplate={handleSelectTemplate}
      />
    </motion.div>
  );
}
