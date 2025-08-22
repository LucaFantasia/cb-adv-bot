# Executive summary (actionable)

- Keep behaviour identical: add tests first, then refactor behind a thin façade.
- Introduce project tooling: `pyproject.toml` with ruff+black+isort+mypy+pytest+coverage+pre-commit.
- Strengthen config: immutable typed configs (Pydantic), environment loading (.env) via python‑dotenv, per‑env overrides.
- Improve API layer: retries/backoff, timeouts, idempotency keys, structured error types, typed responses, and `httpx` client (sync/async) behind an interface to keep the rest of the code stable.
- Stabilise data/strategy interfaces: dataclasses + Protocols for candles, lines, scored results; pure functions where possible; deterministic line selection.
- Observability: consistent structured logging, timing metrics, and debug artefacts (figures, CSVs) behind feature flags.
- Testing: golden‑master tests for scoring/selection, property‑based tests for line geometry, and fixtures for Coinbase responses; a tiny backtest dataset for CI.
- Performance: vectorise hot loops with NumPy, cache repeated calculations, avoid repeated allocations, and gate plotting.
- Next step (bull flags): add a `patterns/` package with a common `PatternDetector` interface, unit tests on synthetic data, and feature‑flag the strategy hook.

---

# 1) Repository hygiene & tooling

## 1.1 pyproject + linters

Create a single `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools", "wheel"]

[project]
name = "cb-adv-bot"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
  "httpx>=0.27",
  "websockets>=12",
  "pydantic>=2",
  "python-dotenv>=1",
  "pandas>=2",
  "numpy>=2",
  "matplotlib>=3",
]

[tool.black]
line-length = 100

[tool.isort]
profile = "black"

[tool.ruff]
line-length = 100
select = ["E","F","I","UP","B","SIM","PL","TCH"]
ignore = ["E501"]

[tool.mypy]
python_version = "3.11"
warn_unused_configs = true
strict = true
plugins = ["pydantic.mypy"]

[tool.pytest.ini_options]
minversion = "8.0"
addopts = "-q --maxfail=1"
pythonpath = ["src"]
```

Add `.pre-commit-config.yaml` with ruff/black/isort, and enable CI (GitHub Actions) to run `pytest` + type checks on every push.

## 1.2 Project layout tweaks

- Root `README.md`: include quick start, environment setup, make targets, and architecture diagram.
- Move `.env` from `src/.env` → project root; load via `python-dotenv` only in dev. In prod, use real env vars or secret manager.
- Add `Makefile` targets: `make setup`, `lint`, `fmt`, `test`, `run-backtest`, `plot-sample`.
- Add `src/cli.py` (Typer) to expose runners as commands instead of multiple `*_runner.py` entrypoints.

---

# 2) Configuration & dependency injection

## 2.1 Typed config objects

Replace `settings/*.py` dataclasses with Pydantic models. Keep defaults identical; allow overrides via env/JSON.

```python
# src/settings/models.py
from pydantic import BaseModel, Field

class CandleConfig(BaseModel):
    granularity_str: str = "FIFTEEN_MINUTE"
    granularity_mins: int = 15
    candle_history_days: int = 7

class StrategyConfig(BaseModel):
    extrema_window_size: int = 7
    duration_in_candles: int = 30
    break_criteria: list[tuple[float, int]] = Field(default_factory=lambda: [(5.0,1),(4.0,5),(3.0,10)])
    num_of_top_lines: int = 2
    deviation_factor: float = 40.0

class BacktestConfig(BaseModel):
    start_days_ago: int = 7
    product_ids: list[str] = ["BTC-USD","ETH-USD","XRP-USD","SOL-USD"]

class Config(BaseModel):
    candle: CandleConfig = CandleConfig()
    strategy: StrategyConfig = StrategyConfig()
    backtest: BacktestConfig = BacktestConfig()
```

Expose a single `get_config()` that returns a cached instance; accept partial overrides for tests.

## 2.2 DI for services

Define light-weight interfaces (Protocols) for `Clock`, `ProductAPI`, `OrderAPI`, `AccountAPI`, and inject them into engines/runners. This lets you swap real clients for fakes in tests without changing behaviour.

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class ProductAPI(Protocol):
    def get_candles(self, product_id: str, start: str, end: str, granularity: str) -> dict: ...
