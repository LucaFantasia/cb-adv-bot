"""
line_strength_plotter.py - Visualises scoring metrics of trend lines

Includes:
- Bar chart for score components
- Candle chart with line and touch/break markers
"""

import os
from datetime import UTC, datetime
from typing import Any

import matplotlib.pyplot as plt
import mplfinance as mpf
import numpy as np
import pandas as pd

from models.scored_line import ScoredLine
from visuals.plotting_utils import finalise_plot


def plot_line_score_components(
    line: ScoredLine, line_number: int, save: bool, show: bool, product_id: str
) -> None:
    """
    Plots a bar chart showing the score contributions from each scoring component.

    Args:
        line: The ScoredLine object containing the score and breakdown
        line_number: Number to identify the line
        save: Whether or not to save the figure in the disk
        show: Whether or not to show the figure on screen
        product_id: ID of the product to plot
    """
    components = line.score_components
    labels = list(components.keys())
    scores = list(components.values())

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(labels, scores, color=["green" if v >= 0 else "red" for v in scores])
    ax.axhline(0, color="black", linewidth=1)
    ax.set_title(
        f"{product_id} {line.current_state} line {line_number} ({line.line.slope:.2f},{line.line.intercept:.2f}) ,score: {line.score:.2f}"
    )
    ax.set_ylabel("Score Contributions")
    plt.xticks(rotation=45, ha="right")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
    line_state_caps = "RESISTANCE" if line.current_state == "resistance" else "SUPPORT"
    filename = f"{product_id}_{line_state_caps}_LINE_{line_number}_SCORE_COMPONENTS_{timestamp}"
    path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "charts", "scores", f"{product_id}")
    )
    os.makedirs(path, exist_ok=True)
    full_path = os.path.join(path, filename)

    finalise_plot(fig, save, show, full_path)


def plot_line_scoring_detections(
    df: pd.DataFrame,
    line: ScoredLine,
    plot_metadata: dict[str, Any],
) -> None:
    """
    Plots a candlestick chart with the trend line and markers for touches, soft touches, and breaks.

    Args:
        df: DataFrame of the product candles
        line: The ScoredLine object containing the score and breakdown
        plot_metadata: Dict containing line number; save; show; product_id
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

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
    line_state_caps = "RESISTANCE" if line.current_state == "resistance" else "SUPPORT"
    filename = f"{plot_metadata['product_id']}_{line_state_caps}_LINE_{plot_metadata['line_number']}_SCORE_DETECTIONS_{timestamp}"
    path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "charts",
            "scores",
            f"{plot_metadata['product_id']}",
        )
    )
    os.makedirs(path, exist_ok=True)
    full_path = os.path.join(path, filename)

    finalise_plot(figure, plot_metadata["save"], plot_metadata["show"], full_path)
