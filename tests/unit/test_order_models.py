from pydantic.type_adapter import TypeAdapter

from api.order_models import Order, OrderReceipt

_order_adapter = TypeAdapter(list[Order])


def test_parse_order_list() -> None:
    payload = {
        "orders": [
            {
                "order_id": "0000-000000-000000",
                "product_id": "BTC-USD",
                "user_id": "2222-000000-000000",
                "order_configuration": {
                    "limit_limit_gtc": {
                        "quote_size": "10.00",
                        "base_size": "0.001",
                        "limit_price": "10000.00",
                        "post_only": False,
                    }
                },
                "side": "BUY",
                "client_order_id": "11111-000000-000000",
                "status": "PENDING",
            }
        ]
    }
    orders = _order_adapter.validate_python(payload.get("orders", []))
    assert len(orders) == 1
    order = orders[0]
    assert order.product_id == "BTC-USD"
    assert order.side == "BUY"
    assert not order.order_configuration.limit_limit_gtc.post_only


def test_parse_order_receipt() -> None:
    payload = {
        "success": True,
        "success_response": {
            "order_id": "11111-00000-000000",
            "product_id": "BTC-USD",
            "side": "BUY",
            "client_order_id": "0000-00000-000000",
        },
        "error_response": {
            "error": "UNKNOWN_FAILURE_REASON",
            "message": "The order configuration was invalid",
            "error_details": "Market orders cannot be placed with empty order sizes",
            "preview_failure_reason": "UNKNOWN_PREVIEW_FAILURE_REASON",
            "new_order_failure_reason": "UNKNOWN_FAILURE_REASON",
        },
        "order_configuration": {
            "limit_limit_gtc": {
                "quote_size": "10.00",
                "base_size": "0.001",
                "limit_price": "10000.00",
                "post_only": False,
            }
        },
    }
    order_receipt = OrderReceipt.model_validate(payload)
    assert order_receipt.success
    assert order_receipt.success_response.side == "BUY"
    assert order_receipt.error_response.error == "UNKNOWN_FAILURE_REASON"
    assert not order_receipt.order_configuration.limit_limit_gtc.post_only
