"""
Browser Automation Integration Module (Architectural Interface & Stubs).
Reserved for future browser integration targeting the designated Custom GPT:
https://chatgpt.com/g/g-jkxrUFNja-indian-stock-market

IMPORTANT ARCHITECTURAL CONSTRAINTS:
1. STRICTLY NO OPENAI API KEY OR OPENAI API INTEGRATIONS.
2. NO UNSUPPORTED CHATGPT SCRAPING.
3. This module acts as the architectural boundary for future Playwright browser orchestration.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from app.core.logging import get_logger

logger = get_logger("integrations.browser_agent")

TARGET_CUSTOM_GPT_URL = "https://chatgpt.com/g/g-jkxrUFNja-indian-stock-market"


class BrowserAgentInterface(ABC):
    """
    Interface definition for the future browser automation agent.
    """

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the browser context."""
        pass

    @abstractmethod
    async def query_intelligence(self, prompt: str) -> Dict[str, Any]:
        """Send a structured intelligence query to the target assistant."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Teardown browser session cleanly."""
        pass


class BrowserAgentStub(BrowserAgentInterface):
    """
    Phase 1 stub reserving the integration contract without executing unsupported scraping.
    """

    def __init__(self, target_url: str = TARGET_CUSTOM_GPT_URL):
        self.target_url = target_url
        self._is_active = False

    async def initialize(self) -> None:
        logger.info(
            f"BrowserAgentStub reserved for future phase. Target GPT: {self.target_url}"
        )
        self._is_active = True

    async def query_intelligence(self, prompt: str) -> Dict[str, Any]:
        """
        Placeholder stub. Returns architectural confirmation during Phase 1.
        """
        return {
            "status": "reserved",
            "message": "Browser integration reserved for future phase. No direct OpenAI API used.",
            "target": self.target_url,
        }

    async def close(self) -> None:
        self._is_active = False
        logger.info("BrowserAgentStub closed.")
