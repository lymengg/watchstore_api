"""
Orders API v1 endpoints with full order management functionality.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.logging import get_logger

logger = get_logger(__name__)

from app.api.deps import get_current_user, get_db, require_admin
from app import crud, models, schemas
from app.schemas.order import PaginatedOrders
from app.utils import db_product_to_list_schema
from app.utils.responses import success, created, not_found, bad_request
from app.exceptions import NotFoundError, ValidationError

router = APIRouter()


def _order_to_out(order: models.Order) -> schemas.OrderOut:
    """Convert order model to order output schema."""
    items_out: List[schemas.OrderItemSummary] = []
    for oi in order.items:
        # Prefer live product if present, else use snapshot fields
        if oi.product is not None:
            product_out = db_product_to_list_schema(oi.product)
        else:
            product_out = schemas.ProductList(
                id=oi.product_id or 0,
                name=oi.product_name,
                brand=oi.brand or "",
                price=oi.unit_price,
                image=None,
                description=None,
            )
        items_out.append(
            schemas.OrderItemSummary(
                product=product_out,
                quantity=oi.quantity,
                line_total=oi.line_total,
            )
        )
    return schemas.OrderOut(
        id=order.id,
        items=items_out,
        total_items=order.total_items,
        subtotal=order.subtotal,
        status=order.status,
        created_at=order.created_at,
    )


@router.post("/")
def create_order(
    body: schemas.OrderCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new order from cart items or provided items."""
    # Determine items source
    if body.items and len(body.items) > 0:
        # Build order manually from provided items
        order = models.Order(user_id=current_user.id, status="Pending Payment")
        db.add(order)
        db.flush()
        total_items = 0
        subtotal = 0.0

        for it in body.items:
            product = crud.get_product(db, it.product_id)
            if not product:
                raise NotFoundError("Product", it.product_id)
            if product.stock is not None and it.quantity > product.stock:
                raise ValidationError(
                    f"Insufficient stock for product {product.id}. Available: {product.stock}, requested: {it.quantity}"
                )
            line_total = product.price * it.quantity
            db.add(
                models.OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    product_name=product.name,
                    brand=product.brand,
                    unit_price=product.price,
                    quantity=it.quantity,
                    line_total=line_total,
                )
            )
            total_items += it.quantity
            subtotal += line_total

        order.total_items = total_items
        order.subtotal = subtotal
        ship = models.Shipping(
            order_id=order.id,
            full_name=body.shipping.full_name,
            phone=body.shipping.phone,
            address1=body.shipping.address1,
            address2=body.shipping.address2,
            city=body.shipping.city,
            state=body.shipping.state,
            postal_code=body.shipping.postal_code,
            country=body.shipping.country,
        )
        db.add(ship)
        db.commit()
        db.refresh(order)
    else:
        cart_items = crud.get_cart_items_by_user(db, current_user.id)
        if not cart_items:
            raise ValidationError("Cart is empty")
        order = crud.create_order_from_items(db, current_user.id, cart_items, body.shipping)

    return created(_order_to_out(order), message="Order created successfully")


