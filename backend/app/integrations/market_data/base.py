"""
Abstract Market Data Provider Base Interface.
Defines mandatory contract for all market data provider adapters.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class MarketDataProvider(ABC):
    """Abstract interface defining market data provider operations."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable provider identifier and source attribution name."""
        pass

    @abstractmethod
    async def search_stocks(
        self,
        query: str,
        exchange: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Searches listed stocks by company legal name or trading symbol.
        Returns list of matching stock descriptors.
        """
        pass

    @abstractmethod
    async def get_quote(
        self,
        symbol: str,
        exchange: Optional[str] = "NSE",
    ) -> Dict[str, Any]:
        """
        Retrieves normalized current quote for target symbol.
        Preserves nulls without zero-filling.
        """
        pass

    @abstractmethod
    async def get_historical_data(
        self,
        symbol: str,
        range_str: str = "1M",
        interval: str = "1d",
        exchange: Optional[str] = "NSE",
    ) -> Dict[str, Any]:
        """
        Retrieves historical OHLCV candle dataset for target symbol across range and interval.
        """
        pass

    @abstractmethod
    async def get_market_status(
        self,
        exchange: Optional[str] = "NSE",
    ) -> Dict[str, Any]:
        """
        Determines current exchange trading session state (OPEN, CLOSED, PRE_OPEN).
        """
        pass

    @abstractmethod
    async def get_company_profile(
        self,
        symbol: str,
        exchange: Optional[str] = "NSE",
    ) -> Dict[str, Any]:
        """
        Retrieves company fundamental profile (sector, industry, description, key stats).
        """
        pass

    @abstractmethod
    async def get_market_indices(self) -> List[Dict[str, Any]]:
        """
        Retrieves major benchmark indices (NIFTY 50, SENSEX, BANK NIFTY, INDIA VIX).
        """
        pass

    @abstractmethod
    async def check_health(self) -> bool:
        """
        Verifies provider connectivity and operational status.
        """
        pass
