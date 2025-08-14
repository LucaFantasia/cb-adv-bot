from __future__ import annotations

import enum
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Annotated

if TYPE_CHECKING:
    from pathlib import Path

import os

import typer

from runners.backtest_runner import main as backtest_run
from runners.best_line_runner import main as best_line_run
from runners.candle_runner import main as candle_run
from runners.debug_runner import main as debug_run
from runners.extrema_runner import main as extrema_run
from runners.main_runner import main as main_run
from runners.metrics_runner import main as metrics_run
from runners.scored_line_runner import main as scored_line_run
from runners.trend_line_runner import main as trend_line_run

app = typer.Typer(help="Coinbase Advanced Bot runners")


class Product(enum.Enum):
    BTC = "BTC-USD"
    ETH = "ETH-USD"
    XRP = "XRP-USD"
    SOL = "SOL-USD"


def _init(
    log_level: Annotated[
        str, typer.Option("--log-level", envvar="LOG_LEVEL", help="Console log level")
    ] = "INFO",
    log_file: Annotated[
        Path | None,
        typer.Option("--log-file", envvar="LOG_FILE", help="Optional rotating log file path"),
    ] = None,
    log_file_level: Annotated[
        str, typer.Option("--log-file-level", envvar="LOG_FILE_LEVEL", help="File log level")
    ] = "INFO",
) -> None:
    if log_file:
        os.environ["LOG_FILE"] = str(log_file)
        os.environ["LOG_FILE_LEVEL"] = log_file_level

    os.environ["LOG_LEVEL"] = log_level


app.callback()(_init)


def candles(
    product: Product = Product.BTC,
    show: Annotated[bool, typer.Option("--show/--no-show")] = False,
    save: Annotated[bool, typer.Option("--save/--no-save")] = False,
) -> None:
    candle_run(product.value, bool(show), bool(save))


app.command(help="Build candles dataframe and plot/save if requested")(candles)


def extrema(
    product: Product = Product.BTC,
    show: Annotated[bool, typer.Option("--show/--no-show")] = False,
    save: Annotated[bool, typer.Option("--save/--no-save")] = False,
) -> None:
    extrema_run(product.value, bool(show), bool(save))


app.command(help="Extrema detector")(extrema)


def trend_lines(
    product: Product = Product.BTC,
    show: Annotated[bool, typer.Option("--show/--no-show")] = False,
    save: Annotated[bool, typer.Option("--save/--no-save")] = False,
) -> None:
    trend_line_run(product.value, bool(show), bool(save))


app.command(help="Trend lines and plots")(trend_lines)


def scored_lines(
    product: Product = Product.BTC,
    show: Annotated[bool, typer.Option("--show/--no-show")] = False,
    save: Annotated[bool, typer.Option("--save/--no-save")] = False,
) -> None:
    scored_line_run(product.value, bool(show), bool(save))


app.command(help="Scored lines and plots")(scored_lines)


def metrics(
    product: Product = Product.BTC,
    show: Annotated[bool, typer.Option("--show/--no-show")] = False,
    save: Annotated[bool, typer.Option("--save/--no-save")] = False,
) -> None:
    metrics_run(product.value, bool(show), bool(save))


app.command(help="Overlays and diagnostics visualisation")(metrics)


def best_line(
    product: Product = Product.BTC,
    current_time: Annotated[
        datetime | None, typer.Option("--current_time", help="ISO8601, e.g. 2024-01-01T00:00:00")
    ] = None,
    show: Annotated[bool, typer.Option("--show/--no-show")] = False,
    save: Annotated[bool, typer.Option("--save/--no-save")] = False,
) -> None:
    best_line_run(
        product.value,
        current_time.astimezone(UTC) if current_time else current_time,
        bool(show),
        bool(save),
    )


app.command(help="Visualise best lines and scoring")(best_line)


def backtest() -> None:
    backtest_run()


app.command(help="Backtest current strategy with historical data")(backtest)


def activate() -> None:
    main_run()


app.command(help="Activate the bot to trading in real time")(activate)


def debug() -> None:
    debug_run()


app.command(help="Special debugging runner")(debug)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
