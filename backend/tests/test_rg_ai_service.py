"""
Tests for Prompt Validation and RG AI Service Orchestration.
Covers input sanitization, length boundaries, adapter routing, and honest integration limitation handling.
"""

import asyncio
import pytest
from app.integrations.browser.browser_status import LoginState
from app.integrations.rg_ai.automation_service import AutomationService
from app.integrations.rg_ai.gpt_adapter import BrowserGPTAdapter, MockGPTAdapter
from app.integrations.rg_ai.prompt_manager import PromptManager
from app.schemas.rg_ai import ChatPromptRequest, RequestStatus
from app.services.request_manager import RequestManager
from app.services.rg_ai_service import RgAiService
from app.core.exceptions import AppException


def test_prompt_validation_empty_and_whitespace():
    pm = PromptManager()

    with pytest.raises(AppException) as exc:
        pm.validate_and_prepare("   ")
    assert exc.value.code == "EMPTY_PROMPT"

    with pytest.raises(AppException) as exc:
        pm.validate_and_prepare("a")
    assert exc.value.code == "PROMPT_TOO_SHORT"


def test_prompt_validation_maximum_length():
    pm = PromptManager()
    long_prompt = "x" * 4001

    with pytest.raises(AppException) as exc:
        pm.validate_and_prepare(long_prompt)
    assert exc.value.code == "PROMPT_TOO_LONG"


def test_metadata_sanitization_removes_suspicious_patterns():
    pm = PromptManager()
    metadata = {
        "valid_key": "nifty_50",
        "suspicious_file": "file:///etc/passwd",
        "suspicious_chrome": "chrome://version",
    }
    prepared = pm.validate_and_prepare("Analyze market breadth", metadata=metadata)
    assert "valid_key" in prepared.metadata
    assert "suspicious_file" not in prepared.metadata
    assert "suspicious_chrome" not in prepared.metadata


@pytest.mark.asyncio
async def test_service_orchestration_integration_unavailable():
    # Configure mock adapter to simulate unsupported integration
    unsupported_adapter = MockGPTAdapter(simulate_unsupported=True)
    automation_svc = AutomationService(adapter=unsupported_adapter)
    manager = RequestManager(
        queue_size=5,
        request_timeout_seconds=2,
        concurrency=1,
        automation_service=automation_svc,
    )
    service = RgAiService(
        request_manager=manager,
        automation_service=automation_svc,
    )

    await manager.start()
    try:
        req = ChatPromptRequest(prompt="What is NIFTY support?")
        submission = await service.submit_prompt(req)
        assert submission.success is True
        assert submission.status == RequestStatus.QUEUED

        for _ in range(40):
            status = await service.get_request_status(submission.request_id)
            if status.status in {
                RequestStatus.COMPLETED,
                RequestStatus.FAILED,
                RequestStatus.INTEGRATION_UNAVAILABLE,
            }:
                break
            await asyncio.sleep(0.05)

        final_status = await service.get_request_status(submission.request_id)
        assert final_status.status == RequestStatus.INTEGRATION_UNAVAILABLE
        assert final_status.error is not None
        assert final_status.error["code"] == "UNSUPPORTED_INTEGRATION"
        assert final_status.result is None  # Never fabricate success
    finally:
        await manager.shutdown()


@pytest.mark.asyncio
async def test_service_orchestration_login_required():
    login_req_adapter = MockGPTAdapter(simulate_login_required=True)
    automation_svc = AutomationService(adapter=login_req_adapter)
    manager = RequestManager(
        queue_size=5,
        request_timeout_seconds=2,
        concurrency=1,
        automation_service=automation_svc,
    )
    service = RgAiService(
        request_manager=manager,
        automation_service=automation_svc,
    )

    await manager.start()
    try:
        req = ChatPromptRequest(prompt="Analyze HDFC Bank technical levels")
        submission = await service.submit_prompt(req)

        for _ in range(40):
            status = await service.get_request_status(submission.request_id)
            if status.status in {RequestStatus.COMPLETED, RequestStatus.FAILED}:
                break
            await asyncio.sleep(0.05)

        final_status = await service.get_request_status(submission.request_id)
        assert final_status.status == RequestStatus.FAILED
        assert final_status.error is not None
        assert final_status.error["code"] == "LOGIN_REQUIRED"
    finally:
        await manager.shutdown()


@pytest.mark.asyncio
async def test_service_orchestration_browser_unavailable():
    down_adapter = MockGPTAdapter(simulate_browser_down=True)
    automation_svc = AutomationService(adapter=down_adapter)
    manager = RequestManager(
        queue_size=5,
        request_timeout_seconds=2,
        concurrency=1,
        automation_service=automation_svc,
    )
    service = RgAiService(
        request_manager=manager,
        automation_service=automation_svc,
    )

    await manager.start()
    try:
        req = ChatPromptRequest(prompt="Analyze Reliance daily charts")
        submission = await service.submit_prompt(req)

        for _ in range(40):
            status = await service.get_request_status(submission.request_id)
            if status.status in {RequestStatus.COMPLETED, RequestStatus.FAILED}:
                break
            await asyncio.sleep(0.05)

        final_status = await service.get_request_status(submission.request_id)
        assert final_status.status == RequestStatus.FAILED
        assert final_status.error is not None
        assert final_status.error["code"] == "BROWSER_UNAVAILABLE"
    finally:
        await manager.shutdown()
