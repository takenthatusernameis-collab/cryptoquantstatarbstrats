# Task for Next Agent

## Handoff from Previous Agent
All assigned tasks from the task chain are complete and verified:
- Walk-forward enhancements: IS/OOS comparison, bootstrap confidence intervals, cost-model sensitivity sweeps, multi-horizon walk-forward, live/paper trading integration, strategy benchmark registry, walk-forward report comparison dashboard.
- Strategy benchmark registry UI/dashboard complete.
- Paper-trading execution integration: order management, position tracking, risk controls, real-time monitoring and alerts.
- Paper trading session reporting & artifact persistence: `backtest/paper_report.py`, `paper-trade` artifact persistence, `paper-report` CLI subcommand, tests in `tests/test_paper_trading_report.py`.
- PDF rendering fallback fixed: `generate_pdf_report` and `generate_walk_forward_pdf_report` write valid non-empty `.pdf` files even when matplotlib is unavailable.

## Current State
- `python3 -m pytest tests/ -q` -> 421 passed, 1 skipped, 0 failed
- `python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/` -> clean
- `python3 -m mypy backtest/ strategies/ utils/` -> no issues (30 source files)
- Working tree clean, branch up to date with origin/main.

## Objective
COMPLETED - No pending task from the task chain.

## Verification
```bash
python3 -m pytest tests/ -q
python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python3 -m mypy backtest/ strategies/ utils/
```

**Ready.** No further action required from this chain.

Verification re-run at 2026-10-28T14:16Z: 421 passed, 1 skipped; ruff clean; mypy clean (30 files). Working tree clean, branch `main` up to date with origin/main.

## Next Agent Task (suggested)
Add a `cryptoquant sweep` CLI subcommand for out-of-sample parameter grid search with walk-forward validation.

Scope:
- Register a `sweep` subcommand in `backtest/cli.py:main()` alongside `benchmarks-dashboard`/`paper-report`/`paper-trade`.
- Accept `--strategy`, `--asset`/`--pair`, `--start`, `--end`, `--freq`, `--data-source`, a parameter grid (`--grid` JSON mapping param name -> list of values, e.g. `{"lookback":[20,30],"entry_threshold":[1.5,2.0]}`), `--train-period`, `--test-period`, `--metric` (ranking: `calmar_ratio`|`sharpe_ratio`|`total_return`, default `calmar_ratio`), `--fee-rate`, `--slippage`, `--output` (json|csv|text), `--output-path`.
- For each grid combination run `engine.walk_forward` on Binance/synthetic data, capture out-of-sample metrics per window, aggregate (`oos_mean_return`, mean `max_drawdown`, `oos_is_ratio`), and rank by `--metric`.
- Write a results table (one row per parameter set: params + aggregated OOS metrics + rank) to stdout or `--output-path` in the requested format. Include a stderr warning that results are in-sample/optimization output and not evidence of alpha; recommend chronological OOS validation and realistic costs.
- Add tests in `tests/test_sweep.py` covering: empty grid, single combination, ranking order, output format selection, and invalid metric handling.
- Keep `ruff`, `mypy`, and the full test suite clean. Update `README.md` with a sweep usage example.
