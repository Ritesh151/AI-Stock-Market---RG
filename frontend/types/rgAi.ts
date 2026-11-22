/**
 * Comprehensive TypeScript types for RG AI Chat, Schemas, and Request Lifecycle.
 */

export type RequestLifecycleStatus =
  | "idle"
  | "queued"
  | "initializing"
  | "waiting_for_login"
  | "submitting"
  | "processing"
  | "validating"
  | "completed"
  | "failed"
  | "cancelled"
  | "integration_unavailable";

export type SupportedSchemaType =
  | "stock_analysis"
  | "technical_analysis"
  | "fundamental_analysis"
  | "portfolio_analysis"
  | "stock_comparison"
  | "market_overview"
  | "educational_content";

// 1. Stock Analysis Schema Data
export interface StockAnalysisData {
  stock_name: string;
  symbol: string;
  exchange: "NSE" | "BSE" | "MCX" | string;
  currency: "INR" | string;
  current_price: number | null;
  price_change: number | null;
  price_change_percent: number | null;
  market_trend: "bullish" | "bearish" | "neutral" | "sideways" | "volatile" | string;
  recommendation:
    | "BUY"
    | "SELL"
    | "HOLD"
    | "ACCUMULATE"
    | "REDUCE"
    | "NEUTRAL"
    | "AVOID"
    | "STRONG_BUY"
    | "STRONG_SELL"
    | string;
  entry_zone: {
    min: number | null;
    max: number | null;
  };
  target_price: number | null;
  stop_loss: number | null;
  risk_level: "low" | "medium" | "high" | "very_high" | string;
  time_horizon: string | null;
  reasoning: string[];
  technical_indicators?: Record<string, unknown> | null;
  fundamental_factors?: Record<string, unknown> | null;
  data_timestamp?: string | null;
  data_source?: string | null;
}

// 2. Technical Analysis Schema Data
export interface TechnicalAnalysisData {
  rsi: number | null;
  macd: {
    macd_line: number | null;
    signal_line: number | null;
    histogram: number | null;
  } | null;
  moving_averages: {
    ema_20?: number | null;
    ema_50?: number | null;
    ema_200?: number | null;
    sma_20?: number | null;
    sma_50?: number | null;
    sma_200?: number | null;
  } | null;
  support_levels: number[];
  resistance_levels: number[];
  trend_direction: "bullish" | "bearish" | "neutral" | "reversal" | "sideways" | string;
  candlestick_patterns: string[];
  data_source?: string | null;
}

// 3. Fundamental Analysis Schema Data
export interface FundamentalAnalysisData {
  revenue: number | null;
  net_profit: number | null;
  eps: number | null;
  pe_ratio: number | null;
  pb_ratio: number | null;
  debt: number | null;
  roe: number | null;
  roce: number | null;
  market_capitalization: number | null;
  financial_reporting_period?: string | null;
  data_source?: string | null;
}

// 4. Portfolio Analysis Schema Data
export interface PortfolioHolding {
  symbol: string;
  allocation_percent: number;
  current_value?: number | null;
  sector?: string | null;
}

export interface PortfolioAnalysisData {
  portfolio_value: number | null;
  holdings: PortfolioHolding[];
  asset_allocation: Record<string, number>;
  concentration_risk: "low" | "medium" | "high" | "critical" | string;
  sector_exposure: Record<string, number>;
  risk_assessment: string | null;
  diversification_observations: string[];
}

// 5. Stock Comparison Schema Data
export interface StockComparisonData {
  stocks_compared: string[];
  price_performance: Record<string, unknown>;
  fundamental_metrics: Record<string, unknown>;
  technical_metrics: Record<string, unknown>;
  risk_comparison: Record<string, unknown>;
  comparison_summary: string;
}

// 6. Market Overview Schema Data
export interface IndexSummary {
  current: number | null;
  change: number | null;
  percent_change: number | null;
}

export interface MarketMover {
  symbol: string;
  price: number;
  percent_change: number;
}

export interface MarketOverviewData {
  nifty_50: IndexSummary;
  sensex: IndexSummary;
  bank_nifty: IndexSummary;
  market_sentiment: "bullish" | "bearish" | "neutral" | "cautious" | "volatile" | string;
  top_gainers: MarketMover[];
  top_losers: MarketMover[];
  market_timestamp?: string | null;
  data_sources?: string[] | null;
}

// 7. Educational Content Schema Data
export interface EducationalContentData {
  concept: string;
  category: string;
  difficulty_level: "beginner" | "intermediate" | "advanced" | string;
  summary: string;
  key_principles: string[];
  practical_examples: string[];
  glossary: Record<string, string>;
}

// Canonical Response Envelope
export interface ResponseEnvelope<T = Record<string, unknown>> {
  success: boolean;
  type: SupportedSchemaType | string;
  schema_version: string;
  request_id: string;
  data: T;
  warnings?: string[] | null;
  disclaimer: string;
  execution_metadata?: Record<string, unknown> | null;
}

// Validation Error Envelope
export interface ValidationErrorDetail {
  field?: string | null;
  issue: string;
}

export interface ValidationErrorPayload {
  code: string;
  message: string;
  details?: ValidationErrorDetail[] | null;
}

export interface ValidationErrorEnvelope {
  success: false;
  type: "validation_error";
  request_id?: string | null;
  error: ValidationErrorPayload;
}

// Chat Message Model
export interface ChatMessage {
  id: string;
  sender: "user" | "rg_ai";
  content: string;
  timestamp: string;
  requestId?: string;
  status?: RequestLifecycleStatus;
  envelope?: ResponseEnvelope | null;
  error?: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  } | null;
  metadata?: {
    templateId?: string;
    targetSchema?: string;
    queuePosition?: number;
  };
}

// Conversation Model
export interface Conversation {
  id: string;
  title: string;
  createdAt: string;
  updatedAt: string;
  messages: ChatMessage[];
}

export interface ConversationSummary {
  id: string;
  title: string;
  createdAt: string;
  updatedAt: string;
  messageCount: number;
  lastMessagePreview?: string;
}

// Prompt Template Definition
export interface TemplateVariable {
  key: string;
  label: string;
  placeholder: string;
  defaultValue?: string;
  required: boolean;
}

export interface PromptTemplateItem {
  id: string;
  name: string;
  targetSchema: SupportedSchemaType;
  description: string;
  variables: TemplateVariable[];
  generatePrompt: (values: Record<string, string>) => string;
}
