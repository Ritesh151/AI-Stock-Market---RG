"""
Stocks API Endpoints (API v1).
Handles stock search, quotes, historical charts, company profiles, and watchlist management.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, Path, status
from app.schemas.market_data import (
    CompanyProfileResponse,
    HistoricalDataResponse,
    StockQuoteResponse,
    StockSearchResponse,
    WatchlistResponse,
)
from app.services.market_data_service import MarketDataService, get_market_data_service

router = APIRouter(prefix="/stocks", tags=["Stock Market Price Tracking"])


@router.get(
    "/search",
    response_model=StockSearchResponse,
    summary="Search listed Indian stocks by company name or symbol",
)
async def search_stocks(
    q: str = Query(..., min_length=1, max_length=100, description="Search query string"),
    exchange: Optional[str] = Query(None, description="Optional exchange filter (NSE or BSE)"),
    service: MarketDataService = Depends(get_market_data_service),
) -> StockSearchResponse:
    """
    Searches listed stocks across symbol tickers and company names.
    Returns deduplicated results matching query.
    """
    return await service.search_stocks(query=q, exchange=exchange)


@router.get(
    "/watchlist",
    response_model=WatchlistResponse,
    summary="Get user stock watchlist",
)
async def get_watchlist(
    q: Optional[str] = Query(None, description="Optional search filter for watchlist"),
    sort_by: Optional[str] = Query(
        None,
        description="Optional sorting ('name', 'price_change', or 'change_percent')",
    ),
    service: MarketDataService = Depends(get_market_data_service),
) -> WatchlistResponse:
    """
    Returns current user watchlist with real-time quotes and sorting.
    """
    return await service.get_watchlist(search_query=q, sort_by=sort_by)


@router.post(
    "/watchlist/{symbol}",
    response_model=WatchlistResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a stock symbol to user watchlist",
)
async def add_to_watchlist(
    symbol: str = Path(..., min_length=1, max_length=20, description="Stock trading symbol"),
    exchange: Optional[str] = Query("NSE", description="Exchange identifier (NSE or BSE)"),
    service: MarketDataService = Depends(get_market_data_service),
) -> WatchlistResponse:
    """
    Adds equity symbol to watchlist with duplicate prevention.
    """
    return await service.add_to_watchlist(symbol=symbol, exchange=exchange)


@router.delete(
    "/watchlist/{symbol}",
    response_model=WatchlistResponse,
    summary="Remove a stock symbol from user watchlist",
)
async def remove_from_watchlist(
    symbol: str = Path(..., min_length=1, max_length=20, description="Stock trading symbol"),
    service: MarketDataService = Depends(get_market_data_service),
) -> WatchlistResponse:
    """
    Removes equity symbol from user watchlist.
    """
    return await service.remove_from_watchlist(symbol=symbol)


@router.get(
    "/{symbol}/quote",
    response_model=StockQuoteResponse,
    summary="Get normalized stock quote for symbol",
)
@router.get(
    "/quote/{symbol}",
    response_model=StockQuoteResponse,
    include_in_schema=False,
)
async def get_stock_quote(
    symbol: str = Path(..., min_length=1, max_length=20, description="Stock trading symbol (e.g., TCS, RELIANCE)"),
    exchange: Optional[str] = Query("NSE", description="Trading exchange (NSE or BSE)"),
    service: MarketDataService = Depends(get_market_data_service),
) -> StockQuoteResponse:
    """
    Returns real-time or delayed stock quote adhering to Section 6 schema.
    Strictly preserves null values for unavailable fields.
    """
    return await service.get_quote(symbol=symbol, exchange=exchange)


@router.get(
    "/{symbol}/history",
    response_model=HistoricalDataResponse,
    summary="Get historical price chart candle series",
)
@router.get(
    "/history/{symbol}",
    response_model=HistoricalDataResponse,
    include_in_schema=False,
)
async def get_stock_history(
    symbol: str = Path(..., min_length=1, max_length=20, description="Stock trading symbol"),
    range: str = Query("1M", description="Chart time range (1D, 5D, 1M, 3M, 6M, 1Y, 5Y)"),
    interval: Optional[str] = Query(None, description="Candle interval (1m, 5m, 15m, 1h, 1d, 1wk)"),
    exchange: Optional[str] = Query("NSE", description="Trading exchange (NSE or BSE)"),
    service: MarketDataService = Depends(get_market_data_service),
) -> HistoricalDataResponse:
    """
    Returns normalized OHLCV candlestick series for target equity.
    """
    return await service.get_historical_data(
        symbol=symbol,
        range_str=range,
        interval=interval,
        exchange=exchange,
    )


@router.get(
    "/{symbol}/profile",
    response_model=CompanyProfileResponse,
    summary="Get company profile and fundamental stats",
)
@router.get(
    "/profile/{symbol}",
    response_model=CompanyProfileResponse,
    include_in_schema=False,
)
async def get_company_profile(
    symbol: str = Path(..., min_length=1, max_length=20, description="Stock trading symbol"),
    exchange: Optional[str] = Query("NSE", description="Trading exchange (NSE or BSE)"),
    service: MarketDataService = Depends(get_market_data_service),
) -> CompanyProfileResponse:
    """
    Returns company background, sector, industry, and fundamental stats.
    """
    return await service.get_company_profile(symbol=symbol, exchange=exchange)
