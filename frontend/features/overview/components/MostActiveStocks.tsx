"use client";

import React from "react";
import Link from "next/link";
import { Activity, Sparkles, ChevronRight } from "lucide-react";
import { StockMoverItem } from "../types/overview";
import { Card } from "@/components/ui/Card";

interface MostActiveStocksProps {
  stocks: StockMoverItem[];
  rankingMetric?: string;
  isLoading?: boolean;
}

export function MostActiveStocks({
  stocks,
  rankingMetric = "Trading Volume (shares)",
  isLoading = false,
}: MostActiveStocksProps) {
  if (isLoading && stocks.length === 0) {
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

  const formatVolume = (val: number | null | undefined): string => {
    if (val === null || val === undefined) return "—";
    if (val >= 10000000) return `${(val / 10000000).toFixed(2)} Cr`;
    if (val >= 100000) return `${(val / 100000).toFixed(2)} L`;
    if (val >= 1000) return `${(val / 1000).toFixed(1)}k`;
    return val.toLocaleString("en-IN");
  };

  return (
    <Card className="p-5 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-[#E8EAE4] pb-3">
        <div>
          <div className="flex items-center gap-2">
            <div className="flex h-6 w-6 items-center justify-center rounded-lg bg-[#176B45]/10 text-[#176B45]">
              <Activity className="h-3.5 w-3.5" />
            </div>
            <h3 className="font-semibold text-sm text-[#20251F]">
              Most Active Stocks
            </h3>
          </div>
          <span className="text-[10px] text-[#777D76]">
            Ranked by {rankingMetric}
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
        {stocks.length === 0 ? (
          <div className="py-6 text-center text-xs text-[#777D76]">
            No volume activity records available.
          </div>
        ) : (
          stocks.map((stock) => {
            const isPos = (stock.change_percent ?? 0) >= 0;
            const aiPrompt = `Analyze high-volume liquidity driver ${stock.symbol} (${stock.exchange}): examine block delivery percentages, institutional activity, and price-volume breakout patterns.`;

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
                  <div className="text-[11px] text-[#777D76]">
                    Vol: <span className="font-mono font-medium text-[#20251F]">{formatVolume(stock.volume)}</span>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <div className="text-right">
                    <div className="font-mono text-xs font-bold text-[#20251F]">
                      ₹{stock.last_price != null ? stock.last_price.toFixed(2) : "—"}
                    </div>
                    <div
                      className={`font-mono text-[11px] font-semibold inline-flex items-center ${
                        isPos ? "text-[#16834A]" : "text-[#D64A4A]"
                      }`}
                    >
                      {isPos ? "+" : ""}
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
