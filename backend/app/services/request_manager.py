"""
RG AI Centralized Request Manager.
Manages request lifecycle, valid state transitions, serialized execution, cancellation, and timeouts.
Protects the single persistent Chrome profile from concurrent multi-session collisions.
"""

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set
import uuid
from pydantic import BaseModel, Field

from app.integrations.rg_ai.automation_service import AutomationService, get_automation_service
from app.integrations.rg_ai.conversation_manager import get_conversation_manager
from app.integrations.rg_ai.gpt_config import (
    DEFAULT_QUEUE_SIZE,
    DEFAULT_REQUEST_TIMEOUT_SECONDS,
    MAX_CONCURRENT_REQUESTS,
)
from app.integrations.rg_ai.integration_exceptions import (
    AuthenticationRequiredError,
    BrowserUnavailableError,
    IntegrationException,
    InvalidStateTransitionError,
    RequestCancelledError,
    RequestTimeoutError,
    UnsupportedIntegrationError,
)
from app.integrations.rg_ai.prompt_manager import PreparedPrompt
from app.integrations.rg_ai.response_manager import ResponseManager
from app.schemas.rg_ai import RequestStatus
from app.services.request_queue import RequestQueue
from app.core.exceptions import AppException
from app.core.logging import get_logger

logger = get_logger("services.request_manager")


# Formal State Transition Matrix
_VALID_TRANSITIONS: Dict[RequestStatus, Set[RequestStatus]] = {
    RequestStatus.IDLE: {RequestStatus.QUEUED},
    RequestStatus.QUEUED: {
        RequestStatus.INITIALIZING,
        RequestStatus.CANCELLED,
        RequestStatus.FAILED,
    },
    RequestStatus.INITIALIZING: {
        RequestStatus.WAITING_FOR_LOGIN,
        RequestStatus.SUBMITTING,
        RequestStatus.INTEGRATION_UNAVAILABLE,
        RequestStatus.FAILED,
        RequestStatus.CANCELLED,
    },
    RequestStatus.WAITING_FOR_LOGIN: {
        RequestStatus.INITIALIZING,
        RequestStatus.SUBMITTING,
        RequestStatus.FAILED,
        RequestStatus.CANCELLED,
    },
    RequestStatus.SUBMITTING: {
        RequestStatus.PROCESSING,
        RequestStatus.INTEGRATION_UNAVAILABLE,
        RequestStatus.FAILED,
        RequestStatus.CANCELLED,
    },
    RequestStatus.PROCESSING: {
        RequestStatus.VALIDATING,
        RequestStatus.INTEGRATION_UNAVAILABLE,
        RequestStatus.FAILED,
        RequestStatus.CANCELLED,
    },
    RequestStatus.VALIDATING: {
        RequestStatus.COMPLETED,
        RequestStatus.FAILED,
        RequestStatus.CANCELLED,
    },
    # Terminal states
    RequestStatus.COMPLETED: set(),
    RequestStatus.FAILED: set(),
    RequestStatus.CANCELLED: set(),
    RequestStatus.INTEGRATION_UNAVAILABLE: set(),
}


class RequestRecord(BaseModel):
    """Full tracking record for an orchestrated request."""

    request_id: str
    prompt: PreparedPrompt
    status: RequestStatus = RequestStatus.QUEUED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    prompt_hash: str


