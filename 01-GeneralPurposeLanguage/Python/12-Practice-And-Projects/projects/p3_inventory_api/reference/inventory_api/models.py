"""Pydantic models: what the API accepts and returns."""
from pydantic import BaseModel, ConfigDict, Field, field_validator

SKU_PATTERN = r"^[A-Za-z0-9-]+$"


class ProductIn(BaseModel):
    """Body of POST /products."""

    name: str = Field(min_length=1, max_length=100)
    sku: str = Field(min_length=1, max_length=40, pattern=SKU_PATTERN)
    price: float = Field(ge=0)
    stock: int = Field(default=0, ge=0)
    category: str | None = Field(default=None, max_length=50)


class ProductUpdate(BaseModel):
    """Body of PATCH /products/{id}. Every field is optional; stock is NOT allowed here."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=100)
    sku: str | None = Field(default=None, min_length=1, max_length=40, pattern=SKU_PATTERN)
    price: float | None = Field(default=None, ge=0)
    category: str | None = Field(default=None, max_length=50)


class Product(ProductIn):
    """A stored product."""

    id: int


class StockAdjustment(BaseModel):
    """Body of POST /products/{id}/stock. Positive adds stock, negative removes it."""

    delta: int

    @field_validator("delta")
    @classmethod
    def _not_zero(cls, v: int) -> int:
        if v == 0:
            raise ValueError("delta must not be 0")
        return v


class Page(BaseModel):
    """One page of search results."""

    items: list[Product]
    total: int
    limit: int
    offset: int
