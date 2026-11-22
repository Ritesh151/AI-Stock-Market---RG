"""
Overview Dashboard Pydantic Schemas.
Defines contracts for aggregated market dashboard, index cards, sentiment,
movers (gainers/losers/most active), and market news.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.integrations.market_data.provider_config import DataFreshness


class MarketIndexOverviewItem(BaseModel):
    """Index card benchmark item with session statistics and mini sparkline."""

    symbol: str = Field(..., description="Index symbol, e.g., ^NSEI")
    name: str = Field(..., description="Index title, e.g., NIFTY 50")
    value: Optional[float] = Field(default=None, description="Current index points")
    change: Optional[float] = Field(default=None, description="Absolute points change")
    percent_change: Optional[float] = Field(default=None, description="Percentage change")
    previous_close: Optional[float] = Field(default=None, description="Previous session close")
    day_high: Optional[float] = Field(default=None, description="Session peak")
    day_low: Optional[float] = Field(default=None, description="Session trough")
    data_status: str = Field(
        default=DataFreshness.UNKNOWN.value,
        description="Freshness classification (REAL_TIME, DELAYED, etc.)",
    )
    source_name: Optional[str] = Field(default=None, description="Data source attribution")
    timestamp: str = Field(..., description="Timestamp of fetch or quote")
    sparkline: List[float] = Field(
        default_factory=list,
        description="Recent trend values for miniature chart",
    )


class SentimentIndicators(BaseModel):
    """Underlying quantitative indicators driving market sentiment."""

    index_momentum: float = Field(..., description="Normalized benchmark return score [-1.0, 1.0]")
    volatility_vix: float = Field(..., description="Normalized India VIX volatility score [-1.0, 1.0]")
    market_breadth: float = Field(..., description="Advance/Decline score [-1.0, 1.0]")


class MarketSentimentData(BaseModel):
    """Documented composite market sentiment."""

    status: str = Field(..., description="Overall classification: BULLISH, BEARISH, NEUTRAL, MIXED, UNAVAILABLE")
    score: Optional[float] = Field(default=None, description="Composite score between -1.0 and 1.0")
    indicators: Optional[SentimentIndicators] = Field(default=None, description="Component metrics")
    description: str = Field(..., description="Human-readable explanation of current market stance")
    methodology: str = Field(..., description="Documented formula, weights, and limitations")
    timestamp: str = Field(..., description="Calculation timestamp")


class StockMoverItem(BaseModel):
    """Single stock mover item (gainer, loser, or active)."""

    symbol: str
    company_name: str
    last_price: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    volume: Optional[int] = None
    exchange: str = "NSE"
    data_status: str = DataFreshness.UNKNOWN.value
    timestamp: str


class MarketMoversData(BaseModel):
    """Categorized market leaders and laggards."""

    gainers: List[StockMoverItem] = Field(default_factory=list, description="Top positive percentage movers")
    losers: List[StockMoverItem] = Field(default_factory=list, description="Top negative percentage movers")
    most_active: List[StockMoverItem] = Field(default_factory=list, description="Top stocks ranked by trading volume")
    ranking_metric: str = Field(default="Trading Volume (shares)", description="Metric used for ranking active stocks")
    data_status: str = DataFreshness.DELAYED.value
    timestamp: str


class MarketNewsArticle(BaseModel):
    """Single legitimate Indian financial news article."""

    id: str
    headline: str
    publisher: str
    published_at: str
    url: str
    related_symbols: List[str] = Field(default_factory=list)
    summary: Optional[str] = None


class MarketNewsData(BaseModel):
    """Market news stream payload."""

    status: str = Field(..., description="AVAILABLE or UNAVAILABLE")
    source_name: Optional[str] = None
    message: Optional[str] = None
    articles: List[MarketNewsArticle] = Field(default_factory=list)
    timestamp: str


class MarketOverviewResponse(BaseModel):
    """Aggregated market intelligence overview response with partial failure resilience."""

    success: bool = True
    status: str = Field(default="SUCCESS", description="SUCCESS, PARTIAL, or UNAVAILABLE")
    exchange: str = "NSE"
    market_status: Dict[str, Any]
    indices: List[MarketIndexOverviewItem] = Field(default_factory=list)
    sentiment: MarketSentimentData
    movers: MarketMoversData
    news: MarketNewsData
    timestamp: str
    cache_ttl_seconds: int = 60
