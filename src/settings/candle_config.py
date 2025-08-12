"""
candle_config.py - Candle aggregation settings

Defines granularity and how much historical data
should be pulled or generated for analysis.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CandleConfig:
    # Resolution of each candle (used in REST + aggregator)
    granularity_str: str = "FIFTEEN_MINUTE"

    # Granularity in minutes, used for candle index calculation
    granularity_mins: int = 15

    # How many days of candles to preload before trade cycle
    candle_history_days: int = 7


candle_config = CandleConfig()
