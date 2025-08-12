"""
backtest_engine.py
"""

from datetime import datetime, timedelta
from typing import Any

from models.scored_line import ScoredLine
from settings.config import config
from strategy.line_evaluator import (
    calc_sell_price,
    default_exit_price,
    intersects_support_line,
)
from strategy.trade_logger import TradeLogger
from strategy.trade_state import TradeState
from utils.logger import logger


class BacktestEngine:
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
        self.logger = TradeLogger(product_id, start_window)

    def on_candle(self, candle: dict[str, Any]) -> None:
        if candle["close"] is None:
            return

        if not self.state.position_open:
            for support_line in self.support_lines:
                proj_price = support_line.line.project_price(candle["index"])
                if intersects_support_line(
                    candle["high"], candle["low"], proj_price, self.deviation_pct
                ):
                    self.state.open_position(candle["timestamp"], proj_price, support_line)
                    self.logger.record_trade(
                        "BUY", candle["timestamp"], proj_price, f"Support at @ {proj_price:.2f}"
                    )
                    logger.info(
                        f"[BUY - {self.product_id}] on {candle['timestamp']} estimated @ {proj_price:.2f} (support: {proj_price:.2f})"
                    )
                    return

            if candle["timestamp"] - self.logger.get_latest_trade_ts() >= timedelta(
                days=config.backtest.candle_history_days
            ):
                logger.info(f"[{self.product_id}] No activity, preparing for reanalysis...")
                self.trade_cycle_complete = True
                return

        elif self.state.buy_point:
            buy_price = self.state.buy_point[1]
            stop_price = buy_price * (1 - self.stop_loss_pct)
            if candle["low"] <= stop_price:
                self.state.close_position(candle["timestamp"], stop_price)
                pct_loss = ((stop_price - buy_price) / buy_price) * 100
                self.logger.append_return(pct_loss)
                self.logger.record_trade(
                    "SELL", candle["timestamp"], stop_price, f"STOP LOSS: {pct_loss:.2f}%"
                )
                logger.info(
                    f"[SELL - {self.product_id}] STOP on {candle['timestamp']} @ {stop_price:.2f}, loss: {pct_loss:.2f}%"
                )
                self.trade_cycle_complete = True
                return

            if len(self.resistance_lines) > 0:
                for resistance_line in self.resistance_lines:
                    proj_price = resistance_line.line.project_price(candle["index"])
                    sell_price = calc_sell_price(buy_price, proj_price)
                    if candle["high"] >= sell_price:
                        self.state.close_position(candle["timestamp"], sell_price, resistance_line)
                        pct_gain = ((sell_price - buy_price) / buy_price) * 100
                        self.logger.append_return(pct_gain)
                        self.logger.record_trade(
                            "SELL", candle["timestamp"], sell_price, f"PROFIT: {pct_gain:.2f}%"
                        )
                        logger.info(
                            f"[SELL - {self.product_id}] GAIN on {candle['timestamp']} @ {sell_price:.2f}, profit: {pct_gain:.2f}%"
                        )
                        self.trade_cycle_complete = True
                        return
            else:
                fallback_price = default_exit_price(buy_price, self.stop_loss_pct)
                if candle["high"] >= fallback_price:
                    self.state.close_position(candle["timestamp"], fallback_price)
                    pct_gain = ((fallback_price - buy_price) / buy_price) * 100
                    self.logger.append_return(pct_gain)
                    self.logger.record_trade(
                        "SELL", candle["timestamp"], fallback_price, f"PROFIT: {pct_gain:.2f}%"
                    )
                    logger.info(
                        f"[SELL - {self.product_id}] GAIN on {candle['timestamp']} @ {fallback_price}, profit: {pct_gain:.2f}%"
                    )
                    self.trade_cycle_complete = True
                    return

    def reset(self) -> None:
        self.state.reset()
        self.trade_cycle_complete = False

    def export_trades(self) -> None:
        self.logger.export_to_csv()

    def get_avg_return(self) -> float:
        return float(self.logger.get_avg_return())
