from api.fakes import FakeAccountAPI


def test_get_accounts() -> None:
    fake = FakeAccountAPI()
    accounts = fake.get_accounts()

    assert len(accounts) == 1
    assert accounts[0].currency == "BTC"


def test_get_account_usdc() -> None:
    fake = FakeAccountAPI()
    account = fake.get_account_usdc()

    if account:
        assert account.currency == "USDC"


def test_get_balance_usdc() -> None:
    expected_balance = 5000.0
    fake = FakeAccountAPI()
    balance = fake.get_balance_usdc()

    assert balance == expected_balance
