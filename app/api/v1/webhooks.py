"""
Webhooks API v1 endpoints for processing external service webhooks.
"""

import os
import logging
from typing import Dict, Any

from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.api.deps import get_db
from app import crud
from app.utils.mailer import build_order_confirmation_email, send_email
from app.utils.telegram import build_order_paid_alert, send_telegram_message
from app.utils.responses import success
from app.exceptions import ValidationError

router = APIRouter()
logger = logging.getLogger("watchstore_api")
load_dotenv()


@router.get("/health")
async def webhook_health():
    """
    Health check endpoint for webhook system.
    """
    return success(
        {
            "status": "healthy",
            "service": "webhooks",
            "stripe_configured": bool(os.getenv("STRIPE_WEBHOOK_SECRET")),
            "email_configured": bool(os.getenv("SMTP_HOST") and os.getenv("SMTP_USER")),
            "telegram_configured": bool(os.getenv("TELEGRAM_BOT_TOKEN"))
        },
        message="Webhook service is healthy"
    )


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    """
    Process Stripe webhook events for payment completion and failures.

    Handles:
    - checkout.session.completed: Mark order as paid, send notifications
    - payment_intent.payment_failed: Mark order as failed
    """
    try:
        import stripe  # type: ignore
    except Exception:
        raise ValidationError("Stripe SDK not installed on server")

    # Get webhook payload and signature
    raw_body = await request.body()
    payload = raw_body.decode("utf-8")
    sig_header = request.headers.get("stripe-signature") or request.headers.get("Stripe-Signature")

    if not sig_header:
        raise ValidationError("Missing Stripe-Signature header")

    # Verify webhook signature
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    if not endpoint_secret:
        raise ValidationError("Stripe webhook secret not configured")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=endpoint_secret
        )
    except Exception as e:
        raise ValidationError(f"Invalid webhook signature: {str(e)}")

    # Process different event types
    event_type = event["type"]

    if event_type == "checkout.session.completed":
        await handle_checkout_session_completed(event, db, background_tasks)
    elif event_type == "payment_intent.payment_failed":
        await handle_payment_intent_failed(event, db)
    else:
        logger.info(f"Unhandled webhook event type: {event_type}")

    return success({"received": True, "event_type": event_type}, message="Webhook processed successfully")


async def handle_checkout_session_completed(
    event: Dict[str, Any],
    db: Session,
    background_tasks: BackgroundTasks = None
):
    """
    Handle successful checkout completion from Stripe.
    """
    session = event["data"]["object"]

    # Extract order ID from session
    order_id = int(
        session.get("client_reference_id") or
        session.get("metadata", {}).get("order_id")
    )

    if not order_id:
        logger.error("No order_id found in Stripe session")
        return

    # Get and update order
    order = crud.get_order(db, order_id)
    if not order:
        logger.error(f"Order {order_id} not found for webhook processing")
        return

    # Update order status to Paid
    order = crud.update_order_status(db, order, "Paid")

    # Update payment record
    crud.upsert_payment_for_order(
        db,
        order_id=order.id,
        stripe_session_id=session.get("id"),
        stripe_payment_intent=session.get("payment_intent"),
        status="Paid",
    )

    # Clear user's cart after successful payment
    if order.user_id:
        crud.clear_cart(db, order.user_id)

    # Send notifications in background
    await send_order_notifications(order, session, db, background_tasks)

    logger.info(f"Successfully processed payment for order {order_id}")


async def handle_payment_intent_failed(event: Dict[str, Any], db: Session):
    """
    Handle payment failure from Stripe.
    """
    data = event["data"]["object"]
    order_id_str = (data.get("metadata") or {}).get("order_id")

    if not order_id_str:
        logger.error("No order_id found in failed payment intent")
        return

    try:
        order_id = int(order_id_str)
    except ValueError:
        logger.error(f"Invalid order_id in payment intent: {order_id_str}")
        return

    # Get and update order
    order = crud.get_order(db, order_id)
    if not order:
        logger.error(f"Order {order_id} not found for payment failure processing")
        return

    # Update order status to Failed
    order = crud.update_order_status(db, order, "Failed")

    # Update payment record
    crud.upsert_payment_for_order(
        db,
        order_id=order.id,
        stripe_payment_intent=data.get("id"),
        status="Failed",
    )

    logger.warning(f"Payment failed for order {order_id}")


async def send_order_notifications(
    order,
    session: Dict[str, Any],
    db: Session,
    background_tasks: BackgroundTasks = None
):
    """
    Send order confirmation email and Telegram notification.
    """
    # Send order confirmation email
    try:
        user = order.user
        to_email = getattr(user, "email", None)

        if to_email:
            subject, text_body, html_body = build_order_confirmation_email(order)

            if background_tasks is not None:
                background_tasks.add_task(
                    send_email,
                    to_email,
                    subject,
                    html_body,
                    text_body
                )
            else:
                # Fallback: send synchronously
                send_email(to_email, subject, html_body, text_body)

            logger.info(f"Order confirmation email queued for order {order.id}")

    except Exception as e:
        # Don't fail the webhook if email sending fails
        logger.exception(
            f"Error while dispatching order confirmation email for order_id={order.id}: {e}"
        )

    # Send Telegram alert to admin
    try:
        alert_text = build_order_paid_alert(order, session)

        if background_tasks is not None:
            background_tasks.add_task(send_telegram_message, alert_text)
        else:
            send_telegram_message(alert_text)

        logger.info(f"Telegram notification queued for order {order.id}")

    except Exception as e:
        # Don't fail the webhook if Telegram notification fails
        logger.exception(
            f"Error while sending Telegram alert for order_id={order.id}: {e}"
        )