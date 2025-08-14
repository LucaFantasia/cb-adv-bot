# src/runners/backtest_bootstrap.py (new small helper)
import os
from datetime import datetime
from pathlib import Path


def prepare_backtest_run_dirs(run_name: str | None = None) -> dict[str, str]:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_name = run_name or "backtest"
    run_dir = Path("runs") / f"{ts}_{run_name}"
    logs_dir = run_dir / "logs"
    charts_dir = run_dir / "charts"
    sheets_dir = run_dir / "sheets"
    for d in (run_dir, logs_dir, charts_dir, sheets_dir):
        d.mkdir(parents=True, exist_ok=True)

    # Set env vars BEFORE logger setup
    os.environ["RUN_TAG"] = run_dir.name
    os.environ["LOG_FILE"] = str(logs_dir / "run.log")
    os.environ["LOG_FORMAT"] = "json"

    os.environ["CHARTS_DIR"] = str(charts_dir)
    os.environ["SHEETS_DIR"] = str(sheets_dir)

    return {
        "run_dir": str(run_dir),
        "logs_dir": str(logs_dir),
        "charts_dir": str(charts_dir),
        "sheets_dir": str(sheets_dir),
    }
