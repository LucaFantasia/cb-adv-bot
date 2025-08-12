"""
extrema_detector.py - Local extremum detection

Finds local maximas and minimas in OHLCV candle data by comparing
each point to its surrounding window.
"""

import pandas as pd


def find_local_extrema(
    df: pd.DataFrame, window_size: int
) -> tuple[list[tuple[str, float, int]], list[tuple[str, float, int]]]:
    """
    Identifies local maximas and minimas in the 'High' and 'Low' columns
    of a DataFrame using a fixed neighbourhood window.

    Args:
        df: DataFrame indexed by timestamp with columns 'High' and 'Low'.
        window_size: Number of candles on either side to check for local extremas.

    Returns:
        Tuple of:
            - list of maximas: (literal, high, index)
            - list of minimas: (literal, low, index)
    """
    highs = df["High"]
    lows = df["Low"]

    maximas = []
    minimas = []

    for i in range(window_size, len(df) - window_size):
        window_highs = highs.iloc[i - window_size : i + window_size + 1]
        window_lows = lows.iloc[i - window_size : i + window_size + 1]

        if highs.iloc[i] == window_highs.max():
            maximas.append(("maxima", highs.iloc[i], i))
        elif lows.iloc[i] == window_lows.min():
            minimas.append(("minima", lows.iloc[i], i))

    return maximas, minimas
