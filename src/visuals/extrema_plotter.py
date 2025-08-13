"""
extrema_plotter.py — Extrema Visualization

Plots local maxima and minima points over a candlestick chart.
"""

import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import mplfinance as mpf
import numpy as np
import pandas as pd

from visuals.plotting_utils import finalise_plot


def plot_extrema(
    df: pd.DataFrame,
    maximas: list[tuple[str, float, int]],
    minimas: list[tuple[str, float, int]],
    plot_metadata: dict[str, Any],
) -> None:
    """
    Plots a candlestick chart with extrema (high/low) points marked.

    Args:
        df: DataFrame with OHLCV data. Index must be datetime.
        maximas: List of (timestamp, price, index) tuples for local peaks.
        minimas: List of (timestamp, price, index) tuples for local troughs.
        plot_metadata: Dict containing info whether to save, show and product id
    """
    addplots = []
    maxima_series = pd.Series(np.nan, index=df.index)
    minima_series = pd.Series(np.nan, index=df.index)

    for _, price, idx in maximas:
        maxima_series.at[df.index[idx]] = price
    for _, price, idx in minimas:
        minima_series.at[df.index[idx]] = price

    if maxima_series.notna().any():
        addplots.append(
            mpf.make_addplot(maxima_series, type="scatter", marker="X", markersize=50, color="blue")
        )
    if minima_series.notna().any():
        addplots.append(
            mpf.make_addplot(minima_series, type="scatter", marker="X", markersize=50, color="red")
        )

    figure, _ = mpf.plot(
        df,
        type="candle",
        style="charles",
        title=f"{plot_metadata['product_id']} extremas",
        volume=False,
        addplot=addplots,
        returnfig=True,
        block=False,
        warn_too_much_data=1500,
    )

    base_dir = Path(os.getenv("CHARTS_DIR", "charts"))
    out_dir = base_dir / "extremas" / f"{plot_metadata['product_id']}"
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
    full_path = out_dir / f"{timestamp}.png"
    finalise_plot(figure, plot_metadata["save"], plot_metadata["show"], full_path)
