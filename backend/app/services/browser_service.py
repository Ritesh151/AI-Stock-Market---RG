"""
Browser Domain Service.
Orchestrates browser automation workflows, login verification, and health checks.
"""

from app.core.logging import get_logger
from app.integrations.browser.browser_manager import BrowserManager, get_browser_manager
from app.integrations.browser.browser_models import (
    BrowserActionResponse,
    BrowserStatusResponse,
)
from app.integrations.browser.browser_status import LoginState

logger = get_logger("browser_service")


class BrowserService:
    def __init__(self, manager: BrowserManager):
        self.manager = manager

    async def get_status(self) -> BrowserStatusResponse:
        """Retrieves verified browser status."""
        return await self.manager.get_status()

    async def start_session(self) -> BrowserActionResponse:
        """Starts persistent browser context."""
        status = await self.manager.start_browser()
        return BrowserActionResponse(
            success=status.is_running,
            message="Persistent Chrome browser session launched successfully.",
            state=status.state,
            login_status=status.login_status,
        )

    async def open_target_gpt(self) -> BrowserActionResponse:
        """Navigates to the centralized Custom GPT URL."""
        status = await self.manager.open_target_gpt()
        return BrowserActionResponse(
            success=True,
            message=f"Target Custom GPT opened successfully: {status.target_url}",
            state=status.state,
            login_status=status.login_status,
        )

    async def confirm_manual_login(self) -> BrowserActionResponse:
        """
        Independently verifies authentication state on the active page.
        """
        login_state = await self.manager.verify_login_state()
        status = await self.manager.get_status()

        if login_state == LoginState.AUTHENTICATED:
            message = "ChatGPT login confirmed and authenticated successfully. Profile is persisted."
            success = True
        elif login_state == LoginState.CHALLENGE_DETECTED:
            message = "Security verification or challenge detected. Please solve it in the browser."
            success = False
        else:
            message = "Authentication not detected. Please complete login in the opened Chrome window."
            success = False

        return BrowserActionResponse(
            success=success,
            message=message,
            state=status.state,
            login_status=login_state,
        )

    async def stop_session(self) -> BrowserActionResponse:
        """Stops the managed browser session."""
        status = await self.manager.stop_browser()
        return BrowserActionResponse(
            success=True,
            message="Browser session terminated cleanly and lock released.",
            state=status.state,
            login_status=status.login_status,
        )

    async def reconnect_session(self) -> BrowserActionResponse:
        """Reconnects or recovers browser after disconnection."""
        status = await self.manager.reconnect_browser()
        return BrowserActionResponse(
            success=status.is_running,
            message="Browser session reconnected successfully.",
            state=status.state,
            login_status=status.login_status,
        )


def get_browser_service() -> BrowserService:
    """Dependency provider returning BrowserService with singleton manager."""
    return BrowserService(manager=get_browser_manager())
