from __future__ import annotations

from src.container import build_fake_services
from src.settings.loader import init_config


def test_build_services_with_fakes_and_use_ports() -> None:
    init_config()  # ensure global config is set

    svcs = build_fake_services()

    # Ports available
    assert hasattr(svcs.product_api, "get_historic_candles")
    assert callable(svcs.order_api.get_orders)
    assert callable(svcs.account_api.get_accounts)
