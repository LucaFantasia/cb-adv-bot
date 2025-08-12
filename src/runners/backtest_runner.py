"""
backtest_runner.py - Bactests the trading strategy of the bot
"""

from datetime import timedelta

import pandas as pd

from api.product import ProductClient
from data.analysis.trend_analysis import TrendAnalysis
from data.structure.candle_loader import candles_to_dataframe
from settings.config import config
from strategy.backtest_engine import BacktestEngine
from utils.logger import logger
from visuals.trade_plotter import plot_trade_cycle
from visuals.trend_line_plotter import plot_scored_lines


def main() -> None:
    for product_id in ["BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD"]:
        avg_return = backtest(product_id)
        print(f"\n{product_id} average return: {avg_return}\n")
        config.backtest.base_time = config.backtest.current_time - timedelta(
            days=config.backtest.candle_history_days
        )


def backtest(product_id: str) -> float:
    client = ProductClient()
    trend_analysis = TrendAnalysis(client, product_id, config.backtest.current_time)
    trend_analysis.run()
    trade_count = 1
    plot_metadata = {"save": True, "show": False, "trade_count": 1, "product_id": product_id}
    plot_scored_lines(trend_analysis.df, trend_analysis.best_lines, plot_metadata)
    engine = BacktestEngine(
        product_id,
        trend_analysis.best_lines,
        trend_analysis.avg_volatility_pct / 2,
        trend_analysis.deviation_pct,
        config.backtest.base_time,
    )

    initial_df = trend_analysis.df
    live_df = candles_to_dataframe(
        client.get_historic_candles(
            product_id,
            trend_analysis.current_time,
            trend_analysis.current_time + timedelta(days=config.backtest.run_time_days),
            config.candle.granularity_mins,
            config.candle.granularity_str,
        )
    )
    full_df = pd.concat([initial_df, live_df])
    full_df = full_df[~full_df.index.duplicated(keep="last")]
    full_df.sort_index(inplace=True)

    for i in range(len(live_df)):
        if engine.trade_cycle_complete:
            logger.info(f"[{product_id}] Refreshing market analysis after trade cycle...")
            if engine.state.buy_point and engine.state.sell_point:
                plot_metadata = {
                    "product_id": product_id,
                    "buy_point": engine.state.buy_point,
                    "sell_point": engine.state.sell_point,
                    "start_window": engine.logger.start_window,
                    "end_window": live_df.index[i],
                    "trade_count": trade_count,
                }
                plot_trade_cycle(
                    full_df, engine.state.support_line, engine.state.resistance_line, plot_metadata
                )
            trade_count += 1
            trend_analysis.current_time = live_df.index[i]
            trend_analysis.run()
            plot_metadata = {
                "save": True,
                "show": False,
                "trade_count": trade_count,
                "product_id": product_id,
            }
            plot_scored_lines(
                trend_analysis.df,
                trend_analysis.best_support_lines + trend_analysis.best_resistance_lines,
                plot_metadata,
            )
            engine.reset()
            engine.support_lines = trend_analysis.best_support_lines
            engine.resistance_lines = trend_analysis.best_resistance_lines
            engine.stop_loss_pct = trend_analysis.avg_volatility_pct / 2
            engine.deviation_pct = trend_analysis.deviation_pct
            engine.logger.start_window = trend_analysis.current_time - timedelta(
                days=config.candle.candle_history_days
            )
            config.backtest.base_time = trend_analysis.current_time - timedelta(
                days=config.candle.candle_history_days
            )

        candle = {
            "timestamp": live_df.index[i],
            "index": int(
                (live_df.index[i] - config.backtest.base_time).total_seconds()
                / (60 * config.candle.granularity_mins)
            ),
            "low": live_df["Low"].iloc[i],
            "high": live_df["High"].iloc[i],
            "open": live_df["Open"].iloc[i],
            "close": live_df["Close"].iloc[i],
        }

        engine.on_candle(candle)

    engine.export_trades()

    return float(engine.get_avg_return())


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback

        traceback.print_exc()
        input("Press ENTER to exit...")
