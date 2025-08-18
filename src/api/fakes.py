from __future__ import annotations

import json
from contextlib import suppress
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, cast

from api.ports import AccountAPI, Clock, OrderAPI, ProductAPI, WebsocketAPI

if TYPE_CHECKING:
    from collections.abc import Callable

    from websocket import WebSocket

import queue
from threading import Event, Thread


class FakeClock(Clock):
    def __init__(self, *, now_value: float = 1_700_000_000.0, monotonic_value: float = 0.0) -> None:
        self._now = now_value
        self._mono = monotonic_value

    def now(self) -> float:
        return self._now

    def monotonic(self) -> float:
        return self._mono

    def advance(self, seconds: float) -> None:
        self._now += seconds
        self._mono += seconds


class FakeProductAPI(ProductAPI):
    def __init__(self) -> None:
        self.candle_calls: list[tuple[str, datetime, datetime, int, str]] = []
        self.product_calls: list[str] = []

    def get_product(self, product_id: str) -> Any | None:
        self.product_calls.append(product_id)
        return {
            "product_id": "BTC-USD",
            "price": "140.21",
            "price_percentage_change_24h": "9.43%",
            "volume_24h": "1908432",
            "volume_percentage_change_24h": "9.43%",
        }

    def get_historic_candles(
        self,
        product_id: str,
        start_time: datetime,
        end_time: datetime,
        granularity_mins: int,
        granularity_str: str,
    ) -> list[dict[str, Any]]:
        self.candle_calls.append(
            (product_id, start_time, end_time, granularity_mins, granularity_str)
        )
        return [
            {
                "start": "1639508050",
                "low": "140.21",
                "high": "140.21",
                "open": "140.21",
                "close": "140.21",
                "volume": "56437345",
            }
        ]


class FakeOrderAPI(OrderAPI):
    def __init__(self) -> None:
        self.placed_buy_orders: list[tuple[str, bool, str, str]] = []

    def place_usdc_buy_limit_order(
        self, product_id: str, post_only: bool, limit_price: str, base_size: str
    ) -> Any | None:
        self.placed_buy_orders.append((product_id, post_only, limit_price, base_size))
        return {
            "success": True,
            "success_response": {
                "order_id": "11111-00000-000000",
                "product_id": product_id,
                "side": "BUY",
                "client_order_id": "0000-00000-000000",
            },
            "order_configuration": {
                "limit_limit_gtc": {
                    "base_size": base_size,
                    "limit_price": limit_price,
                    "post_only": post_only,
                }
            },
        }

    def get_orders(self) -> list[dict[str, Any]]:
        return [
            {
                "order_id": "0000-000000-000000",
                "product_id": "BTC-USD",
                "user_id": "2222-000000-000000",
                "order_configuration": {
                    "limit_limit_gtc": {
                        "quote_size": "10.00",
                        "base_size": "0.001",
                        "limit_price": "10000.00",
                        "post_only": False,
                    },
                },
                "side": "BUY",
                "client_order_id": "11111-000000-000000",
                "status": "PENDING",
                "time_in_force": "UNKNOWN_TIME_IN_FORCE",
                "created_time": "2021-05-31T09:59:59.000Z",
                "completion_percentage": "50",
                "filled_size": "0.001",
                "average_filled_price": "50",
                "fee": "<string>",
                "number_of_fills": "2",
                "filled_value": "10000",
                "pending_cancel": True,
                "size_in_quote": False,
                "total_fees": "5.00",
                "size_inclusive_of_fees": False,
                "total_value_after_fees": "<string>",
                "trigger_status": "UNKNOWN_TRIGGER_STATUS",
                "order_type": "UNKNOWN_ORDER_TYPE",
                "reject_reason": "REJECT_REASON_UNSPECIFIED",
                "settled": True,
                "product_type": "UNKNOWN_PRODUCT_TYPE",
                "reject_message": "<string>",
                "cancel_message": "<string>",
                "order_placement_source": "UNKNOWN_PLACEMENT_SOURCE",
                "outstanding_hold_amount": "<string>",
                "is_liquidation": True,
                "last_fill_time": "<string>",
            }
        ]


class FakeAccountAPI(AccountAPI):
    def get_accounts(self) -> list[dict[str, Any]]:
        return [
            {
                "uuid": "8bfc20d7-f7c6-4422-bf07-8243ca4169fe",
                "name": "BTC Wallet",
                "currency": "BTC",
                "available_balance": {"value": "1.23", "currency": "BTC"},
                "default": False,
                "active": True,
                "created_at": "2021-05-31T09:59:59.000Z",
                "updated_at": "2021-05-31T09:59:59.000Z",
                "deleted_at": "2021-05-31T09:59:59.000Z",
                "type": "FIAT",
                "ready": True,
                "hold": {"value": "1.23", "currency": "BTC"},
                "retail_portfolio_id": "b87a2d3f-8a1e-49b3-a4ea-402d8c389aca",
                "platform": "ACCOUNT_PLATFORM_CONSUMER",
            }
        ]

    def get_account_usdc(self) -> dict[str, Any] | None:
        return {
            "uuid": "8bfc20d7-f7c6-4422-bf07-8243ca4169fe",
            "name": "USDC Wallet",
            "currency": "BTC",
            "available_balance": {"value": "5000.0", "currency": "USDC"},
            "default": False,
            "active": True,
            "created_at": "2021-05-31T09:59:59.000Z",
            "updated_at": "2021-05-31T09:59:59.000Z",
            "deleted_at": "2021-05-31T09:59:59.000Z",
            "type": "FIAT",
            "ready": True,
            "hold": {"value": "5000.0", "currency": "USDC"},
            "retail_portfolio_id": "b87a2d3f-8a1e-49b3-a4ea-402d8c389aca",
            "platform": "ACCOUNT_PLATFORM_CONSUMER",
        }

    def get_balance_usdc(self) -> float:
        return 5000.0


