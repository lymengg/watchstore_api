"""
Users API v1 endpoints with user profile management functionality.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi.responses import JSONResponse
import logging

from app.api.deps import get_current_user, get_db
from app import auth_utils, crud, schemas
from app.utils.responses import success, error, bad_request
from app.exceptions import ValidationError

router = APIRouter()


@router.get("/me")
def get_me(current_user = Depends(get_current_user)):
    """Get current user's profile information."""
    return success({
        "username": current_user.username,
        "email": current_user.email,
        "phone_number": current_user.phone_number,
        "role": getattr(current_user, "role", None),
    }, message="User profile retrieved successfully")


@router.put("/me")
def update_me(
    body: schemas.UserUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile information."""
    # Enforce uniqueness constraints if fields are changing
    if body.username and body.username != current_user.username:
        if crud.get_user_by_username(db, body.username):
            raise ValidationError("Username already exists", field="username")

    if body.email and body.email != current_user.email:
        if crud.get_user_by_email(db, body.email):
            raise ValidationError("Email already exists", field="email")

    if body.phone_number and body.phone_number != current_user.phone_number:
        if crud.get_user_by_phone_number(db, body.phone_number):
            raise ValidationError("Phone number already exists", field="phone_number")

    updated = crud.update_user_profile(
        db,
        current_user,
        username=body.username,
        email=body.email,
        phone_number=body.phone_number,
    )
    return success({
        "username": updated.username,
        "email": updated.email,
        "phone_number": updated.phone_number,
        "role": getattr(updated, "role", None),
    }, message="User profile updated successfully")


@router.post("/change-password")
def change_password(
    body: schemas.ChangePasswordRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change current user's password."""
    if not auth_utils.verify_password(body.current_password, current_user.hashed_password):
        raise ValidationError("Current password is incorrect", field="current_password")

    crud.update_user_password(db, current_user, body.new_password)
    return success(None, message="Password updated successfully")