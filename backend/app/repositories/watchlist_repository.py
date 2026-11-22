"""
Watchlist Repository for MongoDB.
Manages persistent user watchlists with compound unique indexing (user_id, symbol, exchange).
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError

from app.core.logging import get_logger
from app.repositories.base import BaseRepository
from app.schemas.persistence import WatchlistMongoItem

logger = get_logger("watchlist_repo")

# Standard default bluechips
_DEFAULT_WATCHLIST_SEEDS = [
    {"symbol": "RELIANCE", "exchange": "NSE", "notes": "Energy & Retail Conglomerate"},
    {"symbol": "TCS", "exchange": "NSE", "notes": "IT Services Leader"},
    {"symbol": "HDFCBANK", "exchange": "NSE", "notes": "Private Banking Benchmark"},
    {"symbol": "INFY", "exchange": "NSE", "notes": "Technology Major"},
]


class WatchlistRepository(BaseRepository[WatchlistMongoItem]):
    """Repository handling persistent user watchlists."""

    def __init__(self):
        super().__init__(collection_name="watchlists")
        # In-memory store for fallback/tests
        self._fallback_store: Dict[str, List[WatchlistMongoItem]] = {}
        self._initialize_fallback_defaults("guest_user")

    def _initialize_fallback_defaults(self, user_id: str):
        if user_id not in self._fallback_store:
            now = datetime.now(timezone.utc)
            self._fallback_store[user_id] = [
                WatchlistMongoItem(
                    user_id=user_id,
                    symbol=item["symbol"],
                    exchange=item["exchange"],
                    added_at=now,
                    notes=item["notes"],
                )
                for item in _DEFAULT_WATCHLIST_SEEDS
            ]

    async def add_item(
        self,
        user_id: str,
        symbol: Optional[str] = None,
        exchange: str = "NSE",
        notes: Optional[str] = None,
        payload: Optional[WatchlistAddPayload] = None,
        quote_data: Optional[Dict[str, Any]] = None,
    ) -> WatchlistMongoItem:
        """Add symbol to user watchlist with duplicate prevention."""
        if payload is not None:
            clean_symbol = payload.symbol.upper().strip()
            clean_exchange = (payload.exchange or "NSE").upper().strip()
            notes = payload.notes or notes
        else:
            clean_symbol = (symbol or "").upper().strip()
            clean_exchange = (exchange or "NSE").upper().strip()

        now = datetime.now(timezone.utc)

        item = WatchlistMongoItem(
            user_id=user_id,
            symbol=clean_symbol,
            exchange=clean_exchange,
            added_at=now,
            notes=notes,
        )


        if self.is_available and self.collection is not None:
            try:
                await self.collection.insert_one(item.model_dump())
            except DuplicateKeyError:
                # Symbol already exists in watchlist for user, update notes
                if notes:
                    await self.collection.update_one(
                        {"user_id": user_id, "symbol": clean_symbol, "exchange": clean_exchange},
                        {"$set": {"notes": notes}},
                    )
            return item

        # In-memory fallback
        self._initialize_fallback_defaults(user_id)
        existing = [
            i for i in self._fallback_store[user_id]
            if i.symbol == clean_symbol and i.exchange == clean_exchange
        ]
        if not existing:
            self._fallback_store[user_id].append(item)
        elif notes:
            existing[0].notes = notes

        return item

    async def remove_item(
        self,
        user_id: str,
        symbol: str,
        exchange: Optional[str] = None,
    ) -> bool:
        """Remove symbol from user watchlist."""
        clean_symbol = symbol.upper().strip()

        if self.is_available and self.collection is not None:
            query = {"user_id": user_id, "symbol": clean_symbol}
            if exchange:
                query["exchange"] = exchange.upper().strip()
            res = await self.collection.delete_many(query)
            return res.deleted_count > 0

        # In-memory fallback
        self._initialize_fallback_defaults(user_id)
        original_len = len(self._fallback_store[user_id])
        self._fallback_store[user_id] = [
            i for i in self._fallback_store[user_id]
            if not (i.symbol == clean_symbol and (exchange is None or i.exchange == exchange.upper().strip()))
        ]
        return len(self._fallback_store[user_id]) < original_len

    async def get_item(
        self,
        user_id: str,
        symbol: str,
        exchange: Optional[str] = None,
    ) -> Optional[WatchlistMongoItem]:
        """Fetch single watchlist item for user."""
        clean_symbol = symbol.upper().strip()
        query = {"user_id": user_id, "symbol": clean_symbol}
        if exchange:
            query["exchange"] = exchange.upper().strip()

        if self.is_available and self.collection is not None:
            doc = await self.collection.find_one(query)
            if doc:
                doc.pop("_id", None)
                return WatchlistMongoItem(**doc)
            return None

        self._initialize_fallback_defaults(user_id)
        target_ex = exchange.upper().strip() if exchange else None
        for item in self._fallback_store.get(user_id, []):
            if item.symbol == clean_symbol and (target_ex is None or item.exchange == target_ex):
                return item
        return None

    async def list_items(
        self,
        user_id: str = "guest_user",
        search_query: Optional[str] = None,
    ) -> List[WatchlistMongoItem]:

        """Fetch all watchlist entries for user with optional symbol search."""
        if self.is_available and self.collection is not None:
            # Seed defaults on first run if empty
            count = await self.collection.count_documents({"user_id": user_id})
            if count == 0 and user_id == "guest_user":
                now = datetime.now(timezone.utc)
                seed_docs = [
                    {
                        "user_id": user_id,
                        "symbol": item["symbol"],
                        "exchange": item["exchange"],
                        "added_at": now,
                        "notes": item["notes"],
                    }
                    for item in _DEFAULT_WATCHLIST_SEEDS
                ]
                await self.collection.insert_many(seed_docs)

            query: Dict[str, Any] = {"user_id": user_id}
            if search_query and search_query.strip():
                query["symbol"] = {"$regex": search_query.strip().upper()}

            cursor = self.collection.find(query).sort("added_at", ASCENDING)
            results = []
            async for doc in cursor:
                doc.pop("_id", None)
                results.append(WatchlistMongoItem(**doc))
            return results

        # In-memory fallback
        self._initialize_fallback_defaults(user_id)
        items = self._fallback_store.get(user_id, [])
        if search_query and search_query.strip():
            sq = search_query.strip().upper()
            items = [i for i in items if sq in i.symbol]
        return items


_watchlist_repository: Optional[WatchlistRepository] = None


def get_watchlist_repository() -> WatchlistRepository:
    """Singleton getter for WatchlistRepository."""
    global _watchlist_repository
    if _watchlist_repository is None:
        _watchlist_repository = WatchlistRepository()
    return _watchlist_repository
