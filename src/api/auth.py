"""
auth.py - Coinbase JWT Authentication Helper

This module defines the `JWTAuth` class, which generates
JSON Web Tokens (JWTs) to authenticate REST API requests
to the Coinbase Advanced Trade API.

Key reponsibilities:
- Load API credentials from .env
- Generate signed JWTs for Rest endpoints
"""

import base64
import os
import secrets
import time
from typing import Any

import jwt
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from dotenv import load_dotenv


class JWTAuth:
    """
    JWTAuth - Coinbase JWT Generator

    This class reads credentials from environment variables and
    produces a signed edDSA JWT for authenticating a specific REST API URI.
    """

    def __init__(self) -> None:
        load_dotenv()
        self.key_id = os.getenv("CDP_API_KEY_ID")
        self.key_secret = os.getenv("CDP_API_KEY_SECRET")
        if not self.key_id or not self.key_secret:
            raise ValueError("Missing Coinbase API credentials in .env")

    def generate_jwt(self, uri: str) -> Any:
        """
        Generate a JWT signed with Ed25519 for a given URI.
        """
        if not self.key_secret:
            raise ValueError("Missing base64-encoded private key")
        private_key_bytes = base64.b64decode(self.key_secret)[:32]
        private_key = Ed25519PrivateKey.from_private_bytes(private_key_bytes)

        payload = {
            "sub": self.key_id,
            "iss": "cdp",
            "nbf": int(time.time()),
            "exp": int(time.time()) + 120,
            "uri": uri,
        }

        headers = {"kid": self.key_id, "nonce": secrets.token_hex()}

        return jwt.encode(payload, private_key, algorithm="EdDSA", headers=headers)
