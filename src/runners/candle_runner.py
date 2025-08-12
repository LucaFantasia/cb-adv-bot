"""
candle_runner.py — Visual inspection of raw OHLCV candles
"""

import sys
from datetime import UTC, datetime, timedelta

import matplotlib.pyplot as plt

from api.product import ProductClient
from data.structure.candle_loader import candles_to_dataframe
from settings.config import config
from visuals.candle_plotter import plot_candles


def main(product_id: str) -> None:
    show_plot = True
    save_plot = False

    end = datetime.now(UTC)
    start = end - timedelta(days=config.candle.candle_history_days)

    client = ProductClient()
    candles = client.get_historic_candles(
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


if __name__ == "__main__":
    try:
        product_id = sys.argv[1] if len(sys.argv) > 1 else "BTC-USD"
        main(product_id)
    except Exception:
        import traceback

        traceback.print_exc()
        input("Press ENTER to exit...")
