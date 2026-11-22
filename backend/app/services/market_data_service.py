"""
Market Data Service.
Central orchestrator for market data retrieval, TTL caching, and request deduplication.
"""

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

from app.core.config import get_settings
from app.core.logging import get_logger
from app.integrations.market_data.base import MarketDataProvider
from app.integrations.market_data.provider_manager import get_market_data_provider
from app.schemas.market_data import (
    CompanyProfileData,
    CompanyProfileResponse,
    HistoricalDataResponse,
    MarketIndicesResponse,
    MarketStatusResponse,
    StockQuoteResponse,
    StockSearchResponse,
    WatchlistResponse,
)
from app.services.historical_data_service import HistoricalDataService
from app.services.quote_service import QuoteService
from app.services.stock_search_service import StockSearchService
from app.services.watchlist_service import WatchlistService

logger = get_logger("services.market_data")


class MarketDataService:
    """Orchestrates market data operations with thread-safe TTL caching."""

    def __init__(self, provider: Optional[MarketDataProvider] = None) -> None:
        self.provider = provider or get_market_data_provider()
        self.quote_service = QuoteService(self.provider)
        self.historical_service = HistoricalDataService(self.provider)
        self.search_service = StockSearchService(self.provider)
        self.watchlist_service = WatchlistService(self.provider)

        # In-memory TTL cache: key -> (cached_object, expiry_datetime)
        self._cache: Dict[str, Tuple[Any, datetime]] = {}
        self._lock = asyncio.Lock()
        self.cache_ttl = get_settings().MARKET_DATA_CACHE_TTL_SECONDS

    def _get_cache(self, key: str) -> Optional[Any]:
        if key in self._cache:
            data, expiry = self._cache[key]
            if datetime.now(timezone.utc) < expiry:
                return data
            del self._cache[key]
        return None

    def _set_cache(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        ttl = ttl_seconds if ttl_seconds is not None else self.cache_ttl
        expiry = datetime.now(timezone.utc) + asyncio.get_event_loop().time() * 0 + asyncio.tasks.timedelta(seconds=ttl) if hasattr(asyncio.tasks, "timedelta") else datetime.now(timezone.utc)
        # Using datetime timedelta
        from datetime import timedelta
        expiry = datetime.now(timezone.utc) + timedelta(seconds=ttl)
        self._cache[key] = (value, expiry)

    async def search_stocks(
        self,
        query: str,
        exchange: Optional[str] = None,
    ) -> StockSearchResponse:
        """Searches stocks by query string."""
        cache_key = f"search:{query.upper()}:{exchange or 'ALL'}"
        async with self._lock:
            cached = self._get_cache(cache_key)
            if cached:
                return cached

        res = await self.search_service.search_stocks(query, exchange)

        async with self._lock:
            self._set_cache(cache_key, res, ttl_seconds=300)  # Search results cached for 5 mins
        return res

    async def get_quote(
        self,
        symbol: str,
        exchange: Optional[str] = "NSE",
    ) -> StockQuoteResponse:
        """Retrieves normalized stock quote with TTL cache."""
        clean_sym = symbol.strip().upper()
        clean_exch = (exchange or "NSE").strip().upper()
        cache_key = f"quote:{clean_sym}:{clean_exch}"

        async with self._lock:
            cached = self._get_cache(cache_key)
            if cached:
                return cached

        res = await self.quote_service.get_quote(clean_sym, clean_exch)

        async with self._lock:
            self._set_cache(cache_key, res, ttl_seconds=self.cache_ttl)
        return res

    async def get_historical_data(
        self,
        symbol: str,
        range_str: str = "1M",
        interval: Optional[str] = None,
        exchange: Optional[str] = "NSE",
    ) -> HistoricalDataResponse:
        """Retrieves historical chart data with TTL cache."""
        clean_sym = symbol.strip().upper()
        clean_exch = (exchange or "NSE").strip().upper()
        clean_range = range_str.strip().upper()
        cache_key = f"hist:{clean_sym}:{clean_exch}:{clean_range}:{interval or 'DEF'}"

        async with self._lock:
            cached = self._get_cache(cache_key)
            if cached:
                return cached

        res = await self.historical_service.get_historical_data(
            symbol=clean_sym,
            range_str=clean_range,
            interval=interval,
            exchange=clean_exch,
        )

        async with self._lock:
            self._set_cache(cache_key, res, ttl_seconds=self.cache_ttl)
        return res

    async def get_company_profile(
        self,
        symbol: str,
        exchange: Optional[str] = "NSE",
    ) -> CompanyProfileResponse:
        """Retrieves company business profile with TTL cache."""
        clean_sym = symbol.strip().upper()
        clean_exch = (exchange or "NSE").strip().upper()
        cache_key = f"profile:{clean_sym}:{clean_exch}"

        async with self._lock:
            cached = self._get_cache(cache_key)
            if cached:
                return cached

        raw = await self.provider.get_company_profile(clean_sym, clean_exch)
        res = CompanyProfileResponse(success=True, data=CompanyProfileData(**raw))

        async with self._lock:
            self._set_cache(cache_key, res, ttl_seconds=3600)  # Profile cached for 1 hour
        return res

    async def get_market_status(
        self,
        exchange: Optional[str] = "NSE",
    ) -> MarketStatusResponse:
        """Determines market open/closed status."""
        raw = await self.provider.get_market_status(exchange)
        return MarketStatusResponse(**raw)

    async def get_market_indices(self) -> MarketIndicesResponse:
        """Retrieves major benchmark indices with TTL cache."""
        cache_key = "indices:indian_benchmarks"
        async with self._lock:
            cached = self._get_cache(cache_key)
            if cached:
                return cached

        status = await self.provider.get_market_status("NSE")
        raw_indices = await self.provider.get_market_indices()

        from app.schemas.market_data import MarketIndexItem

        items = [MarketIndexItem(**item) for item in raw_indices]
        res = MarketIndicesResponse(
            success=True,
            indices=items,
            market_status=status.get("status", "CLOSED"),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        async with self._lock:
            self._set_cache(cache_key, res, ttl_seconds=30)  # Indices cached for 30 seconds
        return res

    async def get_watchlist(
        self,
        search_query: Optional[str] = None,
        sort_by: Optional[str] = None,
    ) -> WatchlistResponse:
        """Retrieves current watchlist."""
        return await self.watchlist_service.get_watchlist(search_query, sort_by)

    async def add_to_watchlist(
        self,
        symbol: str,
        exchange: Optional[str] = "NSE",
    ) -> WatchlistResponse:
        """Adds symbol to watchlist and returns updated watchlist."""
        await self.watchlist_service.add_symbol(symbol, exchange)
        return await self.watchlist_service.get_watchlist()

    async def remove_from_watchlist(
        self,
        symbol: str,
    ) -> WatchlistResponse:
        """Removes symbol from watchlist and returns updated watchlist."""
        await self.watchlist_service.remove_symbol(symbol)
        return await self.watchlist_service.get_watchlist()


_market_data_service_instance: Optional[MarketDataService] = None


def get_market_data_service() -> MarketDataService:
    """FastAPI dependency resolving MarketDataService singleton."""
    global _market_data_service_instance
    if _market_data_service_instance is None:
        _market_data_service_instance = MarketDataService()
    return _market_data_service_instance
