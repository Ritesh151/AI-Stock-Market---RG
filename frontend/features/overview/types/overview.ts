/**
 * Overview Dashboard TypeScript Definitions.
 * Aligned with backend schemas in app.schemas.overview.
 */

import { DataFreshness } from "@/types/stock";

export interface MarketIndexOverviewItem {
  symbol: string;
  name: string;
  value: number | null;
  change: number | null;
  percent_change: number | null;
  previous_close: number | null;
  day_high: number | null;
  day_low: number | null;
  data_status: DataFreshness;
  source_name: string | null;
  timestamp: string;
  sparkline: number[];
}

export interface SentimentIndicators {
  index_momentum: number;
  volatility_vix: number;
  market_breadth: number;
}

export type MarketSentimentStatus =
  | "BULLISH"
  | "BEARISH"
  | "NEUTRAL"
  | "MIXED"
  | "UNAVAILABLE";

export interface MarketSentimentData {
  status: MarketSentimentStatus;
  score: number | null;
  indicators: SentimentIndicators | null;
  description: string;
  methodology: string;
  timestamp: string;
}

export interface StockMoverItem {
  symbol: string;
  company_name: string;
  last_price: number | null;
  change: number | null;
  change_percent: number | null;
  volume: number | null;
  exchange: string;
  data_status: DataFreshness;
  timestamp: string;
}

export interface MarketMoversData {
  gainers: StockMoverItem[];
  losers: StockMoverItem[];
  most_active: StockMoverItem[];
  ranking_metric: string;
  data_status: DataFreshness;
  timestamp: string;
}

export interface MarketNewsArticle {
  id: string;
  headline: string;
  publisher: string;
  published_at: string;
  url: string;
  related_symbols: string[];
  summary: string | null;
}

export interface MarketNewsData {
  status: "AVAILABLE" | "UNAVAILABLE";
  source_name: string | null;
  message: string | null;
  articles: MarketNewsArticle[];
  timestamp: string;
}

export interface MarketStatusData {
  exchange: string;
  status: "OPEN" | "CLOSED" | "PRE_OPEN" | "UNKNOWN";
  current_time: string;
  session: string;
  market_timezone: string;
  is_open?: boolean;
}

export interface MarketOverviewResponse {
  success: boolean;
  status: "SUCCESS" | "PARTIAL" | "UNAVAILABLE";
  exchange: string;
  market_status: MarketStatusData;
  indices: MarketIndexOverviewItem[];
  sentiment: MarketSentimentData;
  movers: MarketMoversData;
  news: MarketNewsData;
  timestamp: string;
  cache_ttl_seconds: number;
}
