"""
trend_analysis.py - Full market trend detection and evaluation pipeline

Performs:
- Historical candle loading
- Extremum detection
- Trend line generation
- Touch/break detection
- Decay-based scoring

Returns the best support/resistance lines for trade decisions.
"""

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from container import Services
from data.extrema.extrema_detector import find_local_extrema
from data.lines.creation.trend_lines import generate_trend_lines
from data.lines.detection.break_detector import detect_breaks_for_line
from data.lines.detection.touch_detector import detect_touches_for_line
from data.lines.scoring.line_scoring import score_line
from data.lines.selection.line_selector import filter_resistance_lines, select_top_lines
from data.structure.candle_loader import (
    candles_to_dataframe,
    compute_avg_volatility_pct,
)
from settings.loader import get_config

if TYPE_CHECKING:
    from api.product_models import Candle
    from models.scored_line import ScoredLine
    from models.trend_line import TrendLine


class TrendAnalysis:
    """
    Centralized engine for extracting high-confidence trend lines from historical OHLCV data.
    """

    def __init__(self, services: Services, product_id: str, current_time: datetime | None = None):
        self.config = get_config()
        self.services = services
        self.product_id = product_id
        self.current_time = current_time or datetime.now(UTC)

        self.candles: list[Candle] = []
        self.df: pd.DataFrame = pd.DataFrame()
        self.avg_volatility_pct: float = 0.0
        self.deviation_pct: float = 0.0
        self.maximas: list[tuple[str, float, int]] = []
        self.minimas: list[tuple[str, float, int]] = []
        self.raw_lines: list[TrendLine] = []
        self.scored_lines: list[ScoredLine] = []
        self.best_support_lines: list[ScoredLine] = []
        self.best_resistance_lines: list[ScoredLine] = []
        self.best_lines: list[ScoredLine] = []

    def run(self) -> None:
        """
        Executes the full analysis pipeline and populates scored_lines.
        """
        self.candles = self.services.product_api.get_historic_candles(
            self.product_id,
            self.current_time - timedelta(days=self.config.candle.candle_history_days),
            self.current_time,
            self.config.candle.granularity_mins,
            self.config.candle.granularity_str,
        )
        self.df = candles_to_dataframe(self.candles)
        self.avg_volatility_pct = compute_avg_volatility_pct(self.candles)
        self.deviation_pct = self.avg_volatility_pct / self.config.strategy.deviation_factor

        self.maximas, self.minimas = find_local_extrema(
            self.df, self.config.strategy.extrema_window_size
        )
        self.raw_lines = generate_trend_lines(
            self.maximas + self.minimas,
            self.df,
            self.config.strategy.max_slope_deg,
            self.config.strategy.duration_in_candles,
            4 * self.avg_volatility_pct,
        )

        candle_indices = np.arange(len(self.df))
        num_candles = len(self.df)
        q1 = int(num_candles * 0.25)
        q2 = int(num_candles * 0.50)
        q3 = int(num_candles * 0.75)
        closes = list((self.df["Close"].values).astype(float))
        extremas = sorted(self.maximas + self.minimas, key=lambda extrema: extrema[2])
        deviation_price = self.df["Close"].iloc[-1] * (self.deviation_pct)

        self.scored_lines = []
        for line in self.raw_lines:
            proj_prices = line.slope * candle_indices + line.intercept

            scored_line = detect_touches_for_line(
                line, proj_prices, extremas, deviation_price, self.df
            )
            updated_scored_line = detect_breaks_for_line(
                scored_line, num_candles, closes, deviation_price, proj_prices
            )
            score_line(updated_scored_line, q1, q2, q3, num_candles)
            self.scored_lines.append(updated_scored_line)

        support_lines = [line for line in self.scored_lines if line.current_state == "support"]
        resistance_lines = [
            line for line in self.scored_lines if line.current_state == "resistance"
        ]

        self.best_support_lines = select_top_lines(
            support_lines, num_candles, self.deviation_pct, self.config.strategy.num_of_top_lines
        )
        filtered_resistance_lines = filter_resistance_lines(
            resistance_lines, support_lines, num_candles, self.avg_volatility_pct
        )
        self.best_resistance_lines = select_top_lines(
            filtered_resistance_lines,
            num_candles,
            self.deviation_pct,
            self.config.strategy.num_of_top_lines,
        )
        self.best_lines = self.best_support_lines + self.best_resistance_lines
