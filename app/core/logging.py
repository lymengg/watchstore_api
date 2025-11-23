"""
Core logging configuration following FastAPI best practices.
"""

import logging
import sys
import json
import os
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path

from pythonjsonlogger import jsonlogger


class JSONFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for structured logging."""

    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any],
    ) -> None:
        """Add structured fields to log records."""
        super().add_fields(log_record, record, message_dict)

        # Add timestamp if not present
        if not log_record.get("timestamp"):
            log_record["timestamp"] = datetime.utcnow().isoformat()

        # Add log level
        if log_record.get("level"):
            log_record["level"] = log_record["level"].upper()
        else:
            log_record["level"] = record.levelname

        # Add application info
        log_record["application"] = "watchstore-api"
        log_record["environment"] = os.getenv("ENVIRONMENT", "development")

        # Add request context if available
        if hasattr(record, "request_id"):
            log_record["request_id"] = record.request_id
        if hasattr(record, "user_id"):
            log_record["user_id"] = record.user_id


class ColoredFormatter(logging.Formatter):
    """Colored formatter for development environment."""

    COLORS = {
        "DEBUG": "\033[36m",      # Cyan
        "INFO": "\033[32m",       # Green
        "WARNING": "\033[33m",    # Yellow
        "ERROR": "\033[31m",      # Red
        "CRITICAL": "\033[35m",   # Magenta
        "RESET": "\033[0m",       # Reset
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        log_color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        reset_color = self.COLORS["RESET"]

        # Create colored format
        record.levelname = f"{log_color}{record.levelname}{reset_color}"
        return super().format(record)


def setup_logging() -> None:
    """Setup comprehensive logging for the application."""

    # Determine environment
    is_production = os.getenv("ENVIRONMENT") == "production"
    is_development = not is_production

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if is_development else logging.INFO)

    # Clear existing handlers
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if is_development else logging.INFO)

    # Choose formatter based on environment
    if is_production:
        formatter = JSONFormatter(
            "%(timestamp)s %(level)s %(name)s %(message)s"
        )
    else:
        formatter = ColoredFormatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler for development (only if not on Vercel)
    if not os.getenv("VERCEL") and is_development:
        try:
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)

            file_handler = logging.FileHandler(log_dir / "app.log")
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(JSONFormatter())
            root_logger.addHandler(file_handler)
        except Exception:
            # If file logging fails, continue without it
            pass

    # Configure specific loggers
    loggers_config = {
        "uvicorn": logging.WARNING,
        "uvicorn.access": logging.WARNING,
        "uvicorn.error": logging.WARNING,
        "sqlalchemy.engine": logging.WARNING,
        "sqlalchemy.pool": logging.WARNING,
        "httpx": logging.WARNING,
        "watchstore_api": logging.INFO,
        "app": logging.INFO,
        "app.auth": logging.INFO,
        "app.users": logging.INFO,
        "app.products": logging.INFO,
        "app.orders": logging.INFO,
        "app.payments": logging.INFO,
    }

    for logger_name, level in loggers_config.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)

    # Log startup message
    startup_logger = logging.getLogger("app")
    startup_logger.info(
        "Application logging initialized",
        extra={
            "environment": os.getenv("ENVIRONMENT", "development"),
            "python_version": sys.version,
            "log_level": "DEBUG" if is_development else "INFO"
        }
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    return logging.getLogger(name)