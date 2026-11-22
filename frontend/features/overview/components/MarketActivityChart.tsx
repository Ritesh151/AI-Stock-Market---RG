"use client";

import React, { useState, useEffect, useRef } from "react";
import { motion } from "motion/react";
import {
  Layers,
  LineChart as LineChartIcon,
  RefreshCw,
  AlertCircle,
} from "lucide-react";
import { stocksApi } from "@/services/stocksApi";
import { HistoricalCandle, HistoricalDataResponse } from "@/types/stock";
import { MarketDataBadge } from "@/components/stocks/MarketDataBadge";
import { Card } from "@/components/ui/Card";
import { snappyTransition } from "@/lib/motionTokens";

interface MarketActivityChartProps {
  selectedIndex: string;
  onSelectIndex: (symbol: string) => void;
}

const INDEX_TABS = [
  { symbol: "^NSEI", label: "NIFTY 50", exchange: "NSE" },
  { symbol: "^BSESN", label: "SENSEX", exchange: "BSE" },
  { symbol: "^NSEBANK", label: "BANK NIFTY", exchange: "NSE" },
];

const TIMEFRAMES = [
  { id: "1D", label: "1D", interval: "5m" },
  { id: "5D", label: "5D", interval: "15m" },
  { id: "1M", label: "1M", interval: "1d" },
  { id: "6M", label: "6M", interval: "1d" },
  { id: "1Y", label: "1Y", interval: "1d" },
];

