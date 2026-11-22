"""
Tests for RG AI API v1 Endpoints.
Covers endpoint contracts, status polling, cancellation, health, availability, and access control.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.services.rg_ai_service import get_rg_ai_service
from app.integrations.rg_ai.gpt_adapter import MockGPTAdapter


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


def test_submit_chat_prompt_success(client):
    response = client.post(
        "/api/v1/rg-ai/chat",
        json={"prompt": "Analyze NIFTY 50 intraday technical support."},
    )
    assert response.status_code == 202
    data = response.json()
    assert data["success"] is True
    assert data["request_id"].startswith("req_")
    assert data["status"] == "queued"
    assert "queue_position" in data


def test_submit_chat_prompt_validation_error(client):
    # Empty prompt must be rejected with 422
    response = client.post(
        "/api/v1/rg-ai/chat",
        json={"prompt": "   "},
    )
    assert response.status_code == 422


def test_get_request_status_not_found(client):
    response = client.get("/api/v1/rg-ai/status/req_nonexistent")
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "REQUEST_NOT_FOUND"


def test_get_request_status_success(client):
    # Submit first
    post_res = client.post(
        "/api/v1/rg-ai/chat",
        json={"prompt": "Analyze Bank Nifty key pivots."},
    )
    assert post_res.status_code == 202
    request_id = post_res.json()["request_id"]

    # Poll status
    get_res = client.get(f"/api/v1/rg-ai/status/{request_id}")
    assert get_res.status_code == 200
    status_data = get_res.json()
    assert status_data["request_id"] == request_id
    assert "status" in status_data
    assert "created_at" in status_data


def test_cancel_request_api(client):
    post_res = client.post(
        "/api/v1/rg-ai/chat",
        json={"prompt": "Analyze mid-cap momentum stocks."},
    )
    request_id = post_res.json()["request_id"]

    cancel_res = client.post(f"/api/v1/rg-ai/cancel/{request_id}")
    assert cancel_res.status_code == 200
    cancel_data = cancel_res.json()
    assert cancel_data["success"] is True
    assert cancel_data["request_id"] == request_id


def test_rg_ai_health_endpoint(client):
    response = client.get("/api/v1/rg-ai/health")
    assert response.status_code == 200
    data = response.json()
    assert "queue_size" in data
    assert "max_queue_size" in data
    assert "concurrency_limit" in data
    assert data["concurrency_limit"] == 1


def test_rg_ai_availability_endpoint(client):
    response = client.post("/api/v1/rg-ai/availability")
    assert response.status_code == 200
    data = response.json()
    assert "is_available" in data
    assert "is_browser_running" in data
    assert "login_state" in data
    assert "target_url" in data


def test_rg_ai_endpoints_reject_remote_clients():
    app = create_app()
    # Mock remote client IP
    remote_client = TestClient(app, client=("192.168.1.100", 54321))

    res_chat = remote_client.post("/api/v1/rg-ai/chat", json={"prompt": "Analyze test"})
    assert res_chat.status_code == 403

    res_status = remote_client.get("/api/v1/rg-ai/status/req_123")
    assert res_status.status_code == 403

    res_cancel = remote_client.post("/api/v1/rg-ai/cancel/req_123")
    assert res_cancel.status_code == 403

    res_health = remote_client.get("/api/v1/rg-ai/health")
    assert res_health.status_code == 403

    res_avail = remote_client.post("/api/v1/rg-ai/availability")
    assert res_avail.status_code == 403
