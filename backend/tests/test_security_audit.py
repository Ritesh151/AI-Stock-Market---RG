"""
Security Audit and Hardening Automated Tests for RG AI (Phase 11).
Tests HTTP security headers, request size limits, rate limiting, NoSQL injection prevention,
production invariants, error concealment, and network access boundaries.
"""

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.core.security import InMemoryRateLimiter, SecurityHeadersMiddleware, RequestSizeLimitMiddleware
from app.main import create_app
from app.repositories.base import sanitize_filter



# =====================================================================
# 1. HTTP Security Headers
# =====================================================================

def test_defensive_http_security_headers(client: TestClient):
    """Verify that all responses include defensive security headers."""
    response = client.get("/health")
    assert response.status_code == 200

    headers = response.headers
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("X-XSS-Protection") == "1; mode=block"
    assert headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "geolocation=()" in headers.get("Permissions-Policy", "")


# =====================================================================
# 2. Request Size Limits (DoS / Payload Exhaustion)
# =====================================================================

def test_request_payload_size_limit():
    """Verify that payloads exceeding configured maximum size are rejected with HTTP 413."""
    test_settings = Settings(APP_ENV="test")
    app = create_app(settings=test_settings)

    with TestClient(app) as test_client:
        # Normal payload under limit
        normal_res = test_client.post(
            "/api/v1/conversations?user_id=test_size_user",
            json={"title": "Small Title"},
        )
        assert normal_res.status_code == 201

        # Excessively large payload exceeding 2MB threshold
        large_body = "A" * (3 * 1024 * 1024)  # 3 MB
        oversized_res = test_client.post(
            "/api/v1/conversations?user_id=test_size_user",
            content=large_body,
            headers={"Content-Type": "application/json", "Content-Length": str(len(large_body))},
        )
        assert oversized_res.status_code == 413
        assert oversized_res.json()["error"]["code"] == "PAYLOAD_TOO_LARGE"


# =====================================================================
# 3. Rate Limiting
# =====================================================================

def test_in_memory_rate_limiter():
    """Verify that sliding-window rate limiter throttles clients exceeding max_requests."""
    limiter = InMemoryRateLimiter(max_requests=5, window_seconds=60)
    client_ip = "192.168.1.100"

    # First 5 requests must pass
    for i in range(5):
        is_limited, remaining = limiter.is_rate_limited(client_ip)
        assert is_limited is False
        assert remaining == 4 - i

    # 6th request must be rate limited
    is_limited, remaining = limiter.is_rate_limited(client_ip)
    assert is_limited is True
    assert remaining == 0

    # Separate IP must have independent quota
    other_limited, other_remaining = limiter.is_rate_limited("192.168.1.101")
    assert other_limited is False
    assert other_remaining == 4


# =====================================================================
# 4. NoSQL Operator Injection Sanitization
# =====================================================================

def test_nosql_injection_sanitization():
    """Verify that dangerous MongoDB operators and script execution keys are stripped."""
    malicious_query = {
        "user_id": "normal_trader",
        "$where": "this.password == 'secret'",
        "$function": "function() { return true; }",
        "$expr": {"$gt": ["$balance", 0]},
        "nested": {
            "$accumulator": "...",
            "safe_field": 123,
        },
        "query\x00nullbyte": "exploit",
    }

    sanitized = sanitize_filter(malicious_query)

    assert "user_id" in sanitized
    assert sanitized["user_id"] == "normal_trader"
    assert "$where" not in sanitized
    assert "$function" not in sanitized
    assert "$expr" not in sanitized
    assert "query\x00nullbyte" not in sanitized
    assert "$accumulator" not in sanitized["nested"]
    assert sanitized["nested"]["safe_field"] == 123


# =====================================================================
# 5. Production Environment Invariants
# =====================================================================

def test_production_cors_invariants():
    """Verify that wildcard CORS is strictly rejected in production mode."""
    with pytest.raises(ValueError, match="Wildcard '\\*' CORS origins are forbidden"):
        Settings(
            APP_ENV="production",
            CORS_ORIGINS=["*"],
            MONGODB_URI="mongodb://production-cluster:27017",
        )


def test_production_mongodb_uri_invariant():
    """Verify that empty MONGODB_URI is strictly rejected in production mode."""
    with pytest.raises(ValueError, match="MONGODB_URI must be configured for production"):
        Settings(
            APP_ENV="production",
            CORS_ORIGINS=["https://rgai.in"],
            MONGODB_URI="",
        )


# =====================================================================
# 6. Error Concealment & Secret Protection
# =====================================================================

def test_generic_exception_conceals_stack_trace():
    """Verify that unhandled internal server exceptions do not leak stack traces or file paths."""
    from fastapi import APIRouter
    from app.core.exceptions import AppException
    from app.core.handlers import generic_exception_handler

    test_settings = Settings(APP_ENV="test")
    app = create_app(settings=test_settings)

    # Route that deliberately raises an unexpected internal runtime error
    @app.get("/test-internal-error")
    async def deliberate_crash():
        raise RuntimeError("SecretDatabasePassword@123 at /var/www/internal/db.py line 42")

    with TestClient(app, raise_server_exceptions=False) as test_client:
        res = test_client.get("/test-internal-error")
        assert res.status_code == 500
        data = res.json()
        assert data["success"] is False
        assert data["error"]["code"] == "INTERNAL_SERVER_ERROR"
        # Secret string and file path must NEVER be present in response
        assert "SecretDatabasePassword" not in res.text
        assert "/var/www" not in res.text


# =====================================================================
# 7. Local-Only Network Boundary Policy
# =====================================================================

def test_browser_endpoint_rejects_external_hosts():
    """Verify that sensitive browser management endpoints reject remote non-loopback clients."""
    test_settings = Settings(APP_ENV="test")
    app = create_app(settings=test_settings)

    # TestClient by default identifies as "testclient", which is allowed.
    # We simulate a request from an external non-loopback host (e.g., 203.0.113.195).
    with TestClient(app, client=("203.0.113.195", 54321)) as test_client:
        res = test_client.post("/api/v1/browser/start")
        body = res.json()
        error_msg = body.get("error", {}).get("message") or body.get("detail", "")
        assert "restricted to local host" in error_msg

        res_rg = test_client.post("/api/v1/rg-ai/chat", json={"prompt": "Analyze TCS"})
        assert res_rg.status_code == 403
