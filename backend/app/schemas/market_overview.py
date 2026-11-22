"""
Market Overview Pydantic Schema.
Strict validation of Indian headline indices, market breadth, and top movers.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class MarketSentimentEnum(str, Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"
    CAUTIOUS = "cautious"
    VOLATILE = "volatile"


class IndexData(BaseModel):
    current: Optional[float] = Field(default=None, description="Current index points")
    change: Optional[float] = Field(default=None, description="Absolute change")
    percent_change: Optional[float] = Field(default=None, description="Percentage change")


class MoverItem(BaseModel):
    symbol: str = Field(..., description="Stock symbol")
    price: Optional[float] = Field(default=None, description="LTP price")
    percent_change: Optional[float] = Field(default=None, description="Percentage gain or loss")


class MarketOverviewSchema(BaseModel):
    """Schema for broader Indian market overview and index sentiment."""

    nifty_50: Optional[IndexData] = Field(default=None, description="NIFTY 50 index performance")
    sensex: Optional[IndexData] = Field(default=None, description="BSE SENSEX index performance")
    bank_nifty: Optional[IndexData] = Field(default=None, description="NIFTY Bank index performance")
    market_sentiment: Optional[MarketSentimentEnum] = Field(
        default=None, description="Evaluated market breadth sentiment"
    )
    top_gainers: List[MoverItem] = Field(
        default_factory=list, description="Top gaining equities in the session"
    )
    top_losers: List[MoverItem] = Field(
        default_factory=list, description="Top losing equities in the session"
    )
    market_timestamp: Optional[str] = Field(
        default=None, description="Timestamp corresponding to market snapshot"
    )
    data_sources: List[str] = Field(
        default_factory=list, description="Data sources or market feeds"
    )
