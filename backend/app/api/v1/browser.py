"""
Browser Lifecycle & Session Management Endpoints (API v1).
Provides authenticated/local endpoints to control persistent Chrome automation.
"""

import asyncio
from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.integrations.browser.browser_models import (
    BrowserActionResponse,
    BrowserStatusResponse,
)
from app.services.browser_service import BrowserService, get_browser_service
from app.core.logging import get_logger

logger = get_logger("api.v1.browser")

router = APIRouter(prefix="/browser", tags=["Browser Automation"])


def verify_local_access_policy(request: Request) -> None:
    """
    Security Baseline: Protects browser-control endpoints from external network exposure.
    Restricts access to localhost clients during local operation.
    """
    client_host = request.client.host if request.client else "unknown"
    allowed_hosts = {"127.0.0.1", "localhost", "::1", "testclient", "testserver"}

    if client_host not in allowed_hosts and not client_host.startswith("127."):
        logger.warning(f"Unauthorized browser-control access attempt from {client_host}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Browser management endpoints are restricted to local host access.",
        )


@router.get(
    "/status",
    response_model=BrowserStatusResponse,
    summary="Get managed browser lifecycle and login status",
)
async def get_browser_status(
    service: BrowserService = Depends(get_browser_service),
) -> BrowserStatusResponse:
    """
    Returns current browser state, running status, target URL, login status, and last health check.
    """
    return await service.get_status()


@router.post(
    "/start",
    response_model=BrowserActionResponse,
    summary="Launch persistent Chrome browser session",
    dependencies=[Depends(verify_local_access_policy)],
)
async def start_browser(
    service: BrowserService = Depends(get_browser_service),
) -> BrowserActionResponse:
    """
    Starts the persistent Chrome browser using the dedicated user-data profile.
    Protected by process-level lock.
    """
    return await service.start_session()


@router.post(
    "/open-gpt",
    response_model=BrowserActionResponse,
    summary="Navigate managed browser to fixed target Custom GPT",
    dependencies=[Depends(verify_local_access_policy)],
)
async def open_target_gpt(
    service: BrowserService = Depends(get_browser_service),
) -> BrowserActionResponse:
    """
    Opens the centralized Indian Stock Market Custom GPT URL in the managed browser.
    """
    return await service.open_target_gpt()


@router.post(
    "/confirm-login",
    response_model=BrowserActionResponse,
    summary="Verify and confirm manual ChatGPT authentication",
    dependencies=[Depends(verify_local_access_policy)],
)
async def confirm_login(
    service: BrowserService = Depends(get_browser_service),
) -> BrowserActionResponse:
    """
    Independently inspects the active browser DOM to verify authentication.
    Does not falsely classify challenges or unauthenticated states as logged in.
    """
    return await service.confirm_manual_login()


@router.post(
    "/stop",
    response_model=BrowserActionResponse,
    summary="Gracefully terminate browser and release profile lock",
    dependencies=[Depends(verify_local_access_policy)],
)
async def stop_browser(
    service: BrowserService = Depends(get_browser_service),
) -> BrowserActionResponse:
    """
    Gracefully stops the managed browser and releases the POSIX file lock.
    """
    return await service.stop_session()


@router.post(
    "/reconnect",
    response_model=BrowserActionResponse,
    summary="Recover and reconnect disconnected browser session",
    dependencies=[Depends(verify_local_access_policy)],
)
async def reconnect_browser(
    service: BrowserService = Depends(get_browser_service),
) -> BrowserActionResponse:
    """
    Attempts clean recovery when the browser has crashed or disconnected.
    """
    return await service.reconnect_session()