export function MarketActivityChart({
  selectedIndex = "^NSEI",
  onSelectIndex,
}: MarketActivityChartProps) {
  const [activeRange, setActiveRange] = useState<string>("1M");
  const [chartMode, setChartMode] = useState<"area" | "line">("area");
  const [historyData, setHistoryData] = useState<HistoricalDataResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const [reloadKey, setReloadKey] = useState<number>(0);

  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    let isCancelled = false;

    async function loadHistory() {
      try {
        const tf = TIMEFRAMES.find((t) => t.id === activeRange) || TIMEFRAMES[2];
        const res = await stocksApi.getHistory(selectedIndex, activeRange, tf.interval, "NSE");
        if (!isCancelled) {
          if (res && res.success) {
            setHistoryData(res);
            setError(null);
          } else {
            setError("Failed to load benchmark history.");
          }
        }
      } catch (err: unknown) {
        if (!isCancelled) {
          setError(err instanceof Error ? err.message : "Error loading chart data");
        }
      } finally {
        if (!isCancelled) {
          setIsLoading(false);
        }
      }
    }

    void loadHistory();

    return () => {
      isCancelled = true;
    };
  }, [selectedIndex, activeRange, reloadKey]);

  const candles: HistoricalCandle[] = historyData?.candles || [];
  const prices = candles.flatMap((c) => [c.low, c.high]);
  const minPrice = prices.length ? Math.min(...prices) : 0;
  const maxPrice = prices.length ? Math.max(...prices) : 100;
  const priceRange = maxPrice - minPrice || 1;

  // Chart coordinate geometry
  const chartWidth = 720;
  const chartHeight = 260;
  const paddingX = 24;
  const paddingTop = 20;
  const paddingBottom = 28;
  const chartPlotHeight = chartHeight - paddingTop - paddingBottom;

  const getX = (index: number) => {
    if (candles.length <= 1) return chartWidth / 2;
    return paddingX + (index / (candles.length - 1)) * (chartWidth - paddingX * 2);
  };

  const getY = (price: number) => {
    return paddingTop + (1 - (price - minPrice) / priceRange) * chartPlotHeight;
  };

  const linePoints = candles.map((c, i) => ({
    x: getX(i),
    y: getY(c.close),
  }));

  const pathD = linePoints.reduce(
    (acc, pt, idx) => (idx === 0 ? `M ${pt.x} ${pt.y}` : `${acc} L ${pt.x} ${pt.y}`),
    ""
  );

  const baseY = chartHeight - paddingBottom;
  const areaD =
    linePoints.length > 0
      ? `${pathD} L ${linePoints[linePoints.length - 1].x} ${baseY} L ${linePoints[0].x} ${baseY} Z`
      : "";

  const activeCandle =
    hoveredIndex !== null && candles[hoveredIndex]
      ? candles[hoveredIndex]
      : candles[candles.length - 1];

  const firstCandle = candles[0];
  const isPositive =
    firstCandle && activeCandle ? activeCandle.close >= firstCandle.open : true;
  const strokeColor = isPositive ? "#16834A" : "#D64A4A";
  const gradientId = `marketTrendGradient-${selectedIndex}-${activeRange}`;

  const formatCandleTime = (isoString: string) => {
    try {
      const d = new Date(isoString);
      if (activeRange === "1D" || activeRange === "5D") {
        return d.toLocaleTimeString("en-IN", {
          hour: "2-digit",
          minute: "2-digit",
          hour12: false,
        });
      }
      return d.toLocaleDateString("en-IN", { month: "short", day: "numeric" });
    } catch {
      return isoString;
    }
  };

  return (
    <Card className="p-6 space-y-5">
      {/* Top Header: Index Tabs & Timeframe Buttons */}
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between border-b border-[#E8EAE4] pb-4">
        {/* Index Selector Tabs */}
        <div className="flex items-center gap-1.5 rounded-xl border border-[#E8EAE4] bg-[#F8F8F5] p-1">
          {INDEX_TABS.map((tab) => {
            const isTabActive = selectedIndex === tab.symbol;
            return (
              <button
                key={tab.symbol}
                onClick={() => {
                  onSelectIndex(tab.symbol);
                  setIsLoading(true);
                  setHoveredIndex(null);
                }}
                className={`relative rounded-lg px-3 py-1.5 text-xs font-bold transition-all cursor-pointer ${
                  isTabActive
                    ? "bg-[#FFFFFF] text-[#176B45] shadow-xs"
                    : "text-[#777D76] hover:text-[#20251F]"
                }`}
              >
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Readout and Timeframe controls */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Active Readout */}
          {activeCandle && (
            <div className="flex items-baseline gap-2">
              <span className="font-mono text-xl font-bold text-[#20251F]">
                {activeCandle.close.toLocaleString("en-IN", {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })}
              </span>
              <span className="text-[11px] text-[#777D76] font-mono">
                {formatCandleTime(activeCandle.timestamp)}
              </span>
            </div>
          )}

          {/* Timeframe selector */}
          <div className="inline-flex rounded-xl border border-[#E8EAE4] bg-[#F1F2ED]/60 p-0.5">
            {TIMEFRAMES.map((tf) => (
              <button
                key={tf.id}
                onClick={() => {
                  setActiveRange(tf.id);
                  setIsLoading(true);
                  setHoveredIndex(null);
                }}
                className={`relative px-2.5 py-1 text-xs font-semibold transition-colors cursor-pointer ${
                  activeRange === tf.id
                    ? "text-[#176B45] font-bold"
                    : "text-[#777D76] hover:text-[#20251F]"
                }`}
              >
                {activeRange === tf.id && (
                  <motion.div
                    layoutId="activeMarketRange"
                    className="absolute inset-0 rounded-lg bg-[#FFFFFF] shadow-xs border border-[#E8EAE4]"
                    transition={snappyTransition}
                  />
                )}
                <span className="relative z-10">{tf.label}</span>
              </button>
            ))}
          </div>

          {/* Area / Line Toggle */}
          <div className="inline-flex rounded-xl border border-[#E8EAE4] bg-[#F1F2ED]/60 p-0.5">
            <button
              onClick={() => setChartMode("area")}
              className={`rounded-lg p-1.5 transition-colors cursor-pointer ${
                chartMode === "area"
                  ? "bg-[#FFFFFF] text-[#176B45] shadow-xs"
                  : "text-[#777D76] hover:text-[#20251F]"
              }`}
              title="Area Mode"
              aria-label="Area Mode"
            >
              <Layers className="h-3.5 w-3.5" />
            </button>
            <button
              onClick={() => setChartMode("line")}
              className={`rounded-lg p-1.5 transition-colors cursor-pointer ${
                chartMode === "line"
                  ? "bg-[#FFFFFF] text-[#176B45] shadow-xs"
                  : "text-[#777D76] hover:text-[#20251F]"
              }`}
              title="Line Mode"
              aria-label="Line Mode"
            >
              <LineChartIcon className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* SVG Chart Surface */}
      <div className="relative w-full overflow-hidden">
        {isLoading && (
          <div className="absolute inset-0 z-20 flex flex-col items-center justify-center rounded-2xl bg-[#FFFFFF]/85 backdrop-blur-xs">
            <RefreshCw className="h-6 w-6 animate-spin text-[#176B45]" />
            <span className="mt-2 text-xs font-medium text-[#777D76]">
              Loading historical trend...
            </span>
          </div>
        )}

        {error && !isLoading && (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <AlertCircle className="h-7 w-7 text-[#D64A4A] mb-2" />
            <p className="text-xs font-semibold text-[#20251F]">{error}</p>
            <button
              onClick={() => {
                setIsLoading(true);
                setError(null);
                setReloadKey((prev) => prev + 1);
              }}
              className="mt-3 inline-flex items-center gap-1.5 rounded-xl border border-[#E8EAE4] bg-[#F8F8F5] px-3 py-1.5 text-xs font-medium text-[#176B45] hover:bg-[#F1F2ED] cursor-pointer"
            >
              <RefreshCw className="h-3 w-3" />
              <span>Retry Trend Chart</span>
            </button>
          </div>
        )}

        {!error && candles.length === 0 && !isLoading && (
          <div className="py-20 text-center text-xs text-[#777D76]">
            No historical trend points available for this index.
          </div>
        )}

        {!error && candles.length > 0 && (
          <div>
            <svg
              ref={svgRef}
              viewBox={`0 0 ${chartWidth} ${chartHeight}`}
              className="w-full h-auto overflow-visible select-none"
              onMouseLeave={() => setHoveredIndex(null)}
            >
              <defs>
                <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
                  <stop
                    offset="0%"
                    stopColor={strokeColor}
                    stopOpacity={isPositive ? 0.22 : 0.16}
                  />
                  <stop offset="100%" stopColor={strokeColor} stopOpacity={0.0} />
                </linearGradient>
              </defs>

              {/* Grid Lines */}
              {[0, 0.33, 0.66, 1].map((pct, idx) => {
                const y = paddingTop + pct * chartPlotHeight;
                const priceLabel = maxPrice - pct * priceRange;
                return (
                  <g key={idx}>
                    <line
                      x1={paddingX}
                      y1={y}
                      x2={chartWidth - paddingX}
                      y2={y}
                      stroke="#F1F2ED"
                      strokeDasharray="3 3"
                      strokeWidth="1"
                    />
                    <text
                      x={chartWidth - paddingX}
                      y={y - 3}
                      textAnchor="end"
                      className="fill-[#777D76] font-mono text-[9px]"
                    >
                      {priceLabel.toLocaleString("en-IN", { maximumFractionDigits: 1 })}
                    </text>
                  </g>
                );
              })}

              {/* Area fill */}
              {chartMode === "area" && areaD && (
                <path d={areaD} fill={`url(#${gradientId})`} />
              )}

              {/* Smooth Trend Line */}
              <motion.path
                key={`${selectedIndex}-${activeRange}-${chartMode}`}
                initial={{ pathLength: 0.1, opacity: 0.3 }}
                animate={{ pathLength: 1, opacity: 1 }}
                transition={{ duration: 0.45, ease: "easeOut" }}
                d={pathD}
                fill="none"
                stroke={strokeColor}
                strokeWidth="2.2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />

              {/* Hover Crosshair & Node */}
              {hoveredIndex !== null && candles[hoveredIndex] && (
                <g>
                  <line
                    x1={getX(hoveredIndex)}
                    y1={paddingTop}
                    x2={getX(hoveredIndex)}
                    y2={chartHeight - paddingBottom}
                    stroke="#176B45"
                    strokeDasharray="2 2"
                    strokeWidth="1.2"
                  />
                  <circle
                    cx={getX(hoveredIndex)}
                    cy={getY(candles[hoveredIndex].close)}
                    r="5"
                    fill="#FFFFFF"
                    stroke="#176B45"
                    strokeWidth="2.5"
                  />
                </g>
              )}

              {/* Interaction Slices */}
              {candles.map((_, i) => {
                const segWidth = (chartWidth - paddingX * 2) / candles.length;
                const x = getX(i) - segWidth / 2;
                return (
                  <rect
                    key={`slice-${i}`}
                    x={x}
                    y={paddingTop}
                    width={segWidth}
                    height={chartHeight - paddingTop}
                    fill="transparent"
                    className="cursor-crosshair"
                    onMouseEnter={() => setHoveredIndex(i)}
                  />
                );
              })}
            </svg>

            {/* X-Axis Time Labels */}
            <div className="flex justify-between px-6 pt-1 text-[10px] font-mono text-[#777D76]">
              {candles.length > 0 && (
                <>
                  <span>{formatCandleTime(candles[0].timestamp)}</span>
                  {candles.length > 2 && (
                    <span>{formatCandleTime(candles[Math.floor(candles.length / 2)].timestamp)}</span>
                  )}
                  <span>{formatCandleTime(candles[candles.length - 1].timestamp)}</span>
                </>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Footer attribution */}
      {historyData && (
        <div className="flex items-center justify-between border-t border-[#E8EAE4] pt-3 text-[11px] text-[#777D76]">
          <MarketDataBadge
            status={historyData.data_status}
            source={historyData.source_name}
            showSource={true}
          />
          <span className="font-mono text-[10px]">
            {candles.length} periods ({activeRange})
          </span>
        </div>
      )}
    </Card>
  );
}
