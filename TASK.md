# Task for Next Agent

## Handoff from Previous Agent
All assigned tasks complete and verified:
- Walk-forward anchoring control (`anchor` date / origin index) added to `engine.walk_forward` and `engine.walk_forward_portfolio`, threaded through `run_parameter_sweep` and CLI (`--anchor` / `--n-splits`).
- Added `anchor` validation (rejects booleans, non-integral floats, and unparseable timestamp strings; clamps negative offsets to 0) to `engine.walk_forward`, `engine.walk_forward_portfolio`, and `run_parameter_sweep`.
- Added `tests/test_walk_forward_anchor.py` (12 tests): valid int/timestamp/None anchors, invalid anchor rejection for engine, portfolio, sweep, and CLI (`--anchor`).
- Documented CLI walk-forward `--anchor`/`--n-splits`/`--mode` options in the README parameter sweep section (and programmatic API).
- Added config-file (`--config`) walk-forward tests exercising `anchor`/`n_splits` through `_apply_config_from_dict` in `tests/test_config_validation.py` (`test_apply_config_from_dict_walk_forward`, `test_apply_config_from_dict_walk_forward_anchor_and_n_splits_via_config_file`).
- Added end-to-end CLI `--config` walk-forward integration test `tests/test_walk_forward_config.py` (7 tests): runs `main(["--config", ...])` with `--walk-forward`, `anchor`, `n_splits`, `mode` through `_apply_config_from_dict`, asserting exit code 0 and that returned window counts reflect anchor/n_splits; added config-vs-CLI precedence test verifying CLI `--anchor`/`--n-splits`/`--mode` override config values.
- Added `--mode` to main CLI parser; normalized None mode handling in CLI; improved anchor parsing to accept numeric strings (e.g., `"0"`).
- Verified `pytest`, `ruff`, and `mypy` remain clean.
- Verified walk-forward portfolio path (`engine.walk_forward_portfolio`) already validates and threads `anchor`/`n_splits`/`mode`; CLI portfolio path (`rebalance_freq`) passes them through (backtest/cli.py:1159-1161, 1178-1182); `_apply_config_from_dict` covers `anchor`/`n_splits`/`mode`.

## Current State (verified this session)
- `python3 -m pytest tests/ -q` -> 476 passed, 1 skipped, 0 failed
- `python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/` -> clean
- `python3 -m mypy backtest/ strategies/ utils/` -> clean (31 source files)
- Working tree clean, branch up to date with origin/main.

## Next Agent Task
Add `--config` file support to the `cryptoquant sweep` CLI subcommand.

Gap: `cryptoquant sweep` (backtest/cli.py:587-705) builds its own `argparse.ArgumentParser` and never calls `_apply_config`/`load_config`, so `--config` is unsupported for sweep — unlike the main backtest path. CONFIG_SCHEMA already covers all sweep-relevant keys (`strategy`, `asset`, `pair`, `symbols`, `start`, `end`, `freq`, `data_source`, `data_csv`, `train_period`/`trainPeriod`, `test_period`/`testPeriod`, `metric`, `fee_rate`, `slippage`, `mode`, `n_splits`/`nSplits`, `anchor`, `output`, `output_path`).

Scope:
- Add a `--config` option to the `sweep` subparser and call `_apply_config` (or an equivalent config-apply step) so config-file values fill in any sweep arg not explicitly overridden on the CLI, with CLI flags winning.
- Thread walk-forward options (`anchor`, `n_splits`, `mode`, `train_period`, `test_period`) through config into `run_parameter_sweep`.
- Add tests in `tests/test_sweep_config.py` (suggested ~6-8 tests): config-driven sweep exits 0 and produces ranked rows; config `anchor`/`n_splits`/`mode`/`train_period`/`test_period` honored; config-vs-CLI precedence (CLI `--anchor`/`--n-splits`/`--mode` override config); invalid config rejected; invalid anchor via sweep config rejected.
- Update README "Parameter sweep (walk-forward)" section to document `--config` for sweep.
- Verification gate: `pytest tests/ -q`, `ruff check backtest/ data/ strategies/ utils/ tests/ examples/`, `mypy backtest/ strategies/ utils/` all clean; working tree clean.

No further walk-forward changes are required.
