"""
User service layer following FastAPI best practices.
"""

from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.auth import get_password_hash, verify_password
from app.core.logging import get_logger
from app.models.user import User
from app.schemas.auth import UserCreate, UserUpdate

logger = get_logger(__name__)


class UserService:
    """Service for user-related operations."""

    def __init__(self, db: Session):
        self.db = db

    def get(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.db.query(User).filter(User.username == username).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()

    def get_by_phone_number(self, phone_number: str) -> Optional[User]:
        """Get user by phone number."""
        return self.db.query(User).filter(User.phone_number == phone_number).first()

    def authenticate(self, *, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password."""
        user = self.get_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def create(self, obj_in: UserCreate) -> User:
        """Create a new user."""
        try:
            # Create user object
            db_obj = User(
                username=obj_in.username,
                email=obj_in.email,
                phone_number=obj_in.phone_number,
                hashed_password=get_password_hash(obj_in.password),
                is_active=True,
                role="user",  # Default role
            )

            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)

            logger.info(
                f"User created successfully",
                extra={
                    "user_id": db_obj.id,
                    "username": db_obj.username,
                    "email": db_obj.email
                }
            )

            return db_obj

        except IntegrityError as e:
            self.db.rollback()
            logger.warning(f"User creation failed due to integrity error: {e}")
            raise ValueError("User with these details already exists")

        except Exception as e:
            self.db.rollback()
            logger.error(f"User creation failed: {e}", exc_info=True)
            raise ValueError("Failed to create user")

    def update(
        self,
        *,
        db_obj: User,
        obj_in: UserUpdate
    ) -> User:
        """Update an existing user."""
        try:
            update_data = obj_in.dict(exclude_unset=True)

            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)

            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)

            logger.info(
                f"User updated successfully",
                extra={
                    "user_id": db_obj.id,
                    "username": db_obj.username
                }
            )

            return db_obj

        except Exception as e:
            self.db.rollback()
            logger.error(f"User update failed: {e}", exc_info=True)
            raise ValueError("Failed to update user")

    def update_password(
        self,
        *,
        user: User,
        new_password: str
    ) -> User:
        """Update user password."""
        try:
            user.hashed_password = get_password_hash(new_password)
            self.db.add(user)
            self.db.commit()

            logger.info(
                f"User password updated successfully",
                extra={
                    "user_id": user.id,
                    "username": user.username
                }
            )

            return user

        except Exception as e:
            self.db.rollback()
            logger.error(f"Password update failed: {e}", exc_info=True)
            raise ValueError("Failed to update password")

    def delete(self, *, user_id: int) -> Optional[User]:
        """Delete a user (soft delete by deactivating)."""
        try:
            user = self.get(user_id)
            if not user:
                return None

            user.is_active = False
            self.db.add(user)
            self.db.commit()

            logger.info(
                f"User deactivated successfully",
                extra={
                    "user_id": user.id,
                    "username": user.username
                }
            )

            return user

        except Exception as e:
            self.db.rollback()
            logger.error(f"User deactivation failed: {e}", exc_info=True)
            raise ValueError("Failed to deactivate user")

    def is_active(self, user: User) -> bool:
        """Check if user is active."""
        return user.is_active

    def is_admin(self, user: User) -> bool:
        """Check if user is admin."""
        return user.role == "admin"

    def promote_to_admin(self, *, user_id: int) -> Optional[User]:
        """Promote user to admin role."""
        try:
            user = self.get(user_id)
            if not user:
                return None

            user.role = "admin"
            self.db.add(user)
            self.db.commit()

            logger.info(
                f"User promoted to admin",
                extra={
                    "user_id": user.id,
                    "username": user.username
                }
            )

            return user

        except Exception as e:
            self.db.rollback()
            logger.error(f"User promotion failed: {e}", exc_info=True)
            raise ValueError("Failed to promote user to admin")