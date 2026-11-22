"""
Browser Integration Exception Hierarchy.
Provides domain-level exceptions for browser lifecycle and session management.
"""

from typing import Any, Dict, List, Optional
from app.core.exceptions import AppException


class BrowserException(AppException):
    """Base exception for all browser automation errors."""

    def __init__(
        self,
        message: str = "Browser operation error occurred.",
        code: str = "BROWSER_ERROR",
        status_code: int = 500,
        details: Optional[List[Dict[str, Any]]] = None,
    ):
        super().__init__(message=message, code=code, status_code=status_code, details=details)


class ChromeNotFoundError(BrowserException):
    def __init__(self, message: str = "Chrome or compatible Chromium executable not found."):
        super().__init__(message=message, code="CHROME_NOT_FOUND", status_code=500)


class ProfileLockedError(BrowserException):
    def __init__(
        self,
        message: str = "Persistent browser profile is currently locked by another active process.",
    ):
        super().__init__(message=message, code="PROFILE_ALREADY_IN_USE", status_code=409)


class BrowserLaunchError(BrowserException):
    def __init__(self, message: str = "Failed to launch persistent Chrome browser context."):
        super().__init__(message=message, code="BROWSER_LAUNCH_FAILED", status_code=500)


class BrowserNotRunningError(BrowserException):
    def __init__(self, message: str = "Browser instance is not currently active."):
        super().__init__(message=message, code="BROWSER_NOT_RUNNING", status_code=400)


class NavigationTimeoutError(BrowserException):
    def __init__(self, message: str = "Navigation to target URL timed out."):
        super().__init__(message=message, code="NAVIGATION_TIMEOUT", status_code=504)


class AuthenticationRequiredError(BrowserException):
    def __init__(
        self,
        message: str = "Manual authentication required. Please complete login in the opened browser.",
    ):
        super().__init__(message=message, code="AUTHENTICATION_REQUIRED", status_code=401)


class InvalidBrowserStateError(BrowserException):
    def __init__(self, message: str = "Browser is in an invalid state for the requested operation."):
        super().__init__(message=message, code="INVALID_BROWSER_STATE", status_code=400)


class ProfilePermissionError(BrowserException):
    def __init__(self, message: str = "Permission denied accessing persistent profile directory."):
        super().__init__(message=message, code="PROFILE_PERMISSION_ERROR", status_code=500)
