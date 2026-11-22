"""
Market Data Provider Manager.
Manages provider lifecycle, active provider selection, and health probes.
"""

from typing import Optional
from app.core.config import get_settings
from app.core.logging import get_logger
from app.integrations.market_data.base import MarketDataProvider
from app.integrations.market_data.providers.mock_provider import MockMarketDataProvider
from app.integrations.market_data.providers.yahoo_provider import YahooFinanceProvider

logger = get_logger("integrations.market_data.manager")


class ProviderManager:
    """Singleton managing market data provider selection and initialization."""

    def __init__(self) -> None:
        self._provider: Optional[MarketDataProvider] = None
        self._initialize_provider()

    def _initialize_provider(self) -> None:
        settings = get_settings()
        choice = settings.MARKET_DATA_PROVIDER.lower()

        if choice == "mock":
            self._provider = MockMarketDataProvider()
            logger.info("Market data provider initialized: MockMarketDataProvider")
        elif choice == "yahoo":
            self._provider = YahooFinanceProvider(
                timeout_seconds=settings.MARKET_DATA_REQUEST_TIMEOUT_SECONDS,
                max_retries=settings.MARKET_DATA_MAX_RETRIES,
            )
            logger.info("Market data provider initialized: YahooFinanceProvider")
        else:
            # Fallback to Yahoo
            self._provider = YahooFinanceProvider(
                timeout_seconds=settings.MARKET_DATA_REQUEST_TIMEOUT_SECONDS,
                max_retries=settings.MARKET_DATA_MAX_RETRIES,
            )
            logger.info(f"Unrecognized provider '{choice}'; defaulted to YahooFinanceProvider")

    def get_provider(self) -> MarketDataProvider:
        """Returns active market data provider."""
        if self._provider is None:
            self._initialize_provider()
        assert self._provider is not None
        return self._provider

    def set_provider(self, provider: MarketDataProvider) -> None:
        """Overrides active provider (useful for testing)."""
        self._provider = provider
        logger.info(f"Market data provider explicitly set to: {provider.provider_name}")


_provider_manager_instance: Optional[ProviderManager] = None


def get_provider_manager() -> ProviderManager:
    """Returns singleton instance of ProviderManager."""
    global _provider_manager_instance
    if _provider_manager_instance is None:
        _provider_manager_instance = ProviderManager()
    return _provider_manager_instance


def get_market_data_provider() -> MarketDataProvider:
    """FastAPI dependency resolving active market data provider."""
    return get_provider_manager().get_provider()
