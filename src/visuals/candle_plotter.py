"""
candle_plotter.py - OHLC Candle Visualisation

Provides functions to render basic candlestick charts using mplfinance, with optional overlays.
"""

import os
from datetime import UTC, datetime

import mplfinance as mpf
import pandas as pd

from visuals.plotting_utils import finalise_plot


def plot_candles(df: pd.DataFrame, save: bool, show: bool, product_id: str) -> None:
    """
    Plots a basic candlestick chart using the OHLCV dataframe.

    Args:
        df: DataFrame with OHLCV data. Index must be datetime.
        save: Whether to save the plot as a file
        show: Whether to display the plot
        product_id: ID of the product to plot
    """
    figure, _ = mpf.plot(
        df,
        type="candle",
        style="charles",
        title=f"{product_id} candles",
        volume=False,
        returnfig=True,
        block=False,
        warn_too_much_data=1500,
    )

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
    filename = f"{product_id}_CANDLES_{timestamp}"
    path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "charts", "candles", f"{product_id}")
    )
    os.makedirs(path, exist_ok=True)
    full_path = os.path.join(path, filename)

    finalise_plot(figure, save, show, full_path)
