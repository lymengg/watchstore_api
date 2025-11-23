"""
Base middleware utilities and common functionality.
"""

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class BaseMiddleware(BaseHTTPMiddleware):
    """Base middleware with common utilities."""

    def get_client_ip(self, request: Request) -> str:
        """Get client IP address from request, considering proxies."""
        # Check for forwarded headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        return request.client.host if request.client else "unknown"

    def get_user_id(self, request: Request) -> int | None:
        """Get user ID from request state if authenticated."""
        try:
            if hasattr(request.state, "current_user"):
                return request.state.current_user.id
        except AttributeError:
            pass
        except Exception:
            # Log any unexpected errors but don't fail the request
            pass
        return None

    def generate_request_id(self) -> str:
        """Generate unique request ID."""
        return str(uuid.uuid4())

    async def call_next(self, request: Request, call_next: Callable) -> Response:
        """
        Safely call the next middleware/app with proper error handling.
        """
        try:
            return await call_next(request)
        except Exception as exc:
            # Re-raise the exception to be handled by the error handlers
            # This ensures proper error responses are returned
            raise


class TimedMiddleware(BaseMiddleware):
    """Base middleware that includes request timing."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = self.generate_request_id()
        start_time = time.time()

        # Add request ID to request state for downstream use
        request.state.request_id = request_id

        try:
            response = await call_next(request)
            process_time = (time.time() - start_time) * 1000  # Convert to milliseconds

            # Add timing and request ID to response headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(round(process_time, 2))

            return response
        except Exception as e:
            process_time = (time.time() - start_time) * 1000

            # Add request ID to error response
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Something went wrong. Please try again later.",
                    "request_id": request_id
                },
                headers={"X-Request-ID": request_id}
            )