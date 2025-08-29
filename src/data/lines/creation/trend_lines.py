"""
trend_lines.py - Trend line generation from extrema

Generates raw support/resistance lines from extrema pairs.
Each line connects two extrema and is later filtered/scored separately.
"""

import math

import pandas as pd

from models.trend_line import TrendLine
from utils.timer import Timer


def generate_trend_lines(
    extrema: list[tuple[str, float, int]],
    df: pd.DataFrame,
    max_slope_deg: float,
    min_duration_candles: int,
    price_deviation: float,
) -> list[TrendLine]:
    """
    Builds trend lines from extrema pairs (minima or maxima).

    Filters by:
        - Duration between extrema
        - Slope steepness
        - Deviation from latest price

    Args:
        extrema: List of (timestamp, price, index) tuples
        df: Full OHLCV candle DataFrame
        max_slope_deg: Maximum slope steepness in degrees (e.g 70 degrees)
        min_duration_candles: Minimum candle distance between extrema
        price_deviation: Acceptable price deviation multiple of price range

    Returns:
        List of potentially valid TrendLine objects
    """
    with Timer("trend line generation"):
        lines = []

        first_price = df["Close"].iloc[0]
        last_price = df["Close"].iloc[-1]
        last_idx = len(df) - 1

        for i in range(len(extrema)):
            for j in range(i + 1, len(extrema)):
                _, p1, idx1 = extrema[i]
                _, p2, idx2 = extrema[j]

                delta_x = idx2 - idx1
                if delta_x < min_duration_candles:
                    continue

                slope = (p2 - p1) / delta_x
                intercept = p1 - slope * idx1

                if abs(math.degrees(math.atan(slope))) > max_slope_deg:
                    continue

                last_projected_price = slope * last_idx + intercept
                if abs(last_projected_price - last_price) / last_price > price_deviation:
                    continue

                state = "resistance" if intercept > first_price else "support"

                line = TrendLine(
                    slope=float(slope),
                    intercept=float(intercept),
                    state=state,
                    start_index=int(idx1),
                    end_index=int(idx2),
                )
                lines.append(line)

        def key(line: TrendLine) -> tuple[int, int, float, float]:
            return (
                line.start_index,
                line.end_index,
                round(line.slope, 12),
                round(line.intercept, 8),
            )

        seen: set[tuple[int, int, float, float]] = set()
        dedup: list[TrendLine] = []
        for line in lines:
            key_val = key(line)
            if key_val not in seen:
                seen.add(key_val)
                dedup.append(line)

    return dedup
