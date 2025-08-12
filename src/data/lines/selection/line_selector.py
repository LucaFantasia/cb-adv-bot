"""
line_selector.py — Best line filtering and selection logic

This module handles:
- Filtering spatially distinct trend lines
- Scoring and selecting the best support/resistance lines
- Applying volatility-based spacing filters for resistance lines
"""

from models.scored_line import ScoredLine


def _are_lines_similar(
    line_1: ScoredLine, line_2: ScoredLine, last_index: int, deviation_pct: float
) -> bool:
    """
    Compares two lines to determine if they are too close across key index positions.

    Args:
        line_1: First trend line
        line_2: Second trend line
        last_index: Index of the last candle
        deviation_pct: Allowed deviation as a percentage of price

    Returns:
        True if the lines are similar (within deviation), False otherwise.
    """
    for frac in [0.00, 0.25, 0.50, 0.75, 1.00]:
        idx = int(frac * last_index)
        price_1 = line_1.line.slope * idx + line_1.line.intercept
        price_2 = line_2.line.slope * idx + line_2.line.intercept
        if abs(price_1 - price_2) / price_1 > 5 * deviation_pct:
            return False
    return True


def filter_resistance_lines(
    resistance_lines: list[ScoredLine],
    support_lines: list[ScoredLine],
    last_index: int,
    avg_volatility_pct: float,
) -> list[ScoredLine]:
    """
    Filters resistance lines to those reasonably spaced from the strongest support line.

    Args:
        resistance_lines: Candidate resistance lines
        support_lines: Pre-selected support lines
        last_index: Candle index to project price to
        avg_volatility_pct: Baseline volatility for filtering

    Returns:
        Filtered list of resistance lines that are not too close to support levels.
    """
    if not support_lines:
        return []

    max_support_price = max(line.line.project_price(last_index) for line in support_lines)

    return [
        line
        for line in resistance_lines
        if 1.0 * avg_volatility_pct
        <= abs(line.line.project_price(last_index) - max_support_price) / max_support_price
        <= 1.5 * avg_volatility_pct
    ]


def select_top_lines(
    lines: list[ScoredLine], last_index: int, deviation_pct: float, max_lines: int
) -> list[ScoredLine]:
    """
    Selects the highest scoring spatially distinct trend lines.

    Args:
        lines: List of ScoredLine objects
        last_index: Index to evaluate projections at
        deviation_pct: Threshold for distinctiveness
        max_lines: Maximum number of lines to select

    Returns:
        List of distinct, high-scoring trend lines
    """
    sorted_lines = sorted(lines, key=lambda line: line.score, reverse=True)

    selected: list[ScoredLine] = []
    for candidate in sorted_lines:
        if not any(
            _are_lines_similar(candidate, other, last_index, deviation_pct) for other in selected
        ):
            selected.append(candidate)
        if len(selected) >= max_lines:
            break
    return selected
