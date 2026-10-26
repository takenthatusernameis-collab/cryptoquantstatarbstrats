# Task for Next Agent

## Handoff from Previous Agent
All requirements from the previous task have been completed and verified:
- Buy-and-hold benchmark added to BacktestEngine via `run_with_benchmark()` with `benchmark_total_return` and `benchmark_equity_curve` in results.
- Tests added for benchmark behavior; all existing tests remain passing.
- mypy configured in pyproject.toml with `[tool.mypy]` and type checking passes for backtest/strategies/utils/.

## Current State
- 45 tests pass, ruff clean, mypy clean on backtest/strategies/utils/.

## Objective
Extend the framework with position sizing/risk management utilities and integrate them into strategies, with tests and type checking passing.

## Background
The framework has solid backtesting infrastructure, strategies (pairs trading, mean reversion, momentum), and metrics. Adding configurable position sizing (e.g., fixed fractional, volatility targeting/ATR-based sizing, Kelly criterion) would make it more practical. These utilities should be well-tested and integrated cleanly.

## Tasks

### 1. Add position sizing utilities
- Create `utils/sizing.py` with functions:
  - `fixed_fractional(equity, risk_fraction)` returning position size/capital allocation
  - `vol_target(equity, target_vol, realized_vol, lookback=None)` for volatility targeting
  - `kelly(fractional_edge, win_prob, win_loss_ratio)` returning Kelly fraction
- All functions must have type hints, docstrings, and handle edge cases (zeros, invalid inputs) reasonably.

### 2. Integrate into strategies (or provide helper)
- Add support to apply sizing in at least one strategy (e.g., `strategies/mean_reversion.py` or create a sizing-aware wrapper). Keep changes backward compatible.
- Alternatively add a mixin/helper that strategies can use; document usage in docstrings.

### 3. Add tests
- Add tests in `tests/test_sizing.py` covering the utilities and at least one integration case.
- Ensure all existing tests still pass.

### 4. Verify quality
- Run `python3 -m pytest tests/ -q`
- Run `python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/`
- Run `python3 -m mypy backtest/ strategies/ utils/`

## Constraints
- Follow existing code style (4-space indent, `from __future__ import annotations`, type hints on public functions).
- Keep public API backward compatible.
- All existing tests must still pass; ruff and mypy must remain clean.
- Do not add `# type: ignore` to suppress real bugs.

## Verification
```bash
python3 -m pytest tests/ -q
python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python3 -m mypy backtest/ strategies/ utils/
```

## Status
- [ ] Task 1: position sizing utilities
- [ ] Task 2: strategy integration/helper
- [ ] Task 3: tests
- [ ] Task 4: verify quality
