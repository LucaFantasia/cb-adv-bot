from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Side = Literal["BUY", "SELL"]


@dataclass(frozen=True)
class Signal:
    side: Side
    price: float
    reason: str
    ref_line: int

    product_id: str
    candle_id: str
    quantity: float

    stop_loss: float | None = None
    take_profit: float | None = None
