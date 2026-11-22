"use client";

import React, { useState } from "react";
import {
  Sparkles,
  Copy,
  Check,
  RotateCcw,
  ExternalLink,
  Code,
  Download,
  AlertTriangle,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { ChatMessage } from "@/types/rgAi";
import { RequestStatusIndicator } from "./RequestStatusIndicator";
import { ResponseRenderer } from "./ResponseRenderer";

interface AssistantMessageProps {
  message: ChatMessage;
  onRetry?: (originalPrompt: string) => void;
  onCancelRequest?: (requestId: string) => void;
  onOpenChromeDrawer?: () => void;
  lastUserPrompt?: string;
}

export function AssistantMessage({
  message,
  onRetry,
  onCancelRequest,
  onOpenChromeDrawer,
  lastUserPrompt,
}: AssistantMessageProps) {
  const [copiedText, setCopiedText] = useState<boolean>(false);
  const [copiedJson, setCopiedJson] = useState<boolean>(false);

  const isInFlight = [
    "queued",
    "initializing",
    "waiting_for_login",
    "submitting",
    "processing",
    "validating",
  ].includes(message.status || "");

  const handleCopyText = () => {
    if (typeof navigator !== "undefined" && navigator.clipboard) {
      navigator.clipboard.writeText(message.content);
      setCopiedText(true);
      setTimeout(() => setCopiedText(false), 2000);
    }
  };

  const handleCopyJson = () => {
    if (message.envelope && typeof navigator !== "undefined" && navigator.clipboard) {
      navigator.clipboard.writeText(JSON.stringify(message.envelope.data, null, 2));
      setCopiedJson(true);
      setTimeout(() => setCopiedJson(false), 2000);
    }
  };

  const handleDownloadJson = () => {
    if (!message.envelope) return;
    const filename = `rg-ai-analysis-${message.requestId || Date.now()}.json`;
    const blob = new Blob([JSON.stringify(message.envelope.data, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const showChromeDrawerCTA =
    message.status === "integration_unavailable" ||
    message.status === "waiting_for_login" ||
    message.error?.code === "LOGIN_REQUIRED" ||
    message.error?.code === "BROWSER_UNAVAILABLE";

  return (
    <div className="flex justify-start gap-3 group">
      {/* Bot Avatar */}
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-[#176B45] text-white text-xs shadow-xs">
        <Sparkles className="h-4 w-4" />
      </div>

      {/* Main Assistant Card */}
      <div className="relative max-w-3xl w-full rounded-2xl rounded-tl-xs bg-[#FFFFFF] border border-[#E8EAE4] p-4 text-xs text-[#20251F] shadow-xs">
        {/* Status header if in-flight or status tracked */}
        {message.status && (
          <div className="mb-3 flex items-center justify-between border-b border-[#E8EAE4]/60 pb-2">
            <RequestStatusIndicator
              status={message.status}
              queuePosition={message.metadata?.queuePosition}
              requestId={message.requestId}
              compact={!isInFlight}
              onCancel={
                message.requestId && onCancelRequest
                  ? () => onCancelRequest(message.requestId!)
                  : undefined
              }
            />
          </div>
        )}

        {/* In-Flight detailed indicator */}
        {isInFlight && (
          <div className="my-2">
            <RequestStatusIndicator
              status={message.status!}
              queuePosition={message.metadata?.queuePosition}
              requestId={message.requestId}
              onCancel={
                message.requestId && onCancelRequest
                  ? () => onCancelRequest(message.requestId!)
                  : undefined
              }
            />
          </div>
        )}

        {/* Response Body: Either Envelope Renderer or Text */}
        {message.envelope ? (
          <div className="mt-2">
            <ResponseRenderer envelope={message.envelope} />
          </div>
        ) : (
          !isInFlight && (
            <div className="whitespace-pre-wrap leading-relaxed text-xs sm:text-sm">
              {message.content}
            </div>
          )
        )}

        {/* Error Notification with details if failed */}
        {message.status === "failed" && message.error && (
          <div className="mt-3 rounded-xl border border-[#D64A4A]/20 bg-[#D64A4A]/5 p-3 text-xs text-[#D64A4A]">
            <div className="flex items-center gap-1.5 font-semibold">
              <AlertTriangle className="h-4 w-4" />
              <span>Error Code: {message.error.code}</span>
            </div>
            <p className="mt-1 text-[11px] text-[#20251F]">
              {message.error.message}
            </p>
          </div>
        )}

        {/* Contextual Action: Open Chrome Session Drawer */}
        {showChromeDrawerCTA && onOpenChromeDrawer && (
          <div className="mt-3 pt-3 border-t border-[#E8EAE4]">
            <Button
              size="sm"
              variant="primary"
              onClick={onOpenChromeDrawer}
              className="text-[11px] h-7"
            >
              <ExternalLink className="h-3 w-3 mr-1.5" />
              <span>Open Chrome Session Panel</span>
            </Button>
          </div>
        )}

        {/* Actions Footer */}
        {!isInFlight && (
          <div className="mt-3 flex items-center justify-between border-t border-[#E8EAE4]/60 pt-2 text-[10px] text-[#777D76]">
            <span>{message.timestamp}</span>

            <div className="flex items-center gap-2">
              {/* Retry action for failed requests */}
              {message.status === "failed" && onRetry && lastUserPrompt && (
                <button
                  onClick={() => onRetry(lastUserPrompt)}
                  className="inline-flex items-center gap-1 rounded px-1.5 py-0.5 hover:bg-[#E8EAE4] text-[#176B45] font-medium transition-colors cursor-pointer"
                  title="Retry prompt"
                >
                  <RotateCcw className="h-3 w-3" />
                  <span>Retry</span>
                </button>
              )}

              {/* Copy plain text */}
              <button
                onClick={handleCopyText}
                className="inline-flex items-center gap-1 rounded px-1.5 py-0.5 hover:bg-[#E8EAE4] text-[#777D76] transition-colors cursor-pointer"
                title="Copy response text"
              >
                {copiedText ? (
                  <>
                    <Check className="h-3 w-3 text-[#16834A]" />
                    <span className="text-[#16834A]">Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="h-3 w-3" />
                    <span>Copy Text</span>
                  </>
                )}
              </button>

              {/* Copy JSON (if envelope present) */}
              {message.envelope && (
                <>
                  <button
                    onClick={handleCopyJson}
                    className="inline-flex items-center gap-1 rounded px-1.5 py-0.5 hover:bg-[#E8EAE4] text-[#777D76] transition-colors cursor-pointer"
                    title="Copy validated JSON"
                  >
                    {copiedJson ? (
                      <>
                        <Check className="h-3 w-3 text-[#16834A]" />
                        <span className="text-[#16834A]">Copied</span>
                      </>
                    ) : (
                      <>
                        <Code className="h-3 w-3" />
                        <span>Copy JSON</span>
                      </>
                    )}
                  </button>

                  <button
                    onClick={handleDownloadJson}
                    className="inline-flex items-center gap-1 rounded px-1.5 py-0.5 hover:bg-[#E8EAE4] text-[#777D76] transition-colors cursor-pointer"
                    title="Download validated JSON"
                  >
                    <Download className="h-3 w-3" />
                    <span>Download</span>
                  </button>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
