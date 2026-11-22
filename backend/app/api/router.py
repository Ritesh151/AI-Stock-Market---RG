"""
Main API Router.
Mounts root health checks and versioned sub-routers.
"""

from fastapi import APIRouter, Depends
from app.api.v1.router import v1_router
from app.schemas.health import HealthResponse
from app.services.health import HealthService

api_router = APIRouter()


def get_health_service() -> HealthService:
    return HealthService()


@api_router.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health Monitoring"],
    summary="Platform health status probe",
)
async def health_check(
    health_svc: HealthService = Depends(get_health_service),
) -> HealthResponse:
    """
    Root health monitoring endpoint.
    Conforms to the exact Phase 1 specification:
    {
      "success": true,
      "application": "RG AI",
      "status": "healthy"
    }
    """
    return await health_svc.get_health_status()


# Include versioned API routers
api_router.include_router(v1_router, prefix="/api")
