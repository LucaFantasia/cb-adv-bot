from __future__ import annotations

from time import sleep
from typing import TYPE_CHECKING

from src.api.fakes import FakeWebSocketAPI

if TYPE_CHECKING:
    from datetime import datetime


def test_fake_ws_emits_ticker_on_push() -> None:
    prices: list[tuple[datetime, float]] = []

    ws = FakeWebSocketAPI()
    ws.set_message_handler(lambda ts, px: prices.append((ts, px)))

    ws.connect_and_listen()
    ws.push(
        {
            "channel": "ticker",
            "timestamp": "2025-08-19T12:00:00Z",
            "events": [
                {"type": "update", "tickers": [{"product_id": "BTC-USD", "price": "65000"}]}
            ],
        }
    )

    # tiny wait for the background thread
    sleep(0.05)
    ws.stop()

    price_diff = 1e-6

    assert len(prices) == 1
    ts, px = prices[0]
    assert ts.tzinfo is not None
    assert abs(px - 65000.0) < price_diff


def test_fake_ws_ignores_non_json_and_non_ticker() -> None:
    prices: list[tuple[datetime, float]] = []
    ws = FakeWebSocketAPI(on_ticker=lambda ts, px: prices.append((ts, px)))
    ws.connect_and_listen()

    ws.push_raw("not-json")
    ws.push({"channel": "level2", "timestamp": "2025-08-19T12:00:00Z"})  # not ticker

    sleep(0.05)
    ws.stop()

    assert prices == []
