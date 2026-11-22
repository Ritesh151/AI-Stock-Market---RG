"use client";

import React, { useState } from "react";
import { Gauge, Info, ChevronDown, ChevronUp, ShieldAlert } from "lucide-react";
import { MarketSentimentData } from "../types/overview";
import { Card } from "@/components/ui/Card";

interface MarketSentimentProps {
  sentiment: MarketSentimentData | null;
  isLoading?: boolean;
}

export function MarketSentiment({ sentiment, isLoading = false }: MarketSentimentProps) {
  const [showMethodology, setShowMethodology] = useState(false);

  if (isLoading && !sentiment) {
    return (
      <Card className="p-5 animate-pulse space-y-4">
        <div className="h-5 w-32 bg-[#F1F2ED] rounded" />
        <div className="h-10 w-48 bg-[#F1F2ED] rounded" />
        <div className="h-16 bg-[#F1F2ED] rounded-xl" />
      </Card>
    );
  }

  const status = sentiment?.status || "UNAVAILABLE";
  const score = sentiment?.score ?? 0;

  const getStatusConfig = () => {
    switch (status) {
      case "BULLISH":
        return {
          title: "Bullish Sentiment",
          color: "text-[#16834A]",
          bg: "bg-[#16834A]/10 border-[#16834A]/30 text-[#16834A]",
          barColor: "bg-[#16834A]",
          percentPos: 80,
        };
      case "BEARISH":
        return {
          title: "Bearish Sentiment",
          color: "text-[#D64A4A]",
          bg: "bg-[#D64A4A]/10 border-[#D64A4A]/30 text-[#D64A4A]",
          barColor: "bg-[#D64A4A]",
          percentPos: 20,
        };
      case "MIXED":
        return {
          title: "Mixed Signals",
          color: "text-[#D97706]",
          bg: "bg-[#D97706]/10 border-[#D97706]/30 text-[#B45309]",
          barColor: "bg-[#D97706]",
          percentPos: 50,
        };
      case "NEUTRAL":
        return {
          title: "Neutral Consolidation",
          color: "text-[#176B45]",
          bg: "bg-[#176B45]/10 border-[#176B45]/30 text-[#176B45]",
          barColor: "bg-[#176B45]",
          percentPos: 50,
        };
      case "UNAVAILABLE":
      default:
        return {
          title: "Sentiment Unavailable",
          color: "text-[#777D76]",
          bg: "bg-[#777D76]/10 border-[#777D76]/30 text-[#777D76]",
          barColor: "bg-[#777D76]",
          percentPos: 50,
        };
    }
  };

  const config = getStatusConfig();
  const indicators = sentiment?.indicators;

  // Normalized progress bar from -1.0..1.0 to 0%..100%
  const gaugePercent = Math.min(100, Math.max(0, ((score + 1.0) / 2.0) * 100));

  return (
    <Card className="p-5 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-[#E8EAE4] pb-3">
        <div className="flex items-center gap-2">
          <Gauge className="h-4 w-4 text-[#176B45]" />
          <h3 className="font-semibold text-sm text-[#20251F]">
            Institutional Market Sentiment
          </h3>
        </div>

        <span
          className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-bold ${config.bg}`}
        >
          {status}
        </span>
      </div>

      {/* Sentiment Gauge Bar */}
      <div className="space-y-1.5">
        <div className="flex justify-between text-[11px] font-semibold text-[#777D76]">
          <span className="text-[#D64A4A]">Extreme Fear (-1.0)</span>
          <span className="font-mono text-[#20251F]">
            Score: {score !== null ? score.toFixed(2) : "—"}
          </span>
          <span className="text-[#16834A]">Extreme Bullish (+1.0)</span>
        </div>

        <div className="relative h-2.5 w-full rounded-full bg-[#E8EAE4] overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${config.barColor}`}
            style={{ width: `${gaugePercent}%` }}
          />
        </div>
      </div>

      {/* Description */}
      <p className="text-xs text-[#777D76] leading-relaxed">
        {sentiment?.description || "Awaiting live quantitative indicators from market provider."}
      </p>

      {/* Indicators Sub-Bars */}
      {indicators && (
        <div className="grid grid-cols-3 gap-2 border-t border-[#E8EAE4] pt-3 text-[11px]">
          <div className="rounded-xl border border-[#E8EAE4] bg-[#F8F8F5] p-2.5">
            <span className="text-[#777D76] block text-[10px]">Index Momentum</span>
            <span className="font-mono font-bold text-[#20251F]">
              {indicators.index_momentum > 0 ? "+" : ""}
              {indicators.index_momentum.toFixed(2)}
            </span>
          </div>

          <div className="rounded-xl border border-[#E8EAE4] bg-[#F8F8F5] p-2.5">
            <span className="text-[#777D76] block text-[10px]">Volatility (VIX)</span>
            <span className="font-mono font-bold text-[#20251F]">
              {indicators.volatility_vix > 0 ? "+" : ""}
              {indicators.volatility_vix.toFixed(2)}
            </span>
          </div>

          <div className="rounded-xl border border-[#E8EAE4] bg-[#F8F8F5] p-2.5">
            <span className="text-[#777D76] block text-[10px]">Market Breadth</span>
            <span className="font-mono font-bold text-[#20251F]">
              {indicators.market_breadth > 0 ? "+" : ""}
              {indicators.market_breadth.toFixed(2)}
            </span>
          </div>
        </div>
      )}

      {/* Methodology Accordion */}
      <div className="border-t border-[#E8EAE4] pt-2">
        <button
          onClick={() => setShowMethodology(!showMethodology)}
          className="flex items-center justify-between w-full text-[11px] font-semibold text-[#176B45] hover:underline cursor-pointer"
        >
          <span className="flex items-center gap-1">
            <Info className="h-3 w-3" />
            Methodology & Limitations
          </span>
          {showMethodology ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
        </button>

        {showMethodology && (
          <div className="mt-2.5 rounded-xl border border-[#E8EAE4] bg-[#F1F2ED]/50 p-3 text-[11px] text-[#777D76] space-y-1.5">
            <p className="leading-relaxed">
              <strong className="text-[#20251F]">Calculation Method:</strong> Weighted composite score derived from 40% benchmark momentum (NIFTY 50 and SENSEX returns), 30% volatility dynamics (INDIA VIX), and 30% breadth (Advance/Decline ratio).
            </p>
            <p className="flex items-start gap-1 text-[10px] text-[#777D76]/90">
              <ShieldAlert className="h-3.5 w-3.5 text-[#D97706] shrink-0 mt-0.5" />
              <span>
                <strong>Limitation Notice:</strong> This score is a mathematical heuristic based on delayed session feeds and is not an official stock exchange metric. Never trade solely based on automated sentiment.
              </span>
            </p>
          </div>
        )}
      </div>
    </Card>
  );
}
