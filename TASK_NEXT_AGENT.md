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
COMPLETED — Add cost-model sensitivity sweeps to walk-forward reports.

## Background
Good next steps: multi-horizon walk-forward (expanding vs rolling windows), live/paper trading integration, or strategy benchmark registry.

## Tasks
- [x] Task 1: Add in-sample vs out-of-sample performance comparison to walk-forward reports.
- [x] Task 2: Add Monte Carlo / bootstrap confidence intervals to walk-forward reports.
- [x] Task 3: Add cost-model sensitivity sweeps to walk-forward reports.

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

## Next task for the next agent

### Add multi-horizon walk-forward (expanding vs rolling windows) to walk-forward reports

Walk-forward currently uses a single fixed train/test window scheme (rolling walk-forward with `train_period`/`test_period`). Users cannot compare how results differ between expanding windows (growing train set, fixed or growing test set) and rolling windows (fixed-size train set sliding forward), which matters for assessing the stability of stat-arb alpha across different amounts of training data.

### Objective
Add multi-horizon walk-forward support so reports can contrast expanding vs rolling window schemes, exposing per-scheme aggregates (`mean_return`, `oos_mean_return`, `oos_is_ratio`, `max_drawdown`) rendered in walk-forward text/HTML/PDF reports.

### Requirements
1. `backtest/engine.py`: Add an option (e.g. `mode="rolling"`/`mode="expanding"`) to `walk_forward`/`walk_forward_portfolio` supporting expanding windows where the train window grows from a minimum size rather than staying fixed.
2. `utils/reporting.py`: Extend `generate_walk_forward_report` to accept/attach multi-horizon results under a `multi_horizon` key when requested.
3. `utils/reporting.py`: Extend `generate_walk_forward_text_report`, `generate_walk_forward_html_report`, and `generate_walk_forward_pdf_report` to render a "Multi-Horizon Walk-Forward" section when multi-horizon data is present.
4. Add tests in `tests/test_walk_forward_multi_horizon.py`: expanding vs rolling run correctly, return correct shape, text/HTML/PDF rendering, backward compat when absent.
5. Keep public API backward compatible; all existing tests must still pass; ruff and mypy clean.
6. Follow existing code style (4-space indent, `from __future__ import annotations`, type hints on public functions); no `# type: ignore` for real bugs.

### Verification
```bash
python3 -m pytest tests/ -q
python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python3 -m mypy backtest/ strategies/ utils/
```

**Ready for next agent.**
