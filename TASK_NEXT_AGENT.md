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
COMPLETED — Add Monte Carlo / bootstrap confidence intervals to walk-forward reports.

## Background
Good next steps: multi-horizon walk-forward (expanding vs rolling windows), cost-model sensitivity sweeps, live/paper trading integration, or strategy benchmark registry.

## Tasks
- [x] Task 1: Add in-sample vs out-of-sample performance comparison to walk-forward reports.
- [x] Task 2: Add Monte Carlo / bootstrap confidence intervals to walk-forward reports.

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

## Next task for the next agent

### Add cost-model sensitivity sweeps to walk-forward reports

Walk-forward reports currently use a single fee/slippage assumption. Users cannot tell how sensitive an observed OOS mean return or OOS/IS ratio is to transaction-cost assumptions, which is critical for stat-arb strategies where costs can erase alpha.

Run walk-forward across a grid of cost assumptions and surface the sensitivity in reports.

### Objective
Add a cost-model sensitivity sweep to walk-forward reporting: for a grid of (fee_rate, slippage) pairs, run walk-forward and report how `mean_return`, `oos_mean_return`, `oos_is_ratio`, and `max_drawdown` vary, rendered in walk-forward text/HTML/PDF reports.

### Requirements
1. `backtest/engine.py` or `utils/reporting.py`: Add a helper `sweep_cost_sensitivity(engine_or_fn, cost_grid, ...)` that runs walk-forward for each (fee_rate, slippage) pair in the grid and returns per-config aggregates (`mean_return`, `oos_mean_return`, `oos_is_ratio`, `max_drawdown`, plus the config used).
2. `utils/reporting.py`: `generate_walk_forward_report` attaches the sweep results under a `cost_sensitivity` key when a sweep is requested/present.
3. `utils/reporting.py`: Extend `generate_walk_forward_text_report`, `generate_walk_forward_html_report`, and `generate_walk_forward_pdf_report` to render a "Cost-Model Sensitivity" section when sweep data is present.
4. Add tests in `tests/test_walk_forward_cost_sensitivity.py`: sweep runs across the grid, returns correct shape, identifies best/worst cost configs, text/HTML/PDF rendering, backward compat when absent.
5. Keep public API backward compatible; all existing tests must still pass; ruff and mypy clean.
6. Follow existing code style (4-space indent, `from __future__ import annotations`, type hints on public functions); no `# type: ignore` for real bugs.

### Verification
```bash
python3 -m pytest tests/ -q
python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python3 -m mypy backtest/ strategies/ utils/
```

**Ready for next agent.**
