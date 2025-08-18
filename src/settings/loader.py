from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from settings.loader_utils import deep_merge, validate_config
from settings.models import Config
from settings.store import store

if TYPE_CHECKING:
    from datetime import datetime


def _load_json(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    p = Path(path)
    if not p.exists():
        return {}
    data = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Config JSON must be an object at the root.")
    return data


def init_config(json_path: str | None = None, overrides: dict[str, Any] | None = None) -> Config:
    merged = deep_merge({}, Config().model_dump())
    merged = deep_merge(merged, _load_json(json_path))
    merged = deep_merge(merged, overrides or {})
    return store.replace(validate_config(merged))


def get_config() -> Config:
    return store.get()


def update_config(patch: dict[str, Any]) -> Config:
    return store.update(patch)


def set_backtest_base_time(time: datetime) -> Config:
    return update_config({"backtest": {"base_time": time}})
