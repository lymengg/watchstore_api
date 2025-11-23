"""
Custom exception handlers following FastAPI best practices.
"""

import logging
import uuid
from typing import Union

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.core.logging import get_logger
from app.schemas.common import ErrorResponse, ValidationErrorDetail
from app.utils.responses import error, create_validation_error_response

logger = get_logger(__name__)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""
    logger.warning(
        f"HTTP {exc.status_code} error",
        extra={
            "method": request.method,
            "url": str(request.url),
            "status_code": exc.status_code,
            "error_detail": exc.detail,
            "path": request.url.path,
        }
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error(
            data=exc.detail,
            message=exc.detail,
            http_status=exc.status_code
        )
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle request validation errors."""
    logger.warning(
        "Request validation failed",
        extra={
            "method": request.method,
            "url": str(request.url),
            "validation_errors": exc.errors(),
            "path": request.url.path,
        }
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="Validation failed",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            path=request.url.path,
            details=[
                ValidationErrorDetail(
                    field=error["loc"][-1],
                    message=error["msg"],
                    type=error["type"]
                )
                for error in exc.errors()
            ]
        ).model_dump()
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle SQLAlchemy database errors."""
    request_id = str(uuid.uuid4())

    logger.error(
        "Database error occurred",
        extra={
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "path": request.url.path,
        },
        exc_info=True
    )

    # Handle specific database errors
    if isinstance(exc, IntegrityError):
        error_message = "Database integrity constraint violation"
        status_code = status.HTTP_400_BAD_REQUEST
    else:
        error_message = "Internal database error"
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(
            error=error_message,
            status_code=status_code,
            path=request.url.path,
            request_id=request_id
        ).model_dump()
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all unhandled exceptions."""
    request_id = str(uuid.uuid4())

    # Get additional context for better debugging
    request_body = None
    try:
        # Try to get request body for debugging (only for POST/PUT/PATCH)
        if request.method in ["POST", "PUT", "PATCH"]:
            request_body = await request.body()
            request_body = request_body.decode("utf-8", errors="ignore")[:1000]  # Limit size
    except:
        request_body = "Failed to read request body"

    # Log the full exception with context
    logger.error(
        "Unhandled exception occurred",
        extra={
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": dict(request.headers),
            "request_body": request_body,
        },
        exc_info=True
    )

    # Return user-friendly error using the correct ErrorResponse schema
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            data={
                "error": "Internal server error",
                "path": request.url.path,
                "request_id": request_id
            },
            message="An unexpected error occurred. Please try again later."
        ).model_dump()
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """Setup all exception handlers for the FastAPI application."""

    # Custom exception handlers
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    # Starlette HTTP exceptions
    app.add_exception_handler(
        StarletteHTTPException,
        http_exception_handler
    )

    logger.info("Exception handlers configured successfully")


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: dict = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(AppException):
    """Resource not found exception."""

    def __init__(self, resource: str, identifier: Union[str, int] = None):
        message = f"{resource} not found"
        if identifier:
            message += f" with identifier: {identifier}"
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND
        )


class PermissionError(AppException):
    """Permission denied exception."""

    def __init__(self, message: str = "Permission denied"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN
        )


class AuthenticationError(AppException):
    """Authentication failed exception."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class ValidationError(AppException):
    """Validation error exception."""

    def __init__(self, message: str, field: str = None):
        details = {}
        if field:
            details["field"] = field
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


class ConflictError(AppException):
    """Resource conflict exception."""

    def __init__(self, message: str = "Resource conflict"):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT
        )


class RateLimitError(AppException):
    """Rate limit exceeded exception."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )