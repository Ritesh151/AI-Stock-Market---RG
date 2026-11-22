"""
Market Data Exceptions.
Centralized exception hierarchy for market data integration errors.
"""

from typing import Any, Dict, Optional
from app.core.exceptions import AppException


class MarketDataException(AppException):
    """Base exception for all market data integration errors."""

    def __init__(
        self,
        message: str,
        code: str = "MARKET_DATA_ERROR",
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 502,
    ) -> None:
        super().__init__(message=message, code=code, details=details, status_code=status_code)


class StockNotFoundError(MarketDataException):
    """Raised when the requested stock symbol cannot be found on the target exchange."""

    def __init__(
        self,
        symbol: str,
        exchange: Optional[str] = None,
        message: Optional[str] = None,
    ) -> None:
        msg = message or f"Stock symbol '{symbol}' was not found on exchange '{exchange or 'NSE/BSE'}'."
        super().__init__(
            message=msg,
            code="STOCK_NOT_FOUND",
            details={"symbol": symbol, "exchange": exchange},
            status_code=404,
        )


class ProviderUnavailableError(MarketDataException):
    """Raised when the market data provider fails to respond or is unreachable."""

    def __init__(
        self,
        provider_name: str,
        message: Optional[str] = None,
    ) -> None:
        msg = message or f"Market data provider '{provider_name}' is temporarily unavailable."
        super().__init__(
            message=msg,
            code="PROVIDER_UNAVAILABLE",
            details={"provider": provider_name},
            status_code=503,
        )


class RateLimitExceededError(MarketDataException):
    """Raised when the market data provider rate limit is encountered."""

    def __init__(
        self,
        provider_name: str,
        retry_after: Optional[int] = None,
        message: Optional[str] = None,
    ) -> None:
        msg = message or f"Rate limit exceeded for provider '{provider_name}'."
        super().__init__(
            message=msg,
            code="RATE_LIMIT_EXCEEDED",
            details={"provider": provider_name, "retry_after": retry_after},
            status_code=429,
        )


class InvalidTimeframeError(MarketDataException):
    """Raised when an unsupported range or interval combination is requested."""

    def __init__(
        self,
        range_str: str,
        interval: str,
        supported_ranges: Optional[list] = None,
        supported_intervals: Optional[list] = None,
    ) -> None:
        super().__init__(
            message=f"Invalid range '{range_str}' or interval '{interval}'.",
            code="INVALID_TIMEFRAME",
            details={
                "range": range_str,
                "interval": interval,
                "supported_ranges": supported_ranges,
                "supported_intervals": supported_intervals,
            },
            status_code=400,
        )
