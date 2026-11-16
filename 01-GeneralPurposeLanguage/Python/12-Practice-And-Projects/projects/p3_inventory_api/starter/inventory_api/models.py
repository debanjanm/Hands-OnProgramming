"""Pydantic models: what the API accepts and returns."""
from pydantic import BaseModel, ConfigDict, Field, field_validator

SKU_PATTERN = r"^[A-Za-z0-9-]+$"


class ProductIn(BaseModel):
    """Body of POST /products.

    Fields: name (1-100 chars), sku (1-40 chars, matches SKU_PATTERN), price (>= 0),
    stock (int >= 0, default 0), category (optional str, max 50 chars).
    """

    # TODO (milestone 1): declare the fields above with Field(...) constraints.


class ProductUpdate(BaseModel):
    """Body of PATCH /products/{id}. Every field optional (default None); stock NOT allowed."""

    model_config = ConfigDict(extra="forbid")

    # TODO (milestone 1): name, sku, price, category - all optional, same constraints as ProductIn.


class Product(ProductIn):
    """A stored product: ProductIn plus an int `id`."""

    # TODO (milestone 1): add id.


class StockAdjustment(BaseModel):
    """Body of POST /products/{id}/stock. `delta` is a non-zero int."""

    # TODO (milestone 4): add `delta: int` and a field_validator that rejects 0.


class Page(BaseModel):
    """One page of search results: items, total, limit, offset."""

    # TODO (milestone 5): items: list[Product], total: int, limit: int, offset: int
