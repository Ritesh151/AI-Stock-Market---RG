"use client";

import React, { useState } from "react";
import { motion } from "motion/react";
import {
  Building2,
  AlertCircle,
  RefreshCw,
} from "lucide-react";
import { Card } from "@/components/ui/Card";
import { StockChart } from "@/components/stocks/StockChart";
import { StockSearch } from "@/components/stocks/StockSearch";
import { StockQuoteCard } from "@/components/stocks/StockQuoteCard";
import { StockDetails } from "@/components/stocks/StockDetails";
import { Watchlist } from "@/components/stocks/Watchlist";
import { MarketIndexBar } from "@/components/stocks/MarketIndexBar";
import { useStockData } from "@/hooks/useStockData";
import { pageContainerVariants, slideUpVariants } from "@/lib/motionTokens";
import { Exchange } from "@/types/stock";

const POPULAR_STOCKS = [
  { symbol: "RELIANCE", name: "Reliance Industries", exchange: "NSE" as Exchange },
  { symbol: "TCS", name: "Tata Consultancy Services", exchange: "NSE" as Exchange },
  { symbol: "INFY", name: "Infosys Ltd", exchange: "NSE" as Exchange },
  { symbol: "HDFCBANK", name: "HDFC Bank Ltd", exchange: "NSE" as Exchange },
  { symbol: "TATAMOTORS", name: "Tata Motors Ltd", exchange: "NSE" as Exchange },
];

