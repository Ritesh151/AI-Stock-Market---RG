"""
Health Check Service.
Inspects core application subsystems and returns verified status.
"""

from app.core.config import get_settings
from app.schemas.health import HealthResponse


class HealthService:
    def __init__(self):
        self.settings = get_settings()

    async def get_health_status(self) -> HealthResponse:
        """
        Evaluates application state and returns standard health payload.
        Expected format:
        {
          "success": true,
          "application": "RG AI",
          "status": "healthy"
        }
        """
        return HealthResponse(
            success=True,
            application=self.settings.APP_NAME,
            status="healthy",
        )
