"""
strategy_config.py - Strategy behavior configuration

Holds core parameters that control:
- Line detection and evaluation
- Break criteria and durations
- Deviation settings for volatility
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class StrategyConfig:
    # Window size used when detecting local extrema
    extrema_window_size: int = 7

    # Maximum trend line slope steepness in degrees
    max_slope_deg: float = 70

    # Duration (in candles) for which lines must hold to be considered valid
    duration_in_candles: int = 30

    # Criteria for accepting a breakout: (threshold, required touches)
    break_criteria: list[tuple[float, int]] = field(
        default_factory=lambda: [(5.0, 1), (4.0, 5), (3.0, 10)]
    )

    # Number of top-scoring lines to keep for each trend direction
    num_of_top_lines: int = 2

    # Multiplier used in dynamic deviation band around support/resistance
    deviation_factor: float = 40.0

    # Minimum gap between soft touches
    min_gap_soft_touches = 5

    # Minimum amount of touches needed for scoring
    min_touches_scoring = 2

    # Minimum candle distance between touches to get clustering penalty
    cluster_penalty_distance = 50

    # Steepness penalty if greater than this degrees
    steepness_penalty_deg = 60


strategy_config = StrategyConfig()
