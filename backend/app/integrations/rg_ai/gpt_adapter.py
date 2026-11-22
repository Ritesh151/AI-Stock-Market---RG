"""
RG AI GPT Integration Adapters.
Defines abstract integration contract and implementations:
- BaseGPTAdapter (abstract interface)
- BrowserGPTAdapter (production adapter using Phase 3 BrowserManager, enforcing non-scraping boundaries)
- MockGPTAdapter (for automated tests, simulated completions, timeouts, and cancellations)
"""

import abc
import asyncio
from typing import Any, Dict, Optional
from pydantic import BaseModel
from app.integrations.browser import BrowserManager, get_browser_manager
from app.integrations.browser.browser_status import BrowserState, LoginState
from app.integrations.rg_ai.gpt_config import TARGET_GPT_URL
from app.integrations.rg_ai.integration_exceptions import (
    AuthenticationRequiredError,
    BrowserUnavailableError,
    RequestCancelledError,
    UnsupportedIntegrationError,
)
from app.integrations.rg_ai.prompt_manager import PreparedPrompt
from app.integrations.rg_ai.response_manager import NormalizedResult
from app.core.exceptions import AppException
from app.core.logging import get_logger

logger = get_logger("integrations.rg_ai.gpt_adapter")


class AdapterAvailability(BaseModel):
    """Status representing adapter capability and browser readiness."""

    is_available: bool
    is_browser_running: bool
    login_state: str
    target_url: str
    adapter_type: str
    message: str


class BaseGPTAdapter(abc.ABC):
    """Abstract Base Class for RG AI GPT Execution Adapters."""

    @abc.abstractmethod
    async def check_availability(self) -> AdapterAvailability:
        """Checks whether the integration is currently operable."""
        pass

    @abc.abstractmethod
    async def check_authentication(self) -> LoginState:
        """Verifies if the current session is authenticated with the target GPT."""
        pass

    @abc.abstractmethod
    async def initialize(self) -> None:
        """Initializes or warms up integration dependencies."""
        pass

    @abc.abstractmethod
    async def execute(self, prompt: PreparedPrompt, request_id: str) -> NormalizedResult:
        """
        Executes prompt through the integration adapter.
        Must return NormalizedResult or raise appropriate domain IntegrationException.
        """
        pass

    @abc.abstractmethod
    async def cancel(self, request_id: str) -> bool:
        """Cancels an in-flight execution for the given request ID."""
        pass

    @abc.abstractmethod
    async def shutdown(self) -> None:
        """Cleans up adapter resources."""
        pass


def format_strict_market_prompt(user_query: str) -> str:
    """
    Directs the Indian Stock Market Custom GPT to output strictly structured, short JSON.
    Prevents the GPT from asking conversational counter-questions or giving narrative essays.
    """
    clean_query = user_query.strip()
    # If the prompt is already pre-formatted or explicitly contains JSON schema directives, pass as is
    if "Role: Indian Equities" in clean_query or '{"stock_name"' in clean_query:
        return clean_query

    return (
        "Role: Indian Equities Market Intelligence Analyst (NSE/BSE).\n"
        f"User Query: {clean_query}\n\n"
        "MANDATORY INSTRUCTIONS:\n"
        "1. DO NOT ask clarifying or counter-questions (do NOT ask for investment horizon, risk appetite, or budget).\n"
        "2. Provide your immediate analytical assessment assuming standard swing/medium-term timeframe (1-3 months) and medium risk.\n"
        "3. Output MUST be ONLY a single compact, valid JSON object in a ```json ... ``` code fence.\n"
        "4. DO NOT write any greeting, introductory text, conversational counter-questions, disclaimers, or notes outside the JSON block.\n\n"
        "Required JSON format:\n"
        "```json\n"
        "{\n"
        '  "stock_name": "<Company legal name, e.g. Tata Steel Limited>",\n'
        '  "symbol": "<NSE ticker, e.g. TATASTEEL>",\n'
        '  "exchange": "NSE",\n'
        '  "currency": "INR",\n'
        '  "current_price": <number or null>,\n'
        '  "market_trend": "bullish" | "bearish" | "neutral" | "sideways" | "volatile",\n'
        '  "recommendation": "BUY" | "SELL" | "HOLD" | "ACCUMULATE" | "REDUCE" | "AVOID",\n'
        '  "entry_zone": {"min": <number>, "max": <number>},\n'
        '  "target_price": <number>,\n'
        '  "stop_loss": <number>,\n'
        '  "risk_level": "low" | "medium" | "high" | "very_high",\n'
        '  "time_horizon": "1-3 months",\n'
        '  "reasoning": [\n'
        '    "<concise key reason 1>",\n'
        '    "<concise key reason 2>",\n'
        '    "<concise key reason 3>"\n'
        "  ]\n"
        "}\n"
        "```\n"
        "Now respond strictly with the JSON object."
    )


