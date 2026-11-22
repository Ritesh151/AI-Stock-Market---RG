"use client";

import React, { useState, useEffect, useRef } from "react";
import { motion } from "motion/react";
import {
  BarChart2,
  Layers,
  LineChart as LineChartIcon,
  RefreshCw,
  AlertCircle,
} from "lucide-react";
import { stocksApi } from "@/services/stocksApi";
import { HistoricalCandle, HistoricalDataResponse, Exchange } from "@/types/stock";
import { MarketDataBadge } from "./MarketDataBadge";
import { snappyTransition } from "@/lib/motionTokens";

interface StockChartProps {
  symbol: string;
  exchange?: Exchange;
  isPositive?: boolean;
}

const TIMEFRAMES = [
  { id: "1D", label: "1D", defaultInterval: "5m" },
  { id: "5D", label: "5D", defaultInterval: "15m" },
  { id: "1M", label: "1M", defaultInterval: "1d" },
  { id: "3M", label: "3M", defaultInterval: "1d" },
  { id: "6M", label: "6M", defaultInterval: "1d" },
  { id: "1Y", label: "1Y", defaultInterval: "1d" },
  { id: "5Y", label: "5Y", defaultInterval: "1wk" },
] as const;

type ChartType = "area" | "line" | "candle";

export function StockChart({
  symbol = "RELIANCE",
  exchange = "NSE",
  isPositive = true,
}: StockChartProps) {
  const [activeRange, setActiveRange] = useState<string>("1M");
  const [chartType, setChartType] = useState<ChartType>("area");
  const [historyData, setHistoryData] = useState<HistoricalDataResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    let isCancelled = false;

    const loadHistory = async () => {
      try {
        const tfConfig = TIMEFRAMES.find((t) => t.id === activeRange) || TIMEFRAMES[2];
        const res = await stocksApi.getHistory(
          symbol,
          activeRange,
          tfConfig.defaultInterval,
          exchange
        );
        if (!isCancelled) {
          if (res && res.success) {
            setHistoryData(res);
            setError(null);
          } else {
            setError("Failed to load historical data.");
          }
        }
      } catch (err: unknown) {
        if (!isCancelled) {
          const msg = err instanceof Error ? err.message : "Error fetching history";
          setError(msg);
        }
      } finally {
        if (!isCancelled) {
          setIsLoading(false);
        }
      }
    };

    void loadHistory();

    return () => {
      isCancelled = true;
    };
  }, [symbol, exchange, activeRange, reloadKey]);

  const candles: HistoricalCandle[] = historyData?.candles || [];

  // Price and volume math
  const prices = candles.flatMap((c) => [c.low, c.high]);
  const minPrice = prices.length ? Math.min(...prices) : 0;
  const maxPrice = prices.length ? Math.max(...prices) : 100;
  const priceRange = maxPrice - minPrice || 1;

  const volumes = candles.map((c) => c.volume);
  const maxVolume = volumes.length ? Math.max(...volumes, 1) : 1;

  // Chart coordinates
  const chartWidth = 720;
  const chartHeight = 280;
  const paddingX = 24;
  const paddingTop = 20;
  const volumeHeight = 55;
  const paddingBottom = 28;
  const priceChartHeight = chartHeight - paddingTop - paddingBottom - volumeHeight;

  const getX = (index: number) => {
    if (candles.length <= 1) return chartWidth / 2;
    return paddingX + (index / (candles.length - 1)) * (chartWidth - paddingX * 2);
  };

  const getY = (price: number) => {
    return (
      paddingTop +
      (1 - (price - minPrice) / priceRange) * priceChartHeight
    );
  };

  const getVolY = (vol: number) => {
    const volRatio = Math.min(1, vol / maxVolume);
    const bottomY = chartHeight - paddingBottom;
    return bottomY - volRatio * volumeHeight;
  };

  // Generate SVG paths
  const linePoints = candles.map((c, i) => ({
    x: getX(i),
    y: getY(c.close),
  }));

  const pathD = linePoints.reduce(
    (acc, pt, idx) => (idx === 0 ? `M ${pt.x} ${pt.y}` : `${acc} L ${pt.x} ${pt.y}`),
    ""
  );

  const bottomBaseY = chartHeight - paddingBottom - volumeHeight;
  const areaD =
    linePoints.length > 0
      ? `${pathD} L ${linePoints[linePoints.length - 1].x} ${bottomBaseY} L ${linePoints[0].x} ${bottomBaseY} Z`
      : "";

  const activeCandle =
    hoveredIndex !== null && candles[hoveredIndex]
      ? candles[hoveredIndex]
      : candles[candles.length - 1];

  const strokeColor = isPositive ? "#16834A" : "#D64A4A";
  const gradientId = `chartGradient-${symbol}-${activeRange}`;

  // Format date/time for labels
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
      return d.toLocaleDateString("en-IN", {
        month: "short",
        day: "numeric",
      });
    } catch {
      return isoString;
    }
  };

  return (
    <div className="space-y-4">
      {/* Top Bar: Timeframe Buttons, Chart Type Toggle, & Data Attribution */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        {/* Active Candle Readout */}
        <div>
          {activeCandle ? (
            <div className="flex flex-wrap items-baseline gap-2">
              <span className="font-mono text-2xl font-bold text-[#20251F]">
                ₹{activeCandle.close.toFixed(2)}
              </span>
              <span className="text-xs text-[#777D76]">
                {formatCandleTime(activeCandle.timestamp)}
              </span>
              <div className="hidden sm:flex items-center gap-2 text-[11px] font-mono text-[#777D76] ml-2">
                <span>O: ₹{activeCandle.open.toFixed(2)}</span>
                <span>H: ₹{activeCandle.high.toFixed(2)}</span>
                <span>L: ₹{activeCandle.low.toFixed(2)}</span>
                <span>Vol: {(activeCandle.volume / 1000).toFixed(0)}k</span>
              </div>
            </div>
          ) : (
            <span className="text-xs text-[#777D76]">No price points available</span>
          )}
        </div>

        {/* Controls: Chart Type & Timeframe */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Chart Type Toggle */}
          <div className="inline-flex rounded-xl border border-[#E8EAE4] bg-[#F1F2ED]/60 p-0.5">
            <button
              onClick={() => setChartType("area")}
              className={`rounded-lg p-1.5 transition-colors cursor-pointer ${
                chartType === "area"
                  ? "bg-[#FFFFFF] text-[#176B45] shadow-xs"
                  : "text-[#777D76] hover:text-[#20251F]"
              }`}
              title="Area Chart"
              aria-label="Area Chart"
            >
              <Layers className="h-3.5 w-3.5" />
            </button>
            <button
              onClick={() => setChartType("line")}
              className={`rounded-lg p-1.5 transition-colors cursor-pointer ${
                chartType === "line"
                  ? "bg-[#FFFFFF] text-[#176B45] shadow-xs"
                  : "text-[#777D76] hover:text-[#20251F]"
              }`}
              title="Line Chart"
              aria-label="Line Chart"
            >
              <LineChartIcon className="h-3.5 w-3.5" />
            </button>
            <button
              onClick={() => setChartType("candle")}
              className={`rounded-lg p-1.5 transition-colors cursor-pointer ${
                chartType === "candle"
                  ? "bg-[#FFFFFF] text-[#176B45] shadow-xs"
                  : "text-[#777D76] hover:text-[#20251F]"
              }`}
              title="Candlestick Chart"
              aria-label="Candlestick Chart"
            >
              <BarChart2 className="h-3.5 w-3.5" />
            </button>
          </div>

          {/* Timeframe Selectors */}
          <div className="inline-flex rounded-xl border border-[#E8EAE4] bg-[#F1F2ED]/60 p-1">
            {TIMEFRAMES.map((tf) => (
              <button
                key={tf.id}
                onClick={() => setActiveRange(tf.id)}
                className="relative px-2.5 py-1 text-xs font-semibold text-[#777D76] transition-colors hover:text-[#20251F] cursor-pointer"
              >
                {activeRange === tf.id && (
                  <motion.div
                    layoutId="activeRangeBadge"
                    className="absolute inset-0 rounded-lg bg-[#FFFFFF] shadow-xs border border-[#E8EAE4]"
                    transition={snappyTransition}
                  />
                )}
                <span className={`relative z-10 ${activeRange === tf.id ? "text-[#176B45]" : ""}`}>
                  {tf.label}
                </span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Chart Surface */}
      <div className="relative w-full rounded-2xl border border-[#E8EAE4] bg-[#FFFFFF] p-3 shadow-xs">
        {isLoading && (
          <div className="absolute inset-0 z-20 flex flex-col items-center justify-center rounded-2xl bg-[#FFFFFF]/80 backdrop-blur-xs">
            <RefreshCw className="h-6 w-6 animate-spin text-[#176B45]" />
            <span className="mt-2 text-xs font-medium text-[#777D76]">
              Loading {activeRange} historical prices...
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
              <span>Retry History</span>
            </button>
          </div>
        )}

        {!error && candles.length === 0 && !isLoading && (
          <div className="py-20 text-center text-xs text-[#777D76]">
            No historical candles recorded for this timeframe.
          </div>
        )}

        {!error && candles.length > 0 && (
          <div className="relative w-full overflow-hidden">
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
                const y = paddingTop + pct * priceChartHeight;
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
                      ₹{priceLabel.toFixed(1)}
                    </text>
                  </g>
                );
              })}

              {/* Volume Bars */}
              {candles.map((c, i) => {
                const x = getX(i);
                const barWidth = Math.max(2, (chartWidth - paddingX * 2) / candles.length * 0.7);
                const volY = getVolY(c.volume);
                const bottomY = chartHeight - paddingBottom;
                const barHeight = Math.max(2, bottomY - volY);
                const isCandleGreen = c.close >= c.open;

                return (
                  <rect
                    key={`vol-${i}`}
                    x={x - barWidth / 2}
                    y={volY}
                    width={barWidth}
                    height={barHeight}
                    fill={isCandleGreen ? "#16834A" : "#D64A4A"}
                    opacity={hoveredIndex === i ? 0.6 : 0.25}
                  />
                );
              })}

              {/* Volume Label separator */}
              <line
                x1={paddingX}
                y1={chartHeight - paddingBottom - volumeHeight}
                x2={chartWidth - paddingX}
                y2={chartHeight - paddingBottom - volumeHeight}
                stroke="#E8EAE4"
                strokeWidth="1"
              />
              <text
                x={paddingX}
                y={chartHeight - paddingBottom - volumeHeight + 11}
                className="fill-[#777D76] font-mono text-[8px] uppercase tracking-wider"
              >
                Volume Profile
              </text>

              {/* Area / Line Render */}
              {(chartType === "area" || chartType === "line") && (
                <>
                  {chartType === "area" && areaD && (
                    <path d={areaD} fill={`url(#${gradientId})`} />
                  )}
                  <motion.path
                    key={`${symbol}-${activeRange}-${chartType}`}
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
                </>
              )}

              {/* Candlestick Render */}
              {chartType === "candle" &&
                candles.map((c, i) => {
                  const x = getX(i);
                  const openY = getY(c.open);
                  const closeY = getY(c.close);
                  const highY = getY(c.high);
                  const lowY = getY(c.low);
                  const isUp = c.close >= c.open;
                  const candleBodyTop = Math.min(openY, closeY);
                  const candleBodyHeight = Math.max(2, Math.abs(closeY - openY));
                  const candleWidth = Math.max(3, (chartWidth - paddingX * 2) / candles.length * 0.7);

                  return (
                    <g key={`candle-${i}`}>
                      {/* High-Low Wick */}
                      <line
                        x1={x}
                        y1={highY}
                        x2={x}
                        y2={lowY}
                        stroke={isUp ? "#16834A" : "#D64A4A"}
                        strokeWidth="1.2"
                      />
                      {/* Candle Body */}
                      <rect
                        x={x - candleWidth / 2}
                        y={candleBodyTop}
                        width={candleWidth}
                        height={candleBodyHeight}
                        fill={isUp ? "#16834A" : "#D64A4A"}
                        stroke={isUp ? "#16834A" : "#D64A4A"}
                        strokeWidth="0.5"
                        rx="1"
                      />
                    </g>
                  );
                })}

              {/* Interactive Hover Crosshair & Data Hits */}
              {hoveredIndex !== null && candles[hoveredIndex] && (
                <g>
                  {/* Vertical Crosshair */}
                  <line
                    x1={getX(hoveredIndex)}
                    y1={paddingTop}
                    x2={getX(hoveredIndex)}
                    y2={chartHeight - paddingBottom}
                    stroke="#176B45"
                    strokeDasharray="2 2"
                    strokeWidth="1.2"
                  />
                  {/* Active Price Point */}
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

              {/* Mouse Interaction Catchers */}
              {candles.map((_, i) => {
                const segWidth = (chartWidth - paddingX * 2) / candles.length;
                const x = getX(i) - segWidth / 2;
                return (
                  <rect
                    key={`hit-${i}`}
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

        {/* Footer info: Freshness & source */}
        {historyData && (
          <div className="mt-3 flex items-center justify-between border-t border-[#E8EAE4] pt-2 px-1 text-[11px] text-[#777D76]">
            <MarketDataBadge
              status={historyData.data_status}
              source={historyData.source_name}
              showSource={true}
            />
            <span className="font-mono text-[10px]">
              {candles.length} candles ({activeRange} @ {historyData.interval})
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
