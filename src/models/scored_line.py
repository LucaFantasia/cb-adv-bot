"""
scored_line.py - Stores a trend line and its detection metrics
"""

from dataclasses import dataclass, field

from models.trend_line import TrendLine


@dataclass
class ScoredLine:
    """
    Contains a trend line and its associated analysis results.

    Attributes:
        line: The original TrendLine object
        touches: List of candle indices where this line touches price
        breaks: List of candle indices where this line breaks
        soft_touches: List of candle indices where this line almost breaks
        current_state: Whether the line is support or resistance at the current time
    """

    line: TrendLine
    touches: list[int]
    breaks: list[int] = []
    soft_touches: list[int] = []
    current_state: str = ""
    score: float = 0.0
    score_components: dict[str, float] = field(default_factory=dict)
