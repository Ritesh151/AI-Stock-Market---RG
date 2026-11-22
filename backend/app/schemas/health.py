"""
Health Check Schemas.
"""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """
    Schema for GET /health endpoint.
    Strictly conforms to platform specification:
    {
      "success": true,
      "application": "RG AI",
      "status": "healthy"
    }
    """

    success: bool = Field(default=True, description="Indicates operational success")
    application: str = Field(default="RG AI", description="Application identifier")
    status: str = Field(default="healthy", description="Current operational status")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "application": "RG AI",
                "status": "healthy",
            }
        }
    }