```

---

# 3) API layer hardening (behaviour‑preserving)

- **HTTP client**: wrap `requests` in a tiny adapter now; later swap to `httpx` with timeouts and retries via `backoff`.
- **Retries**: exponential backoff on 429/5xx with jitter; respect Coinbase `rate_limit` headers.
- **Idempotency**: set idempotency keys on order POSTs to make retries safe.
- **Timeouts**: connect/read timeouts on all calls; never rely on defaults.
- **Typed responses**: parse JSON into small Pydantic response models to avoid `dict[str, Any]` everywhere.
- **WebSocket**: (when you wire it) add heartbeat/auto‑resubscribe, sequence‑gap detection, and a bounded queue feeding the aggregator.

Example adapter (keeps current call sites unchanged):

```python
# src/api/http.py
from dataclasses import dataclass
from typing import Any, Mapping
import requests

@dataclass
class HttpResponse:
    ok: bool
    status_code: int
    json: Any
    text: str

class HttpClient:
    def __init__(self) -> void:
        self._s = requests.Session()

    def request(self, method: str, url: str, headers: Mapping[str,str], data: bytes|None) -> HttpResponse:
        r = self._s.request(method, url, headers=headers, data=data, timeout=(5, 15))
        return HttpResponse(r.ok, r.status_code, (r.json() if r.content else None), r.text)
```

Your existing `BaseClient` can depend on this `HttpClient` via constructor param with a default, preserving behaviour.

---

# 4) Data layer: determinism, speed, clarity

## 4.1 Deterministic extrema & lines

- Ensure extrema detection is pure and deterministic for given inputs; pass all parameters explicitly.
- Sort and de‑duplicate candidate lines by `(start_idx, end_idx, slope, intercept)` to prevent non‑deterministic iteration ordering.
- Cache repeated `project_price(idx)` calls per line if used inside inner loops.

## 4.2 Vectorise hot paths

Identify loops over candles for touch/break checks and convert to NumPy operations. Example (conceptual):

```python
# Given arrays: proj, highs, lows, body_highs, body_lows
within = (lows <= proj) & (proj <= highs)
soft = ((body_lows <= proj) & (proj <= body_highs)) & ~within
```

Compute touches/breaks indices using `np.where(within)[0].tolist()` instead of Python loops.

## 4.3 Stable scoring

- Keep `score_components` with explicit weights. Extract weights to config and freeze with `MappingProxyType`.
- Prefer `float32` arrays to cut memory and improve cache locality if datasets are large.

## 4.4 Caching & memoisation

- Use `functools.lru_cache` or precomputed arrays for anything derived solely from candles (e.g., ATR, log‑returns, deviation bands).
- If the same `deviation_pct` is reused across lines, precompute band arrays once.

---

# 5) Strategy layer: interfaces & safety

- Define a `Strategy` Protocol with methods `on_candle(...) -> list[Signal]` and `reset()`.
- Keep current behaviour but emit structured `Signal` objects (`BUY`, `SELL`, reason, ref line id, prices).
- Add simple **risk guardrails** (no behavioural change under normal conditions): min/max order size from config, ignore duplicate signals in the same candle, and a cool‑down period parameter (default zero).
- Put slippage and fees as config constants used only in backtests.

```python
@dataclass(frozen=True)
class Signal:
    side: Literal["BUY","SELL"]
    price: float
    reason: str
    ref_line: int  # index or uuid of line
```

---

# 6) Observability & debugging

- Logging: include `product_id`, `granularity`, `candle_idx`, `line_id` in structured key=value style; avoid expensive string formatting if debug is off.
- Metrics: log timing for `extrema`, `line_generation`, `scoring`, `selection` using `time.perf_counter()`.
- Plotting: wrap plotting calls in `if debug_plots:` to avoid heavy matplotlib work in normal runs.
- Artefacts: write plots/CSVs under `artifacts/YYYYMMDD_HHMMSS/` per run id.

---

# 7) Testing strategy (keeps outputs identical)

1. **Golden master**: pick a fixed candle CSV for each product + config. Persist the final selected lines and trade decisions as JSON. After refactors, assert byte‑for‑byte equality.
2. **Unit tests**: geometry utilities (line slope/intercept, projections), extrema windowing, break detection edge cases.
3. **Property‑based** (Hypothesis): random monotonic segments should produce 0 extrema; mirrored data should swap support/resistance in predictable ways.
4. **API fakes**: recorded fixtures for Coinbase endpoints to make runners deterministic.

Minimal example test:

```python
# tests/test_selection.py
import json
from data.analysis.trend_analysis import TrendAnalysis

