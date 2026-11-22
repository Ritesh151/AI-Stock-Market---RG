"use client";

import React, { useRef, useEffect, useState } from "react";
import { ArrowDown } from "lucide-react";
import { ChatMessage } from "@/types/rgAi";
import { WelcomeScreen } from "./WelcomeScreen";
import { UserMessage } from "./UserMessage";
import { AssistantMessage } from "./AssistantMessage";

interface MessageListProps {
  messages: ChatMessage[];
  onSelectPrompt: (prompt: string) => void;
  onRetry: (prompt: string) => void;
  onCancelRequest: (requestId: string) => void;
  onOpenChromeDrawer: () => void;
}

export function MessageList({
  messages,
  onSelectPrompt,
  onRetry,
  onCancelRequest,
  onOpenChromeDrawer,
}: MessageListProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const [showScrollBottom, setShowScrollBottom] = useState<boolean>(false);

  // Auto-scroll to bottom on new messages
  const scrollToBottom = (behavior: ScrollBehavior = "smooth") => {
    bottomRef.current?.scrollIntoView({ behavior });
  };

  useEffect(() => {
    scrollToBottom("smooth");
  }, [messages]);

  // Monitor scroll position to show/hide scroll-to-bottom floating button
  const handleScroll = () => {
    if (!containerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
    const isScrolledUp = scrollHeight - scrollTop - clientHeight > 180;
    setShowScrollBottom(isScrolledUp);
  };

  // Find last user prompt for retry context
  const getLastUserPrompt = (currentIndex: number): string | undefined => {
    for (let i = currentIndex - 1; i >= 0; i--) {
      if (messages[i].sender === "user") {
        return messages[i].content;
      }
    }
    return undefined;
  };

  if (messages.length === 0) {
    return <WelcomeScreen onSelectPrompt={onSelectPrompt} />;
  }

  return (
    <div className="relative flex-1 overflow-hidden">
      <div
        ref={containerRef}
        onScroll={handleScroll}
        className="h-full overflow-y-auto p-4 sm:p-6 space-y-5"
      >
        {messages.map((msg, index) => {
          const uniqueKey = `${msg.id || "msg"}-${index}`;
          if (msg.sender === "user") {
            return <UserMessage key={uniqueKey} message={msg} />;
          }

          return (
            <AssistantMessage
              key={uniqueKey}
              message={msg}
              onRetry={onRetry}
              onCancelRequest={onCancelRequest}
              onOpenChromeDrawer={onOpenChromeDrawer}
              lastUserPrompt={getLastUserPrompt(index)}
            />
          );
        })}

        <div ref={bottomRef} className="h-2" />
      </div>

      {/* Floating Scroll to Bottom Button */}
      {showScrollBottom && (
        <button
          onClick={() => scrollToBottom("smooth")}
          className="absolute bottom-4 right-6 flex h-8 w-8 items-center justify-center rounded-full border border-[#E8EAE4] bg-[#FFFFFF] text-[#20251F] shadow-md hover:bg-[#F8F8F5] transition-all cursor-pointer z-10"
          title="Scroll to bottom"
          aria-label="Scroll to newest message"
        >
          <ArrowDown className="h-4 w-4 text-[#176B45]" />
        </button>
      )}
    </div>
  );
}
