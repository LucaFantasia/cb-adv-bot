"""
websocket.py — Coinbase WebSocket Listener

Establishes a WebSocket connection to the Advanced Trade feed
to receive real-time price data via the 'ticker' channel.
"""

import json
import time
from collections.abc import Callable
from datetime import UTC, datetime

from websocket import WebSocket, WebSocketApp

from utils.logging_config import get_logger


class WebSocketListener:
    """
    WebSocketListener - Connects to Coinbase's real-time ticker feed
    """

    def __init__(self, product_id: str, on_message: Callable[[datetime, float], None]) -> None:
        self.product_id = product_id
        self.on_message = on_message
        self.reconnect_delay = 5.0
        self.ws: WebSocketApp | None = None
        self.stopped_flag = False
        self.logger = get_logger(__name__)

    def stop(self) -> None:
        self.stopped_flag = True
        if self.ws:
            self.ws.close()

    def on_open(self, ws: WebSocket) -> None:
        subscribe_msg = {"type": "subscribe", "channel": "ticker", "product_ids": [self.product_id]}
        ws.send(json.dumps(subscribe_msg))
        self.logger.info("connected", extra={"product_id": self.product_id})

    def _on_message(self, ws: WebSocket, raw_message: str) -> None:
        try:
            data = json.loads(raw_message)
            if data.get("channel") != "ticker":
                return

            timestamp_str = data.get("timestamp") or data.get("time")
            if not timestamp_str:
                self.logger.debug("missing timestamp", extra={"product_id": self.product_id})
                return

            if timestamp_str.endsWith("Z"):
                timestamp_str = timestamp_str[:-1]

            if "." in timestamp_str:
                base, frac = timestamp_str.split(".", 1)
                micro = (frac + "000000")[:6]
                timestamp_str = f"{base}.{micro}"

            timestamp = datetime.fromisoformat(timestamp_str).replace(tzinfo=UTC)
            events = data.get("events", [])

            if not isinstance(events, list):
                self.logger.debug(
                    "malformed events", extra={"product_id": self.product_id, "events": events}
                )
                return

            for event in events:
                if event.get("type") in ("snapshot", "update"):
                    for ticker in event.get("tickers", []):
                        if ticker.get("product_id") == self.product_id:
                            price = float(ticker.get("price"))
                            self.on_message(timestamp, price)

        except Exception as e:
            self.logger.error(
                "message parse error", extra={"product_id": self.product_id, "error_message": e}
            )

    def on_error(self, ws: WebSocket, err: str) -> None:
        self.logger.error("error", extra={"product_id": self.product_id, "error_message": err})

    def on_close(self, ws: WebSocket, code: int, msg: str) -> None:
        self.logger.info(
            "closed", extra={"product_id": self.product_id, "code": code, "message": msg}
        )

    def connect_and_listen(self) -> None:
        while not self.stopped_flag:
            self.ws = WebSocketApp(
                "wss://advanced-trade-ws.coinbase.com",
                on_open=self.on_open,
                on_message=self._on_message,
                on_error=self.on_error,
                on_close=self.on_close,
            )

            try:
                self.ws.run_forever(ping_interval=20, ping_timeout=10)
            except Exception as e:
                self.logger.error(
                    "connection exception", extra={"product_id": self.product_id, "message": e}
                )

            if not self.stopped_flag:
                self.logger.info(
                    f"reconnecting in {self.reconnect_delay:1f}s...",
                    extra={"product_id": self.product_id},
                )
                time.sleep(self.reconnect_delay)
