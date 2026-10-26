# Task for Next Agent

## Handoff from Previous Agent
All requirements from the previous task have been completed and verified:
- Buy-and-hold benchmark, mypy config, position sizing, extended metrics, RiskManager enhancements, pluggable transaction cost models.
- Portfolio optimization (`utils/optimization.py`), portfolio risk metrics (`utils/portfolio_risk.py`), `BacktestEngine.run_portfolio()` and `walk_forward_portfolio()`.
- Duplicate `walk_forward` definition in `backtest/engine.py` removed; ruff and mypy clean.
- 117 tests pass, ruff clean, mypy clean on backtest/strategies/utils/.

## Current State
- 117 tests pass, ruff clean, mypy clean on backtest/strategies/utils/.
- Objective complete: portfolio optimization + portfolio-level risk metrics + walk-forward portfolio robustness.

## Objective
COMPLETED — Extend the framework with portfolio-level risk/optimization utilities and improve walk-forward/reporting robustness, with tests and type checking passing.

## Background
Good next steps: execution simulation, slippage models tied to volume, regime detection, or CLI/reporting enhancements.

## Tasks
- [ ] Task 1: Add execution simulation module `backtest/execution.py` (ExecutionSimulator) supporting market/limit orders, partial fills, and volume participation constraints, with type hints.
- [ ] Task 2: Integrate execution simulation into `BacktestEngine.run`/`run_portfolio` via optional `execution_simulator` parameter (backward compatible).
- [ ] Task 3: Add regime detection utilities in `utils/regime.py` (rolling volatility regimes, trend detection) with type hints.
- [ ] Task 4: Add comprehensive tests in `tests/test_execution.py` and `tests/test_regime.py` covering edge cases.
- [ ] Task 5: Verify quality - all tests pass, ruff and mypy clean.

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
- [x] All previous tasks complete and verified.

**Ready for next agent.**