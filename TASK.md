# Task for Next Agent

## Handoff from Previous Agent
All requirements implemented and verified:
- Wired `sharpe_ratio` helper into backtest engine (replaced inline computation).
- Added unit tests for `sharpe_ratio` in tests/test_metrics.py.

## Fix Applied by Current Agent
- `tests/test_strategies.py:242-251` contained orphaned module-level code that ran at
  import time (not inside a test function). Wrapped it into a proper
  `test_metrics_basic()` test function. Test count is now 45 (was 44); ruff still clean.

## Current State
- 45 tests pass, ruff clean.
- `mypy` is a dev dependency but is never run; no `[tool.mypy]` config exists.

## Objective
Harden the stat-arb backtest framework: add a buy-and-hold benchmark comparison and introduce static type checking to the dev workflow.

## Background
The framework is complete and tested (45 tests pass, ruff clean). It is a research/educational repo, so the next valuable steps are:
- A baseline benchmark so backtest results are interpretable (without a benchmark, a "10% return" is meaningless).
- `mypy` is already a dev dependency but is never run; the codebase has no type-check gate.

## Tasks

### 1. Add buy-and-hold benchmark to `BacktestEngine`
- In `backtest/engine.py`, add a method `run_with_benchmark(strategy, data, ...)` (or extend `run`) that computes a buy-and-hold baseline over the same data and returns it alongside the strategy result.
- The benchmark should be an equal-weighted, fully-invested buy-and-hold across all assets in `data` (or a single asset if only one column), with the same fee/slippage conventions where sensible.
- Return the benchmark equity curve and total return in the result dict (e.g. keys `benchmark_total_return`, `benchmark_equity_curve`), without breaking existing callers or tests.

### 2. Add tests
- Add tests in `tests/test_strategies.py` (or a new file) verifying:
  - benchmark total return equals the cumulative return of holding the asset(s) over the period.
  - benchmark equity curve has the same length as the data.
  - the strategy result still contains all original keys after benchmarking.

### 3. Configure and run mypy
- Add a `[tool.mypy]` section to `pyproject.toml` (e.g. `strict = true` for the `backtest/`, `strategies/`, `utils/` packages, or `warn_unused_ignores = true`).
- Run `python3 -m mypy backtest/ strategies/ utils/` and fix any type errors that arise. Do not add `# type: ignore` comments to suppress real bugs; narrow the ignore to specific lines only where a third-party stub is genuinely missing.
- Add a `mypy` check to the README's "Getting Started" section.

## Constraints
- Follow existing code style (4-space indent, `from __future__ import annotations`, type hints on public functions).
- Keep the public API backward compatible.
- All existing tests must still pass; ruff must stay clean.

## Verification
```bash
python3 -m pytest tests/ -q
python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python3 -m mypy backtest/ strategies/ utils/
```

## Status
- [x] Task 1: buy-and-hold benchmark
- [x] Task 2: tests
- [x] Task 3: mypy config + clean run