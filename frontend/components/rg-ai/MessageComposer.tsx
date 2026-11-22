"use client";

import React, { useRef, useEffect } from "react";
import { Send, Square, LayoutTemplate } from "lucide-react";
import { Button } from "@/components/ui/Button";

interface MessageComposerProps {
  value: string;
  onChange: (val: string) => void;
  onSubmit: () => void;
  onCancel?: () => void;
  onOpenTemplates: () => void;
  isProcessing: boolean;
  disabled?: boolean;
}

const MIN_LENGTH = 2;
const MAX_LENGTH = 4000;

export function MessageComposer({
  value,
  onChange,
  onSubmit,
  onCancel,
  onOpenTemplates,
  isProcessing,
  disabled = false,
}: MessageComposerProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea height to content
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      const nextHeight = Math.min(textareaRef.current.scrollHeight, 180);
      textareaRef.current.style.height = `${Math.max(48, nextHeight)}px`;
    }
  }, [value]);

  const charCount = value.length;
  const isTooShort = value.trim().length > 0 && value.trim().length < MIN_LENGTH;
  const isTooLong = charCount > MAX_LENGTH;
  const isValid = value.trim().length >= MIN_LENGTH && !isTooLong;

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (isValid && !isProcessing && !disabled) {
        onSubmit();
      }
    }
  };

  return (
    <div className="border-t border-[#E8EAE4] bg-[#FFFFFF] p-3 sm:p-4">
      <div className="mx-auto max-w-4xl space-y-2">
        {/* Main Textarea Container */}
        <div className="relative flex flex-col rounded-2xl border border-[#E8EAE4] bg-[#F8F8F5] transition-all focus-within:border-[#176B45] focus-within:bg-[#FFFFFF] focus-within:ring-1 focus-within:ring-[#176B45]/20">
          <textarea
            ref={textareaRef}
            rows={1}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask RG AI about stock valuation, support/resistance, or portfolio risks... (Shift+Enter for newline)"
            disabled={disabled || isProcessing}
            className="w-full resize-none bg-transparent px-4 py-3 text-xs sm:text-sm text-[#20251F] placeholder-[#777D76] focus:outline-none disabled:opacity-60 leading-relaxed"
          />

          {/* Bottom Toolbar inside Composer */}
          <div className="flex items-center justify-between border-t border-[#E8EAE4]/60 px-3 py-2 text-xs">
            <div className="flex items-center gap-2">
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={onOpenTemplates}
                disabled={isProcessing || disabled}
                className="h-7 text-[11px] px-2 py-0 border-[#E8EAE4] bg-[#FFFFFF] text-[#20251F] hover:bg-[#F1F2ED]"
              >
                <LayoutTemplate className="h-3.5 w-3.5 mr-1 text-[#176B45]" />
                <span>Templates</span>
              </Button>

              {isTooShort && (
                <span className="text-[10px] text-[#D64A4A]">
                  Min {MIN_LENGTH} characters required
                </span>
              )}
            </div>

            <div className="flex items-center gap-2.5">
              {/* Character counter */}
              <span
                className={`text-[10px] font-mono ${
                  isTooLong
                    ? "text-[#D64A4A] font-semibold"
                    : charCount > MAX_LENGTH * 0.9
                    ? "text-amber-600"
                    : "text-[#777D76]"
                }`}
              >
                {charCount}/{MAX_LENGTH}
              </span>

              {/* Action buttons: Cancel if processing, else Send */}
              {isProcessing && onCancel ? (
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={onCancel}
                  className="h-8 px-3 text-xs text-[#D64A4A] border-[#D64A4A]/30 hover:bg-[#D64A4A]/10"
                >
                  <Square className="h-3.5 w-3.5 mr-1 fill-current" />
                  <span>Stop</span>
                </Button>
              ) : (
                <Button
                  type="button"
                  variant="primary"
                  size="sm"
                  onClick={onSubmit}
                  disabled={!isValid || isProcessing || disabled}
                  className="h-8 px-3.5 text-xs"
                >
                  <Send className="h-3.5 w-3.5 mr-1" />
                  <span>Send</span>
                </Button>
              )}
            </div>
          </div>
        </div>

        {/* Footer Disclaimer note */}
        <p className="text-center text-[10px] text-[#777D76]">
          RG AI provides educational and analytical market intelligence. Not SEBI registered investment advice.
        </p>
      </div>
    </div>
  );
}
