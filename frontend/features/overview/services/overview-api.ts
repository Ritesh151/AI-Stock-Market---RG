/**
 * Overview Dashboard API Service.
 * Connects to Phase 8 backend endpoints (/api/v1/overview/*).
 */

import { apiClient } from "@/services/apiClient";
import {
  MarketIndexOverviewItem,
  MarketMoversData,
  MarketNewsData,
  MarketOverviewResponse,
  MarketStatusData,
} from "../types/overview";

export const overviewApi = {
  /**
   * Fetches full aggregated dashboard state with partial failure resilience.
   */
  async getOverview(exchange: string = "NSE"): Promise<MarketOverviewResponse> {
    const params = new URLSearchParams({ exchange });
    return apiClient<MarketOverviewResponse>(`/api/v1/overview?${params.toString()}`);
  },

  /**
   * Fetches benchmark indices with session stats and sparklines.
   */
  async getIndices(): Promise<MarketIndexOverviewItem[]> {
    return apiClient<MarketIndexOverviewItem[]>("/api/v1/overview/indices");
  },

  /**
   * Fetches top gainers, losers, and most active stocks.
   */
  async getMovers(exchange: string = "NSE"): Promise<MarketMoversData> {
    const params = new URLSearchParams({ exchange });
    return apiClient<MarketMoversData>(`/api/v1/overview/movers?${params.toString()}`);
  },

  /**
   * Fetches Indian market session status and IST calendar.
   */
  async getMarketStatus(exchange: string = "NSE"): Promise<MarketStatusData> {
    const params = new URLSearchParams({ exchange });
    return apiClient<MarketStatusData>(`/api/v1/overview/market-status?${params.toString()}`);
  },

  /**
   * Fetches live market news stream.
   */
  async getNews(): Promise<MarketNewsData> {
    return apiClient<MarketNewsData>("/api/v1/overview/news");
  },
};
