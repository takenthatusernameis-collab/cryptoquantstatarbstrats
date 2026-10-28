# Task for Next Agent

## Handoff from Previous Agent
All assigned tasks complete and verified:
- Walk-forward anchoring control (`anchor` date / origin index) added to `engine.walk_forward` and `engine.walk_forward_portfolio`, threaded through `run_parameter_sweep` and CLI (`--anchor` / `--n-splits`).
- Added `anchor` validation (rejects booleans, non-integral floats, and unparseable timestamp strings; clamps negative offsets to 0) to `engine.walk_forward`, `engine.walk_forward_portfolio`, and `run_parameter_sweep`.
- Added `tests/test_walk_forward_anchor.py` (12 tests): valid int/timestamp/None anchors, invalid anchor rejection for engine, portfolio, sweep, and CLI (`--anchor`).

## Current State
- `python3 -m pytest tests/ -q` -> 460 passed, 1 skipped, 0 failed
- `python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/` -> clean
- `python3 -m mypy backtest/ strategies/ utils/` -> clean
- Working tree clean, branch up to date with origin/main.

## Next Agent Task (suggested)
Document the CLI walk-forward `--anchor`/`--n-splits`/`--mode` options in the README parameter sweep section (and optionally the programmatic API), and add a config-file (`--config`) walk-forward test that exercises `anchor`/`n_splits` through `_apply_config_from_dict`.
