"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { X, Sparkles, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { PromptTemplateItem } from "@/types/rgAi";
import { snappyTransition } from "@/lib/motionTokens";

export const PROMPT_TEMPLATES: PromptTemplateItem[] = [
  {
    id: "complete_stock_analysis",
    name: "Complete Stock Analysis",
    targetSchema: "stock_analysis",
    description: "Exhaustive equity research covering price action, valuation, indicators, and trade setup.",
    variables: [
      { key: "symbol", label: "Stock Symbol", placeholder: "e.g., RELIANCE, TCS, INFY", required: true },
      { key: "exchange", label: "Exchange", placeholder: "NSE or BSE", defaultValue: "NSE", required: false },
    ],
    generatePrompt: (v) =>
      `Provide a complete Indian stock analysis for ${v.symbol.toUpperCase()} listed on ${
        v.exchange || "NSE"
      }, including current price trend, valuation, support/resistance, and risk rating.`,
  },
  {
    id: "buy_sell_research",
    name: "Buy or Sell Research",
    targetSchema: "stock_analysis",
    description: "Structured trade setup analysis with explicit entry zone, stop loss, and upside target.",
    variables: [
      { key: "symbol", label: "Stock Symbol", placeholder: "e.g., TATAMOTORS, HDFCBANK", required: true },
      { key: "horizon", label: "Time Horizon", placeholder: "e.g., 2 weeks, 1-3 months", defaultValue: "1-3 months", required: false },
    ],
    generatePrompt: (v) =>
      `Conduct buy/sell research for ${v.symbol.toUpperCase()} for a ${
        v.horizon || "1-3 months"
      } horizon with entry price bracket, stop loss, and target price.`,
  },
  {
    id: "short_term_investment",
    name: "Short-Term Investment (Swing)",
    targetSchema: "stock_analysis",
    description: "Swing trade evaluation focusing on momentum indicators, 20-DMA, and key pivots.",
    variables: [
      { key: "symbol", label: "Stock Symbol", placeholder: "e.g., ICICIBANK, SBIN", required: true },
    ],
    generatePrompt: (v) =>
      `Analyze short-term swing trading setup for ${v.symbol.toUpperCase()} emphasizing 20-EMA, RSI momentum, and tight stop loss protection.`,
  },
  {
    id: "long_term_investment",
    name: "Long-Term Investment (Value)",
    targetSchema: "stock_analysis",
    description: "Multi-year fundamentals evaluation focusing on ROCE, ROE, debt profile, and growth.",
    variables: [
      { key: "symbol", label: "Stock Symbol", placeholder: "e.g., LICI, ITC, LT", required: true },
    ],
    generatePrompt: (v) =>
      `Evaluate multi-year fundamental investment merits for ${v.symbol.toUpperCase()} focusing on earnings quality, ROCE, debt-to-equity, and moat.`,
  },
  {
    id: "technical_analysis",
    name: "Technical Analysis",
    targetSchema: "technical_analysis",
    description: "Pure price action, moving averages (EMA/SMA), RSI, MACD, and candlestick patterns.",
    variables: [
      { key: "symbol", label: "Stock Symbol", placeholder: "e.g., NIFTY 50, TITAN", required: true },
    ],
    generatePrompt: (v) =>
      `Perform a pure technical analysis for ${v.symbol.toUpperCase()} covering RSI, MACD histogram, 20/50/200 EMAs, and key support/resistance levels.`,
  },
  {
    id: "fundamental_analysis",
    name: "Fundamental Analysis",
    targetSchema: "fundamental_analysis",
    description: "Financial ratios, balance sheet health, P/E, P/B, EPS, revenue, and net profit trends.",
    variables: [
      { key: "symbol", label: "Stock Symbol", placeholder: "e.g., BHARTIARTL, MARUTI", required: true },
    ],
    generatePrompt: (v) =>
      `Provide a fundamental financial analysis of ${v.symbol.toUpperCase()} including revenue, net profit, EPS, P/E, P/B, and debt metrics.`,
  },
  {
    id: "portfolio_analysis",
    name: "Portfolio Analysis",
    targetSchema: "portfolio_analysis",
    description: "Review portfolio diversification, concentration risk, and sector exposure.",
    variables: [
      {
        key: "holdings",
        label: "Holdings List",
        placeholder: "e.g., RELIANCE 30%, TCS 25%, HDFCBANK 25%, ITC 20%",
        required: true,
      },
    ],
    generatePrompt: (v) =>
      `Analyze this portfolio: ${v.holdings}. Evaluate asset allocation, sector exposure, and concentration risk.`,
  },
  {
    id: "stock_comparison",
    name: "Stock Comparison",
    targetSchema: "stock_comparison",
    description: "Side-by-side comparison of two or more Indian stocks across metrics.",
    variables: [
      { key: "symbol1", label: "First Stock", placeholder: "e.g., RELIANCE", required: true },
      { key: "symbol2", label: "Second Stock", placeholder: "e.g., INFY", required: true },
      { key: "symbol3", label: "Third Stock (Optional)", placeholder: "e.g., TCS", required: false },
    ],
    generatePrompt: (v) => {
      const symbols = [v.symbol1, v.symbol2, v.symbol3].filter(Boolean).map((s) => s.toUpperCase());
      return `Compare ${symbols.join(" vs ")} side by side across valuation, price performance, technicals, and risk profile.`;
    },
  },
  {
    id: "market_overview",
    name: "Market Overview",
    targetSchema: "market_overview",
    description: "Broad Indian market snapshot covering NIFTY 50, SENSEX, sentiment, and movers.",
    variables: [
      { key: "focus", label: "Focus Area (Optional)", placeholder: "e.g., IT vs Auto, Midcaps, or General", defaultValue: "General Indian Market", required: false },
    ],
    generatePrompt: (v) =>
      `Provide an Indian market overview for ${v.focus || "today"} analyzing NIFTY 50, SENSEX, BANK NIFTY, market sentiment, and top movers.`,
  },
  {
    id: "risk_assessment",
    name: "Risk Assessment",
    targetSchema: "stock_analysis",
    description: "Downside risk review, debt sustainability, volatility, and capital preservation.",
    variables: [
      { key: "symbol", label: "Stock Symbol", placeholder: "e.g., ADANIENT, VEDL", required: true },
    ],
    generatePrompt: (v) =>
      `Conduct a comprehensive downside risk assessment for ${v.symbol.toUpperCase()} covering leverage, beta, sector headwinds, and risk classification.`,
  },
];

