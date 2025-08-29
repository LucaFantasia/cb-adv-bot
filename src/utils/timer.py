import logging
import time
from dataclasses import dataclass
from typing import Any

log = logging.getLogger(__name__)


@dataclass
class Timer:
    name: str

    def __enter__(self) -> "Timer":
        self.t0 = time.perf_counter_ns()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.dt_ns = time.perf_counter_ns() - self.t0
        log.info(f"{self.name} took {self.dt_ns / 1e6:.2f} ms")
