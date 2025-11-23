from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ProductBase(BaseModel):
    name: str
    brand: str
    description: Optional[str] = None
    price: float
    image: Optional[str] = None  # base64 string
    stock: int


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    image: Optional[str] = None  # base64 string; set null to clear image
    stock: Optional[int] = None


class Product(BaseModel):
    id: int
    name: str
    brand: str
    description: Optional[str] = None
    price: float
    image: Optional[str] = None
    stock: int

    model_config = {
        "from_attributes": True
    }


class ProductList(BaseModel):
    id: int
    name: str
    brand: str
    price: float
    image: Optional[str] = None
    description: Optional[str] = None

    model_config = {
        "from_attributes": True
    }


class UserCreate(BaseModel):
    username: str
    password: str
    email: str
    phone_number: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPair(Token):
    refresh_token: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class User(BaseModel):
    username: str
    email: str
    phone_number: str

    class Config:
        orm_mode = True


# Cart schemas
class CartItemAdd(BaseModel):
    product_id: int
    quantity: int = 1


class CartItemUpdate(BaseModel):
    quantity: int


class CartItemOut(BaseModel):
    product: ProductList
    quantity: int
    line_total: float


class CartOut(BaseModel):
    items: List[CartItemOut]
    total_items: int
    subtotal: float


# Order & payment schemas
class ShippingAddress(BaseModel):
    full_name: str
    phone: str
    address1: str
    address2: Optional[str] = None
    city: str
    state: Optional[str] = None
    postal_code: str
    country: str


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


class PaymentSessionCreate(BaseModel):
    order_id: int
    success_url: str
    cancel_url: str


class PaymentSessionOut(BaseModel):
    url: str
    session_id: str


class OrderStatusOut(BaseModel):
    order_id: int
    status: str
    updated_at: datetime


class OrderStatusUpdate(BaseModel):
    status: str  # one of: Pending Payment, Paid, Shipped, Completed, Cancelled
