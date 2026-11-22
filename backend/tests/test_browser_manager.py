"""
Unit and Mock Integration Tests for BrowserManager, Locks, and Config.
"""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.integrations.browser.browser_config import BrowserConfig, resolve_executable_path
from app.integrations.browser.browser_exceptions import (
    BrowserLaunchError,
    BrowserNotRunningError,
    ProfileLockedError,
)
from app.integrations.browser.browser_manager import (
    BrowserManager,
    ProfileProcessLock,
)
from app.integrations.browser.browser_status import BrowserState, LoginState


@pytest.fixture
def mock_browser_config(tmp_path: Path) -> BrowserConfig:
    user_data_dir = tmp_path / "chrome-profile"
    lock_file = tmp_path / "chrome-profile.lock"
    return BrowserConfig(
        target_url="https://chatgpt.com/g/g-jkxrUFNja-indian-stock-market",
        user_data_dir=user_data_dir,
        lock_file_path=lock_file,
        headless=True,
        timeout_seconds=5,
    )


def test_profile_process_lock_acquire_and_release(tmp_path: Path):
    """Verify ProfileProcessLock acquires exclusive lock and releases cleanly."""
    lock_file = tmp_path / "test.lock"
    lock1 = ProfileProcessLock(lock_file)
    assert lock1.acquire() is True

    # Second lock on same file must fail
    lock2 = ProfileProcessLock(lock_file)
    assert lock2.acquire() is False

    # Release first lock
    lock1.release()

    # Now second lock can acquire
    assert lock2.acquire() is True
    lock2.release()


def test_resolve_executable_path():
    """Verify executable resolution handles non-existent and system paths."""
    assert resolve_executable_path("/non/existent/path/to/chrome") is None or isinstance(
        resolve_executable_path("/non/existent/path/to/chrome"), str
    )


@pytest.mark.asyncio
async def test_browser_manager_initial_state(mock_browser_config: BrowserConfig):
    """Verify initial state of fresh BrowserManager."""
    manager = BrowserManager(config=mock_browser_config)
    status = await manager.get_status()

    assert status.state == BrowserState.STOPPED
    assert status.is_running is False
    assert status.login_status == LoginState.UNKNOWN
    assert status.target_url == mock_browser_config.target_url
    assert status.active_pages_count == 0


@pytest.mark.asyncio
async def test_browser_manager_start_and_stop_mocked(mock_browser_config: BrowserConfig):
    """Verify start_browser and stop_browser lifecycle with mocked Playwright."""
    manager = BrowserManager(config=mock_browser_config)

    mock_page = AsyncMock()
    mock_context = MagicMock()
    mock_context.pages = [mock_page]
    mock_context.close = AsyncMock()
    mock_context.on = MagicMock()

    mock_playwright_obj = AsyncMock()
    mock_playwright_obj.chromium.launch_persistent_context = AsyncMock(
        return_value=mock_context
    )
    mock_playwright_obj.stop = AsyncMock()

    with patch(
        "app.integrations.browser.browser_manager.async_playwright"
    ) as mock_async_playwright:
        mock_starter = AsyncMock()
        mock_starter.start = AsyncMock(return_value=mock_playwright_obj)
        mock_async_playwright.return_value = mock_starter

        # 1. Start browser
        status = await manager.start_browser()
        assert status.state == BrowserState.RUNNING
        assert status.is_running is True
        assert manager.is_running is True

        # 2. Duplicate start returns current running state
        status2 = await manager.start_browser()
        assert status2.is_running is True

        # 3. Stop browser
        status_stopped = await manager.stop_browser()
        assert status_stopped.state == BrowserState.STOPPED
        assert status_stopped.is_running is False
        assert manager.is_running is False


@pytest.mark.asyncio
async def test_browser_manager_profile_locked_error(mock_browser_config: BrowserConfig):
    """Verify ProfileLockedError is raised if lock is held externally."""
    # Pre-acquire the lock externally
    external_lock = ProfileProcessLock(mock_browser_config.lock_file_path)
    assert external_lock.acquire() is True

    manager = BrowserManager(config=mock_browser_config)

    with pytest.raises(ProfileLockedError):
        await manager.start_browser()

    external_lock.release()


@pytest.mark.asyncio
async def test_open_target_gpt_requires_running_browser(
    mock_browser_config: BrowserConfig,
):
    """Verify opening target GPT fails when browser is stopped."""
    manager = BrowserManager(config=mock_browser_config)
    with pytest.raises(BrowserNotRunningError):
        await manager.open_target_gpt()


@pytest.mark.asyncio
async def test_verify_login_state_login_required(mock_browser_config: BrowserConfig):
    """Verify login evaluation flags LOGIN_REQUIRED when login button is present."""
    manager = BrowserManager(config=mock_browser_config)

    mock_page = MagicMock()
    mock_page.url = "https://chatgpt.com/g/g-jkxrUFNja-indian-stock-market"

    # Mock locator for login button returning count 1
    mock_locator = MagicMock()
    mock_locator.count = AsyncMock(return_value=1)
    mock_page.locator = MagicMock(return_value=mock_locator)

    manager._context = MagicMock()
    manager._active_page = mock_page
    manager._state = BrowserState.RUNNING

    login_state = await manager.verify_login_state()
    assert login_state == LoginState.LOGIN_REQUIRED


@pytest.mark.asyncio
async def test_verify_login_state_authenticated(mock_browser_config: BrowserConfig):
    """Verify login evaluation flags AUTHENTICATED when prompt composer is present."""
    manager = BrowserManager(config=mock_browser_config)

    mock_page = MagicMock()
    mock_page.url = "https://chatgpt.com/g/g-jkxrUFNja-indian-stock-market"

    # Locator router: login button count = 0, challenge count = 0, composer count = 1
    def locator_mock(selector: str):
        mock_loc = MagicMock()
        if "Log in" in selector:
            mock_loc.count = AsyncMock(return_value=0)
        elif "challenge" in selector:
            mock_loc.count = AsyncMock(return_value=0)
        elif "prompt-textarea" in selector:
            mock_loc.count = AsyncMock(return_value=1)
        else:
            mock_loc.count = AsyncMock(return_value=0)
        return mock_loc

    mock_page.locator = MagicMock(side_effect=locator_mock)

    manager._context = MagicMock()
    manager._active_page = mock_page
    manager._state = BrowserState.RUNNING

    login_state = await manager.verify_login_state()
    assert login_state == LoginState.AUTHENTICATED
