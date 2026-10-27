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
- [x] VWAP/TWAP execution models complete and verified.
- [x] OHLC (high/low) passthrough end-to-end for walk-forward VWAP/TWAP.
- [x] VWAP/TWAP + OHLC wired through CLI/config layer (`--volume-csv`/`--high-csv`/`--low-csv`, `--order-type`).
- [x] Jupyter notebooks in `notebooks/`: `vwap_twap_execution.ipynb`, `walk_forward_analysis.ipynb`, `portfolio_optimization.ipynb`, `quickstart_report.ipynb`.
- [x] HTML/PDF report artifact generation from CLI (`--output html|pdf`, `--title`, `--output-path`); PDF defaults to `reports/` when no path given.
- [x] **PDF report layout refined**: tighter spacing (`pad_inches=0.4`), sans-serif fonts, weights rendered as a bar chart, trades rendered as a matplotlib table paginated across multiple pages (50 rows/page). Verified end-to-end; `notebooks/quickstart_report.ipynb` updated to demonstrate.

### Latest task (completed)
Refined PDF report layout in `utils/reporting.py::generate_pdf_report`:
- Page 1 (metrics): tighter `pad_inches=0.4`, sans-serif font, `linespacing=1.15`.
- Page 2 (equity/drawdown): smaller tick labels, `pad=1.2`.
- Page 3 (weights): bar chart with positive/negative colors, value labels, zero baseline.
- Page 4 (trades): matplotlib `ax.table` with headers, centered cells, header shading; multi-page for long trade lists (50 rows/page).

Tests added in `tests/test_reporting.py`:
- `test_generate_pdf_report_multi_page_trades` (120 trades -> multiple pages)
- `test_generate_pdf_report_weights_bar_chart`
- `test_generate_pdf_report_tighter_layout`

Verified: 165 tests pass, `ruff check` clean, `mypy backtest/ strategies/ utils/` clean.

## Next task for the next agent
VWAP/TWAP execution models are complete and verified:

- `backtest/execution.py` `ExecutionSimulator.simulate_order` supports `order_type` in `{"market", "limit", "vwap", "twap"}`. VWAP fills at `(high + low + close) / 3`, TWAP at `(high + low) / 2`, both honoring the bar-volume participation cap for partial fills.
- `BacktestEngine._simulate_execution` reads `order_type` from the simulator and passes `bar_volume` through to `simulate_order`, so VWAP/TWAP are consumable end-to-end via `run`/`run_portfolio`/`walk_forward`/`walk_forward_portfolio`. Public API unchanged.
- `tests/test_execution_vwap_twap.py` covers VWAP/TWAP fill prices, partial-fill participation, divergence from market fills, and end-to-end engine runs.
- Verified: 147 tests pass, `ruff check` clean, `mypy backtest/ strategies/ utils/` clean.

### Suggested next task (completed)
Wired `bar_high`/`bar_low` (OHLC) passthrough end-to-end: `walk_forward`/`walk_forward_portfolio` now slice `volume`/`high`/`low` to each test window (fixing index alignment), so VWAP/TWAP use real bar highs/lows in walk-forward runs. Verified: 148 tests pass, ruff clean, mypy clean.

### Suggested next task (completed)
VWAP/TWAP and OHLC (high/low) support added to the CLI/config layer: `--volume-csv`/`--high-csv`/`--low-csv` flags and config keys wired end-to-end through `backtest/cli.py` to `BacktestEngine.run`/`run_portfolio`/`walk_forward`/`walk_forward_portfolio`. Tests in `tests/test_cli.py` (`test_cli_vwap_order_type_runs`, `test_cli_twap_order_type_runs`, `test_cli_high_low_csv_drives_vwap_fills`, `test_cli_config_drives_vwap_and_ohlc`) cover the CLI path. Verified: 152 tests pass, ruff clean, mypy clean.

### Suggested next task (completed)
Created Jupyter notebooks in `notebooks/`: `vwap_twap_execution.ipynb`, `walk_forward_analysis.ipynb`, `portfolio_optimization.ipynb`.

### Suggested next task (completed)
Add optional HTML/PDF report artifact generation from CLI backtest results (e.g. `--output html` / `--output pdf` leveraging `utils.reporting`), plus notebook/report artifact storage under `reports/`.

### Suggested next task (completed)
Created Jupyter notebooks in `notebooks/`: `quickstart_report.ipynb` added to demonstrate HTML/PDF report generation.

