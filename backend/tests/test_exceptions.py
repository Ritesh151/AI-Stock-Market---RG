"""
Unit tests for Centralized Exception Handling and Secret Shielding.
"""

from fastapi import APIRouter
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

from app.core.exceptions import AppException, NotFoundException
from app.main import create_app
from app.core.config import Settings


def test_404_not_found_handling(client: TestClient):
    """
    Verify nonexistent routes return standardized JSON error envelope.
    """
    response = client.get("/nonexistent-endpoint-path")
    assert response.status_code == 404

    payload = response.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "NOT_FOUND"
    assert "Not Found" in payload["error"]["message"]


def test_custom_app_exception_handling():
    """
    Verify AppException is mapped correctly to HTTP status and JSON response.
    """
    settings = Settings(APP_ENV="test", LOG_LEVEL="CRITICAL")
    test_app = create_app(settings=settings)
    test_router = APIRouter()

    @test_router.get("/test-custom-error")
    def trigger_error():
        raise NotFoundException(message="Requested stock symbol not found.")

    test_app.include_router(test_router)

    with TestClient(test_app, raise_server_exceptions=False) as client:
        response = client.get("/test-custom-error")
        assert response.status_code == 404
        payload = response.json()
        assert payload["success"] is False
        assert payload["error"]["code"] == "NOT_FOUND"
        assert payload["error"]["message"] == "Requested stock symbol not found."


def test_validation_error_handling():
    """
    Verify Pydantic validation failure returns HTTP 422 with standardized error envelope.
    """
    settings = Settings(APP_ENV="test", LOG_LEVEL="CRITICAL")
    test_app = create_app(settings=settings)
    test_router = APIRouter()

    class ItemPayload(BaseModel):
        symbol: str = Field(..., min_length=1)
        price: float = Field(..., gt=0)

    @test_router.post("/test-validation")
    def validate_item(payload: ItemPayload):
        return {"status": "ok"}

    test_app.include_router(test_router)

    with TestClient(test_app, raise_server_exceptions=False) as client:
        response = client.post("/test-validation", json={"symbol": "", "price": -5})
        assert response.status_code == 422
        payload = response.json()
        assert payload["success"] is False
        assert payload["error"]["code"] == "VALIDATION_ERROR"
        assert isinstance(payload["error"]["details"], list)
        assert len(payload["error"]["details"]) > 0


def test_unhandled_exception_does_not_leak_internals():
    """
    Verify unexpected server exceptions return 500 without leaking stack traces or internal secrets.
    """
    settings = Settings(APP_ENV="test", LOG_LEVEL="CRITICAL")
    test_app = create_app(settings=settings)
    test_router = APIRouter()

    @test_router.get("/test-unhandled")
    def trigger_unhandled():
        # Raise unexpected error with sensitive connection string
        raise RuntimeError("Database connection string leaked: mongodb://admin:supersecret@db:27017")

    test_app.include_router(test_router)

    with TestClient(test_app, raise_server_exceptions=False) as client:
        response = client.get("/test-unhandled")
        assert response.status_code == 500
        payload = response.json()
        assert payload["success"] is False
        assert payload["error"]["code"] == "INTERNAL_SERVER_ERROR"
        # Ensure raw exception message and secrets are not in client response
        assert "supersecret" not in response.text
        assert "mongodb://" not in response.text
        assert "RuntimeError" not in response.text
        assert "Traceback" not in response.text
