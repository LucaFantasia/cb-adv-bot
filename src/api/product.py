"""
product.py — Product data client for Coinbase Advanced Trade API

Handles:
- Batched candle fetching (for >350 bar spans)
- Time-ranged OHLCV retrieval
"""

from datetime import datetime, timedelta

from pydantic import ValidationError
from pydantic.type_adapter import TypeAdapter

from api.base import BaseClient
from api.ports import ProductAPI
from api.product_models import Candle, Product
from settings.loader import get_config

_candles_adapter = TypeAdapter(list[Candle])


class ProductClient(BaseClient, ProductAPI):
    """
    Handles historical product data access via Coinbase REST API.
    """

    def get_product(self, product_id: str) -> Product | None:
        """
        Retrieve metadata for a specific trading pair (e.g., BTC-USD)
        """
        raw = self.get(f"products/{product_id}")
        if raw is None:
            return None
        try:
            return Product.model_validate(raw)
        except ValidationError as error:
            self.logger.error(
                "get_product: parse failed",
                extra={"product_id": product_id, "errors": error.errors()},
            )
            return None

    def _get_product_candles(
        self, product_id: str, start: datetime, end: datetime, granularity: str
    ) -> list[Candle]:
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

        raw = self.get(f"products/{product_id}/candles", params=params)
        if raw is None:
            return []

        items = raw.get("candles", [])
        try:
            return _candles_adapter.validate_python(items)
        except Exception:
            self.logger.exception("Failed to parse candles", extra={"count": len(items)})
            return []

    def get_historic_candles(
        self,
        product_id: str,
        start_time: datetime,
        end_time: datetime,
        granularity_mins: int,
        granularity_str: str,
    ) -> list[Candle]:
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
        config = get_config()
        span = timedelta(seconds=granularity_mins * 60 * config.candle.max_candles_per_call)
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
