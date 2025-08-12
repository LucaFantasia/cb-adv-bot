"""
touch_detector.py - Trend line touch detection

Detects whether trend lines intersect candle highs/lows
at extrema points (minima or maxima), within a deviation.
Returns ScoredLine objects.
"""

import numpy as np
import pandas as pd

from models.scored_line import ScoredLine
from models.trend_line import TrendLine


def detect_touches_for_line(
    line: TrendLine,
    proj_prices: np.ndarray,
    extremas: list[tuple[str, float, int]],
    deviation_price: float,
    df: pd.DataFrame,
) -> ScoredLine:
    """
    Detects touch points for a trend line and returns a ScoredLine object.

    A touch is recorded if the projected line price intersects the candle's high/low body within
    the given deviation threshold.

    Args:
        line: TrendLine object
        candle_indices: Array of candle indices used for projecting prices
        extremas: list of maxima and minima points tuple(Literal["maxima", "minima"], price, index)
        deviation_price: Permissible deviation price from candle body
        df: DataFrame containing all candle data

    Returns:
        ScoredLine object containing the line and touch points
    """
    highs = df["High"].values
    lows = df["Low"].values
    opens = list((df["Open"].values).astype(float))
    closes = list((df["Close"].values).astype(float))
    body_highs = np.maximum(opens, closes)
    body_lows = np.minimum(opens, closes)

    touches = []
    for type, _, i in extremas:
        proj_price = proj_prices[i]

        in_upper = highs[i] + deviation_price >= proj_price >= body_highs[i] - deviation_price
        in_lower = lows[i] - deviation_price <= proj_price <= body_lows[i] + deviation_price

        if (type == "maxima" and in_upper) or (type == "minima" and in_lower):
            touches.append(i)

    return ScoredLine(line=line, touches=touches)
