"""
Tests for Centralized Request Manager and Request Queue.
Covers queue limits, duplicate detection, state transitions, serialization, cancellation, and timeouts.
"""

import asyncio
import pytest
from app.integrations.rg_ai.automation_service import AutomationService
from app.integrations.rg_ai.gpt_adapter import MockGPTAdapter
from app.integrations.rg_ai.integration_exceptions import (
    DuplicateRequestError,
    InvalidStateTransitionError,
    QueueFullError,
)
from app.integrations.rg_ai.prompt_manager import PreparedPrompt
from app.schemas.rg_ai import RequestStatus
from app.services.request_manager import RequestManager
from app.services.request_queue import RequestQueue


@pytest.fixture
def mock_automation_service():
    adapter = MockGPTAdapter(simulated_delay=0.05)
    return AutomationService(adapter=adapter)


@pytest.fixture
def request_manager(mock_automation_service):
    manager = RequestManager(
        queue_size=5,
        request_timeout_seconds=2,
        concurrency=1,
        automation_service=mock_automation_service,
    )
    return manager


@pytest.mark.asyncio
async def test_queue_enqueue_and_capacity():
    queue = RequestQueue(maxsize=2)
    pos1 = await queue.enqueue("req_1", "What is NIFTY support?")
    assert pos1 == 1
    assert queue.size() == 1

    pos2 = await queue.enqueue("req_2", "Analyze Bank Nifty")
    assert pos2 == 2
    assert queue.is_full()

    with pytest.raises(QueueFullError):
        await queue.enqueue("req_3", "Analyze Reliance")


@pytest.mark.asyncio
async def test_queue_duplicate_protection():
    queue = RequestQueue(maxsize=10)
    await queue.enqueue("req_1", "Analyze Tata Motors")

    # Identical prompt with different casing/whitespace must be rejected
    with pytest.raises(DuplicateRequestError):
        await queue.enqueue("req_2", "  analyze  tata  motors  ")

    # After hash is released, identical prompt can be submitted
    prompt_hash = RequestQueue.compute_prompt_hash("Analyze Tata Motors")
    await queue.release_prompt_hash(prompt_hash)
    pos = await queue.enqueue("req_3", "Analyze Tata Motors")
    assert pos == 2


@pytest.mark.asyncio
async def test_state_transitions_valid_and_invalid(request_manager):
    prompt = PreparedPrompt(
        original_prompt="Test prompt",
        cleaned_prompt="Test prompt",
        template_version="v1",
    )
    record = await request_manager.create_request(prompt)
    assert record.status == RequestStatus.QUEUED

    # Valid: QUEUED -> INITIALIZING
    request_manager.transition_state(record, RequestStatus.INITIALIZING)
    assert record.status == RequestStatus.INITIALIZING

    # Invalid: INITIALIZING -> COMPLETED (must go through SUBMITTING/PROCESSING/VALIDATING)
    with pytest.raises(InvalidStateTransitionError):
        request_manager.transition_state(record, RequestStatus.COMPLETED)

    # Valid: INITIALIZING -> SUBMITTING -> PROCESSING -> VALIDATING -> COMPLETED
    request_manager.transition_state(record, RequestStatus.SUBMITTING)
    request_manager.transition_state(record, RequestStatus.PROCESSING)
    request_manager.transition_state(record, RequestStatus.VALIDATING)
    request_manager.transition_state(record, RequestStatus.COMPLETED)
    assert record.status == RequestStatus.COMPLETED

    # Terminal state: Cannot transition out of COMPLETED
    with pytest.raises(InvalidStateTransitionError):
        request_manager.transition_state(record, RequestStatus.QUEUED)


@pytest.mark.asyncio
async def test_request_manager_execution_pipeline(request_manager):
    await request_manager.start()
    try:
        prompt = PreparedPrompt(
            original_prompt="Technical analysis of Reliance",
            cleaned_prompt="Technical analysis of Reliance",
            template_version="v1",
        )
        record = await request_manager.create_request(prompt)
        assert record.status == RequestStatus.QUEUED

        # Wait for worker to complete execution
        for _ in range(50):
            if record.status in {RequestStatus.COMPLETED, RequestStatus.FAILED}:
                break
            await asyncio.sleep(0.05)

        assert record.status == RequestStatus.COMPLETED
        assert record.result is not None
        assert "Verified Result" in record.result["content"]
        assert record.completed_at is not None
    finally:
        await request_manager.shutdown()


@pytest.mark.asyncio
async def test_request_manager_cancellation(request_manager):
    # Set long simulated delay on mock adapter
    mock_adapter = MockGPTAdapter(simulated_delay=1.0)
    request_manager._automation_service.set_adapter(mock_adapter)

    await request_manager.start()
    try:
        prompt = PreparedPrompt(
            original_prompt="Long running query",
            cleaned_prompt="Long running query",
            template_version="v1",
        )
        record = await request_manager.create_request(prompt)

        # Cancel shortly after submit
        await asyncio.sleep(0.02)
        cancelled_record = await request_manager.cancel_request(record.request_id)

        assert cancelled_record.status == RequestStatus.CANCELLED
        assert cancelled_record.error is not None
        assert cancelled_record.error["code"] == "REQUEST_CANCELLED"
    finally:
        await request_manager.shutdown()


@pytest.mark.asyncio
async def test_request_manager_timeout(mock_automation_service):
    # Short timeout manager with long-running adapter
    long_adapter = MockGPTAdapter(simulated_delay=0.5)
    automation_service = AutomationService(adapter=long_adapter)
    manager = RequestManager(
        queue_size=5,
        request_timeout_seconds=0.1,  # 100ms timeout
        concurrency=1,
        automation_service=automation_service,
    )

    await manager.start()
    try:
        prompt = PreparedPrompt(
            original_prompt="Timeout test query",
            cleaned_prompt="Timeout test query",
            template_version="v1",
        )
        record = await manager.create_request(prompt)

        for _ in range(40):
            if record.status in {RequestStatus.COMPLETED, RequestStatus.FAILED}:
                break
            await asyncio.sleep(0.05)

        assert record.status == RequestStatus.FAILED
        assert record.error is not None
        assert record.error["code"] == "REQUEST_TIMEOUT"
    finally:
        await manager.shutdown()
