"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  Building,
  Globe,
  Sparkles,
  Star,
  ExternalLink,
  ChevronRight,
} from "lucide-react";
import { CompanyProfileData, Exchange } from "@/types/stock";

interface StockDetailsProps {
  profile: CompanyProfileData | null;
  symbol: string;
  exchange: Exchange;
  isInWatchlist: boolean;
  onToggleWatchlist: () => void;
  isWatchlistLoading?: boolean;
}

export function StockDetails({
  profile,
  symbol,
  exchange,
  isInWatchlist,
  onToggleWatchlist,
  isWatchlistLoading = false,
}: StockDetailsProps) {
  const [showFullSummary, setShowFullSummary] = useState(false);

  // Formatting helpers with strict null preservation
  const formatRatio = (val: number | null | undefined): string => {
    if (val === null || val === undefined) return "Not available";
    return `${val.toFixed(2)}x`;
  };

  const formatPrice = (val: number | null | undefined): string => {
    if (val === null || val === undefined) return "Not available";
    return `₹${val.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  const aiPrompt = `Perform in-depth RG AI financial intelligence analysis on ${symbol} (${exchange}). Provide institutional insights on valuation, technical momentum, key catalysts, and risk factors.`;

  return (
    <div className="w-full rounded-2xl border border-[#E8EAE4] bg-[#FFFFFF] p-6 shadow-xs space-y-6">
      {/* Top Header: Actions */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between border-b border-[#E8EAE4] pb-5">
        <div>
          <div className="flex items-center gap-2">
            <Building className="h-4 w-4 text-[#176B45]" />
            <h3 className="font-semibold text-base text-[#20251F]">
              Company Profile & Intelligence
            </h3>
          </div>
          <p className="mt-0.5 text-xs text-[#777D76]">
            Sector classification, valuation metrics, and institutional intelligence.
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center gap-2.5">
          {/* Watchlist Toggle */}
          <button
            onClick={onToggleWatchlist}
            disabled={isWatchlistLoading}
            className={`inline-flex items-center gap-1.5 rounded-xl border px-3.5 py-2 text-xs font-semibold transition-all cursor-pointer ${
              isInWatchlist
                ? "border-[#176B45] bg-[#176B45]/10 text-[#176B45]"
                : "border-[#E8EAE4] bg-[#FFFFFF] text-[#20251F] hover:bg-[#F1F2ED]"
            }`}
          >
            <Star
              className={`h-4 w-4 ${
                isInWatchlist ? "fill-[#176B45] text-[#176B45]" : "text-[#777D76]"
              }`}
            />
            <span>{isInWatchlist ? "In Watchlist" : "Add to Watchlist"}</span>
          </button>

          {/* RG AI Analysis Bridge Button */}
          <Link
            href={`/rg-ai?prompt=${encodeURIComponent(aiPrompt)}`}
            className="inline-flex items-center gap-1.5 rounded-xl bg-[#176B45] px-4 py-2 text-xs font-semibold text-white shadow-xs transition-all hover:bg-[#125837] active:scale-98 cursor-pointer"
          >
            <Sparkles className="h-4 w-4" />
            <span>Open RG AI Analysis</span>
            <ChevronRight className="h-3.5 w-3.5" />
          </Link>
        </div>
      </div>

      {/* Fundamental Ratios Grid */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <div className="rounded-xl border border-[#E8EAE4] bg-[#F8F8F5] p-3.5">
          <span className="text-[11px] font-medium text-[#777D76]">P/E Ratio (TTM)</span>
          <div className="mt-1 font-mono text-sm font-bold text-[#20251F]">
            {formatRatio(profile?.pe_ratio)}
          </div>
        </div>

        <div className="rounded-xl border border-[#E8EAE4] bg-[#F8F8F5] p-3.5">
          <span className="text-[11px] font-medium text-[#777D76]">52-Week High</span>
          <div className="mt-1 font-mono text-sm font-bold text-[#16834A]">
            {formatPrice(profile?.high_52w)}
          </div>
        </div>

        <div className="rounded-xl border border-[#E8EAE4] bg-[#F8F8F5] p-3.5">
          <span className="text-[11px] font-medium text-[#777D76]">52-Week Low</span>
          <div className="mt-1 font-mono text-sm font-bold text-[#D64A4A]">
            {formatPrice(profile?.low_52w)}
          </div>
        </div>

        <div className="rounded-xl border border-[#E8EAE4] bg-[#F8F8F5] p-3.5">
          <span className="text-[11px] font-medium text-[#777D76]">Sector</span>
          <div className="mt-1 font-sans text-xs font-bold text-[#20251F] line-clamp-1">
            {profile?.sector || "Not available"}
          </div>
        </div>
      </div>

      {/* Industry & Links */}
      <div className="flex flex-wrap items-center gap-y-2 gap-x-6 text-xs text-[#777D76]">
        <div>
          <span className="font-medium text-[#20251F]">Industry: </span>
          <span>{profile?.industry || "Not available"}</span>
        </div>

        {profile?.website && (
          <a
            href={profile.website}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-[#176B45] hover:underline"
          >
            <Globe className="h-3.5 w-3.5" />
            <span>Corporate Website</span>
            <ExternalLink className="h-3 w-3" />
          </a>
        )}
      </div>

      {/* Description / Summary */}
      {profile?.description && (
        <div className="rounded-xl border border-[#E8EAE4] bg-[#F1F2ED]/30 p-4">
          <h4 className="text-xs font-semibold text-[#20251F] mb-1.5">Business Overview</h4>
          <p
            className={`text-xs leading-relaxed text-[#777D76] ${
              !showFullSummary ? "line-clamp-3" : ""
            }`}
          >
            {profile.description}
          </p>
          {profile.description.length > 220 && (
            <button
              onClick={() => setShowFullSummary(!showFullSummary)}
              className="mt-2 text-xs font-medium text-[#176B45] hover:underline cursor-pointer"
            >
              {showFullSummary ? "Show less" : "Read full overview"}
            </button>
          )}
        </div>
      )}
    </div>
  );
}
