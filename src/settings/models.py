from __future__ import annotations

from datetime import UTC, datetime, timedelta

from pydantic import BaseModel, Field


class CandleConfig(BaseModel):
    granularity_str: str = "FIFTEEN_MINUTE"
    granularity_mins: int = 15
    candle_history_days: int = 7


class StrategyConfig(BaseModel):
    extrema_window_size: int = 7
    duration_in_candles: int = 30
    break_criteria: list[tuple[float, int]] = Field(
        default_factory=lambda: [(5.0, 1), (4.0, 5), (3.0, 10)]
    )
    num_of_top_lines: int = 2
    deviation_factor: int = 40
    min_gap_soft_touches: int = 5
    min_touches_scoring: int = 2
    cluster_penalty_distance: int = 50
    steepness_penalty_deg: int = 60


class BacktestConfig(BaseModel):
    current_time: datetime = Field(default_factory=lambda: datetime.now(UTC) - timedelta(days=60))
    candle_history_days: int = 7
    run_time: int = 45
    product_ids: list[str] = ["BTC-USD", "ETH-USD", "XRP-USD", "SOL-USD"]
    base_time: datetime = Field(default=current_time - timedelta(days=candle_history_days))


class Config(BaseModel):
    candle: CandleConfig = CandleConfig()
    strategy: StrategyConfig = StrategyConfig()
    backtest: BacktestConfig = BacktestConfig()
