from __future__ import annotations

import json
from typing import TYPE_CHECKING

from src.settings.loader import get_config, init_config, update_config

if TYPE_CHECKING:
    from pathlib import Path


def test_json_file_merged_over_defaults(tmp_path: Path) -> None:
    deviation_factor = 35.5
    candle_history_days = 10

    override = {
        "strategy": {"deviation_factor": deviation_factor},
        "backtest": {"candle_history_days": candle_history_days},
    }
    p = tmp_path / "config.override.json"
    p.write_text(json.dumps(override), encoding="utf-8")

    init_config(json_path=str(p))
    cfg = get_config()
    assert cfg.strategy.deviation_factor == deviation_factor
    assert cfg.backtest.candle_history_days == candle_history_days


def test_runtime_update_preserves_other_sections() -> None:
    num_of_top_lines = 3

    init_config()
    before = get_config().model_copy(deep=True)

    update_config({"strategy": {"num_of_top_lines": num_of_top_lines}})
    cfg = get_config()

    assert cfg.strategy.num_of_top_lines == num_of_top_lines
    # unchanged section remains identical
    assert cfg.candle == before.candle
