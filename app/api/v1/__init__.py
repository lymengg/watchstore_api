"""
API v1 package for the FastAPI application.
"""

from fastapi import APIRouter

# Import all v1 routers
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.products import router as products_router
from app.api.v1.cart import router as cart_router
from app.api.v1.orders import router as orders_router
from app.api.v1.payments import router as payments_router

# Create main v1 router
router = APIRouter()

# Include all sub-routers
router.include_router(auth_router, prefix="/auth", tags=["authentication"])
router.include_router(users_router, prefix="/users", tags=["users"])
router.include_router(products_router, prefix="/products", tags=["products"])
router.include_router(cart_router, prefix="/cart", tags=["cart"])
router.include_router(orders_router, prefix="/orders", tags=["orders"])
router.include_router(payments_router, prefix="/payments", tags=["payments"])

__all__ = ["router"]