"""
trade_logger.py
"""

import csv
from datetime import datetime, timedelta
from pathlib import Path


class TradeLogger:
    def __init__(self, product_id: str, start_window: datetime) -> None:
        self.product_id = product_id
        self.start_window = start_window
        self.trade_log: list[dict[str, str | datetime | float]] = []
        self.returns: list[float] = []

    def record_trade(self, action: str, ts: datetime, price: float, note: str) -> None:
        self.trade_log.append(
            {
                "product_id": self.product_id,
                "action": action,
                "timestamp": ts,
                "price": price,
                "note": note,
                "start_window": self.start_window,
                "end_window": ts,
            }
        )

    def append_return(self, delta: float) -> None:
        self.returns.append(delta)

    def get_avg_return(self) -> float:
        return (sum(self.returns) / len(self.returns)) if len(self.returns) > 0 else 0.0

    def get_latest_trade_ts(self) -> datetime:
        return self.start_window + timedelta(days=7)

    def export_to_csv(self) -> None:
        if not self.trade_log:
            return

        project_root = Path(__file__).resolve().parents[2]
        out_path = project_root / "sheets" / self.product_id / "TRADES.csv"
        path = Path(out_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        write_header = not path.exists()
        fieldnames = list(self.trade_log[0].keys())
        with path.open("a", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if write_header:
                writer.writeheader()
            writer.writerows(self.trade_log)
