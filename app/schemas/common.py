"""
Common schemas following FastAPI and Nuxt best practices.
Provides standardized {status, code, data} format for all API responses.
"""

from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar('T')


class BaseResponse(BaseModel, Generic[T]):
    """
    Base response schema for all API endpoints.
    Follows the {status, code, data} format expected by Nuxt frontend.
    """
    status: str = Field(..., description="Response status: 'success' or 'error'")
    code: int = Field(..., description="HTTP status code")
    data: Optional[T] = Field(None, description="Response data or error details")
    message: Optional[str] = Field(None, description="Optional message for additional context")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "code": 200,
                "data": {"key": "value"},
                "message": "Operation completed successfully"
            }
        }


class SuccessResponse(BaseResponse[T]):
    """Success response with data."""
    status: str = Field(default="success", description="Success status")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "code": 200,
                "data": {"id": 1, "name": "Example"},
                "message": "Resource retrieved successfully"
            }
        }


class ErrorResponse(BaseResponse[T]):
    """Error response with error details."""
    status: str = Field(default="error", description="Error status")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "error",
                "code": 400,
                "data": {"field": "username", "message": "Username is required"},
                "message": "Validation failed"
            }
        }


class PaginatedData(BaseModel, Generic[T]):
    """Paginated response data structure."""
    items: List[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number (1-based)")
    size: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")

    class Config:
        json_schema_extra = {
            "example": {
                "items": [{"id": 1, "name": "Item 1"}],
                "total": 100,
                "page": 1,
                "size": 10,
                "pages": 10
            }
        }


class PaginatedResponse(BaseResponse[PaginatedData[T]]):
    """Paginated success response."""
    status: str = Field(default="success", description="Success status")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "code": 200,
                "data": {
                    "items": [{"id": 1, "name": "Item 1"}],
                    "total": 100,
                    "page": 1,
                    "size": 10,
                    "pages": 10
                },
                "message": "Items retrieved successfully"
            }
        }


class ValidationErrorDetail(BaseModel):
    """Individual validation error detail."""
    field: str = Field(..., description="Field name")
    message: str = Field(..., description="Error message")
    value: Optional[Any] = Field(None, description="Invalid value")

    class Config:
        json_schema_extra = {
            "example": {
                "field": "email",
                "message": "Invalid email format",
                "value": "not-an-email"
            }
        }


class ValidationErrorResponse(ErrorResponse[List[ValidationErrorDetail]]):
    """Validation error response with field details."""
    message: Optional[str] = Field(default="Validation failed", description="Validation error message")


# Legacy schemas for backward compatibility
class LegacyErrorResponse(BaseModel):
    """Legacy error response schema (for backward compatibility)."""
    error: str
    status_code: int
    path: Optional[str] = None
    request_id: Optional[str] = None
    details: Optional[List[ValidationErrorDetail]] = None


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str
    version: str
    environment: str
    timestamp: Optional[str] = None


# Type aliases for common responses
SuccessResponseDict = dict[str, Any]
ErrorResponseDict = dict[str, Any]
PaginatedResponseDict = dict[str, Any]