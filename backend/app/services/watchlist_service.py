"""
Watchlist Service.
Manages user watchlist storage, duplicate prevention, and real-time quote augmentation.
Integrates with WatchlistRepository for MongoDB persistence and in-memory fallback.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional
import asyncio
import logging

from app.integrations.market_data.base import MarketDataProvider
from app.schemas.market_data import WatchlistItem, WatchlistResponse
from app.repositories.watchlist_repository import WatchlistRepository, get_watchlist_repository
from app.schemas.persistence import WatchlistAddPayload

logger = logging.getLogger(__name__)


class WatchlistService:
    """Service handling watchlist operations backed by MongoDB repository."""

    def __init__(
        self,
        provider: MarketDataProvider,
        repository: Optional[WatchlistRepository] = None,
    ) -> None:
        self.provider = provider
        self.repository = repository
        # Internal in-memory cache for fast lookup
        self._items: Dict[str, WatchlistItem] = {}
        self._lock = asyncio.Lock()
        self._initialize_default_watchlist()

    def _get_repo(self) -> WatchlistRepository:
        if self.repository is None:
            self.repository = get_watchlist_repository()
        return self.repository

    def _initialize_default_watchlist(self) -> None:
        """Seeds default bluechip Indian stocks on startup."""
        defaults = [
            ("RELIANCE", "Reliance Industries Limited", "NSE"),
            ("TCS", "Tata Consultancy Services", "NSE"),
            ("INFY", "Infosys Limited", "NSE"),
            ("HDFCBANK", "HDFC Bank Limited", "NSE"),
        ]
        now = datetime.now(timezone.utc).isoformat()
        for sym, name, exch in defaults:
            self._items[sym] = WatchlistItem(
                symbol=sym,
                company_name=name,
                exchange=exch,
                added_at=now,
            )

    async def add_symbol(
        self,
        symbol: str,
        exchange: Optional[str] = "NSE",
        user_id: str = "guest_user",
    ) -> WatchlistItem:
        """Adds a symbol to the watchlist with duplicate prevention and repository sync."""
        clean_symbol = symbol.strip().upper()
        clean_exchange = (exchange or "NSE").strip().upper()

        async with self._lock:
            if clean_symbol in self._items:
                return self._items[clean_symbol]

            # Fetch current quote to populate company name and pricing
            try:
                quote = await self.provider.get_quote(clean_symbol, clean_exchange)
                item = WatchlistItem(
                    symbol=clean_symbol,
                    company_name=quote.get("company_name", clean_symbol),
                    exchange=clean_exchange,
                    last_price=quote.get("last_price"),
                    change=quote.get("change"),
                    change_percent=quote.get("change_percent"),
                    data_status=quote.get("data_status", "UNKNOWN"),
                    added_at=datetime.now(timezone.utc).isoformat(),
                )
            except Exception:
                item = WatchlistItem(
                    symbol=clean_symbol,
                    company_name=clean_symbol,
                    exchange=clean_exchange,
                    added_at=datetime.now(timezone.utc).isoformat(),
                )

            self._items[clean_symbol] = item

            # Persist to repository
            try:
                repo = self._get_repo()
                await repo.add_item(
                    user_id=user_id,
                    payload=WatchlistAddPayload(
                        symbol=item.symbol,
                        company_name=item.company_name,
                        exchange=item.exchange,
                    ),
                    quote_data={
                        "last_price": item.last_price,
                        "change": item.change,
                        "change_percent": item.change_percent,
                        "data_status": item.data_status,
                    },
                )
            except Exception as e:
                logger.warning(f"Error persisting watchlist item to repository: {e}")

            return item

    async def remove_symbol(
        self,
        symbol: str,
        exchange: Optional[str] = "NSE",
        user_id: str = "guest_user",
    ) -> bool:
        """Removes a symbol from the watchlist."""
        clean_symbol = symbol.strip().upper()
        clean_exchange = (exchange or "NSE").strip().upper()

        async with self._lock:
            removed = False
            if clean_symbol in self._items:
                del self._items[clean_symbol]
                removed = True

            try:
                repo = self._get_repo()
                repo_removed = await repo.remove_item(
                    user_id=user_id,
                    symbol=clean_symbol,
                    exchange=clean_exchange,
                )
                removed = removed or repo_removed
            except Exception as e:
                logger.warning(f"Error removing watchlist item from repo: {e}")

            return removed

    async def get_watchlist(
        self,
        search_query: Optional[str] = None,
        sort_by: Optional[str] = None,
        user_id: str = "guest_user",
    ) -> WatchlistResponse:
        """
        Retrieves all watchlist items with optional search filtering and sorting.
        Synchronizes with repository if available.
        """
        try:
            repo = self._get_repo()
            repo_items = await repo.list_items(user_id=user_id)
            if repo_items:
                for r in repo_items:
                    if r.symbol not in self._items:
                        self._items[r.symbol] = WatchlistItem(
                            symbol=r.symbol,
                            company_name=r.company_name,
                            exchange=r.exchange,
                            last_price=r.last_price,
                            change=r.change,
                            change_percent=r.change_percent,
                            data_status=r.data_status,
                            added_at=r.added_at.isoformat(),
                        )
        except Exception as e:
            logger.warning(f"Error querying watchlist repository: {e}")

        items: List[WatchlistItem] = list(self._items.values())

        if search_query:
            sq = search_query.strip().upper()
            items = [
                i for i in items
                if sq in i.symbol.upper() or sq in i.company_name.upper()
            ]

        # Sorting logic
        if sort_by == "name":
            items.sort(key=lambda x: x.company_name.lower())
        elif sort_by == "price_change":
            items.sort(key=lambda x: (x.change is not None, x.change or 0), reverse=True)
        elif sort_by == "change_percent":
            items.sort(key=lambda x: (x.change_percent is not None, x.change_percent or 0), reverse=True)

        return WatchlistResponse(success=True, items=items, total=len(items))
