"""
RG AI Orchestration Configuration Constants.
Centralizes limits, timeouts, and target settings.
"""

from typing import Final
from app.core.config import get_settings

settings = get_settings()

# Target GPT URL (strictly centralized from core settings)
TARGET_GPT_URL: Final[str] = settings.TARGET_GPT_URL

# Prompt Constraints
MIN_PROMPT_LENGTH: Final[int] = 2
MAX_PROMPT_LENGTH: Final[int] = 4000
MAX_METADATA_KEYS: Final[int] = 20

# Orchestrator Queue & Concurrency Constraints
# Concurrency is strictly 1 to serialize access to the single persistent Chrome profile
DEFAULT_QUEUE_SIZE: Final[int] = 50
MAX_CONCURRENT_REQUESTS: Final[int] = 1
DEFAULT_REQUEST_TIMEOUT_SECONDS: Final[int] = 120
DEFAULT_POLL_INTERVAL_SECONDS: Final[float] = 1.0

# Supported Template Versions
CURRENT_PROMPT_TEMPLATE_VERSION: Final[str] = "v1_indian_stock_analysis"
