"""
Application settings and configuration following FastAPI best practices.
Environment-aware configuration for development, production, and testing.
"""

import os
from functools import lru_cache
from typing import List, Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Environment-aware application settings."""

    # Environment Detection
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Application Information
    PROJECT_NAME: str = "Watchstore API"
    PROJECT_DESCRIPTION: str = "E-commerce API for luxury watch store"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"  # Updated to remove /v1

    # Server Configuration
    HOST: str = "127.0.0.1"  # Development default
    PORT: int = 8000
    ALLOWED_HOSTS: List[str] = ["*"]

    # Database Configuration - Base defaults
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/watchstore_dev"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10

    # Security Configuration
    SECRET_KEY: str = "change_me_super_secret_key_for_development"
    JWT_SECRET_KEY: str = "change_me_access_secret"
    JWT_REFRESH_SECRET_KEY: str = "change_me_refresh_secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    JWT_ENCODE_ALGORITHM: str = "HS256"

    # CORS Configuration - Base defaults
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "https://your-frontend-domain.com"
    ]

    # Payment Configuration
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None

    # Email Configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_NAME: str = "Watchstore"
    EMAILS_FROM_EMAIL: Optional[str] = None

    # Telegram Configuration
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None

    # File Upload Configuration
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB
    UPLOAD_DIR: str = "uploads"

    # Pagination Configuration
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # Environment-aware properties
    @property
    def DEBUG(self) -> bool:
        """Debug mode based on environment."""
        return self.ENVIRONMENT in ["development", "dev", "local"]

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.ENVIRONMENT in ["production", "prod"]

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.ENVIRONMENT in ["development", "dev", "local"]

    @property
    def is_testing(self) -> bool:
        """Check if running in testing."""
        return self.ENVIRONMENT in ["testing", "test"]

    @property
    def LOG_LEVEL(self) -> str:
        """Log level based on environment."""
        if self.is_production:
            return "WARNING"
        elif self.is_testing:
            return "ERROR"
        else:
            return "DEBUG"

    @property
    def database_url_sync(self) -> str:
        """Synchronous database URL for Alembic."""
        url = self.DATABASE_URL.replace("postgresql+psycopg2://", "postgresql://")
        if self.is_testing:
            return "sqlite:///./test.db"
        return url

    # Dynamic environment overrides
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Override settings based on environment
        if self.is_production:
            # Production overrides
            self.HOST = os.getenv("HOST", "0.0.0.0")
            self.PORT = int(os.getenv("PORT", "8000"))
            if os.getenv("DATABASE_URL"):
                self.DATABASE_URL = os.getenv("DATABASE_URL")
            self.JWT_ACCESS_EXPIRE_MINUTES = 15  # Shorter in production
            self.JWT_REFRESH_EXPIRE_MINUTES = 60 * 24  # 1 day in production
            # Production CORS - use environment variable or fallback
            cors_origins_env = os.getenv("CORS_ORIGINS", "")
            if cors_origins_env:
                # Split comma-separated origins from environment variable
                self.BACKEND_CORS_ORIGINS = [origin.strip() for origin in cors_origins_env.split(",")]
            else:
                # Fallback - add your actual frontend domains here
                self.BACKEND_CORS_ORIGINS = [
                    "https://st10-ecommerce.pages.dev",  # Your frontend main domain
                    "https://www.st10-ecommerce.pages.dev",  # www version if applicable
                ]
        elif self.is_testing:
            # Testing overrides
            self.DATABASE_URL = "sqlite:///:memory:"
            self.BACKEND_CORS_ORIGINS = ["http://localhost:3000"]
        else:
            # Development overrides
            self.DATABASE_URL = os.getenv("DATABASE_URL",
                                          "postgresql+psycopg2://postgres:postgres@localhost:5432/watchstore_dev")
            self.BACKEND_CORS_ORIGINS = [
                "http://localhost:3000",
                "http://localhost:3001",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:3001"
            ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"

    def __getitem__(self, item):
        """Allow dictionary-style access for compatibility."""
        return getattr(self, item)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Create a singleton instance for backward compatibility
settings = get_settings()

# Legacy exports for backward compatibility
DEBUG = settings.DEBUG
HOST = settings.HOST
PORT = settings.PORT
ALLOWED_ORIGINS = settings.BACKEND_CORS_ORIGINS
LOG_LEVEL = settings.LOG_LEVEL
JWT_SECRET_KEY = settings.JWT_SECRET_KEY
JWT_REFRESH_SECRET_KEY = settings.JWT_REFRESH_SECRET_KEY
JWT_ALGORITHM = settings.JWT_ALGORITHM
JWT_ACCESS_EXPIRE_MINUTES = settings.JWT_ACCESS_EXPIRE_MINUTES
JWT_REFRESH_EXPIRE_MINUTES = settings.JWT_REFRESH_EXPIRE_MINUTES
