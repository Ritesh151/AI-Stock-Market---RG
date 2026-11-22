"""
Portfolio Analysis Pydantic Schema.
Strict validation of holdings, sector exposures, asset allocations, and concentration risk.
"""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class ConcentrationRiskEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class HoldingItem(BaseModel):
    symbol: str = Field(..., description="Stock or asset ticker symbol")
    allocation_percent: Optional[float] = Field(
        default=None, description="Percentage allocation in the portfolio"
    )
    current_value: Optional[float] = Field(
        default=None, description="Current value of holding in INR"
    )
    sector: Optional[str] = Field(default=None, description="Industry sector")

    @field_validator("allocation_percent")
    @classmethod
    def validate_allocation_bounds(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and (v < 0 or v > 100):
            raise ValueError("Holding allocation percentage must be between 0 and 100.")
        return v


class PortfolioAnalysisSchema(BaseModel):
    """Schema for portfolio asset allocation and risk assessment."""

    portfolio_value: Optional[float] = Field(
        default=None, description="Total assessed portfolio valuation in INR"
    )
    holdings: List[HoldingItem] = Field(
        default_factory=list, description="List of individual portfolio assets"
    )
    asset_allocation: Optional[Dict[str, float]] = Field(
        default=None, description="Asset class allocation map (e.g. Equity, Debt, Cash)"
    )
    concentration_risk: Optional[ConcentrationRiskEnum] = Field(
        default=None, description="Evaluated portfolio concentration risk tier"
    )
    sector_exposure: Optional[Dict[str, float]] = Field(
        default=None, description="Sector breakdown percentages"
    )
    risk_assessment: Optional[str] = Field(
        default=None, description="Overall risk narrative"
    )
    diversification_observations: List[str] = Field(
        default_factory=list, description="Observations regarding portfolio diversification"
    )

    @field_validator("portfolio_value")
    @classmethod
    def validate_positive_portfolio(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError("Portfolio value cannot be negative.")
        return v
