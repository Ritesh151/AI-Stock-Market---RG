"""
Market Data Provider Configuration & Constants.
Defines supported exchanges, freshness statuses, timeframes, and Indian trading sessions.
"""

from enum import Enum
from typing import Dict, Set

# Data Freshness Classifications (Section 3)
class DataFreshness(str, Enum):
    REAL_TIME = "REAL_TIME"
    DELAYED = "DELAYED"
    END_OF_DAY = "END_OF_DAY"
    HISTORICAL = "HISTORICAL"
    UNAVAILABLE = "UNAVAILABLE"
    UNKNOWN = "UNKNOWN"


# Supported Exchanges
SUPPORTED_EXCHANGES: Set[str] = {"NSE", "BSE"}

# Exchange ticker suffixes for Yahoo Finance
EXCHANGE_SUFFIX_MAP: Dict[str, str] = {
    "NSE": ".NS",
    "BSE": ".BO",
}

# Standard Indian Market Trading Parameters
MARKET_TIMEZONE: str = "Asia/Kolkata"
MARKET_OPEN_HOUR: int = 9
MARKET_OPEN_MINUTE: int = 15
MARKET_CLOSE_HOUR: int = 15
MARKET_CLOSE_MINUTE: int = 30

# Supported Chart Ranges & Valid Intervals Mapping
SUPPORTED_CHART_RANGES: Set[str] = {"1D", "5D", "1M", "3M", "6M", "1Y", "5Y"}

SUPPORTED_CHART_INTERVALS: Set[str] = {"1m", "5m", "15m", "1h", "1d", "1wk"}

# Range to default interval mapping
DEFAULT_INTERVAL_FOR_RANGE: Dict[str, str] = {
    "1D": "5m",
    "5D": "15m",
    "1M": "1d",
    "3M": "1d",
    "6M": "1d",
    "1Y": "1d",
    "5Y": "1wk",
}

# Valid intervals allowed per range (to prevent provider reject)
ALLOWED_INTERVALS_BY_RANGE: Dict[str, Set[str]] = {
    "1D": {"1m", "5m", "15m", "1h"},
    "5D": {"5m", "15m", "1h", "1d"},
    "1M": {"15m", "1h", "1d", "1wk"},
    "3M": {"1h", "1d", "1wk"},
    "6M": {"1d", "1wk"},
    "1Y": {"1d", "1wk"},
    "5Y": {"1d", "1wk"},
}
