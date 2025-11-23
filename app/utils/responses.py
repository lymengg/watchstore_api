"""
Response utility functions for creating standardized API responses.
Provides helper functions to create consistent {status, code, data} responses.
"""

from typing import Any, List, Optional, TypeVar, Union
from fastapi import HTTPException, status

from app.schemas.common import (
    SuccessResponse,
    ErrorResponse,
    PaginatedResponse,
    PaginatedData,
    ValidationErrorDetail,
    ValidationErrorResponse,
    BaseResponse
)

T = TypeVar('T')


def create_success_response(
    data: Optional[T] = None,
    message: Optional[str] = None,
    http_status: int = status.HTTP_200_OK
) -> SuccessResponse[T]:
    """
    Create a standardized success response.

    Args:
        data: Response data (optional)
        message: Optional success message
        http_status: HTTP status code (default 200)

    Returns:
        SuccessResponse with standardized format
    """
    return SuccessResponse[T](
        status="success",
        code=http_status,
        data=data,
        message=message
    )


def create_error_response(
    data: Optional[T] = None,
    message: Optional[str] = None,
    http_status: int = status.HTTP_400_BAD_REQUEST
) -> ErrorResponse[T]:
    """
    Create a standardized error response.

    Args:
        data: Error details (optional)
        message: Optional error message
        http_status: HTTP status code (default 400)

    Returns:
        ErrorResponse with standardized format
    """
    return ErrorResponse[T](
        status="error",
        code=http_status,
        data=data,
        message=message
    )


def create_paginated_response(
    items: List[T],
    total: int,
    page: int,
    size: int,
    message: Optional[str] = None
) -> PaginatedResponse[T]:
    """
    Create a standardized paginated response.

    Args:
        items: List of items for current page
        total: Total number of items
        page: Current page number (1-based)
        size: Items per page
        message: Optional success message

    Returns:
        PaginatedResponse with standardized format
    """
    # Calculate total pages
    pages = (total + size - 1) // size if size > 0 else 0

    paginated_data = PaginatedData[T](
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages
    )

    return PaginatedResponse[T](
        status="success",
        code=status.HTTP_200_OK,
        data=paginated_data,
        message=message or f"Retrieved {len(items)} items"
    )


def create_validation_error_response(
    validation_errors: List[ValidationErrorDetail],
    message: Optional[str] = None
) -> ValidationErrorResponse:
    """
    Create a standardized validation error response.

    Args:
        validation_errors: List of validation error details
        message: Optional error message

    Returns:
        ValidationErrorResponse with field-level error details
    """
    return ValidationErrorResponse(
        status="error",
        code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        data=validation_errors,
        message=message or "Validation failed"
    )


def success(data: Optional[T] = None, message: Optional[str] = None) -> dict:
    """
    Quick success response creator that returns a dict.

    Args:
        data: Response data (optional)
        message: Optional success message

    Returns:
        Dict in standardized format
    """
    return {
        "status": "success",
        "code": status.HTTP_200_OK,
        "data": data,
        "message": message
    }


def created(data: Optional[T] = None, message: Optional[str] = None) -> dict:
    """
    Quick created response (201) that returns a dict.

    Args:
        data: Created resource data (optional)
        message: Optional success message

    Returns:
        Dict in standardized format with 201 status code
    """
    return {
        "status": "success",
        "code": status.HTTP_201_CREATED,
        "data": data,
        "message": message or "Resource created successfully"
    }


def error(data: Optional[T] = None, message: Optional[str] = None, http_status: int = status.HTTP_400_BAD_REQUEST) -> dict:
    """
    Quick error response creator that returns a dict.

    Args:
        data: Error details (optional)
        message: Optional error message
        http_status: HTTP status code (default 400)

    Returns:
        Dict in standardized error format
    """
    return {
        "status": "error",
        "code": http_status,
        "data": data,
        "message": message
    }


def paginated(
    items: List[T],
    total: int,
    page: int,
    size: int,
    message: Optional[str] = None
) -> dict:
    """
    Quick paginated response creator that returns a dict.

    Args:
        items: List of items for current page
        total: Total number of items
        page: Current page number (1-based)
        size: Items per page
        message: Optional success message

    Returns:
        Dict in standardized paginated format
    """
    pages = (total + size - 1) // size if size > 0 else 0

    return {
        "status": "success",
        "code": status.HTTP_200_OK,
        "data": {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "pages": pages
        },
        "message": message or f"Retrieved {len(items)} items (page {page} of {pages})"
    }


def no_content(message: Optional[str] = None) -> dict:
    """
    Quick no content response (204) that returns a dict.

    Args:
        message: Optional success message

    Returns:
        Dict in standardized format with 204 status code
    """
    return {
        "status": "success",
        "code": status.HTTP_204_NO_CONTENT,
        "data": None,
        "message": message or "Operation completed successfully"
    }


def not_found(resource: str = "Resource") -> dict:
    """
    Quick not found response (404) that returns a dict.

    Args:
        resource: Name of the resource that was not found

    Returns:
        Dict in standardized error format with 404 status code
    """
    return {
        "status": "error",
        "code": status.HTTP_404_NOT_FOUND,
        "data": None,
        "message": f"{resource} not found"
    }


def bad_request(message: str = "Bad request", data: Optional[Any] = None) -> dict:
    """
    Quick bad request response (400) that returns a dict.

    Args:
        message: Error message
        data: Additional error details (optional)

    Returns:
        Dict in standardized error format with 400 status code
    """
    return {
        "status": "error",
        "code": status.HTTP_400_BAD_REQUEST,
        "data": data,
        "message": message
    }


def unauthorized(message: str = "Unauthorized") -> dict:
    """
    Quick unauthorized response (401) that returns a dict.

    Args:
        message: Error message

    Returns:
        Dict in standardized error format with 401 status code
    """
    return {
        "status": "error",
        "code": status.HTTP_401_UNAUTHORIZED,
        "data": None,
        "message": message
    }


def forbidden(message: str = "Forbidden") -> dict:
    """
    Quick forbidden response (403) that returns a dict.

    Args:
        message: Error message

    Returns:
        Dict in standardized error format with 403 status code
    """
    return {
        "status": "error",
        "code": status.HTTP_403_FORBIDDEN,
        "data": None,
        "message": message
    }


def internal_server_error(message: str = "Internal server error", data: Optional[Any] = None) -> dict:
    """
    Quick internal server error response (500) that returns a dict.

    Args:
        message: Error message
        data: Additional error details (optional)

    Returns:
        Dict in standardized error format with 500 status code
    """
    return {
        "status": "error",
        "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "data": data,
        "message": message
    }