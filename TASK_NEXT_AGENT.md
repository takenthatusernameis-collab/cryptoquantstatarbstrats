# Task for Next Agent

## Context
The previous agent added HTML and PDF report generation:
- Added `generate_html_report()` and `generate_pdf_report()` to `utils/reporting.py`
- Extended CLI (`backtest/cli.py`) to support `--output html|pdf` with `--output-path`
- Added notebook `notebooks/quickstart_report.ipynb` with examples

All existing tests pass (152 passed). New tests for HTML/PDF generation were added.

## Goal
Enhance the reporting functionality to make reports more useful and production-ready.

## Suggested Tasks
1. **Enhance HTML reports with visualizations** - Add equity curve charts (e.g., using Chart.js or inline SVG). The result dict may contain `equity_curve` (pandas Series). Make the HTML report include a plot of equity curve and drawdown.
2. **Improve PDF reports** - If matplotlib is available, generate better formatted multi-page PDFs with charts. Currently falls back to HTML if matplotlib missing; add graceful handling and better layout.
3. **Add CLI options** - Consider adding `--title` for custom report titles.
4. **Export formats** - Maybe support exporting trade list/weights in reports.

## Files to look at
- `utils/reporting.py` - main implementation
- `backtest/cli.py` - CLI integration
- `tests/test_reporting.py` - reporting tests
- `notebooks/quickstart_report.ipynb` - usage example

## Acceptance Criteria
- HTML reports should display equity curve if available in result
- Maintain backward compatibility
- All tests pass
- Add tests for new functionality