class BrowserGPTAdapter(BaseGPTAdapter):
    """
    Browser-backed GPT Adapter using Phase 3 persistent Chrome BrowserManager.
    Strictly adheres to project boundaries:
    - Verifies Chrome lifecycle & login state.
    - Does NOT use unsupported scraping, fragile DOM selectors, or undocumented private APIs.
    - Honestly raises UnsupportedIntegrationError when programmatic extraction is unavailable.
    """

    def __init__(self, browser_manager: Optional[BrowserManager] = None) -> None:
        self._browser_manager = browser_manager or get_browser_manager()
        self._target_url = TARGET_GPT_URL
        self._active_requests: Dict[str, asyncio.Event] = {}

    async def check_availability(self) -> AdapterAvailability:
        """Checks browser manager running status and returns adapter readiness."""
        status = await self._browser_manager.get_status()
        is_running = status.is_running and status.state not in {
            BrowserState.STOPPED,
            BrowserState.ERROR,
            BrowserState.DISCONNECTED,
            BrowserState.STOPPING,
        }
        login_str = (
            status.login_status.value
            if isinstance(status.login_status, LoginState)
            else str(status.login_status)
        )

        return AdapterAvailability(
            is_available=is_running,
            is_browser_running=is_running,
            login_state=login_str,
            target_url=self._target_url,
            adapter_type="BrowserGPTAdapter",
            message="Managed Chrome browser session available" if is_running else "Browser is not running",
        )

    async def check_authentication(self) -> LoginState:
        """Probes live ChatGPT page to verify user login state."""
        return await self._browser_manager.verify_login_state()

    async def initialize(self) -> None:
        """Validates browser availability before execution."""
        status = await self._browser_manager.get_status()
        if not status.is_running:
            raise BrowserUnavailableError(
                "Browser is not currently running. Please start the browser via the Chrome Session panel."
            )

    async def execute(self, prompt: PreparedPrompt, request_id: str) -> NormalizedResult:
        """
        Executes prompt through the adapter.
        Automates typing the prompt into the managed Custom GPT, submitting it,
        and extracting the completed response.
        """
        cancel_event = asyncio.Event()
        self._active_requests[request_id] = cancel_event

        try:
            status = await self._browser_manager.get_status()
            if not status.is_running:
                raise BrowserUnavailableError("Browser is not running. Please start the browser session first.")

            # Verify authentication state
            login_state = await self._browser_manager.verify_login_state()
            if login_state != LoginState.AUTHENTICATED:
                raise AuthenticationRequiredError(
                    f"Authentication required (current login state: {login_state.value}). "
                    "Please complete manual login in the managed Chrome browser."
                )

            # Check if cancelled before execution
            if cancel_event.is_set():
                raise RequestCancelledError(f"Request {request_id} was cancelled before execution.")

            page = self._browser_manager._active_page
            if not page or page.is_closed():
                raise BrowserUnavailableError("Browser active page is not available.")

            # 1. Ensure active page is on ChatGPT
            if "chatgpt.com" not in page.url.lower():
                await self._browser_manager.open_target_gpt()
                page = self._browser_manager._active_page
                await asyncio.sleep(2)

            # 2. Locate input composer (supports modern ProseMirror contenteditable and legacy textareas)
            textarea = page.locator(
                '#prompt-textarea, [contenteditable="true"], .ProseMirror, textarea[placeholder*="message"], [data-placeholder]'
            ).first
            await textarea.wait_for(state="visible", timeout=25000)

            # Record existing assistant message count
            # Record existing assistant / message count
            assistant_selector = '[data-message-author-role="assistant"], [class*="prose"], [class*="markdown"], article'
            initial_count = await page.locator(assistant_selector).count()

            # 3. Enter user prompt wrapped in strict JSON instructions
            prompt_text = format_strict_market_prompt(prompt.cleaned_prompt)
            try:
                await textarea.click()
                await textarea.fill(prompt_text)
                await page.keyboard.type(" ")
            except Exception:
                await textarea.click()
                await page.keyboard.insert_text(prompt_text)
                await page.keyboard.type(" ")

            await asyncio.sleep(0.5)

            # 4. Click Send button or press Enter
            send_btn = page.locator('button[aria-label="Send"], button[data-testid="send-button"], button[aria-label*="Send"], button[aria-label*="submit"]')
            send_clicked = False
            for _ in range(5):
                if await send_btn.count() > 0 and await send_btn.first.is_enabled():
                    await send_btn.first.click()
                    send_clicked = True
                    break
                await asyncio.sleep(0.3)

            if not send_clicked:
                await page.keyboard.press("Control+Enter")
                await asyncio.sleep(0.3)
                if await send_btn.count() > 0 and await send_btn.first.is_enabled():
                    await send_btn.first.click()
                else:
                    await page.keyboard.press("Enter")

            logger.info(f"Request {request_id}: Strict prompt submitted to Custom GPT. Waiting for response...")

            # 5. Wait for generation to start
            stop_btn_selector = 'button[data-testid="stop-button"], button[aria-label="Stop generating"], button[aria-label*="Stop"]'
            start_wait = 0.0
            while start_wait < 15.0:
                if cancel_event.is_set():
                    raise RequestCancelledError(f"Request {request_id} was cancelled.")
                current_count = await page.locator(assistant_selector).count()
                stop_visible = await page.locator(stop_btn_selector).count() > 0
                has_code = await page.locator("pre code, pre").count() > 0
                if current_count > initial_count or stop_visible or has_code:
                    break
                await asyncio.sleep(0.5)
                start_wait += 0.5

            # 6. Wait for streaming to finish and text to stabilize
            gen_wait = 0.0
            max_gen_time = 90.0
            last_text = ""
            stable_ticks = 0

            while gen_wait < max_gen_time:
                if cancel_event.is_set():
                    stop_btn = page.locator(stop_btn_selector)
                    if await stop_btn.count() > 0:
                        await stop_btn.first.click()
                    raise RequestCancelledError(f"Request {request_id} was cancelled during generation.")

                stop_visible = await page.locator(stop_btn_selector).count() > 0
                assistants = page.locator(assistant_selector)
                count = await assistants.count()

                # Get latest text from pre code or assistants
                code_blocks = page.locator("pre code, pre")
                if await code_blocks.count() > 0:
                    current_text = (await code_blocks.last.inner_text()).strip()
                elif count > initial_count:
                    current_text = (await assistants.last.inner_text()).strip()
                elif count > 0:
                    current_text = (await assistants.last.inner_text()).strip()
                else:
                    current_text = ""

                if current_text:
                    if current_text == last_text and not stop_visible:
                        stable_ticks += 1
                        if stable_ticks >= 2:
                            break
                    else:
                        stable_ticks = 0
                    last_text = current_text

                await asyncio.sleep(1.0)
                gen_wait += 1.0

            # 7. Extract final response text
            final_text = ""
            code_blocks = page.locator("pre code, pre")
            code_count = await code_blocks.count()
            for idx in reversed(range(code_count)):
                candidate = (await code_blocks.nth(idx).inner_text()).strip()
                if "{" in candidate and ("stock_name" in candidate or "symbol" in candidate or "recommendation" in candidate):
                    final_text = candidate
                    break

            if not final_text:
                assistants = page.locator(assistant_selector)
                if await assistants.count() > 0:
                    final_text = (await assistants.last.inner_text()).strip()
                elif last_text:
                    final_text = last_text.strip()

            if not final_text:
                raise AppException(
                    message="Custom GPT response could not be extracted from browser page.",
                    code="EXTRACTION_FAILED",
                    status_code=502,
                )

            logger.info(f"Request {request_id}: Response successfully extracted ({len(final_text)} chars).")
            return NormalizedResult(
                content=final_text,
                raw_response={"text": final_text, "source": "chatgpt_browser"},
                format_type="application/json" if ("{" in final_text or "```" in final_text) else "text/plain",
            )
        finally:
            self._active_requests.pop(request_id, None)

    async def cancel(self, request_id: str) -> bool:
        """Marks the cancellation event for an active request."""
        event = self._active_requests.get(request_id)
        if event:
            event.set()
            return True
        return False

    async def shutdown(self) -> None:
        """Clean up active request map."""
        for event in self._active_requests.values():
            event.set()
        self._active_requests.clear()


