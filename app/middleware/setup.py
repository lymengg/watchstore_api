"""
Middleware setup and configuration functions.
"""

from fastapi import FastAPI

from app.core.logging import get_logger
from .logging import RequestLoggingMiddleware
from .security import SecurityHeadersMiddleware
from .rate_limit import RateLimitMiddleware, AuthRateLimitMiddleware

logger = get_logger(__name__)


def setup_middleware(app: FastAPI) -> None:
    """Setup all middleware for the FastAPI application.

    Note: Middleware is applied in reverse order (last added runs first).
    RequestLoggingMiddleware should be added last so it runs first.
    """

    # Add middleware in correct order (last added runs first)

    # 1. Auth-specific rate limiting (runs last - most specific)
    app.add_middleware(
        AuthRateLimitMiddleware,
        max_attempts=5,           # 5 attempts
        window_minutes=15         # per 15 minutes
    )

    # 2. General rate limiting
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=60,  # 60 requests per minute
        requests_per_hour=1000   # 1000 requests per hour
    )

    # 3. Security headers
    app.add_middleware(SecurityHeadersMiddleware)

    # 4. Request logging (runs first - sets up request_id)
    app.add_middleware(RequestLoggingMiddleware)

    logger.info(
        "Middleware configured successfully",
        extra={
            "middleware": [
                "RequestLoggingMiddleware",
                "SecurityHeadersMiddleware",
                "RateLimitMiddleware",
                "AuthRateLimitMiddleware"
            ]
        }
    )