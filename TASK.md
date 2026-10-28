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
- `python3 -m pytest tests/ -q` -> 443 passed, 1 skipped, 0 failed
- `python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/` -> clean
- `python3 -m mypy backtest/ strategies/ utils/` -> no issues (31 source files)
- Working tree clean, branch up to date with origin/main.

## Objective
COMPLETED - `backtest/sweep.py` API enhanced (validation, strategy factory/`strategy_kwargs`, JSON-serializable rows, progress callback); `tests/test_sweep_api_enhanced.py` added; `examples/sweep_api.py` updated with factory usage.

## Next Agent Task (suggested)

Add walk-forward `mode` ("rolling" | "expanding") and `n_splits`/anchoring control to `run_parameter_sweep` in `backtest/sweep.py`, exposed through the CLI (`cryptoquant sweep`).

Scope:
- Thread a `mode` parameter through `run_parameter_sweep` to `engine.walk_forward(mode=...)` ("rolling" default, "expanding" optional).
- Add `n_splits` to cap the number of walk-forward windows evaluated per combo (useful for long sweeps).
- Add CLI flags `--mode` and `--n-splits` to `cryptoquant sweep`.
- Add tests in `tests/test_sweep_api_enhanced.py` covering expanding mode, n_splits cap, and CLI flag propagation.
- Keep `ruff`, `mypy`, and the full test suite clean.

Verification:
```bash
python3 -m pytest tests/ -q
python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python3 -m mypy backtest/ strategies/ utils/
```
