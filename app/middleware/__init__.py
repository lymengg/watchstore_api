"""
Middleware package for the FastAPI application.

This package provides various middleware components for:
- Request logging
- Rate limiting
- Security headers
- Base middleware utilities

Usage:
    from app.middleware import setup_middleware
    app = FastAPI()
    setup_middleware(app)
"""

from .base import BaseMiddleware, TimedMiddleware
from .logging import RequestLoggingMiddleware
from .security import SecurityHeadersMiddleware
from .rate_limit import RateLimitMiddleware, AuthRateLimitMiddleware
from .setup import setup_middleware

__all__ = [
    # Base utilities
    "BaseMiddleware",
    "TimedMiddleware",

    # Specific middleware
    "RequestLoggingMiddleware",
    "SecurityHeadersMiddleware",
    "RateLimitMiddleware",
    "AuthRateLimitMiddleware",

    # Setup function
    "setup_middleware"
]