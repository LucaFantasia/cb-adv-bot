"""
overlays_plotter.py - Visualise volatility metrics of trend lines

Plots trend lines with volatility and deviation overlays
"""

import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import mplfinance as mpf
import numpy as np
import pandas as pd

from models.scored_line import ScoredLine
from visuals.plotting_utils import finalise_plot


def plot_trend_line_overlays(
    df: pd.DataFrame,
    line: ScoredLine,
    avg_volatility_pct: float,
    deviation_price: float,
    plot_metadata: dict[str, Any],
) -> None:
    """
    Plots a candlestick chart with the trend line and markers for touches, soft touches, and breaks, as well as volatility overlays
    for average volatility and deviation price.

    Args:
        df: DataFrame of the product candles
        line: The ScoredLine object containing the score and breakdown
        plot_metadata: Dict containing info about save; show; line_number; product_id
    """
    addplots = []
    touch_series = pd.Series(np.nan, index=df.index)
    soft_touch_series = pd.Series(np.nan, index=df.index)
    break_series = pd.Series(np.nan, index=df.index)

    x_vals = np.arange(len(df))
    y_vals = line.line.slope * x_vals + line.line.intercept
    addplots.append(
        mpf.make_addplot(y_vals, color="green" if line.current_state == "support" else "red")
    )
    addplots.append(
        mpf.make_addplot(
            y_vals + 4 * deviation_price, type="line", linestyle="--", width=1, color="gray"
        )
    )
    addplots.append(
        mpf.make_addplot(
            y_vals - 4 * deviation_price, type="line", linestyle="--", width=1, color="gray"
        )
    )

    latest_price = df["Close"].iloc[-1]
    volatility_height = latest_price * avg_volatility_pct
    volatility_bar_top = pd.Series(np.nan, index=df.index)
    volatility_bar_bottom = pd.Series(np.nan, index=df.index)
    for i, factor in enumerate([1.0, 2.0, 4.0], 1):
        volatility_bar_top.iloc[len(df) - i] = latest_price + factor * volatility_height
        volatility_bar_bottom.iloc[len(df) - i] = latest_price - factor * volatility_height
    addplots.append(
        mpf.make_addplot(
            volatility_bar_top, type="scatter", marker="_", markersize=200, color="green"
        )
    )
    addplots.append(
        mpf.make_addplot(
            volatility_bar_bottom, type="scatter", marker="_", markersize=200, color="red"
        )
    )

    for idx in line.touches:
        touch_series.at[df.index[idx]] = line.line.project_price(idx)
    for idx in line.soft_touches:
        soft_touch_series.at[df.index[idx]] = line.line.project_price(idx)
    for idx in line.breaks:
        break_series.at[df.index[idx]] = line.line.project_price(idx)

    if touch_series.notna().any():
        addplots.append(
            mpf.make_addplot(
                touch_series, type="scatter", marker="*", markersize=75, color="purple"
            )
        )
    if soft_touch_series.notna().any():
        addplots.append(
            mpf.make_addplot(
                soft_touch_series, type="scatter", marker="+", markersize=75, color="blue"
            )
        )
    if break_series.notna().any():
        addplots.append(
            mpf.make_addplot(break_series, type="scatter", marker="X", markersize=75, color="black")
        )

    figure, _ = mpf.plot(
        df,
        type="candle",
        style="charles",
        title=f"{plot_metadata['product_id']} {line.current_state} line {plot_metadata['line_number']} scoring detections",
        volume=False,
        addplot=addplots,
        returnfig=True,
        block=False,
        warn_too_much_data=1500,
    )

    base_dir = Path(os.getenv("CHARTS_DIR", "charts"))
    out_dir = base_dir / "overlays" / f"{plot_metadata['product_id']}"
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
    line_state_caps = "RESISTANCE" if line.current_state == "resistance" else "SUPPORT"
    full_path = (
        out_dir / f"{line_state_caps}_LINE_{plot_metadata['line_number']}_OVERLAY_{timestamp}.png"
    )
    finalise_plot(figure, plot_metadata["save"], plot_metadata["show"], full_path)
