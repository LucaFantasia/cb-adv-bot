"""
product.py — Product data client for Coinbase Advanced Trade API

Handles:
- Batched candle fetching (for >350 bar spans)
- Time-ranged OHLCV retrieval
"""

import os
from datetime import datetime, timedelta
from typing import Any

from .base import BaseClient


class ProductClient(BaseClient):
    """
    Handles historical product data access via Coinbase REST API.
    """

    def get_product(self, product_id: str) -> Any | None:
        """
        Retrieve metadata for a specific trading pair (e.g., BTC-USD)
        """
        return self.get(f"products/{product_id}")

    def _get_product_candles(
        self, product_id: str, start: datetime, end: datetime, granularity: str
    ) -> list[list[float]]:
        """
        Basic wrapper for Coinbase candle endpoint (max ~350 bars per request).

        Args:
            product_id: "BTC-USD", "ETH-USD", etc.
            start_time: ISO timestamp
            end_time: ISO timestamp
            granularity: String granularity (e.g., "FIVE_MINUTE")

        Returns:
            Raw list of candles (each is a list of OHLCV values)
        """
        params = {
            "start": int(start.timestamp()),
            "end": int(end.timestamp()),
            "granularity": granularity,
        }

        result = self.get(f"products/{product_id}/candles", params=params)
        return result.get("candles", []) if result else []

    def get_historic_candles(
        self,
        product_id: str,
        start_time: datetime,
        end_time: datetime,
        granularity_mins: int,
        granularity_str: str,
    ) -> list[list[float]]:
        """
        Returns OHLCV data across multiple API calls if necessary.

        Args:
            product_id: Pair symbol (e.g., "BTC-USD")
            start_time: Start timestamp
            end_time: Final timestamp
            granularity_in_minutes: Candlestick size
            granularity_str: API granularity enum

        Returns:
            List of OHLCV candle rows (newest first)
        """
        span = timedelta(
            seconds=granularity_mins * 60 * self._as_int(os.getenv("MAX_CANDLES_PER_CALL"))
        )
        cursor = start_time
        all_candles = []

        while cursor < end_time:
            chunk_end = min(cursor + span, end_time)
            candle_batch = self._get_product_candles(product_id, cursor, chunk_end, granularity_str)
            if not candle_batch:
                break
            all_candles.extend(candle_batch)
            cursor = chunk_end + timedelta(seconds=granularity_mins * 60)

        return all_candles

    def _as_int(self, value: int | str | None, default: int = 1) -> int:
        if value is None:
            return default
        return value if isinstance(value, int) else int(value)
