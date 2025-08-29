"""
extrema_detector.py - Local extremum detection (deterministic & vectorised)

Rules:
    - A point is a maxima iff its High is strictly greater than all neighbours in the window
    - A point is a minima iff its Low is strictly less than all neighnours in the window
    - Tie cases (equal high/lows) are ignored to keep determinism

Finds local maximas and minimas in OHLCV candle data by comparing
each point to its surrounding window.
"""

import numpy as np
import pandas as pd

from utils.timer import Timer


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
    with Timer("find_local_extrema"):
        highs = np.asarray(df["High"].to_numpy(copy=True), dtype=np.float32)
        lows = np.asarray(df["Low"].to_numpy(copy=True), dtype=np.float32)
        df_size = len(df)

        if df_size < (2 * window_size + 1):
            return [], []

        indices = np.arange(window_size, df_size - window_size, dtype=np.int32)
        centre_high = highs[indices]
        centre_low = lows[indices]

        neigh_left_max = np.array([np.max(highs[i - window_size : i]) for i in indices])
        neigh_right_max = np.array([np.max(highs[i + 1 : i + window_size + 1]) for i in indices])
        neigh_max = np.maximum(neigh_left_max, neigh_right_max)

        neigh_left_min = np.array([np.min(lows[i - window_size : i]) for i in indices])
        neigh_right_min = np.array([np.min(lows[i + 1 : i + window_size + 1]) for i in indices])
        neigh_min = np.minimum(neigh_left_min, neigh_right_min)

        maxima_mask = centre_high > neigh_max
        minima_mask = centre_low < neigh_min

        maxima_indices = indices[maxima_mask].tolist()
        minima_indices = indices[minima_mask].tolist()

        maximas = [("maxima", float(highs[i]), int(i)) for i in maxima_indices]
        minimas = [("minima", float(lows[i]), int(i)) for i in minima_indices]

    return maximas, minimas
