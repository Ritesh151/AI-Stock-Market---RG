"""
Unit Tests for RG AI Response Normalizer.
Verifies canonical ResponseEnvelope packaging, timestamp ISO 8601 formatting, and error envelopes.
"""

from datetime import datetime, timezone
import pytest
from app.services.response_normalizer import ResponseNormalizer


@pytest.fixture
def normalizer():
    return ResponseNormalizer()


def test_normalize_success_envelope(normalizer):
    data = {
        "stock_name": "ITC Limited",
        "symbol": "ITC",
        "current_price": 472.30,
        "recommendation": "ACCUMULATE",
        "target_price": None,  # Must remain None
        "created_at": datetime(2026, 11, 17, 6, 30, 0, tzinfo=timezone.utc),
    }
    warnings = ["Quote timestamp missing"]

    envelope = normalizer.normalize_success(
        schema_type="stock_analysis",
        validated_data=data,
        request_id="req_test_123",
        warnings=warnings,
    )

    dumped = envelope.model_dump()
    assert dumped["success"] is True
    assert dumped["type"] == "stock_analysis"
    assert dumped["schema_version"] == "1.0"
    assert dumped["request_id"] == "req_test_123"
    assert dumped["data"]["symbol"] == "ITC"
    assert dumped["data"]["current_price"] == 472.30
    assert dumped["data"]["target_price"] is None
    assert dumped["data"]["created_at"] == "2026-11-17T06:30:00+00:00"
    assert dumped["warnings"] == warnings
    assert "Informational research only" in dumped["disclaimer"]


def test_normalize_error_envelope_invalid_json(normalizer):
    err_envelope = normalizer.normalize_error(
        code="INVALID_JSON",
        message="The response is not valid JSON.",
        request_id="req_err_1",
    )
    dumped = err_envelope.model_dump()
    assert dumped["success"] is False
    assert dumped["type"] == "validation_error"
    assert dumped["request_id"] == "req_err_1"
    assert dumped["error"]["code"] == "INVALID_JSON"
    assert dumped["error"]["message"] == "The response is not valid JSON."


def test_normalize_error_envelope_schema_mismatch(normalizer):
    from app.schemas.response_envelope import ValidationErrorDetail

    details = [ValidationErrorDetail(field="symbol", issue="Field required")]
    err_envelope = normalizer.normalize_error(
        code="SCHEMA_VALIDATION_FAILED",
        message="The response does not match the expected schema.",
        request_id="req_err_2",
        details=details,
    )
    dumped = err_envelope.model_dump()
    assert dumped["success"] is False
    assert dumped["error"]["code"] == "SCHEMA_VALIDATION_FAILED"
    assert len(dumped["error"]["details"]) == 1
    assert dumped["error"]["details"][0]["field"] == "symbol"
