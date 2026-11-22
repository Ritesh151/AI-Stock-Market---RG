"""
Versioned Prompt Templates for RG AI Analysis Operations.
Each template strictly instructs analysis engines to return validated JSON matching target schemas.
"""

from typing import Dict, Optional
from app.core.validation_config import DEFAULT_SCHEMA_VERSION, STANDARD_FINANCIAL_DISCLAIMER


class PromptTemplate:
    """Represents a versioned system prompt template."""

    def __init__(
        self,
        name: str,
        template_id: str,
        target_schema_type: str,
        version: str = DEFAULT_SCHEMA_VERSION,
        instructions: str = "",
    ) -> None:
        self.name = name
        self.template_id = template_id
        self.target_schema_type = target_schema_type
        self.version = version
        self.instructions = instructions

    def format_prompt(self, user_prompt: str) -> str:
        """Composes template instructions with user prompt."""
        return (
            f"{self.instructions}\n\n"
            f"USER QUERY: {user_prompt}\n\n"
            f"MANDATORY OUTPUT REQUIREMENT: Output strictly valid JSON conforming to the "
            f"'{self.target_schema_type}' schema. Do NOT include markdown code fences, conversational greetings, "
            f"or postscript commentary. Use null for any unavailable metrics. Never fabricate values."
        )


