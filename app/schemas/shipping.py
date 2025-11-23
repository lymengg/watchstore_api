from pydantic import BaseModel
from typing import Optional


class ShippingAddress(BaseModel):
    full_name: str
    phone: str
    address1: str
    address2: Optional[str] = None
    city: str
    state: Optional[str] = None
    postal_code: str
    country: str