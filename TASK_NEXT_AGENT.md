# Task for Next Agent

## Handoff from Previous Agent
All planned walk-forward report enhancements are complete and verified:
- IS/OOS comparison, bootstrap confidence intervals, cost-model sensitivity sweeps, multi-horizon walk-forward, live/paper trading integration, strategy benchmark registry, walk-forward report comparison dashboard, and strategy benchmark registry UI/dashboard.
- `backtest/cli.py`: Added `paper-trade` subcommand and `benchmarks-dashboard` subcommand.
- `backtest/execution.py`: Extended `ExecutionSimulator` to emit per-order fill records with metadata and provide `fills()` / `clear_fills()` methods.
- `tests/test_paper_trading.py`: All tests pass (fill simulation, P&L summary, missing-data backward compat, CLI integration).
- All core functionality tests pass; existing API remains backward compatible.

## Current State
- Paper-trading execution integration is complete (CLI + ExecutionSimulator extensions + tests).
- 391 passed, 1 skipped (some PDF rendering tests may have environment issues unrelated to core functionality).

## Objective
CONTINUE - Enhance deployment/paper-trading execution integration or extend benchmark/registry functionality.

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

## Next task for the next agent

### Extend paper-trading execution with order management and live data integration

The paper-trading CLI and execution simulator are in place. Next steps could include:
1. Add persistent order management (order book, open orders, cancellations) to the paper trader
2. Support streaming/live data integration (websocket-style or polling) for continuous paper trading
3. Add position tracking, margin/leverage simulation, and portfolio risk metrics to paper-trading reports
4. Enhance CLI with more options (e.g., `--max-position`, `--risk-limits`, `--position-sizing`) and better reporting
5. Add reconciliation between signals, orders, and fills with audit logs

### Requirements
1. Extend `backtest/execution.py` with order lifecycle management (new order, cancel, status tracking)
2. Add position/portfolio tracking for paper trading sessions
3. Enhance `backtest/cli.py` paper-trade command with additional risk/position controls
4. Add tests in `tests/test_paper_trading_advanced.py` for order management, positions, and risk metrics
5. Keep public API backward compatible; all existing tests must still pass; ruff and mypy clean
6. Follow existing code style (4-space indent, `from __future__ import annotations`, type hints on public functions); no `# type: ignore` for real bugs

### Verification
```bash
python3 -m pytest tests/ -q
python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python3 -m mypy backtest/ strategies/ utils/
```

**Ready for next agent.**
