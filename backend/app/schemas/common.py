"""
Common API Schemas and Response Envelopes.
"""

from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    field: Optional[str] = Field(default=None, description="Request field with issue")
    issue: str = Field(..., description="Description of the validation issue")


class ErrorPayload(BaseModel):
    code: str = Field(..., description="System error code")
    message: str = Field(..., description="Human-readable explanation")
    details: Optional[List[ErrorDetail]] = Field(
        default=None, description="Detailed validation errors if any"
    )


class ApiResponse(BaseModel, Generic[T]):
    success: bool = Field(default=True, description="Indicates request success")
    data: Optional[T] = Field(default=None, description="Payload data")
    error: Optional[ErrorPayload] = Field(
        default=None, description="Error payload on failure"
    )
