"use client";

import React from "react";
import { RefreshCw, Clock, ShieldCheck } from "lucide-react";
import { MarketStatusData } from "../types/overview";

interface OverviewHeaderProps {
  status: MarketStatusData | null;
  lastUpdated: string | null;
  onRefresh: () => void;
  isRefreshing?: boolean;
}

export function OverviewHeader({
  status,
  lastUpdated,
  onRefresh,
  isRefreshing = false,
}: OverviewHeaderProps) {
  const isOpen = status?.status === "OPEN";

  const formatISTTime = (isoString: string | null): string => {
    if (!isoString) return "Updating...";
    try {
      const d = new Date(isoString);
      return d.toLocaleTimeString("en-IN", {
        timeZone: "Asia/Kolkata",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        hour12: true,
      }) + " IST";
    } catch {
      return isoString;
    }
  };

  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-[#E8EAE4] pb-5">
      <div>
        <div className="flex flex-wrap items-center gap-2.5">
          <h1 className="text-2xl font-bold tracking-tight text-[#20251F] sm:text-3xl">
            Market Overview
          </h1>

          {/* Market Status Pill */}
          <div
            className={`flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-semibold border ${
              isOpen
                ? "bg-[#16834A]/10 text-[#16834A] border-[#16834A]/30"
                : "bg-[#777D76]/10 text-[#777D76] border-[#777D76]/30"
            }`}
          >
            <span className="relative flex h-2 w-2">
              {isOpen && (
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[#16834A] opacity-75" />
              )}
              <span
                className={`relative inline-flex h-2 w-2 rounded-full ${
                  isOpen ? "bg-[#16834A]" : "bg-[#777D76]"
                }`}
              />
            </span>
            <span>{status?.exchange || "NSE"}: {isOpen ? "MARKET OPEN" : "MARKET CLOSED"}</span>
          </div>

          <span className="hidden sm:inline-flex items-center gap-1 rounded-full border border-[#E8EAE4] bg-[#F1F2ED]/60 px-2 py-0.5 text-[10px] font-medium text-[#777D76]">
            <ShieldCheck className="h-3 w-3 text-[#176B45]" />
            Verified Feeds (~15m delay)
          </span>
        </div>

        <p className="mt-1 text-xs text-[#777D76]">
          Your Indian stock market at a glance. Real-time technical breadth and institutional benchmarks.
        </p>
      </div>

      {/* Controls: Timestamp & Refresh */}
      <div className="flex items-center gap-3 self-start sm:self-auto">
        <div className="text-left sm:text-right">
          <div className="flex items-center gap-1 text-[11px] text-[#777D76]">
            <Clock className="h-3 w-3" />
            <span>Updated: <span className="font-mono font-medium text-[#20251F]">{formatISTTime(lastUpdated)}</span></span>
          </div>
          <div className="text-[10px] text-[#777D76]/80">
            Session: {status?.session || "REGULAR"} (09:15–15:30 IST)
          </div>
        </div>

        <button
          onClick={onRefresh}
          disabled={isRefreshing}
          className="inline-flex items-center gap-1.5 rounded-xl border border-[#E8EAE4] bg-[#FFFFFF] px-3.5 py-2 text-xs font-semibold text-[#20251F] shadow-xs transition-all hover:bg-[#F1F2ED] active:scale-98 cursor-pointer disabled:opacity-50"
          aria-label="Refresh Market Dashboard"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${isRefreshing ? "animate-spin text-[#176B45]" : "text-[#777D76]"}`} />
          <span className="hidden sm:inline">Refresh</span>
        </button>
      </div>
    </div>
  );
}
