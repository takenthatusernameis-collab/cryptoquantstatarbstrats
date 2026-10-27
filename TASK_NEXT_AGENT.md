# Task for Next Agent

## Context
Enhanced HTML reports with equity curve and drawdown visualization (inline SVG) when `equity_curve` is present in result. Added test `test_generate_html_report_includes_equity_curve`.

All tests pass (153 passed). ruff and mypy clean.

## Suggested Tasks
1. Improve PDF reports with multi-page charts (already partially implemented; refine layout).
2. Add `--title` CLI option for custom report titles.
3. Export trade list/weights in reports.

## Files to look at
- `utils/reporting.py`
- `backtest/cli.py`
- `tests/test_reporting.py`

## Acceptance Criteria
- HTML reports display equity curve if available
- Maintain backward compatibility
- All tests pass
- Add tests for new functionality
" filePath">
/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats/TASK_NEXT_AGENT.md