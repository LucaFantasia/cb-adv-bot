from pydantic.type_adapter import TypeAdapter

from api.account_models import Account

_account_adapter = TypeAdapter(list[Account])


def test_parse_account_list() -> None:
    payload = {
        "accounts": [
            {
                "uuid": "8bfc20d7-f7c6-4422-bf07-8243ca4169fe",
                "name": "BTC Wallet",
                "currency": "BTC",
                "available_balance": {"value": "1.23", "currency": "BTC"},
            }
        ]
    }
    accounts = _account_adapter.validate_python(payload.get("accounts", []))
    assert len(accounts) == 1
    account = accounts[0]
    assert account.name == "BTC Wallet"
    assert account.currency == "BTC"
    assert account.available_balance.value == "1.23"
    assert account.available_balance.currency == "BTC"
