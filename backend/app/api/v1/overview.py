"""
Overview Dashboard API Endpoints (API v1).
Provides aggregated Indian stock market intelligence, benchmark indices,
market sentiment, top movers, market status, and news.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.schemas.market_data import MarketStatusResponse
from app.schemas.overview import (
    MarketIndexOverviewItem,
    MarketMoversData,
    MarketNewsData,
    MarketOverviewResponse,
    MarketSentimentData,
)
from app.services.overview_service import OverviewService, get_overview_service

router = APIRouter(prefix="/overview", tags=["Market Overview & Intelligence"])


@router.get(
    "",
    response_model=MarketOverviewResponse,
    summary="Get aggregated Indian stock market intelligence dashboard",
)
async def get_overview(
    exchange: Optional[str] = Query("NSE", description="Primary exchange (NSE or BSE)"),
    service: OverviewService = Depends(get_overview_service),
) -> MarketOverviewResponse:
    """
    Returns full aggregated overview payload: indices with sparklines,
    quantitative market sentiment, top movers, market status, and curated news.
    Resilient to partial provider failures.
    """
    return await service.get_overview(exchange=exchange or "NSE")


@router.get(
    "/indices",
    response_model=List[MarketIndexOverviewItem],
    summary="Get benchmark indices with sparklines and session stats",
)
async def get_overview_indices(
    service: OverviewService = Depends(get_overview_service),
) -> List[MarketIndexOverviewItem]:
    """
    Retrieves NIFTY 50, SENSEX, BANK NIFTY, and INDIA VIX with session stats and sparkline series.
    """
    return await service.get_indices_overview()


@router.get(
    "/sentiment",
    response_model=MarketSentimentData,
    summary="Get calculated Indian stock market sentiment",
)
async def get_overview_sentiment(
    exchange: Optional[str] = Query("NSE", description="Exchange (NSE or BSE)"),
    service: OverviewService = Depends(get_overview_service),
) -> MarketSentimentData:
    """
    Retrieves composite market sentiment, including momentum, VIX volatility, and breadth.
    """
    overview = await service.get_overview(exchange=exchange or "NSE")
    return overview.sentiment


@router.get(
    "/movers",
    response_model=MarketMoversData,
    summary="Get top gainers, top losers, and most active stocks",
)
async def get_overview_movers(
    exchange: Optional[str] = Query("NSE", description="Exchange (NSE or BSE)"),
    service: OverviewService = Depends(get_overview_service),
) -> MarketMoversData:
    """
    Retrieves top 5 positive movers, top 5 negative movers, and top 5 most active stocks.
    """
    return await service.get_movers(exchange=exchange or "NSE")


@router.get(
    "/market-status",
    response_model=MarketStatusResponse,
    summary="Get Indian market session and IST operating hours",
)
async def get_overview_market_status(
    exchange: Optional[str] = Query("NSE", description="Exchange (NSE or BSE)"),
    service: OverviewService = Depends(get_overview_service),
) -> MarketStatusResponse:
    """
    Retrieves current trading state (OPEN, CLOSED), session description, and IST market hours.
    """
    raw_status = await service.provider.get_market_status(exchange or "NSE")
    return MarketStatusResponse(**raw_status)


@router.get(
    "/news",
    response_model=MarketNewsData,
    summary="Get live Indian market news feed",
)
async def get_overview_news(
    service: OverviewService = Depends(get_overview_service),
) -> MarketNewsData:
    """
    Retrieves legitimate Indian market news articles or explicit unavailable status.
    """
    return await service.get_news()
