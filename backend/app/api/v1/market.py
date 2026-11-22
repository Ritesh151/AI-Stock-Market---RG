"""
Market API Endpoints (API v1).
Provides market open/closed session status and major benchmark indices.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from app.schemas.market_data import MarketIndicesResponse, MarketStatusResponse
from app.services.market_data_service import MarketDataService, get_market_data_service

router = APIRouter(prefix="/market", tags=["Market Overview & Indices"])


@router.get(
    "/status",
    response_model=MarketStatusResponse,
    summary="Get current Indian market trading session status",
)
async def get_market_status(
    exchange: Optional[str] = Query("NSE", description="Exchange identifier (NSE or BSE)"),
    service: MarketDataService = Depends(get_market_data_service),
) -> MarketStatusResponse:
    """
    Returns current trading state (OPEN, CLOSED), session description, and current UTC time.
    """
    return await service.get_market_status(exchange=exchange)


@router.get(
    "/indices",
    response_model=MarketIndicesResponse,
    summary="Get key Indian benchmark indices (NIFTY 50, SENSEX, BANK NIFTY, INDIA VIX)",
)
async def get_market_indices(
    service: MarketDataService = Depends(get_market_data_service),
) -> MarketIndicesResponse:
    """
    Retrieves latest values, session changes, and freshness for major benchmark indices.
    """
    return await service.get_market_indices()
