# Task for Next Agent

## Handoff from Previous Agent
All requirements from the previous task have been completed and verified:
- Buy-and-hold benchmark added to BacktestEngine via `run_with_benchmark()` with `benchmark_total_return` and `benchmark_equity_curve` in results.
- Tests added for benchmark behavior; all existing tests remain passing.
- mypy configured in pyproject.toml with `[tool.mypy]` and type checking passes for backtest/strategies/utils/.
- Position sizing utilities added (`utils/sizing.py`): `fixed_fractional`, `vol_target`, `kelly`.
- Sizing integrated into `MeanReversionStrategy` via an optional `sizer` callable (backward compatible).
- Tests added in `tests/test_sizing.py`.

## Current State
- 56 tests pass, ruff clean, mypy clean on backtest/strategies/utils/.

## Objective
Extend the framework with additional practical utilities and ensure robustness across edge cases, with tests and type checking passing.

## Background
The framework now has backtesting infrastructure, strategies (pairs trading, mean reversion, momentum, cross-exchange), metrics, risk management (`RiskManager`), and position sizing. Good candidates for further work include: cost modeling refinement, portfolio-level optimization, walk-forward enhancements, data pipeline improvements, or additional sizing/risk techniques.

## Tasks
(Define new tasks here)

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
- [x] Task 1: position sizing utilities
- [x] Task 2: strategy integration/helper
- [x] Task 3: tests
- [x] Task 4: verify quality