"""
main_engine.py
"""

from datetime import datetime
from typing import Any

from models.scored_line import ScoredLine
from strategy.line_evaluator import calc_sell_price, default_exit_price, is_near_line
from strategy.trade_logger import TradeLogger
from strategy.trade_state import TradeState
from utils.logging_config import get_logger


class MainEngine:
    def __init__(
        self,
        product_id: str,
        best_lines: list[ScoredLine],
        stop_loss_pct: float,
        deviation_pct: float,
        start_window: datetime,
    ) -> None:
        self.product_id = product_id
        self.support_lines = [line for line in best_lines if line.current_state == "support"]
        self.resistance_lines = [line for line in best_lines if line.current_state == "resistance"]
        self.stop_loss_pct = stop_loss_pct
        self.deviation_pct = deviation_pct
        self.trade_cycle_complete = False
        self.state = TradeState()
        self.trade_logger = TradeLogger(product_id, start_window)
        self.logger = get_logger(__name__)

    def on_candle(self, candle: dict[str, Any]) -> None:
        if candle["close"] is None:
            return

        if not self.state.position_open:
            for support_line in self.support_lines:
                proj_price = support_line.line.project_price(candle["index"])
                if is_near_line(candle["low"], proj_price, self.deviation_pct):
                    self.state.open_position(candle["timestamp"], candle["low"], support_line)
                    self.trade_logger.record_trade(
                        "BUY", candle["timestamp"], candle["low"], f"Support at @ {proj_price:.2f}"
                    )
                    self.logger.info(
                        "BUY signal",
                        extra={
                            "product_id": self.product_id,
                            "signal": "line_breakout",
                            "timestamp": candle["timestamp"],
                            "price": candle["low"],
                        },
                    )
                    return
        elif self.state.buy_point:
            buy_price = self.state.buy_point[1]
            stop_price = buy_price * (1 - self.stop_loss_pct)
            if candle["low"] <= stop_price:
                self.state.close_position(candle["timestamp"], candle["low"])
                pct_loss = ((candle["low"] - buy_price) / buy_price) * 100
                self.trade_logger.record_trade(
                    "SELL", candle["timestamp"], candle["low"], f"STOP LOSS: {pct_loss:.2f}%"
                )
                self.logger.info(
                    "SELL signal",
                    extra={
                        "product_id": self.product_id,
                        "signal": "stop_loss",
                        "timestamp": candle["timestamp"],
                        "price": candle["low"],
                        "pct_loss": pct_loss,
                    },
                )
                self.state.reset()
                return

            if len(self.resistance_lines) > 0:
                for resistance_line in self.resistance_lines:
                    proj_price = resistance_line.line.project_price(candle["index"])
                    sell_price = calc_sell_price(buy_price, proj_price)
                    if candle["high"] >= sell_price:
                        self.state.close_position(
                            candle["timestamp"], candle["high"], resistance_line
                        )
                        pct_gain = ((candle["high"] - buy_price) / buy_price) * 100
                        self.trade_logger.record_trade(
                            "SELL", candle["timestamp"], candle["high"], f"PROFIT: {pct_gain:.2f}%"
                        )
                        self.logger.info(
                            "SELL signal",
                            extra={
                                "product_id": self.product_id,
                                "signal": "line_breakout",
                                "timestamp": candle["timestamp"],
                                "price": candle["high"],
                                "pct_gain": pct_gain,
                            },
                        )
                        self.state.reset()
                        return
            else:
                fallback_price = default_exit_price(buy_price, self.stop_loss_pct)
                if candle["high"] >= fallback_price:
                    self.state.close_position(candle["timestamp"], candle["high"])
                    pct_gain = ((candle["high"] - buy_price) / buy_price) * 100
                    self.trade_logger.record_trade(
                        "SELL", candle["timestamp"], candle["high"], f"PROFIT: {pct_gain:.2f}%"
                    )
                    self.logger.info(
                        "SELL signal",
                        extra={
                            "product_id": self.product_id,
                            "signal": "line_breakout",
                            "timestamp": candle["timestamp"],
                            "price": candle["high"],
                            "pct_gain": pct_gain,
                        },
                    )
                    self.state.reset()
                    return

    def export_trades(self) -> None:
        self.trade_logger.export_to_csv()
