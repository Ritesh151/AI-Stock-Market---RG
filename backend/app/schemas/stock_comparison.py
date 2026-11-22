"""
Stock Comparison Pydantic Schema.
Strict validation of comparative financial and technical analysis across multiple equities.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class StockComparisonSchema(BaseModel):
    """Schema comparing multiple stocks across price, technicals, and fundamentals."""

    stocks_compared: List[str] = Field(
        ..., min_length=2, description="List of stock symbols being compared (minimum 2)"
    )
    price_performance: Optional[Dict[str, Any]] = Field(
        default=None, description="Comparative price returns across periods"
    )
    fundamental_metrics: Optional[Dict[str, Any]] = Field(
        default=None, description="Comparative fundamental valuation metrics"
    )
    technical_metrics: Optional[Dict[str, Any]] = Field(
        default=None, description="Comparative technical indicators"
    )
    risk_comparison: Optional[Dict[str, Any]] = Field(
        default=None, description="Comparative risk profiles"
    )
    comparison_summary: Optional[str] = Field(
        default=None, description="Analytical summary highlighting relative advantages"
    )

    @field_validator("stocks_compared")
    @classmethod
    def validate_symbols(cls, v: List[str]) -> List[str]:
        if len(v) < 2:
            raise ValueError("Comparison requires at least 2 distinct stock symbols.")
        cleaned = [s.strip().upper() for s in v if s.strip()]
        if len(set(cleaned)) < 2:
            raise ValueError("Comparison symbols must be distinct.")
        return cleaned
