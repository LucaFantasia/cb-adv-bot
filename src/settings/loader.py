from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import TypeAdapter

from .models import Config


def _deep_update(base: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    """Minimal recursive dict merge (values in `patch` win)."""
    for key, value in patch.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            base[key] = _deep_update(base[key], value)
        else:
            base[key] = value
    return base


def _config_to_dict(config: Config) -> dict[str, Any]:
    """Export Pydantic model to plain dict for merging."""
    return config.model_dump()


def _load_json_file(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    oPath = Path(path)
    if not oPath.exists():
        return {}
    with oPath.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("Config JSON must be an object at the root.")
    return data


def _validate_config(payload: dict[str, Any]) -> Config:
    """Validate merged dict using Pydantic (strict typing)."""
    adapter = TypeAdapter(Config)
    return adapter.validate_python(payload)


@lru_cache(maxsize=1)
def get_config(*, json_path: str | None = None, overrides: dict[str, Any] | None = None) -> Config:
    """
    Returns a cached Config.

    Merge order (later wins):
      1) defaults (from models)
      2) JSON file (if provided)
      3) ad-hoc overrides (dict; useful in tests)
    """
    base = _config_to_dict(Config())
    json_patch = _load_json_file(json_path) if json_path else {}
    user_patch = overrides or {}

    merged: dict[str, Any] = {}
    _deep_update(merged, base)
    _deep_update(merged, json_patch)
    _deep_update(merged, user_patch)

    return _validate_config(merged)


def reset_config_cache() -> None:
    """Clear the cached config (useful in tests to re-evaluate overrides)."""
    get_config.cache_clear()
