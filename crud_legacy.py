from sqlalchemy.orm import Session

from app import auth_utils
from app import models, schemas
from app import utils
import base64


def get_products(db: Session, q: str = None, brand: str = None, skip: int = 0, limit: int = 10):
    query = db.query(models.Product).filter(models.Product.is_deleted == False)
    if q:
        query = query.filter(
            (models.Product.name.ilike(f"%{q}%")) |
            (models.Product.brand.ilike(f"%{q}%"))
        )
    if brand:
        query = query.filter(models.Product.brand.ilike(f"%{brand}%"))
    return query.offset(skip).limit(limit).all()


def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id, models.Product.is_deleted == False).first()


def create_product(db: Session, product: schemas.ProductBase):
    image_bytes = None
    if product.image:
        cleaned = utils.clean_base64_input(product.image)
        image_bytes = base64.b64decode(cleaned)
    db_product = models.Product(
        name=product.name,
        brand=product.brand,
        description=product.description,
        price=product.price,
        image=image_bytes,
        stock=product.stock,
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(db: Session, db_product: models.Product, updates: schemas.ProductUpdate):
    if updates.name is not None:
        db_product.name = updates.name
    if updates.brand is not None:
        db_product.brand = updates.brand
    if updates.description is not None:
        db_product.description = updates.description
    if updates.price is not None:
        db_product.price = updates.price
    if updates.stock is not None:
        db_product.stock = updates.stock
    if updates.image is not None:
        # image: base64 string or data URL; allow empty string or null to clear
        if updates.image:
            cleaned = utils.clean_base64_input(updates.image)
            db_product.image = base64.b64decode(cleaned)
        else:
            db_product.image = None
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def soft_delete_product(db: Session, product_id: int) -> bool:
    prod = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not prod:
        return False
    if prod.is_deleted:
        return True
    prod.is_deleted = True
    db.add(prod)
    db.commit()
    return True


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_phone_number(db: Session, phone_number: str):
    return db.query(models.User).filter(models.User.phone_number == phone_number).first()

def create_user(db: Session, username: str, email: str, phone_number: str, password: str):
    hashed_password = auth_utils.hash_password(password)
    db_user = models.User(username=username, email=email, phone_number=phone_number, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_password(db: Session, user: models.User, new_password: str):
    user.hashed_password = auth_utils.hash_password(new_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# Cart CRUD

def get_cart_items_by_user(db: Session, user_id: int):
    return db.query(models.CartItem).filter(models.CartItem.user_id == user_id).all()


def add_to_cart(db: Session, user_id: int, product_id: int, quantity: int = 1):
    item = db.query(models.CartItem).filter(
        models.CartItem.user_id == user_id,
        models.CartItem.product_id == product_id,
    ).first()
    if item:
        item.quantity = item.quantity + quantity
        db.add(item)
    else:
        item = models.CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
        db.add(item)
    db.commit()
    db.refresh(item)
    return item


def set_cart_item_qty(db: Session, user_id: int, product_id: int, quantity: int):
    item = db.query(models.CartItem).filter(
        models.CartItem.user_id == user_id,
        models.CartItem.product_id == product_id,
    ).first()
    if not item:
        return None
    if quantity <= 0:
        db.delete(item)
        db.commit()
        return None
    item.quantity = quantity
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def remove_cart_item(db: Session, user_id: int, product_id: int):
    item = db.query(models.CartItem).filter(
        models.CartItem.user_id == user_id,
        models.CartItem.product_id == product_id,
    ).first()
    if not item:
        return False
    db.delete(item)
    db.commit()
    return True


def clear_cart(db: Session, user_id: int):
    db.query(models.CartItem).filter(models.CartItem.user_id == user_id).delete(synchronize_session=False)
    db.commit()
    return True


# Orders CRUD
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
