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

## Next task for the next agent

### Add real-time monitoring and alerts for paper trading

Extend the paper-trading system with real-time monitoring capabilities including alerts, performance tracking, and dashboard integration.

### Objective
Add monitoring and alerting for paper trading sessions with configurable thresholds and reporting.

### Requirements
1. Create `backtest/monitoring.py` with alerting system (email/webhook/console alerts) for drawdowns, PnL thresholds, risk limits
2. Add monitoring integration to `backtest/cli.py` paper-trade command with `--monitor`, `--alert-config` options
3. Add position/risk monitoring with real-time metrics tracking
4. Create tests in `tests/test_paper_trading_monitoring.py`
5. Keep public API backward compatible; all existing tests must still pass
6. Follow existing code style (4-space indent, `from __future__ import annotations`, type hints on public functions)

### Verification
```bash
python3 -m pytest tests/ -q
```

**Ready for next agent.**
