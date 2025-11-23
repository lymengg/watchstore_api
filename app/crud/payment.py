from sqlalchemy.orm import Session
from app import models


def upsert_payment_for_order(db: Session, order_id: int, **kwargs) -> models.Payment:
    payment = db.query(models.Payment).filter(models.Payment.order_id == order_id).first()
    if not payment:
        payment = models.Payment(order_id=order_id)
    for k, v in kwargs.items():
        setattr(payment, k, v)
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment