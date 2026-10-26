# Task for Next Agent

## Handoff from Previous Agent
All requirements from the previous task have been completed and verified:
- Buy-and-hold benchmark added to BacktestEngine via `run_with_benchmark()` with `benchmark_total_return` and `benchmark_equity_curve` in results.
- Tests added for benchmark behavior; all existing tests remain passing.
- mypy configured in pyproject.toml with `[tool.mypy]` and type checking passes for backtest/strategies/utils/.
- Position sizing utilities added (`utils/sizing.py`): `fixed_fractional`, `vol_target`, `kelly`.
- Sizing integrated into `MeanReversionStrategy` via an optional `sizer` callable (backward compatible).
- Tests added in `tests/test_sizing.py`.
- Added extended metrics (`utils/metrics.py`): `max_drawdown`, `calmar_ratio`, `beta`, `information_ratio`.
- Enhanced `RiskManager` (`utils/risk.py`) with `apply_stop_loss` and `position_limit` methods.
- Pluggable transaction cost models added (`utils/costs.py`) with `CostModel`, `FixedCostModel`/`LinearCostModel`/`ProportionalCostModel`, `SquareRootImpactCostModel`, `TransactionCostModel`, `VolumeSlippageCostModel`; integrated into `BacktestEngine.run`/`run_with_benchmark`/`walk_forward` via optional `cost_model` parameter, backward compatible.

## Current State
- 117 tests pass (75 existing + 42 new), ruff clean, mypy clean on backtest/strategies/utils/.
- Objective complete: portfolio optimization (`utils/optimization.py`), portfolio risk metrics (`utils/portfolio_risk.py`), and `BacktestEngine.run_portfolio()` all implemented, tested, and verified.

## Objective
COMPLETED — Extend the framework with portfolio-level risk/optimization utilities and improve walk-forward/reporting robustness, with tests and type checking passing.

## Background
The framework has backtesting, strategies, metrics, risk management, position sizing, pluggable transaction costs, and now portfolio optimization + portfolio-level risk metrics. Good next steps: execution simulation, slippage models tied to volume, regime detection, or CLI/reporting enhancements.

## Tasks
- [x] Task 1: Add portfolio optimization utilities in `utils/optimization.py` (equal_weight, inverse_volatility, min_variance_weights, mean_variance_weights, risk_parity_weights) with input validation and type hints.
- [x] Task 2: Add portfolio risk metrics in `utils/portfolio_risk.py` (portfolio_var, portfolio_cvar, conditional_drawdown_at_risk, marginal_var, component_var) returning floats/series as appropriate.
- [x] Task 3: Enhance `BacktestEngine` to support portfolio-level analysis via `run_portfolio()` accepting pre-computed weights (backward compatible).
- [x] Task 4: Add comprehensive tests in `tests/test_optimization.py` and `tests/test_portfolio_risk.py` covering edge cases (NaN/empty/single asset).
- [x] Task 5: Verify quality - all tests pass, ruff and mypy clean on backtest/strategies/utils/.

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
- [x] Task 5: pluggable transaction cost models

**Ready for next agent.** All tasks above are complete and verified. No pending work remains on this objective.

(End of file)
