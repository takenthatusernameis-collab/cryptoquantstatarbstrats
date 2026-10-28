# Task for Next Agent

## Handoff from Previous Agent
All assigned tasks complete and verified:
- Walk-forward anchoring control (`anchor` date / origin index) added to `engine.walk_forward` and threaded through `run_parameter_sweep` and CLI (`--anchor`).

## Current State
- `python3 -m pytest tests/ -q` -> 448 passed, 1 skipped, 0 failed
- `python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/` -> clean
- Working tree clean, branch up to date with origin/main.

## Next Agent Task (suggested)
Add `n_splits`/`anchor` validation and tests for invalid anchor values; thread `anchor` into direct CLI walk-forward calls (`engine.walk_forward`), with tests.
