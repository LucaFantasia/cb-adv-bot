from __future__ import annotations

from datetime import UTC, datetime, timedelta

from src.settings.loader import (
    get_config,
    init_config,
    set_backtest_base_time,
    update_config,
)


def test_init_config_defaults_roundtrip() -> None:
    max_candles_per_call = 350

    cfg = init_config()
    assert cfg.candle.granularity_str == "FIFTEEN_MINUTE"
    assert cfg.candle.max_candles_per_call == max_candles_per_call
    assert cfg.backtest.base_time is not None

    cfg_2 = get_config()
    assert cfg_2 is cfg


def test_update_config_deep_merge_and_validation() -> None:
    granularity_mins = 60
    num_of_top_lines = 2

    init_config()
    update_config({"candle": {"granularity_str": "ONE_HOUR", "granularity_mins": granularity_mins}})
    cfg = get_config()
    assert cfg.candle.granularity_str == "ONE_HOUR"
    assert cfg.candle.granularity_mins == granularity_mins

    assert cfg.strategy.num_of_top_lines == num_of_top_lines


def test_set_backtest_base_time_global_visibility() -> None:
    init_config()
    now = datetime.now(UTC)
    dt = now - timedelta(days=3)

    set_backtest_base_time(dt)
    # Any module calling get_config() should now see the updated time
    seen = get_config().backtest.base_time
    assert seen is not None
    # Allow a small delta since some impls round micros
    assert abs((seen - dt).total_seconds()) < 1.0
