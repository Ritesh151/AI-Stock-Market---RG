/**
 * Market Data & Stocks API Client.
 * Connects to FastAPI Phase 7 market data endpoints.
 */

import { apiClient } from "./apiClient";
import {
  StockQuoteResponse,
  HistoricalDataResponse,
  StockSearchResponse,
  CompanyProfileResponse,
  WatchlistResponse,
  MarketStatusResponse,
  MarketIndicesResponse,
} from "@/types/stock";

export const stocksApi = {
  /**
   * Search Indian stocks by symbol or company name.
   */
  async search(query: string, exchange?: string): Promise<StockSearchResponse> {
    const params = new URLSearchParams({ q: query });
    if (exchange) {
      params.append("exchange", exchange);
    }
    return apiClient<StockSearchResponse>(`/api/v1/stocks/search?${params.toString()}`);
  },

  /**
   * Retrieve normalized stock quote with freshness metadata.
   */
  async getQuote(symbol: string, exchange?: string): Promise<StockQuoteResponse> {
    const params = exchange ? `?exchange=${encodeURIComponent(exchange)}` : "";
    return apiClient<StockQuoteResponse>(`/api/v1/stocks/${encodeURIComponent(symbol)}/quote${params}`);
  },

  /**
   * Retrieve historical OHLCV candlestick data for charting.
   */
  async getHistory(
    symbol: string,
    range: string = "1M",
    interval: string = "1d",
    exchange?: string
  ): Promise<HistoricalDataResponse> {
    const params = new URLSearchParams({ range, interval });
    if (exchange) {
      params.append("exchange", exchange);
    }
    return apiClient<HistoricalDataResponse>(
      `/api/v1/stocks/${encodeURIComponent(symbol)}/history?${params.toString()}`
    );
  },

  /**
   * Retrieve fundamental company profile.
   */
  async getProfile(symbol: string, exchange?: string): Promise<CompanyProfileResponse> {
    const params = exchange ? `?exchange=${encodeURIComponent(exchange)}` : "";
    return apiClient<CompanyProfileResponse>(`/api/v1/stocks/${encodeURIComponent(symbol)}/profile${params}`);
  },

  /**
   * Fetch active watchlist items with optional search query and sorting.
   */
  async getWatchlist(q?: string, sortBy?: string): Promise<WatchlistResponse> {
    const params = new URLSearchParams();
    if (q) params.append("q", q);
    if (sortBy) params.append("sort_by", sortBy);
    const queryString = params.toString();
    return apiClient<WatchlistResponse>(`/api/v1/stocks/watchlist${queryString ? `?${queryString}` : ""}`);
  },

  /**
   * Add a stock to watchlist.
   */
  async addToWatchlist(symbol: string, exchange?: string): Promise<{ success: boolean; message: string }> {
    const params = exchange ? `?exchange=${encodeURIComponent(exchange)}` : "";
    return apiClient<{ success: boolean; message: string }>(
      `/api/v1/stocks/watchlist/${encodeURIComponent(symbol)}${params}`,
      { method: "POST" }
    );
  },

  /**
   * Remove a stock from watchlist.
   */
  async removeFromWatchlist(symbol: string): Promise<{ success: boolean; message: string }> {
    return apiClient<{ success: boolean; message: string }>(
      `/api/v1/stocks/watchlist/${encodeURIComponent(symbol)}`,
      { method: "DELETE" }
    );
  },

  /**
   * Retrieve real-time market session status for exchange.
   */
  async getMarketStatus(exchange?: string): Promise<MarketStatusResponse> {
    const params = exchange ? `?exchange=${encodeURIComponent(exchange)}` : "";
    return apiClient<MarketStatusResponse>(`/api/v1/market/status${params}`);
  },

  /**
   * Retrieve major Indian benchmark indices (NIFTY 50, SENSEX, etc.).
   */
  async getMarketIndices(): Promise<MarketIndicesResponse> {
    return apiClient<MarketIndicesResponse>("/api/v1/market/indices");
  },
};
