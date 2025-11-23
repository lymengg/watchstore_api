import smtplib
import ssl
import logging
from email.message import EmailMessage
from typing import Optional, Tuple

from app.config import settings

logger = logging.getLogger("watchstore_api")


def _from_address() -> str:
    """
    Build the from address for emails using settings.
    Follows FastAPI best practices by using the centralized settings.
    """
    from_email = settings.EMAILS_FROM_EMAIL or settings.SMTP_USER
    display_name = settings.EMAILS_FROM_NAME.strip() if settings.EMAILS_FROM_NAME else ""
    return f"{display_name} <{from_email}>" if display_name else from_email


def send_email(
    to_email: str,
    subject: str,
    html_body: str,
    text_body: Optional[str] = None
) -> bool:
    """
    Send an email using SMTP configuration from settings.

    Args:
        to_email: Recipient email address
        subject: Email subject line
        html_body: HTML content of the email
        text_body: Optional plain text content

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    # Validate SMTP configuration
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning(
            "SMTP not configured: set SMTP_USER and SMTP_PASSWORD to enable email sending"
        )
        return False

    try:
        # Create email message
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = _from_address()
        msg["To"] = to_email

        # Set content
        if text_body:
            msg.set_content(text_body)
        else:
            msg.set_content("This email contains HTML content. Please view in an HTML-capable client.")

        if html_body:
            msg.add_alternative(html_body, subtype="html")

        # Send email
        context = ssl.create_default_context()
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.ehlo()
            server.starttls(context=context)
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)

        logger.info("Email sent successfully to %s with subject '%s'", to_email, subject)
        return True

    except smtplib.SMTPAuthenticationError as e:
        logger.error(
            "SMTP authentication failed for user %s: %s",
            settings.SMTP_USER,
            str(e)
        )
        return False
    except smtplib.SMTPRecipientsRefused as e:
        logger.error("All recipients were refused: %s", str(e))
        return False
    except smtplib.SMTPException as e:
        logger.error("SMTP error occurred while sending email to %s: %s", to_email, str(e))
        return False
    except Exception as e:
        logger.exception(
            "Unexpected error while sending email to %s with subject '%s': %s",
            to_email,
            subject,
            str(e)
        )
        return False


def build_order_confirmation_email(order) -> Tuple[str, str, str]:
    """
    Build order confirmation email content (subject, text body, and HTML body).

    Args:
        order: Order object with related items and shipping information

    Returns:
        Tuple[str, str, str]: (subject, text_body, html_body)
    """
    # Safely extract order information with fallbacks
    try:
        order_id = getattr(order, "id", "")
        full_name = (
            getattr(getattr(order, "shipping", None), "full_name", None) or
            getattr(getattr(order, "user", None), "username", "Customer")
        )
        subtotal = float(getattr(order, "subtotal", 0.0))
        total_items = int(getattr(order, "total_items", 0))
        items = getattr(order, "items", [])
    except Exception as e:
        logger.error("Error extracting order information: %s", str(e))
        # Fallback values if extraction fails
        order_id = "unknown"
        full_name = "Customer"
        subtotal = 0.0
        total_items = 0
        items = []

    subject = f"Your order #{order_id} is confirmed"

    # Build text email body
    lines = [
        f"Hi {full_name},",
        "",
        f"Thank you for your purchase! Your order #{order_id} has been confirmed.",
        "",
        "Items:",
    ]

    # Add order items with error handling
    for item in items:
        try:
            product_name = getattr(item, "product_name", "Unknown Product")
            quantity = int(getattr(item, "quantity", 1))
            line_total = float(getattr(item, "line_total", 0.0))
            lines.append(f"- {product_name} x{quantity} — ${line_total:.2f}")
        except Exception as e:
            logger.warning("Error processing order item: %s", str(e))
            continue

    lines.extend([
        "",
        f"Total items: {total_items}",
        f"Subtotal: ${subtotal:.2f}",
        "",
        "We'll notify you when your order ships.",
        "",
        "— Watchstore",
    ])
    text_body = "\n".join(lines)

    # Build HTML email body
    html_rows = []
    for item in items:
        try:
            product_name = getattr(item, "product_name", "Unknown Product")
            quantity = int(getattr(item, "quantity", 1))
            line_total = float(getattr(item, "line_total", 0.0))
            html_rows.append(
                f"<tr><td>{product_name}</td>"
                f"<td style='text-align:center'>{quantity}</td>"
                f"<td style='text-align:right'>${line_total:.2f}</td></tr>"
            )
        except Exception as e:
            logger.warning("Error processing order item for HTML: %s", str(e))
            continue

    html_body = f"""
    <div style="font-family:Arial,Helvetica,sans-serif; color:#111; max-width:600px; margin:0 auto;">
      <div style="background-color:#f8f9fa; padding:20px; border-radius:8px; margin-bottom:20px;">
        <h1 style="color:#333; margin:0; font-size:24px;">Order Confirmation</h1>
      </div>

      <p>Hi {full_name},</p>
      <p>Thank you for your purchase! Your order <strong>#{order_id}</strong> has been confirmed.</p>

      <div style="background-color:#ffffff; border:1px solid #dee2e6; border-radius:8px; overflow:hidden; margin:20px 0;">
        <table width="100%" cellpadding="12" cellspacing="0" style="border-collapse:collapse;">
          <thead style="background-color:#f8f9fa;">
            <tr>
              <th align="left" style="padding:12px; border-bottom:1px solid #dee2e6;">Item</th>
              <th align="center" style="padding:12px; border-bottom:1px solid #dee2e6;">Qty</th>
              <th align="right" style="padding:12px; border-bottom:1px solid #dee2e6;">Total</th>
            </tr>
          </thead>
          <tbody>
            {''.join(html_rows)}
          </tbody>
          <tfoot style="background-color:#f8f9fa;">
            <tr>
              <td colspan="2" align="right" style="padding:12px; border-top:1px solid #dee2e6;">
                <strong>Total items</strong>
              </td>
              <td align="right" style="padding:12px; border-top:1px solid #dee2e6;">
                {total_items}
              </td>
            </tr>
            <tr>
              <td colspan="2" align="right" style="padding:12px; border-top:1px solid #dee2e6;">
                <strong>Subtotal</strong>
              </td>
              <td align="right" style="padding:12px; border-top:1px solid #dee2e6;">
                <strong>${subtotal:.2f}</strong>
              </td>
            </tr>
          </tfoot>
        </table>
      </div>

      <div style="background-color:#e9ecef; padding:15px; border-radius:8px; margin:20px 0;">
        <p style="margin:0; color:#6c757d;">
          We'll notify you when your order ships. You can check your order status anytime.
        </p>
      </div>

      <p style="margin-top:30px; padding-top:20px; border-top:1px solid #dee2e6; color:#6c757d;">
        — Watchstore Team<br>
        <small style="color:#adb5bd;">This is an automated message. Please do not reply to this email.</small>
      </p>
    </div>
    """

    return subject, text_body, html_body
