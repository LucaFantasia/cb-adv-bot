"""
account.py — Coinbase Account API Client

Handles retrieval of account balances and wallet metadata.
Currently supports full account list and USDC-specific balance queries.
"""

from pydantic.type_adapter import TypeAdapter

from api.account_models import Account
from api.base import BaseClient
from api.ports import AccountAPI

_account_adapter = TypeAdapter(list[Account])


class AccountClient(BaseClient, AccountAPI):
    """
    AccountClient — Fetches wallet info and available balances
    """

    def get_accounts(self) -> list[Account]:
        """
        Retrieve all trading accounts (one per currency).
        """
        raw = self.get("accounts")
        if raw is None:
            return []

        items = raw.get("accounts", [])
        try:
            return _account_adapter.validate_python(items)
        except Exception:
            self.logger.error("Failed to parse accounts", extra={"count": len(items)})
            return []

    def get_account_usdc(self) -> Account | None:
        """
        Return the account dict associated with the USDC wallet.
        """
        for account in self.get_accounts():
            if account.currency == "USDC":
                return account
        return None

    def get_balance_usdc(self) -> float:
        """
        Return the available USDC balance.
        """
        account = self.get_account_usdc()
        if not account:
            raise RuntimeError("USDC account not found.")
        return float(account.available_balance.value)
