"""
API dependencies following FastAPI best practices.
"""

from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.auth import verify_token
from app.core.logging import get_logger
from app.database import get_db
from app.models import User
from app.config import settings

logger = get_logger(__name__)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=True
)


def get_current_user_optional(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> Optional[User]:
    """Get current user if token is provided, otherwise return None."""
    try:
        payload = verify_token(token, token_type="access")
        if payload is None:
            return None

        username: str = payload.get("sub")
        if username is None:
            return None

        user = db.query(User).filter(User.username == username).first()
        return user

    except JWTError:
        return None
    except Exception as e:
        logger.warning(f"Error getting current user: {e}")
        return None


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """Get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = verify_token(token, token_type="access")
        if payload is None:
            raise credentials_exception

        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current admin user."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require admin role for access."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def get_or_404(
    model_class,
    item_id: int,
    db: Session = Depends(get_db)
):
    """Generic dependency to get an item or return 404."""
    item = db.query(model_class).filter(model_class.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{model_class.__name__} not found"
        )
    return item


def verify_user_ownership(
    resource_user_id: int,
    current_user: User = Depends(get_current_user)
) -> User:
    """Verify that the current user owns the resource."""
    if resource_user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this resource"
        )
    return current_user


class CommonQueryParams:
    """Common query parameters for pagination and filtering."""

    def __init__(
        self,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ):
        # Validate and sanitize parameters
        self.skip = max(0, skip)
        self.limit = min(max(1, limit), settings.MAX_PAGE_SIZE)
        self.search = search.strip() if search else None
        self.sort_by = sort_by
        self.sort_order = sort_order.lower() if sort_order.lower() in ["asc", "desc"] else "asc"

    @property
    def page(self) -> int:
        """Calculate current page number."""
        return (self.skip // self.limit) + 1


def get_common_params(
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: str = "asc"
) -> CommonQueryParams:
    """Get common query parameters."""
    return CommonQueryParams(skip, limit, search, sort_by, sort_order)


class RateLimiter:
    """Simple rate limiter for API endpoints."""

    def __init__(self, calls: int = 100, period: int = 60):
        self.calls = calls
        self.period = period
        self.clients = {}

    def is_allowed(self, client_id: str) -> bool:
        """Check if client is allowed to make a request."""
        import time

        current_time = time.time()

        if client_id not in self.clients:
            self.clients[client_id] = []

        # Remove old requests
        self.clients[client_id] = [
            req_time for req_time in self.clients[client_id]
            if current_time - req_time < self.period
        ]

        # Check if under limit
        if len(self.clients[client_id]) >= self.calls:
            return False

        # Add current request
        self.clients[client_id].append(current_time)
        return True


def create_rate_limiter(calls: int = 100, period: int = 60):
    """Create a rate limiter dependency."""
    limiter = RateLimiter(calls, period)

    def rate_limit(
        request,
        current_user: User = Depends(get_current_user_optional)
    ):
        client_id = request.client.host if request.client else "unknown"
        if current_user:
            client_id = f"user_{current_user.id}"

        if not limiter.is_allowed(client_id):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )

    return rate_limit