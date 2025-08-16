from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from datetime import datetime

    from websocket import WebSocket


@runtime_checkable
class Clock(Protocol):
    def now(self) -> float:
        """Return current UNIX time in seconds."""
        ...

    def monotonic(self) -> float:
        """Return a monotonic increasing clock in seconds (for measuring durations)."""


@runtime_checkable
class ProductAPI(Protocol):
    def get_product(self, product_id: str) -> Any | None:
        """Retrieve metadata for a specific trading pair (e.g., BTC-USD)"""
        ...

    def get_historic_candles(
        self,
        product_id: str,
        start_time: datetime,
        end_time: datetime,
        granularity_mins: int,
        granularity_str: str,
    ) -> list[dict[str, Any]]:
        """Returns raw candle data"""
        ...


@runtime_checkable
class OrderAPI(Protocol):
    def place_usdc_buy_limit_order(
        self, product_id: str, post_only: bool, limit_price: str, base_size: str
    ) -> Any | None:
        """
        Place a USDC-denominated buy limit order.
        Returns the API response (order status or error).
        """
        ...

    def get_orders(self) -> list[dict[str, Any]]:
        """Retrieve historical orders (basic batch query)."""
        ...


@runtime_checkable
class AccountAPI(Protocol):
    def get_accounts(self) -> list[dict[str, Any]]:
        """Retrieve all trading accounts (one per currency)."""
        ...

    def get_account_usdc(self) -> dict[str, Any] | None:
        """Return the account dict associated with the USDC wallet."""
        ...

    def get_balance_usdc(self) -> float:
        """Return the available USDC balance."""
        ...


@runtime_checkable
class WebsocketAPI(Protocol):
    def stop(self) -> None: ...

    def on_open(self, ws: WebSocket) -> None: ...

    def _on_message(self, ws: WebSocket, raw_message: str) -> None: ...

    def on_error(self, ws: WebSocket, err: str) -> None: ...

    def on_close(self, ws: WebSocket, code: int, msg: str) -> None: ...

    def connect_and_listen(self) -> None: ...
