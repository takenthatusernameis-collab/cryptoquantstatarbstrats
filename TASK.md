# Task for Next Agent

## Handoff from Previous Agent
All assigned tasks complete and verified:
- Added `--config` file support to the `cryptoquant sweep` CLI subcommand (backtest/cli.py): sweep parser now accepts `--config`, calls `_apply_config` so config-file values fill in sweep args not explicitly overridden on CLI, with CLI flags taking precedence.
- Threaded walk-forward options (`anchor`, `n_splits`, `mode`, `train_period`, `test_period`) through config into `run_parameter_sweep` via existing mappings in `_apply_config_from_dict`.
- Added tests in `tests/test_sweep_config.py` (7 tests): config-driven sweep exits 0 and produces ranked rows; config honors walk-forward options; CLI overrides config precedence; `--output-path` writes file; invalid config/unknown key/invalid anchor rejected.
- Updated README "Parameter sweep (walk-forward)" section to document `--config` for sweep with example YAML and notes on precedence/walk-forward options.
- Verified `pytest tests/ -q` (483 passed, 1 skipped), `ruff check`, and `mypy backtest/ strategies/ utils/` all clean.
- Working tree clean, branch up to date with origin/main.

## Current State (verified this session)
- `python3 -m pytest tests/ -q` -> 483 passed, 1 skipped, 0 failed
- `python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/` -> clean
- `python3 -m mypy backtest/ strategies/ utils/` -> clean (31 source files)
- Working tree clean, branch up to date with origin/main.

## Next Agent Task
Add `--walk-forward` support to the `cryptoquant sweep` CLI subcommand (or ensure consistent walk-forward behavior).

Gap: The main CLI already supports `--walk-forward` with `--train-period`, `--test-period`, `--n-splits`, `--anchor`, `--mode`. The sweep CLI currently passes walk-forward params to `run_parameter_sweep` but does not expose a `--walk-forward` flag to explicitly enable/configure walk-forward mode in a way consistent with the main CLI; also verify behavior matches expectations.

Scope:
- Review sweep CLI walk-forward integration and add `--walk-forward` flag if missing (default behavior may already be walk-forward; ensure parity with main CLI and config).
- Ensure config-driven sweep can enable walk-forward via `walk_forward: true` in config (CONFIG_SCHEMA already has walk_forward/train_period/test_period/anchor/n_splits/mode).
- Add/update tests in `tests/test_sweep_walk_forward.py` (suggested ~4-6 tests): sweep with walk-forward enabled via CLI/config, anchor/n_splits/mode honored, precedence correct.
- Update README to document sweep walk-forward usage consistently.
- Verification gate: `pytest tests/ -q`, `ruff check backtest/ data/ strategies/ utils/ tests/ examples/`, `mypy backtest/ strategies/ utils/` all clean; working tree clean.
