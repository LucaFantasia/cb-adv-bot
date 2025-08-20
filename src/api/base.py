"""
base.py - Shared Coinbase API client foundation

This module defines the `BaseClient` class, responsible for:
- Managing authentication via JWT
- Executing HTTP GET and POST requests
- Handling headers, errors, and logging
- Acting as the parent for domain-specific API clients (orders, products, etc.)
"""

import json
import os
from typing import Any

from dotenv import load_dotenv

from utils.logging_config import get_logger

from .auth import JWTAuth
from .http import HttpClient
from .utils import idempotency_key


class BaseClient:
    """
    BaseClient - Coinbase API base class
    Handles authenticated GET and POST requests using JWT.
    """

    def __init__(self, auth: JWTAuth | None = None, http: HttpClient | None = None) -> None:
        load_dotenv()
        self.auth = auth or JWTAuth()
        self.host = os.getenv("CB_HOST_NAME")
        self.api_path = os.getenv("CB_API_PATH")
        self.http = http or HttpClient()
        self.logger = get_logger(__name__)

    def _headers(self, method: str, query: str) -> dict[str, str]:
        uri = f"{method} {self.host}{self.api_path}{query}"
        token = self.auth.generate_jwt(uri)
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def _url(self, query: str) -> str:
        return f"https://{self.host}{self.api_path}{query}"

    def get(self, query: str, params: dict[str, Any] | None = None) -> Any | None:
        url = self._url(query)
        headers = self._headers("GET", query)
        response = self.http.request("GET", url, headers=headers, params=params)

        if not response.ok:
            self.logger.error(
                "Failed GET request",
                extra={"url": url, "status_code": response.status_code, "text": response.text},
            )
            return None

        return response.json

    def post(self, query: str, body: dict[str, Any] | None = None) -> Any | None:
        url = self._url(query)
        headers = self._headers("POST", query)
        payload = json.dumps(body) if body else ""
        # Safety: idempotency for order POSTs
        if query == "orders" and "Idempotency-Key" not in headers:
            headers["Idempotency-Key"] = idempotency_key()

        response = self.http.request("POST", url, headers=headers, data=payload)

        if not response.ok:
            self.logger.error(
                "Failed POST request",
                extra={"url": url, "status_code": response.status_code, "text": response.text},
            )
            return None
        return response.json
