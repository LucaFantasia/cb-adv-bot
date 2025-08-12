"""
order.py - Coinbase Orders API Client

Handles creation and retrieval of orders on the Advanced Trade API.
Currently supports USDC buy limit orders and basic order history.
"""

import time
from typing import Any

from .base import BaseClient


class OrderClient(BaseClient):
    """
    OrderClient - Places and fetches spot orders (limit buy only)
    """

    def place_usdc_buy_limit_order(
        self, product_id: str, post_only: bool, limit_price: str, base_size: str
    ) -> Any | None:
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

        return self.post("orders", body=order_data)

    def get_orders(self) -> list[dict[str, Any]]:
        """
        Retrieve historical orders (basic batch query).
        """
        response = self.get("orders/historical/batch")
        return response.get("orders", []) if response else []
