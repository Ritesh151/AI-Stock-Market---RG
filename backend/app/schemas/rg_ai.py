"""
RG AI Orchestration Pydantic Schemas.
Defines schemas for chat requests, request states, availability, and response envelopes.
"""

from datetime import datetime, timezone
from enum import Enum
import re
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, field_validator
from app.integrations.rg_ai.gpt_config import (
    MAX_METADATA_KEYS,
    MAX_PROMPT_LENGTH,
    MIN_PROMPT_LENGTH,
)

_RESTRICTED_METADATA_PATTERN = re.compile(
    r"(file://|chrome://|about:|javascript:|data:|/etc/|/var/|/usr/|/root/|C:\\|[a-zA-Z]:\\)",
    re.IGNORECASE,
)


class RequestStatus(str, Enum):
    """The 11 formal states of the RG AI request lifecycle."""

    IDLE = "idle"
    QUEUED = "queued"
    INITIALIZING = "initializing"
    WAITING_FOR_LOGIN = "waiting_for_login"
    SUBMITTING = "submitting"
    PROCESSING = "processing"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    INTEGRATION_UNAVAILABLE = "integration_unavailable"


class ChatPromptRequest(BaseModel):
    """Validated incoming chat request from frontend or local client."""

    prompt: str = Field(
        ...,
        description="User analysis prompt. Cannot be empty or whitespace-only.",
        min_length=MIN_PROMPT_LENGTH,
        max_length=MAX_PROMPT_LENGTH,
    )
    conversation_id: Optional[str] = Field(
        default=None,
        description="Optional conversation thread ID for multi-turn sessions.",
        max_length=64,
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional contextual metadata. System paths and executable URLs are rejected.",
    )

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Prompt cannot be empty or whitespace-only.")
        if len(trimmed) < MIN_PROMPT_LENGTH:
            raise ValueError(f"Prompt must be at least {MIN_PROMPT_LENGTH} characters.")
        if len(value) > MAX_PROMPT_LENGTH:
            raise ValueError(f"Prompt cannot exceed {MAX_PROMPT_LENGTH} characters.")
        return trimmed

    @field_validator("metadata")
    @classmethod
    def sanitize_metadata(cls, value: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if value is None:
            return None
        if len(value) > MAX_METADATA_KEYS:
            raise ValueError(f"Metadata cannot contain more than {MAX_METADATA_KEYS} keys.")
        cleaned: Dict[str, Any] = {}
        for k, v in value.items():
            if not isinstance(k, str) or len(k) > 50:
                continue
            str_val = str(v)
            if _RESTRICTED_METADATA_PATTERN.search(str_val):
                raise ValueError(f"Metadata key '{k}' contains restricted path or URL patterns.")
            if len(str_val) > 500:
                raise ValueError(f"Metadata value for '{k}' exceeds maximum 500 characters.")
            cleaned[k] = v
        return cleaned


class ChatSubmissionResponse(BaseModel):
    """Immediate response confirming request queued."""

    success: bool = True
    request_id: str
    status: RequestStatus = RequestStatus.QUEUED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    queue_position: int = 1
    message: str = "Request queued for execution."


class RequestStatusResponse(BaseModel):
    """Comprehensive request lifecycle status envelope."""

    success: bool
    request_id: str
    status: RequestStatus
    created_at: str
    updated_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    queue_position: Optional[int] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


class CancelRequestResponse(BaseModel):
    """Response payload when cancelling an in-flight or queued request."""

    success: bool
    request_id: str
    status: RequestStatus
    message: str


class RGAvailabilityResponse(BaseModel):
    """Response reporting integration capability and browser readiness."""

    is_available: bool
    is_browser_running: bool
    login_state: str
    target_url: str
    adapter_type: str
    message: str


class RGHealthResponse(BaseModel):
    """Response reporting request manager worker health and queue load."""

    status: str
    queue_size: int
    max_queue_size: int
    active_worker: bool
    concurrency_limit: int
    total_processed: int
    total_failed: int
    total_cancelled: int
