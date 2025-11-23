"""
Watchstore API - Single Entry Point for Development and Production
Follows FastAPI best practices with environment-aware configuration.

This file serves as both:
- Development server entry point (python api.py)
- Vercel production entry point (automatic)

Environment Variables:
- ENVIRONMENT: "development", "production", or "testing"
- DATABASE_URL: PostgreSQL connection string
- DEBUG: Enable/disable debug mode
- HOST: Server host (development only)
- PORT: Server port (development only)
"""

import os
import sys
from typing import Optional

from app.main import create_app
from app.config import settings

# Create the FastAPI application
app = create_app()

def get_server_info() -> dict:
    """Get current server configuration information."""
    return {
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "host": settings.HOST,
        "port": settings.PORT,
        "database_configured": bool(settings.DATABASE_URL),
        "project_name": settings.PROJECT_NAME,
        "version": settings.VERSION
    }

def run_development_server() -> None:
    """Run the development server with optimal configuration."""
    import uvicorn

    server_info = get_server_info()

    print(f"Starting {server_info['project_name']} Development Server")
    print(f"Environment: {server_info['environment']}")
    print(f"Server: http://{server_info['host']}:{server_info['port']}")
    print(f"API Docs: http://{server_info['host']}:{server_info['port']}/docs")
    print(f"Debug Mode: {server_info['debug']}")

    # Configure uvicorn for development
    uvicorn.run(
        "api:app" if settings.DEBUG else app,
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
        use_colors=True
    )

if __name__ == "__main__":
    """
    Development mode: Run when script is executed directly
    Usage: python api.py
    """
    # Ensure we're in development mode when running locally
    if not os.getenv("ENVIRONMENT"):
        os.environ["ENVIRONMENT"] = "development"

    # Run the development server
    run_development_server()

# Vercel Production Mode:
# Vercel automatically imports 'app' from this file
# No server startup needed - Vercel handles serving
# The 'app' variable above is used for production deployment