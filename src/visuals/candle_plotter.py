"""
candle_plotter.py - OHLC Candle Visualisation

Provides functions to render basic candlestick charts using mplfinance, with optional overlays.
"""

import os
from datetime import UTC, datetime
from pathlib import Path

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

    base_dir = Path(os.getenv("CHARTS_DIR", "charts"))
    out_dir = base_dir / "candles" / f"{product_id}"
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
    full_path = out_dir / f"{timestamp}.png"
    finalise_plot(figure, save, show, full_path)
