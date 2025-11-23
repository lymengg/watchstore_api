import base64
import re
from app import models, schemas


_B64_RE = re.compile(r"^[A-Za-z0-9+/]+={0,2}$")

def _clean_base64_input(data: str) -> str:
    s = data.strip()
    if s.startswith("data:"):
        if "base64," in s:
            return s.split("base64,", 1)[1].strip()
        if "," in s:
            return s.split(",", 1)[1].strip()
    return s


def _to_plain_base64(image_bytes: bytes) -> str:
    if image_bytes is None:
        return None
    try:
        text = image_bytes.decode("utf-8").strip()
        if text.startswith("data:"):
            return _clean_base64_input(text)
        if len(text) % 4 == 0 and _B64_RE.match(text):
            return text
    except UnicodeDecodeError:
        pass
    return base64.b64encode(image_bytes).decode("utf-8")


def _to_data_url(image_bytes: bytes, default_mime: str = "image/jpeg") -> str:
    """Return a data URL string. If stored bytes are a data URL already, preserve it."""
    if image_bytes is None:
        return None
    try:
        text = image_bytes.decode("utf-8").strip()
        if text.startswith("data:"):
            return text  # preserve existing data URL (with ;base64, etc.)
    except UnicodeDecodeError:
        pass
    # Otherwise, wrap base64-encoded bytes with data URL prefix
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{default_mime};base64,{b64}"


def db_product_to_schema(product: models.Product) -> schemas.Product:
    """Convert SQLAlchemy model to Pydantic schema with base64 image as a proper data URL."""
    image_value = _to_data_url(product.image) if product.image else None
    return schemas.Product(
        id=product.id,
        name=product.name,
        brand=product.brand,
        description=product.description,
        price=product.price,
        image=image_value,
        stock=product.stock
    )


def schema_to_db_product(product: schemas.ProductBase) -> models.Product:
    """Convert Pydantic schema to SQLAlchemy model with binary image (support data URLs)."""
    image_bytes = None
    if product.image:
        cleaned = _clean_base64_input(product.image)
        image_bytes = base64.b64decode(cleaned)
    return models.Product(
        name=product.name,
        brand=product.brand,
        description=product.description,
        price=product.price,
        image=image_bytes,
        stock=product.stock
    )

# Expose helper for other modules
clean_base64_input = _clean_base64_input


def db_product_to_list_schema(product: models.Product) -> schemas.ProductList:
    image_value = _to_data_url(product.image) if product.image else None
    return schemas.ProductList(
        id=product.id,
        name=product.name,
        brand=product.brand,
        price=product.price,
        image=image_value,
        description=product.description,
    )