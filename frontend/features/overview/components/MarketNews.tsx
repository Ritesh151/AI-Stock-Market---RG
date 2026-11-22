"use client";

import React from "react";
import { Newspaper, ExternalLink, AlertCircle, Clock } from "lucide-react";
import { MarketNewsData } from "../types/overview";
import { Card } from "@/components/ui/Card";

interface MarketNewsProps {
  news: MarketNewsData | null;
  isLoading?: boolean;
}

export function MarketNews({ news, isLoading = false }: MarketNewsProps) {
  if (isLoading && !news) {
    return (
      <Card className="p-5 animate-pulse space-y-4">
        <div className="h-5 w-32 bg-[#F1F2ED] rounded" />
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 bg-[#F1F2ED] rounded-xl" />
          ))}
        </div>
      </Card>
    );
  }

  const isUnavailable = !news || news.status === "UNAVAILABLE" || news.articles.length === 0;

  const formatPubDate = (isoOrRssDate: string): string => {
    try {
      const d = new Date(isoOrRssDate);
      if (isNaN(d.getTime())) return isoOrRssDate;
      return d.toLocaleDateString("en-IN", {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return isoOrRssDate;
    }
  };

  return (
    <Card className="p-5 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-[#E8EAE4] pb-3">
        <div className="flex items-center gap-2">
          <div className="flex h-6 w-6 items-center justify-center rounded-lg bg-[#176B45]/10 text-[#176B45]">
            <Newspaper className="h-3.5 w-3.5" />
          </div>
          <h3 className="font-semibold text-sm text-[#20251F]">
            Indian Market News
          </h3>
        </div>

        {news?.source_name && (
          <span className="text-[10px] font-medium text-[#777D76]">
            Source: {news.source_name}
          </span>
        )}
      </div>

      {/* Content */}
      {isUnavailable ? (
        <div className="rounded-xl border border-[#E8EAE4] bg-[#F8F8F5] p-5 text-center space-y-2">
          <AlertCircle className="h-6 w-6 text-[#777D76]/60 mx-auto" />
          <h4 className="font-semibold text-xs text-[#20251F]">
            News Feed Unavailable
          </h4>
          <p className="text-[11px] text-[#777D76] max-w-md mx-auto leading-relaxed">
            {news?.message ||
              "Live financial news feed is currently unavailable. In compliance with RG AI data standards, synthetic headlines are never generated."}
          </p>
        </div>
      ) : (
        <div className="divide-y divide-[#E8EAE4]">
          {news.articles.slice(0, 5).map((article) => (
            <a
              key={article.id}
              href={article.url}
              target="_blank"
              rel="noopener noreferrer"
              className="block py-3 hover:bg-[#F8F8F5] rounded-xl px-2 transition-colors group"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="space-y-1">
                  <h4 className="font-semibold text-xs text-[#20251F] group-hover:text-[#176B45] leading-snug">
                    {article.headline}
                  </h4>
                  <div className="flex flex-wrap items-center gap-2 text-[10px] text-[#777D76]">
                    <span className="font-medium text-[#20251F]">{article.publisher}</span>
                    <span>•</span>
                    <span className="flex items-center gap-1">
                      <Clock className="h-2.5 w-2.5" />
                      {formatPubDate(article.published_at)}
                    </span>
                    {article.related_symbols && article.related_symbols.length > 0 && (
                      <>
                        <span>•</span>
                        <span className="rounded bg-[#F1F2ED] px-1 py-0.2 text-[9px] font-mono font-bold text-[#176B45]">
                          {article.related_symbols.join(", ")}
                        </span>
                      </>
                    )}
                  </div>
                </div>

                <ExternalLink className="h-3.5 w-3.5 text-[#777D76] group-hover:text-[#176B45] shrink-0 mt-0.5 transition-colors" />
              </div>
            </a>
          ))}
        </div>
      )}
    </Card>
  );
}
