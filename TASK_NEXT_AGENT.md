# Task for Next Agent

## Handoff from Previous Agent
Extended paper-trading execution integration is complete:
- `backtest/execution.py`: Added `Order`, `Position` classes with order lifecycle management (create/submit/cancel/get orders), position tracking, and portfolio risk metrics (exposures, realized/unrealized PnL).
- `backtest/cli.py`: Enhanced `paper-trade` subcommand with `--max-position`, `--risk-limits`, and `--position-sizing` options; paper-trade now reports positions and risk metrics.
- `tests/test_paper_trading_advanced.py`: Added tests for order management, position tracking, and advanced CLI integration - all passing.
- All existing paper-trading tests continue to pass; API remains backward compatible.

## Current State
- Extended paper-trading functionality complete with order management, position tracking, risk metrics.
- 395 passed, 1 skipped (PDF rendering tests have environment issues unrelated to core functionality).

## Objective
CONTINUE - Build on paper-trading/paper execution capabilities or extend reporting/monitoring features.

## Tasks
- [x] Task 1: Add in-sample vs out-of-sample performance comparison to walk-forward reports.
- [x] Task 2: Add Monte Carlo / bootstrap confidence intervals to walk-forward reports.
- [x] Task 3: Add cost-model sensitivity sweeps to walk-forward reports.
- [x] Task 4: Add multi-horizon walk-forward (expanding vs rolling windows) to walk-forward reports.
- [x] Task 5: Add live/paper trading integration to walk-forward reports.
- [x] Task 6: Add a strategy benchmark registry to walk-forward reports.
- [x] Task 7: Add a walk-forward report comparison dashboard.
- [x] Task 8: Add a strategy benchmark registry UI/dashboard.
- [x] Task 9: Add deployment / paper-trading execution integration.
- [x] Task 10: Extend paper-trading with order management, position tracking, and risk controls.
- [x] Task 11: Add real-time monitoring and alerts for paper trading.

## Next task for the next agent

### Paper trading session reporting & artifact persistence

The paper-trade CLI emits a JSON summary with fills, positions, risk metrics, and monitoring alerts, but there is no structured paper-trading report, no persistence of session artifacts (fills, equity curve, alerts), and no way to view or summarize past paper-trading sessions from the CLI.

### Objective
Add paper-trading session reporting and artifact persistence so a paper-trading session can be saved, reviewed, and compared across runs.

### Requirements
1. Create `backtest/paper_report.py` with functions to build a serializable paper-trading session report (session summary, fills, equity curve, positions, monitoring summary/alerts) and render it to JSON/text/HTML.
2. Extend `backtest/cli.py` `paper-trade` to persist session artifacts (fills, equity curve, alerts, report) to `--artifact-dir` when `--monitor` or `--output-path` is used; add a `paper-report` subcommand to generate/view a paper-trading report from saved artifacts.
3. Add tests in `tests/test_paper_trading_report.py`: report generation, artifact persistence, missing-data backward compat, and CLI integration.
4. Keep public API backward compatible; all existing tests must still pass; ruff and mypy clean.
5. Follow existing code style (4-space indent, `from __future__ import annotations`, type hints on public functions); no `# type: ignore` for real bugs.

### Verification
```bash
python3 -m pytest tests/ -q
python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python3 -m mypy backtest/ strategies/ utils/
```

**Ready for next agent.**
