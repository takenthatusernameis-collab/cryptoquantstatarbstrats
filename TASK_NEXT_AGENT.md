# Task for Next Agent

## Status
The previous agent's assigned task (config schema validation) is complete and verified:
- `backtest/config.py`: `ConfigValidationError`, `CONFIG_SCHEMA`, and `validate_config(config)` added; all CLI keys + aliases validated (type/choice/range).
- `backtest/cli.py`: `_apply_config` calls `validate_config` and surfaces errors via `parser.error` (exit code 2).
- `tests/test_config_validation.py`: 21 tests covering valid/invalid/unknown/normalized configs.
- Verified: 235 tests pass (1 skipped), `ruff check` clean, `mypy backtest/ strategies/ utils/` clean.

## Next task for the next agent
No assigned task pending. Concrete next step: add a new strategy module complementing the existing mean-reversion, momentum, pairs, and cross-exchange strategies.

### Task: Add an options/volatility-surface strategy
- Create `strategies/volatility_surface.py` with a `VolatilitySurfaceStrategy(Strategy)` that trades on implied-volatility surface signals (e.g., IV percentile rank relative to rolling mean; long when IV is depressed vs. its regime, short when elevated, exit on reversion), following the existing `Strategy` base-class contract (`generate_signals` / `calculate_position_sizes`).
- Export it from `strategies/__init__.py`.
- Add `tests/test_volatility_surface.py` covering signal generation columns, position sizes, and an end-to-end `BacktestEngine.run` run.
- Verify public API stays backward compatible; do not modify existing strategy modules.

### Verification
```bash
python3 -m pytest tests/ -q
python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python3 -m mypy backtest/ strategies/ utils/
```

## Constraints
- Follow existing code style (4-space indent, `from __future__ import annotations`, type hints on public functions).
- Keep public API backward compatible.
- All existing tests must still pass; ruff and mypy must remain clean.
- Do not add `# type: ignore` to suppress real bugs.

**Ready for next agent.**
