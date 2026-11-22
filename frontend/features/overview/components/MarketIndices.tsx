"use client";

import React from "react";
import { MarketIndexOverviewItem } from "../types/overview";
import { MarketIndexCard } from "./MarketIndexCard";

interface MarketIndicesProps {
  indices: MarketIndexOverviewItem[];
  selectedIndex: string;
  onSelectIndex: (symbol: string) => void;
  isLoading?: boolean;
}

export function MarketIndices({
  indices,
  selectedIndex,
  onSelectIndex,
  isLoading = false,
}: MarketIndicesProps) {
  if (isLoading && indices.length === 0) {
    return (
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="h-44 rounded-2xl border border-[#E8EAE4] bg-[#FFFFFF] p-5 animate-pulse space-y-3"
          >
            <div className="h-4 w-28 bg-[#F1F2ED] rounded" />
            <div className="h-8 w-44 bg-[#F1F2ED] rounded" />
            <div className="h-4 w-20 bg-[#F1F2ED] rounded" />
            <div className="mt-4 pt-3 border-t border-[#E8EAE4] grid grid-cols-3 gap-2">
              <div className="h-4 bg-[#F1F2ED] rounded" />
              <div className="h-4 bg-[#F1F2ED] rounded" />
              <div className="h-4 bg-[#F1F2ED] rounded" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  // Filter to primary benchmarks: NIFTY 50, SENSEX, BANK NIFTY (and optional INDIA VIX)
  const displayIndices = indices.slice(0, 3);

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {displayIndices.map((item) => (
        <MarketIndexCard
          key={item.symbol}
          item={item}
          isSelected={selectedIndex === item.symbol}
          onSelect={() => onSelectIndex(item.symbol)}
        />
      ))}
    </div>
  );
}
