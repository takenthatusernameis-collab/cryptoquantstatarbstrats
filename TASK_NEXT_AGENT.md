# Task for Next Agent

## Context
All work assigned in previous rounds is complete and verified:

1. `--benchmark` CLI flag — equal-weighted buy-and-hold benchmark (`benchmark_equity_curve` / `benchmark_total_return`) on result; rendered in `generate_html_report` (SVG) and `generate_pdf_report` (equity page). Computed for `run`, `run_portfolio`, and `walk_forward_portfolio` paths when `--benchmark` or `--rebalance-benchmark` is set (`backtest/cli.py`).
2. `generate_walk_forward_report` utility — aggregates per-window walk-forward results into summary `DataFrame` + chained `equity_curve` Series (`utils/reporting.py`).
3. `generate_walk_forward_html_report` / `generate_walk_forward_pdf_report` renderers — summary table + equity chart pages (`utils/reporting.py`).
4. `--walk-forward-report` CLI flag — emits walk-forward summary artifact (csv/html/pdf) under `reports/` or via `--artifact-dir`/`--output-path` (`backtest/cli.py`).
5. Comprehensive walk-forward reporting tests and all prior features (portfolio optimization/risk, execution simulation VWAP/TWAP + OHLC, regime detection, rebalancing, config-driven CLI, HTML/PDF artifacts) remain intact.
6. **GitHub Actions CI workflow** (`.github/workflows/ci.yml`) added — runs on push/PR, installs deps via `pip install -e ".[dev]"`, and executes `ruff check`, `mypy backtest/ strategies/ utils/`, and `pytest tests/ -q` across Python 3.10/3.11/3.12.

## Current State (verified)
- `python3 -m pytest tests/ -q` -> 180 passed
- `python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/` -> All checks passed
- `python3 -m mypy backtest/ strategies/ utils/` -> Success: no issues found in 24 source files
- `.github/workflows/ci.yml` created with `lint`, `typecheck`, and `test` jobs (test job matrixed on Python 3.10/3.11/3.12)

## Framework Status
Feature-complete: portfolio optimization, portfolio-level risk metrics, execution simulation (market/limit/VWAP/TWAP + OHLC passthrough), regime detection, walk-forward robustness, config-driven CLI (YAML/TOML/JSON), HTML/PDF report artifacts, rebalancing, benchmark curves, walk-forward reporting, and CI workflow — all with tests and type checking passing.

## Next task for the next agent
Add a GitHub Actions CI workflow (`.github/workflows/ci.yml`) that runs on push/PR and executes:
- Install dependencies (e.g. `pip install -e ".[dev]"` or install from `requirements.txt` + dev deps)
- Lint: `ruff check .`
- Type check: `mypy backtest/ strategies/ utils/`
- Tests: `python -m pytest tests/ -q`

Keep workflow minimal, cache pip if reasonable, and ensure it passes against current repo state. Update README if desired (optional). Do not change library code unless necessary for CI to pass.

### Acceptance criteria
- [x] `.github/workflows/ci.yml` added with jobs for ruff, mypy, pytest
- [x] Workflow runs successfully (or is correctly configured)
- [x] All checks remain green: `pytest`, `ruff`, `mypy`

**Ready for next agent.**