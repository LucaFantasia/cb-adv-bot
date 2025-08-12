"""
trend_line.py Data structure for trend lines

Represents a line drawn between two extrema points on a price chart.
Used to model support and resistance levels, later scored for signal strength.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class TrendLine:
    """
    Represents a linear support or resistance level defined by slope and intercept.

    Attributes:
        slope: The line's slope (Δprice / Δcandle index)
        intercept: The Y-axis intercept relative to candle index zero
        state: Either 'support' or 'resistance'
        start_index: Index (relative to first candle) of first extremum
        end_index: Index of second extremum
    """

    slope: float
    intercept: float
    state: str
    start_index: int
    end_index: int

    def project_price(self, candle_idx: int) -> float:
        """
        Projects the price on this trend line at a given candle index.

        Args:
            candle_idx: Float index relative to first candle in analysis window.

        Returns:
            Projected price as float
        """
        return self.slope * candle_idx + self.intercept
