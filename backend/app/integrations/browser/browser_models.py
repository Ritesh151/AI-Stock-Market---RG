"""
Pydantic Models for Browser State and Action Responses.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.integrations.browser.browser_status import BrowserState, LoginState


class BrowserStatusResponse(BaseModel):
    """
    Schema returned by GET /api/v1/browser/status.
    Never exposes internal filesystem paths, tokens, or cookies.
    """
    state: BrowserState = Field(..., description="Current operational state of browser")
    is_running: bool = Field(..., description="Whether browser process is running")
    target_url: str = Field(..., description="Centralized target Custom GPT URL")
    login_status: LoginState = Field(..., description="Evaluated ChatGPT authentication status")
    last_health_check: Optional[datetime] = Field(
        default=None, description="Timestamp of most recent health check"
    )
    error_message: Optional[str] = Field(
        default=None, description="Safe user-facing error details if state is ERROR"
    )
    active_pages_count: int = Field(default=0, description="Number of currently open tabs")
    is_locked: bool = Field(default=False, description="Whether profile file-lock is held")


class BrowserActionResponse(BaseModel):
    """
    Standard schema returned by action endpoints (start, stop, open-gpt, confirm-login, reconnect).
    """
    success: bool = Field(..., description="Indicates whether the requested action succeeded")
    message: str = Field(..., description="Action outcome description")
    state: BrowserState = Field(..., description="Resulting browser operational state")
    login_status: LoginState = Field(..., description="Resulting login status")
