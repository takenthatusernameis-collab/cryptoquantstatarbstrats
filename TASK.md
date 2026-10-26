# Task for Next Agent

## Handoff from Previous Agent
All requirements from the previous task have been completed and verified:
- Buy-and-hold benchmark, mypy config, position sizing, extended metrics, RiskManager enhancements, pluggable transaction cost models.
- Portfolio optimization (`utils/optimization.py`), portfolio risk metrics (`utils/portfolio_risk.py`), `BacktestEngine.run_portfolio()` and `walk_forward_portfolio()`.
- Duplicate `walk_forward` definition in `backtest/engine.py` removed; ruff and mypy clean.
- 117 tests pass, ruff clean, mypy clean on backtest/strategies/utils/.

## Current State
- 128 tests pass, ruff clean, mypy clean on backtest/strategies/utils/.
- Objective complete: portfolio optimization + portfolio-level risk metrics + walk-forward portfolio robustness.
- Execution simulation module `backtest/execution.py` (ExecutionSimulator) added with market/limit orders, partial fills, and volume participation constraints.
- Regime detection utilities `utils/regime.py` (rolling volatility regimes, trend detection) already present with tests.
- `BacktestEngine._evaluate_weights` now integrates `execution_simulator` (slippage applied per fill) when provided; legacy `fee_rate`/`slippage`/`cost_model` path unchanged when not provided.

## Objective
COMPLETED — Extend the framework with portfolio-level risk/optimization utilities, execution simulation, regime detection, and walk-forward robustness, with tests and type checking passing.

## Background
Good next steps: CLI/reporting enhancements, volume-tied slippage (partial fills driven by bar volume in the engine), more execution models, or config-driven backtest runs.

## Tasks
- [ ] Task 1: Add a CLI entry point (`cli.py` / `__main__.py`) that runs a backtest and emits a text or JSON report, reusing `utils.reporting` (generate_report / report_to_dict / generate_risk_report).
- [ ] Task 2: Extend the engine's execution-simulation integration to accept bar volume (e.g. via an optional `volume` DataFrame or per-asset volume column) so volume participation constraints produce real partial fills in-engine.
- [ ] Task 3: Add comprehensive tests in `tests/test_cli.py` covering the CLI output and volume-tied partial fills.
- [ ] Task 4: Verify quality - all tests pass, ruff and mypy clean.

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
- [x] Execution simulation module + engine integration + tests complete.

**Ready for next agent.**
