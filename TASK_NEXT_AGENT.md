# Task for Next Agent

## Context
Fixed HTML report output: `generate_html_report` now joins lines with real newlines instead of literal `\\n`, so saved HTML files render correctly. All 155 tests pass; ruff and mypy clean.

## Suggested Tasks
1. Refine PDF report layout (multi-page charts, tighter spacing, fonts).
2. Add `--title` CLI option (already wired) end-to-end tests.
3. Export trade list/weights in reports (already implemented; add tests).
4. Persist report artifacts under `reports/` from notebooks.

## Files to look at
- `utils/reporting.py`
- `backtest/cli.py`
- `tests/test_reporting.py`
- `tests/test_cli.py`

## Acceptance Criteria
- HTML files render correctly in browsers
- All tests pass
- Add tests for new functionality
" filePath">
/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats/TASK_NEXT_AGENT.md