"""
Fundamental Analysis Pydantic Schema.
Strict validation of corporate financials, earnings ratios, and balance sheet metrics.
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator


class FundamentalAnalysisSchema(BaseModel):
    """Schema for fundamental valuation metrics."""

    revenue: Optional[float] = Field(default=None, description="Total reported revenue in INR Cr")
    net_profit: Optional[float] = Field(default=None, description="Net profit / PAT in INR Cr")
    eps: Optional[float] = Field(default=None, description="Earnings Per Share (INR)")
    pe_ratio: Optional[float] = Field(default=None, description="Price-to-Earnings valuation multiple")
    pb_ratio: Optional[float] = Field(default=None, description="Price-to-Book valuation multiple")
    debt: Optional[float] = Field(default=None, description="Total debt in INR Cr")
    roe: Optional[float] = Field(default=None, description="Return on Equity percentage")
    roce: Optional[float] = Field(default=None, description="Return on Capital Employed percentage")
    market_capitalization: Optional[float] = Field(
        default=None, description="Market Capitalization in INR Cr"
    )
    financial_reporting_period: Optional[str] = Field(
        default=None, description="Reporting quarter or financial year (e.g. Q3 FY25, FY24)"
    )
    data_source: Optional[str] = Field(
        default=None, description="Financial data source or filing reference"
    )

    @field_validator("market_capitalization", "debt")
    @classmethod
    def validate_non_negative_balance(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError("Balance sheet capital figures cannot be negative.")
        return v
