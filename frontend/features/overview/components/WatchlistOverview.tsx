"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Star, ChevronRight, Sparkles, Building2 } from "lucide-react";
import { stocksApi } from "@/services/stocksApi";
import { WatchlistItem } from "@/types/stock";
import { Card } from "@/components/ui/Card";

export function WatchlistOverview() {
  const [items, setItems] = useState<WatchlistItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isCancelled = false;
    async function loadWatchlist() {
      try {
        const res = await stocksApi.getWatchlist();
        if (!isCancelled && res && res.success) {
          setItems(res.items || []);
        }
      } catch {
        // Fallback
      } finally {
        if (!isCancelled) {
          setIsLoading(false);
        }
      }
    }
    void loadWatchlist();
    return () => {
      isCancelled = true;
    };
  }, []);

  return (
    <Card className="p-5 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-[#E8EAE4] pb-3">
        <div className="flex items-center gap-2">
          <div className="flex h-6 w-6 items-center justify-center rounded-lg bg-[#176B45]/10 text-[#176B45]">
            <Star className="h-3.5 w-3.5 fill-[#176B45]" />
          </div>
          <h3 className="font-semibold text-sm text-[#20251F]">
            My Watchlist
          </h3>
          <span className="rounded-full bg-[#F1F2ED] px-2 py-0.2 font-mono text-[10px] font-bold text-[#777D76]">
            {items.length}
          </span>
        </div>

        <Link
          href="/stocks"
          className="text-xs font-semibold text-[#176B45] hover:underline inline-flex items-center"
        >
          <span>Manage</span>
          <ChevronRight className="h-3.5 w-3.5" />
        </Link>
      </div>

      {/* List / Empty State */}
      <div className="divide-y divide-[#E8EAE4]">
        {isLoading ? (
          <div className="py-8 text-center text-xs text-[#777D76]">
            Loading watchlist...
          </div>
        ) : items.length === 0 ? (
          <div className="py-8 text-center text-xs text-[#777D76] space-y-1.5">
            <Building2 className="h-6 w-6 text-[#777D76]/50 mx-auto mb-1" />
            <p className="font-medium text-[#20251F]">Your watchlist is empty</p>
            <p className="text-[11px] text-[#777D76]">
              Search and add stocks in the Stock Screener to monitor them here.
            </p>
            <Link
              href="/stocks"
              className="inline-block mt-2 rounded-lg bg-[#176B45] px-3 py-1.5 text-xs font-semibold text-white hover:bg-[#125837]"
            >
              Explore Stocks
            </Link>
          </div>
        ) : (
          items.slice(0, 5).map((stock) => {
            const isPos = (stock.change_percent ?? 0) >= 0;
            const aiPrompt = `Perform institutional portfolio review on watchlist holding ${stock.symbol} (${stock.exchange}): check current support levels and valuation targets.`;

            return (
              <div
                key={stock.symbol}
                className="flex items-center justify-between py-2.5 hover:bg-[#F8F8F5] rounded-xl px-2 transition-colors group"
              >
                <div>
                  <div className="flex items-center gap-1.5">
                    <span className="font-mono text-xs font-bold text-[#20251F]">
                      {stock.symbol}
                    </span>
                    <span className="rounded bg-[#F1F2ED] px-1 py-0.2 text-[9px] font-bold text-[#176B45]">
                      {stock.exchange}
                    </span>
                  </div>
                  <div className="text-[11px] text-[#777D76] truncate max-w-[150px]">
                    {stock.company_name}
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <div className="text-right">
                    <div className="font-mono text-xs font-bold text-[#20251F]">
                      ₹{stock.last_price != null ? stock.last_price.toFixed(2) : "—"}
                    </div>
                    {stock.change_percent != null && (
                      <div
                        className={`font-mono text-[11px] font-semibold ${
                          isPos ? "text-[#16834A]" : "text-[#D64A4A]"
                        }`}
                      >
                        {isPos ? "+" : ""}
                        {stock.change_percent.toFixed(2)}%
                      </div>
                    )}
                  </div>

                  <Link
                    href={`/rg-ai?prompt=${encodeURIComponent(aiPrompt)}`}
                    className="opacity-0 group-hover:opacity-100 rounded-lg p-1 text-[#176B45] hover:bg-[#176B45]/10 transition-all cursor-pointer"
                    title="Analyze with RG AI"
                  >
                    <Sparkles className="h-3.5 w-3.5" />
                  </Link>
                </div>
              </div>
            );
          })
        )}
      </div>
    </Card>
  );
}
