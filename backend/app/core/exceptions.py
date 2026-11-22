"""
Custom Application Exception Hierarchy for RG AI.
Provides clean error semantics decoupled from HTTP presentation.
"""

from typing import Any, Dict, List, Optional


class AppException(Exception):
    """
    Base exception for all domain and operational errors in RG AI.
    """

    def __init__(
        self,
        message: str = "An application error occurred.",
        code: str = "INTERNAL_SERVER_ERROR",
        status_code: int = 500,
        details: Optional[List[Dict[str, Any]]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or []


class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found.", details: Optional[List[Dict[str, Any]]] = None):
        super().__init__(
            message=message,
            code="NOT_FOUND",
            status_code=404,
            details=details,
        )


class ValidationException(AppException):
    def __init__(self, message: str = "Validation failed.", details: Optional[List[Dict[str, Any]]] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=422,
            details=details,
        )


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Authentication required.", details: Optional[List[Dict[str, Any]]] = None):
        super().__init__(
            message=message,
            code="UNAUTHORIZED",
            status_code=401,
            details=details,
        )


class ForbiddenException(AppException):
    def __init__(self, message: str = "Permission denied.", details: Optional[List[Dict[str, Any]]] = None):
        super().__init__(
            message=message,
            code="FORBIDDEN",
            status_code=403,
            details=details,
        )


class DatabaseException(AppException):
    def __init__(self, message: str = "Database operation failed.", details: Optional[List[Dict[str, Any]]] = None):
        super().__init__(
            message=message,
            code="DATABASE_ERROR",
            status_code=500,
            details=details,
        )


class IntegrationException(AppException):
    def __init__(self, message: str = "External integration error.", details: Optional[List[Dict[str, Any]]] = None):
        super().__init__(
            message=message,
            code="INTEGRATION_ERROR",
            status_code=502,
            details=details,
        )


class ServiceUnavailableException(AppException):
    def __init__(self, message: str = "Service temporarily unavailable.", details: Optional[List[Dict[str, Any]]] = None):
        super().__init__(
            message=message,
            code="SERVICE_UNAVAILABLE",
            status_code=503,
            details=details,
        )
