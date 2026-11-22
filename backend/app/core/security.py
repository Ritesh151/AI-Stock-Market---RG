"""
Security baseline helpers, headers configuration, payload size limits, and rate limiting.
Protects the RG AI API against DoS, payload exhaustion, and injection vectors.
"""

import time
from typing import Dict, List, Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from app.core.logging import get_logger

logger = get_logger("security")

# Maximum permitted HTTP request payload size (2 MB default)
DEFAULT_MAX_REQUEST_SIZE: int = 2 * 1024 * 1024


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Appends standard defensive HTTP security headers to all outbound responses.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        return response


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """
    Rejects requests whose Content-Length exceeds the maximum permitted payload threshold.
    Guards against memory exhaustion and large payload denial-of-service.
    """

    def __init__(self, app, max_bytes: int = DEFAULT_MAX_REQUEST_SIZE) -> None:
        super().__init__(app)
        self.max_bytes = max_bytes

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.method in {"POST", "PUT", "PATCH"}:
            content_length = request.headers.get("content-length")
            if content_length:
                try:
                    length = int(content_length)
                    if length > self.max_bytes:
                        logger.warning(
                            f"Request payload {length} bytes exceeds maximum permitted size {self.max_bytes} bytes."
                        )
                        return JSONResponse(
                            status_code=413,
                            content={
                                "success": False,
                                "error": {
                                    "code": "PAYLOAD_TOO_LARGE",
                                    "message": f"Request payload exceeds maximum allowed size of {self.max_bytes} bytes.",
                                    "details": None,
                                },
                            },
                        )
                except ValueError:
                    pass

        return await call_next(request)


class InMemoryRateLimiter:
    """
    Thread-safe in-memory sliding-window rate limiter per client IP address.
    Default: 120 requests per minute per IP.
    """

    def __init__(self, max_requests: int = 120, window_seconds: int = 60) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._clients: Dict[str, List[float]] = {}

    def is_rate_limited(self, client_ip: str) -> tuple[bool, int]:
        now = time.time()
        cutoff = now - self.window_seconds

        # Clean timestamps older than window
        timestamps = self._clients.get(client_ip, [])
        valid_timestamps = [t for t in timestamps if t > cutoff]

        if len(valid_timestamps) >= self.max_requests:
            remaining = 0
            self._clients[client_ip] = valid_timestamps
            return True, remaining

        valid_timestamps.append(now)
        self._clients[client_ip] = valid_timestamps
        remaining = self.max_requests - len(valid_timestamps)
        return False, remaining

    def reset(self) -> None:
        """Clears client tracking (useful for isolated tests)."""
        self._clients.clear()


# Default singleton instance
rate_limiter = InMemoryRateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Enforces sliding-window rate limits across incoming API requests.
    Excludes testing and local diagnostics if needed.
    """

    def __init__(self, app, limiter: Optional[InMemoryRateLimiter] = None) -> None:
        super().__init__(app)
        self.limiter = limiter or rate_limiter

    async def dispatch(self, request: Request, call_next) -> Response:
        # Bypass rate limits for health ping probes
        if request.url.path in {"/health", "/api/v1/ping"}:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        is_limited, remaining = self.limiter.is_rate_limited(client_ip)

        if is_limited:
            logger.warning(f"Rate limit exceeded for client: {client_ip}")
            response = JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": {
                        "code": "TOO_MANY_REQUESTS",
                        "message": "Rate limit exceeded. Please slow down your requests.",
                        "details": None,
                    },
                },
            )
            response.headers["Retry-After"] = str(self.limiter.window_seconds)
            response.headers["X-RateLimit-Limit"] = str(self.limiter.max_requests)
            response.headers["X-RateLimit-Remaining"] = "0"
            return response

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.limiter.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
        return response
