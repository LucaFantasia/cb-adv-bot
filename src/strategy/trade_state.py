"""
trade_state.py
"""

from datetime import datetime

from models.scored_line import ScoredLine


class TradeState:
    def __init__(self) -> None:
        self.position_open: bool = False
        self.buy_point: tuple[datetime, float] | None = None
        self.sell_point: tuple[datetime, float] | None = None
        self.support_line: ScoredLine | None = None
        self.resistance_line: ScoredLine | None = None

    def open_position(self, ts: datetime, price: float, support_line: ScoredLine) -> None:
        self.position_open = True
        self.buy_point = (ts, price)
        self.support_line = support_line

    def close_position(
        self, ts: datetime, price: float, resistance_line: ScoredLine | None = None
    ) -> None:
        self.position_open = False
        self.sell_point = (ts, price)
        self.resistance_line = resistance_line

    def reset(self) -> None:
        self.buy_point = None
        self.sell_point = None
        self.support_line = None
        self.resistance_line = None
