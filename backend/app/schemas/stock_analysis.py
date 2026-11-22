"""
Stock Analysis Pydantic Schema.
Primary strict model for individual Indian equity intelligence reports.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from app.core.validation_config import (
    MAX_PERCENT_CHANGE,
    MAX_REASONING_ITEMS,
    MIN_PERCENT_CHANGE,
    SUPPORTED_CURRENCIES,
    SUPPORTED_EXCHANGES,
)
from app.schemas.fundamental_analysis import FundamentalAnalysisSchema
from app.schemas.technical_analysis import TechnicalAnalysisSchema


class ExchangeEnum(str, Enum):
    NSE = "NSE"
    BSE = "BSE"
    MCX = "MCX"


class CurrencyEnum(str, Enum):
    INR = "INR"


class RecommendationEnum(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    ACCUMULATE = "ACCUMULATE"
    REDUCE = "REDUCE"
    NEUTRAL = "NEUTRAL"
    AVOID = "AVOID"
    STRONG_BUY = "STRONG_BUY"
    STRONG_SELL = "STRONG_SELL"


class RiskLevelEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class MarketTrendEnum(str, Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"
    SIDEWAYS = "sideways"
    VOLATILE = "volatile"


class EntryZone(BaseModel):
    """Entry price boundary range."""

    min: Optional[float] = Field(default=None, description="Minimum recommended entry price")
    max: Optional[float] = Field(default=None, description="Maximum recommended entry price")

    @model_validator(mode="after")
    def validate_entry_zone_relationship(self) -> "EntryZone":
        if self.min is not None and self.min <= 0:
            raise ValueError("Entry zone minimum must be strictly positive.")
        if self.max is not None and self.max <= 0:
            raise ValueError("Entry zone maximum must be strictly positive.")
        if self.min is not None and self.max is not None and self.min > self.max:
            raise ValueError(
                f"Entry zone minimum ({self.min}) cannot exceed maximum ({self.max})."
            )
        return self


class StockAnalysisSchema(BaseModel):
    """Authoritative schema for complete single-stock intelligence analysis."""

    stock_name: str = Field(..., min_length=1, max_length=100, description="Company or asset legal name")
    symbol: str = Field(..., min_length=1, max_length=20, description="Official trading symbol/ticker")
    exchange: ExchangeEnum = Field(default=ExchangeEnum.NSE, description="Trading exchange")
    currency: CurrencyEnum = Field(default=CurrencyEnum.INR, description="Denominated currency")
    current_price: Optional[float] = Field(default=None, description="Last Traded Price (LTP)")
    price_change: Optional[float] = Field(default=None, description="Absolute price change in session")
    price_change_percent: Optional[float] = Field(
        default=None, description="Percentage change in price"
    )
    market_trend: MarketTrendEnum = Field(
        default=MarketTrendEnum.NEUTRAL, description="Prevailing market trend"
    )
    recommendation: RecommendationEnum = Field(
        default=RecommendationEnum.HOLD,
        description="Analytical recommendation stance (not a trade instruction)",
    )
    entry_zone: EntryZone = Field(
        default_factory=EntryZone, description="Recommended entry price bracket"
    )
    target_price: Optional[float] = Field(
        default=None, description="Analytical upside price target"
    )
    stop_loss: Optional[float] = Field(
        default=None, description="Analytical downside risk stop loss"
    )
    risk_level: RiskLevelEnum = Field(
        default=RiskLevelEnum.MEDIUM, description="Assessed volatility and balance sheet risk level"
    )
    time_horizon: str = Field(
        default="1-3 months", description="Target investment or swing trade duration"
    )
    reasoning: List[str] = Field(
        default_factory=list, description="List of qualitative analytical rationale statements"
    )
    technical_analysis: Optional[Dict[str, Any]] = Field(
        default=None, description="Nested technical indicator metrics"
    )
    fundamental_analysis: Optional[Dict[str, Any]] = Field(
        default=None, description="Nested fundamental valuation metrics"
    )
    data_timestamp: Optional[str] = Field(
        default=None, description="ISO-8601 timestamp of analysis or underlying market quotes"
    )
    data_source: Optional[str] = Field(
        default=None, description="Source of underlying financial quotes or fundamentals"
    )

    @field_validator("recommendation", mode="before")
    @classmethod
    def normalize_recommendation(cls, v: Any) -> Any:
        if isinstance(v, str):
            v_upper = v.strip().upper().replace(" ", "_")
            if v_upper in RecommendationEnum.__members__:
                return RecommendationEnum[v_upper]
        return v

    @field_validator("exchange", mode="before")
    @classmethod
    def normalize_exchange(cls, v: Any) -> Any:
        if isinstance(v, str):
            v_upper = v.strip().upper()
            if v_upper in ExchangeEnum.__members__:
                return ExchangeEnum[v_upper]
        return v

    @field_validator("currency", mode="before")
    @classmethod
    def normalize_currency(cls, v: Any) -> Any:
        if isinstance(v, str):
            v_upper = v.strip().upper()
            if v_upper in CurrencyEnum.__members__:
                return CurrencyEnum[v_upper]
        return v

    @field_validator("market_trend", mode="before")
    @classmethod
    def normalize_market_trend(cls, v: Any) -> Any:
        if isinstance(v, str):
            v_lower = v.strip().lower()
            if v_lower in MarketTrendEnum._value2member_map_:
                return MarketTrendEnum(v_lower)
        return v

    @field_validator("risk_level", mode="before")
    @classmethod
    def normalize_risk_level(cls, v: Any) -> Any:
        if isinstance(v, str):
            v_lower = v.strip().lower().replace(" ", "_")
            if v_lower in RiskLevelEnum._value2member_map_:
                return RiskLevelEnum(v_lower)
        return v

    @field_validator("current_price", "target_price", "stop_loss", mode="before")
    @classmethod
    def clean_numeric_prices(cls, v: Any) -> Any:
        if isinstance(v, str):
            cleaned = v.replace("₹", "").replace("Rs.", "").replace("Rs", "").replace(",", "").strip()
            try:
                return float(cleaned)
            except ValueError:
                return v
        return v

    @field_validator("stock_name", "symbol")
    @classmethod
    def validate_non_empty_strings(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Field cannot be empty or whitespace-only.")
        return trimmed

    @field_validator("current_price", "target_price", "stop_loss")
    @classmethod
    def validate_positive_prices(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError("Price values must be strictly positive.")
        return v

    @field_validator("price_change_percent")
    @classmethod
    def validate_percent_bounds(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and (v < MIN_PERCENT_CHANGE or v > MAX_PERCENT_CHANGE):
            raise ValueError(
                f"Percentage change must be between {MIN_PERCENT_CHANGE}% and {MAX_PERCENT_CHANGE}%."
            )
        return v

    @field_validator("reasoning")
    @classmethod
    def validate_reasoning_length(cls, v: List[str]) -> List[str]:
        if len(v) > MAX_REASONING_ITEMS:
            raise ValueError(f"Reasoning statements cannot exceed {MAX_REASONING_ITEMS} items.")
        return [item.strip() for item in v if item.strip()]
