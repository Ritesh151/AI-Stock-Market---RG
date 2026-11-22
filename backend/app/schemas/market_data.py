"""
Market Data Pydantic Schemas.
Defines normalized contracts for quotes, historical candles, searches, company profiles, and watchlists.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from app.integrations.market_data.provider_config import DataFreshness


class StockQuoteData(BaseModel):
    """Normalized stock quote payload strictly adhering to Section 6 specifications."""

    symbol: str = Field(..., description="Stock trading symbol")
    company_name: str = Field(..., description="Company or asset legal name")
    exchange: str = Field(default="NSE", description="Trading exchange (NSE or BSE)")
    currency: str = Field(default="INR", description="Denominated currency")
    last_price: Optional[float] = Field(default=None, description="Last traded price")
    previous_close: Optional[float] = Field(default=None, description="Previous session closing price")
    change: Optional[float] = Field(default=None, description="Absolute price change")
    change_percent: Optional[float] = Field(default=None, description="Percentage price change")
    open: Optional[float] = Field(default=None, description="Day opening price")
    day_high: Optional[float] = Field(default=None, description="Session peak price")
    day_low: Optional[float] = Field(default=None, description="Session trough price")
    volume: Optional[int] = Field(default=None, description="Trading volume in shares")
    market_cap: Optional[float] = Field(default=None, description="Total market capitalization in INR")
    data_status: str = Field(
        default=DataFreshness.UNKNOWN.value,
        description="Data freshness classification (REAL_TIME, DELAYED, END_OF_DAY, etc.)",
    )
    source_name: Optional[str] = Field(default=None, description="Source provider attribution")
    market_timestamp: Optional[str] = Field(default=None, description="Provider market data timestamp")
    fetched_at: Optional[str] = Field(default=None, description="ISO-8601 UTC timestamp of fetch")


class StockQuoteResponse(BaseModel):
    """Enveloped stock quote response."""

    success: bool = True
    data: StockQuoteData


class HistoricalCandle(BaseModel):
    """Single normalized OHLCV price candle."""

    timestamp: str = Field(..., description="Candle start ISO timestamp")
    open: float = Field(..., description="Period opening price")
    high: float = Field(..., description="Period highest price")
    low: float = Field(..., description="Period lowest price")
    close: float = Field(..., description="Period closing price")
    volume: int = Field(default=0, description="Volume traded during candle interval")


class HistoricalDataResponse(BaseModel):
    """Normalized historical chart response."""

    success: bool = True
    symbol: str
    exchange: str = "NSE"
    currency: str = "INR"
    range: str
    interval: str
    data_status: str
    source_name: Optional[str] = None
    fetched_at: str
    candles: List[HistoricalCandle]


class StockSearchResult(BaseModel):
    """Single stock search hit."""

    symbol: str
    company_name: str
    exchange: str
    currency: str = "INR"
    type: str = "EQUITY"


class StockSearchResponse(BaseModel):
    """Enveloped search response."""

    success: bool = True
    query: str
    results: List[StockSearchResult]
    total: int


class CompanyProfileData(BaseModel):
    """Company fundamental business profile."""

    symbol: str
    company_name: str
    exchange: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    high_52w: Optional[float] = None
    low_52w: Optional[float] = None
    currency: str = "INR"
    data_status: str
    source_name: Optional[str] = None
    fetched_at: str


class CompanyProfileResponse(BaseModel):
    """Enveloped company profile response."""

    success: bool = True
    data: CompanyProfileData


class MarketStatusResponse(BaseModel):
    """Market trading session status response."""

    success: bool = True
    exchange: str = "NSE"
    status: str
    current_time: str
    session: str
    market_timezone: str


class MarketIndexItem(BaseModel):
    """Single market index benchmark item."""

    symbol: str
    name: str
    value: Optional[float] = None
    change: Optional[float] = None
    percent_change: Optional[float] = None
    data_status: str
    timestamp: str


class MarketIndicesResponse(BaseModel):
    """Enveloped market benchmark indices response."""

    success: bool = True
    indices: List[MarketIndexItem]
    market_status: str
    timestamp: str


class WatchlistItem(BaseModel):
    """Single watchlist entry."""

    symbol: str
    company_name: str
    exchange: str = "NSE"
    last_price: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    data_status: str = DataFreshness.UNKNOWN.value
    added_at: str


class WatchlistResponse(BaseModel):
    """Enveloped watchlist response."""

    success: bool = True
    items: List[WatchlistItem]
    total: int
