"""
Comprehensive logging configuration for FastAPI application.
Optimized for Vercel deployment and production monitoring.
"""

import logging
import sys
import json
import os
from datetime import datetime
from typing import Any, Dict
from pathlib import Path

from pythonjsonlogger import jsonlogger
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class StructuredFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for structured logging."""

    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]):
        """Add structured fields to log records."""
        super().add_fields(log_record, record, message_dict)

        # Add timestamp if not present
        if not log_record.get('timestamp'):
            log_record['timestamp'] = datetime.utcnow().isoformat()

        # Add log level
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname

        # Add application info
        log_record['application'] = 'watchstore-api'
        log_record['environment'] = os.getenv('VERCEL_ENV', 'development')

        # Add request context if available
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id
        if hasattr(record, 'user_id'):
            log_record['user_id'] = record.user_id
        if hasattr(record, 'ip_address'):
            log_record['ip_address'] = record.ip_address


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log HTTP requests and responses."""

    async def dispatch(self, request: Request, call_next):
        # Generate unique request ID
        import uuid
        request_id = str(uuid.uuid4())

        # Get request info
        method = request.method
        url = str(request.url)
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        # Get user info if authenticated
        user_id = None
        try:
            # Try to get user from request state (set by auth middleware)
            if hasattr(request.state, 'current_user'):
                user_id = request.state.current_user.username
        except:
            pass

        # Log request start
        logger = logging.getLogger("request")
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

        # Process request
        start_time = datetime.utcnow()
        try:
            response = await call_next(request)
            process_time = (datetime.utcnow() - start_time).total_seconds()

            # Log successful response
            logger.info(
                "Request completed",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "url": url,
                    "status_code": response.status_code,
                    "process_time_ms": round(process_time * 1000, 2),
                    "user_id": user_id
                }
            )

            # Add request ID to response headers for debugging
            response.headers["X-Request-ID"] = request_id
            return response

        except Exception as e:
            process_time = (datetime.utcnow() - start_time).total_seconds()

            # Log error
            logger.error(
                "Request failed",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "url": url,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "process_time_ms": round(process_time * 1000, 2),
                    "user_id": user_id
                },
                exc_info=True
            )

            # Add request ID to error response
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "data": "Something went wrong. Please try again later.",
                    "request_id": request_id
                }
            )


def setup_logging():
    """Setup comprehensive logging for the application."""

    # Determine environment
    is_production = os.getenv('VERCEL_ENV') == 'production'
    is_development = not is_production

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if is_development else logging.INFO)

    # Clear existing handlers
    root_logger.handlers.clear()

    # Console handler (for Vercel and local development)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if is_development else logging.INFO)

    # Use structured JSON formatter for production, readable format for development
    if is_production:
        formatter = StructuredFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler for critical errors (only if not on Vercel)
    if not os.getenv('VERCEL'):
        try:
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)

            file_handler = logging.FileHandler(log_dir / "app.log")
            file_handler.setLevel(logging.WARNING)
            file_handler.setFormatter(StructuredFormatter())
            root_logger.addHandler(file_handler)
        except Exception:
            # If file logging fails, continue without it
            pass

    # Configure specific loggers
    loggers = {
        "uvicorn": logging.WARNING,
        "uvicorn.access": logging.WARNING,
        "sqlalchemy.engine": logging.WARNING,
        "sqlalchemy.pool": logging.WARNING,
        "httpx": logging.WARNING,
        "watchstore_api": logging.INFO,
        "request": logging.INFO,
        "auth": logging.INFO,
        "database": logging.WARNING,
        "security": logging.WARNING,
        "business_logic": logging.INFO,
        "external_apis": logging.INFO,
    }

    for logger_name, level in loggers.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)

    # Log startup
    startup_logger = logging.getLogger("watchstore_api")
    startup_logger.info(
        "Application logging initialized",
        extra={
            "environment": os.getenv('VERCEL_ENV', 'development'),
            "python_version": sys.version,
            "log_level": "DEBUG" if is_development else "INFO"
        }
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    return logging.getLogger(name)