"""
scored_line_runner.py - Visualise the scored lines
"""

import sys
from datetime import UTC, datetime, timedelta

import matplotlib.pyplot as plt

from api.product import ProductClient
from data.analysis.trend_analysis import TrendAnalysis
from settings.config import config
from visuals.trend_line_plotter import plot_scored_lines


def main(product_id: str) -> None:
    show_plot = True
    save_plot = False

    client = ProductClient()
    trend_analysis = TrendAnalysis(client, product_id, datetime.now(UTC))
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


if __name__ == "__main__":
    try:
        product_id = sys.argv[1] if len(sys.argv) > 1 else "BTC-USD"
        main(product_id)
    except Exception:
        import traceback

        traceback.print_exc()
        input("Press ENTER to exit...")
