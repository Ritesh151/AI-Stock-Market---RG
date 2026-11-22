"""
Technical Analysis Pydantic Schema.
Strict validation of momentum, moving averages, support/resistance, and indicators.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from app.core.validation_config import MAX_RSI_VALUE, MIN_RSI_VALUE


class TrendDirectionEnum(str, Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"
    REVERSAL = "reversal"
    SIDEWAYS = "sideways"


class MacdData(BaseModel):
    macd_line: Optional[float] = None
    signal_line: Optional[float] = None
    histogram: Optional[float] = None


class MovingAverages(BaseModel):
    ema_20: Optional[float] = None
    ema_50: Optional[float] = None
    ema_200: Optional[float] = None
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None

    @field_validator("ema_20", "ema_50", "ema_200", "sma_20", "sma_50", "sma_200")
    @classmethod
    def validate_positive_ma(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError("Moving average price value must be strictly positive.")
        return v


class TechnicalAnalysisSchema(BaseModel):
    """Schema for technical indicator analysis."""

    rsi: Optional[float] = Field(default=None, description="Relative Strength Index (0-100)")
    macd: Optional[MacdData] = Field(default=None, description="MACD indicator data")
    moving_averages: Optional[MovingAverages] = Field(
        default=None, description="Key Exponential & Simple Moving Averages"
    )
    support_levels: Optional[List[float]] = Field(
        default=None, description="Key technical support price levels"
    )
    resistance_levels: Optional[List[float]] = Field(
        default=None, description="Key technical resistance price levels"
    )
    trend_direction: Optional[TrendDirectionEnum] = Field(
        default=None, description="Overall evaluated technical trend"
    )
    candlestick_patterns: Optional[List[str]] = Field(
        default=None, description="Detected Japanese candlestick patterns"
    )
    indicator_timestamps: Optional[str] = Field(
        default=None, description="Timestamp corresponding to indicator calculations"
    )
    data_source: Optional[str] = Field(
        default=None, description="Data vendor or feed source (e.g. NSE, TradingView)"
    )

    @field_validator("rsi")
    @classmethod
    def validate_rsi_bounds(cls, v: Optional[float]) -> Optional[float]:
        if v is not None:
            if v < MIN_RSI_VALUE or v > MAX_RSI_VALUE:
                raise ValueError(f"RSI must be between {MIN_RSI_VALUE} and {MAX_RSI_VALUE}.")
        return v

    @field_validator("support_levels", "resistance_levels")
    @classmethod
    def validate_price_levels(cls, v: Optional[List[float]]) -> Optional[List[float]]:
        if v is not None:
            for val in v:
                if val <= 0:
                    raise ValueError(f"Technical price level {val} must be strictly positive.")
        return v
