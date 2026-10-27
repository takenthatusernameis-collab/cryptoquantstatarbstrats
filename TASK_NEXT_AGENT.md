# Task for Next Agent

## Status
The previous agent's assigned task (LOB execution model enhancement with per-level liquidity and queue position effects) is complete and verified:
- `backtest/execution.py`: `level_liquidity` / `queue_position` on `LimitOrderBookExecution`, `lob_level_liquidity` / `lob_queue_position` on `ExecutionSimulator`, level-by-level consumption with per-level market impact in `_simulate_lob`, volume-proxy fallback when `level_liquidity` is not provided.
- `tests/test_execution_lob_enhanced.py`: per-level liquidity enforcement, multi-level consumption, queue position reductions, backward compatibility.
- Verified: 201 tests pass (1 skipped), `ruff check` clean, `mypy backtest/ strategies/ utils/` clean.

## Assigned task (next)
Integrate regime detection (`utils/regime.py`) with the backtest engine so strategies can be regime-aware.

### Requirements
1. Add a regime parameter (e.g. `regime_signal` series or `regime_mode`) to `BacktestEngine.run`/`run_portfolio`/`walk_forward`/`walk_forward_portfolio` that gates strategy signals by detected regime (e.g. only trade in trending / low-volatility regimes).
2. Expose regime-aware toggles via the CLI (`--regime-mode`, `--regime-lookback`) and the config layer (`backtest/config.py`).
3. Add tests in `tests/test_regime_integration.py` covering: regime gating of signals, no-op behavior when regime detection is disabled, and backward compatibility with existing runs.
4. Keep public API backward compatible; all existing tests must still pass; ruff and mypy clean.

### Acceptance criteria
- `python3 -m pytest tests/test_regime_integration.py -v` passes
- `python3 -m pytest tests/ -q` passes (no regressions)
- `python3 -m ruff check backtest/ strategies/ utils/ tests/` clean
- `python3 -m mypy backtest/ strategies/ utils/` clean

### Context
- Regime utilities: `utils/regime.py` (rolling volatility regimes, trend detection) already present with tests.
- Engine entry points: `backtest/engine.py` `BacktestEngine.run`, `run_portfolio`, `walk_forward`, `walk_forward_portfolio`.
- CLI: `backtest/cli.py` (`main`), config: `backtest/config.py` (`load_config`).

## Constraints
- Follow existing code style (4-space indent, `from __future__ import annotations`, type hints on public functions).
- Keep public API backward compatible.
- Do not add `# type: ignore` to suppress real bugs.

## Verification
```bash
python3 -m pytest tests/ -q
python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python3 -m mypy backtest/ strategies/ utils/
```
