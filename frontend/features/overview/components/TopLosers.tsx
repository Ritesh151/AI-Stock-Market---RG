"use client";

import React from "react";
import Link from "next/link";
import { TrendingDown, Sparkles, ChevronRight } from "lucide-react";
import { StockMoverItem } from "../types/overview";
import { Card } from "@/components/ui/Card";

interface TopLosersProps {
  losers: StockMoverItem[];
  isLoading?: boolean;
}

export function TopLosers({ losers, isLoading = false }: TopLosersProps) {
  if (isLoading && losers.length === 0) {
    return (
      <Card className="p-5 animate-pulse space-y-3">
        <div className="h-4 w-32 bg-[#F1F2ED] rounded" />
        <div className="space-y-2">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="h-12 bg-[#F1F2ED] rounded-xl" />
          ))}
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-5 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-[#E8EAE4] pb-3">
        <div className="flex items-center gap-2">
          <div className="flex h-6 w-6 items-center justify-center rounded-lg bg-[#D64A4A]/10 text-[#D64A4A]">
            <TrendingDown className="h-3.5 w-3.5" />
          </div>
          <h3 className="font-semibold text-sm text-[#20251F]">
            Top Losers
          </h3>
          <span className="rounded-full bg-[#D64A4A]/10 px-2 py-0.2 font-mono text-[10px] font-bold text-[#D64A4A]">
            NSE Bluechips
          </span>
        </div>

        <Link
          href="/stocks"
          className="text-xs font-semibold text-[#176B45] hover:underline inline-flex items-center"
        >
          <span>View all</span>
          <ChevronRight className="h-3.5 w-3.5" />
        </Link>
      </div>

      {/* List */}
      <div className="divide-y divide-[#E8EAE4]">
        {losers.length === 0 ? (
          <div className="py-6 text-center text-xs text-[#777D76]">
            No losing stocks recorded for this session.
          </div>
        ) : (
          losers.map((stock) => {
            const aiPrompt = `Analyze top loser ${stock.symbol} (${stock.exchange}): examine support levels, fundamental catalysts behind today's decline, and mean-reversion potential.`;
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
                    <div className="font-mono text-[11px] font-semibold text-[#D64A4A] inline-flex items-center">
                      <TrendingDown className="mr-0.5 h-2.5 w-2.5" />
                      {stock.change_percent != null ? stock.change_percent.toFixed(2) : "0.00"}%
                    </div>
                  </div>

                  {/* Actions: Quick RG AI bridge */}
                  <Link
                    href={`/rg-ai?prompt=${encodeURIComponent(aiPrompt)}`}
                    className="opacity-0 group-hover:opacity-100 rounded-lg p-1 text-[#176B45] hover:bg-[#176B45]/10 transition-all cursor-pointer"
                    title="Analyze with RG AI"
                    aria-label={`Analyze ${stock.symbol} with RG AI`}
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
