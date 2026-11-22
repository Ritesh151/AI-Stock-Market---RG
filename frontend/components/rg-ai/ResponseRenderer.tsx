"use client";

import React, { useState } from "react";
import { LayoutDashboard, Code, ShieldCheck, Activity, BarChart2, Layers, PieChart } from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { ResponseEnvelope, StockAnalysisData } from "@/types/rgAi";
import { StockAnalysisCards } from "./StockAnalysisCards";
import { JsonViewer } from "./JsonViewer";

interface ResponseRendererProps {
  envelope: ResponseEnvelope;
}

function formatSafe(val: unknown, prefix = "", suffix = ""): string {
  if (val === null || val === undefined) return "Not available";
  if (typeof val === "number") return `${prefix}${val.toLocaleString("en-IN")}${suffix}`;
  return `${prefix}${String(val)}${suffix}`;
}

export function ResponseRenderer({ envelope }: ResponseRendererProps) {
  const [activeTab, setActiveTab] = useState<"structured" | "json">("structured");

  const renderDomainContent = () => {
    const { type, data, disclaimer, warnings } = envelope;

    switch (type) {
      case "stock_analysis":
        return (
          <StockAnalysisCards
            data={data as unknown as StockAnalysisData}
            disclaimer={disclaimer}
            warnings={warnings}
          />
        );

      case "technical_analysis": {
        const d = data as Record<string, unknown>;
        const ma = (d.moving_averages as Record<string, unknown>) || {};
        const supports = (d.support_levels as number[]) || [];
        const resistances = (d.resistance_levels as number[]) || [];
        const patterns = (d.candlestick_patterns as string[]) || [];

        return (
          <div className="space-y-4">
            <div className="rounded-xl border border-[#E8EAE4] bg-[#FFFFFF] p-4 shadow-2xs">
              <div className="flex items-center gap-2 mb-3">
                <Activity className="h-4 w-4 text-[#176B45]" />
                <h4 className="text-xs font-semibold uppercase tracking-wider text-[#777D76]">
                  Technical Indicators
                </h4>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="rounded-lg bg-[#F8F8F5] p-2.5">
                  <span className="text-[10px] text-[#777D76]">RSI (14)</span>
                  <div className="text-xs font-bold text-[#20251F] mt-1">
                    {formatSafe(d.rsi)}
                  </div>
                </div>

                <div className="rounded-lg bg-[#F8F8F5] p-2.5">
                  <span className="text-[10px] text-[#777D76]">Trend</span>
                  <div className="mt-1">
                    <Badge variant="accent">
                      {String(d.trend_direction || "Not available").toUpperCase()}
                    </Badge>
                  </div>
                </div>

                <div className="rounded-lg bg-[#F8F8F5] p-2.5">
                  <span className="text-[10px] text-[#777D76]">20-EMA</span>
                  <div className="text-xs font-bold text-[#20251F] mt-1">
                    {formatSafe(ma.ema_20, "₹")}
                  </div>
                </div>

                <div className="rounded-lg bg-[#F8F8F5] p-2.5">
                  <span className="text-[10px] text-[#777D76]">200-EMA</span>
                  <div className="text-xs font-bold text-[#20251F] mt-1">
                    {formatSafe(ma.ema_200, "₹")}
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-4 pt-3 border-t border-[#E8EAE4]">
                <div>
                  <span className="text-[11px] font-semibold text-[#16834A] block mb-1">
                    Support Levels
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {supports.length > 0 ? (
                      supports.map((s, idx) => (
                        <span
                          key={idx}
                          className="rounded-md bg-green-50 px-2 py-0.5 text-xs font-mono font-medium text-[#16834A] border border-green-200"
                        >
                          ₹{s}
                        </span>
                      ))
                    ) : (
                      <span className="text-xs text-[#777D76]">Not available</span>
                    )}
                  </div>
                </div>

                <div>
                  <span className="text-[11px] font-semibold text-[#D64A4A] block mb-1">
                    Resistance Levels
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {resistances.length > 0 ? (
                      resistances.map((r, idx) => (
                        <span
                          key={idx}
                          className="rounded-md bg-red-50 px-2 py-0.5 text-xs font-mono font-medium text-[#D64A4A] border border-red-200"
                        >
                          ₹{r}
                        </span>
                      ))
                    ) : (
                      <span className="text-xs text-[#777D76]">Not available</span>
                    )}
                  </div>
                </div>
              </div>

              {patterns.length > 0 && (
                <div className="mt-3 pt-3 border-t border-[#E8EAE4]">
                  <span className="text-[11px] text-[#777D76] block mb-1">
                    Detected Patterns
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {patterns.map((p, idx) => (
                      <span
                        key={idx}
                        className="rounded-md bg-[#F1F2ED] px-2 py-0.5 text-xs text-[#20251F]"
                      >
                        {p}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {disclaimer && (
              <div className="rounded-xl border border-[#E8EAE4] bg-[#F1F2ED]/60 p-3 text-[11px] text-[#777D76] leading-relaxed flex items-start gap-2">
                <ShieldCheck className="h-4 w-4 text-[#176B45] shrink-0 mt-0.5" />
                <span>{disclaimer}</span>
              </div>
            )}
          </div>
        );
      }

      case "fundamental_analysis": {
        const d = data as Record<string, unknown>;
        return (
          <div className="space-y-4">
            <div className="rounded-xl border border-[#E8EAE4] bg-[#FFFFFF] p-4 shadow-2xs">
              <div className="flex items-center gap-2 mb-3">
                <BarChart2 className="h-4 w-4 text-[#176B45]" />
                <h4 className="text-xs font-semibold uppercase tracking-wider text-[#777D76]">
                  Fundamental Metrics
                </h4>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                <div className="rounded-lg bg-[#F8F8F5] p-2.5">
                  <span className="text-[10px] text-[#777D76]">P/E Ratio</span>
                  <div className="font-bold text-[#20251F] mt-1">{formatSafe(d.pe_ratio)}</div>
                </div>
                <div className="rounded-lg bg-[#F8F8F5] p-2.5">
                  <span className="text-[10px] text-[#777D76]">P/B Ratio</span>
                  <div className="font-bold text-[#20251F] mt-1">{formatSafe(d.pb_ratio)}</div>
                </div>
                <div className="rounded-lg bg-[#F8F8F5] p-2.5">
                  <span className="text-[10px] text-[#777D76]">ROE (%)</span>
                  <div className="font-bold text-[#20251F] mt-1">{formatSafe(d.roe, "", "%")}</div>
                </div>
                <div className="rounded-lg bg-[#F8F8F5] p-2.5">
                  <span className="text-[10px] text-[#777D76]">ROCE (%)</span>
                  <div className="font-bold text-[#20251F] mt-1">{formatSafe(d.roce, "", "%")}</div>
                </div>
                <div className="rounded-lg bg-[#F8F8F5] p-2.5">
                  <span className="text-[10px] text-[#777D76]">EPS</span>
                  <div className="font-bold text-[#20251F] mt-1">{formatSafe(d.eps, "₹")}</div>
                </div>
                <div className="rounded-lg bg-[#F8F8F5] p-2.5">
                  <span className="text-[10px] text-[#777D76]">Debt</span>
                  <div className="font-bold text-[#20251F] mt-1">{formatSafe(d.debt, "₹")}</div>
                </div>
                <div className="rounded-lg bg-[#F8F8F5] p-2.5">
                  <span className="text-[10px] text-[#777D76]">Market Cap</span>
                  <div className="font-bold text-[#20251F] mt-1">{formatSafe(d.market_capitalization, "₹")}</div>
                </div>
                <div className="rounded-lg bg-[#F8F8F5] p-2.5">
                  <span className="text-[10px] text-[#777D76]">Reporting Period</span>
                  <div className="font-bold text-[#20251F] mt-1">{formatSafe(d.financial_reporting_period)}</div>
                </div>
              </div>
            </div>

            {disclaimer && (
              <div className="rounded-xl border border-[#E8EAE4] bg-[#F1F2ED]/60 p-3 text-[11px] text-[#777D76] leading-relaxed flex items-start gap-2">
                <ShieldCheck className="h-4 w-4 text-[#176B45] shrink-0 mt-0.5" />
                <span>{disclaimer}</span>
              </div>
            )}
          </div>
        );
      }

      case "portfolio_analysis": {
        const d = data as Record<string, unknown>;
        const holdings = (d.holdings as Array<Record<string, unknown>>) || [];
        const observations = (d.diversification_observations as string[]) || [];

        return (
          <div className="space-y-4">
            <div className="rounded-xl border border-[#E8EAE4] bg-[#FFFFFF] p-4 shadow-2xs">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <PieChart className="h-4 w-4 text-[#176B45]" />
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-[#777D76]">
                    Portfolio Analysis
                  </h4>
                </div>
                {Boolean(d.concentration_risk) && (
                  <Badge variant="accent">
                    Risk: {String(d.concentration_risk).toUpperCase()}
                  </Badge>
                )}
              </div>

              {holdings.length > 0 && (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-[#E8EAE4] text-[10px] uppercase text-[#777D76]">
                        <th className="py-2">Symbol</th>
                        <th className="py-2">Allocation</th>
                        <th className="py-2">Sector</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#E8EAE4]/60">
                      {holdings.map((h, idx) => (
                        <tr key={idx}>
                          <td className="py-2 font-semibold text-[#20251F]">{formatSafe(h.symbol)}</td>
                          <td className="py-2 text-[#176B45] font-mono">{formatSafe(h.allocation_percent, "", "%")}</td>
                          <td className="py-2 text-[#777D76]">{formatSafe(h.sector)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {observations.length > 0 && (
                <div className="mt-4 pt-3 border-t border-[#E8EAE4]">
                  <span className="text-[11px] font-semibold text-[#20251F] block mb-1">
                    Diversification Observations
                  </span>
                  <ul className="list-disc pl-5 space-y-1 text-xs text-[#777D76]">
                    {observations.map((obs, idx) => (
                      <li key={idx}>{obs}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {disclaimer && (
              <div className="rounded-xl border border-[#E8EAE4] bg-[#F1F2ED]/60 p-3 text-[11px] text-[#777D76] leading-relaxed flex items-start gap-2">
                <ShieldCheck className="h-4 w-4 text-[#176B45] shrink-0 mt-0.5" />
                <span>{disclaimer}</span>
              </div>
            )}
          </div>
        );
      }

      default:
        // Generic structured card for other schema types (market_overview, educational_content, stock_comparison)
        return (
          <div className="space-y-4">
            <div className="rounded-xl border border-[#E8EAE4] bg-[#FFFFFF] p-4 shadow-2xs">
              <div className="flex items-center gap-2 mb-3">
                <Layers className="h-4 w-4 text-[#176B45]" />
                <h4 className="text-xs font-semibold uppercase tracking-wider text-[#777D76]">
                  {type.replace("_", " ")}
                </h4>
              </div>

              <div className="space-y-2 text-xs">
                {Object.entries(data).map(([key, val]) => (
                  <div key={key} className="rounded-lg bg-[#F8F8F5] p-2.5">
                    <span className="text-[10px] uppercase font-semibold text-[#777D76] block">
                      {key.replace(/_/g, " ")}
                    </span>
                    <div className="mt-1 text-[#20251F]">
                      {typeof val === "object" && val !== null ? (
                        <pre className="text-[11px] font-mono bg-[#FFFFFF] p-2 rounded border border-[#E8EAE4] overflow-auto">
                          {JSON.stringify(val, null, 2)}
                        </pre>
                      ) : (
                        formatSafe(val as string | number | null)
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {disclaimer && (
              <div className="rounded-xl border border-[#E8EAE4] bg-[#F1F2ED]/60 p-3 text-[11px] text-[#777D76] leading-relaxed flex items-start gap-2">
                <ShieldCheck className="h-4 w-4 text-[#176B45] shrink-0 mt-0.5" />
                <span>{disclaimer}</span>
              </div>
            )}
          </div>
        );
    }
  };

  return (
    <div className="space-y-3">
      {/* Top Tab Bar: Structured vs Raw JSON */}
      <div className="flex items-center justify-between border-b border-[#E8EAE4] pb-2 text-xs">
        <div className="flex items-center gap-1.5">
          <button
            onClick={() => setActiveTab("structured")}
            className={`inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-xs font-medium transition-colors cursor-pointer ${
              activeTab === "structured"
                ? "bg-[#176B45] text-white shadow-2xs"
                : "text-[#777D76] hover:bg-[#E8EAE4] hover:text-[#20251F]"
            }`}
          >
            <LayoutDashboard className="h-3.5 w-3.5" />
            <span>Structured Analysis</span>
          </button>

          <button
            onClick={() => setActiveTab("json")}
            className={`inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-xs font-medium transition-colors cursor-pointer ${
              activeTab === "json"
                ? "bg-[#176B45] text-white shadow-2xs"
                : "text-[#777D76] hover:bg-[#E8EAE4] hover:text-[#20251F]"
            }`}
          >
            <Code className="h-3.5 w-3.5" />
            <span>Raw JSON</span>
          </button>
        </div>

        <span className="text-[10px] font-mono text-[#777D76]">
          {envelope.type} • v{envelope.schema_version}
        </span>
      </div>

      {/* Tab Content */}
      {activeTab === "structured" ? (
        renderDomainContent()
      ) : (
        <JsonViewer
          data={envelope.data}
          schemaVersion={envelope.schema_version}
          requestId={envelope.request_id}
        />
      )}
    </div>
  );
}
