"""
break_detector.py - Detects breaks through trend lines

Detects breakouts based on deviation strength and recovery duration.
"""

import numpy as np

from models.scored_line import ScoredLine
from settings.loader import get_config


def detect_breaks_for_line(
    line: ScoredLine,
    num_candles: int,
    closes: list[float],
    deviation_price: float,
    proj_prices: np.ndarray,
) -> ScoredLine:
    """
    Evaluates a single trend line for break points and soft touches.


    Vectorised over segments (runs) to reduce per-candle Python work while
    preserving the original semantics:
    - A break candidate starts when price crosses through the line given the current state.
    - The run continues until price recovers to the opposite side of the line.
    - For the run, compute max_height (peak thrust) and duration; validate
    against (factor * deviation_price, min_bars) criteria.
    - If validated, record a break at the run start and flip state.
    - Otherwise, record a soft-touch at the peak (declustered by min_gap_soft_touches).
    """
    config = get_config()

    # Make contiguous arrays for performance
    closes_vect = np.asarray(closes, dtype=np.float32)
    proj_prices_vect = np.asarray(proj_prices, dtype=np.float32)

    # Precompute directional masks
    below = closes_vect < proj_prices_vect
    above = closes_vect > proj_prices_vect

    state = line.line.state
    breaks: list[int] = []
    soft_touches: list[int] = []

    i = 0
    while i < num_candles:
        if state == "support":
            # next index where price is below the line (down-break candidate)
            rel = np.nonzero(below[i:])[0]
            if rel.size == 0:
                break
            start = i + int(rel[0])

            # run ends at first index where price goes above the line (recovery)
            rel_rec = np.nonzero(above[start:])[0]
            j = start + int(rel_rec[0]) if rel_rec.size else num_candles

            # thrust distance during run (positive for downward thrust)
            run_dist = proj_prices_vect[start:j] - closes_vect[start:j]

        else:  # state == "resistance"
            # next index where price is above the line (up-break candidate)
            rel = np.nonzero(above[i:])[0]
            if rel.size == 0:
                break
            start = i + int(rel[0])

            # run ends at first index where price goes below the line (recovery)
            rel_rec = np.nonzero(below[start:])[0]
            j = start + int(rel_rec[0]) if rel_rec.size else num_candles

            # thrust distance during run (positive for upward thrust)
            run_dist = closes_vect[start:j] - proj_prices_vect[start:j]

        # Compute metrics for this run
        if run_dist.size == 0:
            i = start + 1
            continue

        # duration and peak
        duration = int(j - start)
        argmax = int(np.argmax(run_dist))
        max_height = float(run_dist[argmax])
        peak = start + argmax

        # validate against break criteria (first satisfied)
        break_added = False
        for factor, min_bars in config.strategy.break_criteria:
            if (max_height >= factor * deviation_price) and (duration >= min_bars):
                breaks.append(start)
                # flip state only on actual break
                state = "resistance" if state == "support" else "support"
                break_added = True
                break

        # soft-touch bookkeeping when no break added
        if (not break_added) and (
            not soft_touches
            or (peak - soft_touches[-1]) > int(config.strategy.min_gap_soft_touches)
        ):
            soft_touches.append(peak)

        # jump to end of the run (recovery point)
        i = j

    return ScoredLine(
        line=line.line,
        touches=line.touches,
        breaks=breaks,
        soft_touches=soft_touches,
        current_state=state,
    )