### Latest task (completed)
Added GitHub Actions CI workflow `.github/workflows/ci.yml`:
- Triggers on `push` and `pull_request` for all branches.
- Three jobs: `lint` (ruff), `typecheck` (mypy), `test` (pytest matrixed on Python 3.10/3.11/3.12).
- Installs dependencies via `pip install -e ".[dev]"`.

Verified: 180 tests pass, `ruff check` clean, `mypy backtest/ strategies/ utils/` clean, workflow YAML valid.

### Latest task (completed)
Enhanced the LOB execution model with per-level liquidity and queue position effects (`backtest/execution.py` `LimitOrderBookExecution` / `_simulate_lob` / `ExecutionSimulator`):
- `level_liquidity` (per-level quantities) and `queue_position` (fraction 0-1) fields on `LimitOrderBookExecution` and `lob_level_liquidity` / `lob_queue_position` on `ExecutionSimulator`, passed through cleanly.
- `_simulate_lob` consumes liquidity level-by-level up to `depth_levels`, applying `market_impact_bps` per level walked; queue position reduces the fillable portion at the first level.
- Falls back to the volume-proxy logic when `level_liquidity` is not provided (backward compatible).
- Tests in `tests/test_execution_lob_enhanced.py` cover per-level liquidity enforcement, multi-level consumption, queue position reductions, and backward compatibility.

Verified: 201 tests pass (1 skipped), `ruff check` clean, `mypy backtest/ strategies/ utils/` clean.

### Latest task (completed)
Regime detection integration with the backtest engine:
- `backtest/engine.py`: `_apply_regime_gating` gates weights by `regime_signal` (boolean Series/DataFrame/scalar) or `regime_mode="trend"` (detected trend regimes) across `run`/`run_portfolio`/`walk_forward`/`walk_forward_portfolio`.
- `backtest/cli.py`: `--regime-mode` and `--regime-lookback` flags wired through all engine paths.
- `backtest/config.py`: `regime_mode`/`regime_lookback` config keys mapped in `_apply_config`.
- `tests/test_regime_integration.py`: 10 tests covering regime gating of signals, no-op when disabled, scalar/DataFrame/Series regime_signal, trend-mode on flat vs trending data, run_portfolio, walk_forward, walk_forward_portfolio, and backward compatibility.
- Verified: 211 tests pass (1 skipped), `ruff check` clean, `mypy backtest/ strategies/ utils/` clean.

### Latest task (completed)
Extended regime-aware gating to support volatility-based regimes:
- `BacktestEngine.run`/`run_portfolio`/`walk_forward`/`walk_forward_portfolio` accept `regime_vol_mode` (e.g. `"low_vol"`) gating trading to low-volatility regimes via `utils.regime.volatility_regime` (already present in `_apply_regime_gating`).
- CLI: added `--regime-vol-mode` flag to `backtest/cli.py` `build_parser()`; already wired through `main()` and `_apply_config` config mapping (`regime_vol_mode` / `regimeVolMode`).
- Config layer: `regime_vol_mode`/`regimeVolMode` already mapped in `backtest/cli.py::_apply_config`.
- Tests added in `tests/test_regime_integration.py`:
  - `test_regime_vol_mode_low_vol_gates_weights` (low-vol gating zeros high-vol periods)
  - `test_regime_vol_mode_combined_with_trend` (trend + vol combined gating)
  - `test_regime_vol_mode_none_backward_compatible` (None matches legacy behavior)
- Verified: 214 tests pass (1 skipped), `ruff check` clean, `mypy backtest/ strategies/ utils/` clean.

### Latest task (completed)
Config schema validation for config-driven backtest runs:
- `backtest/config.py`: added `ConfigValidationError`, `CONFIG_SCHEMA` (every CLI key + alias with type/choice/range validators), and `validate_config(config)` that collects all errors and raises a single `ConfigValidationError`.
- `backtest/cli.py`: `_apply_config` now calls `validate_config` on the loaded dict and surfaces errors via `parser.error` (exit code 2) instead of silently ignoring unknown keys or bad values.
- `tests/test_config_validation.py`: 21 tests covering valid dicts, camelCase/snake aliases, unknown keys, wrong types, out-of-range numerics (incl. bool-as-numeric rejection), invalid enum choices, non-dict input, and CLI integration paths.
- Verified: 235 tests pass (1 skipped), `ruff check` clean, `mypy backtest/ strategies/ utils/` clean.

**Ready for next agent.**
