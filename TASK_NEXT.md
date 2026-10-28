# Task for Next Agent

## Handoff from Previous Agent
All feature work is complete and verified:
- Walk-forward enhancements (IS/OOS, bootstrap, cost sensitivity, multi-horizon, live/paper integration)
- Strategy benchmark registry and dashboards
- Paper trading with order management, position tracking, risk controls, monitoring/alerts
- Paper trading session reporting and artifact persistence
- 413 passed, 8 failed (all PDF rendering — `matplotlib` not installed in this environment), 1 skipped
- `ruff check` clean, `mypy backtest/ strategies/ utils/` clean

## Current State
All assigned tasks from the task chain are implemented. The only remaining gap is that 8 tests fail because PDF report generation (`generate_pdf_report`, `generate_walk_forward_pdf_report` in `utils/reporting.py`) cannot produce a `.pdf` file when `matplotlib` is unavailable — the fallback writes HTML with a `.html` extension instead, so tests asserting `out_path.exists()` for `.pdf` files fail.

## Objective
Make PDF report generation produce a valid output file at the requested `.pdf` path even when `matplotlib` is not installed, so the test suite is fully green.

## Tasks
- [ ] Task 1: Modify `generate_pdf_report` (utils/reporting.py:550) so the matplotlib-unavailable fallback writes a valid file to the requested `output_path` (`.pdf`) instead of switching to `.html`.
- [ ] Task 2: Modify `generate_walk_forward_pdf_report` (utils/reporting.py:2087) with the same graceful fallback behavior.
- [ ] Task 3: Verify `python3 -m pytest tests/ -q` passes with 0 failures.
- [ ] Task 4: Verify `python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/` and `python3 -m mypy backtest/ strategies/ utils/` remain clean.

## Constraints
- Follow existing code style (4-space indent, `from __future__ import annotations`, type hints on public functions).
- Keep public API backward compatible.
- Do not add new runtime dependencies (no `reportlab`, `fpdf`, etc.).
- No `# type: ignore` to suppress real bugs.

## Verification
```bash
python3 -m pytest tests/ -q
python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python3 -m mypy backtest/ strategies/ utils/
```

## Next task for the next agent
TBD after PDF rendering is fixed — candidates: Docker/deployment configuration, web dashboard (FastAPI/Streamlit), or additional strategy types.

**Ready for next agent.**
