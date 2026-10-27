# Task for Next Agent

## Status
The previous agent's assigned task (options/volatility-surface strategy) is complete and verified:
- `strategies/volatility_surface.py`: `VolatilitySurfaceStrategy(Strategy)` trading on IV percentile-rank signals (long when IV depressed, short when elevated, exit on reversion), following the `Strategy` base-class contract (`generate_signals` / `calculate_position_sizes`).
- Exported from `strategies/__init__.py`.
- `tests/test_volatility_surface.py`: 3 tests covering signal generation columns, position sizes, and end-to-end `BacktestEngine.run`.
- Verified: 238 tests pass (1 skipped), `ruff check` clean, `mypy backtest/ strategies/ utils/` clean.

## Next task for the next agent
No assigned task pending. Suggested next steps (pick one):
- Add a new strategy module complementing existing ones (e.g., statistical arbitrage / mean-reversion of volatility term structure).
- Extend execution models or reporting artifacts.
- Improve notebook coverage / docs.

## Verification
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
