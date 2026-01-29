import json
import time
from datetime import UTC, datetime

from websocket import WebSocketApp

from api.ports import WebSocketAPI
from utils.logging_config import get_logger


class CoinbaseWebSocket(WebSocketAPI):
    def __init__(self, product_id: str) -> None:
        self.product_id = product_id
        self.logger = get_logger(__name__)
        self.ws: WebSocketApp | None = None
        self.stopped_flag = False

    def connect_and_listen(self) -> None:
        self.ws = WebSocketApp(
            "wss://advanced-trade-ws.coinbase.com",
            on_open=self.on_open,
            on_message=self._on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )

        while not self.stopped_flag:
            self.ws.run_forever()
            time.sleep(1)

    def stop(self) -> None:
        self.stopped_flag = True
        if self.ws:
            self.ws.close()

    def on_open(self, ws: WebSocketApp) -> None:
        subscribe_msg = {
            "type": "subscribe",
            "channel": "ticker",
            "product_ids": [self.product_id],
        }
        ws.send(json.dumps(subscribe_msg))
        self.logger.info("connected", extra={"product_id": self.product_id})

    def _on_message(self, ws: WebSocketApp, raw_message: str) -> None:
        try:
            data = json.loads(raw_message)

            if data.get("channel") != "ticker":
                return

            events = data.get("events", [])
            if not events:
                return

            ticker = events[0].get("tickers", [{}])[0]
            price = float(ticker["price"])
            timestamp_str = ticker.get("time")

            if not timestamp_str:
                return

            if timestamp_str.endswith("Z"):
                timestamp_str = timestamp_str[:-1]

            timestamp = datetime.fromisoformat(timestamp_str).replace(tzinfo=UTC)

            self.logger.debug(
                "ticker",
                extra={
                    "product_id": self.product_id,
                    "price": price,
                    "timestamp": timestamp,
                },
            )

        except Exception as e:
            self.logger.error(
                "message parse error",
                extra={"product_id": self.product_id, "error_message": str(e)},
            )

    def on_error(self, ws: WebSocketApp, err: object) -> None:
        self.logger.error(
            "websocket error",
            extra={"product_id": self.product_id, "error_message": str(err)},
        )

    def on_close(self, ws: WebSocketApp, code: object, msg: object) -> None:
        self.logger.info(
            "websocket closed",
            extra={
                "product_id": self.product_id,
                "code": code,
                "message": msg,
            },
        )
