"""
Unit and Integration Tests for Browser API Endpoints.
"""

from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.integrations.browser.browser_models import BrowserStatusResponse
from app.integrations.browser.browser_status import BrowserState, LoginState
from app.services.browser_service import BrowserService, get_browser_service


def test_get_browser_status_endpoint(client: TestClient):
    """Verify GET /api/v1/browser/status returns status structure."""
    response = client.get("/api/v1/browser/status")
    assert response.status_code == 200

    payload = response.json()
    assert "state" in payload
    assert "is_running" in payload
    assert "target_url" in payload
    assert payload["target_url"] == "https://chatgpt.com/g/g-jkxrUFNja-indian-stock-market"
    assert "login_status" in payload


def test_browser_start_stop_endpoints_with_mocked_service(app, client: TestClient):
    """Verify POST /api/v1/browser/start and stop endpoints using mocked service."""
    mock_service = AsyncMock(spec=BrowserService)

    mock_service.start_session.return_value = {
        "success": True,
        "message": "Persistent Chrome browser session launched successfully.",
        "state": BrowserState.RUNNING,
        "login_status": LoginState.UNKNOWN,
    }

    mock_service.stop_session.return_value = {
        "success": True,
        "message": "Browser session terminated cleanly and lock released.",
        "state": BrowserState.STOPPED,
        "login_status": LoginState.UNKNOWN,
    }

    mock_service.open_target_gpt.return_value = {
        "success": True,
        "message": "Target Custom GPT opened successfully.",
        "state": BrowserState.TARGET_OPEN,
        "login_status": LoginState.LOGIN_REQUIRED,
    }

    mock_service.confirm_manual_login.return_value = {
        "success": True,
        "message": "ChatGPT login confirmed and authenticated successfully.",
        "state": BrowserState.AUTHENTICATED,
        "login_status": LoginState.AUTHENTICATED,
    }

    app.dependency_overrides[get_browser_service] = lambda: mock_service

    try:
        # 1. Start browser
        start_res = client.post("/api/v1/browser/start")
        assert start_res.status_code == 200
        assert start_res.json()["success"] is True
        assert start_res.json()["state"] == "RUNNING"

        # 2. Open GPT
        open_res = client.post("/api/v1/browser/open-gpt")
        assert open_res.status_code == 200
        assert open_res.json()["state"] == "TARGET_OPEN"

        # 3. Confirm Login
        login_res = client.post("/api/v1/browser/confirm-login")
        assert login_res.status_code == 200
        assert login_res.json()["login_status"] == "AUTHENTICATED"

        # 4. Stop browser
        stop_res = client.post("/api/v1/browser/stop")
        assert stop_res.status_code == 200
        assert stop_res.json()["state"] == "STOPPED"

    finally:
        app.dependency_overrides.pop(get_browser_service, None)


def test_browser_endpoints_reject_remote_clients(app):
    """Verify security policy blocks requests from non-localhost clients."""
    with TestClient(app, base_url="http://192.168.1.50:8000") as remote_client:
        # Fake a remote IP
        headers = {"x-forwarded-for": "203.0.113.195"}
        # Note: in TestClient, the client.host is 'testclient', so let's test verify_local_access_policy directly
        from app.api.v1.browser import verify_local_access_policy
        from fastapi import HTTPException
        from unittest.mock import MagicMock

        remote_request = MagicMock()
        remote_request.client.host = "198.51.100.42"

        import pytest
        with pytest.raises(HTTPException) as exc_info:
            verify_local_access_policy(remote_request)
        assert exc_info.value.status_code == 403
