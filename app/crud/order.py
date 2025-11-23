from sqlalchemy.orm import Session
from app import models, schemas


def create_order_from_items(db: Session, user_id: int, items: list[models.CartItem], shipping: schemas.ShippingAddress) -> models.Order:
    order = models.Order(user_id=user_id, status="Pending Payment")
    db.add(order)
    db.flush()  # get order.id

    total_items = 0
    subtotal = 0.0
    for ci in items:
        product = ci.product
        line_total = product.price * ci.quantity
        oi = models.OrderItem(
            order_id=order.id,
            product_id=product.id,
            product_name=product.name,
            brand=product.brand,
            unit_price=product.price,
            quantity=ci.quantity,
            line_total=line_total,
        )
        db.add(oi)
        total_items += ci.quantity
        subtotal += line_total

    order.total_items = total_items
    order.subtotal = subtotal
    
    # shipping
    ship = models.Shipping(
        order_id=order.id,
        full_name=shipping.full_name,
        phone=shipping.phone,
        address1=shipping.address1,
        address2=shipping.address2,
        city=shipping.city,
        state=shipping.state,
        postal_code=shipping.postal_code,
        country=shipping.country,
    )
    db.add(ship)
    db.commit()
    db.refresh(order)
    return order


def get_order(db: Session, order_id: int) -> models.Order | None:
    return db.query(models.Order).filter(models.Order.id == order_id).first()


def update_order_status(db: Session, order: models.Order, status: str):
    order.status = status
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def get_orders_by_user(db: Session, user_id: int, status: str | None = None, skip: int = 0, limit: int = 50):
    q = db.query(models.Order).filter(models.Order.user_id == user_id)
    if status:
        q = q.filter(models.Order.status == status)
    return q.order_by(models.Order.created_at.desc()).offset(skip).limit(limit).all()


def get_orders_admin(db: Session, status: str | None = None, user_id: int | None = None, skip: int = 0, limit: int = 50):
    q = db.query(models.Order)
    if user_id is not None:
        q = q.filter(models.Order.user_id == user_id)
    if status:
        q = q.filter(models.Order.status == status)
    return q.order_by(models.Order.created_at.desc()).offset(skip).limit(limit).all()