export default function StockPricePage() {
  const {
    symbol,
    exchange,
    quote,
    profile,
    watchlist,
    isInWatchlist,
    isQuoteLoading,
    isWatchlistLoading,
    error,
    selectStock,
    refresh,
    toggleWatchlist,
    removeFromWatchlist,
  } = useStockData("RELIANCE", "NSE");

  const [activeTab, setActiveTab] = useState<"screener" | "watchlist">("watchlist");

  const isPos = (quote?.change ?? 0) >= 0;

  return (
    <motion.div
      variants={pageContainerVariants}
      initial="hidden"
      animate="visible"
      className="mx-auto max-w-7xl space-y-6"
    >
      {/* 1. Indian Market Status & Benchmark Ticker Bar */}
      <motion.div variants={slideUpVariants}>
        <MarketIndexBar />
      </motion.div>

      {/* 2. Page Header & Real-Time Stock Search */}
      <motion.div
        variants={slideUpVariants}
        className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"
      >
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-[#20251F]">
            Indian Stock Intelligence & Screener
          </h1>
          <p className="text-xs text-[#777D76]">
            Real-time & delayed quotes, institutional indicators, and verified data provenance for NSE/BSE securities.
          </p>
        </div>

        {/* Search Bar */}
        <div className="w-full sm:w-80">
          <StockSearch
            onSelectStock={(sym, ex) => selectStock(sym, ex)}
            currentSymbol={symbol}
          />
        </div>
      </motion.div>

      {/* 3. Error Banner if quote retrieval failed */}
      {error && (
        <motion.div
          variants={slideUpVariants}
          className="flex items-center justify-between rounded-xl border border-[#D64A4A]/30 bg-[#D64A4A]/10 p-3.5 text-xs text-[#D64A4A]"
        >
          <div className="flex items-center gap-2">
            <AlertCircle className="h-4 w-4" />
            <span>{error}</span>
          </div>
          <button
            onClick={refresh}
            className="inline-flex items-center gap-1 font-semibold underline hover:opacity-80 cursor-pointer"
          >
            <RefreshCw className="h-3 w-3" />
            <span>Try Again</span>
          </button>
        </motion.div>
      )}

      {/* 4. Two-Column Layout */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        {/* Left Column: Watchlist & Quick Screener (5 cols) */}
        <motion.div variants={slideUpVariants} className="space-y-4 lg:col-span-5">
          {/* Navigation Tabs */}
          <div className="flex rounded-xl border border-[#E8EAE4] bg-[#FFFFFF] p-1 shadow-xs">
            <button
              onClick={() => setActiveTab("watchlist")}
              className={`flex-1 rounded-lg py-2 text-xs font-semibold transition-all cursor-pointer ${
                activeTab === "watchlist"
                  ? "bg-[#176B45] text-white shadow-xs"
                  : "text-[#777D76] hover:text-[#20251F]"
              }`}
            >
              Watchlist ({watchlist.length})
            </button>
            <button
              onClick={() => setActiveTab("screener")}
              className={`flex-1 rounded-lg py-2 text-xs font-semibold transition-all cursor-pointer ${
                activeTab === "screener"
                  ? "bg-[#176B45] text-white shadow-xs"
                  : "text-[#777D76] hover:text-[#20251F]"
              }`}
            >
              Popular Equities
            </button>
          </div>

          {/* Active Tab View */}
          {activeTab === "watchlist" ? (
            <Watchlist
              items={watchlist}
              selectedSymbol={symbol}
              onSelectStock={(sym, ex) => selectStock(sym, ex)}
              onRemoveItem={(sym) => removeFromWatchlist(sym)}
              isLoading={isWatchlistLoading}
            />
          ) : (
            <Card className="p-4 space-y-3">
              <div className="flex items-center justify-between border-b border-[#E8EAE4] pb-2.5">
                <span className="text-xs font-semibold text-[#20251F]">
                  Top Traded Indian Bluechips
                </span>
                <span className="text-[11px] text-[#777D76]">NSE / BSE</span>
              </div>

              <div className="space-y-1.5">
                {POPULAR_STOCKS.map((stk) => {
                  const isSelected = stk.symbol === symbol;
                  return (
                    <div
                      key={stk.symbol}
                      onClick={() => selectStock(stk.symbol, stk.exchange)}
                      className={`flex items-center justify-between rounded-xl p-2.5 cursor-pointer transition-all ${
                        isSelected
                          ? "bg-[#176B45]/10 border border-[#176B45]/30"
                          : "border border-transparent hover:border-[#E8EAE4] hover:bg-[#F8F8F5]"
                      }`}
                    >
                      <div className="flex items-center gap-2.5">
                        <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-[#E8EAE4]/60 text-[#176B45]">
                          <Building2 className="h-3.5 w-3.5" />
                        </div>
                        <div>
                          <div className="flex items-center gap-1.5">
                            <span className="font-mono text-xs font-bold text-[#20251F]">
                              {stk.symbol}
                            </span>
                            <span className="rounded bg-[#F1F2ED] px-1 py-0.2 text-[9px] font-bold text-[#176B45]">
                              {stk.exchange}
                            </span>
                          </div>
                          <div className="text-[11px] text-[#777D76]">{stk.name}</div>
                        </div>
                      </div>

                      <span className="text-[11px] font-medium text-[#176B45] hover:underline">
                        View Quote &rarr;
                      </span>
                    </div>
                  );
                })}
              </div>
            </Card>
          )}

          {/* Market Freshness Assurance Card */}
          <Card className="p-4 bg-[#F8F8F5] border-[#E8EAE4] space-y-2">
            <h4 className="text-xs font-semibold text-[#20251F]">
              Data Freshness & Provenance Standard
            </h4>
            <p className="text-[11px] text-[#777D76] leading-relaxed">
              RG AI enforces transparent reporting of market feeds. In compliance with exchange guidelines, feeds during regular market hours (09:15–15:30 IST) are labelled as <span className="font-semibold text-[#20251F]">DELAYED (~15m)</span>. Unsubstantiated metrics are never fabricated and are marked as Not available.
            </p>
          </Card>
        </motion.div>

        {/* Right Column: Quote Card, Interactive Chart & Profile (7 cols) */}
        <motion.div variants={slideUpVariants} className="space-y-6 lg:col-span-7">
          {/* Quote Card */}
          <StockQuoteCard
            quote={quote}
            isLoading={isQuoteLoading}
            onRefresh={refresh}
          />

          {/* Interactive Chart */}
          <Card className="p-6">
            <StockChart
              symbol={symbol}
              exchange={exchange}
              isPositive={isPos}
            />
          </Card>

          {/* Company Profile, Ratios & RG AI Bridge */}
          <StockDetails
            profile={profile}
            symbol={symbol}
            exchange={exchange}
            isInWatchlist={isInWatchlist}
            onToggleWatchlist={() => toggleWatchlist(symbol, exchange)}
            isWatchlistLoading={isWatchlistLoading}
          />
        </motion.div>
      </div>
    </motion.div>
  );
}