@dataclass
class FakeWebsocketAPI(WebsocketAPI):
    """A minimal fake that matches your `WebsocketAPI` protocol.

    Features:
      - Background loop started by `connect_and_listen()`
      - Enqueues JSON strings via `push_raw()` or Python dicts via `push()`
      - Calls `_on_message(ws, raw_json)` for each enqueued message
      - Records open/close/error events for assertions in tests

    Extra helpers (not part of the protocol):
      - `set_message_handler(func)` to intercept parsed tickers and drive your app logic
        (Optional: only needed if your tests want a callback like the real listener has.)
    """

    # Optional test callback: receives (timestamp, price) extracted from ticker payloads
    on_ticker: Callable[[datetime, float], None] | None = None

    # Internal state
    _ws: WebSocket | None = None
    _stop_evt: Event = field(default_factory=Event)
    _thread: Thread | None = None
    _q: queue.Queue[str] = field(default_factory=queue.Queue)

    # Observability for tests
    opened: bool = False
    closed: bool = False
    last_close: tuple[int | None, str | None] | None = None
    last_error: str | None = None

    # --------------------- Protocol methods ---------------------

    def stop(self) -> None:
        self._stop_evt.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
        self.closed = True

    def on_open(self, ws: WebSocket) -> None:
        self.opened = True
        self._ws = ws

    def _on_message(self, ws: WebSocket, raw_message: str) -> None:
        data = self._json_or_none(raw_message)
        if not data:
            return

        # Guard: only care about ticker channel if present
        ch = data.get("channel")
        if ch and ch != "ticker":
            return

        # Timestamp
        ts_raw = data.get("timestamp") or data.get("time")
        dt = self._parse_iso_utc(ts_raw)

        # Price (supports both flat {'price':...} and events->tickers shapes)
        price = None
        if "price" in data:
            price = data.get("price")
        else:
            for ev in data.get("events") or []:
                if not isinstance(ev, dict):
                    continue
                for tk in ev.get("tickers") or []:
                    if "price" in tk:
                        price = tk.get("price")
                        break
                if price is not None:
                    break

        if price is None or self.on_ticker is None:
            return

        try:
            self.on_ticker(dt, float(price))
        except Exception:
            # keep fake resilient in tests
            suppress(Exception)

    def _json_or_none(self, raw: str) -> dict[str, Any] | None:
        try:
            obj = json.loads(raw)
            return obj if isinstance(obj, dict) else None
        except Exception:
            return None

    def _parse_iso_utc(self, ts: str | None) -> datetime:
        if not ts or not isinstance(ts, str):
            return datetime.now(UTC)
        # normalize: strip trailing Z, pad micros
        s = ts[:-1] if ts.endswith("Z") else ts
        if "." in s:
            base, frac = s.split(".", 1)
            s = f"{base}.{(frac + '000000')[:6]}"
        try:
            return datetime.fromisoformat(s).replace(tzinfo=UTC)
        except Exception:
            return datetime.now(UTC)

    def on_error(self, ws: WebSocket, err: str) -> None:
        self.last_error = str(err)

    def on_close(self, ws: WebSocket, code: int, msg: str) -> None:
        self.closed = True
        self.last_close = (code, msg)

    def connect_and_listen(self) -> None:
        """Start a small background loop that feeds queued messages to `_on_message`."""
        if self._thread and self._thread.is_alive():
            return
        self._stop_evt.clear()

        # A tiny dummy WebSocket object for signature compatibility
        class _DummyWS:
            def send(self, *_args: Any, **_kwargs: Any) -> None:  # pragma: no cover
                return

        dummy_ws = cast("WebSocket", _DummyWS())
        self.on_open(dummy_ws)  # mark opened

        def _loop() -> None:
            while not self._stop_evt.is_set():
                try:
                    raw = self._q.get(timeout=0.1)
                except queue.Empty:
                    continue
                self._on_message(dummy_ws, raw)

        self._thread = Thread(target=_loop, daemon=True)
        self._thread.start()

    # --------------------- Test helpers (not in protocol) ---------------------

    def push_raw(self, raw_json: str) -> None:
        """Inject a raw JSON string to be processed by the background loop."""
        self._q.put(raw_json)

    def push(self, payload: dict[str, Any]) -> None:
        """Inject a Python dict; it will be JSON-encoded and processed."""
        self._q.put(json.dumps(payload))

    def set_message_handler(self, handler: Callable[[datetime, float], None]) -> None:
        """Register a convenience ticker handler, consistent with your real listener's API."""
        self.on_ticker = handler
