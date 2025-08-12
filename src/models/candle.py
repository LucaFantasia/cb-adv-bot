"""
candle.py — OHLCV Candle Data Structure

Represents a single price candle, including time, prices,
and optional volume. All times are assumed to be UTC.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Candle:
    """
    Candle represents one OHLCV data point at a fixed granularity.

    Attributes:
        time: Start time of the candle (UTC)
        open: opening price
        high: highest price
        low: lowest price
        close: closing price
        volume: volume traded
    """

    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float | None = None
