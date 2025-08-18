"""
metrics_runner.py - Visuals metrics on candle chart
"""

from datetime import UTC, datetime, timedelta

import matplotlib.pyplot as plt

from container import build_services
from data.analysis.trend_analysis import TrendAnalysis
from settings.loader import get_config
from visuals.overlays_plotter import plot_trend_line_overlays


def main(product_id: str, show_plot: bool, save_plot: bool) -> None:
    config = get_config()
    services = build_services()
    trend_analysis = TrendAnalysis(services, product_id, datetime.now(UTC))
    trend_analysis.run()

    deviation_pct = trend_analysis.avg_volatility_pct / config.strategy.deviation_factor
    deviation_price = (trend_analysis.df["Close"].iloc[-1]) * deviation_pct

    print(f"\nEND TIME: {trend_analysis.current_time}\n")
    print(
        f"\nSTART TIME: {trend_analysis.current_time - timedelta(days=config.candle.candle_history_days)}\n"
    )
    print(f"\nDELTA TIME: {config.candle.candle_history_days} days\n")
    print(f"\nNUMBER OF CANDLES: {len(trend_analysis.candles)}\n")
    print(f"\nDATAFRAME SIZE: {len(trend_analysis.df)}\n")
    print(f"\nNUMBER OF MAXIMAS: {len(trend_analysis.maximas)}\n")
    print(f"\nNUMBER OF MINIMAS: {len(trend_analysis.minimas)}\n")
    print(f"\nNUMBER OF RAW TREND LINES: {len(trend_analysis.raw_lines)}\n")
    print(f"\nNUMBER OF BEST SUPPORT LINES: {len(trend_analysis.best_support_lines)}\n")
    print(f"\nNUMBER OF BEST RESISTANCE LINES: {len(trend_analysis.best_resistance_lines)}\n")
    print(f"\nAVERAGE VOLATILITY PERCENTAGE: {trend_analysis.avg_volatility_pct}\n")
    print(f"\nDEVIATION PERCENTAGE: {deviation_pct}\n")
    print(f"\nDEVIATION_PRICE: {deviation_price}\n")

    for i, line in enumerate(trend_analysis.best_support_lines, 1):
        plot_metadata = {
            "save": save_plot,
            "show": show_plot,
            "line_number": i,
            "product_id": product_id,
        }
        plot_trend_line_overlays(
            trend_analysis.df,
            line,
            trend_analysis.avg_volatility_pct,
            deviation_price,
            plot_metadata,
        )
    for i, line in enumerate(trend_analysis.best_resistance_lines, 1):
        plot_metadata = {
            "save": save_plot,
            "show": show_plot,
            "line_number": i,
            "product_id": product_id,
        }
        plot_trend_line_overlays(
            trend_analysis.df,
            line,
            trend_analysis.avg_volatility_pct,
            deviation_price,
            plot_metadata,
        )

    if show_plot:
        plt.show()
