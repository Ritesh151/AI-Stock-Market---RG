"""
Centralized Exception Handlers for FastAPI.
Ensures uniform error structures and prevents leaking internal stack traces or secrets.
"""

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import AppException
from app.core.logging import get_logger

logger = get_logger("exception_handler")


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """
    Handles application-specific custom exceptions.
    """
    logger.warning(
        f"Handled AppException [{exc.code}] at {request.method} {request.url.path}: {exc.message}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details if exc.details else None,
            },
        },
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Handles Pydantic request validation errors (HTTP 422).
    """
    formatted_errors = []
    for err in exc.errors():
        field = ".".join(str(loc) for loc in err.get("loc", []))
        formatted_errors.append(
            {
                "field": field,
                "issue": err.get("msg", "Invalid parameter"),
            }
        )

    logger.info(
        f"Validation error at {request.method} {request.url.path}: {len(formatted_errors)} issues"
    )

    status_code = 422
    return JSONResponse(

        status_code=status_code,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "The request contains invalid or missing parameters.",
                "details": formatted_errors,
            },
        },
    )


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """
    Handles Starlette/FastAPI standard HTTP exceptions (404, 405, etc.).
    """
    code_map = {
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        403: "FORBIDDEN",
        401: "UNAUTHORIZED",
    }
    error_code = code_map.get(exc.status_code, "HTTP_ERROR")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": error_code,
                "message": str(exc.detail),
                "details": None,
            },
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Fallback catch-all handler for unexpected internal server errors.
    CRITICAL: Never exposes internal file paths, stack traces, or credentials to the client.
    """
    logger.exception(
        f"Unhandled server exception at {request.method} {request.url.path}: {str(exc)}"
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred while processing your request. Please try again later.",
                "details": None,
            },
        },
    )
