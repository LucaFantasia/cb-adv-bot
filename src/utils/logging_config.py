from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from logging.config import dictConfig
from pathlib import Path
from typing import Any

_LOGGING_STATE = {"configured": False}


@dataclass(frozen=True)
class LogSettings:
    level: str = os.getenv("LOG_LEVEL", "INFO").upper()
    fmt: str = os.getenv("LOG_FORMAT", "json")  # "json" or "plain"
    file_path: str | None = os.getenv("LOG_FILE")  # e.g. "logs/app.log"
    file_level: str = os.getenv("LOG_FILE_LEVEL", "INFO").upper()
    max_bytes: int = int(os.getenv("LOG_MAX_BYTES", str(5 * 1024 * 1024)))
    backup_count: int = int(os.getenv("LOG_BACKUP_COUNT", "3"))
    run_tag: str | None = os.getenv("RUN_TAG")  # e.g. backtest id


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.fromtimestamp(record.created, tz=UTC).isoformat().replace("+00:00", "Z"),
            "lvl": record.levelname,
            "name": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        # Add extra fields if present
        for k, v in record.__dict__.items():
            if k not in payload and k not in {
                "args",
                "msg",
                "levelno",
                "levelname",
                "name",
                "created",
                "msecs",
                "relativeCreated",
                "pathname",
                "filename",
                "module",
                "lineno",
                "funcName",
                "exc_info",
                "exc_text",
                "stack_info",
            }:
                payload[k] = v
        return json.dumps(payload, ensure_ascii=False, default=str)


def _file_handler(path: Path, level: str, max_bytes: int, backup_count: int) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    return {
        "class": "logging.handlers.RotatingFileHandler",
        "level": level,
        "filename": str(path),
        "maxBytes": max_bytes,
        "backupCount": backup_count,
        "encoding": "utf-8",
    }


def setup_logging() -> None:
    """
    Idempotent logging config:
      - stdout JSON (prod) or plain (dev)
      - optional rotating file if LOG_FILE is set
    """
    if _LOGGING_STATE["configured"]:
        return

    cfg = LogSettings()
    common_fmt = "%(asctime)s %(levelname)s %(name)s %(message)s"

    handlers: dict[str, dict[str, Any]] = {}
    root_handlers: list[str] = []

    # stdout handler (always on)
    handlers["stdout"] = {
        "class": "logging.StreamHandler",
        "stream": "ext://sys.stdout",
        "level": cfg.level,
        "formatter": "json" if cfg.fmt == "json" else "plain",
    }
    root_handlers.append("stdout")

    # optional file handler
    if cfg.file_path:
        handlers["file"] = _file_handler(
            Path(cfg.file_path), cfg.file_level, cfg.max_bytes, cfg.backup_count
        )
        handlers["file"]["formatter"] = "json" if cfg.fmt == "json" else "plain"
        root_handlers.append("file")

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "plain": {"format": common_fmt},
                "json": {"()": JsonFormatter},  # noqa: PLC2801
            },
            "handlers": handlers,
            "root": {"level": "DEBUG", "handlers": root_handlers},
        }
    )

    # Mark configured so we don’t re-add handlers
    _LOGGING_STATE["configured"] = True


def get_logger(name: str = "cb") -> logging.Logger:
    setup_logging()
    return logging.getLogger(name)
