# Task for Next Agent

## Context
Refined the PDF report layout in `utils/reporting.py::generate_pdf_report`:
- Page 1 (metrics): tighter `pad_inches=0.4`, sans-serif font, `linespacing=1.15`.
- Page 2 (equity/drawdown): smaller tick labels, `pad=1.2`.
- Page 3 (weights): rendered as a **bar chart** with positive/negative colors, value labels, and zero baseline instead of monospace text.
- Page 4 (trades): rendered as a **matplotlib table** (`ax.table`) with column headers, centered cells, and header shading; long trade lists paginate across multiple PDF pages (50 rows/page) instead of a single cramped page.
- Notebook `notebooks/quickstart_report.ipynb` updated to demonstrate the new PDF pages (trades + weights attached to the result).

All 165 tests pass; `ruff check` clean; `mypy backtest/ strategies/ utils/` clean.

## Suggested Tasks
1. Add a CLI flag to persist report artifacts under `reports/` with timestamped filenames (e.g. `--artifact-dir reports`), so each run produces a dated HTML/PDF/JSON artifact.
2. Add a notebook that walks through walk-forward portfolio results and renders per-window equity curves + a summary table.
3. Add a `--benchmark` CLI flag to include an equal-weighted buy-and-hold benchmark line on the equity chart in HTML/PDF reports.
4. Add tests for the new PDF table rendering (e.g. asserting the generated PDF contains expected trade cell text via `pypdf`/`pdfplumber` if available, or at least multi-page behavior).
5. Add a `generate_walk_forward_report` utility that aggregates per-window results into a summary table + equity curve.

## Files to look at
- `utils/reporting.py`
- `backtest/cli.py`
- `tests/test_reporting.py`
- `tests/test_cli.py`
- `notebooks/quickstart_report.ipynb`

## Acceptance Criteria
- All tests pass
- ruff and mypy clean