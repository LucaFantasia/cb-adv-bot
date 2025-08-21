from pydantic.type_adapter import TypeAdapter

from api.product_models import Candle, Product

_candle_adapter = TypeAdapter(list[Candle])


def test_parse_product() -> None:
    payload = {
        "product_id": "BTC-USD",
        "price": "140.21",
        "price_percentage_change_24h": "9.43%",
        "volume_24h": "1908432",
        "volume_percentage_change_24h": "9.43%",
        "unknown_field_we_ignore": {"x": 1},
    }
    product = Product.model_validate(payload)
    assert product.product_id == "BTC-USD"
    assert product.price == "140.21"
    assert product.price_percentage_change_24h == "9.43%"
    assert product.volume_24h == "1908432"
    assert product.volume_percentage_change_24h == "9.43%"
    assert "unknown_field_we_ignore" not in product.model_dump()


def test_parse_candle_list() -> None:
    payload = {
        "candles": [
            {
                "start": "1639508050",
                "low": "140.21",
                "high": "141.00",
                "open": "140.50",
                "close": "140.90",
                "volume": "100",
            },
            {
                "start": "1639508051",
                "low": "140.21",
                "high": "141.00",
                "open": "140.50",
                "close": "140.90",
                "volume": "100",
            },
        ]
    }
    candles = _candle_adapter.validate_python(payload.get("candles", []))
    assert len(candles) == len(payload.get("candles", []))
    candle = candles[0]
    assert candle.start == "1639508050"
    assert candle.open == "140.50"
    assert candle.close == "140.90"
