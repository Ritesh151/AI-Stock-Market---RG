"""
RG AI Integration Exceptions.
Defines domain-specific exception taxonomy for browser and custom GPT integration workflows.
"""

from typing import Any, Dict, Optional
from app.core.exceptions import AppException


class IntegrationException(AppException):
    """Base exception for all RG AI integration and orchestration errors."""

    def __init__(
        self,
        message: str,
        code: str = "INTEGRATION_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message=message, code=code, status_code=status_code, details=details)


class UnsupportedIntegrationError(IntegrationException):
    """Raised when an operation cannot be fulfilled without unsupported scraping or unofficial APIs."""

    def __init__(
        self,
        message: str = "The configured browser integration does not support this operation without unsupported scraping.",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            message=message,
            code="UNSUPPORTED_INTEGRATION",
            status_code=501,
            details=details,
        )


class AuthenticationRequiredError(IntegrationException):
    """Raised when the target Custom GPT requires user authentication before executing prompts."""

    def __init__(
        self,
        message: str = "Authentication required. Please complete manual login in the managed Chrome browser.",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            message=message,
            code="LOGIN_REQUIRED",
            status_code=401,
            details=details,
        )


class BrowserUnavailableError(IntegrationException):
    """Raised when the persistent browser process is not running or unreachable."""

    def __init__(
        self,
        message: str = "Browser session is not running. Please start the managed browser first.",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            message=message,
            code="BROWSER_UNAVAILABLE",
            status_code=503,
            details=details,
        )


class RequestCancelledError(IntegrationException):
    """Raised when a queued or in-flight request is cancelled by user or operator."""

    def __init__(
        self,
        message: str = "The request was cancelled before completion.",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            message=message,
            code="REQUEST_CANCELLED",
            status_code=499,
            details=details,
        )


class RequestTimeoutError(IntegrationException):
    """Raised when request execution exceeds the configured timeout window."""

    def __init__(
        self,
        message: str = "Request execution timed out.",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            message=message,
            code="REQUEST_TIMEOUT",
            status_code=504,
            details=details,
        )


class QueueFullError(IntegrationException):
    """Raised when the bounded request queue capacity is exceeded."""

    def __init__(
        self,
        message: str = "Request queue is currently full. Please try again shortly.",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            message=message,
            code="QUEUE_FULL",
            status_code=503,
            details=details,
        )


class DuplicateRequestError(IntegrationException):
    """Raised when an identical prompt is already queued or actively processing."""

    def __init__(
        self,
        message: str = "A duplicate request is already in-flight. Please wait for it to finish.",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            message=message,
            code="DUPLICATE_REQUEST",
            status_code=409,
            details=details,
        )


class InvalidStateTransitionError(IntegrationException):
    """Raised when attempting an illegal request state transition."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            message=message,
            code="INVALID_STATE_TRANSITION",
            status_code=400,
            details=details,
        )
