"""
Rate limiting middleware for API endpoints.
"""

import time
from typing import Dict, Optional

from fastapi import Request, HTTPException, status
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import get_logger

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware based on client IP addresses."""

    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        whitelist_ips: Optional[list] = None
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.whitelist_ips = whitelist_ips or []

        # In-memory storage for request tracking (in production, use Redis)
        self.requests: Dict[str, list] = {}

    async def dispatch(self, request: Request, call_next):
        try:
            # Get client IP
            client_ip = self._get_client_ip(request)

            # Skip rate limiting for whitelisted IPs
            if client_ip in self.whitelist_ips:
                return await call_next(request)

            # Check rate limits
            if self._is_rate_limited(client_ip):
                logger.warning(
                    f"Rate limit exceeded for IP: {client_ip}",
                    extra={
                        "ip": client_ip,
                        "path": request.url.path,
                        "method": request.method
                    }
                )
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Please try again later."
                )

            # Record request
            self._record_request(client_ip)

            # Process request
            response = await call_next(request)
            return response

        except HTTPException:
            # Re-raise HTTP exceptions (like rate limiting)
            raise
        except Exception as e:
            # Log unexpected errors but don't fail the request
            logger.error(
                f"Unexpected error in rate limiting middleware: {str(e)}",
                extra={
                    "error_type": type(e).__name__,
                    "path": str(request.url.path) if hasattr(request, 'url') else 'unknown',
                    "method": request.method if hasattr(request, 'method') else 'unknown'
                },
                exc_info=True
            )
            # Continue processing the request even if rate limiting fails
            try:
                return await call_next(request)
            except Exception as fallback_error:
                logger.error(
                    f"Critical error in rate limiting fallback: {str(fallback_error)}",
                    extra={
                        "error_type": type(fallback_error).__name__,
                        "original_error": str(e)
                    },
                    exc_info=True
                )
                # Re-raise this critical error to be handled by global exception handlers
                raise

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request headers."""
        # Check for forwarded IP first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        return request.client.host if request.client else "unknown"

    def _is_rate_limited(self, ip: str) -> bool:
        """Check if IP has exceeded rate limits."""
        current_time = time.time()

        if ip not in self.requests:
            self.requests[ip] = []

        # Remove old requests (older than 1 hour)
        self.requests[ip] = [
            req_time for req_time in self.requests[ip]
            if current_time - req_time < 3600  # 1 hour
        ]

        # Check per-minute limit
        requests_last_minute = [
            req_time for req_time in self.requests[ip]
            if current_time - req_time < 60  # 1 minute
        ]

        if len(requests_last_minute) >= self.requests_per_minute:
            return True

        # Check per-hour limit
        if len(self.requests[ip]) >= self.requests_per_hour:
            return True

        return False

    def _record_request(self, ip: str):
        """Record a request for rate limiting."""
        current_time = time.time()
        if ip not in self.requests:
            self.requests[ip] = []
        self.requests[ip].append(current_time)


class AuthRateLimitMiddleware(BaseHTTPMiddleware):
    """Stricter rate limiting specifically for auth endpoints."""

    def __init__(self, app, max_attempts: int = 5, window_minutes: int = 15):
        super().__init__(app)
        self.max_attempts = max_attempts
        self.window_minutes = window_minutes
        self.attempts: Dict[str, list] = {}

    async def dispatch(self, request: Request, call_next):
        try:
            # Only apply to auth endpoints (with safe path checking)
            path = str(request.url.path) if hasattr(request, 'url') else ''
            if not path.startswith("/api/auth/"):
                return await call_next(request)

            # Stricter limits for login and refresh endpoints
            if path in ["/api/auth/login", "/api/auth/refresh"]:
                client_ip = self._get_client_ip(request)

                if self._is_auth_rate_limited(client_ip):
                    logger.warning(
                        f"Auth rate limit exceeded for IP: {client_ip}",
                        extra={
                            "ip": client_ip,
                            "path": path,
                            "method": request.method if hasattr(request, 'method') else 'unknown'
                        }
                    )
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Too many authentication attempts. Please try again later."
                    )

                self._record_auth_attempt(client_ip)

            return await call_next(request)

        except HTTPException:
            # Re-raise HTTP exceptions (like rate limiting)
            raise
        except Exception as e:
            # Log unexpected errors but don't fail auth requests
            logger.error(
                f"Unexpected error in auth rate limiting middleware: {str(e)}",
                extra={
                    "error_type": type(e).__name__,
                    "path": str(request.url.path) if hasattr(request, 'url') else 'unknown',
                    "method": request.method if hasattr(request, 'method') else 'unknown'
                },
                exc_info=True
            )
            # Continue processing the request even if rate limiting fails
            try:
                return await call_next(request)
            except Exception as fallback_error:
                logger.error(
                    f"Critical error in auth rate limiting fallback: {str(fallback_error)}",
                    extra={
                        "error_type": type(fallback_error).__name__,
                        "original_error": str(e)
                    },
                    exc_info=True
                )
                # Re-raise this critical error to be handled by global exception handlers
                raise

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request headers."""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        return request.client.host if request.client else "unknown"

    def _is_auth_rate_limited(self, ip: str) -> bool:
        """Check if IP has exceeded auth rate limits."""
        current_time = time.time()

        if ip not in self.attempts:
            self.attempts[ip] = []

        # Remove old attempts
        window_seconds = self.window_minutes * 60
        self.attempts[ip] = [
            attempt_time for attempt_time in self.attempts[ip]
            if current_time - attempt_time < window_seconds
        ]

        return len(self.attempts[ip]) >= self.max_attempts

    def _record_auth_attempt(self, ip: str):
        """Record an auth attempt."""
        current_time = time.time()
        if ip not in self.attempts:
            self.attempts[ip] = []
        self.attempts[ip].append(current_time)