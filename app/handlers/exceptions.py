"""
Global exception handlers for standardized API responses.
"""

from typing import Union
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.utils.response import APIResponse


def setup_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers for consistent error responses."""

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        """Handle HTTPException with standardized response format."""
        return APIResponse.error(
            message=str(exc.detail) if exc.detail else "HTTP error occurred",
            http_status=exc.status_code
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """Handle validation errors with detailed field information."""
        # Format validation errors for better frontend handling
        error_details = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            error_details.append({
                "field": field,
                "message": error["msg"],
                "type": error["type"]
            })

        return APIResponse.error(
            message="Validation failed",
            http_status=422,
            details=error_details
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        """Handle ValueError with standardized response."""
        return APIResponse.error(
            message=str(exc) or "Invalid value provided",
            http_status=400
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle unexpected exceptions with generic error message."""
        # Log the detailed error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Unexpected error: {type(exc).__name__}: {str(exc)}", exc_info=True)

        return APIResponse.error(
            message="An unexpected error occurred. Please try again later.",
            http_status=500
        )