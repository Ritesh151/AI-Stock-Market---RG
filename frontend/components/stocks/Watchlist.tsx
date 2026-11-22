"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import {
  Star,
  Search,
  Trash2,
  TrendingUp,
  TrendingDown,
  ArrowUpDown,
  Building2,
} from "lucide-react";
import { WatchlistItem, Exchange } from "@/types/stock";
import { snappyTransition } from "@/lib/motionTokens";

interface WatchlistProps {
  items: WatchlistItem[];
  selectedSymbol: string;
  onSelectStock: (symbol: string, exchange: Exchange) => void;
  onRemoveItem: (symbol: string) => void;
  isLoading?: boolean;
}

export function Watchlist({
  items,
  selectedSymbol,
  onSelectStock,
  onRemoveItem,
  isLoading = false,
}: WatchlistProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [sortBy, setSortBy] = useState<"name" | "price_change" | "change_percent">("name");

  // Client-side filtering & sorting for instant responsiveness
  const filtered = items
    .filter((item) => {
      const q = searchQuery.toLowerCase();
      return (
        item.symbol.toLowerCase().includes(q) ||
        item.company_name.toLowerCase().includes(q)
      );
    })
    .sort((a, b) => {
      if (sortBy === "name") {
        return a.symbol.localeCompare(b.symbol);
      }
      if (sortBy === "price_change") {
        return (b.change ?? 0) - (a.change ?? 0);
      }
      if (sortBy === "change_percent") {
        return (b.change_percent ?? 0) - (a.change_percent ?? 0);
      }
      return 0;
    });

  return (
    <div className="w-full rounded-2xl border border-[#E8EAE4] bg-[#FFFFFF] p-4 shadow-xs space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-[#E8EAE4] pb-3">
        <div className="flex items-center gap-2">
          <Star className="h-4 w-4 fill-[#176B45] text-[#176B45]" />
          <h3 className="font-semibold text-sm text-[#20251F]">
            My Watchlist
          </h3>
          <span className="rounded-full bg-[#F1F2ED] px-2 py-0.5 text-[10px] font-mono font-bold text-[#777D76]">
            {items.length}
          </span>
        </div>

        {/* Sort Dropdown */}
        <div className="flex items-center gap-1.5 text-xs text-[#777D76]">
          <ArrowUpDown className="h-3 w-3" />
          <select
            value={sortBy}
            onChange={(e) =>
              setSortBy(
                e.target.value as "name" | "price_change" | "change_percent"
              )
            }
            className="rounded-lg border border-[#E8EAE4] bg-[#F8F8F5] px-2 py-1 text-[11px] font-medium text-[#20251F] focus:outline-none focus:ring-1 focus:ring-[#176B45] cursor-pointer"
          >
            <option value="name">Sort: Symbol</option>
            <option value="change_percent">Sort: % Change</option>
            <option value="price_change">Sort: ₹ Change</option>
          </select>
        </div>
      </div>

      {/* Search in Watchlist */}
      {items.length > 3 && (
        <div className="relative">
          <Search className="absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-[#777D76]" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Filter watchlist..."
            className="w-full rounded-xl border border-[#E8EAE4] bg-[#F8F8F5] py-1.5 pl-8 pr-3 text-xs text-[#20251F] placeholder-[#777D76] focus:border-[#176B45] focus:outline-none"
          />
        </div>
      )}

      {/* Items List */}
      <div className="space-y-1.5 max-h-[360px] overflow-y-auto">
        {isLoading && items.length === 0 ? (
          <div className="py-8 text-center text-xs text-[#777D76]">
            Loading watchlist...
          </div>
        ) : filtered.length === 0 ? (
          <div className="py-8 text-center text-xs text-[#777D76] space-y-1">
            <Building2 className="h-6 w-6 text-[#777D76]/50 mx-auto mb-1" />
            <p>
              {searchQuery
                ? "No stocks match your filter."
                : "Your watchlist is empty."}
            </p>
            {!searchQuery && (
              <p className="text-[11px] text-[#777D76]/80">
                Search and click &ldquo;Add to Watchlist&rdquo; to track stocks.
              </p>
            )}
          </div>
        ) : (
          <AnimatePresence initial={false}>
            {filtered.map((item) => {
              const isSelected = selectedSymbol === item.symbol;
              const isPos = (item.change ?? 0) >= 0;

              return (
                <motion.div
                  key={item.symbol}
                  layout
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  transition={snappyTransition}
                  onClick={() => onSelectStock(item.symbol, item.exchange)}
                  className={`group flex items-center justify-between rounded-xl p-2.5 cursor-pointer transition-all ${
                    isSelected
                      ? "bg-[#176B45]/10 border border-[#176B45]/30 shadow-xs"
                      : "border border-transparent hover:border-[#E8EAE4] hover:bg-[#F8F8F5]"
                  }`}
                >
                  <div className="flex items-center gap-2.5 min-w-0">
                    <div>
                      <div className="flex items-center gap-1.5">
                        <span className="font-mono text-xs font-bold text-[#20251F]">
                          {item.symbol}
                        </span>
                        <span className="rounded bg-[#F1F2ED] px-1 py-0.2 text-[9px] font-bold text-[#176B45]">
                          {item.exchange}
                        </span>
                      </div>
                      <div className="text-[11px] text-[#777D76] truncate max-w-[140px]">
                        {item.company_name}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <div className="text-right">
                      <div className="font-mono text-xs font-bold text-[#20251F]">
                        {item.last_price != null
                          ? `₹${item.last_price.toFixed(2)}`
                          : "Not available"}
                      </div>
                      {item.change_percent != null && (
                        <div
                          className={`inline-flex items-center font-mono text-[10px] font-semibold ${
                            isPos ? "text-[#16834A]" : "text-[#D64A4A]"
                          }`}
                        >
                          {isPos ? (
                            <TrendingUp className="mr-0.5 h-2.5 w-2.5" />
                          ) : (
                            <TrendingDown className="mr-0.5 h-2.5 w-2.5" />
                          )}
                          {isPos ? "+" : ""}
                          {item.change_percent.toFixed(2)}%
                        </div>
                      )}
                    </div>

                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onRemoveItem(item.symbol);
                      }}
                      className="opacity-0 group-hover:opacity-100 rounded-lg p-1 text-[#777D76] hover:bg-[#D64A4A]/10 hover:text-[#D64A4A] transition-all cursor-pointer"
                      title="Remove from watchlist"
                      aria-label={`Remove ${item.symbol} from watchlist`}
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  </div>
                </motion.div>
              );
            })}
          </AnimatePresence>
        )}
      </div>
    </div>
  );
}
