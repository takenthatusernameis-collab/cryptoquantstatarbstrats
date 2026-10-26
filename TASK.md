# Task for Next Agent

## Status: COMPLETE (2026-10-26)

All requirements from the previous task have been implemented and verified:

- `utils/metrics.py` now includes a `sharpe_ratio` helper alongside sortino/var/cvar/max_drawdown_duration.
- Verification passed: 26 tests pass, ruff clean.

## Current State
- 26 tests pass, ruff clean.

## Next Steps
- Wire `sharpe_ratio` into the backtest engine and reporting layer for consistency (engine currently computes sharpe inline).
- Add unit tests for `sharpe_ratio` in tests/test_metrics.py (new).
