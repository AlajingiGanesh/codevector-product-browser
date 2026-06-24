from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_serializer


ProductCategory = Literal[
    "Electronics",
    "Clothing",
    "Books",
    "Sports",
    "Home",
    "Beauty",
    "Automotive",
    "Toys",
    "Grocery",
    "Health",
]

PRODUCT_CATEGORIES: tuple[str, ...] = (
    "Electronics",
    "Clothing",
    "Books",
    "Sports",
    "Home",
    "Beauty",
    "Automotive",
    "Toys",
    "Grocery",
    "Health",
)


class ProductRead(BaseModel):
    id: int
    name: str
    category: str
    price: Decimal = Field(description="Decimal string to avoid floating point money issues.")
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("price")
    def serialize_price(self, value: Decimal) -> str:
        return f"{value:.2f}"


class PaginatedProducts(BaseModel):
    data: list[ProductRead]
    next_cursor: str | None
    has_more: bool

