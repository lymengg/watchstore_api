"""
Request and response logging middleware with robust error handling.
"""

from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import get_logger

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log HTTP requests and responses with robust error handling."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        import time
        import uuid

        # Generate request_id and add to request state
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Get request info
        method = request.method
        url = str(request.url)
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "unknown")
        user_id = self._get_user_id(request)
        start_time = time.time()

        # Log request start
        logger.info(
            "Request started",
            extra={
                "request_id": request_id,
                "method": method,
                "url": url,
                "ip_address": client_ip,
                "user_agent": user_agent,
                "user_id": user_id
            }
        )

        try:
            response = await call_next(request)
            process_time = (time.time() - start_time) * 1000

            # Add headers to response (safely handle potential errors)
            try:
                response.headers["X-Request-ID"] = request_id
                response.headers["X-Process-Time"] = str(round(process_time, 2))
            except Exception as header_error:
                logger.warning(
                    f"Failed to add headers to response: {header_error}",
                    extra={"request_id": request_id}
                )

            # Log successful response
            logger.info(
                "Request completed",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "url": url,
                    "status_code": response.status_code,
                    "process_time_ms": round(process_time, 2),
                    "user_id": user_id
                }
            )

            return response

        except Exception as e:
            process_time = (time.time() - start_time) * 1000

            # Log error with full context
            logger.error(
                "Request failed",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "url": url,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "process_time_ms": round(process_time, 2),
                    "user_id": user_id
                },
                exc_info=True
            )

            # Create error response with request_id
            try:
                return JSONResponse(
                    status_code=500,
                    content={
                        "status": "error",
                        "code": 500,
                        "data": {
                            "error": "Internal server error",
                            "request_id": request_id
                        },
                        "message": "An unexpected error occurred. Please try again later."
                    },
                    headers={"X-Request-ID": request_id}
                )
            except Exception as response_error:
                logger.error(
                    f"Failed to create error response: {response_error}",
                    extra={"request_id": request_id},
                    exc_info=True
                )
                # Last resort - return a minimal error response
                return JSONResponse(
                    status_code=500,
                    content={"error": "Internal server error"}
                )

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request, considering proxies."""
        try:
            # Check for forwarded headers
            forwarded_for = request.headers.get("X-Forwarded-For")
            if forwarded_for:
                return forwarded_for.split(",")[0].strip()

            real_ip = request.headers.get("X-Real-IP")
            if real_ip:
                return real_ip

            return request.client.host if request.client else "unknown"
        except Exception:
            return "unknown"

    def _get_user_id(self, request: Request) -> int | None:
        """Get user ID from request state if authenticated."""
        try:
            if hasattr(request.state, "current_user") and request.state.current_user:
                return getattr(request.state.current_user, "id", None)
        except Exception:
            pass
        return None