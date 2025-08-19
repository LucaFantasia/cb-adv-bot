from __future__ import annotations

from datetime import UTC, datetime, timedelta

from settings.loader import get_config, init_config, set_backtest_base_time


def test_global_update_seen_by_independent_module_calls() -> None:
    init_config()
    # Simulate an arbitrary module reading config before the update
    before = get_config().backtest.base_time

    # Update base time
    target = datetime.now(UTC) - timedelta(days=2)
    set_backtest_base_time(target)

    # Simulate another independent module reading config *after* the update
    after = get_config().backtest.base_time
    assert after is not None
    assert before != after
    assert abs((after - target).total_seconds()) < 1.0
