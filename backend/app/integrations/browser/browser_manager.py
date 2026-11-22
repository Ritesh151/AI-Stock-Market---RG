"""
Centralized Browser Lifecycle & Persistent Session Manager.
Implements thread-safe and process-locked Playwright browser automation for RG AI.
"""

import asyncio
import fcntl
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from playwright.async_api import (
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
    Error as PlaywrightError,
)

from app.core.logging import get_logger
from app.integrations.browser.browser_config import BrowserConfig, get_browser_config
from app.integrations.browser.browser_exceptions import (
    BrowserException,
    BrowserLaunchError,
    BrowserNotRunningError,
    InvalidBrowserStateError,
    NavigationTimeoutError,
    ProfileLockedError,
)
from app.integrations.browser.browser_models import BrowserStatusResponse
from app.integrations.browser.browser_status import BrowserState, LoginState

logger = get_logger("browser_manager")


class ProfileProcessLock:
    """
    POSIX advisory file lock (fcntl.flock) ensuring only one backend
    process controls the persistent Chrome profile directory at any time.
    """

    def __init__(self, lock_path: Path):
        self.lock_path = lock_path
        self._fd: Optional[int] = None

    def acquire(self) -> bool:
        """
        Attempts non-blocking acquisition of exclusive file lock.
        Returns True if acquired, False if already held by another process.
        """
        try:
            self.lock_path.parent.mkdir(parents=True, exist_ok=True)
            self._fd = os.open(str(self.lock_path), os.O_CREAT | os.O_RDWR, 0o600)
            fcntl.flock(self._fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except (BlockingIOError, OSError) as exc:
            logger.warning(f"Profile lock held by another process: {exc}")
            if self._fd is not None:
                try:
                    os.close(self._fd)
                except OSError:
                    pass
                self._fd = None
            return False

    def release(self) -> None:
        """Releases the held lock and closes the file descriptor."""
        if self._fd is not None:
            try:
                fcntl.flock(self._fd, fcntl.LOCK_UN)
                os.close(self._fd)
            except OSError as exc:
                logger.debug(f"Error releasing lock descriptor: {exc}")
            finally:
                self._fd = None


class BrowserManager:
    """
    Singleton Manager governing Chrome lifecycle, persistent profile,
    and ChatGPT manual login verification.
    """

    _instance: Optional["BrowserManager"] = None

    def __init__(self, config: Optional[BrowserConfig] = None):
        self.config = config or get_browser_config()
        self._playwright: Optional[Playwright] = None
        self._context: Optional[BrowserContext] = None
        self._active_page: Optional[Page] = None

        self._state: BrowserState = BrowserState.STOPPED
        self._login_state: LoginState = LoginState.UNKNOWN
        self._last_health_check: Optional[datetime] = None
        self._error_message: Optional[str] = None

        self._lock = asyncio.Lock()
        self._process_lock = ProfileProcessLock(self.config.lock_file_path)

    @classmethod
    def get_instance(cls, config: Optional[BrowserConfig] = None) -> "BrowserManager":
        """Returns or creates the singleton BrowserManager instance."""
        if cls._instance is None:
            cls._instance = cls(config=config)
        return cls._instance

    @property
    def is_running(self) -> bool:
        """Indicates if the browser context is active and not stopped."""
        return (
            self._context is not None
            and self._state not in (BrowserState.STOPPED, BrowserState.ERROR, BrowserState.DISCONNECTED)
        )

    async def get_status(self) -> BrowserStatusResponse:
        """
        Returns full status response without exposing raw paths or credentials.
        """
        async with self._lock:
            # Perform inline health verification if running
            if self.is_running:
                try:
                    pages = self._context.pages if self._context else []
                    pages_count = len(pages)
                    self._last_health_check = datetime.now(timezone.utc)
                except Exception:
                    self._state = BrowserState.DISCONNECTED
                    pages_count = 0
            else:
                pages_count = 0

            return BrowserStatusResponse(
                state=self._state,
                is_running=self.is_running,
                target_url=self.config.target_url,
                login_status=self._login_state,
                last_health_check=self._last_health_check,
                error_message=self._error_message,
                active_pages_count=pages_count,
                is_locked=self._process_lock._fd is not None,
            )

    async def start_browser(self) -> BrowserStatusResponse:
        """
        Launches the persistent Chrome browser session.
        Acquires process lock to prevent concurrent corruption of the user-data directory.
        """
        async with self._lock:
            if self.is_running:
                logger.info("start_browser called but browser is already running.")
                return await self._build_status_response_unlocked()

            self._state = BrowserState.STARTING
            self._error_message = None

            # 1. Acquire process-level lock
            if not self._process_lock.acquire():
                self._state = BrowserState.ERROR
                self._error_message = "Browser profile is in use by another process."
                raise ProfileLockedError(self._error_message)

            try:
                # 2. Initialize Playwright
                self._playwright = await async_playwright().start()

                # 3. Launch Persistent Context with timeout
                launch_kwargs = {
                    "user_data_dir": str(self.config.user_data_dir),
                    "headless": self.config.headless,
                    "args": self.config.args,
                    "ignore_default_args": ["--enable-automation"],
                    "viewport": {
                        "width": self.config.viewport_width,
                        "height": self.config.viewport_height,
                    },
                }

                if self.config.executable_path:
                    launch_kwargs["executable_path"] = self.config.executable_path

                logger.info(
                    f"Launching persistent Chrome context (executable: {self.config.executable_path or 'bundled Chromium'})"
                )

                self._context = await asyncio.wait_for(
                    self._playwright.chromium.launch_persistent_context(**launch_kwargs),
                    timeout=self.config.timeout_seconds,
                )

                # Attach context disconnection listener
                self._context.on("close", self._on_context_closed)

                # Get or create initial page
                if self._context.pages:
                    self._active_page = self._context.pages[0]
                else:
                    self._active_page = await self._context.new_page()

                self._state = BrowserState.RUNNING
                self._last_health_check = datetime.now(timezone.utc)
                logger.info("Persistent Chrome browser started successfully.")

                return await self._build_status_response_unlocked()

            except asyncio.TimeoutError:
                await self._cleanup_unlocked()
                self._state = BrowserState.ERROR
                self._error_message = f"Browser launch timed out after {self.config.timeout_seconds}s."
                raise BrowserLaunchError(self._error_message)

            except Exception as exc:
                await self._cleanup_unlocked()
                self._state = BrowserState.ERROR
                self._error_message = f"Failed to start browser: {str(exc)}"
                logger.exception("Error launching browser context:")
                raise BrowserLaunchError(self._error_message)

    async def open_target_gpt(self) -> BrowserStatusResponse:
        """
        Navigates the managed browser to the fixed target Custom GPT URL.
        """
        async with self._lock:
            if not self.is_running or not self._active_page:
                raise BrowserNotRunningError("Cannot open target GPT: browser is not running.")

            try:
                logger.info(f"Navigating to target Custom GPT: {self.config.target_url}")
                await self._active_page.goto(
                    self.config.target_url,
                    wait_until="commit",
                    timeout=60000,
                )

                self._state = BrowserState.TARGET_OPEN
                self._last_health_check = datetime.now(timezone.utc)

                # Wait briefly for initial DOM hydration then evaluate login
                await asyncio.sleep(2)
                await self._evaluate_login_unlocked()

                return await self._build_status_response_unlocked()

            except PlaywrightError as exc:
                logger.error(f"Navigation error: {exc}")
                raise NavigationTimeoutError(f"Navigation to Custom GPT timed out or failed.")

    async def verify_login_state(self) -> LoginState:
        """
        Independently verifies whether the active browser page is authenticated.
        Inspects page DOM for logged-in indicators vs authentication challenges.
        Never falsely claims authentication just because a URL loaded.
        """
        async with self._lock:
            if not self.is_running or not self._active_page:
                self._login_state = LoginState.UNKNOWN
                return self._login_state

            return await self._evaluate_login_unlocked()

    async def _evaluate_login_unlocked(self) -> LoginState:
        """
        Inspects the active page DOM to classify login state.
        Private method: must be called within `self._lock`.
        """
        if not self._active_page:
            return LoginState.UNKNOWN

        try:
            url = self._active_page.url.lower()

            # 1. Check if redirected to login/auth domain
            if "auth0" in url or "login" in url or "accounts.google" in url:
                self._login_state = LoginState.LOGIN_REQUIRED
                self._state = BrowserState.LOGIN_REQUIRED
                return self._login_state

            # 2. Inspect DOM for unauthenticated triggers (e.g. "Log in", "Sign up" buttons)
            login_buttons = await self._active_page.locator(
                'button:has-text("Log in"), a:has-text("Log in"), button[data-testid="login-button"]'
            ).count()

            if login_buttons > 0:
                self._login_state = LoginState.LOGIN_REQUIRED
                self._state = BrowserState.LOGIN_REQUIRED
                logger.info("Unauthenticated state detected on ChatGPT page.")
                return self._login_state

            # 3. Check for security challenge (Cloudflare / Turnstile)
            challenge_elements = await self._active_page.locator(
                '#challenge-running, #cf-challenge, iframe[src*="cloudflare"]'
            ).count()
            if challenge_elements > 0:
                self._login_state = LoginState.CHALLENGE_DETECTED
                logger.warning("Cloudflare challenge detected on page.")
                return self._login_state

            # 4. Check for active prompt composer (modern contenteditable, ProseMirror, or textarea)
            composer = await self._active_page.locator(
                '#prompt-textarea, [data-placeholder], [contenteditable="true"], textarea[placeholder*="message"], .ProseMirror'
            ).count()

            if composer > 0:
                self._login_state = LoginState.AUTHENTICATED
                self._state = BrowserState.AUTHENTICATED
                logger.info("Authenticated ChatGPT session verified successfully.")
                return self._login_state

            # If on chatgpt.com domain and no login button is present, mark as login required until composer is visible
            if "chatgpt.com" in url:
                self._login_state = LoginState.LOGIN_REQUIRED
                return self._login_state

            self._login_state = LoginState.UNKNOWN
            return self._login_state

        except Exception as exc:
            logger.debug(f"Error during login evaluation: {exc}")
            return self._login_state

    async def stop_browser(self) -> BrowserStatusResponse:
        """
        Gracefully terminates the persistent browser and releases the profile lock.
        """
        async with self._lock:
            self._state = BrowserState.STOPPING
            logger.info("Stopping persistent browser session...")
            await self._cleanup_unlocked()
            self._state = BrowserState.STOPPED
            self._active_page = None
            self._login_state = LoginState.UNKNOWN
            self._last_health_check = datetime.now(timezone.utc)
            logger.info("Browser stopped and profile lock released.")

            return await self._build_status_response_unlocked()

    async def check_browser_health(self) -> BrowserStatusResponse:
        """
        Probes browser responsiveness and updates health check timestamp.
        """
        async with self._lock:
            if not self.is_running or not self._active_page:
                return await self._build_status_response_unlocked()

            try:
                # Simple ping: retrieve active page title
                _ = await self._active_page.title()
                self._last_health_check = datetime.now(timezone.utc)
            except Exception as exc:
                logger.warning(f"Browser health probe failed: {exc}")
                self._state = BrowserState.DISCONNECTED
                self._error_message = "Browser connection lost."

            return await self._build_status_response_unlocked()

    async def reconnect_browser(self) -> BrowserStatusResponse:
        """
        Attempts clean reconnection if browser crashed or disconnected.
        """
        async with self._lock:
            logger.info("Reconnecting browser...")
            await self._cleanup_unlocked()

        # Restart via start_browser
        return await self.start_browser()

    async def shutdown(self) -> None:
        """Clean shutdown hook for FastAPI lifespan."""
        logger.info("FastAPI shutdown: terminating managed browser...")
        try:
            await self.stop_browser()
        except Exception as exc:
            logger.debug(f"Error during shutdown: {exc}")

    def _on_context_closed(self) -> None:
        """Event callback invoked when the user manually closes the Chrome window."""
        logger.info("Browser context closed by user or external event.")
        self._state = BrowserState.DISCONNECTED
        self._active_page = None
        self._process_lock.release()

    async def _cleanup_unlocked(self) -> None:
        """Internal cleanup releasing Playwright and file lock."""
        try:
            if self._context:
                await self._context.close()
        except Exception:
            pass
        finally:
            self._context = None

        try:
            if self._playwright:
                await self._playwright.stop()
        except Exception:
            pass
        finally:
            self._playwright = None

        self._process_lock.release()

    async def _build_status_response_unlocked(self) -> BrowserStatusResponse:
        """Internal helper to construct status model."""
        pages_count = 0
        if self._context:
            try:
                pages_count = len(self._context.pages)
            except Exception:
                pass

        return BrowserStatusResponse(
            state=self._state,
            is_running=self.is_running,
            target_url=self.config.target_url,
            login_status=self._login_state,
            last_health_check=self._last_health_check,
            error_message=self._error_message,
            active_pages_count=pages_count,
            is_locked=self._process_lock._fd is not None,
        )


def get_browser_manager() -> BrowserManager:
    """Dependency provider returning the singleton BrowserManager."""
    return BrowserManager.get_instance()
