"""
scored_line_runner.py - Visualise the scored lines
"""

from datetime import UTC, datetime, timedelta

import matplotlib.pyplot as plt

from container import build_services
from data.analysis.trend_analysis import TrendAnalysis
from settings.loader import get_config
from visuals.trend_line_plotter import plot_scored_lines


def main(product_id: str, show_plot: bool, save_plot: bool) -> None:
    config = get_config()
    services = build_services()
    trend_analysis = TrendAnalysis(services, product_id, datetime.now(UTC))
    trend_analysis.run()

    raw_support_lines = [line for line in trend_analysis.raw_lines if line.state == "support"]
    raw_resistance_lines = [line for line in trend_analysis.raw_lines if line.state == "resistance"]
    support_lines = [
        line for line in trend_analysis.scored_lines if line.current_state == "support"
    ]
    resistance_lines = [
        line for line in trend_analysis.scored_lines if line.current_state == "resistance"
    ]

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
    print(f"\nNUMBER OF RAW SUPPORT LINES: {len(raw_support_lines)}\n")
    print(f"\nNUMBER OF RAW RESISTANCE LINES: {len(raw_resistance_lines)}\n")
    print(f"\nNUMBER OF SCORED LINES: {len(trend_analysis.scored_lines)}\n")
    print(f"\nNUMBER OF SUPPORT LINES: {len(support_lines)}\n")
    print(f"\nNUMBER OF RESISTANCE LINES: {len(resistance_lines)}\n")
    print(f"\nSCORED LINES: {trend_analysis.scored_lines}\n")

    plot_metadata = {
        "save": save_plot,
        "show": show_plot,
        "trade_count": None,
        "product_id": product_id,
    }
    plot_scored_lines(trend_analysis.df, trend_analysis.scored_lines, plot_metadata)

    if show_plot:
        plt.show()
