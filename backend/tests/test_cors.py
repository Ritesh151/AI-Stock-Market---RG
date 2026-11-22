"""
Unit tests for CORS headers and defensive security headers.
"""

from fastapi.testclient import TestClient


def test_cors_preflight_allowed_origin(client: TestClient):
    """
    Verify preflight request from allowed origin returns proper CORS headers.
    """
    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "GET",
    }
    response = client.options("/health", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_security_headers_present(client: TestClient):
    """
    Verify defensive security headers are appended to responses.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers.get("x-content-type-options") == "nosniff"
    assert response.headers.get("x-frame-options") == "DENY"
    assert response.headers.get("referrer-policy") == "strict-origin-when-cross-origin"
