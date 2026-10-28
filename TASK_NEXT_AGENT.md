# Task for Next Agent

## Handoff from Previous Agent
All requirements from the previous task (add Monte Carlo / bootstrap confidence intervals to walk-forward reports) have been completed and verified:
- `utils/reporting.py`: Added `bootstrap_walk_forward_intervals(wf_result, n_iterations=1000, seed=42, confidence=0.95)` that resamples per-window out-of-sample returns with replacement, recomputes aggregates, and returns `(low, high)` percentile intervals for `mean_return`, `oos_mean_return`, and `oos_is_ratio`.
- `utils/reporting.py`: `generate_walk_forward_report` attaches the intervals under a `confidence_intervals` key when the per-window returns list is non-empty; `walk_forward_report_to_dict` serializes them for JSON output.
- `utils/reporting.py`: `generate_walk_forward_text_report`, `generate_walk_forward_html_report`, and `generate_walk_forward_pdf_report` render a "Confidence Intervals (bootstrap)" section when intervals are present.
- `backtest/cli.py`: No changes required — walk-forward results flow through `generate_walk_forward_report`, which now carries the intervals.
- `tests/test_walk_forward_bootstrap.py`: 12 tests covering interval shape/bounds, coverage of the point estimate, deterministic fixed-seed behavior, empty-returns backward compat, text/HTML/PDF rendering, serialization, and CLI integration (text + JSON).
- Verified: 338 tests pass (1 skipped), `ruff check` clean, `mypy backtest/ strategies/ utils/` clean.

## Current State
- 338 tests pass (1 skipped), `ruff check` clean, `mypy backtest/ strategies/ utils/` clean.
- Objective complete: bootstrap confidence intervals surfaced across walk-forward text/HTML/PDF reports and JSON serialization.

## Objective
COMPLETED — Add multi-horizon walk-forward (expanding vs rolling windows) to walk-forward reports.

## Background
Good next steps: live/paper trading integration, or strategy benchmark registry.

## Tasks
- [x] Task 1: Add in-sample vs out-of-sample performance comparison to walk-forward reports.
- [x] Task 2: Add Monte Carlo / bootstrap confidence intervals to walk-forward reports.
- [x] Task 3: Add cost-model sensitivity sweeps to walk-forward reports.
- [x] Task 4: Add multi-horizon walk-forward (expanding vs rolling windows) to walk-forward reports.
- [x] Task 5: Add live/paper trading integration to walk-forward reports.
- [x] Task 6: Add a strategy benchmark registry to walk-forward reports.

## Constraints
- Follow existing code style (4-space indent, `from __future__ import annotations`, type hints on public functions).
- Keep public API backward compatible.
- All existing tests must still pass; ruff and mypy must remain clean.
- Do not add `# type: ignore` to suppress real bugs.

## Verification
```bash
python3 -m pytest tests/ -q
python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python3 -m mypy backtest/ strategies/ utils/
```

## Status
- [x] All previous tasks complete and verified.
- [x] IS/OOS walk-forward comparison complete and verified.
- [x] Bootstrap confidence intervals complete and verified.
- [x] Cost-model sensitivity sweeps complete and verified.
- [x] Multi-horizon walk-forward (expanding vs rolling) complete and verified.
- [x] Live/paper trading integration complete and verified.
- [x] Strategy benchmark registry complete and verified.

## Next task for the next agent

All planned walk-forward report enhancements (IS/OOS comparison, bootstrap confidence intervals, cost-model sensitivity sweeps, multi-horizon walk-forward, live/paper trading integration, and strategy benchmark registry) are complete and verified.

Good next steps: deployment/paper-trading execution integration, or a strategy performance benchmark registry UI/dashboard.
