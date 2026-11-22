"""
Unit and integration tests for Health check and System endpoints.
"""

from fastapi.testclient import TestClient


def test_health_endpoint_success(client: TestClient):
    """
    Verify GET /health returns 200 and exact required schema:
    {
      "success": true,
      "application": "RG AI",
      "status": "healthy"
    }
    """
    response = client.get("/health")
    assert response.status_code == 200

    payload = response.json()
    assert payload == {
        "success": True,
        "application": "RG AI",
        "status": "healthy",
    }
    assert payload["success"] is True
    assert payload["application"] == "RG AI"
    assert payload["status"] == "healthy"


def test_api_v1_ping_endpoint(client: TestClient):
    """
    Verify GET /api/v1/ping returns 200 with standard ApiResponse envelope.
    """
    response = client.get("/api/v1/ping")
    assert response.status_code == 200

    payload = response.json()
    assert payload["success"] is True
    assert "data" in payload
    assert payload["data"]["application"] == "RG AI"
    assert payload["data"]["version"] == "1.0.0"
    assert payload["data"]["environment"] == "test"
    assert "timestamp" in payload["data"]
