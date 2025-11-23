"""
Standardized API response wrapper for consistent frontend integration.
All API responses should follow the format: {code, status, data}
"""

from typing import Any, Optional
from fastapi import status
from fastapi.responses import JSONResponse


class APIResponse:
    """Standardized API response wrapper."""

    @staticmethod
    def success(
        data: Any = None,
        message: Optional[str] = None,
        http_status: int = status.HTTP_200_OK
    ) -> JSONResponse:
        """
        Create a successful API response.

        Args:
            data: Response data payload
            message: Optional success message
            http_status: HTTP status code (default: 200)

        Returns:
            JSONResponse with standardized format
        """
        content = {
            "code": http_status,
            "status": "success",
            "data": data if data is not None else message or "Operation successful"
        }
        return JSONResponse(
            status_code=http_status,
            content=content
        )

    @staticmethod
    def error(
        message: str,
        http_status: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Any] = None
    ) -> JSONResponse:
        """
        Create an error API response.

        Args:
            message: Error message
            http_status: HTTP status code (default: 400)
            details: Optional error details

        Returns:
            JSONResponse with standardized format
        """
        content = {
            "code": http_status,
            "status": "error",
            "data": message
        }

        if details is not None:
            content["details"] = details

        return JSONResponse(
            status_code=http_status,
            content=content
        )

    @staticmethod
    def created(
        data: Any = None,
        message: str = "Resource created successfully"
    ) -> JSONResponse:
        """Convenience method for 201 Created responses."""
        return APIResponse.success(
            data=data,
            message=message,
            http_status=status.HTTP_201_CREATED
        )

    @staticmethod
    def not_found(
        message: str = "Resource not found"
    ) -> JSONResponse:
        """Convenience method for 404 Not Found responses."""
        return APIResponse.error(
            message=message,
            http_status=status.HTTP_404_NOT_FOUND
        )

    @staticmethod
    def bad_request(
        message: str = "Bad request",
        details: Optional[Any] = None
    ) -> JSONResponse:
        """Convenience method for 400 Bad Request responses."""
        return APIResponse.error(
            message=message,
            http_status=status.HTTP_400_BAD_REQUEST,
            details=details
        )

    @staticmethod
    def unauthorized(
        message: str = "Unauthorized"
    ) -> JSONResponse:
        """Convenience method for 401 Unauthorized responses."""
        return APIResponse.error(
            message=message,
            http_status=status.HTTP_401_UNAUTHORIZED
        )

    @staticmethod
    def forbidden(
        message: str = "Forbidden"
    ) -> JSONResponse:
        """Convenience method for 403 Forbidden responses."""
        return APIResponse.error(
            message=message,
            http_status=status.HTTP_403_FORBIDDEN
        )

    @staticmethod
    def internal_error(
        message: str = "Internal server error"
    ) -> JSONResponse:
        """Convenience method for 500 Internal Server Error responses."""
        return APIResponse.error(
            message=message,
            http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def wrap_response(data: Any, message: str = "Success") -> dict:
    """
    Wrap data in standardized response format for endpoints that need to return dict directly.

    Args:
        data: Response data payload
        message: Success message

    Returns:
        Dictionary with standardized format
    """
    return {
        "code": 200,
        "status": "success",
        "data": data
    }


def wrap_error_response(message: str, code: int = 400) -> dict:
    """
    Wrap error message in standardized response format.

    Args:
        message: Error message
        code: Error code

    Returns:
        Dictionary with standardized error format
    """
    return {
        "code": code,
        "status": "error",
        "data": message
    }