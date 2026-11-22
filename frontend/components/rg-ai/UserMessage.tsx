"use client";

import React, { useState } from "react";
import { User, Copy, Check } from "lucide-react";
import { ChatMessage } from "@/types/rgAi";

interface UserMessageProps {
  message: ChatMessage;
}

export function UserMessage({ message }: UserMessageProps) {
  const [copied, setCopied] = useState<boolean>(false);

  const handleCopy = () => {
    if (typeof navigator !== "undefined" && navigator.clipboard) {
      navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="flex justify-end gap-3 group">
      <div className="relative max-w-2xl rounded-2xl rounded-tr-xs bg-[#176B45] p-4 text-xs text-white leading-relaxed shadow-xs">
        {/* Content */}
        <div className="whitespace-pre-wrap">{message.content}</div>

        {/* Footer info: timestamp and copy */}
        <div className="mt-2 flex items-center justify-between text-[10px] text-white/70">
          <span>{message.timestamp}</span>

          <button
            onClick={handleCopy}
            className="ml-3 inline-flex items-center gap-1 rounded px-1.5 py-0.5 hover:bg-white/10 text-white/80 transition-colors cursor-pointer"
            title="Copy prompt"
            aria-label="Copy prompt text"
          >
            {copied ? (
              <>
                <Check className="h-3 w-3 text-white" />
                <span>Copied</span>
              </>
            ) : (
              <>
                <Copy className="h-3 w-3" />
                <span>Copy</span>
              </>
            )}
          </button>
        </div>
      </div>

      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-[#F1F2ED] text-[#20251F] text-xs">
        <User className="h-4 w-4" />
      </div>
    </div>
  );
}
