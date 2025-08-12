"""
line_scoring.py — Decay-based scoring of trend lines

Computes a score for each ScoredLine based on:
- Section-weighted touches, soft touches, and breaks
- Temporal spread and clustering
- Recency decay and steepness
- Price-space compactness

Used to rank and select the most reliable trend lines.
"""

import math

import numpy as np

from models.scored_line import ScoredLine
from settings.config import config


def _get_section(index: int, q1: int, q2: int, q3: int) -> int:
    if index <= q1:
        return 0
    elif index <= q2:
        return 1
    elif index <= q3:
        return 2
    else:
        return 3


def _section_decay_score(
    indices: list[int], values: list[float], q1: int, q2: int, q3: int
) -> float:
    return sum(values[_get_section(idx, q1, q2, q3)] for idx in indices)


def _spread_bonus(touches: list[int], num_candles: int) -> float:
    return float(
        5.0
        * (
            ((max(touches) - min(touches)) / num_candles)
            if len(touches) >= config.strategy.min_touches_scoring
            else 0.0
        )
    )


def _clustering_penalty(touches: list[int]) -> float:
    if len(touches) < config.strategy.min_touches_scoring:
        return 0.0
    return -(float(np.sum(np.diff(touches) < config.strategy.cluster_penalty_distance)))


def _recent_event_penalty(indices: list[int], num_candles: int) -> float:
    arr = np.asarray(indices)
    return float(-5.0 * np.sum(arr >= (num_candles - 5)))


def _break_recency_decay(breaks: list[int], num_candles: int) -> float:
    if not breaks:
        return 0.0
    arr = np.asarray(breaks)
    return float(-2.0 * np.sum(1 - ((num_candles - arr) / num_candles)))


def _steepness_penalty(slope: float) -> float:
    degrees = abs(math.degrees(math.atan(slope)))
    return float(-1.0 if degrees > config.strategy.steepness_penalty_deg else 0.0)


def score_line(line: ScoredLine, q1: int, q2: int, q3: int, num_candles: int) -> None:
    """
    Computes a decay-aware trend line score using touch, break, and spread metrics.

    Args:
        line: ScoredLine instance
        df: Price data used to analyze touch price span
        avg_volatility_pct: Volatility of price as a percentage

    Returns:
        A float score indicating line quality
    """
    touches = line.touches
    soft_touches = line.soft_touches
    breaks = line.breaks
    slope = line.line.slope
    components = {}

    components["touch_score"] = _section_decay_score(touches, [1.0, 0.5, 0.25, 0.125], q1, q2, q3)
    components["soft_touch_score"] = _section_decay_score(
        soft_touches, [0.1, 0.05, 0.025, 0.0125], q1, q2, q3
    )
    components["break_penalty"] = _section_decay_score(breaks, [-0.5, -1.0, -2.0, -4.0], q1, q2, q3)
    components["spread_bonus"] = _spread_bonus(touches, num_candles)
    components["clustering_penalty"] = _clustering_penalty(touches)
    components["recent_penalty"] = _recent_event_penalty(
        touches + soft_touches + breaks, num_candles
    )
    components["break_decay"] = _break_recency_decay(breaks, num_candles)
    components["steepness_penalty"] = _steepness_penalty(slope)

    score = sum(components.values())
    line.score = score
    line.score_components = components
