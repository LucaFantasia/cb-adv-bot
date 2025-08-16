"""
account.py — Coinbase Account API Client

Handles retrieval of account balances and wallet metadata.
Currently supports full account list and USDC-specific balance queries.
"""

from typing import Any

from api.base import BaseClient
from api.ports import AccountAPI


class AccountClient(BaseClient, AccountAPI):
    """
    AccountClient — Fetches wallet info and available balances
    """

    def get_accounts(self) -> list[dict[str, Any]]:
        """
        Retrieve all trading accounts (one per currency).
        """
        response = self.get("accounts")
        return response.get("accounts", []) if response else []

    def get_account_usdc(self) -> dict[str, Any] | None:
        """
        Return the account dict associated with the USDC wallet.
        """
        for account in self.get_accounts():
            if account.get("currency") == "USDC":
                return account
        return None

    def get_balance_usdc(self) -> float:
        """
        Return the available USDC balance.
        """
        account = self.get_account_usdc()
        if not account:
            raise RuntimeError("USDC account not found.")
        return float(account["available_balance"]["value"])
