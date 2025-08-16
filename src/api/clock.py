from __future__ import annotations

import time

from .ports import Clock


class SystemClock(Clock):
    # Thin wrapper over stdlib time
    def now(self) -> float:
        return time.time()

    def monotonic(self) -> float:
        return time.monotonic()
