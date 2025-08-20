from __future__ import annotations

from pydantic import BaseModel, Field


class Product(BaseModel):
    product_id: str = Field(alias="product_id")
    base_currency: str
    quote_currency: str


class Account(BaseModel):
    uuid: str
    currency: str
    available_balance: float | str
    hold: float | str | None = None


class OrderCreated(BaseModel):
    order_id: str = Field(alias="order_id")
    success: bool = True
    message: str | None = None
