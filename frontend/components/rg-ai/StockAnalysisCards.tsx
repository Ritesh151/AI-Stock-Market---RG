"use client";

import React from "react";
import {
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  Compass,
  Layers,
  Activity,
  FileText,
  Calendar,
  Database,
  ShieldCheck,
} from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { StockAnalysisData } from "@/types/rgAi";

interface StockAnalysisCardsProps {
  data: StockAnalysisData;
  disclaimer?: string;
  warnings?: string[] | null;
}

// Format currency / number safely preserving null as 'Not available'
function formatValue(
  val: number | string | null | undefined,
  prefix = "",
  suffix = ""
): string {
  if (val === null || val === undefined) {
    return "Not available";
  }
  if (typeof val === "number") {
    return `${prefix}${val.toLocaleString("en-IN")}${suffix}`;
  }
  return `${prefix}${val}${suffix}`;
}

export function StockAnalysisCards({
  data,
  disclaimer,
  warnings,
}: StockAnalysisCardsProps) {
  const isPositive =
    data.price_change !== null && data.price_change !== undefined
      ? data.price_change > 0
      : null;

  const getRecommendationBadgeVariant = (rec: string) => {
    switch (rec.toUpperCase()) {
      case "BUY":
      case "STRONG_BUY":
      case "ACCUMULATE":
        return "positive";
      case "SELL":
      case "STRONG_SELL":
      case "REDUCE":
      case "AVOID":
        return "negative";
      default:
        return "neutral";
    }
  };

  const getRiskBadgeVariant = (risk: string) => {
    switch (risk.toLowerCase()) {
      case "low":
        return "positive";
      case "high":
      case "very_high":
        return "negative";
      default:
        return "accent";
    }
  };

  return (
    <div className="space-y-4">
      {/* Non-fatal financial warnings banner if present */}
      {warnings && warnings.length > 0 && (
        <div className="rounded-xl border border-amber-200 bg-amber-50/80 p-3 text-xs text-amber-900 space-y-1">
          <div className="flex items-center gap-1.5 font-semibold">
            <AlertTriangle className="h-4 w-4 text-amber-600" />
            <span>Analysis Consistency Notices</span>
          </div>
          <ul className="list-disc pl-5 space-y-0.5 text-[11px] text-amber-800">
            {warnings.map((w, i) => (
              <li key={i}>{w}</li>
            ))}
          </ul>
        </div>
      )}

      {/* 1. Stock Overview Card */}
      <div className="rounded-xl border border-[#E8EAE4] bg-[#FFFFFF] p-4 shadow-2xs">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-bold text-[#20251F]">
                {data.stock_name}
              </h3>
              <span className="rounded-md bg-[#F1F2ED] px-2 py-0.5 text-xs font-mono font-medium text-[#20251F]">
                {data.symbol}
              </span>
              <span className="rounded-md border border-[#E8EAE4] px-1.5 py-0.5 text-[10px] font-medium text-[#777D76]">
                {data.exchange}
              </span>
            </div>
            <div className="mt-1 flex items-center gap-3 text-xs text-[#777D76]">
              {data.market_trend && (
                <span className="capitalize flex items-center gap-1">
                  <Compass className="h-3 w-3 text-[#176B45]" />
                  Trend: {data.market_trend}
                </span>
              )}
              {data.data_timestamp && (
                <span className="flex items-center gap-1 hidden sm:inline-flex">
                  <Calendar className="h-3 w-3" />
                  {new Date(data.data_timestamp).toLocaleDateString("en-IN", {
                    month: "short",
                    day: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </span>
              )}
            </div>
          </div>

          <div className="text-right">
            <div className="text-lg font-bold text-[#20251F]">
              {data.current_price !== null && data.current_price !== undefined
                ? `₹${data.current_price.toLocaleString("en-IN")}`
                : "Not available"}
            </div>
            {data.price_change !== null && data.price_change !== undefined ? (
              <div
                className={`flex items-center justify-end gap-1 text-xs font-medium ${
                  isPositive ? "text-[#16834A]" : "text-[#D64A4A]"
                }`}
              >
                {isPositive ? (
                  <TrendingUp className="h-3.5 w-3.5" />
                ) : (
                  <TrendingDown className="h-3.5 w-3.5" />
                )}
                <span>
                  {data.price_change > 0 ? "+" : ""}
                  {data.price_change.toFixed(2)} (
                  {data.price_change_percent !== null &&
                  data.price_change_percent !== undefined
                    ? `${data.price_change_percent > 0 ? "+" : ""}${data.price_change_percent.toFixed(2)}%`
                    : "Not available"}
                  )
                </span>
              </div>
            ) : (
              <div className="text-xs text-[#777D76]">Price change not available</div>
            )}
          </div>
        </div>

        {data.data_source && (
          <div className="mt-3 pt-2.5 border-t border-[#E8EAE4] flex items-center justify-between text-[11px] text-[#777D76]">
            <span className="flex items-center gap-1">
              <Database className="h-3 w-3" />
              Source: {data.data_source}
            </span>
            <span>Currency: {data.currency}</span>
          </div>
        )}
      </div>

      {/* 2. Recommendation & Trade Setup Card */}
      <div className="rounded-xl border border-[#E8EAE4] bg-[#FFFFFF] p-4 shadow-2xs">
        <h4 className="text-xs font-semibold uppercase tracking-wider text-[#777D76] mb-3">
          Research Recommendation & Targets
        </h4>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="rounded-lg bg-[#F8F8F5] p-2.5">
            <span className="text-[10px] text-[#777D76] block">Recommendation</span>
            <div className="mt-1">
              <Badge variant={getRecommendationBadgeVariant(data.recommendation)}>
                {data.recommendation}
              </Badge>
            </div>
          </div>

          <div className="rounded-lg bg-[#F8F8F5] p-2.5">
            <span className="text-[10px] text-[#777D76] block">Risk Level</span>
            <div className="mt-1">
              <Badge variant={getRiskBadgeVariant(data.risk_level)}>
                {data.risk_level.toUpperCase()}
              </Badge>
            </div>
          </div>

          <div className="rounded-lg bg-[#F8F8F5] p-2.5">
            <span className="text-[10px] text-[#777D76] block">Target Price</span>
            <div className="text-xs font-bold text-[#16834A] mt-1">
              {formatValue(data.target_price, "₹")}
            </div>
          </div>

          <div className="rounded-lg bg-[#F8F8F5] p-2.5">
            <span className="text-[10px] text-[#777D76] block">Stop Loss</span>
            <div className="text-xs font-bold text-[#D64A4A] mt-1">
              {formatValue(data.stop_loss, "₹")}
            </div>
          </div>
        </div>

        <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-3 pt-3 border-t border-[#E8EAE4]">
          <div className="text-xs">
            <span className="text-[#777D76]">Entry Zone: </span>
            <span className="font-semibold text-[#20251F]">
              {data.entry_zone.min !== null || data.entry_zone.max !== null
                ? `₹${formatValue(data.entry_zone.min)} – ₹${formatValue(data.entry_zone.max)}`
                : "Not available"}
            </span>
          </div>
          <div className="text-xs sm:text-right">
            <span className="text-[#777D76]">Time Horizon: </span>
            <span className="font-semibold text-[#20251F]">
              {formatValue(data.time_horizon)}
            </span>
          </div>
        </div>
      </div>

      {/* 3. Technical & Fundamental Sub-Sections (if present) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Technical Sub-Card */}
        <div className="rounded-xl border border-[#E8EAE4] bg-[#FFFFFF] p-4 shadow-2xs">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-[#20251F] mb-3">
            <Activity className="h-4 w-4 text-[#176B45]" />
            <span>Technical Indicators</span>
          </div>
          {data.technical_indicators &&
          Object.keys(data.technical_indicators).length > 0 ? (
            <div className="grid grid-cols-2 gap-2 text-xs">
              {Object.entries(data.technical_indicators).map(([key, val]) => (
                <div key={key} className="rounded-lg bg-[#F8F8F5] p-2">
                  <span className="text-[10px] uppercase text-[#777D76] block truncate">
                    {key.replace(/_/g, " ")}
                  </span>
                  <span className="font-semibold text-[#20251F] mt-0.5 block truncate">
                    {typeof val === "object" && val !== null
                      ? JSON.stringify(val)
                      : formatValue(val as string | number | null)}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-[#777D76] italic">
              No detailed technical indicators provided.
            </p>
          )}
        </div>

        {/* Fundamental Sub-Card */}
        <div className="rounded-xl border border-[#E8EAE4] bg-[#FFFFFF] p-4 shadow-2xs">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-[#20251F] mb-3">
            <Layers className="h-4 w-4 text-[#176B45]" />
            <span>Fundamental Factors</span>
          </div>
          {data.fundamental_factors &&
          Object.keys(data.fundamental_factors).length > 0 ? (
            <div className="grid grid-cols-2 gap-2 text-xs">
              {Object.entries(data.fundamental_factors).map(([key, val]) => (
                <div key={key} className="rounded-lg bg-[#F8F8F5] p-2">
                  <span className="text-[10px] uppercase text-[#777D76] block truncate">
                    {key.replace(/_/g, " ")}
                  </span>
                  <span className="font-semibold text-[#20251F] mt-0.5 block truncate">
                    {typeof val === "object" && val !== null
                      ? JSON.stringify(val)
                      : formatValue(val as string | number | null)}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-[#777D76] italic">
              No detailed fundamental factors provided.
            </p>
          )}
        </div>
      </div>

      {/* 4. Validated Reasoning List */}
      {data.reasoning && data.reasoning.length > 0 && (
        <div className="rounded-xl border border-[#E8EAE4] bg-[#FFFFFF] p-4 shadow-2xs">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-[#20251F] mb-2.5">
            <FileText className="h-4 w-4 text-[#176B45]" />
            <span>Research Rationale & Key Drivers</span>
          </div>
          <ul className="space-y-1.5">
            {data.reasoning.map((item, idx) => (
              <li
                key={idx}
                className="flex items-start gap-2 text-xs text-[#20251F] leading-relaxed"
              >
                <span className="flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-[#176B45]/15 text-[10px] font-semibold text-[#176B45] mt-0.5">
                  {idx + 1}
                </span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* 5. Prominent Disclaimer */}
      {disclaimer && (
        <div className="rounded-xl border border-[#E8EAE4] bg-[#F1F2ED]/60 p-3 text-[11px] text-[#777D76] leading-relaxed flex items-start gap-2">
          <ShieldCheck className="h-4 w-4 text-[#176B45] shrink-0 mt-0.5" />
          <span>{disclaimer}</span>
        </div>
      )}
    </div>
  );
}
