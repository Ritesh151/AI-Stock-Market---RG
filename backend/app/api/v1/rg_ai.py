"""
RG AI Orchestration & Chat API Endpoints (API v1).
Provides authenticated/local endpoints for prompt submission, real-time status tracking, cancellation, and health.
"""

from fastapi import APIRouter, Depends, status
from app.api.v1.browser import verify_local_access_policy
from app.schemas.rg_ai import (
    CancelRequestResponse,
    ChatPromptRequest,
    ChatSubmissionResponse,
    RGAvailabilityResponse,
    RGHealthResponse,
    RequestStatusResponse,
)
from app.services.rg_ai_service import RgAiService, get_rg_ai_service
from app.core.logging import get_logger

logger = get_logger("api.v1.rg_ai")

router = APIRouter(prefix="/rg-ai", tags=["RG AI Intelligence Orchestration"])


@router.post(
    "/chat",
    response_model=ChatSubmissionResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit an analysis prompt for orchestrated execution",
    dependencies=[Depends(verify_local_access_policy)],
)
async def submit_chat_prompt(
    payload: ChatPromptRequest,
    service: RgAiService = Depends(get_rg_ai_service),
) -> ChatSubmissionResponse:
    """
    Accepts a user analysis prompt, validates length and content bounds,
    and enqueues the request in the serialized orchestration pipeline.
    """
    logger.info(f"Received prompt submission (length: {len(payload.prompt)})")
    return await service.submit_prompt(payload)


@router.get(
    "/status/{request_id}",
    response_model=RequestStatusResponse,
    summary="Get real-time execution status and results of a request",
    dependencies=[Depends(verify_local_access_policy)],
)
async def get_request_status(
    request_id: str,
    service: RgAiService = Depends(get_rg_ai_service),
) -> RequestStatusResponse:
    """
    Retrieves current state, timestamps, queue position, and normalized results or error messages.
    """
    return await service.get_request_status(request_id)


@router.post(
    "/cancel/{request_id}",
    response_model=CancelRequestResponse,
    summary="Cancel a queued or active request",
    dependencies=[Depends(verify_local_access_policy)],
)
async def cancel_request(
    request_id: str,
    service: RgAiService = Depends(get_rg_ai_service),
) -> CancelRequestResponse:
    """
    Cancels an in-flight or queued request, releasing worker lock and queue slot.
    """
    return await service.cancel_request(request_id)


@router.get(
    "/health",
    response_model=RGHealthResponse,
    summary="Get RG AI orchestrator engine health and queue telemetry",
    dependencies=[Depends(verify_local_access_policy)],
)
async def get_rg_ai_health(
    service: RgAiService = Depends(get_rg_ai_service),
) -> RGHealthResponse:
    """
    Reports internal worker health, queue occupancy, concurrency limits, and execution metrics.
    """
    return service.get_health()


@router.post(
    "/availability",
    response_model=RGAvailabilityResponse,
    summary="Check whether the configured integration adapter is available",
    dependencies=[Depends(verify_local_access_policy)],
)
@router.get(
    "/availability",
    response_model=RGAvailabilityResponse,
    summary="Check whether the configured integration adapter is available (GET alias)",
    dependencies=[Depends(verify_local_access_policy)],
    include_in_schema=False,
)
async def check_availability(
    service: RgAiService = Depends(get_rg_ai_service),
) -> RGAvailabilityResponse:
    """
    Probes browser availability, login state, and integration adapter status.
    """
    return await service.check_availability()
