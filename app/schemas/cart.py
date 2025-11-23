from pydantic import BaseModel
from typing import List
from .product import ProductList


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