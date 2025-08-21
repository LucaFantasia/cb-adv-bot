"""
order.py - Coinbase Orders API Client

Handles creation and retrieval of orders on the Advanced Trade API.
Currently supports USDC buy limit orders and basic order history.
"""

import time

from pydantic import ValidationError
from pydantic.type_adapter import TypeAdapter

from api.base import BaseClient
from api.order_models import Order, OrderReceipt
from api.ports import OrderAPI

_order_adapter = TypeAdapter(list[Order])


class OrderClient(BaseClient, OrderAPI):
    """
    OrderClient - Places and fetches spot orders (limit buy only)
    """

    def place_usdc_buy_limit_order(
        self, product_id: str, post_only: bool, limit_price: str, base_size: str
    ) -> OrderReceipt | None:
        """
        Place a USDC-denominated buy limit order.

        Returns the API response (order status or error).
        """
        client_order_id = str(int(time.time() * 1000))

        order_data = {
            "client_order_id": client_order_id,
            "product_id": product_id,
            "side": "BUY",
            "order_configuration": {
                "limit_limit_gtc": {
                    "base_size": base_size,
                    "limit_price": limit_price,
                    "post_only": post_only,
                }
            },
        }

        raw = self.post("orders", body=order_data)
        if not raw:
            return None
        try:
            return OrderReceipt.model_validate(raw)
        except ValidationError as error:
            self.logger.error(
                "place_usdc_buy_limit_order: parse failed",
                extra={"product_id": product_id, "errors": error.errors()},
            )
            return None

    def get_orders(self) -> list[Order]:
        """
        Retrieve historical orders (basic batch query).
        """
        raw = self.get("orders/historical/batch")
        if raw is None:
            return []

        items = raw.get("orders", [])
        try:
            return _order_adapter.validate_python(items)
        except Exception:
            self.logger.error("Failed to parse orders", extra={"count": len(items)})
            return []
