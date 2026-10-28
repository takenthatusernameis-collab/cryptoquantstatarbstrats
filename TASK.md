# Task for Next Agent

## Handoff from Previous Agent
All assigned tasks from the task chain are complete and verified:
- Walk-forward enhancements: IS/OOS comparison, bootstrap confidence intervals, cost-model sensitivity sweeps, multi-horizon walk-forward, live/paper trading integration, strategy benchmark registry, walk-forward report comparison dashboard.
- Strategy benchmark registry UI/dashboard complete.
- Paper-trading execution integration: order management, position tracking, risk controls, real-time monitoring and alerts.
- Paper trading session reporting & artifact persistence: `backtest/paper_report.py`, `paper-trade` artifact persistence, `paper-report` CLI subcommand, tests in `tests/test_paper_trading_report.py`.
- PDF rendering fallback fixed: `generate_pdf_report` and `generate_walk_forward_pdf_report` write valid non-empty `.pdf` files even when matplotlib is unavailable.
- `cryptoquant sweep` CLI subcommand: out-of-sample parameter grid search with walk-forward validation.
- Sweep API extracted to `backtest/sweep.py` with programmatic `run_parameter_sweep`, CLI refactored to use it, API tests added, example added.

## Current State
- `python3 -m pytest tests/ -q` -> 432 passed, 1 skipped, 0 failed
- `python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/` -> clean
- `python3 -m mypy backtest/ strategies/ utils/` -> no issues (30 source files)
- Working tree clean, branch up to date with origin/main.

## Objective
COMPLETED - No pending task from the task chain.

## Next Agent Task (suggested)

Enhance `backtest/sweep.py` API with better validation, serialization safety, and progress reporting so programmatic users can rely on it robustly.

Scope:
- Improve input validation in `run_parameter_sweep`: validate `train_period`/`test_period` > 0, handle missing/empty `grid` values more clearly, validate `metric` against allowed set with clear errors (already partially done; make consistent).
- Add support for passing `strategy_kwargs` or allow strategy factory/callable to be passed (e.g. `strategy_factory(combo) -> Strategy`) in addition to class/instance, to avoid mutating instances; update tests accordingly if needed.
- Make returned rows JSON-serializable by default (convert numpy scalars to Python types) without losing precision where reasonable; ensure `oos_returns` not leaked in public API (already popped) and floats are native Python types.
- Add optional `progress_callback(completed, total, current_combo, row)` and/or `show_progress: bool = False` for long sweeps.
- Add `tests/test_sweep_api_enhanced.py` covering factory pattern, validation errors (bad periods/metric), JSON serializability, and progress callback.
- Update `examples/sweep_api.py` to show factory usage.
- Keep `ruff`, `mypy`, and the full test suite clean.

Verification:
```bash
python3 -m pytest tests/ -q
python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python3 -m mypy backtest/ strategies/ utils/
```
