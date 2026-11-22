"""
Browser Integration Package for Playwright Persistent Session Management.
"""

from app.integrations.browser.browser_config import BrowserConfig, get_browser_config
from app.integrations.browser.browser_exceptions import (
    BrowserException,
    BrowserLaunchError,
    BrowserNotRunningError,
    ChromeNotFoundError,
    NavigationTimeoutError,
    ProfileLockedError,
)
from app.integrations.browser.browser_manager import BrowserManager, get_browser_manager
from app.integrations.browser.browser_models import (
    BrowserActionResponse,
    BrowserStatusResponse,
)
from app.integrations.browser.browser_status import BrowserState, LoginState

__all__ = [
    "BrowserConfig",
    "get_browser_config",
    "BrowserException",
    "BrowserLaunchError",
    "BrowserNotRunningError",
    "ChromeNotFoundError",
    "NavigationTimeoutError",
    "ProfileLockedError",
    "BrowserManager",
    "get_browser_manager",
    "BrowserActionResponse",
    "BrowserStatusResponse",
    "BrowserState",
    "LoginState",
]
