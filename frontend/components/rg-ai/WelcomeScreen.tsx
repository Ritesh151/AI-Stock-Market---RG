"use client";

import React from "react";
import { motion } from "motion/react";
import {
  TrendingUp,
  BarChart3,
  GitCompare,
  PieChart,
  ShieldAlert,
  Sparkles,
  Search,
} from "lucide-react";
import { slideUpVariants, cardHoverTransition } from "@/lib/motionTokens";

interface WelcomeScreenProps {
  onSelectPrompt: (prompt: string) => void;
}

const SUGGESTIONS = [
  {
    title: "Analyze TCS stock",
    description: "Full research on Tata Consultancy Services (trend, target, valuation)",
    prompt: "Provide a comprehensive analysis of TCS on NSE including valuation, 20-DMA support, and analytical target price.",
    icon: TrendingUp,
  },
  {
    title: "Compare Reliance & Infosys",
    description: "Side-by-side comparison across valuations, earnings, and tech charts",
    prompt: "Compare Reliance Industries (RELIANCE) and Infosys (INFY) on NSE across P/E, price performance, and technical strength.",
    icon: GitCompare,
  },
  {
    title: "Explain today's NIFTY trend",
    description: "Macro snapshot of NIFTY 50, institutional flows, and key pivot levels",
    prompt: "Explain today's NIFTY 50 market trend with key support/resistance levels, sentiment, and sector rotation.",
    icon: BarChart3,
  },
  {
    title: "Perform technical analysis",
    description: "Evaluate RSI, MACD momentum, 20/50/200-EMAs, and candlestick patterns",
    prompt: "Perform a pure technical analysis of Tata Motors (TATAMOTORS) on NSE covering RSI, MACD, and moving averages.",
    icon: Search,
  },
  {
    title: "Evaluate investment risks",
    description: "Downside scenario testing, debt profile, and capital preservation",
    prompt: "Evaluate the primary downside investment risks, debt sustainability, and volatility for Adani Enterprises.",
    icon: ShieldAlert,
  },
  {
    title: "Analyze investment portfolio",
    description: "Assess sector concentration, asset weighting, and diversification",
    prompt: "Analyze my portfolio allocation: RELIANCE 30%, HDFCBANK 25%, TCS 25%, ITC 20%. Highlight concentration risk.",
    icon: PieChart,
  },
];

export function WelcomeScreen({ onSelectPrompt }: WelcomeScreenProps) {
  return (
    <motion.div
      variants={slideUpVariants}
      initial="hidden"
      animate="visible"
      className="flex flex-1 flex-col items-center justify-center p-6 text-center"
    >
      {/* Hero Badge & Heading */}
      <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-[#E8EAE4] bg-[#FFFFFF] px-3 py-1 shadow-xs">
        <Sparkles className="h-3.5 w-3.5 text-[#176B45]" />
        <span className="text-[11px] font-medium text-[#176B45]">
          RG AI Indian Equities Intelligence
        </span>
      </div>

      <h1 className="max-w-xl text-xl sm:text-2xl font-bold tracking-tight text-[#20251F]">
        Your Indian Stock Market Intelligence Assistant
      </h1>

      <p className="mt-2 max-w-lg text-xs sm:text-sm text-[#777D76]">
        Analyze stocks, understand market movements and make informed research decisions.
      </p>

      {/* Suggestion Cards Grid */}
      <div className="mt-8 grid w-full max-w-3xl grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3 text-left">
        {SUGGESTIONS.map((item, index) => {
          const IconComponent = item.icon;
          return (
            <motion.button
              key={index}
              whileHover={{ y: -2 }}
              transition={cardHoverTransition}
              onClick={() => onSelectPrompt(item.prompt)}
              className="group flex flex-col justify-between rounded-xl border border-[#E8EAE4] bg-[#FFFFFF] p-3.5 shadow-2xs hover:border-[#176B45]/40 hover:bg-[#F8F8F5] transition-colors cursor-pointer text-left"
            >
              <div className="flex items-center gap-2 mb-2">
                <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-[#F1F2ED] text-[#176B45] group-hover:bg-[#176B45] group-hover:text-white transition-colors">
                  <IconComponent className="h-3.5 w-3.5" />
                </div>
                <h3 className="text-xs font-semibold text-[#20251F] group-hover:text-[#176B45] transition-colors">
                  {item.title}
                </h3>
              </div>
              <p className="text-[11px] leading-relaxed text-[#777D76]">
                {item.description}
              </p>
            </motion.button>
          );
        })}
      </div>
    </motion.div>
  );
}
