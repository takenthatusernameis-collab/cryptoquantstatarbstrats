# Task for Next Agent

## Context
Added `--artifact-dir` CLI flag to persist timestamped report artifacts under a directory (`reports_<timestamp>.{json,html,pdf,txt}`), wired through config mappings. All 165 tests pass; ruff and mypy clean.

## Suggested Tasks
1. Add a `--benchmark` CLI flag to include an equal-weighted buy-and-hold benchmark line on the equity chart in HTML/PDF reports.
2. Add a notebook that walks through walk-forward portfolio results and renders per-window equity curves + a summary table.
3. Add a `generate_walk_forward_report` utility that aggregates per-window results into a summary table + equity curve.
4. Add tests asserting PDF report contains expected trade cell text via pypdf/pdfplumber if available.

## Files to look at
- utils/reporting.py
- backtest/cli.py
- tests/test_reporting.py
- tests/test_cli.py

## Acceptance Criteria
- All tests pass
- ruff and mypy clean
