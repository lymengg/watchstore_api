"""
Security headers middleware for FastAPI applications with robust error handling.
"""

from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import get_logger

logger = get_logger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to HTTP responses with error handling."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)

            # Add security headers safely
            security_headers = {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "X-XSS-Protection": "1; mode=block",
                "Referrer-Policy": "strict-origin-when-cross-origin",
                "Permissions-Policy": "geolocation=(), microphone=(), camera=(), payment=()",
                "Cross-Origin-Embedder-Policy": "require-corp",
                "Cross-Origin-Resource-Policy": "same-origin"
            }

            # Add each security header safely
            for header_name, header_value in security_headers.items():
                try:
                    response.headers[header_name] = header_value
                except Exception as header_error:
                    logger.warning(
                        f"Failed to set security header {header_name}: {header_error}",
                        extra={"header": header_name, "value": header_value}
                    )

            # Add HSTS in production (HTTPS only)
            if request.url.scheme == "https":
                try:
                    response.headers["Strict-Transport-Security"] = (
                        "max-age=31536000; includeSubDomains"
                    )
                except Exception as hsts_error:
                    logger.warning(
                        f"Failed to set HSTS header: {hsts_error}"
                    )

            # Remove server header to avoid information disclosure (safely)
            try:
                if "server" in response.headers:
                    del response.headers["server"]
            except Exception as server_header_error:
                logger.warning(
                    f"Failed to remove server header: {server_header_error}"
                )

            return response

        except Exception as e:
            # Log the error but don't fail the request
            logger.error(
                f"Error in security headers middleware: {str(e)}",
                extra={"error_type": type(e).__name__},
                exc_info=True
            )
            # Continue processing the request even if security headers fail
            return await call_next(request)