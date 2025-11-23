from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from .product import ProductList
from .cart import CartItemAdd
from .shipping import ShippingAddress


class OrderItemSummary(BaseModel):
    product: ProductList
    quantity: int
    line_total: float


class OrderOut(BaseModel):
    id: int
    items: List[OrderItemSummary]
    total_items: int
    subtotal: float
    status: str
    created_at: datetime


class OrderCreate(BaseModel):
    shipping: ShippingAddress
    items: Optional[List[CartItemAdd]] = None  # optional; if omitted, use user's cart


class OrderStatusOut(BaseModel):
    order_id: int
    status: str
    updated_at: datetime


class OrderStatusUpdate(BaseModel):
    status: str  # one of: Pending Payment, Paid, Shipped, Completed, Cancelled


class PaginatedOrders(BaseModel):
    items: List[OrderOut]
    total: int
    skip: int
    limit: int
