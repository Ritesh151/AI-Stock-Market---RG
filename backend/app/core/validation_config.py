"""
RG AI Validation Configuration Constants.
Defines limits, payload thresholds, percentage ranges, and standard disclaimers.
"""

from typing import Final, Set

# Payload Constraints
MAX_JSON_PAYLOAD_SIZE: Final[int] = 512 * 1024  # 512 KB
MAX_JSON_DEPTH: Final[int] = 15
MAX_REASONING_ITEMS: Final[int] = 20
MAX_STRING_LENGTH: Final[int] = 2000

# Schema Metadata
DEFAULT_SCHEMA_VERSION: Final[str] = "1.0"
STANDARD_FINANCIAL_DISCLAIMER: Final[str] = (
    "Informational research only. Not financial advice."
)

# Supported Financial Identifiers
SUPPORTED_EXCHANGES: Final[Set[str]] = {"NSE", "BSE", "MCX"}
SUPPORTED_CURRENCIES: Final[Set[str]] = {"INR"}

# Financial Sanity Bounds
MIN_PERCENT_CHANGE: Final[float] = -100.0
MAX_PERCENT_CHANGE: Final[float] = 10000.0  # Max +10,000%
MIN_RSI_VALUE: Final[float] = 0.0
MAX_RSI_VALUE: Final[float] = 100.0
