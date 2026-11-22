"use client";

import React from "react";
import { ShieldAlert } from "lucide-react";

interface CandlestickIllustratorProps {
  patternKey?: string;
  className?: string;
}

/**
 * Programmatic SVG Educational Candlestick Chart Renderer.
 * Generates accurate diagrams for all 13 Japanese candlestick patterns.
 * Explicitly watermarked as an educational example.
 */
export const CandlestickIllustrator: React.FC<CandlestickIllustratorProps> = ({
  patternKey = "pattern_hammer_shooting_star",
  className = "",
}) => {
  const renderDiagram = () => {
    switch (patternKey) {
      case "pattern_doji":
        return (
          <g>
            {/* Context downtrend dashed line */}
            <path d="M 40 40 L 90 90 L 140 120" stroke="#777D76" strokeWidth="2" strokeDasharray="4 4" fill="none" opacity="0.4" />
            
            {/* Standard Doji */}
            <g transform="translate(180, 50)">
              <line x1="20" y1="10" x2="20" y2="110" stroke="#20251F" strokeWidth="2.5" />
              <line x1="8" y1="60" x2="32" y2="60" stroke="#20251F" strokeWidth="4" />
              <text x="20" y="130" textAnchor="middle" fill="#20251F" fontSize="11" fontWeight="600">Standard Doji</text>
              <text x="20" y="145" textAnchor="middle" fill="#777D76" fontSize="9">Open = Close</text>
            </g>

            {/* Dragonfly Doji */}
            <g transform="translate(260, 50)">
              <line x1="20" y1="20" x2="20" y2="110" stroke="#16834A" strokeWidth="2.5" />
              <line x1="8" y1="20" x2="32" y2="20" stroke="#16834A" strokeWidth="4" />
              <text x="20" y="130" textAnchor="middle" fill="#16834A" fontSize="11" fontWeight="600">Dragonfly Doji</text>
              <text x="20" y="145" textAnchor="middle" fill="#777D76" fontSize="9">Lower Rejection</text>
            </g>

            {/* Gravestone Doji */}
            <g transform="translate(340, 50)">
              <line x1="20" y1="10" x2="20" y2="100" stroke="#D64A4A" strokeWidth="2.5" />
              <line x1="8" y1="100" x2="32" y2="100" stroke="#D64A4A" strokeWidth="4" />
              <text x="20" y="130" textAnchor="middle" fill="#D64A4A" fontSize="11" fontWeight="600">Gravestone Doji</text>
              <text x="20" y="145" textAnchor="middle" fill="#777D76" fontSize="9">Upper Rejection</text>
            </g>
          </g>
        );

      case "pattern_hammer_shooting_star":
        return (
          <g>
            {/* Hammer on left (after downtrend) */}
            <g transform="translate(80, 30)">
              <path d="M 20 20 L 50 60 L 80 85" stroke="#777D76" strokeWidth="2" strokeDasharray="3 3" fill="none" opacity="0.4" />
              {/* Prior red candle */}
              <line x1="80" y1="70" x2="80" y2="110" stroke="#D64A4A" strokeWidth="1.5" />
              <rect x="74" y="78" width="12" height="24" fill="#D64A4A" rx="1" />
              {/* Hammer */}
              <line x1="110" y1="88" x2="110" y2="145" stroke="#16834A" strokeWidth="2" />
              <rect x="103" y="88" width="14" height="14" fill="#16834A" rx="1" />
              {/* Labels */}
              <text x="110" y="165" textAnchor="middle" fill="#16834A" fontSize="12" fontWeight="700">Bullish Hammer</text>
              <text x="110" y="180" textAnchor="middle" fill="#777D76" fontSize="10">Lower Shadow &ge; 2x Body</text>
            </g>

            {/* Shooting Star on right (after uptrend) */}
            <g transform="translate(290, 30)">
              <path d="M 20 85 L 50 55 L 80 30" stroke="#777D76" strokeWidth="2" strokeDasharray="3 3" fill="none" opacity="0.4" />
              {/* Prior green candle */}
              <line x1="80" y1="35" x2="80" y2="75" stroke="#16834A" strokeWidth="1.5" />
              <rect x="74" y="42" width="12" height="24" fill="#16834A" rx="1" />
              {/* Shooting star */}
              <line x1="110" y1="15" x2="110" y2="75" stroke="#D64A4A" strokeWidth="2" />
              <rect x="103" y="60" width="14" height="14" fill="#D64A4A" rx="1" />
              {/* Labels */}
              <text x="110" y="165" textAnchor="middle" fill="#D64A4A" fontSize="12" fontWeight="700">Shooting Star</text>
              <text x="110" y="180" textAnchor="middle" fill="#777D76" fontSize="10">Upper Shadow &ge; 2x Body</text>
            </g>
          </g>
        );

      case "pattern_engulfing":
        return (
          <g>
            {/* Bullish Engulfing */}
            <g transform="translate(60, 30)">
              <text x="90" y="20" textAnchor="middle" fill="#16834A" fontSize="13" fontWeight="700">Bullish Engulfing</text>
              <path d="M 40 40 L 70 75" stroke="#777D76" strokeWidth="1.5" strokeDasharray="3 3" opacity="0.4" />
              {/* Candle 1 (Small Red) */}
              <line x1="75" y1="65" x2="75" y2="105" stroke="#D64A4A" strokeWidth="1.5" />
              <rect x="68" y="72" width="14" height="22" fill="#D64A4A" rx="1" />
              {/* Candle 2 (Large Green engulfing) */}
              <line x1="105" y1="50" x2="105" y2="125" stroke="#16834A" strokeWidth="2" />
              <rect x="96" y="58" width="18" height="52" fill="#16834A" rx="2" />
              <text x="90" y="160" textAnchor="middle" fill="#777D76" fontSize="10">Green body completely envelops red body</text>
            </g>

            {/* Bearish Engulfing */}
            <g transform="translate(280, 30)">
              <text x="90" y="20" textAnchor="middle" fill="#D64A4A" fontSize="13" fontWeight="700">Bearish Engulfing</text>
              <path d="M 40 75 L 70 40" stroke="#777D76" strokeWidth="1.5" strokeDasharray="3 3" opacity="0.4" />
              {/* Candle 1 (Small Green) */}
              <line x1="75" y1="45" x2="75" y2="85" stroke="#16834A" strokeWidth="1.5" />
              <rect x="68" y="52" width="14" height="22" fill="#16834A" rx="1" />
              {/* Candle 2 (Large Red engulfing) */}
              <line x1="105" y1="35" x2="105" y2="115" stroke="#D64A4A" strokeWidth="2" />
              <rect x="96" y="42" width="18" height="55" fill="#D64A4A" rx="2" />
              <text x="90" y="160" textAnchor="middle" fill="#777D76" fontSize="10">Red body completely envelops green body</text>
            </g>
          </g>
        );

      case "pattern_piercing_dark_cloud":
        return (
          <g>
            {/* Piercing Pattern */}
            <g transform="translate(60, 30)">
              <text x="90" y="20" textAnchor="middle" fill="#16834A" fontSize="13" fontWeight="700">Piercing Pattern</text>
              {/* Candle 1 (Long Red) */}
              <line x1="70" y1="40" x2="70" y2="120" stroke="#D64A4A" strokeWidth="2" />
              <rect x="61" y="50" width="18" height="60" fill="#D64A4A" rx="1" />
              {/* 50% midpoint line */}
              <line x1="61" y1="80" x2="125" y2="80" stroke="#777D76" strokeWidth="1" strokeDasharray="3 3" />
              {/* Candle 2 (Gaps down, closes > 50% into body) */}
              <line x1="105" y1="70" x2="105" y2="135" stroke="#16834A" strokeWidth="2" />
              <rect x="96" y="75" width="18" height="50" fill="#16834A" rx="1" />
              <text x="90" y="155" textAnchor="middle" fill="#777D76" fontSize="10">Pierces &gt; 50% into prior red body</text>
            </g>

            {/* Dark Cloud Cover */}
            <g transform="translate(280, 30)">
              <text x="90" y="20" textAnchor="middle" fill="#D64A4A" fontSize="13" fontWeight="700">Dark Cloud Cover</text>
              {/* Candle 1 (Long Green) */}
              <line x1="70" y1="40" x2="70" y2="120" stroke="#16834A" strokeWidth="2" />
              <rect x="61" y="50" width="18" height="60" fill="#16834A" rx="1" />
              {/* 50% midpoint line */}
              <line x1="61" y1="80" x2="125" y2="80" stroke="#777D76" strokeWidth="1" strokeDasharray="3 3" />
              {/* Candle 2 (Gaps up, closes > 50% down into body) */}
              <line x1="105" y1="30" x2="105" y2="95" stroke="#D64A4A" strokeWidth="2" />
              <rect x="96" y="38" width="18" height="50" fill="#D64A4A" rx="1" />
              <text x="90" y="155" textAnchor="middle" fill="#777D76" fontSize="10">Closes &gt; 50% down into green body</text>
            </g>
          </g>
        );

      case "pattern_stars_soldiers_crows":
        return (
          <g>
            {/* Morning Star */}
            <g transform="translate(40, 20)">
              <text x="75" y="15" textAnchor="middle" fill="#16834A" fontSize="12" fontWeight="700">Morning Star</text>
              {/* 1: Long Red */}
              <rect x="40" y="35" width="14" height="40" fill="#D64A4A" rx="1" />
              {/* 2: Star */}
              <rect x="68" y="80" width="12" height="12" fill="#777D76" rx="1" />
              {/* 3: Long Green */}
              <rect x="92" y="42" width="14" height="42" fill="#16834A" rx="1" />
              <text x="75" y="120" textAnchor="middle" fill="#777D76" fontSize="9">3-Candle Bottom Reversal</text>
            </g>

            {/* Three White Soldiers */}
            <g transform="translate(180, 20)">
              <text x="65" y="15" textAnchor="middle" fill="#16834A" fontSize="12" fontWeight="700">Three White Soldiers</text>
              <rect x="30" y="70" width="14" height="28" fill="#16834A" rx="1" />
              <rect x="52" y="50" width="14" height="30" fill="#16834A" rx="1" />
              <rect x="74" y="30" width="14" height="32" fill="#16834A" rx="1" />
              <text x="65" y="120" textAnchor="middle" fill="#777D76" fontSize="9">Consecutive Higher Closes</text>
            </g>

            {/* Three Black Crows */}
            <g transform="translate(320, 20)">
              <text x="65" y="15" textAnchor="middle" fill="#D64A4A" fontSize="12" fontWeight="700">Three Black Crows</text>
              <rect x="30" y="30" width="14" height="32" fill="#D64A4A" rx="1" />
              <rect x="52" y="50" width="14" height="30" fill="#D64A4A" rx="1" />
              <rect x="74" y="70" width="14" height="28" fill="#D64A4A" rx="1" />
              <text x="65" y="120" textAnchor="middle" fill="#777D76" fontSize="9">Consecutive Lower Closes</text>
            </g>
          </g>
        );

      default:
        // Default candlestick representation
        return (
          <g transform="translate(120, 30)">
            <line x1="60" y1="20" x2="60" y2="120" stroke="#16834A" strokeWidth="2" />
            <rect x="50" y="40" width="20" height="50" fill="#16834A" rx="2" />
            <line x1="140" y1="20" x2="140" y2="120" stroke="#D64A4A" strokeWidth="2" />
            <rect x="130" y="45" width="20" height="50" fill="#D64A4A" rx="2" />
            <text x="100" y="150" textAnchor="middle" fill="#20251F" fontSize="12" fontWeight="600">
              Japanese Candlestick Anatomy
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
          Educational Illustration Only
        </span>
        <span className="text-[11px] text-[#777D76]">Not a Live Market Signal</span>
      </div>

      {/* SVG Canvas */}
      <div className="w-full overflow-x-auto">
        <svg
          viewBox="0 0 480 200"
          className="mx-auto h-48 w-full min-w-[340px] select-none"
        >
          {/* Subtle grid background */}
          <defs>
            <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
              <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#F1F2ED" strokeWidth="1" />
            </pattern>
          </defs>
          <rect width="480" height="200" fill="url(#grid)" opacity="0.6" />

          {/* Render target pattern */}
          {renderDiagram()}
        </svg>
      </div>

      {/* Caption Footer */}
      <div className="mt-2 rounded-lg bg-[#F8F8F5] p-2 text-center text-[11px] text-[#777D76]">
        Formations require structural market context, volume expansion, and subsequent candle confirmation. No pattern guarantees price direction.
      </div>
    </div>
  );
};
