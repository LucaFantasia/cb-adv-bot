"""
candle_runner.py — Visual inspection of raw OHLCV candles
"""

from datetime import UTC, datetime, timedelta

import matplotlib.pyplot as plt

from container import build_services
from data.structure.candle_loader import candles_to_dataframe
from settings.loader import get_config
from visuals.candle_plotter import plot_candles


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

    print(f"\nEND TIME: {end}\n")
    print(f"\nSTART TIME: {start}\n")
    print(f"\nDELTA TIME: {config.candle.candle_history_days} days\n")
    print(f"\nNUMBER OF CANDLES: {len(candles)}\n")
    print(f"\nCANDLES: {candles}\n")
    print(f"\nDATAFRAME SIZE: {len(df)}\n")
    print(f"\nDATAFRAME: {df}\n")

    plot_candles(df, save_plot, show_plot, product_id)

    if show_plot:
        plt.show()
