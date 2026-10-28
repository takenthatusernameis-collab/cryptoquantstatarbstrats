# Task for Next Agent

## Handoff from Previous Agent
All assigned tasks complete and verified:
- Walk-forward anchoring control (`anchor` date / origin index) added to `engine.walk_forward` and `engine.walk_forward_portfolio`, threaded through `run_parameter_sweep` and CLI (`--anchor` / `--n-splits`).
- Added `anchor` validation (rejects booleans, non-integral floats, and unparseable timestamp strings; clamps negative offsets to 0) to `engine.walk_forward`, `engine.walk_forward_portfolio`, and `run_parameter_sweep`.
- Added `tests/test_walk_forward_anchor.py` (12 tests): valid int/timestamp/None anchors, invalid anchor rejection for engine, portfolio, sweep, and CLI (`--anchor`).
- Documented CLI walk-forward `--anchor`/`--n-splits`/`--mode` options in the README parameter sweep section (and programmatic API).
- Added config-file (`--config`) walk-forward tests exercising `anchor`/`n_splits` through `_apply_config_from_dict` in `tests/test_config_validation.py` (`test_apply_config_from_dict_walk_forward`, `test_apply_config_from_dict_walk_forward_anchor_and_n_splits_via_config_file`).

## This Agent
- Added end-to-end CLI `--config` walk-forward integration test `tests/test_walk_forward_config.py` (6 tests): runs `main(["--config", ...])` with `--walk-forward`, `anchor`, `n_splits`, `mode` through `_apply_config_from_dict`, asserting exit code 0 and that returned window counts reflect anchor/n_splits (default None -> 3, anchor=40 -> 2, n_splits=2 cap -> 2, combined -> 1, mode=expanding runs, invalid anchor raises).
- Verified `pytest`, `ruff`, and `mypy` remain clean.

## Current State
- `python3 -m pytest tests/ -q` -> 468 passed, 1 skipped, 0 failed
- `python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/` -> clean
- `python3 -m mypy backtest/ strategies/ utils/` -> clean
- Working tree clean, branch up to date with origin/main.

## Next Agent Task (suggested)
Add an end-to-end CLI test asserting config-vs-CLI precedence: an explicit CLI `--anchor`/`--n-splits`/`--mode` overrides the config-file value through `_apply_config_from_dict` (run `main(["--config", ..., "--anchor", ...])`), asserting exit code 0 and that the returned window counts reflect the CLI override, not the config value. Then verify `pytest`, `ruff`, and `mypy` remain clean and update TASK.md.
