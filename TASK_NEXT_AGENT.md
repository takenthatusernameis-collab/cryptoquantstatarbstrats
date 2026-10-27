# Task for Next Agent

## Assigned task
Implement a limit-order book (LOB) execution model in `backtest/execution.py`.

### Requirements
1. Add `LimitOrderBookExecution` class following the existing execution interface (see `MarketExecution`, `LimitExecution`, `VWAPExecution`, `TWAPExecution`, `IcebergExecution`).
2. Support parameters: `depth_levels` (number of price levels to consume), `market_impact_bps` (price impact per unit of size consumed from the book), `slippage_bps`, and optional `participation_rate`.
3. Behavior: walk the book consuming price levels up to `depth_levels`, applying market impact to fill price, respecting volume-tied fills and OHLC passthrough where applicable. Partial fills when book depth is insufficient.
4. Integrate cleanly with existing order/fill logic (no breaking changes to other execution models). Register `order_type == "lob"` in `ExecutionSimulator.simulate_order` and route to a `_simulate_lob` helper.
5. Add unit tests in `tests/test_execution_lob.py` covering: single-level fill, multi-level walk with market impact, partial fill when depth insufficient, price impact direction (buy pushes price up, sell pushes price down).

## Acceptance criteria
- `python3 -m pytest tests/test_execution_lob.py -v` passes
- `python3 -m pytest tests/ -q` passes (no regressions)
- `python3 -m ruff check backtest/execution.py tests/test_execution_lob.py` clean
- `python3 -m mypy backtest/execution.py` clean

## Context
- Implementation patterns: `backtest/execution.py` (`ExecutionSimulator`, `_simulate_iceberg`, existing dataclasses), `backtest/engine.py` (how executions are used).
- Volume/partial fills: see `_simulate_iceberg` / `VolumeTiedMixin`-related logic.
- Tests: `tests/test_execution_iceberg.py` and `tests/test_execution_vwap_twap.py` for style/reference.

## Prior completed task (reference)
Iceberg execution model (`IcebergExecution` + `_simulate_iceberg` + `order_type="iceberg"`) complete with tests in `tests/test_execution_iceberg.py`; ruff and mypy clean, 186 tests pass.
