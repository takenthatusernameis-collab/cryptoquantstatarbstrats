# Task for Next Agent

## Handoff from Previous Agent
All requirements from the previous task (add in-sample vs out-of-sample performance comparison to walk-forward reports) have been completed and verified:
- `backtest/engine.py`: `walk_forward`/`walk_forward_portfolio` evaluate in-sample performance on the train window per window via `_evaluate_in_sample`, attaching `is_total_return`, `is_sharpe_ratio`, `is_max_drawdown` and `oos_total_return` (mirroring `total_return`) to each per-window result. Aggregates `is_mean_return`, `oos_mean_return`, `oos_is_ratio` (mean OOS return / mean IS return) into the walk-forward result dict.
- `utils/reporting.py`: `generate_walk_forward_report` includes IS/OOS columns in the summary DataFrame and an `is_vs_oos` aggregate; `generate_walk_forward_text_report`, `generate_walk_forward_html_report`, and `generate_walk_forward_pdf_report` render an "In-Sample vs Out-of-Sample" section when IS data is present.
- `backtest/cli.py`: walk-forward runs surface IS/OOS comparison through the report generators (text/json/html/pdf/output-path paths all route through `generate_walk_forward_report`).
- `tests/test_walk_forward_is_oos.py`: 11 tests covering per-window IS/OOS columns, aggregate ratios, text/HTML/PDF rendering, serialization, backward compatibility when IS data absent, and CLI integration (text + JSON).
- Verified: 326 tests pass (1 skipped), `ruff check` clean, `mypy backtest/ strategies/ utils/` clean.

## Current State
- 326 tests pass, ruff clean, mypy clean on backtest/strategies/utils/.
- Objective complete: in-sample vs out-of-sample walk-forward comparison surfaced across text/HTML/PDF reports and JSON serialization.

## Objective
COMPLETED — Add in-sample vs out-of-sample performance comparison to walk-forward reports.

## Background
Good next steps: Monte Carlo / bootstrap confidence intervals on walk-forward results, multi-horizon walk-forward (expanding vs rolling windows), cost-model sensitivity sweeps, live/paper trading integration, or strategy benchmark registry.

## Tasks
- [x] Task 1: Add in-sample vs out-of-sample performance comparison to walk-forward reports.

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

## Next task for the next agent

### Add Monte Carlo / bootstrap confidence intervals to walk-forward reports

The framework reports point estimates (mean return, Sharpe, OOS/IS ratio) across walk-forward windows, but provides no uncertainty quantification. Users cannot tell whether an observed OOS mean return is statistically distinguishable from zero or from the in-sample mean.

Add bootstrap / Monte Carlo confidence intervals to walk-forward reporting.

### Objective
Surface bootstrap confidence intervals (e.g. 5th–95th percentile, or 95% CI) for walk-forward aggregates (`mean_return`, `oos_mean_return`, `oos_is_ratio`) and render them in walk-forward text/HTML/PDF reports.

### Requirements
1. `utils/reporting.py`: Add a `bootstrap_walk_forward_intervals(wf_result, n_iterations=1000, seed=42, confidence=0.95)` helper that resamples the per-window returns with replacement, recomputes the aggregates, and returns a dict of `(low, high)` intervals for `mean_return`, `oos_mean_return`, and `oos_is_ratio`.
2. `utils/reporting.py`: `generate_walk_forward_report` attaches the intervals under a `confidence_intervals` key when the per-window returns list is non-empty.
3. `utils/reporting.py`: Extend `generate_walk_forward_text_report`, `generate_walk_forward_html_report`, and `generate_walk_forward_pdf_report` to render a "Confidence Intervals (bootstrap)" section when intervals are present.
4. `backtest/cli.py`: No changes required — walk-forward results already flow through `generate_walk_forward_report`, which now carries the intervals.
5. Add tests in `tests/test_walk_forward_bootstrap.py`: intervals present with correct shape, coverage of the point estimate within the interval, deterministic with a fixed seed, backward compatibility when intervals absent, text/HTML/PDF rendering.
6. Keep public API backward compatible; all existing tests must still pass; ruff and mypy clean.
7. Follow existing code style (4-space indent, `from __future__ import annotations`, type hints on public functions); no `# type: ignore` for real bugs.

### Verification
```bash
python3 -m pytest tests/ -q
python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python3 -m mypy backtest/ strategies/ utils/
```

**Ready for next agent.**

(End of file - total 96 lines)