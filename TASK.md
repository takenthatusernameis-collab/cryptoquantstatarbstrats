# Task for Next Agent

## Handoff from Previous Agent
All assigned tasks from the task chain are complete and verified:
- Walk-forward enhancements: IS/OOS comparison, bootstrap confidence intervals, cost-model sensitivity sweeps, multi-horizon walk-forward, live/paper trading integration, strategy benchmark registry, walk-forward report comparison dashboard.
- Strategy benchmark registry UI/dashboard complete.
- Paper-trading execution integration: order management, position tracking, risk controls, real-time monitoring and alerts.
- Paper trading session reporting & artifact persistence: `backtest/paper_report.py`, `paper-trade` artifact persistence, `paper-report` CLI subcommand, tests in `tests/test_paper_trading_report.py`.
- PDF rendering fallback fixed: `generate_pdf_report` and `generate_walk_forward_pdf_report` write valid non-empty `.pdf` files even when matplotlib is unavailable.
- `cryptoquant sweep` CLI subcommand: out-of-sample parameter grid search with walk-forward validation.

## Current State
- `python3 -m pytest tests/ -q` -> 427 passed, 1 skipped, 0 failed
- `python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/` -> clean
- `python3 -m mypy backtest/ strategies/ utils/` -> no issues (30 source files)
- Working tree clean, branch up to date with origin/main.

## Objective
COMPLETED - No pending task from the task chain.

## Next Agent Task (suggested)

Extract the `cryptoquant sweep` grid-search/walk-forward logic out of `backtest/cli.py` into a reusable Python API module so it is callable programmatically (not just via the CLI).

Scope:
- Create `backtest/sweep.py` (or `utils/sweep.py`) exposing a function such as `run_parameter_sweep(strategy, data, grid, train_period, test_period, fee_rate, slippage, metric) -> list[dict]` that performs per-combo walk-forward runs, OOS aggregation (`oos_mean_return`, `mean_max_drawdown`, `oos_is_ratio`, `oos_periods`), ranking by `--metric`, and returns ranked rows.
- Refactor `backtest/cli.py:main()` sweep branch (lines 566-714) to call the new module instead of inline logic; keep CLI behavior, output formats (json/csv/text), `--output-path`, and the stderr alpha-warning unchanged.
- Add unit tests in `tests/test_sweep_api.py` covering: empty grid, single combination, ranking order, invalid metric, and deterministic output; keep the existing `tests/test_sweep.py` CLI tests passing.
- Keep `ruff`, `mypy`, and the full test suite clean. Add an example script (e.g. `examples/sweep_api.py`) demonstrating programmatic usage.
- Update `README.md` sweep section to mention the programmatic API alongside the CLI example.

Verification:
```bash
python3 -m pytest tests/ -q
python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python3 -m mypy backtest/ strategies/ utils/
```