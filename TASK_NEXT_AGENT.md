# Task for Next Agent

## Assigned task
Enhance the LOB execution model with per-level liquidity and queue position effects.

### Requirements
1. Extend `LimitOrderBookExecution` to support per-level configuration: allow passing `level_liquidity` (list/array of quantities available at each price level) and `queue_position` (fraction 0-1 indicating position in queue at first level).
2. Update `ExecutionSimulator._simulate_lob` to consume liquidity level-by-level: for each of the first `depth_levels` levels, consume up to the level's available liquidity (or remaining order quantity), applying `market_impact_bps` per level consumed. If `level_liquidity` not provided, fall back to the current volume-proxy logic for backward compatibility.
3. Apply queue position penalty/constraint: when `queue_position` is provided and > 0, the order may only fill from the portion behind queue (reduce fillable by queue position) before consuming subsequent levels; this affects partial fills when queue is long.
4. Register/accept parameters via `ExecutionSimulator` (add `lob_level_liquidity`, `lob_queue_position` fields) and pass through cleanly.
5. Add unit tests in `tests/test_execution_lob_enhanced.py` covering: per-level liquidity enforcement, multi-level consumption with different liquidity per level, queue position reducing fills, and backward compatibility when enhanced params not provided.

## Acceptance criteria
- `python3 -m pytest tests/test_execution_lob_enhanced.py -v` passes
- `python3 -m pytest tests/ -q` passes (no regressions)
- `python3 -m ruff check backtest/execution.py tests/test_execution_lob_enhanced.py` clean
- `python3 -m mypy backtest/execution.py` clean

## Context
- Implementation patterns: `backtest/execution.py` (`LimitOrderBookExecution`, `_simulate_lob`, `ExecutionSimulator`), existing LOB tests in `tests/test_execution_lob.py`.
- Volume/partial fills: see current `_simulate_lob` logic for volume caps and depth limits.
- Keep public API backward compatible - all existing behavior must remain unchanged when new params are not specified.

## Prior completed task (reference)
Limit order book execution model (`LimitOrderBookExecution` + `_simulate_lob` + `order_type="lob"`) complete with tests in `tests/test_execution_lob.py`; ruff and mypy clean, 190 tests pass.

## Verification
```bash
python3 -m pytest tests/test_execution_lob_enhanced.py -v
python3 -m pytest tests/ -q
python3 -m ruff check backtest/execution.py tests/test_execution_lob_enhanced.py
python3 -m mypy backtest/execution.py
```
