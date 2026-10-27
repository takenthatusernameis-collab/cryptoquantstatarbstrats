# Task for Next Agent

## Assigned task
Implement an iceberg execution model in `backtest/execution.py`.

### Requirements
1. Add `IcebergExecution` class following the existing execution interface (see `MarketExecution`, `LimitExecution`, `VWAPExecution`, `TWAPExecution`).
2. Support parameters: `visible_qty` (or `display_qty`), `min_fill`, `price_offset` (basis points or absolute), and optional `time_in_force`.
3. Behavior: only `visible_qty` is exposed at a time; when filled, replenish another visible slice until order complete. Respect volume-tied fills and OHLC passthrough where applicable.
4. Integrate cleanly with existing order/fill logic (no breaking changes to other execution models).
5. Add unit tests in `tests/test_execution_iceberg.py` covering: partial replenishment, full fill, min_fill constraints, price_offset application.

## Acceptance criteria
- `python3 -m pytest tests/test_execution_iceberg.py -v` passes
- `python3 -m pytest tests/ -q` passes (no regressions)
- `python3 -m ruff check backtest/execution.py tests/test_execution_iceberg.py` clean
- `python3 -m mypy backtest/execution.py` clean

## Context
- Implementation patterns: `backtest/execution.py`, `backtest/engine.py` (how executions are used)
- Volume/partial fills: see `VolumeTiedMixin`/related logic
- Tests: `tests/test_execution.py` for style/reference