class MockGPTAdapter(BaseGPTAdapter):
    """
    Mock GPT Adapter for automated test suites and local orchestration verification.
    Supports simulated responses, delays, cancellations, and controlled errors.
    """

    def __init__(
        self,
        simulated_delay: float = 0.05,
        default_response: str = "Technical analysis complete: NIFTY 50 trading above 20-DMA support at 24,200.",
        simulate_login_required: bool = False,
        simulate_browser_down: bool = False,
        simulate_unsupported: bool = False,
        simulate_failure: bool = False,
    ) -> None:
        self.simulated_delay = simulated_delay
        self.default_response = default_response
        self.simulate_login_required = simulate_login_required
        self.simulate_browser_down = simulate_browser_down
        self.simulate_unsupported = simulate_unsupported
        self.simulate_failure = simulate_failure
        self._active_requests: Dict[str, asyncio.Event] = {}

    async def check_availability(self) -> AdapterAvailability:
        is_running = not self.simulate_browser_down
        return AdapterAvailability(
            is_available=is_running,
            is_browser_running=is_running,
            login_state=LoginState.LOGIN_REQUIRED.value if self.simulate_login_required else LoginState.AUTHENTICATED.value,
            target_url=TARGET_GPT_URL,
            adapter_type="MockGPTAdapter",
            message="Mock adapter active",
        )

    async def check_authentication(self) -> LoginState:
        if self.simulate_login_required:
            return LoginState.LOGIN_REQUIRED
        return LoginState.AUTHENTICATED

    async def initialize(self) -> None:
        if self.simulate_browser_down:
            raise BrowserUnavailableError("Simulated browser unavailable in mock adapter.")

    async def execute(self, prompt: PreparedPrompt, request_id: str) -> NormalizedResult:
        cancel_event = asyncio.Event()
        self._active_requests[request_id] = cancel_event

        try:
            if self.simulate_browser_down:
                raise BrowserUnavailableError("Browser process is not running.")

            if self.simulate_login_required:
                raise AuthenticationRequiredError("Authentication required on target GPT.")

            if self.simulate_unsupported:
                raise UnsupportedIntegrationError("Unsupported integration operation.")

            if self.simulate_failure:
                raise RuntimeError("Simulated internal execution failure.")

            # Simulate execution duration with cancellation support
            elapsed = 0.0
            step = 0.02
            while elapsed < self.simulated_delay:
                if cancel_event.is_set():
                    raise RequestCancelledError(f"Request {request_id} was cancelled.")
                await asyncio.sleep(min(step, self.simulated_delay - elapsed))
                elapsed += step

            if cancel_event.is_set():
                raise RequestCancelledError(f"Request {request_id} was cancelled.")

            return NormalizedResult(
                content=f"[Verified Result] {self.default_response} (Prompt: {prompt.cleaned_prompt})",
                metadata={"template": prompt.template_version, "mock": True},
                format_type="text/plain",
            )
        finally:
            self._active_requests.pop(request_id, None)

    async def cancel(self, request_id: str) -> bool:
        event = self._active_requests.get(request_id)
        if event:
            event.set()
            return True
        return False

    async def shutdown(self) -> None:
        for event in self._active_requests.values():
            event.set()
        self._active_requests.clear()
