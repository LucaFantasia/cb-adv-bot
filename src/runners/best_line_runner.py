"""
best_line_runner.py - Visualise the best scored lines
"""

from datetime import datetime, timedelta

import matplotlib.pyplot as plt

from container import build_services
from data.analysis.trend_analysis import TrendAnalysis
from settings.loader import get_config
from visuals.line_strength_plotter import (
    plot_line_score_components,
    plot_line_scoring_detections,
)


def main(product_id: str, current_time: datetime | None, show_plot: bool, save_plot: bool) -> None:
    config = get_config()
    services = build_services()
    trend_analysis = TrendAnalysis(services, product_id, current_time)
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
    print(f"\nNUMBER OF BEST SUPPORT LINES: {len(trend_analysis.best_support_lines)}\n")
    print(f"\nBEST SUPPORT LINES: {trend_analysis.best_support_lines}\n")
    print(f"\nNUMBER OF BEST RESISTANCE LINES: {len(trend_analysis.best_resistance_lines)}\n")
    print(f"\nBEST RESISTANCE LINES: {trend_analysis.best_resistance_lines}\n")

    for i, line in enumerate(trend_analysis.best_support_lines, 1):
        plot_line_score_components(line, i, save_plot, show_plot, product_id)
        plot_metadata = {
            "save": save_plot,
            "show": show_plot,
            "line_number": i,
            "product_id": product_id,
        }
        plot_line_scoring_detections(trend_analysis.df, line, plot_metadata)
    for i, line in enumerate(trend_analysis.best_resistance_lines, 1):
        plot_line_score_components(line, i, save_plot, show_plot, product_id)
        plot_metadata = {
            "save": save_plot,
            "show": show_plot,
            "line_number": i,
            "product_id": product_id,
        }
        plot_line_scoring_detections(trend_analysis.df, line, plot_metadata)

    if show_plot:
        plt.show()
