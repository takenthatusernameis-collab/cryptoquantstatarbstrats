# Task for Next Agent

## Status
The previous agent's assigned task (regime detection integration with the backtest engine) is complete and verified:
- `backtest/engine.py`: `_apply_regime_gating` gates weights by `regime_signal` or `regime_mode="trend"` across `run`/`run_portfolio`/`walk_forward`/`walk_forward_portfolio`.
- `backtest/cli.py`: `--regime-mode` and `--regime-lookback` flags wired through all engine paths.
- `backtest/config.py`: `regime_mode`/`regime_lookback` config keys mapped in `_apply_config`.
- `tests/test_regime_integration.py`: 10 tests covering regime gating, no-op when disabled, backward compatibility, run_portfolio, walk_forward, walk_forward_portfolio.
- Fixed 2 pre-existing ruff issues in `backtest/engine.py` (unused `mode` variable, over-long comment).
- Verified: 211 tests pass (1 skipped), `ruff check` clean, `mypy backtest/ strategies/ utils/` clean.

## Assigned task (next)
Extend regime-aware gating to support volatility-based regimes.

### Requirements
1. Add a `regime_vol_mode` parameter (e.g. `"low_vol"`) to `BacktestEngine.run`/`run_portfolio`/`walk_forward`/`walk_forward_portfolio` that gates trading to low-volatility regimes using `utils.regime.volatility_regime`.
2. Expose via the CLI (`--regime-vol-mode`) and the config layer (`backtest/config.py`).
3. Add tests in `tests/test_regime_integration.py` covering low-vol gating, combination with trend mode, and backward compatibility.
4. Keep public API backward compatible; all existing tests must still pass; ruff and mypy clean.

### Acceptance criteria
- `python3 -m pytest tests/test_regime_integration.py -v` passes
- `python3 -m pytest tests/ -q` passes (no regressions)
- `python3 -m ruff check backtest/ strategies/ utils/ tests/` clean
- `python3 -m mypy backtest/ strategies/ utils/` clean

### Context
- Regime utilities: `utils/regime.py` (rolling volatility regimes via `volatility_regime`, trend detection via `trend_detection`) already present with tests.
- Engine entry points: `backtest/engine.py` `BacktestEngine.run`, `run_portfolio`, `walk_forward`, `walk_forward_portfolio`.
- CLI: `backtest/cli.py` (`main`), config: `backtest/config.py` (`load_config`).
- Existing regime trend gating is in `backtest/engine.py::_apply_regime_gating`.

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
