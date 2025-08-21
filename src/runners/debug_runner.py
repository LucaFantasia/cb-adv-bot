from datetime import UTC, datetime, timedelta

from container import build_services


def main() -> None:
    services = build_services()

    end = datetime.now(UTC)
    start = end - timedelta(days=7)
    print(services.product_api.get_historic_candles("BTC-USD", start, end, 15, "FIFTEEN_MINUTE"))
