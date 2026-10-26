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
- 75 tests pass, ruff clean, mypy clean on backtest/strategies/utils/.

## Objective
Extend the framework with portfolio-level risk/optimization utilities and improve walk-forward/reporting robustness, with tests and type checking passing.

## Background
The framework has backtesting, strategies, metrics, risk management, position sizing, and pluggable transaction costs. Good next steps: portfolio optimization (e.g., mean-variance / minimum variance / risk parity helpers), portfolio-level risk metrics (e.g., portfolio VaR/CVaR, correlation-based risk, drawdown analysis), walk-forward/reporting enhancements (e.g., summary statistics aggregation), and broader test coverage for edge cases.

## Tasks
- [ ] Task 1: Add portfolio optimization utilities in `utils/optimization.py` (e.g., `equal_weight`, `inverse_volatility`, `min_variance_weights`, `mean_variance_weights`, `risk_parity_weights`) with input validation and type hints.
- [ ] Task 2: Add portfolio risk metrics in `utils/portfolio_risk.py` (e.g., `portfolio_var`, `portfolio_cvar`, `conditional_drawdown_at_risk`, `marginal_var`, `component_var`) returning floats/series as appropriate.
- [ ] Task 3: Enhance `BacktestEngine` to support portfolio-level analysis helpers or accept portfolio weights constructor/utility integration (backward compatible). If helpful, add a method like `run_portfolio()` or just ensure compatibility.
- [ ] Task 4: Add comprehensive tests in `tests/test_optimization.py` and `tests/test_portfolio_risk.py` covering edge cases (NaN/empty/single asset).
- [ ] Task 5: Verify quality - all tests pass, ruff and mypy clean on backtest/strategies/utils/.

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

(End of file - total 65 lines)
