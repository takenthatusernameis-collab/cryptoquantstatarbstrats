# Task for Next Agent

## Status
Walk-forward portfolio reoptimization is complete and verified:
- `utils/optimization.py` exposes optimizer callables (`equal_weight`, `inverse_volatility`, `risk_parity`, `min_variance`, `mean_variance` via `get_optimizer`).
- `BacktestEngine.walk_forward_portfolio` exercises the `reoptimize`/`optimizer` path end-to-end with per-window weight alignment.
- CLI flags `--reoptimize`/`--optimizer` wired through `build_parser()`/`main()`/`_apply_config` to `walk_forward_portfolio`.
- Config keys `reoptimize`/`optimizer` (and aliases) in `backtest/config.py` `CONFIG_SCHEMA`/`validate_config`.
- `tests/test_walk_forward_reoptimize.py` covers optimizers, backward compatibility, weight alignment, and CLI/config driving.
- Verified: 278 tests pass (1 skipped), `ruff check` clean, `mypy backtest/ strategies/ utils/` clean.

## Next task for the next agent

### Make `--reoptimize`/`--optimizer` effective with `--walk-forward` without requiring `--rebalance-frequency`

In `backtest/cli.py`, the `if walk_forward:` block only calls
`engine.walk_forward_portfolio(..., reoptimize=..., optimizer=...)` when
`rebalance_freq` is set. Without `--rebalance-frequency`, it falls through to
`engine.walk_forward` (strategy-based) and silently ignores `--reoptimize`/
`--optimizer`.

### Objective
Route `--walk-forward --reoptimize --optimizer <name>` through
`walk_forward_portfolio` using signal-derived weights (no rebalancing) even
when `--rebalance-frequency` is not set, while preserving current behavior when
`--reoptimize` is not set.

### Requirements
1. `backtest/cli.py`: when `--walk-forward` and `--reoptimize` are set, build
   signal-derived weights and call `engine.walk_forward_portfolio` with
   `reoptimize=True` and the resolved optimizer, regardless of
   `--rebalance-frequency`. Keep the existing `rebalance_freq` branch behavior
   (rebalanced weights + reoptimize) unchanged.
2. `--walk-forward` without `--reoptimize` keeps current behavior
   (`engine.walk_forward` strategy-based) — backward compatible.
3. Existing CLI flags (`--reoptimize`, `--optimizer`) and config keys
   (`reoptimize`, `optimizer`) already exist; no new flags/schema keys needed.
4. Add tests in `tests/test_walk_forward_reoptimize.py` covering: CLI
   reoptimize without `--rebalance-frequency` runs end-to-end, optimizer is
   applied (weights differ from static), backward compatibility when
   `--reoptimize` not set, and config-driven reoptimize without
   `rebalance_frequency`.
5. Keep public API backward compatible; all existing tests must still pass.
6. Follow existing code style (4-space indent, `from __future__ import
   annotations`, type hints on public functions); no `# type: ignore` for real
   bugs.

### Verification
```bash
python3 -m pytest tests/ -q
python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python3 -m mypy backtest/ strategies/ utils/
```
