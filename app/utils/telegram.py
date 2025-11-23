import json
from urllib import request, parse
from typing import Any
import logging

from app.config import settings

logger = logging.getLogger("watchstore_api")

TELEGRAM_API_BASE = "https://api.telegram.org"


def send_telegram_message(text: str) -> None:
    token = settings.telegram_bot_token
    chat_id = settings.telegram_chat_id
    if not token or not chat_id:
        logger.warning("Telegram not configured: set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID to enable alerts")
        return
    url = f"{TELEGRAM_API_BASE}/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    body = parse.urlencode(data).encode()
    req = request.Request(url, data=body, headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        with request.urlopen(req, timeout=10) as resp:
            _ = resp.read()
        logger.info("Telegram alert sent to chat_id=%s", chat_id)
    except Exception:
        logger.exception("Failed to send Telegram alert to chat_id=%s", chat_id)
        _ = resp.read()
        print(resp)


def build_order_paid_alert(order: Any, session: dict[str, Any] | None = None) -> str:
    order_id = getattr(order, "id", "")
    subtotal = getattr(order, "subtotal", 0.0)
    total_items = getattr(order, "total_items", 0)
    user = getattr(order, "user", None)
    email = getattr(user, "email", "")
    username = getattr(user, "username", "")
    payment_intent = None
    session_id = None
    if session:
        payment_intent = session.get("payment_intent")
        session_id = session.get("id")

    lines = [
        "✅ <b>Payment Succeeded</b>",
        f"Order: <code>#{order_id}</code>",
        f"Amount: <b>$ {subtotal:.2f}</b>",
        f"Items: <b>{total_items}</b>",
    ]
    if username or email:
        lines.append(f"User: {username} {f'({email})' if email else ''}")
    if payment_intent:
        lines.append(f"PI: <code>{payment_intent}</code>")
    if session_id:
        lines.append(f"Session: <code>{session_id}</code>")
    return "\n".join(lines)