interface PromptTemplateModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectTemplate: (prompt: string, templateId: string, schemaType: string) => void;
}

export function PromptTemplateModal({
  isOpen,
  onClose,
  onSelectTemplate,
}: PromptTemplateModalProps) {
  const [selectedId, setSelectedId] = useState<string>("complete_stock_analysis");
  const [variableValues, setVariableValues] = useState<Record<string, string>>({});
  const [validationError, setValidationError] = useState<string | null>(null);

  const activeTemplate = PROMPT_TEMPLATES.find((t) => t.id === selectedId) || PROMPT_TEMPLATES[0];

  const handleVariableChange = (key: string, value: string) => {
    setVariableValues((prev) => ({ ...prev, [key]: value }));
    setValidationError(null);
  };

  const handleApply = () => {
    // Validate required variables
    for (const v of activeTemplate.variables) {
      if (v.required && !variableValues[v.key]?.trim() && !v.defaultValue) {
        setValidationError(`Please provide a value for ${v.label}.`);
        return;
      }
    }

    const mergedValues: Record<string, string> = {};
    for (const v of activeTemplate.variables) {
      mergedValues[v.key] = variableValues[v.key]?.trim() || v.defaultValue || "";
    }

    const generated = activeTemplate.generatePrompt(mergedValues);
    onSelectTemplate(generated, activeTemplate.id, activeTemplate.targetSchema);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-xs">
        <motion.div
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.96 }}
          transition={snappyTransition}
          className="relative flex flex-col w-full max-w-3xl max-h-[85vh] rounded-2xl border border-[#E8EAE4] bg-[#FFFFFF] shadow-xl overflow-hidden"
        >
          {/* Header */}
          <div className="flex items-center justify-between border-b border-[#E8EAE4] px-6 py-4 bg-[#F8F8F5]">
            <div className="flex items-center gap-2.5">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#176B45] text-white">
                <Sparkles className="h-4 w-4" />
              </div>
              <div>
                <h2 className="text-sm font-semibold text-[#20251F]">
                  Analysis Prompt Templates
                </h2>
                <p className="text-[11px] text-[#777D76]">
                  Select a standardized Indian market research template
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="rounded-lg p-1 text-[#777D76] hover:bg-[#E8EAE4] hover:text-[#20251F] transition-colors cursor-pointer"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          {/* Body Split */}
          <div className="flex flex-1 overflow-hidden divide-x divide-[#E8EAE4]">
            {/* Template List */}
            <div className="w-1/3 overflow-y-auto p-3 space-y-1 bg-[#F8F8F5]/50">
              {PROMPT_TEMPLATES.map((tmpl) => {
                const isSelected = tmpl.id === selectedId;
                return (
                  <button
                    key={tmpl.id}
                    onClick={() => {
                      setSelectedId(tmpl.id);
                      setVariableValues({});
                      setValidationError(null);
                    }}
                    className={`w-full text-left rounded-xl p-2.5 text-xs transition-all cursor-pointer ${
                      isSelected
                        ? "bg-[#FFFFFF] text-[#176B45] font-medium shadow-xs border border-[#176B45]/20"
                        : "text-[#20251F] hover:bg-[#F1F2ED]"
                    }`}
                  >
                    <div className="truncate">{tmpl.name}</div>
                    <div className="text-[10px] text-[#777D76] truncate mt-0.5">
                      {tmpl.targetSchema.replace("_", " ")}
                    </div>
                  </button>
                );
              })}
            </div>

            {/* Template Parameter Form & Preview */}
            <div className="flex-1 overflow-y-auto p-5 flex flex-col justify-between space-y-4">
              <div className="space-y-4">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-sm font-medium text-[#20251F]">
                      {activeTemplate.name}
                    </h3>
                    <Badge variant="accent">
                      {activeTemplate.targetSchema.replace("_", " ")}
                    </Badge>
                  </div>
                  <p className="text-xs text-[#777D76] mt-1">
                    {activeTemplate.description}
                  </p>
                </div>

                {/* Variable Inputs */}
                <div className="space-y-3 pt-2">
                  <span className="text-[11px] font-semibold uppercase tracking-wider text-[#777D76]">
                    Template Parameters
                  </span>
                  {activeTemplate.variables.map((variable) => (
                    <div key={variable.key} className="space-y-1">
                      <label className="text-xs font-medium text-[#20251F] flex items-center gap-1">
                        <span>{variable.label}</span>
                        {variable.required && (
                          <span className="text-[#D64A4A]">*</span>
                        )}
                      </label>
                      <input
                        type="text"
                        value={variableValues[variable.key] ?? variable.defaultValue ?? ""}
                        onChange={(e) => handleVariableChange(variable.key, e.target.value)}
                        placeholder={variable.placeholder}
                        className="w-full rounded-xl border border-[#E8EAE4] bg-[#F8F8F5] px-3 py-2 text-xs text-[#20251F] placeholder-[#777D76] focus:border-[#176B45] focus:bg-[#FFFFFF] focus:outline-none transition-all"
                      />
                    </div>
                  ))}
                </div>

                {/* Validation error */}
                {validationError && (
                  <p className="text-xs text-[#D64A4A] font-medium">
                    {validationError}
                  </p>
                )}

                {/* Live Preview */}
                <div className="space-y-1 pt-1">
                  <span className="text-[11px] font-semibold uppercase tracking-wider text-[#777D76]">
                    Generated Prompt Preview
                  </span>
                  <div className="rounded-xl border border-[#E8EAE4] bg-[#F1F2ED]/60 p-3 text-xs text-[#20251F] font-mono leading-relaxed">
                    {activeTemplate.generatePrompt(
                      activeTemplate.variables.reduce((acc, v) => {
                        acc[v.key] = variableValues[v.key] || v.defaultValue || `[${v.label}]`;
                        return acc;
                      }, {} as Record<string, string>)
                    )}
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center justify-end gap-2 pt-4 border-t border-[#E8EAE4]">
                <Button size="sm" variant="outline" onClick={onClose}>
                  Cancel
                </Button>
                <Button size="sm" variant="primary" onClick={handleApply}>
                  <span>Insert into Composer</span>
                  <ArrowRight className="h-3.5 w-3.5 ml-1" />
                </Button>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
