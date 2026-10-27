# Task for Next Agent

## Context
All work assigned in previous rounds is complete and verified:

- 180 tests pass, ruff clean, mypy clean on backtest/strategies/utils/.
- CI workflow present and green.
- Framework feature-complete (portfolio optimization, execution sim, VWAP/TWAP, OHLC, rebalancing, benchmark, walk-forward reporting, HTML/PDF artifacts, CLI/config).

## Observed minor issue
`utils/rebalance.py:31` emits `Pandas4Warning: 'w' is deprecated... use 'W'` during test runs. Not a failure but should be cleaned up.

## Next task for the next agent
1. Fix the pandas deprecation in `utils/rebalance.py` (use frequency `'W'` instead of `'w'`) so tests run warning-free.
2. Verify no other deprecated pandas frequency strings or APIs are used across `backtest/`, `strategies/`, `utils/`.
3. Optionally add a test asserting rebalancing runs without warnings (`pytest -W error`).

### Acceptance criteria
- [ ] `utils/rebalance.py` no longer emits `Pandas4Warning`.
- [ ] `python3 -m pytest tests/ -q -W error::DeprecationWarning` passes (or warnings filtered appropriately).
- [ ] `ruff check` and `mypy backtest/ strategies/ utils/` remain clean.
- [ ] No library API changes.

**Ready for next agent.**
