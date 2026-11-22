"""
RG AI Automation Service.
Coordinates adapter lifecycle, availability probes, and execution handoffs.
"""

from typing import Optional
from app.integrations.rg_ai.gpt_adapter import (
    AdapterAvailability,
    BaseGPTAdapter,
    BrowserGPTAdapter,
)
from app.integrations.browser.browser_status import LoginState
from app.integrations.rg_ai.prompt_manager import PreparedPrompt
from app.integrations.rg_ai.response_manager import NormalizedResult
from app.core.logging import get_logger

logger = get_logger("integrations.rg_ai.automation_service")


class AutomationService:
    """Service facade coordinating the underlying GPT integration adapter."""

    def __init__(self, adapter: Optional[BaseGPTAdapter] = None) -> None:
        self._adapter: BaseGPTAdapter = adapter or BrowserGPTAdapter()

    def set_adapter(self, adapter: BaseGPTAdapter) -> None:
        """Allows injecting alternative adapters (e.g., MockGPTAdapter for unit tests)."""
        logger.info(f"Switching RG AI adapter to {adapter.__class__.__name__}")
        self._adapter = adapter

    def get_adapter(self) -> BaseGPTAdapter:
        """Returns the active adapter instance."""
        return self._adapter

    async def check_availability(self) -> AdapterAvailability:
        """Checks adapter availability and browser status."""
        return await self._adapter.check_availability()

    async def check_authentication(self) -> LoginState:
        """Checks authentication status on the target GPT."""
        return await self._adapter.check_authentication()

    async def initialize(self) -> None:
        """Initializes adapter readiness."""
        await self._adapter.initialize()

    async def execute_prompt(self, prompt: PreparedPrompt, request_id: str) -> NormalizedResult:
        """Executes a prepared prompt using the active adapter."""
        return await self._adapter.execute(prompt, request_id)

    async def cancel_request(self, request_id: str) -> bool:
        """Triggers cancellation on active adapter."""
        return await self._adapter.cancel(request_id)

    async def shutdown(self) -> None:
        """Gracefully shuts down adapter."""
        await self._adapter.shutdown()


_automation_service_instance: Optional[AutomationService] = None


def get_automation_service() -> AutomationService:
    """Returns singleton instance of AutomationService."""
    global _automation_service_instance
    if _automation_service_instance is None:
        _automation_service_instance = AutomationService()
    return _automation_service_instance
