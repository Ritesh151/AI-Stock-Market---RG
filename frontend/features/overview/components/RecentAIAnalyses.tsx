"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Sparkles, MessageSquare, ChevronRight, Bot } from "lucide-react";
import { conversationRepository } from "@/services/conversationRepository";
import { ConversationSummary } from "@/types/rgAi";
import { Card } from "@/components/ui/Card";

export function RecentAIAnalyses() {
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isCancelled = false;
    async function loadConversations() {
      try {
        const list = await conversationRepository.list();
        if (!isCancelled) {
          // Filter to conversations that have at least 1 message or meaningful title
          setConversations(list.filter((c) => c.messageCount > 0));
        }
      } catch {
        // Fallback
      } finally {
        if (!isCancelled) {
          setIsLoading(false);
        }
      }
    }
    void loadConversations();
    return () => {
      isCancelled = true;
    };
  }, []);

  const formatDate = (isoString: string): string => {
    try {
      const d = new Date(isoString);
      return d.toLocaleDateString("en-IN", {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return isoString;
    }
  };

  return (
    <Card className="p-5 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-[#E8EAE4] pb-3">
        <div className="flex items-center gap-2">
          <div className="flex h-6 w-6 items-center justify-center rounded-lg bg-[#176B45]/10 text-[#176B45]">
            <Bot className="h-3.5 w-3.5" />
          </div>
          <h3 className="font-semibold text-sm text-[#20251F]">
            Recent RG AI Analyses
          </h3>
          <span className="rounded-full bg-[#F1F2ED] px-2 py-0.2 font-mono text-[10px] font-bold text-[#777D76]">
            {conversations.length}
          </span>
        </div>

        <Link
          href="/rg-ai"
          className="text-xs font-semibold text-[#176B45] hover:underline inline-flex items-center"
        >
          <span>Open Chat</span>
          <ChevronRight className="h-3.5 w-3.5" />
        </Link>
      </div>

      {/* List or Empty State */}
      <div className="divide-y divide-[#E8EAE4]">
        {isLoading ? (
          <div className="py-8 text-center text-xs text-[#777D76]">
            Loading recent analyses...
          </div>
        ) : conversations.length === 0 ? (
          <div className="py-8 text-center text-xs text-[#777D76] space-y-1.5">
            <Sparkles className="h-6 w-6 text-[#777D76]/50 mx-auto mb-1" />
            <p className="font-medium text-[#20251F]">No previous RG AI analyses yet</p>
            <p className="text-[11px] text-[#777D76]">
              Submit stock questions in RG AI Assistant to view institutional summaries here.
            </p>
            <Link
              href="/rg-ai"
              className="inline-block mt-2 rounded-lg bg-[#176B45] px-3 py-1.5 text-xs font-semibold text-white hover:bg-[#125837]"
            >
              Start New Analysis
            </Link>
          </div>
        ) : (
          conversations.slice(0, 4).map((conv) => (
            <Link
              key={conv.id}
              href="/rg-ai"
              className="flex items-center justify-between py-2.5 hover:bg-[#F8F8F5] rounded-xl px-2 transition-colors group"
            >
              <div className="min-w-0 pr-3">
                <div className="font-semibold text-xs text-[#20251F] truncate group-hover:text-[#176B45]">
                  {conv.title}
                </div>
                <div className="flex items-center gap-2 text-[11px] text-[#777D76] mt-0.5">
                  <span className="flex items-center gap-1">
                    <MessageSquare className="h-3 w-3" />
                    {conv.messageCount} messages
                  </span>
                  <span>•</span>
                  <span>{formatDate(conv.updatedAt)}</span>
                </div>
              </div>

              <ChevronRight className="h-4 w-4 text-[#777D76] shrink-0 group-hover:text-[#176B45] transition-colors" />
            </Link>
          ))
        )}
      </div>
    </Card>
  );
}
