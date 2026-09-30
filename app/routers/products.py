"""HTTP routes for /products."""
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas import ProductCreate, ProductOut, ProductUpdate

router = APIRouter(prefix="/products", tags=["Products"])

DB = Annotated[Session, Depends(get_db)]
ProductIdPath = Annotated[int, Path(gt=0, description="Product ID")]

_ERRORS = {
    404: {"description": "Product not found"},
    409: {"description": "Product ID already exists"},
    422: {"description": "Validation error"},
}


@router.post(
    "",
    response_model=ProductOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a product",
    responses={k: _ERRORS[k] for k in (409, 422)},
)
def create_product(payload: ProductCreate, db: DB):
    return crud.create_product(db, payload.model_dump())


@router.get("", response_model=list[ProductOut], summary="List products (optionally by category)")
def list_products(
    db: DB,
    category: Annotated[
        str | None, Query(description="Filter by category (case-insensitive)")
    ] = None,
    skip: Annotated[int, Query(ge=0, description="Records to skip")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Max records to return")] = 50,
):
    return crud.list_products(db, skip=skip, limit=limit, category=category)


@router.get(
    "/{product_id}",
    response_model=ProductOut,
    summary="Get a product by ID",
    responses={404: _ERRORS[404]},
)
def get_product(product_id: ProductIdPath, db: DB):
    return crud.get_product(db, product_id)


@router.put(
    "/{product_id}",
    response_model=ProductOut,
    summary="Update a product (all fields required)",
    responses={404: _ERRORS[404], 422: _ERRORS[422]},
)
def update_product(product_id: ProductIdPath, payload: ProductUpdate, db: DB):
    return crud.update_product(db, product_id, payload.model_dump())


@router.delete(
    "/{product_id}",
    summary="Delete a product",
    responses={404: _ERRORS[404]},
)
def delete_product(product_id: ProductIdPath, db: DB):
    crud.delete_product(db, product_id)
    return {"message": f"Product with ID {product_id} deleted successfully."}
