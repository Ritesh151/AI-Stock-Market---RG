"""
RG AI Integration Package.
Exposes config, exceptions, managers, adapters, and automation services.
"""

from app.integrations.rg_ai.gpt_config import (
    CURRENT_PROMPT_TEMPLATE_VERSION,
    DEFAULT_POLL_INTERVAL_SECONDS,
    DEFAULT_QUEUE_SIZE,
    DEFAULT_REQUEST_TIMEOUT_SECONDS,
    MAX_CONCURRENT_REQUESTS,
    MAX_PROMPT_LENGTH,
    MIN_PROMPT_LENGTH,
    TARGET_GPT_URL,
)
from app.integrations.rg_ai.integration_exceptions import (
    AuthenticationRequiredError,
    BrowserUnavailableError,
    DuplicateRequestError,
    IntegrationException,
    InvalidStateTransitionError,
    QueueFullError,
    RequestCancelledError,
    RequestTimeoutError,
    UnsupportedIntegrationError,
)
from app.integrations.rg_ai.prompt_manager import (
    PreparedPrompt,
    PromptManager,
    get_prompt_manager,
)
from app.integrations.rg_ai.response_manager import (
    NormalizedError,
    NormalizedResult,
    ResponseManager,
    get_response_manager,
)
from app.integrations.rg_ai.conversation_manager import (
    ConversationManager,
    ConversationSession,
    get_conversation_manager,
)
from app.integrations.rg_ai.gpt_adapter import (
    AdapterAvailability,
    BaseGPTAdapter,
    BrowserGPTAdapter,
    MockGPTAdapter,
)
from app.integrations.rg_ai.automation_service import (
    AutomationService,
    get_automation_service,
)

__all__ = [
    "TARGET_GPT_URL",
    "MIN_PROMPT_LENGTH",
    "MAX_PROMPT_LENGTH",
    "DEFAULT_QUEUE_SIZE",
    "MAX_CONCURRENT_REQUESTS",
    "DEFAULT_REQUEST_TIMEOUT_SECONDS",
    "DEFAULT_POLL_INTERVAL_SECONDS",
    "CURRENT_PROMPT_TEMPLATE_VERSION",
    "IntegrationException",
    "UnsupportedIntegrationError",
    "AuthenticationRequiredError",
    "BrowserUnavailableError",
    "RequestCancelledError",
    "RequestTimeoutError",
    "QueueFullError",
    "DuplicateRequestError",
    "InvalidStateTransitionError",
    "PreparedPrompt",
    "PromptManager",
    "get_prompt_manager",
    "NormalizedResult",
    "NormalizedError",
    "ResponseManager",
    "get_response_manager",
    "ConversationSession",
    "ConversationManager",
    "get_conversation_manager",
    "AdapterAvailability",
    "BaseGPTAdapter",
    "BrowserGPTAdapter",
    "MockGPTAdapter",
    "AutomationService",
    "get_automation_service",
]
