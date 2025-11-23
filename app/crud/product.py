import base64
from sqlalchemy.orm import Session
from app import models, schemas
from app.utils import clean_base64_input


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
    return db.query(models.Product).filter(
        models.Product.id == product_id, 
        models.Product.is_deleted == False
    ).first()


def create_product(db: Session, product: schemas.ProductBase):
    image_bytes = None
    if product.image:
        cleaned = clean_base64_input(product.image)
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
            cleaned = clean_base64_input(updates.image)
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