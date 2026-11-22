"""
Main Application Entrypoint and Factory for RG AI Backend.
"""

from contextlib import asynccontextmanager
from typing import Optional
import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.router import api_router
from app.core.config import Settings, get_settings
from app.core.exceptions import AppException
from app.core.handlers import (
    app_exception_handler,
    generic_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from app.core.logging import get_logger, setup_logging
from app.core.security import (
    RateLimitMiddleware,
    RequestSizeLimitMiddleware,
    SecurityHeadersMiddleware,
)



@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle event management for startup and graceful shutdown.
    """
    settings: Settings = app.state.settings
    logger = get_logger("lifecycle")
    logger.info(
        f"Starting {settings.APP_NAME} in [{settings.APP_ENV}] mode on {settings.APP_HOST}:{settings.APP_PORT}"
    )

    # Initialize MongoDB connection pool
    try:
        from app.core.database import get_database_manager
        await get_database_manager().connect()
    except Exception as exc:
        logger.warning(f"Database startup warning: {exc}")

    # Start background request orchestration worker
    try:
        from app.services.request_manager import get_request_manager
        await get_request_manager().start()
    except Exception as exc:
        logger.warning(f"Request manager startup warning: {exc}")

    # Yield control to the application during runtime
    yield

    # Cleanly terminate request manager worker
    try:
        from app.services.request_manager import get_request_manager
        await get_request_manager().shutdown()
    except Exception as exc:
        logger.debug(f"Request manager shutdown notice: {exc}")

    # Cleanly terminate browser process and release locks on shutdown
    try:
        from app.integrations.browser import get_browser_manager
        await get_browser_manager().shutdown()
    except Exception as exc:
        logger.debug(f"Browser shutdown notice: {exc}")

    # Cleanly terminate database connection pool
    try:
        from app.core.database import get_database_manager
        await get_database_manager().disconnect()
    except Exception as exc:
        logger.debug(f"Database disconnect notice: {exc}")

    logger.info(f"Shutting down {settings.APP_NAME} cleanly.")



def create_app(settings: Optional[Settings] = None) -> FastAPI:
    """
    Application factory initializing FastAPI with modular configurations.
    """
    if settings is None:
        settings = get_settings()

    # Initialize structured logging
    setup_logging(log_level=settings.LOG_LEVEL)
    logger = get_logger("app_factory")

    app = FastAPI(
        title=f"{settings.APP_NAME} API",
        description="Indian Stock Market Intelligence Platform Backend",
        version="1.0.0",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # Store settings in application state
    app.state.settings = settings

    # Security & Defensive Middlewares
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestSizeLimitMiddleware, max_bytes=2 * 1024 * 1024)
    if not settings.is_test:
        app.add_middleware(RateLimitMiddleware)

    # CORS Middleware Configuration

    cors_origins = (
        settings.CORS_ORIGINS
        if isinstance(settings.CORS_ORIGINS, list)
        else [settings.CORS_ORIGINS]
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # Register Centralized Exception Handlers
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    # Mount API Router (includes /health and /api/v1)
    app.include_router(api_router)

    logger.info("FastAPI application instance created successfully.")
    return app


# Default ASGI application instance
app = create_app()

if __name__ == "__main__":
    current_settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=current_settings.APP_HOST,
        port=current_settings.APP_PORT,
        reload=current_settings.is_development,
    )
