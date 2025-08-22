from api.fakes import FakeOrderAPI


def test_place_buy_limit_order() -> None:
    product_id = "BTC-USD"
    post_only = True
    limit_price = "10000.00"
    base_size = "10.00"
    fake = FakeOrderAPI()
    receipt = fake.place_usdc_buy_limit_order(product_id, post_only, limit_price, base_size)

    assert len(fake.placed_buy_orders) == 1
    assert fake.placed_buy_orders[0] == (product_id, post_only, limit_price, base_size)

    if receipt:
        assert receipt.success
        assert receipt.success_response.product_id == product_id
        assert receipt.order_configuration.limit_limit_gtc.base_size == base_size
        assert receipt.order_configuration.limit_limit_gtc.limit_price == limit_price
        assert receipt.order_configuration.limit_limit_gtc.post_only == post_only


def test_get_orders() -> None:
    fake = FakeOrderAPI()
    orders = fake.get_orders()

    assert len(orders) == 1
    assert orders[0].product_id == "BTC-USD"
