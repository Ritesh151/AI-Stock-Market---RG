"use client";

import React from "react";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { MarketIndexOverviewItem } from "../types/overview";
import { MarketDataBadge } from "@/components/stocks/MarketDataBadge";
import { Card } from "@/components/ui/Card";

interface MarketIndexCardProps {
  item: MarketIndexOverviewItem;
  isSelected?: boolean;
  onSelect?: () => void;
}

export function MarketIndexCard({
  item,
  isSelected = false,
  onSelect,
}: MarketIndexCardProps) {
  const isPos = (item.change ?? 0) > 0;
  const isNeg = (item.change ?? 0) < 0;

  const strokeColor = isPos ? "#16834A" : isNeg ? "#D64A4A" : "#777D76";

  // Generate SVG Sparkline path
  const sparklineData = item.sparkline || [];
  let sparklinePath = "";
  if (sparklineData.length >= 2) {
    const min = Math.min(...sparklineData);
    const max = Math.max(...sparklineData);
    const range = max - min || 1;
    const width = 110;
    const height = 36;
    const pad = 4;

    const points = sparklineData.map((val, idx) => {
      const x = pad + (idx / (sparklineData.length - 1)) * (width - pad * 2);
      const y = height - pad - ((val - min) / range) * (height - pad * 2);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    });

    sparklinePath = `M ${points.join(" L ")}`;
  }

  const formatPoints = (val: number | null | undefined): string => {
    if (val === null || val === undefined) return "Data unavailable";
    return val.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  };

  return (
    <Card
      onClick={onSelect}
      className={`relative p-5 cursor-pointer transition-all ${
        isSelected
          ? "border-[#176B45] ring-2 ring-[#176B45]/20 shadow-sm"
          : "hover:border-[#D5D8CF] hover:shadow-xs"
      }`}
    >
      {/* Top Header: Title & Freshness */}
      <div className="flex items-start justify-between">
        <div>
          <span className="font-mono text-sm font-bold text-[#20251F]">
            {item.name}
          </span>
          <div className="text-[11px] font-mono text-[#777D76]">
            {item.symbol}
          </div>
        </div>

        <MarketDataBadge
          status={item.data_status}
          source={null}
          showSource={false}
        />
      </div>

      {/* Main Value & Sparkline Row */}
      <div className="mt-3 flex items-end justify-between">
        <div>
          <div className="font-mono text-2xl font-extrabold text-[#20251F]">
            {item.value !== null ? formatPoints(item.value) : "Data unavailable"}
          </div>

          {/* Change pill */}
          <div className="mt-1 flex items-center gap-1.5 font-mono text-xs font-semibold">
            {item.change !== null && item.percent_change !== null ? (
              <span
                className={`inline-flex items-center gap-0.5 rounded-md px-1.5 py-0.5 ${
                  isPos
                    ? "bg-[#16834A]/10 text-[#16834A]"
                    : isNeg
                    ? "bg-[#D64A4A]/10 text-[#D64A4A]"
                    : "bg-[#777D76]/10 text-[#777D76]"
                }`}
              >
                {isPos && <TrendingUp className="h-3 w-3" />}
                {isNeg && <TrendingDown className="h-3 w-3" />}
                {!isPos && !isNeg && <Minus className="h-3 w-3" />}
                <span>
                  {isPos ? "+" : ""}
                  {item.change.toFixed(2)} ({isPos ? "+" : ""}
                  {item.percent_change.toFixed(2)}%)
                </span>
              </span>
            ) : (
              <span className="text-[11px] text-[#777D76]">Change unavailable</span>
            )}
          </div>
        </div>

        {/* Mini SVG Sparkline */}
        {sparklinePath && (
          <div className="w-[110px] h-[36px] overflow-hidden">
            <svg viewBox="0 0 110 36" className="w-full h-full overflow-visible">
              <path
                d={sparklinePath}
                fill="none"
                stroke={strokeColor}
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
        )}
      </div>

      {/* Session Details Footer: Prev Close, High, Low */}
      <div className="mt-4 grid grid-cols-3 gap-2 border-t border-[#E8EAE4] pt-3 text-[10px] font-mono">
        <div>
          <span className="text-[#777D76] block">Prev Close</span>
          <span className="font-semibold text-[#20251F]">
            {item.previous_close !== null ? formatPoints(item.previous_close) : "—"}
          </span>
        </div>

        <div>
          <span className="text-[#777D76] block">Day High</span>
          <span className="font-semibold text-[#16834A]">
            {item.day_high !== null ? formatPoints(item.day_high) : "—"}
          </span>
        </div>

        <div>
          <span className="text-[#777D76] block">Day Low</span>
          <span className="font-semibold text-[#D64A4A]">
            {item.day_low !== null ? formatPoints(item.day_low) : "—"}
          </span>
        </div>
      </div>
    </Card>
  );
}
