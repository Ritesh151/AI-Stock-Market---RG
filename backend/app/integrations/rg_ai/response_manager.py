"""
RG AI Response Manager.
Normalizes and formats integration and orchestration response payloads.
Never fabricates success responses.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class NormalizedResult(BaseModel):
    """Normalized payload of a validated integration result."""

    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    format_type: str = "text/plain"


class NormalizedError(BaseModel):
    """Normalized payload of an integration or orchestration failure."""

    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class ResponseManager:
    """Formats standardized API response dictionaries matching contract requirements."""

    @staticmethod
    def build_success_response(
        request_id: str,
        status: str,
        result: NormalizedResult,
        created_at: datetime,
        completed_at: datetime,
    ) -> Dict[str, Any]:
        """Builds a standardized success response payload."""
        return {
            "success": True,
            "request_id": request_id,
            "status": status,
            "result": {
                "content": result.content,
                "metadata": result.metadata,
                "format_type": result.format_type,
            },
            "created_at": created_at.isoformat(),
            "completed_at": completed_at.isoformat(),
        }

    @staticmethod
    def build_unavailable_response(
        request_id: str,
        code: str = "UNSUPPORTED_INTEGRATION",
        message: str = "The configured browser integration does not support this operation without unsupported scraping.",
        details: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Builds a standardized integration_unavailable response payload."""
        now = datetime.now(timezone.utc)
        return {
            "success": False,
            "request_id": request_id,
            "status": "integration_unavailable",
            "error": {
                "code": code,
                "message": message,
                "details": details,
            },
            "created_at": (created_at or now).isoformat(),
            "completed_at": (completed_at or now).isoformat(),
        }

    @staticmethod
    def build_error_response(
        request_id: str,
        status: str,
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Builds a standardized failure response payload."""
        now = datetime.now(timezone.utc)
        return {
            "success": False,
            "request_id": request_id,
            "status": status,
            "error": {
                "code": code,
                "message": message,
                "details": details,
            },
            "created_at": (created_at or now).isoformat(),
            "completed_at": (completed_at or now).isoformat(),
        }


_response_manager_instance: Optional[ResponseManager] = None


def get_response_manager() -> ResponseManager:
    """Returns singleton instance of ResponseManager."""
    global _response_manager_instance
    if _response_manager_instance is None:
        _response_manager_instance = ResponseManager()
    return _response_manager_instance
