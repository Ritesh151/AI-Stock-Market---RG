"""
Stock Search Service.
Coordinates stock discovery across company names, NSE/BSE symbols, and keywords.
"""

from typing import Optional
from app.integrations.market_data.base import MarketDataProvider
from app.schemas.market_data import StockSearchResponse, StockSearchResult


class StockSearchService:
    """Service handling stock query sanitization, discovery, and deduplication."""

    def __init__(self, provider: MarketDataProvider) -> None:
        self.provider = provider

    async def search_stocks(
        self,
        query: str,
        exchange: Optional[str] = None,
    ) -> StockSearchResponse:
        """
        Searches provider for matching equities with deduplication.
        """
        trimmed = query.strip()
        if not trimmed:
            return StockSearchResponse(success=True, query=trimmed, results=[], total=0)

        raw_results = await self.provider.search_stocks(trimmed, exchange=exchange)

        # Deduplicate results by symbol and exchange
        seen = set()
        deduped = []
        for r in raw_results:
            key = (r["symbol"].upper(), r["exchange"].upper())
            if key not in seen:
                seen.add(key)
                deduped.append(StockSearchResult(**r))

        return StockSearchResponse(
            success=True,
            query=trimmed,
            results=deduped,
            total=len(deduped),
        )
