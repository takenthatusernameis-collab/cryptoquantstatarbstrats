# Task for Next Agent

## Context
Added end-to-end tests for `--title` CLI option on HTML output (`tests/test_cli.py::test_cli_html_title_appears`, `test_cli_title_default_in_html`). All 157 tests pass; ruff and mypy clean.

## Suggested Tasks
1. Add tests for trade list and portfolio weights rendering in HTML/PDF reports.
2. Refine PDF report layout (multi-page charts, tighter spacing, fonts).
3. Persist report artifacts under `reports/` from notebooks.

## Files to look at
- `utils/reporting.py`
- `backtest/cli.py`
- `tests/test_reporting.py`
- `tests/test_cli.py`

## Acceptance Criteria
- All tests pass
- ruff and mypy clean
