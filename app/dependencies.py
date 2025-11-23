from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from .auth_utils import decode_access_token
from .database import get_db
from . import crud

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# 1. Returns JWT payload (dict)
def get_current_user_payload(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload

# 2. Returns user object from DB
def get_current_user(
    payload: dict = Depends(get_current_user_payload),
    db=Depends(get_db)
):
    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = crud.get_user_by_username(db, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# Dependency to allow only admin users
def require_admin(current_user=Depends(get_current_user)):
    # Verify role against database, not just JWT token
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admins only"
        )
    return current_user

# Factory for requiring one of several roles
def require_roles(*roles: str):
    def _inner(current_user=Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires role in {roles}",
            )
        return current_user
    return _inner