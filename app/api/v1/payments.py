"""
Payments API v1 endpoints with Stripe payment session creation.
"""

import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.api.deps import get_current_user, get_db
from app import crud, models, schemas
from app.utils.responses import success, created, not_found, bad_request
from app.exceptions import NotFoundError, ValidationError

router = APIRouter()
load_dotenv()


@router.post("/create-session")
def create_stripe_session(
    body: schemas.PaymentSessionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a Stripe payment session for an order."""
    try:
        import stripe  # type: ignore
    except Exception:
        raise ValidationError("Stripe SDK not installed on server")

    secret = os.getenv("STRIPE_SECRET_KEY")
    if not secret:
        raise ValidationError("Stripe secret key not configured")

    stripe.api_key = secret

    order = crud.get_order(db, body.order_id)
    if not order or (order.user_id and order.user_id != current_user.id):
        raise NotFoundError("Order", body.order_id)

    if not order.items:
        raise ValidationError("Order has no items")

    # Build line items for Stripe
    line_items = []
    for oi in order.items:
        price_in_cents = int(round(oi.unit_price * 100))
        line_items.append(
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": f"{oi.product_name} ({oi.brand or ''})".strip()},
                    "unit_amount": price_in_cents,
                },
                "quantity": oi.quantity,
            }
        )

    # Create Stripe checkout session
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=line_items,
        success_url=body.success_url,
        cancel_url=body.cancel_url,
        client_reference_id=str(order.id),
        metadata={"order_id": str(order.id)},
    )

    # Save payment record
    crud.upsert_payment_for_order(
        db,
        order_id=order.id,
        provider="stripe",
        stripe_session_id=session.get("id"),
        status="Pending",
    )

    session_data = schemas.PaymentSessionOut(
        url=session.get("url"),
        session_id=session.get("id")
    )
    return created(session_data, message="Payment session created successfully")