"""
Market Data Integration Package.
"""

from app.integrations.market_data.base import MarketDataProvider
from app.integrations.market_data.exceptions import (
    MarketDataException,
    StockNotFoundError,
    ProviderUnavailableError,
    RateLimitExceededError,
    InvalidTimeframeError,
)
from app.integrations.market_data.provider_config import DataFreshness
from app.integrations.market_data.provider_manager import (
    ProviderManager,
    get_provider_manager,
    get_market_data_provider,
)

__all__ = [
    "MarketDataProvider",
    "MarketDataException",
    "StockNotFoundError",
    "ProviderUnavailableError",
    "RateLimitExceededError",
    "InvalidTimeframeError",
    "DataFreshness",
    "ProviderManager",
    "get_provider_manager",
    "get_market_data_provider",
]
