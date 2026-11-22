"use client";

import { useState } from "react";
import { MarketIndexOverviewItem } from "../types/overview";

export function useMarketIndices(initialIndices: MarketIndexOverviewItem[] = []) {
  const [selectedIndex, setSelectedIndex] = useState<string>("^NSEI");

  return {
    selectedIndex,
    setSelectedIndex,
    indices: initialIndices,
  };
}
