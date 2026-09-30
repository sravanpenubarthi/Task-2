"""Pydantic schemas: request validation and response serialisation."""
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

# Reusable field types keep Create / Update schemas consistent.
ProductId = Annotated[int, Field(gt=0, description="Unique product ID")]
Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
Price = Annotated[float, Field(gt=0, description="Must be greater than 0")]
Quantity = Annotated[int, Field(gt=0, description="Must be greater than 0")]


class ProductUpdate(BaseModel):
    """Payload for PUT: every field is mandatory (product_id comes from the URL)."""

    product_name: Text
    category: Text
    price: Price
    quantity: Quantity


class ProductCreate(ProductUpdate):
    """Payload for POST: same fields plus the unique product_id."""

    product_id: ProductId


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    product_name: str
    category: str
    price: float
    quantity: int
