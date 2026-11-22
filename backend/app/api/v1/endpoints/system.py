"""
System and Diagnostic endpoints for API v1.
"""

from typing import Any, Dict
from fastapi import APIRouter, Depends
from app.core.config import Settings, get_settings
from app.schemas.common import ApiResponse, ErrorPayload
from app.schemas.persistence import DatabaseHealthResponse
from app.utils.datetime import iso_now

router = APIRouter()



@router.get("/ping", response_model=ApiResponse[Dict[str, Any]])
@router.get("/health", response_model=ApiResponse[Dict[str, Any]])
async def ping(
    settings: Settings = Depends(get_settings),
) -> ApiResponse[Dict[str, Any]]:
    """
    Connectivity ping endpoint within the versioned API router.
    """
    return ApiResponse(
        success=True,
        data={
            "application": settings.APP_NAME,
            "version": "1.0.0",
            "environment": settings.APP_ENV,
            "timestamp": iso_now(),
        },
    )


@router.get("/database-health", response_model=ApiResponse[DatabaseHealthResponse])
@router.get("/system/database-health", response_model=ApiResponse[DatabaseHealthResponse])
async def get_database_health() -> ApiResponse[DatabaseHealthResponse]:

    """
    Returns connection health and latency metrics for the MongoDB persistence tier.
    Gracefully returns 'disconnected' if MongoDB is unavailable without crashing.
    """
    from app.core.database import database_manager
    ping_result = await database_manager.ping()
    health_data = DatabaseHealthResponse(
        status=ping_result["status"],
        database=ping_result["database"],
        latency_ms=ping_result["latency_ms"],
        message=ping_result["message"],
    )
    return ApiResponse(
        success=health_data.status == "connected",
        data=health_data,
        error=None
        if health_data.status == "connected"
        else ErrorPayload(
            code="DATABASE_DISCONNECTED",
            message=health_data.message or "Database client is not connected.",
        ),
    )

