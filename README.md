# Coinbase Advanced Trading Bot (cb-adv-bot)

## Overview
`cb-adv-bot` is a Python trading system built around the Coinbase **Advanced Trade** API. It combines:
- a modular API layer (REST + WebSocket),
- a configurable strategy engine,
- backtesting utilities, and
- rich visualisations for diagnostics.

> **Disclaimer:** This project is for educational purposes and is **not** financial advice. Use paper trading / sandbox environments where possible and never trade funds you can’t afford to lose.

---

## Key Features
- **API layer** for Coinbase Advanced Trade (JWT auth, typed models, clean client abstractions)
- **WebSocket listener** for real-time ticker updates
- **Strategy engine** with trend-line / extrema based logic
- **Backtesting runner** using historical candles
- **Visual diagnostics** (plots, overlays, saved artefacts)
- **CLI** (Typer) to run pipelines, visualisations, backtests, and live mode

---

## Project Structure
- `src/api/` — REST clients, auth, websocket, models, ports (interfaces)
- `src/strategy/` — strategy + backtest engines and state/logging
- `src/runners/` — runnable entry points (backtest, metrics, best line, etc.)
- `src/visuals/` — plotting + chart outputs
- `tests/` — unit tests (fakes for external services)

---

## Setup

### 1) Create a virtual environment
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

### 2) Install dependencies
```bash
pip install -U pip
pip install -e .
```

### 3) Configure environment variables
Create a local `.env` file (do **not** commit it) with:

```bash
# Coinbase Advanced Trade credentials
CDP_API_KEY_ID="..."
CDP_API_KEY_SECRET="..."   # base64-encoded private key

# Coinbase host + base path (example values)
CB_HOST_NAME="api.coinbase.com"
CB_API_PATH="/api/v3/brokerage"

# Optional: logging
LOG_LEVEL="INFO"
LOG_FILE=""
LOG_FILE_LEVEL="INFO"

# Optional: output directories
CHARTS_DIR="charts"
SHEETS_DIR="runs"
RUN_TAG=""
```

---

## Usage (CLI)

After installation, the CLI entry point is:

```bash
cb --help
```

Common commands:

```bash
cb candles --product BTC --show
cb extrema --product BTC --save
cb trend-lines --product BTC --show
cb scored-lines --product BTC --save
cb metrics --product BTC --show
cb best-line --product BTC --show
cb backtest
cb activate
```

- `backtest` runs the current strategy logic on historical candles.
- `activate` starts the bot in real time (uses REST + WebSocket).

---

## Testing & CI

Run locally:
```bash
ruff check .
mypy src
pytest
```

CI runs the same checks on each push / PR.

---

## Why This Project Matters
This repository demonstrates end-to-end engineering of a data-driven system:
- clean boundaries (ports/adapters),
- typed data models and strict linting,
- backtesting and evaluation scaffolding,
- observability via structured logging and saved artefacts.
