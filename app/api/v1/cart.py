"""
Cart API v1 endpoints with full cart management functionality.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app import crud, schemas
from app.utils import db_product_to_list_schema
from app.utils.responses import success, not_found, bad_request
from app.exceptions import NotFoundError, ValidationError

router = APIRouter()


@router.get("/")
def get_cart(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get current user's cart with items and totals."""
    items = crud.get_cart_items_by_user(db, current_user.id)
    out_items = []
    total_items = 0
    subtotal = 0.0

    for item in items:
        product = item.product
        product_out = db_product_to_list_schema(product)
        line_total = product.price * item.quantity
        out_items.append(schemas.CartItemOut(
            product=product_out,
            quantity=item.quantity,
            line_total=line_total
        ))
        total_items += item.quantity
        subtotal += line_total

    cart_data = schemas.CartOut(
        items=out_items,
        total_items=total_items,
        subtotal=subtotal
    )
    return success(cart_data, message="Cart retrieved successfully")


@router.post("/items")
def add_item(
    body: schemas.CartItemAdd,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Add an item to the cart."""
    # Validate quantity
    qty = max(1, body.quantity)
    product = crud.get_product(db, body.product_id)
    if not product:
        raise NotFoundError("Product", body.product_id)

    # Stock check
    existing_items = crud.get_cart_items_by_user(db, current_user.id)
    existing = next((i for i in existing_items if i.product_id == body.product_id), None)
    new_qty = qty + (existing.quantity if existing else 0)

    if product.stock is not None and new_qty > product.stock:
        raise ValidationError(
            f"Insufficient stock. Available: {product.stock}, requested: {new_qty}"
        )

    crud.add_to_cart(db, current_user.id, body.product_id, qty)
    return get_cart(db, current_user)


@router.patch("/items/{product_id}")
def update_item(
    product_id: int,
    body: schemas.CartItemUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update the quantity of an item in the cart."""
    product = crud.get_product(db, product_id)
    if not product:
        raise NotFoundError("Product", product_id)

    qty = body.quantity
    if qty < 0:
        raise ValidationError("Quantity cannot be negative", field="quantity")

    if qty > 0 and product.stock is not None and qty > product.stock:
        raise ValidationError(
            f"Insufficient stock. Available: {product.stock}, requested: {qty}",
            field="quantity"
        )

    crud.set_cart_item_qty(db, current_user.id, product_id, qty)
    return get_cart(db, current_user)


@router.delete("/items/{product_id}")
def remove_item(
    product_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Remove an item from the cart."""
    crud.remove_cart_item(db, current_user.id, product_id)
    return get_cart(db, current_user)


@router.delete("/")
def clear_cart(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Clear all items from the cart."""
    crud.clear_cart(db, current_user.id)
    return get_cart(db, current_user)