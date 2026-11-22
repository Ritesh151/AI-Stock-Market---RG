"""
Historical Data Service.
Validates chart timeframes and normalizes OHLCV price series.
"""

from typing import Optional
from app.integrations.market_data.base import MarketDataProvider
from app.integrations.market_data.exceptions import InvalidTimeframeError
from app.integrations.market_data.provider_config import (
    ALLOWED_INTERVALS_BY_RANGE,
    DEFAULT_INTERVAL_FOR_RANGE,
    SUPPORTED_CHART_INTERVALS,
    SUPPORTED_CHART_RANGES,
)
from app.schemas.market_data import HistoricalCandle, HistoricalDataResponse


class HistoricalDataService:
    """Service handling historical chart series and timeframe validation."""

    def __init__(self, provider: MarketDataProvider) -> None:
        self.provider = provider

    async def get_historical_data(
        self,
        symbol: str,
        range_str: str = "1M",
        interval: Optional[str] = None,
        exchange: Optional[str] = "NSE",
    ) -> HistoricalDataResponse:
        """
        Validates timeframe parameters and returns normalized historical candle data.
        """
        clean_symbol = symbol.strip().upper()
        clean_exchange = (exchange or "NSE").strip().upper()
        clean_range = range_str.strip().upper()

        if clean_range not in SUPPORTED_CHART_RANGES:
            raise InvalidTimeframeError(
                clean_range,
                interval or "default",
                list(SUPPORTED_CHART_RANGES),
                list(SUPPORTED_CHART_INTERVALS),
            )

        # Default interval if not specified
        clean_interval = (
            interval.strip().lower()
            if interval
            else DEFAULT_INTERVAL_FOR_RANGE.get(clean_range, "1d")
        )

        allowed_intervals = ALLOWED_INTERVALS_BY_RANGE.get(clean_range, set())
        if clean_interval not in allowed_intervals:
            raise InvalidTimeframeError(
                clean_range,
                clean_interval,
                list(SUPPORTED_CHART_RANGES),
                list(allowed_intervals),
            )

        raw_data = await self.provider.get_historical_data(
            symbol=clean_symbol,
            range_str=clean_range,
            interval=clean_interval,
            exchange=clean_exchange,
        )

        candles = [HistoricalCandle(**c) for c in raw_data.get("candles", [])]

        return HistoricalDataResponse(
            success=True,
            symbol=clean_symbol,
            exchange=clean_exchange,
            currency=raw_data.get("currency", "INR"),
            range=clean_range,
            interval=clean_interval,
            data_status=raw_data.get("data_status", "HISTORICAL"),
            source_name=raw_data.get("source_name"),
            fetched_at=raw_data.get("fetched_at", ""),
            candles=candles,
        )
