"""
trade_plotter.py
"""

import os
from pathlib import Path
from typing import Any

import mplfinance as mpf
import numpy as np
import pandas as pd

from models.scored_line import ScoredLine
from settings.config import config
from visuals.plotting_utils import finalise_plot


def plot_trade_cycle(
    df: pd.DataFrame,
    support_line: ScoredLine,
    resistance_line: ScoredLine | None,
    plot_metadata: dict[str, Any],
) -> None:
    mask = (df.index >= plot_metadata["start_window"]) & (df.index <= plot_metadata["end_window"])
    df_window = df.loc[mask].copy()
    addplots = []

    x_vals = np.array(
        [
            (
                (ts - config.backtest.base_time).total_seconds()
                / (60 * config.candle.granularity_mins)
            )
            for ts in df_window.index
        ]
    )
    support_y_vals = support_line.line.slope * x_vals + support_line.line.intercept
    addplots.append(mpf.make_addplot(support_y_vals, color="green"))
    if resistance_line:
        resistance_y_vals = resistance_line.line.slope * x_vals + resistance_line.line.intercept
        addplots.append(mpf.make_addplot(resistance_y_vals, color="red"))

    buy_series = pd.Series(np.nan, index=df_window.index)
    sell_series = pd.Series(np.nan, index=df_window.index)
    buy_series.at[plot_metadata["buy_point"][0]] = plot_metadata["buy_point"][1]
    sell_series.at[plot_metadata["sell_point"][0]] = plot_metadata["sell_point"][1]
    addplots.append(
        mpf.make_addplot(buy_series, type="scatter", marker="^", markersize=75, color="blue")
    )
    addplots.append(
        mpf.make_addplot(sell_series, type="scatter", marker="v", markersize=75, color="orange")
    )

    figure, _ = mpf.plot(
        df_window,
        type="candle",
        style="charles",
        title=f"{plot_metadata['product_id']} Trade Cycle {plot_metadata['trade_count']}",
        volume=False,
        addplot=addplots,
        returnfig=True,
        block=False,
        warn_too_much_data=1500,
    )

    base_dir = Path(os.getenv("CHARTS_DIR", "charts"))
    out_dir = base_dir / "trades" / f"{plot_metadata['product_id']}"
    out_dir.mkdir(parents=True, exist_ok=True)
    full_path = out_dir / f"{plot_metadata['trade_count']}.png"
    finalise_plot(figure, True, False, full_path)
