"use client";

import React, { useEffect, useState } from "react";
import { motion } from "motion/react";
import { TrendingUp, TrendingDown, Clock, Activity, RefreshCw } from "lucide-react";
import { stocksApi } from "@/services/stocksApi";
import { MarketIndexItem, MarketStatusResponse } from "@/types/stock";
import { snappyTransition } from "@/lib/motionTokens";

export function MarketIndexBar() {
  const [indices, setIndices] = useState<MarketIndexItem[]>([]);
  const [status, setStatus] = useState<MarketStatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    let isCancelled = false;

    async function load() {
      try {
        const [indicesRes, statusRes] = await Promise.allSettled([
          stocksApi.getMarketIndices(),
          stocksApi.getMarketStatus("NSE"),
        ]);

        if (!isCancelled) {
          if (indicesRes.status === "fulfilled" && indicesRes.value.success) {
            setIndices(indicesRes.value.indices);
          }
          if (statusRes.status === "fulfilled" && statusRes.value.success) {
            setStatus(statusRes.value);
          }
        }
      } catch {
        // Graceful fallback
      } finally {
        if (!isCancelled) {
          setLoading(false);
          setRefreshing(false);
        }
      }
    }

    void load();
    const interval = setInterval(load, 60000); // 60s poll
    return () => {
      isCancelled = true;
      clearInterval(interval);
    };
  }, []);

  const handleManualRefresh = async () => {
    setRefreshing(true);
    try {
      const [indicesRes, statusRes] = await Promise.allSettled([
        stocksApi.getMarketIndices(),
        stocksApi.getMarketStatus("NSE"),
      ]);

      if (indicesRes.status === "fulfilled" && indicesRes.value.success) {
        setIndices(indicesRes.value.indices);
      }
      if (statusRes.status === "fulfilled" && statusRes.value.success) {
        setStatus(statusRes.value);
      }
    } finally {
      setRefreshing(false);
    }
  };

  const isOpen = status?.status === "OPEN";

  return (
    <div className="w-full rounded-2xl border border-[#E8EAE4] bg-[#FFFFFF] p-3 shadow-xs">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        {/* Market Status Pill */}
        <div className="flex items-center gap-2 text-xs">
          <div
            className={`flex items-center gap-1.5 rounded-lg px-2.5 py-1 font-semibold ${
              isOpen
                ? "bg-[#16834A]/10 text-[#16834A] border border-[#16834A]/20"
                : "bg-[#777D76]/10 text-[#777D76] border border-[#777D76]/20"
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

          <div className="hidden sm:flex items-center gap-1 text-[11px] text-[#777D76]">
            <Clock className="h-3.5 w-3.5" />
            <span>IST: {status?.current_time ? status.current_time.slice(11, 16) : "09:15-15:30"}</span>
            <span className="text-[#E8EAE4]">•</span>
            <span>Session: {status?.session || "REGULAR"}</span>
          </div>

          <button
            onClick={handleManualRefresh}
            disabled={refreshing || loading}
            aria-label="Refresh Market Benchmarks"
            className="ml-auto sm:ml-2 rounded-lg p-1 text-[#777D76] transition-colors hover:bg-[#F1F2ED] hover:text-[#20251F] cursor-pointer"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${refreshing ? "animate-spin text-[#176B45]" : ""}`} />
          </button>
        </div>

        {/* Indices Strip */}
        <div className="flex items-center gap-3 overflow-x-auto pb-1 lg:pb-0 scrollbar-none">
          {indices.length > 0 ? (
            indices.map((idx) => {
              const isPos = (idx.change ?? 0) >= 0;
              return (
                <motion.div
                  key={idx.symbol}
                  className="flex flex-shrink-0 items-center gap-2 rounded-xl border border-[#E8EAE4] bg-[#F8F8F5] px-3 py-1.5"
                  whileHover={{ y: -1 }}
                  transition={snappyTransition}
                >
                  <Activity className="h-3 w-3 text-[#777D76]" />
                  <span className="font-mono text-xs font-semibold text-[#20251F]">
                    {idx.name}
                  </span>
                  <span className="font-mono text-xs font-bold text-[#20251F]">
                    {idx.value != null ? idx.value.toLocaleString("en-IN", { maximumFractionDigits: 2 }) : "—"}
                  </span>
                  {idx.percent_change != null && (
                    <span
                      className={`inline-flex items-center font-mono text-[10px] font-semibold ${
                        isPos ? "text-[#16834A]" : "text-[#D64A4A]"
                      }`}
                    >
                      {isPos ? <TrendingUp className="mr-0.5 h-2.5 w-2.5" /> : <TrendingDown className="mr-0.5 h-2.5 w-2.5" />}
                      {isPos ? "+" : ""}
                      {idx.percent_change.toFixed(2)}%
                    </span>
                  )}
                </motion.div>
              );
            })
          ) : (
            <div className="text-xs text-[#777D76] py-1">
              {loading ? "Loading benchmark indices..." : "Benchmark indices ready"}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
