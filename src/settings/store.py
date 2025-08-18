from __future__ import annotations

from threading import RLock
from typing import Any

from settings.loader_utils import deep_merge, validate_config
from settings.models import Config


class ConfigStore:
    def __init__(self, initial: Config | None = None) -> None:
        self._lock = RLock()
        self._cfg: Config = initial or Config()

    def get(self) -> Config:
        return self._cfg

    def snapshot(self) -> Config:
        with self._lock:
            return self._cfg.model_copy(deep=True)

    def replace(self, cfg: Config) -> Config:
        with self._lock:
            self._cfg = cfg
            return self._cfg

    def update(self, patch: dict[str, Any]) -> Config:
        with self._lock:
            merged = deep_merge(self._cfg.model_dump(), patch)
            self._cfg = validate_config(merged)
            return self._cfg


store = ConfigStore()
