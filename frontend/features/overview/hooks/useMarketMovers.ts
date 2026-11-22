"use client";

import { useState } from "react";

export type MoverTab = "gainers" | "losers" | "most_active";

export function useMarketMovers(initialTab: MoverTab = "gainers") {
  const [activeTab, setActiveTab] = useState<MoverTab>(initialTab);

  return {
    activeTab,
    setActiveTab,
  };
}
