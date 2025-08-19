from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from api.account import AccountClient
from api.clock import SystemClock
from api.fakes import (
    FakeAccountAPI,
    FakeClock,
    FakeOrderAPI,
    FakeProductAPI,
    FakeWebsocketAPI,
)
from api.order import OrderClient
from api.product import ProductClient

if TYPE_CHECKING:
    from api.ports import AccountAPI, Clock, OrderAPI, ProductAPI, WebSocketAPI
    from api.websocket import WebSocketListener


@dataclass(frozen=True)
class Services:
    clock: Clock
    product_api: ProductAPI
    order_api: OrderAPI
    account_api: AccountAPI
    websocket_api: WebSocketAPI | None


def build_services(websocket_api: WebSocketListener | None = None) -> Services:
    return Services(
        clock=SystemClock(),
        product_api=ProductClient(),
        order_api=OrderClient(),
        account_api=AccountClient(),
        websocket_api=websocket_api,
    )


def build_fake_services() -> Services:
    return Services(
        clock=FakeClock(),
        product_api=FakeProductAPI(),
        order_api=FakeOrderAPI(),
        account_api=FakeAccountAPI(),
        websocket_api=FakeWebsocketAPI(),
    )
