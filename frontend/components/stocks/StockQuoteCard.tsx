"use client";

import React from "react";
import { TrendingUp, TrendingDown, RefreshCw } from "lucide-react";
import { StockQuoteData } from "@/types/stock";
import { MarketDataBadge } from "./MarketDataBadge";

interface StockQuoteCardProps {
  quote: StockQuoteData | null;
  isLoading?: boolean;
  onRefresh?: () => void;
}

export function StockQuoteCard({ quote, isLoading = false, onRefresh }: StockQuoteCardProps) {
  if (isLoading && !quote) {
    return (
      <div className="w-full rounded-2xl border border-[#E8EAE4] bg-[#FFFFFF] p-6 shadow-xs animate-pulse">
        <div className="h-6 w-32 bg-[#F1F2ED] rounded-md mb-4" />
        <div className="h-10 w-48 bg-[#F1F2ED] rounded-md mb-6" />
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <div className="h-16 bg-[#F1F2ED] rounded-xl" />
          <div className="h-16 bg-[#F1F2ED] rounded-xl" />
          <div className="h-16 bg-[#F1F2ED] rounded-xl" />
          <div className="h-16 bg-[#F1F2ED] rounded-xl" />
        </div>
      </div>
    );
  }

  if (!quote) {
    return (
      <div className="w-full rounded-2xl border border-[#E8EAE4] bg-[#FFFFFF] p-8 text-center text-xs text-[#777D76]">
        No quote data available for this security.
      </div>
    );
  }

  const isPos = (quote.change ?? 0) >= 0;

  // Formatting helpers with strict null safety
  const formatCurrency = (val: number | null | undefined): string => {
    if (val === null || val === undefined) return "Not available";
    return `₹${val.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  const formatVolume = (val: number | null | undefined): string => {
    if (val === null || val === undefined) return "Not available";
    if (val >= 10000000) return `${(val / 10000000).toFixed(2)} Cr`;
    if (val >= 100000) return `${(val / 100000).toFixed(2)} L`;
    if (val >= 1000) return `${(val / 1000).toFixed(1)}k`;
    return val.toLocaleString("en-IN");
  };

  const formatMarketCap = (val: number | null | undefined): string => {
    if (val === null || val === undefined) return "Not available";
    // val is in INR. Convert to Crores (1 Cr = 10,000,000)
    const cr = val / 10000000;
    if (cr >= 100000) return `₹${(cr / 100000).toFixed(2)} Lakh Cr`;
    if (cr >= 1000) return `₹${(cr / 1000).toFixed(2)}k Cr`;
    return `₹${cr.toFixed(2)} Cr`;
  };

  // Day range progress calculation if both low and high exist
  let rangePercent: number | null = null;
  if (
    quote.day_low !== null &&
    quote.day_high !== null &&
    quote.last_price !== null &&
    quote.day_high > quote.day_low
  ) {
    rangePercent = Math.min(
      100,
      Math.max(0, ((quote.last_price - quote.day_low) / (quote.day_high - quote.day_low)) * 100)
    );
  }

  return (
    <div className="w-full rounded-2xl border border-[#E8EAE4] bg-[#FFFFFF] p-6 shadow-xs space-y-6">
      {/* Header: Identity & Status */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="font-mono text-2xl font-bold tracking-tight text-[#20251F]">
              {quote.symbol}
            </h2>
            <span className="rounded-lg bg-[#F1F2ED] px-2 py-0.5 font-mono text-xs font-semibold text-[#176B45]">
              {quote.exchange} Equity
            </span>
            <MarketDataBadge
              status={quote.data_status}
              source={quote.source_name}
              showSource={true}
            />
          </div>
          <div className="mt-1 text-xs text-[#777D76] font-medium">{quote.company_name}</div>
        </div>

        {/* Action: Refresh */}
        {onRefresh && (
          <button
            onClick={onRefresh}
            disabled={isLoading}
            className="self-start inline-flex items-center gap-1.5 rounded-xl border border-[#E8EAE4] bg-[#F8F8F5] px-3 py-1.5 text-xs font-medium text-[#777D76] transition-colors hover:bg-[#F1F2ED] hover:text-[#20251F] cursor-pointer disabled:opacity-50"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? "animate-spin text-[#176B45]" : ""}`} />
            <span>Refresh</span>
          </button>
        )}
      </div>

      {/* Main Price Readout */}
      <div className="flex flex-col gap-2 sm:flex-row sm:items-baseline sm:justify-between border-b border-[#E8EAE4] pb-5">
        <div className="flex items-baseline gap-3">
          <div className="font-mono text-3xl sm:text-4xl font-extrabold text-[#20251F]">
            {formatCurrency(quote.last_price)}
          </div>
          <span className="text-xs text-[#777D76] font-mono">{quote.currency}</span>
        </div>

        <div className="flex items-center gap-2">
          {quote.change !== null && quote.change_percent !== null ? (
            <div
              className={`inline-flex items-center gap-1 font-mono text-sm font-semibold rounded-lg px-2.5 py-1 ${
                isPos ? "bg-[#16834A]/10 text-[#16834A]" : "bg-[#D64A4A]/10 text-[#D64A4A]"
              }`}
            >
              {isPos ? <TrendingUp className="h-4 w-4" /> : <TrendingDown className="h-4 w-4" />}
              <span>
                {isPos ? "+" : ""}
                {quote.change.toFixed(2)} ({isPos ? "+" : ""}
                {quote.change_percent.toFixed(2)}%)
              </span>
            </div>
          ) : (
            <span className="text-xs text-[#777D76]">Change: Not available</span>
          )}

          {quote.previous_close !== null && (
            <span className="text-xs text-[#777D76]">
              Prev: <span className="font-mono font-medium text-[#20251F]">₹{quote.previous_close.toFixed(2)}</span>
            </span>
          )}
        </div>
      </div>

      {/* Day Range Bar (if high & low are present) */}
      {quote.day_low !== null && quote.day_high !== null && rangePercent !== null && (
        <div className="space-y-1.5 rounded-xl border border-[#E8EAE4] bg-[#F8F8F5] p-3 text-xs">
          <div className="flex justify-between font-mono text-[11px] text-[#777D76]">
            <span>Day Low: ₹{quote.day_low.toFixed(2)}</span>
            <span className="font-medium text-[#20251F]">Day Range</span>
            <span>Day High: ₹{quote.day_high.toFixed(2)}</span>
          </div>
          <div className="relative h-2 w-full rounded-full bg-[#E8EAE4]">
            <div
              className="absolute top-0 bottom-0 rounded-full bg-[#176B45]"
              style={{ width: `${rangePercent}%` }}
            />
            <div
              className="absolute top-1/2 -mt-1.5 h-3 w-3 -ml-1.5 rounded-full border-2 border-white bg-[#176B45] shadow-xs"
              style={{ left: `${rangePercent}%` }}
            />
          </div>
        </div>
      )}

      {/* Session Details Grid */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <div className="rounded-xl border border-[#E8EAE4] bg-[#F1F2ED]/40 p-3">
          <span className="text-[11px] text-[#777D76] font-medium">Day Open</span>
          <div className="mt-1 font-mono font-semibold text-sm text-[#20251F]">
            {formatCurrency(quote.open)}
          </div>
        </div>

        <div className="rounded-xl border border-[#E8EAE4] bg-[#F1F2ED]/40 p-3">
          <span className="text-[11px] text-[#777D76] font-medium">Volume</span>
          <div className="mt-1 font-mono font-semibold text-sm text-[#20251F]">
            {formatVolume(quote.volume)}
          </div>
        </div>

        <div className="rounded-xl border border-[#E8EAE4] bg-[#F1F2ED]/40 p-3">
          <span className="text-[11px] text-[#777D76] font-medium">Market Cap</span>
          <div className="mt-1 font-mono font-semibold text-sm text-[#20251F]">
            {formatMarketCap(quote.market_cap)}
          </div>
        </div>

        <div className="rounded-xl border border-[#E8EAE4] bg-[#F1F2ED]/40 p-3">
          <span className="text-[11px] text-[#777D76] font-medium">Previous Close</span>
          <div className="mt-1 font-mono font-semibold text-sm text-[#20251F]">
            {formatCurrency(quote.previous_close)}
          </div>
        </div>
      </div>
    </div>
  );
}
