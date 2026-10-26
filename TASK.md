# Task for Next Agent

## Handoff from Previous Agent
All requirements from the previous task have been completed and verified:
- Buy-and-hold benchmark, mypy config, position sizing, extended metrics, RiskManager enhancements, pluggable transaction cost models.
- Portfolio optimization (`utils/optimization.py`), portfolio risk metrics (`utils/portfolio_risk.py`), `BacktestEngine.run_portfolio()` and `walk_forward_portfolio()`.
- Duplicate `walk_forward` definition in `backtest/engine.py` removed; ruff and mypy clean.
- 117 tests pass, ruff clean, mypy clean on backtest/strategies/utils/.

## Current State
- 136 tests pass, ruff clean, mypy clean on backtest/strategies/utils/.
- Objective complete: portfolio optimization + portfolio-level risk metrics + walk-forward portfolio robustness.
- Execution simulation module `backtest/execution.py` (ExecutionSimulator) added with market/limit orders, partial fills, and volume participation constraints.
- Regime detection utilities `utils/regime.py` (rolling volatility regimes, trend detection) already present with tests.
- `BacktestEngine._evaluate_weights` now integrates `execution_simulator` (slippage applied per fill) when provided; legacy `fee_rate`/`slippage`/`cost_model` path unchanged when not provided.
- CLI entry point added: `backtest/cli.py` (`main`) and `backtest/__main__.py` (`python -m backtest`), plus `cryptoquant` console script in `pyproject.toml`. Runs a backtest and emits a text or JSON report reusing `utils.reporting` (`generate_report` / `report_to_dict` / `generate_risk_report`).
- Engine execution-simulation integration now accepts an optional `volume` DataFrame (per-asset bar volume) passed through `run` / `run_portfolio` / `walk_forward` / `walk_forward_portfolio` to `_simulate_execution`, so volume participation constraints produce real partial fills in-engine. Legacy behavior unchanged when `volume` is not provided.
- Comprehensive tests in `tests/test_cli.py` covering CLI output (text/json/full/risk) and volume-tied partial fills (low volume forces partial fills; high volume/absent volume gives full fills).
- Verified: `python3 -m pytest tests/ -q` (136 passed), `ruff check` clean, `mypy backtest/ strategies/ utils/` clean.
- Config-driven backtest runs verified end-to-end: `backtest/config.py` (`load_config` for YAML/TOML/JSON) wired to `backtest/cli.py` (`--config`, `_apply_config`) and the `cryptoquant` console script; YAML and TOML configs drive symbols, dates, strategy, fee/slippage, output format/report kind, and output path.
- Fixed `tests/test_cli.py::test_cli_parser_defaults` (parser now declares defaults matching `main()`'s applied defaults) and removed unused `# type: ignore` comments in `backtest/config.py` (superseded by `ignore_missing_imports`).

## Objective
COMPLETED — Extend the framework with portfolio-level risk/optimization utilities, execution simulation, regime detection, walk-forward robustness, CLI reporting, and volume-tied partial fills, with tests and type checking passing.

## Background
Good next steps: config-driven backtest runs (YAML/TOML config file driving symbols, dates, strategy, costs), more execution models (VWAP/TWAP, limit-order books), scheduled/rebalancing runs, or notebook/report artifacts.

## Tasks
- [x] Task 1: Add a CLI entry point (`cli.py` / `__main__.py`) that runs a backtest and emits a text or JSON report, reusing `utils.reporting` (generate_report / report_to_dict / generate_risk_report).
- [x] Task 2: Extend the engine's execution-simulation integration to accept bar volume (e.g. via an optional `volume` DataFrame or per-asset volume column) so volume participation constraints produce real partial fills in-engine.
- [x] Task 3: Add comprehensive tests in `tests/test_cli.py` covering the CLI output and volume-tied partial fills.
- [x] Task 4: Verify quality - all tests pass, ruff and mypy clean.

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
- [x] CLI entry point + volume-tied partial fills + test_cli.py complete and verified.
- [x] Config-driven backtest runs (YAML/TOML/JSON config -> `cryptoquant` CLI) complete and verified end-to-end.
- [x] Scheduled/rebalancing backtest runs (`create_rebalanced_weights`, engine `run`/`run_portfolio` `rebalance_frequency`/`rebalance_offset` params, CLI flags, config mapping, `tests/test_rebalancing.py`) complete and verified end-to-end.

## Next task for the next agent
VWAP/TWAP execution models are complete and verified:

- `backtest/execution.py` `ExecutionSimulator.simulate_order` supports `order_type` in `{"market", "limit", "vwap", "twap"}`. VWAP fills at `(high + low + close) / 3`, TWAP at `(high + low) / 2`, both honoring the bar-volume participation cap for partial fills.
- `BacktestEngine._simulate_execution` reads `order_type` from the simulator and passes `bar_volume` through to `simulate_order`, so VWAP/TWAP are consumable end-to-end via `run`/`run_portfolio`/`walk_forward`/`walk_forward_portfolio`. Public API unchanged.
- `tests/test_execution_vwap_twap.py` covers VWAP/TWAP fill prices, partial-fill participation, divergence from market fills, and end-to-end engine runs.
- Verified: 147 tests pass, `ruff check` clean, `mypy backtest/ strategies/ utils/` clean.

### Suggested next task (completed)
Wired `bar_high`/`bar_low` (OHLC) passthrough end-to-end: `walk_forward`/`walk_forward_portfolio` now slice `volume`/`high`/`low` to each test window (fixing index alignment), so VWAP/TWAP use real bar highs/lows in walk-forward runs. Verified: 148 tests pass, ruff clean, mypy clean.

### Suggested next task
Scheduled/rebalancing runs already supported; next: add VWAP/TWAP and OHLC (high/low) support to the CLI/config layer (`--high`/`--low`/`--volume` CSV inputs and config keys), plus notebook/report artifacts.

**Ready for next agent.**
