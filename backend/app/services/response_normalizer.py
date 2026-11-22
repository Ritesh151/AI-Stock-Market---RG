"""
Response Normalizer for RG AI.
Constructs canonical ResponseEnvelope instances from validated data.
Preserves nulls, numeric precision, and attaches warnings and disclaimers.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from app.core.validation_config import DEFAULT_SCHEMA_VERSION, STANDARD_FINANCIAL_DISCLAIMER
from app.schemas.response_envelope import (
    ResponseEnvelope,
    ValidationErrorDetail,
    ValidationErrorEnvelope,
    ValidationErrorPayload,
)
from app.core.logging import get_logger

logger = get_logger("services.response_normalizer")


class ResponseNormalizer:
    """Normalizes validated outputs into authoritative API response envelopes."""

    def __init__(self, schema_version: str = DEFAULT_SCHEMA_VERSION) -> None:
        self.schema_version = schema_version

    def normalize_success(
        self,
        schema_type: str,
        validated_data: Dict[str, Any],
        request_id: str,
        warnings: Optional[List[str]] = None,
        disclaimer: str = STANDARD_FINANCIAL_DISCLAIMER,
    ) -> ResponseEnvelope:
        """
        Builds a canonical ResponseEnvelope.
        Normalizes timestamps to ISO 8601 while preserving precision and nulls.
        """
        normalized_data = self._deep_normalize_dict(validated_data)

        envelope = ResponseEnvelope(
            success=True,
            type=schema_type,
            schema_version=self.schema_version,
            request_id=request_id,
            data=normalized_data,
            warnings=warnings if warnings else None,
            disclaimer=disclaimer,
        )
        return envelope

    def normalize_error(
        self,
        code: str,
        message: str,
        request_id: Optional[str] = None,
        details: Optional[List[ValidationErrorDetail]] = None,
    ) -> ValidationErrorEnvelope:
        """Constructs a canonical ValidationErrorEnvelope."""
        return ValidationErrorEnvelope(
            success=False,
            type="validation_error",
            request_id=request_id,
            error=ValidationErrorPayload(
                code=code,
                message=message,
                details=details,
            ),
        )

    def _deep_normalize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively normalizes dictionary values, formatting timestamps and preserving nulls."""
        cleaned: Dict[str, Any] = {}
        for k, v in data.items():
            if isinstance(v, dict):
                cleaned[k] = self._deep_normalize_dict(v)
            elif isinstance(v, list):
                cleaned[k] = [
                    self._deep_normalize_dict(item) if isinstance(item, dict) else item
                    for item in v
                ]
            elif isinstance(v, datetime):
                # Ensure UTC and ISO 8601 format
                if v.tzinfo is None:
                    v = v.replace(tzinfo=timezone.utc)
                cleaned[k] = v.isoformat()
            else:
                cleaned[k] = v
        return cleaned


_response_normalizer_instance: Optional[ResponseNormalizer] = None


def get_response_normalizer() -> ResponseNormalizer:
    """Returns singleton instance of ResponseNormalizer."""
    global _response_normalizer_instance
    if _response_normalizer_instance is None:
        _response_normalizer_instance = ResponseNormalizer()
    return _response_normalizer_instance
