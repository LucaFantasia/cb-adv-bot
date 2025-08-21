"""
candle_loader.py - Raw candle processing utilities

Converts raw candle dictionaries into clean, typed DataFrame for
further analysis, and computes volatility statistics.
"""

from datetime import UTC, datetime

import numpy as np
import pandas as pd

from api.product_models import Candle


def candles_to_dataframe(candles: list[Candle]) -> pd.DataFrame:
    """
    Converts raw candle list into a sorted DataFrame indexed by UTC datetime.
    Assumes each candle has 'start', 'open', 'high', 'low', 'close', 'volume'.
    """
    df = pd.DataFrame(
        {
            "Date": [datetime.fromtimestamp(int(c.start), tz=UTC) for c in candles],
            "Open": [float(c.open) for c in candles],
            "High": [float(c.high) for c in candles],
            "Low": [float(c.low) for c in candles],
            "Close": [float(c.close) for c in candles],
            "Volume": [float(c.volume) for c in candles],
        }
    )
    df.set_index("Date", inplace=True)
    df.sort_index(inplace=True)
    return df


def compute_avg_volatility_pct(candles: list[Candle]) -> float:
    """
    Computes the standard deviation of log returns of closing prices,
    scaled by 10 to yield a pseudo-percentage measure of volatility.
    """
    closes = np.array([float(c.close) for c in candles])
    log_returns = np.diff(np.log(closes))
    return float(10 * np.std(log_returns))
