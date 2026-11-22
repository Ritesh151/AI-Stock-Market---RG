"use client";

import { useState, useEffect } from "react";
import { stocksApi } from "@/services/stocksApi";
import {
  StockQuoteData,
  CompanyProfileData,
  WatchlistItem,
  Exchange,
} from "@/types/stock";

export function useStockData(
  initialSymbol: string = "RELIANCE",
  initialExchange: Exchange = "NSE"
) {
  const [symbol, setSymbol] = useState<string>(initialSymbol);
  const [exchange, setExchange] = useState<Exchange>(initialExchange);

  const [quote, setQuote] = useState<StockQuoteData | null>(null);
  const [profile, setProfile] = useState<CompanyProfileData | null>(null);
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);

  const [isQuoteLoading, setIsQuoteLoading] = useState<boolean>(true);
  const [isProfileLoading, setIsProfileLoading] = useState<boolean>(true);
  const [isWatchlistLoading, setIsWatchlistLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Load stock details when symbol or exchange changes
  useEffect(() => {
    let isCancelled = false;

    async function loadData() {
      try {
        const [qRes, pRes] = await Promise.allSettled([
          stocksApi.getQuote(symbol, exchange),
          stocksApi.getProfile(symbol, exchange),
        ]);

        if (!isCancelled) {
          if (qRes.status === "fulfilled" && qRes.value.success) {
            setQuote(qRes.value.data);
            setError(null);
          } else if (qRes.status === "rejected") {
            setError(
              qRes.reason instanceof Error
                ? qRes.reason.message
                : "Error fetching quote"
            );
          }

          if (pRes.status === "fulfilled" && pRes.value.success) {
            setProfile(pRes.value.data);
          } else {
            setProfile(null);
          }
        }
      } catch (err: unknown) {
        if (!isCancelled) {
          setError(
            err instanceof Error ? err.message : "Error fetching stock details"
          );
        }
      } finally {
        if (!isCancelled) {
          setIsQuoteLoading(false);
          setIsProfileLoading(false);
        }
      }
    }

    void loadData();

    return () => {
      isCancelled = true;
    };
  }, [symbol, exchange]);

  // Load initial watchlist on mount
  useEffect(() => {
    let isCancelled = false;

    async function loadWatchlist() {
      try {
        const res = await stocksApi.getWatchlist();
        if (!isCancelled && res && res.success) {
          setWatchlist(res.items || []);
        }
      } catch {
        // Fallback
      } finally {
        if (!isCancelled) {
          setIsWatchlistLoading(false);
        }
      }
    }

    void loadWatchlist();

    return () => {
      isCancelled = true;
    };
  }, []);

  // Switch active stock (user event)
  const selectStock = (newSymbol: string, newExchange: Exchange = "NSE") => {
    setIsQuoteLoading(true);
    setIsProfileLoading(true);
    setSymbol(newSymbol);
    setExchange(newExchange);
  };

  // Manual refresh (user event)
  const refresh = async () => {
    setIsQuoteLoading(true);
    setIsProfileLoading(true);
    setIsWatchlistLoading(true);
    try {
      const [qRes, pRes, wRes] = await Promise.allSettled([
        stocksApi.getQuote(symbol, exchange),
        stocksApi.getProfile(symbol, exchange),
        stocksApi.getWatchlist(),
      ]);
      if (qRes.status === "fulfilled" && qRes.value.success) {
        setQuote(qRes.value.data);
        setError(null);
      }
      if (pRes.status === "fulfilled" && pRes.value.success) {
        setProfile(pRes.value.data);
      }
      if (wRes.status === "fulfilled" && wRes.value.success) {
        setWatchlist(wRes.value.items || []);
      }
    } finally {
      setIsQuoteLoading(false);
      setIsProfileLoading(false);
      setIsWatchlistLoading(false);
    }
  };

  // Add / remove watchlist toggle (user event)
  const toggleWatchlist = async (sym: string = symbol, ex: Exchange = exchange) => {
    const isPresent = watchlist.some((item) => item.symbol === sym);
    try {
      if (isPresent) {
        await stocksApi.removeFromWatchlist(sym);
        setWatchlist((prev) => prev.filter((item) => item.symbol !== sym));
      } else {
        await stocksApi.addToWatchlist(sym, ex);
        const res = await stocksApi.getWatchlist();
        if (res && res.success) {
          setWatchlist(res.items);
        }
      }
    } catch {
      const res = await stocksApi.getWatchlist();
      if (res && res.success) {
        setWatchlist(res.items);
      }
    }
  };

  const removeFromWatchlist = async (sym: string) => {
    try {
      await stocksApi.removeFromWatchlist(sym);
      setWatchlist((prev) => prev.filter((item) => item.symbol !== sym));
    } catch {
      const res = await stocksApi.getWatchlist();
      if (res && res.success) {
        setWatchlist(res.items);
      }
    }
  };

  const isInWatchlist = watchlist.some((item) => item.symbol === symbol);

  return {
    symbol,
    exchange,
    quote,
    profile,
    watchlist,
    isInWatchlist,
    isQuoteLoading,
    isProfileLoading,
    isWatchlistLoading,
    error,
    selectStock,
    refresh,
    toggleWatchlist,
    removeFromWatchlist,
  };
}
