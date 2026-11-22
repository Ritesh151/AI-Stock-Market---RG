"""
Standard Response Envelope and Error Envelopes for RG AI Strict JSON Engine.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.core.validation_config import DEFAULT_SCHEMA_VERSION, STANDARD_FINANCIAL_DISCLAIMER


class SupportedResponseType(str, Enum):
    """The 7 officially supported analysis response types."""

    STOCK_ANALYSIS = "stock_analysis"
    TECHNICAL_ANALYSIS = "technical_analysis"
    FUNDAMENTAL_ANALYSIS = "fundamental_analysis"
    PORTFOLIO_ANALYSIS = "portfolio_analysis"
    STOCK_COMPARISON = "stock_comparison"
    MARKED_OVERVIEW = "market_overview"
    EDUCATIONAL_CONTENT = "educational_content"


class ResponseEnvelope(BaseModel):
    """Common envelope encapsulating all validated RG AI analysis responses."""

    success: bool = Field(default=True, description="Indicates response validity")
    type: str = Field(..., description="Registered response type identifier")
    schema_version: str = Field(default=DEFAULT_SCHEMA_VERSION, description="Schema version identifier")
    request_id: str = Field(..., description="Server-generated unique request tracking ID")
    data: Dict[str, Any] = Field(..., description="Validated domain analysis data payload")
    warnings: Optional[List[str]] = Field(default=None, description="Non-fatal financial or data warnings")
    disclaimer: str = Field(
        default=STANDARD_FINANCIAL_DISCLAIMER,
        description="Standard financial research disclaimer",
    )


class ValidationErrorDetail(BaseModel):
    """Field-level schema or validation error detail."""

    field: Optional[str] = Field(default=None, description="Name of the invalid field")
    issue: str = Field(..., description="Description of the error or failed constraint")


class ValidationErrorPayload(BaseModel):
    """Error payload nested inside validation error envelopes."""

    code: str = Field(..., description="Validation error code (e.g. INVALID_JSON, SCHEMA_VALIDATION_FAILED)")
    message: str = Field(..., description="Safe human-readable error summary")
    details: Optional[List[ValidationErrorDetail]] = Field(
        default=None, description="Detailed field-level validation errors"
    )


class ValidationErrorEnvelope(BaseModel):
    """Standard error envelope returned when response parsing or validation fails."""

    success: bool = Field(default=False, description="Always false for validation errors")
    type: str = Field(default="validation_error", description="Indicates validation failure")
    request_id: Optional[str] = Field(default=None, description="Request ID if known")
    error: ValidationErrorPayload = Field(..., description="Structured error payload")
