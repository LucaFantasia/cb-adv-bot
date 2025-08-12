"""
backtest_config.py - Backtest execution time settings

Controls when the backtest starts and how far
back candles should be loaded relative to the start.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta


@dataclass
class BacktestConfig:
    # Timestamp when backtest logic begins (first signal evaluation)
    current_time: datetime = field(default_factory=lambda: datetime.now(UTC) - timedelta(days=60))

    # Candle history depth needed to evaluate trend lines (must match candle config)
    candle_history_days: int = 7

    run_time_days: int = 45

    # Automatically computed base time = current_time - history
    base_time: datetime = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "base_time", self.current_time - timedelta(days=self.candle_history_days)
        )


backtest_config = BacktestConfig()
