from datetime import UTC, datetime, timedelta

from api.fakes import FakeProductAPI


def test_get_product() -> None:
    product_id = "BTC'USD"
    fake = FakeProductAPI()
    product = fake.get_product(product_id)

    assert len(fake.product_calls) == 1
    assert fake.product_calls[0] == product_id

    if product:
        assert product.product_id == product_id
        assert product.price == "140.21"


def test_get_historic_candles() -> None:
    end = datetime.now(UTC)
    start = end - timedelta(days=7)
    fake = FakeProductAPI()
    candles = fake.get_historic_candles("BTC-USD", start, end, 15, "FIFTEEN_MINUTE")

    assert len(fake.candle_calls) == 1
    assert fake.candle_calls[0] == ("BTC-USD", start, end, 15, "FIFTEEN_MINUTE")
    assert len(candles) == 1
    assert candles[0].low == "140.21"
