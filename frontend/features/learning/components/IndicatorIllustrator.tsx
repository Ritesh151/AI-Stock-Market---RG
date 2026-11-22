"use client";

import React from "react";
import { ShieldAlert } from "lucide-react";

interface IndicatorIllustratorProps {
  illustrationKey?: string;
  className?: string;
}

/**
 * Programmatic SVG Educational Technical Indicator Illustrator.
 * Renders RSI, MACD, Moving Averages, Support/Resistance, and Volume diagrams.
 */
export const IndicatorIllustrator: React.FC<IndicatorIllustratorProps> = ({
  illustrationKey = "indicator_rsi_divergence",
  className = "",
}) => {
  const renderDiagram = () => {
    switch (illustrationKey) {
      case "indicator_rsi_divergence":
        return (
          <g>
            {/* Top Price Action Panel */}
            <g transform="translate(40, 20)">
              <text x="10" y="15" fill="#20251F" fontSize="11" fontWeight="700">Price Chart (Higher High)</text>
              <path d="M 40 70 L 100 45 L 140 60 L 220 30 L 260 50" fill="none" stroke="#20251F" strokeWidth="2.5" />
              {/* Divergence trendline across price peaks */}
              <line x1="100" y1="45" x2="220" y2="30" stroke="#16834A" strokeWidth="2" strokeDasharray="3 3" />
              <circle cx="100" cy="45" r="3.5" fill="#16834A" />
              <circle cx="220" cy="30" r="3.5" fill="#16834A" />
              <text x="160" y="30" fill="#16834A" fontSize="10" fontWeight="600">Higher Peak</text>
            </g>

            {/* Bottom RSI Panel */}
            <g transform="translate(40, 105)">
              <rect x="20" y="10" width="360" height="70" fill="#F8F8F5" rx="4" stroke="#E8EAE4" />
              {/* 70 overbought level */}
              <line x1="20" y1="25" x2="380" y2="25" stroke="#D64A4A" strokeWidth="1" strokeDasharray="3 3" />
              <text x="385" y="28" fill="#D64A4A" fontSize="9">70 Overbought</text>
              {/* 30 oversold level */}
              <line x1="20" y1="65" x2="380" y2="65" stroke="#16834A" strokeWidth="1" strokeDasharray="3 3" />
              <text x="385" y="68" fill="#16834A" fontSize="9">30 Oversold</text>
              {/* RSI Oscillating Line with Lower High */}
              <path d="M 40 50 L 100 20 L 140 45 L 220 35 L 260 55" fill="none" stroke="#176B45" strokeWidth="2.5" />
              {/* Divergence line */}
              <line x1="100" y1="20" x2="220" y2="35" stroke="#D64A4A" strokeWidth="2" strokeDasharray="3 3" />
              <circle cx="100" cy="20" r="3.5" fill="#D64A4A" />
              <circle cx="220" cy="35" r="3.5" fill="#D64A4A" />
              <text x="160" y="22" fill="#D64A4A" fontSize="10" fontWeight="700">Lower Peak (Bearish Divergence)</text>
            </g>
          </g>
        );

      case "indicator_macd_structure":
        return (
          <g transform="translate(40, 25)">
            {/* Zero line */}
            <line x1="30" y1="90" x2="380" y2="90" stroke="#777D76" strokeWidth="1.5" />
            <text x="385" y="94" fill="#777D76" fontSize="10">Zero Line</text>

            {/* Histogram bars */}
            <rect x="60" y="70" width="10" height="20" fill="#16834A" opacity="0.7" />
            <rect x="80" y="55" width="10" height="35" fill="#16834A" opacity="0.7" />
            <rect x="100" y="65" width="10" height="25" fill="#16834A" opacity="0.7" />
            <rect x="120" y="80" width="10" height="10" fill="#16834A" opacity="0.7" />
            {/* Negative bars */}
            <rect x="140" y="90" width="10" height="15" fill="#D64A4A" opacity="0.7" />
            <rect x="160" y="90" width="10" height="30" fill="#D64A4A" opacity="0.7" />
            <rect x="180" y="90" width="10" height="20" fill="#D64A4A" opacity="0.7" />

            {/* MACD Line (12-26 EMA) */}
            <path d="M 40 120 L 90 60 L 150 110 L 220 70 L 280 50 L 350 40" fill="none" stroke="#176B45" strokeWidth="2.5" />
            {/* Signal Line (9 EMA) */}
            <path d="M 40 115 L 90 75 L 150 100 L 220 85 L 280 65 L 350 55" fill="none" stroke="#D64A4A" strokeWidth="2" strokeDasharray="3 3" />

            {/* Bullish crossover marker */}
            <circle cx="210" cy="78" r="5" fill="none" stroke="#16834A" strokeWidth="2" />
            <text x="210" y="115" fill="#16834A" fontSize="10" fontWeight="700" textAnchor="middle">Bullish Crossover</text>

            {/* Legend */}
            <g transform="translate(50, 10)">
              <line x1="0" y1="5" x2="20" y2="5" stroke="#176B45" strokeWidth="2.5" />
              <text x="25" y="8" fill="#20251F" fontSize="10">MACD Line</text>
              <line x1="110" y1="5" x2="130" y2="5" stroke="#D64A4A" strokeWidth="2" strokeDasharray="3 3" />
              <text x="135" y="8" fill="#20251F" fontSize="10">Signal Line</text>
            </g>
          </g>
        );

      case "indicator_moving_averages":
        return (
          <g transform="translate(40, 25)">
            <text x="200" y="15" textAnchor="middle" fill="#20251F" fontSize="12" fontWeight="700">
              Golden Cross (50 EMA crosses above 200 SMA)
            </text>

            {/* 200 SMA (Long Term Baseline) */}
            <path d="M 30 110 Q 180 100, 360 85" fill="none" stroke="#777D76" strokeWidth="2" />
            <text x="365" y="88" fill="#777D76" fontSize="10">200 SMA</text>

            {/* 50 EMA (Intermediate Momentum) */}
            <path d="M 30 135 Q 150 115, 200 95 T 360 45" fill="none" stroke="#16834A" strokeWidth="2.5" />
            <text x="365" y="48" fill="#16834A" fontSize="10" fontWeight="600">50 EMA</text>

            {/* Golden cross intersection */}
            <circle cx="195" cy="98" r="6" fill="#16834A" fillOpacity="0.2" stroke="#16834A" strokeWidth="2" />
            <text x="195" y="130" textAnchor="middle" fill="#16834A" fontSize="11" fontWeight="700">
              Golden Cross
            </text>
          </g>
        );

      case "support_resistance_zones":
      case "breakout_role_reversal":
        return (
          <g transform="translate(40, 20)">
            <text x="200" y="15" textAnchor="middle" fill="#20251F" fontSize="12" fontWeight="700">
              Role Reversal: Broken Resistance Becomes New Support
            </text>

            {/* Prior Resistance Zone */}
            <rect x="20" y="70" width="360" height="20" fill="#D64A4A" fillOpacity="0.1" stroke="#D64A4A" strokeDasharray="3 3" />
            <text x="30" y="84" fill="#D64A4A" fontSize="10" fontWeight="600">Prior Resistance Zone (Supply)</text>

            {/* Price path showing breakout and retest */}
            <path
              d="M 30 130 L 90 75 L 130 110 L 180 75 L 210 100 L 260 40 L 300 72 L 350 30"
              fill="none"
              stroke="#20251F"
              strokeWidth="2.5"
            />

            {/* Retest bounce circle */}
            <circle cx="300" cy="72" r="5" fill="#16834A" stroke="#16834A" strokeWidth="2" />
            <text x="300" y="115" textAnchor="middle" fill="#16834A" fontSize="10" fontWeight="700">
              Retest Bounce (New Support)
            </text>
          </g>
        );

      case "indicator_volume_spread":
        return (
          <g transform="translate(40, 20)">
            {/* Price section */}
            <path d="M 40 80 L 100 82 L 160 81 L 220 40 L 280 45 L 340 25" fill="none" stroke="#20251F" strokeWidth="2" />
            <text x="220" y="25" fill="#16834A" fontSize="10" fontWeight="700">Breakout Candle</text>

            {/* Volume section */}
            <line x1="30" y1="140" x2="360" y2="140" stroke="#E8EAE4" strokeWidth="1" />
            {/* Average volume line */}
            <line x1="30" y1="120" x2="360" y2="120" stroke="#777D76" strokeWidth="1" strokeDasharray="3 3" />
            <text x="365" y="123" fill="#777D76" fontSize="9">20-Day Avg Volume</text>

            {/* Bars */}
            <rect x="50" y="125" width="14" height="25" fill="#777D76" opacity="0.5" />
            <rect x="90" y="127" width="14" height="23" fill="#777D76" opacity="0.5" />
            <rect x="130" y="126" width="14" height="24" fill="#777D76" opacity="0.5" />
            {/* Breakout huge volume surge */}
            <rect x="210" y="95" width="18" height="55" fill="#16834A" />
            <rect x="270" y="128" width="14" height="22" fill="#777D76" opacity="0.5" />
            <rect x="330" y="105" width="16" height="45" fill="#16834A" opacity="0.8" />

            <text x="219" y="165" textAnchor="middle" fill="#16834A" fontSize="10" fontWeight="700">
              Institutional Volume Surge (3x Avg)
            </text>
          </g>
        );

      default:
        return (
          <g transform="translate(80, 50)">
            <rect x="20" y="20" width="280" height="70" fill="#F8F8F5" stroke="#E8EAE4" rx="6" />
            <text x="160" y="60" textAnchor="middle" fill="#20251F" fontSize="12" fontWeight="600">
              Technical Indicator Model
            </text>
          </g>
        );
    }
  };

  return (
    <div
      className={`relative w-full rounded-xl border border-[#E8EAE4] bg-[#FFFFFF] p-4 shadow-xs ${className}`}
    >
      {/* Top Disclaimer Badge */}
      <div className="mb-2 flex items-center justify-between">
        <span className="inline-flex items-center gap-1.5 rounded-md bg-[#F1F2ED] px-2.5 py-1 text-[11px] font-medium text-[#777D76]">
          <ShieldAlert className="h-3.5 w-3.5 text-[#176B45]" />
          Educational Indicator Model
        </span>
        <span className="text-[11px] text-[#777D76]">No Indicator Guarantees Outcomes</span>
      </div>

      {/* SVG Canvas */}
      <div className="w-full overflow-x-auto">
        <svg
          viewBox="0 0 460 190"
          className="mx-auto h-48 w-full min-w-[340px] select-none"
        >
          {renderDiagram()}
        </svg>
      </div>

      {/* Caption Footer */}
      <div className="mt-2 rounded-lg bg-[#F8F8F5] p-2 text-center text-[11px] text-[#777D76]">
        Indicators lag real-time price action. Use indicators as momentum confirmation filters, never as isolated entry triggers.
      </div>
    </div>
  );
};