_TEMPLATES: Dict[str, PromptTemplate] = {
    # 1. Complete Stock Analysis
    "complete_stock_analysis": PromptTemplate(
        name="Complete Stock Analysis",
        template_id="v1_complete_stock_analysis",
        target_schema_type="stock_analysis",
        instructions=(
            "Act as an Indian Equities Research Analyst (NSE/BSE). Perform an exhaustive stock analysis. "
            "Return a JSON object with: stock_name, symbol, exchange ('NSE'|'BSE'), currency ('INR'), "
            "current_price, price_change, price_change_percent, market_trend ('bullish'|'bearish'|'neutral'|'sideways'|'volatile'), "
            "recommendation ('BUY'|'SELL'|'HOLD'|'ACCUMULATE'|'REDUCE'|'NEUTRAL'|'AVOID'|'STRONG_BUY'|'STRONG_SELL'), "
            "entry_zone {min, max}, target_price, stop_loss, risk_level ('low'|'medium'|'high'|'very_high'), "
            "time_horizon, reasoning (list of rationale strings), technical_analysis (dict), fundamental_analysis (dict), "
            "data_timestamp (ISO-8601), data_source."
        ),
    ),
    # 2. Buy or Sell Research
    "buy_sell_research": PromptTemplate(
        name="Buy or Sell Research",
        template_id="v1_buy_sell_research",
        target_schema_type="stock_analysis",
        instructions=(
            "Conduct structured buy/sell trade setup research for the requested Indian equity. "
            "Provide explicit risk parameters: entry_zone {min, max}, target_price, stop_loss, and analytical recommendation. "
            "Ensure entry zone min <= max, and target/stop loss reflect risk-reward logic."
        ),
    ),
    # 3. Short-Term Investment
    "short_term_investment": PromptTemplate(
        name="Short-Term Investment (Swing)",
        template_id="v1_short_term_investment",
        target_schema_type="stock_analysis",
        instructions=(
            "Evaluate short-term swing trading setup (time horizon 1-4 weeks). Emphasize momentum indicators (RSI, 20-DMA), "
            "key pivot support/resistance levels, and tight stop loss protection."
        ),
    ),
    # 4. Long-Term Investment
    "long_term_investment": PromptTemplate(
        name="Long-Term Investment (Value)",
        template_id="v1_long_term_investment",
        target_schema_type="stock_analysis",
        instructions=(
            "Evaluate multi-year fundamental investment merits (time horizon 1-3 years). Emphasize ROCE, ROE, debt-to-equity, "
            "earnings visibility, sector tailwinds, and valuation multiples."
        ),
    ),
    # 5. Technical Analysis
    "technical_analysis": PromptTemplate(
        name="Technical Analysis",
        template_id="v1_technical_analysis",
        target_schema_type="technical_analysis",
        instructions=(
            "Perform pure technical analysis for the requested asset. Return JSON containing: "
            "rsi (0-100 float), macd {macd_line, signal_line, histogram}, moving_averages {ema_20, ema_50, ema_200, sma_20, sma_50, sma_200}, "
            "support_levels (list of positive floats), resistance_levels (list of positive floats), "
            "trend_direction ('bullish'|'bearish'|'neutral'|'reversal'|'sideways'), candlestick_patterns (list), data_source."
        ),
    ),
    # 6. Fundamental Analysis
    "fundamental_analysis": PromptTemplate(
        name="Fundamental Analysis",
        template_id="v1_fundamental_analysis",
        target_schema_type="fundamental_analysis",
        instructions=(
            "Perform corporate fundamental evaluation. Return JSON with: revenue, net_profit, eps, pe_ratio, pb_ratio, debt, "
            "roe, roce, market_capitalization, financial_reporting_period, data_source."
        ),
    ),
    # 7. Portfolio Analysis
    "portfolio_analysis": PromptTemplate(
        name="Portfolio Analysis",
        template_id="v1_portfolio_analysis",
        target_schema_type="portfolio_analysis",
        instructions=(
            "Analyze portfolio asset allocation, concentration risk, and sector exposure. Return JSON with: "
            "portfolio_value, holdings (list of {symbol, allocation_percent, current_value, sector}), "
            "asset_allocation (dict of asset category percentages), concentration_risk ('low'|'medium'|'high'|'critical'), "
            "sector_exposure (dict of sector percentages), risk_assessment, diversification_observations (list)."
        ),
    ),
    # 8. Stock Comparison
    "stock_comparison": PromptTemplate(
        name="Stock Comparison",
        template_id="v1_stock_comparison",
        target_schema_type="stock_comparison",
        instructions=(
            "Compare at least two Indian equities side by side. Return JSON with: "
            "stocks_compared (list of at least 2 distinct symbols), price_performance (dict), fundamental_metrics (dict), "
            "technical_metrics (dict), risk_comparison (dict), comparison_summary."
        ),
    ),
    # 9. Market Overview
    "market_overview": PromptTemplate(
        name="Market Overview",
        template_id="v1_market_overview",
        target_schema_type="market_overview",
        instructions=(
            "Generate comprehensive Indian market overview snapshot. Return JSON with: "
            "nifty_50 {current, change, percent_change}, sensex {current, change, percent_change}, bank_nifty {current, change, percent_change}, "
            "market_sentiment ('bullish'|'bearish'|'neutral'|'cautious'|'volatile'), top_gainers (list of {symbol, price, percent_change}), "
            "top_losers (list of {symbol, price, percent_change}), market_timestamp, data_sources."
        ),
    ),
    # 10. Risk Assessment
    "risk_assessment": PromptTemplate(
        name="Risk Assessment",
        template_id="v1_risk_assessment",
        target_schema_type="stock_analysis",
        instructions=(
            "Evaluate downside risks, beta, standard deviation, debt profile, and industry headwinds for the target stock. "
            "Classify risk_level ('low'|'medium'|'high'|'very_high') and establish clear stop_loss levels."
        ),
    ),
}


class TemplateManager:
    """Manages retrieval and formatting of analysis prompt templates."""

    @staticmethod
    def get_template(template_id: str) -> Optional[PromptTemplate]:
        """Retrieves template by ID or key."""
        return _TEMPLATES.get(template_id)

    @staticmethod
    def list_templates() -> Dict[str, str]:
        """Lists all available template IDs and names."""
        return {tid: t.name for tid, t in _TEMPLATES.items()}


_template_manager_instance: Optional[TemplateManager] = None


def get_template_manager() -> TemplateManager:
    """Returns singleton instance of TemplateManager."""
    global _template_manager_instance
    if _template_manager_instance is None:
        _template_manager_instance = TemplateManager()
    return _template_manager_instance
