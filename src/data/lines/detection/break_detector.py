"""
break_detector.py - Detects breaks through trend lines

Detects breakouts based on deviation strength and recovery duration.
"""

import numpy as np

from models.scored_line import ScoredLine
from settings.config import config


def detect_breaks_for_line(
    line: ScoredLine,
    num_candles: int,
    closes: list[float],
    deviation_price: float,
    proj_prices: np.ndarray,
) -> ScoredLine:
    """
    Evaluates a single trend line for break points and soft touches.

    Returns an updated ScoredLine with break and soft touch indices.
    """
    state = line.line.state
    breaks: list[int] = []
    soft_touches: list[int] = []
    i = 0
    while i < num_candles:
        proj_price = proj_prices[i]
        close = closes[i]

        if state == "support" and close < proj_price:
            new_state = "resistance"
        elif state == "resistance" and close > proj_price:
            new_state = "support"
        else:
            i += 1
            continue

        # Break detected - now validate
        start = i
        max_height = abs(closes[i] - proj_price)
        peak = i
        j = i + 1

        while j < num_candles:
            proj_j = proj_prices[j]
            close_j = closes[j]

            if state == "support" and max_height < proj_j - close_j:
                max_height = proj_j - close_j
                peak = j
            elif state == "resistance" and max_height < close_j - proj_j:
                max_height = close_j - proj_j
                peak = j

            recovered = (new_state == "resistance" and close_j > proj_j) or (
                new_state == "support" and close_j < proj_j
            )
            if recovered:
                break

            j += 1

        duration = j - start
        break_added = False

        for factor, min_bars in config.strategy.break_criteria:
            if max_height >= factor * deviation_price and duration >= min_bars:
                breaks.append(start)
                state = new_state
                break_added = True
                break

        if (not break_added) and (
            not soft_touches or peak - soft_touches[-1] > config.strategy.min_gap_soft_touches
        ):
            soft_touches.append(peak)

        i = j

    return ScoredLine(
        line=line.line,
        touches=line.touches,
        breaks=breaks,
        soft_touches=soft_touches,
        current_state=state,
    )