def test_top_lines_golden(sample_candles):
    ta = TrendAnalysis(sample_candles, product_id="BTC-USD")
    support, resistance = ta.compute()
    got = json.loads((ARTIFACTS/"lines_btc.json").read_text())
    assert support == got["support"]
    assert resistance == got["resistance"]
```

---

# 8) Runners & CLI

- Replace multiple `*_runner.py` scripts with CLI commands (Typer): `cb run backtest`, `cb run debug --product BTC-USD`, `cb plot lines`.
- Keep `main.py` as tiny façade that imports the CLI. This maintains entry points but centralises logic.

---

# 9) Security & secrets

- Never commit `.env`. Load secrets with `python-dotenv` only in local dev. In code, accept `key_id`, `private_key` via env. Provide a `JWTAuth.from_env()` constructor.
- Consider support for Coinbase sandbox/staging hosts via config.

---

# 10) Bull flag module (next step, pluggable & testable)

Create `src/patterns/` with a common interface and a first detector that you can unit‑test thoroughly before wiring to live trading.

```
src/patterns/
  base.py            # PatternDetector Protocol
  bull_flag.py       # Implementation
  tests/
    test_bull_flag.py
```

`base.py`:

```python
from typing import Protocol, Iterable
from models.candle import Candle

class PatternDetector(Protocol):
    def find(self, candles: Iterable[Candle]) -> list[PatternMatch]: ...
```

`bull_flag.py` (outline, behaviour‑neutral when disabled):

```python
from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class PatternMatch:
    start: int
    end: int
    pole_height_pct: float
    channel_slope: float

class BullFlagDetector:
    def __init__(self,
                 min_pole_pct: float = 2.0,
                 max_flag_retracement_pct: float = 38.2,
                 min_flag_bars: int = 4,
                 max_flag_bars: int = 24):
        self.min_pole_pct = min_pole_pct
        self.max_flag_retracement_pct = max_flag_retracement_pct
        self.min_flag_bars = min_flag_bars
        self.max_flag_bars = max_flag_bars

    def find(self, closes: np.ndarray) -> list[PatternMatch]:
        # 1) detect impulse leg (pole)
        # 2) detect descending parallel channel (flag)
        # 3) confirm breakout above upper channel
        ...
```

Wire it into the strategy behind a feature flag (`enable_bull_flag=False`), so current behaviour is unchanged. Add exhaustive unit tests using synthetic series to nail down parameters before live use.

---

# 11) Small, concrete code nits (from this tree)

- `src/api/*`: ensure all modules export minimal `__all__` to avoid namespace leaks.
- Replace implicit `...` stubs with `NotImplementedError()` or real logic; stubs should be guarded by tests.
- `utils/logger.py`: make sound handler optional via env (`LOG_SOUNDS=0/1`), and avoid attaching multiple handlers when imported repeatedly.
- `models/scored_line.py`: avoid mutable default args (`breaks: list[int] | None = None`); initialise in `__post_init__` or set `default_factory=list`.
- `visuals/*`: move plotting helpers behind debug flag; return figure objects for tests rather than calling `plt.show()`.
- `settings/config.py`: expose a single `config = get_config()` from §2; mark as read‑only object.
- `runners/*`: arrange common argument parsing and logging boilerplate under `cli.py`.

---

# 12) Migration plan (no behaviour change)

1. **Freeze outputs**: capture current selected lines, deviations, and trade actions for a fixed historical window as golden artefacts.
2. Add test scaffolding + CI.
3. Introduce typed configs + DI interfaces (adapters return the exact same data).
4. Refactor hot loops to vectorised code; verify golden tests still pass.
5. Add logging/metrics flags and artefacts.
6. Prepare `patterns/` skeleton; keep disabled by default.

This path keeps functional outputs identical while pushing the project toward professional standards (tooling, safety, testability, and scalability).
