/**
 * Stock Market Data TypeScript Definitions.
 * Aligned with Phase 7 backend schemas and provider specifications.
 */

export type DataFreshness =
  | "REAL_TIME"
  | "DELAYED"
  | "END_OF_DAY"
  | "HISTORICAL"
  | "UNAVAILABLE"
  | "UNKNOWN";

export type Exchange = "NSE" | "BSE";

export interface StockQuoteData {
  symbol: string;
  company_name: string;
  exchange: Exchange;
  currency: string;
  last_price: number | null;
  previous_close: number | null;
  change: number | null;
  change_percent: number | null;
  open: number | null;
  day_high: number | null;
  day_low: number | null;
  volume: number | null;
  market_cap: number | null;
  data_status: DataFreshness;
  source_name: string | null;
  market_timestamp: string | null;
  fetched_at: string | null;
}

export interface StockQuoteResponse {
  success: boolean;
  data: StockQuoteData;
}

export interface HistoricalCandle {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface HistoricalDataResponse {
  success: boolean;
  symbol: string;
  exchange: string;
  currency: string;
  range: string;
  interval: string;
  data_status: DataFreshness;
  source_name: string | null;
  fetched_at: string;
  candles: HistoricalCandle[];
}

export interface StockSearchResult {
  symbol: string;
  company_name: string;
  exchange: Exchange;
  currency: string;
  type: string;
}

export interface StockSearchResponse {
  success: boolean;
  query: string;
  results: StockSearchResult[];
  total: number;
}

export interface CompanyProfileData {
  symbol: string;
  company_name: string;
  exchange: Exchange;
  sector: string | null;
  industry: string | null;
  description: string | null;
  website: string | null;
  market_cap: number | null;
  pe_ratio: number | null;
  high_52w: number | null;
  low_52w: number | null;
  currency: string;
  data_status: DataFreshness;
  source_name: string | null;
  fetched_at: string;
}

export interface CompanyProfileResponse {
  success: boolean;
  data: CompanyProfileData;
}

export interface MarketStatusResponse {
  success: boolean;
  exchange: string;
  status: string;
  current_time: string;
  session: string;
  market_timezone: string;
}

export interface MarketIndexItem {
  symbol: string;
  name: string;
  value: number | null;
  change: number | null;
  percent_change: number | null;
  data_status: DataFreshness;
  timestamp: string;
}

export interface MarketIndicesResponse {
  success: boolean;
  indices: MarketIndexItem[];
  market_status: string;
  timestamp: string;
}

export interface WatchlistItem {
  symbol: string;
  company_name: string;
  exchange: Exchange;
  last_price: number | null;
  change: number | null;
  change_percent: number | null;
  data_status: DataFreshness;
  added_at: string;
}

export interface WatchlistResponse {
  success: boolean;
  items: WatchlistItem[];
  total: number;
}
