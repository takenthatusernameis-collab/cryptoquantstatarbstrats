# Task for Next Agent

## Context
All four suggested tasks from the previous round are complete and verified:
1. `--benchmark` CLI flag added to `backtest/cli.py`; equal-weighted buy-and-hold benchmark equity curve computed and exposed as `benchmark_equity_curve` / `benchmark_total_return` on the result; rendered as a dashed green line in `generate_html_report` (SVG) and `generate_pdf_report` (equity page).
2. `generate_walk_forward_report` utility added to `utils/reporting.py`, aggregating per-window walk-forward results into a summary `DataFrame` + chained `equity_curve` Series, copying `mean_return`/`std_return`/`positive_periods`/`total_periods` aggregates.
3. Notebook `notebooks/walk_forward_portfolio_report.ipynb` added: runs `walk_forward_portfolio`, aggregates via `generate_walk_forward_report`, renders per-window + chained equity curves, saves summary/equity CSVs under `reports/`.
4. PDF trade cell text tests added to `tests/test_reporting.py` using pypdf (extracts "BUY"/"SELL"/prices from the trade table page), skipped when pypdf unavailable.

Verification: `python3 -m pytest tests/ -q` -> 174 passed; `ruff check` clean; `mypy backtest/ strategies/ utils/` clean.

## Suggested Tasks
1. Add a `--rebalance-benchmark` variant so the benchmark is also computed for the `run_portfolio`/`walk_forward_portfolio` path (currently benchmark only applies to the strategy `run` path).
2. Add a `generate_walk_forward_report` HTML/PDF renderer in `utils/reporting.py` (summary table + equity chart pages).
3. Add CLI flag `--walk-forward-report` to emit a walk-forward summary artifact (csv/html/pdf).
4. Add unit tests for `generate_walk_forward_report` edge cases (single window, missing equity_curve, NaN first value).

## Files to look at
- utils/reporting.py
- backtest/cli.py
- tests/test_reporting.py
- tests/test_cli.py

## Acceptance Criteria
- All tests pass
- ruff and mypy clean

**Ready for next agent.**
