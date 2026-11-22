"use client";

import React, { useState } from "react";
import { motion } from "motion/react";
import { AlertCircle, RefreshCw } from "lucide-react";
import { pageContainerVariants, slideUpVariants } from "@/lib/motionTokens";

import { useMarketOverview } from "@/features/overview/hooks/useMarketOverview";
import { OverviewHeader } from "@/features/overview/components/OverviewHeader";
import { MarketIndices } from "@/features/overview/components/MarketIndices";
import { MarketActivityChart } from "@/features/overview/components/MarketActivityChart";
import { MarketSentiment } from "@/features/overview/components/MarketSentiment";
import { TopGainers } from "@/features/overview/components/TopGainers";
import { TopLosers } from "@/features/overview/components/TopLosers";
import { MostActiveStocks } from "@/features/overview/components/MostActiveStocks";
import { WatchlistOverview } from "@/features/overview/components/WatchlistOverview";
import { RecentAIAnalyses } from "@/features/overview/components/RecentAIAnalyses";
import { MarketNews } from "@/features/overview/components/MarketNews";
import { MarketStatusCard } from "@/features/overview/components/MarketStatusCard";

export default function OverviewPage() {
  const { data, isLoading, isRefreshing, error, refresh } = useMarketOverview(60000);
  const [selectedChartIndex, setSelectedChartIndex] = useState<string>("^NSEI");

  return (
    <motion.div
      variants={pageContainerVariants}
      initial="hidden"
      animate="visible"
      className="mx-auto max-w-7xl space-y-8"
    >
      {/* TOP: Dashboard Title, Live Market Status Pill, and Refresh Control */}
      <motion.div variants={slideUpVariants}>
        <OverviewHeader
          status={data?.market_status || null}
          lastUpdated={data?.timestamp || null}
          onRefresh={refresh}
          isRefreshing={isRefreshing}
        />
      </motion.div>

      {/* Error Notice Banner if backend failed */}
      {error && (
        <motion.div
          variants={slideUpVariants}
          className="flex items-center justify-between rounded-xl border border-[#D64A4A]/30 bg-[#D64A4A]/10 p-4 text-xs text-[#D64A4A]"
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

      {/* SECTION 1: NIFTY 50, SENSEX, BANK NIFTY Cards */}
      <motion.div variants={slideUpVariants} className="space-y-2">
        <div className="flex items-center justify-between px-1">
          <span className="text-xs font-bold text-[#777D76] uppercase tracking-wider">
            Benchmark Indices
          </span>
          <span className="text-[11px] text-[#777D76]">
            Select an index to inspect historical trend
          </span>
        </div>
        <MarketIndices
          indices={data?.indices || []}
          selectedIndex={selectedChartIndex}
          onSelectIndex={(sym) => setSelectedChartIndex(sym)}
          isLoading={isLoading}
        />
      </motion.div>

      {/* SECTION 2: Market Trend Chart (8 cols) & Market Sentiment (4 cols) */}
      <motion.div
        variants={slideUpVariants}
        className="grid grid-cols-1 gap-6 lg:grid-cols-12"
      >
        <div className="lg:col-span-8">
          <MarketActivityChart
            selectedIndex={selectedChartIndex}
            onSelectIndex={(sym) => setSelectedChartIndex(sym)}
          />
        </div>
        <div className="space-y-6 lg:col-span-4">
          <MarketSentiment
            sentiment={data?.sentiment || null}
            isLoading={isLoading}
          />
          <MarketStatusCard status={data?.market_status || null} />
        </div>
      </motion.div>

      {/* SECTION 3: Top Gainers & Top Losers */}
      <motion.div
        variants={slideUpVariants}
        className="grid grid-cols-1 gap-6 sm:grid-cols-2"
      >
        <TopGainers
          gainers={data?.movers?.gainers || []}
          isLoading={isLoading}
        />
        <TopLosers
          losers={data?.movers?.losers || []}
          isLoading={isLoading}
        />
      </motion.div>

      {/* SECTION 4: Most Active Stocks & Watchlist Overview */}
      <motion.div
        variants={slideUpVariants}
        className="grid grid-cols-1 gap-6 sm:grid-cols-2"
      >
        <MostActiveStocks
          stocks={data?.movers?.most_active || []}
          rankingMetric={data?.movers?.ranking_metric}
          isLoading={isLoading}
        />
        <WatchlistOverview />
      </motion.div>

      {/* SECTION 5: Recent RG AI Analyses & Market News */}
      <motion.div
        variants={slideUpVariants}
        className="grid grid-cols-1 gap-6 sm:grid-cols-2"
      >
        <RecentAIAnalyses />
        <MarketNews
          news={data?.news || null}
          isLoading={isLoading}
        />
      </motion.div>
    </motion.div>
  );
}
