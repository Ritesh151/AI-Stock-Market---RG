"use client";

import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "motion/react";
import { Search, Loader2, X, Building2, ChevronRight } from "lucide-react";
import { stocksApi } from "@/services/stocksApi";
import { StockSearchResult, Exchange } from "@/types/stock";
import { snappyTransition } from "@/lib/motionTokens";

interface StockSearchProps {
  onSelectStock: (symbol: string, exchange: Exchange) => void;
  currentSymbol?: string;
}

export function StockSearch({ onSelectStock }: StockSearchProps) {
  const [query, setQuery] = useState("");
  const [exchangeFilter, setExchangeFilter] = useState<string>("ALL");
  const [results, setResults] = useState<StockSearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(0);

  const containerRef = useRef<HTMLDivElement>(null);
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Debounced search
  useEffect(() => {
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    const trimmed = query.trim();
    if (!trimmed) {
      debounceTimerRef.current = setTimeout(() => {
        setResults([]);
        setIsLoading(false);
      }, 0);
      return;
    }

    debounceTimerRef.current = setTimeout(async () => {
      setIsLoading(true);
      try {
        const exchangeParam = exchangeFilter === "ALL" ? undefined : exchangeFilter;
        const res = await stocksApi.search(trimmed, exchangeParam);
        if (res && res.success) {
          setResults(res.results || []);
          setIsOpen(true);
          setHighlightedIndex(0);
        }
      } catch {
        setResults([]);
      } finally {
        setIsLoading(false);
      }
    }, 300);

    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, [query, exchangeFilter]);

  // Handle outside click
  useEffect(() => {
    const handleOutsideClick = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleOutsideClick);
    return () => document.removeEventListener("mousedown", handleOutsideClick);
  }, []);

  const handleSelect = (stock: StockSearchResult) => {
    onSelectStock(stock.symbol, stock.exchange as Exchange);
    setQuery("");
    setResults([]);
    setIsOpen(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen || results.length === 0) return;

    if (e.key === "ArrowDown") {
      e.preventDefault();
      setHighlightedIndex((prev) => (prev + 1) % results.length);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setHighlightedIndex((prev) => (prev - 1 + results.length) % results.length);
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (results[highlightedIndex]) {
        handleSelect(results[highlightedIndex]);
      }
    } else if (e.key === "Escape") {
      setIsOpen(false);
    }
  };

  return (
    <div ref={containerRef} className="relative w-full">
      <div className="relative flex items-center">
        <Search className="pointer-events-none absolute left-3.5 h-4 w-4 text-[#777D76]" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => query.trim() && results.length > 0 && setIsOpen(true)}
          onKeyDown={handleKeyDown}
          placeholder="Search by ticker or company (e.g., RELIANCE, TCS, INFY)..."
          className="w-full rounded-xl border border-[#E8EAE4] bg-[#FFFFFF] py-2.5 pl-10 pr-24 text-xs font-medium text-[#20251F] placeholder-[#777D76] transition-all focus:border-[#176B45] focus:outline-none focus:ring-1 focus:ring-[#176B45]"
        />

        <div className="absolute right-2 flex items-center gap-1.5">
          {isLoading && <Loader2 className="h-3.5 w-3.5 animate-spin text-[#176B45]" />}
          {query && !isLoading && (
            <button
              onClick={() => {
                setQuery("");
                setResults([]);
              }}
              className="rounded-full p-1 text-[#777D76] hover:bg-[#F1F2ED] hover:text-[#20251F]"
              aria-label="Clear search"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          )}

          {/* Quick exchange filter pill */}
          <div className="flex rounded-lg border border-[#E8EAE4] bg-[#F1F2ED]/80 p-0.5 text-[10px] font-semibold">
            {["ALL", "NSE", "BSE"].map((ex) => (
              <button
                key={ex}
                type="button"
                onClick={() => setExchangeFilter(ex)}
                className={`rounded px-1.5 py-0.5 transition-colors cursor-pointer ${
                  exchangeFilter === ex
                    ? "bg-[#FFFFFF] text-[#176B45] shadow-xs"
                    : "text-[#777D76] hover:text-[#20251F]"
                }`}
              >
                {ex}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Autocomplete Dropdown */}
      <AnimatePresence>
        {isOpen && results.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            transition={snappyTransition}
            className="absolute z-50 mt-1.5 w-full rounded-xl border border-[#E8EAE4] bg-[#FFFFFF] p-1.5 shadow-lg max-h-80 overflow-y-auto"
          >
            <div className="px-2.5 py-1 text-[10px] font-semibold tracking-wider text-[#777D76] uppercase">
              Matching Securities ({results.length})
            </div>
            {results.map((stock, idx) => {
              const isHighlighted = idx === highlightedIndex;
              return (
                <div
                  key={`${stock.symbol}-${stock.exchange}`}
                  onClick={() => handleSelect(stock)}
                  onMouseEnter={() => setHighlightedIndex(idx)}
                  className={`flex items-center justify-between rounded-lg px-3 py-2 cursor-pointer transition-colors ${
                    isHighlighted ? "bg-[#F1F2ED]" : "hover:bg-[#F8F8F5]"
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-[#E8EAE4]/60 text-[#176B45]">
                      <Building2 className="h-3.5 w-3.5" />
                    </div>
                    <div>
                      <div className="flex items-center gap-1.5">
                        <span className="font-mono text-xs font-bold text-[#20251F]">
                          {stock.symbol}
                        </span>
                        <span className="rounded bg-[#F1F2ED] px-1.5 py-0.2 text-[9px] font-bold text-[#176B45]">
                          {stock.exchange}
                        </span>
                      </div>
                      <div className="text-[11px] text-[#777D76] line-clamp-1">
                        {stock.company_name}
                      </div>
                    </div>
                  </div>

                  <ChevronRight className="h-3.5 w-3.5 text-[#777D76]" />
                </div>
              );
            })}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
