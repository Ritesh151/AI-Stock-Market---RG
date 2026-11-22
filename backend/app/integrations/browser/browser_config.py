"""
Browser Configuration and Environment Path Resolution.
Resolves persistent profile directory and detects Chrome/Chromium executables.
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field

from app.core.config import get_settings


KNOWN_CHROME_EXECUTABLES = [
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/snap/bin/chromium",
]


class BrowserConfig(BaseModel):
    """
    Resolved operational configuration for launching Playwright persistent context.
    """
    target_url: str
    user_data_dir: Path
    lock_file_path: Path
    executable_path: Optional[str] = None
    headless: bool = False
    timeout_seconds: int = 30
    viewport_width: int = 1280
    viewport_height: int = 800
    args: List[str] = Field(default_factory=list)

    model_config = {"arbitrary_types_allowed": True}


def resolve_executable_path(explicit_path: Optional[str] = None) -> Optional[str]:
    """
    Locates an installed Chrome or Chromium executable on the system.
    Returns None if using Playwright's bundled Chromium.
    """
    if explicit_path and os.path.exists(explicit_path) and os.access(explicit_path, os.X_OK):
        return explicit_path

    # Check known paths
    for path_str in KNOWN_CHROME_EXECUTABLES:
        if os.path.exists(path_str) and os.access(path_str, os.X_OK):
            return path_str

    # Check PATH via shutil.which
    for candidate in ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser"]:
        found = shutil.which(candidate)
        if found:
            return found

    return None


def get_browser_config() -> BrowserConfig:
    """
    Assembles verified BrowserConfig using centralized application settings.
    Ensures persistent profile directory is created with restricted permissions (0700).
    """
    settings = get_settings()

    # Resolve absolute path for profile directory
    backend_root = Path(__file__).resolve().parent.parent.parent.parent
    user_data_dir = (backend_root / settings.CHROME_PROFILE_DIR).resolve()
    lock_file_path = user_data_dir.parent / f"{user_data_dir.name}.lock"

    # Ensure profile directory exists with restricted 0700 permissions
    user_data_dir.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(user_data_dir, 0o700)
    except OSError:
        pass

    executable = resolve_executable_path(settings.CHROME_EXECUTABLE_PATH)

    default_args = [
        "--disable-blink-features=AutomationControlled",
        "--no-default-browser-check",
        "--no-first-run",
        "--disable-infobars",
    ]

    return BrowserConfig(
        target_url=settings.TARGET_GPT_URL,
        user_data_dir=user_data_dir,
        lock_file_path=lock_file_path,
        executable_path=executable,
        headless=settings.BROWSER_HEADLESS,
        timeout_seconds=settings.BROWSER_STARTUP_TIMEOUT_SECONDS,
        args=default_args,
    )
