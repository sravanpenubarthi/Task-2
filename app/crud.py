"""Database access layer. No HTTP concerns live here."""
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.exceptions import DuplicateProductError, ProductNotFoundError
from app.models import Product


def list_products(
    db: Session, skip: int = 0, limit: int = 50, category: str | None = None
) -> list[Product]:
    stmt = select(Product)
    if category:
        stmt = stmt.where(func.lower(Product.category) == category.strip().lower())
    stmt = stmt.order_by(Product.product_id).offset(skip).limit(limit)
    return list(db.scalars(stmt))


def get_product(db: Session, product_id: int) -> Product:
    product = db.get(Product, product_id)
    if product is None:
        raise ProductNotFoundError(product_id)
    return product


def create_product(db: Session, data: dict[str, object]) -> Product:
    product_id = int(data["product_id"])  # type: ignore[arg-type]
    if db.get(Product, product_id) is not None:
        raise DuplicateProductError(product_id)
    product = Product(**data)
    db.add(product)
    try:
        db.commit()
    except IntegrityError:  # two requests raced with the same ID
        db.rollback()
        raise DuplicateProductError(product_id) from None
    db.refresh(product)
    return product


def update_product(db: Session, product_id: int, changes: dict[str, object]) -> Product:
    product = get_product(db, product_id)
    for field, value in changes.items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product_id: int) -> None:
    product = get_product(db, product_id)
    db.delete(product)
    db.commit()
