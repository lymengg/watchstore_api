from sqlalchemy.orm import Session
from app import models


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