"""
Quote Service.
Normalizes, validates, and coordinates single-stock market quote retrieval.
"""

from typing import Optional
from app.integrations.market_data.base import MarketDataProvider
from app.schemas.market_data import StockQuoteData, StockQuoteResponse


class QuoteService:
    """Service handling stock quote retrieval and normalization."""

    def __init__(self, provider: MarketDataProvider) -> None:
        self.provider = provider

    async def get_quote(
        self,
        symbol: str,
        exchange: Optional[str] = "NSE",
    ) -> StockQuoteResponse:
        """
        Retrieves normalized quote from provider, strictly preserving nulls without zero-filling.
        """
        clean_symbol = symbol.strip().upper()
        clean_exchange = (exchange or "NSE").strip().upper()

        raw_quote = await self.provider.get_quote(clean_symbol, clean_exchange)
        quote_data = StockQuoteData(**raw_quote)

        return StockQuoteResponse(success=True, data=quote_data)
