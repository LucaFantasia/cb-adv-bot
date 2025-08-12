"""
websocket.py — Coinbase WebSocket Listener

Establishes a WebSocket connection to the Advanced Trade feed
to receive real-time price data via the 'ticker' channel.
"""

import json
import time
from collections.abc import Callable
from datetime import UTC, datetime

from websocket import WebSocketApp

from utils.logger import logger


class WebSocketListener:
    """
    WebSocketListener - Connects to Coinbase's real-time ticker feed
    """

    def __init__(self, product_id: str, on_message: Callable[[datetime, float], None]) -> None:
        self.product_id = product_id
        self.on_message = on_message
        self.reconnect_delay = 5.0
        self.ws: WebSocketApp = None
        self.stopped_flag = False

    def stop(self) -> None:
        self.stopped_flag = True
        if self.ws:
            self.ws.close()

    def on_open(self, ws: WebSocketApp) -> None:
        subscribe_msg = {"type": "subscribe", "channel": "ticker", "product_ids": [self.product_id]}
        ws.send(json.dumps(subscribe_msg))
        logger.info(f"[WS - {self.product_id}] connected and subscribed.")

    def _on_message(self, ws: WebSocketApp, raw_message: str) -> None:
        try:
            data = json.loads(raw_message)
            if data.get("channel") != "ticker":
                return

            timestamp_str = data.get("timestamp") or data.get("time")
            if not timestamp_str:
                logger.debug(f"[WS - {self.product_id}] missing timestamp")
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
                logger.debug(f"[WS - {self.product_id}] malformed events: {events}")
                return

            for event in events:
                if event.get("type") in ("snapshot", "update"):
                    for ticker in event.get("tickers", []):
                        if ticker.get("product_id") == self.product_id:
                            price = float(ticker.get("price"))
                            self.on_message(timestamp, price)

        except Exception as e:
            logger.error(f"[WS - {self.product_id}] message parse error: {e}")

    def on_error(self, ws: WebSocketApp, err: str) -> None:
        logger.error(f"[WS - {self.product_id}] error: {err}")

    def on_close(self, ws: WebSocketApp, code: int, msg: str) -> None:
        logger.info(f"[WS - {self.product_id}] closed: {code}, {msg}")

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
                logger.error(f"[WS - {self.product_id}] connection exception: {e}")

            if not self.stopped_flag:
                logger.info(
                    f"[WS - {self.product_id}] reconnecting in {self.reconnect_delay:.1f}s..."
                )
                time.sleep(self.reconnect_delay)
