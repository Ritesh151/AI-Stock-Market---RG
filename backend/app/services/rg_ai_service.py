"""
RG AI High-Level Orchestration Service.
Interfaces between API v1 endpoints and internal request managers, prompt managers, and adapters.
"""

from typing import Optional
from app.integrations.rg_ai.automation_service import AutomationService, get_automation_service
from app.integrations.rg_ai.prompt_manager import PromptManager, get_prompt_manager
from app.schemas.rg_ai import (
    CancelRequestResponse,
    ChatPromptRequest,
    ChatSubmissionResponse,
    RGAvailabilityResponse,
    RGHealthResponse,
    RequestStatus,
    RequestStatusResponse,
)
from app.services.request_manager import RequestManager, RequestRecord, get_request_manager
from app.core.exceptions import AppException
from app.core.logging import get_logger

logger = get_logger("services.rg_ai_service")


class RgAiService:
    """Service facade exposing high-level operations for RG AI intelligence chat."""

    def __init__(
        self,
        request_manager: Optional[RequestManager] = None,
        prompt_manager: Optional[PromptManager] = None,
        automation_service: Optional[AutomationService] = None,
    ) -> None:
        self.request_manager = request_manager or get_request_manager()
        self.prompt_manager = prompt_manager or get_prompt_manager()
        self.automation_service = automation_service or get_automation_service()

    async def submit_prompt(self, payload: ChatPromptRequest) -> ChatSubmissionResponse:
        """
        Validates prompt and enqueues request for serialized execution.
        """
        # Validate & package prompt
        prepared = self.prompt_manager.validate_and_prepare(
            raw_prompt=payload.prompt,
            conversation_id=payload.conversation_id,
            metadata=payload.metadata,
        )

        # Enqueue request in request manager
        record = await self.request_manager.create_request(prepared)
        queue_pos = await self.request_manager.get_queue_position(record.request_id)

        return ChatSubmissionResponse(
            success=True,
            request_id=record.request_id,
            status=record.status,
            created_at=record.created_at,
            queue_position=queue_pos or 1,
            message="Prompt successfully queued for orchestration.",
        )

    async def get_request_status(self, request_id: str) -> RequestStatusResponse:
        """
        Retrieves real-time execution status for a given request ID.
        """
        record: Optional[RequestRecord] = self.request_manager.get_request(request_id)
        if not record:
            raise AppException(
                message=f"Request '{request_id}' not found.",
                code="REQUEST_NOT_FOUND",
                status_code=404,
            )

        queue_pos = await self.request_manager.get_queue_position(request_id)

        is_success = record.status in {
            RequestStatus.QUEUED,
            RequestStatus.INITIALIZING,
            RequestStatus.WAITING_FOR_LOGIN,
            RequestStatus.SUBMITTING,
            RequestStatus.PROCESSING,
            RequestStatus.VALIDATING,
            RequestStatus.COMPLETED,
        }

        return RequestStatusResponse(
            success=is_success,
            request_id=record.request_id,
            status=record.status,
            created_at=record.created_at.isoformat(),
            updated_at=record.updated_at.isoformat(),
            started_at=record.started_at.isoformat() if record.started_at else None,
            completed_at=record.completed_at.isoformat() if record.completed_at else None,
            queue_position=queue_pos,
            result=record.result,
            error=record.error,
        )

    async def cancel_request(self, request_id: str) -> CancelRequestResponse:
        """
        Cancels a queued or executing request.
        """
        record = await self.request_manager.cancel_request(request_id)
        return CancelRequestResponse(
            success=True,
            request_id=record.request_id,
            status=record.status,
            message=f"Request {request_id} has been cancelled.",
        )

    async def check_availability(self) -> RGAvailabilityResponse:
        """
        Queries adapter availability and live browser status.
        """
        status = await self.automation_service.check_availability()
        return RGAvailabilityResponse(
            is_available=status.is_available,
            is_browser_running=status.is_browser_running,
            login_state=status.login_state,
            target_url=status.target_url,
            adapter_type=status.adapter_type,
            message=status.message,
        )

    def get_health(self) -> RGHealthResponse:
        """
        Returns queue health metrics and telemetry counters.
        """
        metrics = self.request_manager.get_health_metrics()
        return RGHealthResponse(**metrics)


_rg_ai_service_instance: Optional[RgAiService] = None


def get_rg_ai_service() -> RgAiService:
    """Returns singleton instance of RgAiService."""
    global _rg_ai_service_instance
    if _rg_ai_service_instance is None:
        _rg_ai_service_instance = RgAiService()
    return _rg_ai_service_instance
