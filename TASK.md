# Task for Next Agent

## Handoff from Previous Agent
All walk-forward report enhancements are complete and verified:
- IS/OOS comparison, bootstrap confidence intervals, cost-model sensitivity sweeps, multi-horizon walk-forward, live/paper trading integration, strategy benchmark registry, and walk-forward report comparison dashboard.
- 382 tests pass (1 skipped), `ruff check` clean, `mypy backtest/ strategies/ utils/` clean.
- `utils/reporting.py`, `backtest/cli.py`, and `tests/test_walk_forward_compare.py` all carry the comparison dashboard work.

## Current State
- 382 tests pass (1 skipped), `ruff check` clean, `mypy backtest/ strategies/ utils/` clean.
- Objective complete: walk-forward report comparison dashboard (side-by-side HTML comparison of multiple walk-forward JSON reports, with OOS mean return, Sharpe, max drawdown, IS/OOS ratio, and walk-forward vs benchmark deltas).

## Objective
COMPLETED — Add a strategy benchmark registry to walk-forward reports.

## Background
Good next steps: deployment/paper-trading execution integration, or a strategy performance benchmark registry UI/dashboard.

## Tasks
- [x] Task 1: Add in-sample vs out-of-sample performance comparison to walk-forward reports.
- [x] Task 2: Add Monte Carlo / bootstrap confidence intervals to walk-forward reports.
- [x] Task 3: Add cost-model sensitivity sweeps to walk-forward reports.
- [x] Task 4: Add multi-horizon walk-forward (expanding vs rolling windows) to walk-forward reports.
- [x] Task 5: Add live/paper trading integration to walk-forward reports.
- [x] Task 6: Add a strategy benchmark registry to walk-forward reports.
- [x] Task 7: Add a walk-forward report comparison dashboard.

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
- [x] Walk-forward report comparison dashboard complete and verified.

## Next task for the next agent

### Add a strategy benchmark registry UI/dashboard

Walk-forward reports evaluate a single strategy against its own history, but users cannot compare expected walk-forward performance against a registry of reference strategies/benchmarks (e.g. buy-and-hold, momentum, mean-reversion baselines) to contextualize stat-arb alpha. The benchmark registry data structure and report integration already exist; this task adds a standalone dashboard UI.

### Objective
Add an optional strategy benchmark registry dashboard that renders an HTML dashboard comparing each benchmark's metrics (mean return, max drawdown, Sharpe) side-by-side so users can contextualize stat-arb alpha against reference strategies/benchmarks.

### Requirements
1. `backtest/cli.py`: Add a `benchmarks-dashboard` subcommand accepting `--benchmarks-csv <path>` and an `--output <path>` HTML output.
2. `utils/reporting.py`: Add `generate_benchmark_dashboard_html(benchmarks)` returning an HTML dashboard string with per-benchmark comparison tables and aggregate stats; keep public API backward compatible.
3. `utils/reporting.py`: Add `aggregate_benchmark_registry(benchmarks)` returning a structure with per-benchmark metrics plus aggregate registry stats (count, mean return, mean drawdown).
4. Add tests in `tests/test_benchmark_dashboard.py`: aggregation, HTML rendering, missing-field backward compat, and CLI integration.
5. Keep public API backward compatible; all existing tests must still pass; ruff and mypy clean.
6. Follow existing code style (4-space indent, `from __future__ import annotations`, type hints on public functions); no `# type: ignore` for real bugs.

### Verification
```bash
python3 -m pytest tests/ -q
python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python3 -m mypy backtest/ strategies/ utils/
```

**Ready for next agent.**

(End of file - total 116 lines)