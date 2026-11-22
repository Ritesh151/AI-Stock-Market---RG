"use client";

import { useState, useEffect } from "react";
import { overviewApi } from "../services/overview-api";
import { MarketOverviewResponse } from "../types/overview";

export function useMarketOverview(pollIntervalMs: number = 60000) {
  const [data, setData] = useState<MarketOverviewResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isCancelled = false;

    async function loadData() {
      try {
        const res = await overviewApi.getOverview("NSE");
        if (!isCancelled) {
          if (res && res.success) {
            setData(res);
            setError(null);
          } else {
            setError("Failed to load overview data.");
          }
        }
      } catch (err: unknown) {
        if (!isCancelled) {
          setError(err instanceof Error ? err.message : "Error fetching market overview");
        }
      } finally {
        if (!isCancelled) {
          setIsLoading(false);
          setIsRefreshing(false);
        }
      }
    }

    void loadData();

    let timer: NodeJS.Timeout | null = null;
    if (pollIntervalMs > 0) {
      timer = setInterval(loadData, pollIntervalMs);
    }

    return () => {
      isCancelled = true;
      if (timer) clearInterval(timer);
    };
  }, [pollIntervalMs]);

  const refresh = async () => {
    setIsRefreshing(true);
    try {
      const res = await overviewApi.getOverview("NSE");
      if (res && res.success) {
        setData(res);
        setError(null);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Error refreshing overview");
    } finally {
      setIsRefreshing(false);
    }
  };

  return {
    data,
    isLoading,
    isRefreshing,
    error,
    refresh,
  };
}
