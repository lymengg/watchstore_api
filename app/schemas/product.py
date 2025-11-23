import base64
import re
from typing import Optional

from pydantic import BaseModel, Field, field_validator


_B64_RE = re.compile(r"^[A-Za-z0-9+/]+={0,2}$")


def _clean_base64_input(data: str) -> str:
    s = data.strip()
    if s.startswith("data:"):
        if "base64," in s:
            return s.split("base64,", 1)[1].strip()
        if "," in s:
            return s.split(",", 1)[1].strip()
    return s


class ProductBase(BaseModel):
    name: str = Field(min_length=1)
    brand: str = Field(min_length=1)
    description: Optional[str] = None
    price: float = Field(gt=0)
    image: Optional[str] = None  # base64 string or data URL
    stock: int = Field(ge=0)

    @field_validator("name", "brand")
    @classmethod
    def _no_blank(cls, v: str):
        s = v.strip() if isinstance(v, str) else v
        if not s:
            raise ValueError("must not be empty")
        return s

    @field_validator("image")
    @classmethod
    def _valid_image(cls, v: Optional[str]):
        if v is None:
            return v
        s = v.strip()
        if not s:
            return None  # treat empty string as no image on create
        cleaned = _clean_base64_input(s)
        try:
            # validate base64 without altering original representation
            base64.b64decode(cleaned, validate=True)
        except Exception:
            raise ValueError("image must be a valid base64 string or data URL")
        return s


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(default=None, gt=0)
    image: Optional[str] = None  # base64 string; set null to clear image
    stock: Optional[int] = Field(default=None, ge=0)

    @field_validator("name", "brand")
    @classmethod
    def _no_blank_optional(cls, v: Optional[str]):
        if v is None:
            return v
        s = v.strip()
        if not s:
            raise ValueError("must not be empty")
        return s

    @field_validator("image")
    @classmethod
    def _valid_image_optional(cls, v: Optional[str]):
        # allow empty string to pass through so router can clear the image
        if v is None or v == "":
            return v
        s = v.strip()
        cleaned = _clean_base64_input(s)
        try:
            base64.b64decode(cleaned, validate=True)
        except Exception:
            raise ValueError("image must be a valid base64 string or data URL")
        return s


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


class PaginatedProducts(BaseModel):
    items: list[ProductList]
    total: int
    skip: int
    limit: int


class PaginatedProductsFull(BaseModel):
    items: list[Product]
    total: int
    skip: int
    limit: int
