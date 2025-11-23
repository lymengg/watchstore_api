"""
FastAPI application factory with best practices structure.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.logging import setup_logging
from app.api.v1 import auth, users, products, cart, orders, payments, webhooks
from app.exceptions import setup_exception_handlers
from app.middleware import setup_middleware


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""

    # Setup logging first
    setup_logging()

    # Create FastAPI app
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.VERSION,
        openapi_url="/openapi.json" if settings.DEBUG else None,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )

    # Setup middleware
    setup_middleware(app)

    # Setup CORS with comprehensive settings for admin endpoints
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "Accept",
            "X-Requested-With",
            "X-Forwarded-For",
            "X-Real-IP",
            "Origin",
            "User-Agent",
            "Cache-Control",
            "Pragma"
        ],
        expose_headers=["X-Request-ID", "X-Process-Time"],
        max_age=600,  # Cache preflight for 10 minutes
    )

    # Setup exception handlers
    setup_exception_handlers(app)

    # Include API routers
    app.include_router(
        auth.router,
        prefix="/api/auth",
        tags=["authentication"]
    )
    app.include_router(
        users.router,
        prefix="/api/users",
        tags=["users"]
    )
    app.include_router(
        products.router,
        prefix="/api/products",
        tags=["products"]
    )
    app.include_router(
        cart.router,
        prefix="/api/cart",
        tags=["cart"]
    )
    app.include_router(
        orders.router,
        prefix="/api/orders",
        tags=["orders"]
    )
    app.include_router(
        payments.router,
        prefix="/api/payments",
        tags=["payments"]
    )
    app.include_router(
        webhooks.router,
        prefix="/api/webhooks",
        tags=["webhooks"]
    )

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "version": settings.VERSION,
            "environment": "development" if settings.DEBUG else "production"
        }

    @app.get("/")
    async def root():
        return {
            "message": f"Welcome to {settings.PROJECT_NAME}",
            "version": settings.VERSION,
            "docs": "/docs" if settings.DEBUG else "Docs not available in production"
        }

    return app