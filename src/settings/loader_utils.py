from __future__ import annotations

from typing import Any

from pydantic import TypeAdapter

from settings.models import Config


def deep_merge(base: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for key, value in patch.items():
        if key in out and isinstance(out[key], dict) and isinstance(value, dict):
            out[key] = deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def validate_config(payload: dict[str, Any]) -> Config:
    return TypeAdapter(Config).validate_python(payload)
