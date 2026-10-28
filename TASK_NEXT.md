# Task for Next Agent

## Handoff from Previous Agent
All walk-forward report enhancements are complete and verified:
- IS/OOS comparison, bootstrap confidence intervals, cost-model sensitivity sweeps, multi-horizon walk-forward, live/paper trading integration, and strategy benchmark registry.
- 377 tests pass (1 skipped), `ruff check` clean, `mypy backtest/ strategies/ utils/` clean.
- `utils/reporting.py`, `backtest/cli.py`, and `tests/test_walk_forward_benchmarks.py` all carry the benchmark registry work.

## Objective
Add a walk-forward report comparison dashboard: a CLI command that loads multiple walk-forward JSON reports and renders a side-by-side HTML comparison (OOS mean return, Sharpe, max drawdown, IS/OOS ratio, and walk-forward vs benchmark deltas) so users can contextualize stat-arb alpha across runs and benchmarks.

## Requirements
1. `backtest/cli.py`: Add a `wf-compare` subcommand accepting multiple `--report <path>` JSON inputs and an `--output <path>` HTML output.
2. `utils/reporting.py`: Add `compare_walk_forward_reports(reports)` returning a comparison structure with per-report metrics and benchmark-vs-walk-forward deltas; keep public API backward compatible.
3. `utils/reporting.py`: Add an HTML renderer for the comparison dashboard (stdlib-only HTML generation; no new hard dependencies).
4. Add tests in `tests/test_walk_forward_compare.py`: comparison aggregation, HTML rendering, missing-field backward compat, and CLI integration (text/JSON paths unchanged).
5. Keep public API backward compatible; all existing tests must still pass; ruff and mypy clean.
6. Follow existing code style (4-space indent, `from __future__ import annotations`, type hints on public functions); no `# type: ignore` for real bugs.

## Verification
```bash
python3 -m pytest tests/ -q
python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python3 -m mypy backtest/ strategies/ utils/
```

## Status
- [ ] Walk-forward report comparison dashboard (next agent)

**Ready for next agent.**
