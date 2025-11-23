"""
Products API v1 endpoints with full CRUD implementation.
"""

import base64
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_admin
from app import crud, schemas
from app.models import Product
from app.utils import db_product_to_schema, schema_to_db_product, db_product_to_list_schema
from app.utils.responses import success, created, not_found, bad_request
from app.exceptions import NotFoundError, ValidationError

router = APIRouter()


@router.get("/")
def list_products(
    q: Optional[str] = None,
    brand: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List products with optional search and pagination."""
    # Build filtered query for count and pagination
    query = db.query(Product).filter(Product.is_deleted == False)
    if q:
        like = f"%{q}%"
        query = query.filter((Product.name.ilike(like)) | (Product.brand.ilike(like)))
    if brand:
        query = query.filter(Product.brand.ilike(f"%{brand}%"))
    total = query.count()
    rows = query.offset(skip).limit(limit).all()
    data = [db_product_to_list_schema(p) for p in rows]

    # Convert skip/limit to page/size for consistent pagination
    page = (skip // limit) + 1 if limit > 0 else 1
    return success({
        "items": data,
        "total": total,
        "page": page,
        "size": limit,
        "pages": (total + limit - 1) // limit if limit > 0 else 0
    }, message=f"Retrieved {len(data)} products")


@router.get("/admin")
def admin_list_products(
    q: Optional[str] = None,
    brand: Optional[str] = None,
    include_deleted: bool = False,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin),
):
    """Admin-only route to list products with pagination and full fields."""
    query = db.query(Product)
    if not include_deleted:
        query = query.filter(Product.is_deleted == False)
    if q:
        like = f"%{q}%"
        query = query.filter((Product.name.ilike(like)) | (Product.brand.ilike(like)))
    if brand:
        query = query.filter(Product.brand.ilike(f"%{brand}%"))
    total = query.count()
    rows = query.offset(skip).limit(limit).all()
    data = [db_product_to_schema(p) for p in rows]

    # Convert skip/limit to page/size for consistent pagination
    page = (skip // limit) + 1 if limit > 0 else 1
    return success({
        "items": data,
        "total": total,
        "page": page,
        "size": limit,
        "pages": (total + limit - 1) // limit if limit > 0 else 0
    }, message=f"Retrieved {len(data)} products for admin")


@router.post("/")
def create_product(
    product: schemas.ProductBase,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin-only route to create a new product."""
    # Map Pydantic model to SQLAlchemy model (handles base64 or data URLs)
    db_product = schema_to_db_product(product)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return created(
        db_product_to_schema(db_product),
        message=f"Product '{db_product.name}' created successfully"
    )


@router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a specific product by ID."""
    product = crud.get_product(db, product_id)
    if not product:
        raise NotFoundError("Product", product_id)
    return success(
        db_product_to_schema(product),
        message="Product retrieved successfully"
    )


@router.put("/{product_id}")
def update_product(
    product_id: int,
    updates: schemas.ProductUpdate,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin-only route to update a product (partial update)."""
    db_product = crud.get_product(db, product_id)
    if not db_product:
        raise NotFoundError("Product", product_id)
    updated = crud.update_product(db, db_product, updates)
    return success(
        db_product_to_schema(updated),
        message="Product updated successfully"
    )


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin-only route to soft delete a product."""
    ok = crud.soft_delete_product(db, product_id)
    if not ok:
        raise NotFoundError("Product", product_id)
    return success(None, message=f"Product {product_id} marked as deleted")