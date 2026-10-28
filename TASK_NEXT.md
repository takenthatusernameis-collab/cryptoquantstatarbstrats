# Task for Next Agent

## Handoff from Previous Agent
All walk-forward report enhancements are complete and verified:
- IS/OOS comparison, bootstrap confidence intervals, cost-model sensitivity sweeps, multi-horizon walk-forward, live/paper trading integration, strategy benchmark registry, and walk-forward report comparison dashboard.
- 382 tests pass (1 skipped), `ruff check` clean, `mypy backtest/ strategies/ utils/` clean.
- `utils/reporting.py`, `backtest/cli.py`, and `tests/test_walk_forward_compare.py` all carry the comparison dashboard work.

## Objective
Add a strategy benchmark registry UI/dashboard: a CLI command that loads a benchmark registry CSV and renders an HTML dashboard comparing each benchmark's metrics (mean return, max drawdown, Sharpe) side-by-side so users can contextualize stat-arb alpha against reference strategies/benchmarks.

## Requirements
1. `backtest/cli.py`: Add a `benchmarks-dashboard` subcommand accepting `--benchmarks-csv <path>` and an `--output <path>` HTML output.
2. `utils/reporting.py`: Add `generate_benchmark_dashboard_html(benchmarks)` returning an HTML dashboard string with per-benchmark comparison tables and aggregate stats; keep public API backward compatible.
3. `utils/reporting.py`: Add `aggregate_benchmark_registry(benchmarks)` returning a structure with per-benchmark metrics plus aggregate registry stats (count, mean return, mean drawdown).
4. Add tests in `tests/test_benchmark_dashboard.py`: aggregation, HTML rendering, missing-field backward compat, and CLI integration.
5. Keep public API backward compatible; all existing tests must still pass; ruff and mypy clean.
6. Follow existing code style (4-space indent, `from __future__ import annotations`, type hints on public functions); no `# type: ignore` for real bugs.

## Verification
```bash
python3 -m pytest tests/ -q
python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python3 -m mypy backtest/ strategies/ utils/
```

## Status
- [ ] Strategy benchmark registry UI/dashboard (next agent)

**Ready for next agent.**

(End of file - total 44 lines)