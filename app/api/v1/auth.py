"""
Authentication API v1 endpoints following FastAPI best practices.
"""

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.auth import create_access_token, create_refresh_token, verify_token
from app.core.logging import get_logger
from app.api.deps import get_current_user, get_db
from app.schemas.auth import Token, UserCreate, UserResponse, PasswordChange, RefreshTokenRequest
from app.services.user_service import UserService
from app.config import settings
from app.utils.responses import success, created, error

router = APIRouter()
logger = get_logger(__name__)


@router.post("/register", response_model=UserResponse)
def register(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate
) -> Any:
    """Register a new user."""
    user_service = UserService(db)

    # Log registration attempt
    logger.info(
        "User registration attempt",
        extra={
            "username": user_in.username,
            "email": user_in.email,
            "phone_number": user_in.phone_number,
            "action": "registration_attempt"
        }
    )

    try:
        # Check if user already exists
        if user_service.get_by_username(user_in.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )

        if user_service.get_by_email(user_in.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        if user_service.get_by_phone_number(user_in.phone_number):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered"
            )

        # Create new user
        user = user_service.create(user_in)

        logger.info(
            "User registration successful",
            extra={
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "action": "registration_success"
            }
        )

        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Registration failed",
            extra={
                "username": user_in.username,
                "email": user_in.email,
                "error": str(e),
                "action": "registration_failed"
            },
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again later."
        )


@router.post("/login")
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """OAuth2 compatible token login, get an access token for future requests."""
    user_service = UserService(db)

    logger.info(
        "User login attempt",
        extra={
            "username": form_data.username,
            "action": "login_attempt"
        }
    )

    try:
        # Authenticate user
        user = user_service.authenticate(
            username=form_data.username,
            password=form_data.password
        )

        if not user:
            logger.warning(
                "Login failed - invalid credentials",
                extra={
                    "username": form_data.username,
                    "reason": "invalid_credentials",
                    "action": "login_failed"
                }
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create tokens
        access_token_expires = timedelta(minutes=settings.JWT_ACCESS_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(minutes=settings.JWT_REFRESH_EXPIRE_MINUTES)

        access_token = create_access_token(
            subject=user.username,
            expires_delta=access_token_expires,
            role=user.role
        )

        refresh_token = create_refresh_token(
            subject=user.username,
            expires_delta=refresh_token_expires,
            role=user.role
        )

        logger.info(
            "User login successful",
            extra={
                "user_id": user.id,
                "username": user.username,
                "role": user.role,
                "action": "login_success"
            }
        )

        return success(
            data={
                "test_field": "TEST_CHANGE_TO_VERIFY_RELOAD",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": settings.JWT_ACCESS_EXPIRE_MINUTES * 60,
                "username": user.username,
                "role": user.role,
                "email": user.email,
                "phone_number": user.phone_number,
            },
            message="Login successful"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Login failed",
            extra={
                "username": form_data.username,
                "error": str(e),
                "action": "login_failed"
            },
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again later."
        )


@router.post("/refresh")
def refresh_token(
    *,  # Force keyword arguments
    db: Session = Depends(get_db),
    token_request: RefreshTokenRequest  # Use proper Pydantic schema
) -> Any:
    """Refresh access token using refresh token."""
    user_service = UserService(db)

    logger.info(
        "Token refresh attempt",
        extra={"action": "refresh_attempt"}
    )

    try:
        # Verify refresh token
        payload = verify_token(token_request.refresh_token, token_type="refresh")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        username = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        # Get user
        user = user_service.get_by_username(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        # Create new tokens
        access_token_expires = timedelta(minutes=settings.JWT_ACCESS_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(minutes=settings.JWT_REFRESH_EXPIRE_MINUTES)

        new_access_token = create_access_token(
            subject=user.username,
            expires_delta=access_token_expires,
            role=user.role
        )

        new_refresh_token = create_refresh_token(
            subject=user.username,
            expires_delta=refresh_token_expires,
            role=user.role
        )

        logger.info(
            "Token refresh successful",
            extra={
                "user_id": user.id,
                "username": user.username,
                "action": "refresh_success"
            }
        )

        return success(
            data={
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
                "token_type": "bearer",
                "expires_in": settings.JWT_ACCESS_EXPIRE_MINUTES * 60
            },
            message="Token refreshed successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Token refresh failed",
            extra={
                "error": str(e),
                "action": "refresh_failed"
            },
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user = Depends(get_current_user)
) -> Any:
    """Get current user information."""
    return success(
        data={
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "phone_number": current_user.phone_number,
            "role": current_user.role,
            "is_active": current_user.is_active,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
            "updated_at": current_user.updated_at.isoformat() if current_user.updated_at else None,
        },
        message="User profile retrieved successfully"
    )


@router.post("/change-password")
def change_password(
    *,
    db: Session = Depends(get_db),
    password_in: PasswordChange,
    current_user = Depends(get_current_user)
) -> Any:
    """Change current user password."""
    user_service = UserService(db)

    logger.info(
        "Password change attempt",
        extra={
            "user_id": current_user.id,
            "username": current_user.username,
            "action": "password_change_attempt"
        }
    )

    try:
        # Verify current password
        if not user_service.authenticate(
            username=current_user.username,
            password=password_in.current_password
        ):
            logger.warning(
                "Password change failed - incorrect current password",
                extra={
                    "user_id": current_user.id,
                    "username": current_user.username,
                    "reason": "incorrect_current_password",
                    "action": "password_change_failed"
                }
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect current password"
            )

        # Update password
        user_service.update_password(
            user=current_user,
            new_password=password_in.new_password
        )

        logger.info(
            "Password change successful",
            extra={
                "user_id": current_user.id,
                "username": current_user.username,
                "action": "password_change_success"
            }
        )

        return {"message": "Password updated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Password change failed",
            extra={
                "user_id": current_user.id,
                "username": current_user.username,
                "error": str(e),
                "action": "password_change_failed"
            },
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed. Please try again later."
        )


@router.post("/logout")
def logout(
    current_user = Depends(get_current_user)
) -> Any:
    """Logout current user."""
    logger.info(
        "User logout",
        extra={
            "user_id": current_user.id,
            "username": current_user.username,
            "action": "logout"
        }
    )

    # In a stateless JWT setup, logout is typically handled on the client side
    # by deleting the tokens. We just log the event here.
    return {"message": "Successfully logged out"}