class RequestManager:
    """
    Centralized Request Orchestration Manager.
    Enforces concurrency = 1 (single Chrome profile serialization), async safety, and valid transitions.
    """

    def __init__(
        self,
        queue_size: int = DEFAULT_QUEUE_SIZE,
        request_timeout_seconds: int = DEFAULT_REQUEST_TIMEOUT_SECONDS,
        concurrency: int = MAX_CONCURRENT_REQUESTS,
        automation_service: Optional[AutomationService] = None,
    ) -> None:
        self.queue_size = queue_size
        self.request_timeout_seconds = request_timeout_seconds
        self.concurrency = concurrency
        self._automation_service = automation_service or get_automation_service()

        self._queue = RequestQueue(maxsize=queue_size)
        self._records: Dict[str, RequestRecord] = {}
        self._cancellation_events: Dict[str, asyncio.Event] = {}
        self._running_tasks: Dict[str, asyncio.Task] = {}

        self._worker_task: Optional[asyncio.Task] = None
        self._is_running = False
        self._lock = asyncio.Lock()

        # Telemetry metrics
        self._total_processed = 0
        self._total_failed = 0
        self._total_cancelled = 0

    async def start(self) -> None:
        """Starts background queue processing worker loop."""
        async with self._lock:
            if self._is_running:
                return
            self._is_running = True
            self._worker_task = asyncio.create_task(self._worker_loop(), name="rg_ai_request_worker")
            logger.info(f"RequestManager worker started (concurrency: {self.concurrency}, queue_size: {self.queue_size})")

    async def shutdown(self) -> None:
        """Gracefully cancels active worker and cleans up resources."""
        async with self._lock:
            if not self._is_running:
                return
            self._is_running = False

            if self._worker_task:
                self._worker_task.cancel()
                try:
                    await self._worker_task
                except asyncio.CancelledError:
                    pass
                self._worker_task = None

            # Cancel running tasks
            for rid, task in list(self._running_tasks.items()):
                task.cancel()
                self._cancellation_events.get(rid, asyncio.Event()).set()

            await self._queue.clear()
            logger.info("RequestManager shutdown complete.")

    async def create_request(self, prompt: PreparedPrompt) -> RequestRecord:
        """
        Creates a new request record, registers it in conversation, and pushes to queue.
        Enforces duplicate detection and queue capacity limits.
        """
        request_id = f"req_{uuid.uuid4().hex[:12]}"
        prompt_hash = RequestQueue.compute_prompt_hash(prompt.cleaned_prompt)

        record = RequestRecord(
            request_id=request_id,
            prompt=prompt,
            status=RequestStatus.QUEUED,
            prompt_hash=prompt_hash,
        )

        async with self._lock:
            self._records[request_id] = record
            self._cancellation_events[request_id] = asyncio.Event()

        # Link to conversation session
        if prompt.conversation_id:
            get_conversation_manager().link_request(prompt.conversation_id, request_id)

        try:
            position = await self._queue.enqueue(request_id, prompt.cleaned_prompt)
            logger.info(f"Request {request_id} queued at position {position} for prompt: '{prompt.cleaned_prompt[:40]}...'")
            return record
        except Exception:
            async with self._lock:
                self._records.pop(request_id, None)
                self._cancellation_events.pop(request_id, None)
            raise

    def get_request(self, request_id: str) -> Optional[RequestRecord]:
        """Retrieves request record by ID."""
        return self._records.get(request_id)

    async def get_queue_position(self, request_id: str) -> Optional[int]:
        """Returns 1-indexed queue position if queued."""
        record = self.get_request(request_id)
        if not record or record.status != RequestStatus.QUEUED:
            return None
        return await self._queue.get_position(request_id)

    def transition_state(
        self,
        record: RequestRecord,
        new_status: RequestStatus,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Transitions request to a new status according to state machine rules.
        Rejects invalid transitions with InvalidStateTransitionError.
        """
        current_status = record.status
        allowed = _VALID_TRANSITIONS.get(current_status, set())

        if new_status not in allowed:
            msg = f"Invalid state transition from {current_status.value} to {new_status.value} for request {record.request_id}."
            logger.error(msg)
            raise InvalidStateTransitionError(msg)

        now = datetime.now(timezone.utc)
        record.status = new_status
        record.updated_at = now

        if new_status == RequestStatus.INITIALIZING and record.started_at is None:
            record.started_at = now

        if new_status in {
            RequestStatus.COMPLETED,
            RequestStatus.FAILED,
            RequestStatus.CANCELLED,
            RequestStatus.INTEGRATION_UNAVAILABLE,
        }:
            record.completed_at = now
            if result:
                record.result = result
            if error:
                record.error = error

        logger.debug(f"Request {record.request_id}: transitioned {current_status.value} -> {new_status.value}")

    async def cancel_request(self, request_id: str) -> RequestRecord:
        """
        Cancels a queued or currently executing request.
        """
        record = self.get_request(request_id)
        if not record:
            raise AppException(message=f"Request {request_id} not found.", code="REQUEST_NOT_FOUND", status_code=404)

        if record.status in {
            RequestStatus.COMPLETED,
            RequestStatus.FAILED,
            RequestStatus.CANCELLED,
            RequestStatus.INTEGRATION_UNAVAILABLE,
        }:
            return record

        logger.info(f"Cancelling request {request_id} from status {record.status.value}")

        # Signal cancellation event
        event = self._cancellation_events.get(request_id)
        if event:
            event.set()

        # Cancel running task if active
        task = self._running_tasks.get(request_id)
        if task and not task.done():
            task.cancel()

        # Tell underlying adapter to cancel
        await self._automation_service.cancel_request(request_id)

        # Release prompt hash so prompt can be re-submitted
        await self._queue.release_prompt_hash(record.prompt_hash)

        # Transition to CANCELLED
        self.transition_state(
            record,
            RequestStatus.CANCELLED,
            error={
                "code": "REQUEST_CANCELLED",
                "message": "The request was cancelled by user or operator.",
            },
        )
        self._total_cancelled += 1
        return record

    async def _worker_loop(self) -> None:
        """
        Continuous background worker loop.
        Processes requests one at a time (serialized) to protect the persistent Chrome profile.
        """
        logger.info("RequestManager worker loop active.")
        while self._is_running:
            try:
                queued_item = await self._queue.dequeue()
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error(f"Worker dequeue error: {exc}")
                await asyncio.sleep(0.1)
                continue

            request_id = queued_item.request_id
            record = self.get_request(request_id)
            if not record:
                await self._queue.release_prompt_hash(queued_item.prompt_hash)
                continue

            # If request was already cancelled while in queue
            if record.status == RequestStatus.CANCELLED:
                await self._queue.release_prompt_hash(queued_item.prompt_hash)
                continue

            # Execute with concurrency serialization
            try:
                task = asyncio.create_task(
                    self._execute_request_pipeline(record),
                    name=f"exec_{request_id}",
                )
                self._running_tasks[request_id] = task
                await task
            except asyncio.CancelledError:
                logger.info(f"Worker execution task cancelled for {request_id}")
            except Exception as exc:
                logger.error(f"Unexpected worker execution exception for {request_id}: {exc}")
            finally:
                self._running_tasks.pop(request_id, None)
                await self._queue.release_prompt_hash(queued_item.prompt_hash)
                self._cancellation_events.pop(request_id, None)

    async def _execute_request_pipeline(self, record: RequestRecord) -> None:
        """
        Executes request through formal lifecycle stages:
        QUEUED -> INITIALIZING -> [WAITING_FOR_LOGIN | SUBMITTING] -> PROCESSING -> VALIDATING -> COMPLETED
        or transitions to INTEGRATION_UNAVAILABLE, FAILED, CANCELLED.
        """
        rid = record.request_id
        cancel_event = self._cancellation_events.get(rid)

        try:
            # 1. INITIALIZING
            if cancel_event and cancel_event.is_set():
                raise RequestCancelledError()
            self.transition_state(record, RequestStatus.INITIALIZING)

            # Check browser availability & login
            availability = await self._automation_service.check_availability()
            from app.integrations.rg_ai.gpt_adapter import BrowserGPTAdapter
            if not availability.is_browser_running and isinstance(self._automation_service.get_adapter(), BrowserGPTAdapter):
                logger.info(f"Request {rid}: Browser not active, attempting auto-launch...")
                try:
                    from app.integrations.browser import get_browser_manager
                    bm = get_browser_manager()
                    if not bm.is_running:
                        await bm.start_browser()
                        await bm.open_target_gpt()
                        await asyncio.sleep(2)
                        availability = await self._automation_service.check_availability()
                except Exception as exc:
                    logger.warning(f"Browser auto-launch attempt failed: {exc}")

            if not availability.is_browser_running:
                raise BrowserUnavailableError(
                    "Managed Chrome browser is not running. Please launch the browser from the Chrome Session panel."
                )

            # Probe login state
            login_state = await self._automation_service.check_authentication()
            from app.integrations.browser.browser_status import LoginState

            if login_state != LoginState.AUTHENTICATED:
                logger.info(f"Request {rid}: Browser running but login state is {login_state.value}")
                self.transition_state(record, RequestStatus.WAITING_FOR_LOGIN)
                raise AuthenticationRequiredError(
                    f"Authentication required (login state: {login_state.value}). "
                    "Please complete manual login in the managed Chrome browser."
                )

            # 2. SUBMITTING
            if cancel_event and cancel_event.is_set():
                raise RequestCancelledError()
            self.transition_state(record, RequestStatus.SUBMITTING)

            # 3. PROCESSING (wrapped with configured timeout)
            self.transition_state(record, RequestStatus.PROCESSING)
            result = await asyncio.wait_for(
                self._automation_service.execute_prompt(record.prompt, rid),
                timeout=float(self.request_timeout_seconds),
            )

            # 4. VALIDATING
            if cancel_event and cancel_event.is_set():
                raise RequestCancelledError()
            self.transition_state(record, RequestStatus.VALIDATING)

            # Content presence validation
            if not result or not result.content:
                raise AppException(
                    message="Integration response failed validation (empty content).",
                    code="VALIDATION_FAILED",
                    status_code=502,
                )

            # Strict JSON validation & normalization engine (Phase 5)
            raw_text = result.content.strip()
            is_json_candidate = (
                raw_text.startswith("{")
                or "```json" in raw_text
                or raw_text.startswith("```")
                or getattr(result, "format_type", None) == "application/json"
            )

            if is_json_candidate:
                from app.services.response_processor import get_response_processor

                expected_schema = (
                    record.prompt.metadata.get("expected_schema_type")
                    if record.prompt and record.prompt.metadata
                    else None
                )
                processor = get_response_processor()
                processed_envelope = processor.process(
                    raw_content=result.content,
                    request_id=rid,
                    expected_type=expected_schema,
                )

                if not processed_envelope.success:
                    err_payload = getattr(processed_envelope, "error", None)
                    err_code = err_payload.code if err_payload else "SCHEMA_VALIDATION_FAILED"
                    err_msg = err_payload.message if err_payload else "Response validation failed."
                    err_details = [d.model_dump() for d in err_payload.details] if err_payload and err_payload.details else None
                    raise AppException(
                        message=err_msg,
                        code=err_code,
                        details={"validation_details": err_details} if err_details else None,
                        status_code=422,
                    )

                result_data = processed_envelope.model_dump()
            else:
                # Maintain backward-compatible payload for non-JSON string results
                response_payload = ResponseManager.build_success_response(
                    request_id=rid,
                    status="completed",
                    result=result,
                    created_at=record.created_at,
                    completed_at=datetime.now(timezone.utc),
                )
                result_data = response_payload["result"]

            # 5. COMPLETED
            self.transition_state(record, RequestStatus.COMPLETED, result=result_data)
            self._total_processed += 1
            logger.info(f"Request {rid} completed successfully.")


        except UnsupportedIntegrationError as exc:
            logger.info(f"Request {rid} marked integration_unavailable: {exc.message}")
            payload = ResponseManager.build_unavailable_response(
                request_id=rid,
                code=exc.code,
                message=exc.message,
                details=exc.details,
                created_at=record.created_at,
            )
            self.transition_state(record, RequestStatus.INTEGRATION_UNAVAILABLE, error=payload["error"])
            self._total_processed += 1

        except AuthenticationRequiredError as exc:
            logger.info(f"Request {rid} waiting for login: {exc.message}")
            # Ensure in WAITING_FOR_LOGIN if not already transitioned
            if record.status != RequestStatus.WAITING_FOR_LOGIN:
                try:
                    self.transition_state(record, RequestStatus.WAITING_FOR_LOGIN)
                except InvalidStateTransitionError:
                    pass
            # Mark failed as login required timeout
            try:
                self.transition_state(
                    record,
                    RequestStatus.FAILED,
                    error={"code": exc.code, "message": exc.message},
                )
            except InvalidStateTransitionError:
                pass
            self._total_failed += 1

        except (BrowserUnavailableError, IntegrationException, AppException) as exc:
            logger.warning(f"Request {rid} failed with application exception [{exc.code}]: {exc.message}")
            try:
                self.transition_state(
                    record,
                    RequestStatus.FAILED,
                    error={"code": exc.code, "message": exc.message},
                )
            except InvalidStateTransitionError:
                pass
            self._total_failed += 1

        except asyncio.TimeoutError:
            logger.warning(f"Request {rid} timed out after {self.request_timeout_seconds}s")
            try:
                self.transition_state(
                    record,
                    RequestStatus.FAILED,
                    error={
                        "code": "REQUEST_TIMEOUT",
                        "message": f"Execution timed out after {self.request_timeout_seconds} seconds.",
                    },
                )
            except InvalidStateTransitionError:
                pass
            self._total_failed += 1

        except asyncio.CancelledError:
            logger.info(f"Request {rid} cancelled during execution.")
            try:
                self.transition_state(
                    record,
                    RequestStatus.CANCELLED,
                    error={"code": "REQUEST_CANCELLED", "message": "Request cancelled."},
                )
            except InvalidStateTransitionError:
                pass
            self._total_cancelled += 1

        except Exception as exc:
            logger.error(f"Request {rid} failed unexpectedly: {exc}", exc_info=True)
            try:
                self.transition_state(
                    record,
                    RequestStatus.FAILED,
                    error={
                        "code": "INTERNAL_EXECUTION_ERROR",
                        "message": "An unexpected error occurred during request orchestration.",
                    },
                )
            except InvalidStateTransitionError:
                pass
            self._total_failed += 1

    def get_health_metrics(self) -> Dict[str, Any]:
        """Returns internal queue load, worker status, and counters."""
        return {
            "status": "healthy" if self._is_running else "stopped",
            "queue_size": self._queue.size(),
            "max_queue_size": self.queue_size,
            "active_worker": self._is_running and self._worker_task is not None and not self._worker_task.done(),
            "concurrency_limit": self.concurrency,
            "total_processed": self._total_processed,
            "total_failed": self._total_failed,
            "total_cancelled": self._total_cancelled,
        }


_request_manager_instance: Optional[RequestManager] = None


def get_request_manager() -> RequestManager:
    """Returns singleton instance of RequestManager."""
    global _request_manager_instance
    if _request_manager_instance is None:
        _request_manager_instance = RequestManager()
    return _request_manager_instance