@router.get("/")
def list_my_orders(
    status: Optional[str] = Query(default=None, description="Filter by status"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """List current user's orders with optional filtering and pagination."""
    q = db.query(models.Order).filter(models.Order.user_id == current_user.id)
    if status:
        q = q.filter(models.Order.status == status)
    total = q.count()
    orders = q.order_by(models.Order.created_at.desc()).offset(skip).limit(limit).all()

    # Convert skip/limit to page/size for consistent pagination
    page = (skip // limit) + 1 if limit > 0 else 1
    return success({
        "items": [_order_to_out(o) for o in orders],
        "total": total,
        "page": page,
        "size": limit,
        "pages": (total + limit - 1) // limit if limit > 0 else 0
    }, message=f"Retrieved {len(orders)} orders")


@router.get("/{order_id}")
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific order by ID."""
    order = crud.get_order(db, order_id)
    if not order or (order.user_id and order.user_id != current_user.id):
        raise NotFoundError("Order", order_id)
    return success(_order_to_out(order), message="Order retrieved successfully")


@router.get("/{order_id}/status")
def get_order_status(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get the status of a specific order."""
    order = crud.get_order(db, order_id)
    if not order or (order.user_id and order.user_id != current_user.id):
        raise NotFoundError("Order", order_id)
    return success({
        "order_id": order.id,
        "status": order.status,
        "updated_at": order.updated_at
    }, message="Order status retrieved successfully")


@router.get("/{order_id}/invoice")
def get_invoice(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get invoice data for a specific order."""
    order = crud.get_order(db, order_id)
    if not order or (order.user_id and order.user_id != current_user.id):
        raise NotFoundError("Order", order_id)

    # Placeholder structured JSON invoice; PDF generation can be added later
    invoice_data = {
        "order_id": order.id,
        "status": order.status,
        "created_at": order.created_at,
        "billing": {
            "name": order.shipping.full_name if order.shipping else None,
            "phone": order.shipping.phone if order.shipping else None,
            "address": {
                "line1": order.shipping.address1 if order.shipping else None,
                "line2": order.shipping.address2 if order.shipping else None,
                "city": order.shipping.city if order.shipping else None,
                "state": order.shipping.state if order.shipping else None,
                "postal_code": order.shipping.postal_code if order.shipping else None,
                "country": order.shipping.country if order.shipping else None,
            } if order.shipping else None,
        },
        "items": [
            {
                "name": oi.product_name,
                "brand": oi.brand,
                "unit_price": oi.unit_price,
                "quantity": oi.quantity,
                "line_total": oi.line_total,
            }
            for oi in order.items
        ],
        "total_items": order.total_items,
        "subtotal": order.subtotal,
    }
    return success(invoice_data, message="Invoice generated successfully")


# Admin endpoints
@router.get("/admin/orders")
def admin_list_orders(
    status: Optional[str] = Query(default=None),
    user_id: Optional[int] = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(require_admin),
):
    """Admin-only route to list all orders with filtering and pagination."""
    # Build filtered query for count and pagination
    q = db.query(models.Order)
    if user_id is not None:
        q = q.filter(models.Order.user_id == user_id)
    if status:
        q = q.filter(models.Order.status == status)
    total = q.count()
    orders = q.order_by(models.Order.created_at.desc()).offset(skip).limit(limit).all()

    # Convert skip/limit to page/size for consistent pagination
    page = (skip // limit) + 1 if limit > 0 else 1
    return success({
        "items": [_order_to_out(o) for o in orders],
        "total": total,
        "page": page,
        "size": limit,
        "pages": (total + limit - 1) // limit if limit > 0 else 0
    }, message=f"Admin: Retrieved {len(orders)} orders")


_ALLOWED_STATUS_TRANSITIONS = {
    "Pending Payment": {"Paid", "Cancelled"},
    "Paid": {"Shipped", "Cancelled"},
    "Shipped": {"Completed", "Cancelled"},
    "Completed": set(),
    "Cancelled": set(),
}


@router.patch("/admin/orders/{order_id}/status")
def admin_update_order_status(
    order_id: int,
    body: schemas.OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin),
    request: Request = None,
):
    """
    Admin-only route to update order status.

    Args:
        order_id: ID of the order to update
        body: Order status update data
        db: Database session
        current_user: Authenticated admin user
        request: HTTP request object for logging

    Returns:
        Updated order status information

    Raises:
        NotFoundError: If order doesn't exist
        ValidationError: If status transition is invalid
        HTTPException: If user lacks admin permissions
    """
    logger.info(
        f"Admin order status update requested",
        extra={
            "order_id": order_id,
            "admin_user_id": current_user.id,
            "target_status": body.status,
            "request_id": getattr(request.state, 'request_id', None) if request else None
        }
    )

    # Validate order exists
    order = crud.get_order(db, order_id)
    if not order:
        logger.warning(
            f"Order not found for status update",
            extra={
                "order_id": order_id,
                "admin_user_id": current_user.id
            }
        )
        raise NotFoundError("Order", order_id)

    current = order.status
    target = body.status

    # Validate status transition
    if current not in _ALLOWED_STATUS_TRANSITIONS:
        logger.error(
            f"Unknown current status",
            extra={
                "order_id": order_id,
                "current_status": current,
                "admin_user_id": current_user.id
            }
        )
        raise ValidationError(f"Unknown current status: {current}")

    allowed = _ALLOWED_STATUS_TRANSITIONS[current]
    if target not in allowed:
        logger.warning(
            f"Invalid status transition attempted",
            extra={
                "order_id": order_id,
                "current_status": current,
                "target_status": target,
                "allowed_transitions": list(allowed),
                "admin_user_id": current_user.id
            }
        )
        raise ValidationError(f"Invalid transition {current} -> {target}")

    # Update order status
    try:
        order = crud.update_order_status(db, order, target)
        logger.info(
            f"Order status updated successfully",
            extra={
                "order_id": order_id,
                "old_status": current,
                "new_status": target,
                "admin_user_id": current_user.id
            }
        )

        return success({
            "order_id": order.id,
            "status": order.status,
            "updated_at": order.updated_at
        }, message=f"Order status updated to {target}")

    except Exception as e:
        logger.error(
            f"Failed to update order status",
            extra={
                "order_id": order_id,
                "target_status": target,
                "admin_user_id": current_user.id,
                "error": str(e)
            },
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update order status"
        )