"""
trend_line_runner.py - Visualise raw trend lines
"""

from datetime import UTC, datetime, timedelta

import matplotlib.pyplot as plt

from container import build_services
from data.extrema.extrema_detector import find_local_extrema
from data.lines.creation.trend_lines import generate_trend_lines
from data.structure.candle_loader import (
    candles_to_dataframe,
    compute_avg_volatility_pct,
)
from settings.loader import get_config
from visuals.trend_line_plotter import plot_trend_lines


def main(product_id: str, show_plot: bool, save_plot: bool) -> None:
    config = get_config()
    services = build_services()
    end = datetime.now(UTC)
    start = end - timedelta(days=config.candle.candle_history_days)

    candles = services.product_api.get_historic_candles(
        product_id,
        start_time=start,
        end_time=end,
        granularity_mins=config.candle.granularity_mins,
        granularity_str=config.candle.granularity_str,
    )
    df = candles_to_dataframe(candles)
    avg_volatility_pct = compute_avg_volatility_pct(candles)
    maximas, minimas = find_local_extrema(df, config.strategy.extrema_window_size)
    raw_trend_lines = generate_trend_lines(
        maximas + minimas,
        df,
        config.strategy.max_slope_deg,
        config.strategy.duration_in_candles,
        4 * avg_volatility_pct,
    )

    raw_support_lines = [line for line in raw_trend_lines if line.state == "support"]
    raw_resistance_lines = [line for line in raw_trend_lines if line.state == "resistance"]

    print(f"\nEND TIME: {end}\n")
    print(f"\nSTART TIME: {start}\n")
    print(f"\nDELTA TIME: {config.candle.candle_history_days} days\n")
    print(f"\nNUMBER OF CANDLES: {len(candles)}\n")
    print(f"\nDATAFRAME SIZE: {len(df)}\n")
    print(f"\nNUMBER OF MAXIMAS: {len(maximas)}\n")
    print(f"\nNUMBER OF MINIMAS: {len(minimas)}\n")
    print(f"\nNUMBER OF RAW TREND LINES: {len(raw_trend_lines)}\n")
    print(f"\nNUMBER OF RAW SUPPORT LINES: {len(raw_support_lines)}\n")
    print(f"\nNUMBER OF RAW RESISTANCE LINES: {len(raw_resistance_lines)}\n")
    print(f"\nRAW SUPPORT LINES: {raw_support_lines}\n")
    print(f"\nRAW RESISTANCE LINES: {raw_resistance_lines}\n")

    plot_trend_lines(df, raw_trend_lines, save_plot, show_plot, product_id)

    if show_plot:
        plt.show()
