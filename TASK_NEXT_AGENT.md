# Task for Next Agent

## Status
The previous agent's assigned task (options/volatility-surface strategy) is complete and verified:
- `strategies/volatility_surface.py`: `VolatilitySurfaceStrategy(Strategy)` trading on IV percentile-rank signals (long when IV depressed, short when elevated, exit on reversion), following the `Strategy` base-class contract (`generate_signals` / `calculate_position_sizes`).
- Exported from `strategies/__init__.py`.
- `tests/test_volatility_surface.py`: 3 tests covering signal generation columns, position sizes, and end-to-end `BacktestEngine.run`.
- Verified: 238 tests pass (1 skipped), `ruff check` clean, `mypy backtest/ strategies/ utils/` clean.

## Next task for the next agent
Add a volatility term-structure mean-reversion strategy.

### Task: Add a term-structure / calendar spread strategy
- Create `strategies/term_structure.py` with `TermStructureStrategy(Strategy)`.
- Trade mean-reversion between near-term and long-term implied volatility (or realized/IV spread). When the spread (long - short, or vice versa) widens beyond a threshold relative to its rolling mean/z-score, take a spread trade expecting convergence; flatten on reversion.
- Follow the existing `Strategy` base-class contract (`generate_signals` / `calculate_position_sizes`).
- Support configurable parameters (e.g., `near_tenor`, `far_tenor`, `lookback`, `entry_threshold`, `exit_threshold`) and work with multi-column data where IV term structure is provided as columns like `iv_30d`, `iv_90d` (or similar). If those columns don't exist, the strategy should be robust or clearly raise informative errors consistent with codebase style.
- Export it from `strategies/__init__.py`.
- Add `tests/test_term_structure.py` covering signal generation columns, position sizes, and an end-to-end `BacktestEngine.run` run.
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
