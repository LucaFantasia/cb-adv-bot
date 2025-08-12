"""
trend_line_plotter.py — Trend Line Visualization

Plots generated support/resistance lines over a candlestick chart, with optional scoring info.
"""

import os
from datetime import UTC, datetime
from typing import Any

import mplfinance as mpf
import pandas as pd

from models.scored_line import ScoredLine
from models.trend_line import TrendLine
from visuals.plotting_utils import finalise_plot


def plot_trend_lines(
    df: pd.DataFrame, lines: list[TrendLine], save: bool, show: bool, product_id: str
) -> None:
    """
    Plots basic trend lines over a candlestick chart.

    Args:
        df: OHLCV DataFrame
        lines: List of TrendLine objects
        save, show: Plot I/O options
        product_id: ID of product to plot
    """
    addplots = []
    for line in lines:
        x_vals = list(range(len(df)))
        y_vals = [line.slope * i + line.intercept for i in x_vals]
        addplots.append(
            mpf.make_addplot(y_vals, color="green" if line.state == "support" else "red")
        )

    figure, _ = mpf.plot(
        df,
        type="candle",
        style="charles",
        title=f"{product_id} trend lines",
        volume=False,
        addplot=addplots,
        returnfig=True,
        block=False,
        warn_too_much_data=1500,
    )

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
    filename = f"{product_id}_TREND_LINES_{timestamp}"
    path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "charts", "lines", f"{product_id}")
    )
    os.makedirs(path, exist_ok=True)
    full_path = os.path.join(path, filename)

    finalise_plot(figure, save, show, full_path)


def plot_scored_lines(
    df: pd.DataFrame, lines: list[ScoredLine], plot_metadata: dict[str, Any]
) -> None:
    """
    Plots basic scored lines over a candlestick chart.

    Args:
        df: OHLCV DataFrame
        lines: List of ScoredLine objects
        plot_metadata: Dict containing info about save; show; trade_count; product_id
    """
    addplots = []
    for line in lines:
        x_vals = list(range(len(df)))
        y_vals = [line.line.slope * i + line.line.intercept for i in x_vals]
        addplots.append(
            mpf.make_addplot(y_vals, color="green" if line.current_state == "support" else "red")
        )

    figure, _ = mpf.plot(
        df,
        type="candle",
        style="charles",
        title=(
            f"{plot_metadata['product_id']} scored lines {plot_metadata['trade_count']}"
            if plot_metadata["trade_count"]
            else f"{plot_metadata['product_id']} scored lines"
        ),
        volume=False,
        addplot=addplots,
        returnfig=True,
        block=False,
        warn_too_much_data=1500,
    )

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
    filename = (
        f"{plot_metadata['product_id']}_SCORED_LINES_{plot_metadata['trade_count']}"
        if plot_metadata["trade_count"]
        else f"{plot_metadata['product_id']}_SCORED_LINES_{timestamp}"
    )
    path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "charts",
            "lines",
            f"{plot_metadata['product_id']}",
        )
    )
    os.makedirs(path, exist_ok=True)
    full_path = os.path.join(path, filename)

    finalise_plot(figure, plot_metadata["save"], plot_metadata["show"], full_path)
