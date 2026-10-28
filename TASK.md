# Task for Next Agent

## Handoff from Previous Agent
All assigned tasks complete and verified:
- `--walk-forward` support on the `cryptoquant sweep` CLI subcommand is present and consistent with the main CLI:
  - Sweep parser accepts `--walk-forward` (and suppressed `--walk_forward` alias) at backtest/cli.py:609-617.
  - Walk-forward options (`--train-period`, `--test-period`, `--n-splits`, `--anchor`, `--mode`) are passed through to `run_parameter_sweep` at backtest/cli.py:677-690.
  - Config-driven sweep enables walk-forward via `walk_forward: true` in config; `_apply_config_from_dict` maps `walk_forward`, `train_period`, `test_period`, `anchor`, `n_splits`, `mode` (backtest/cli.py:474-479).
- Tests in `tests/test_sweep_walk_forward.py` (4 tests): walk-forward enabled via CLI flag, via config `walk_forward: true`, CLI-over-config precedence, and pairs strategy parity.
- Tests in `tests/test_sweep_config.py` (7 tests) cover config-driven sweep, walk-forward option threading, precedence, output-path, and invalid-config/unknown-key/invalid-anchor rejection.
- README "Parameter sweep (walk-forward)" section documents `--walk-forward`, config `walk_forward: true`, and all walk-forward options with YAML example and precedence notes (README.md:72-160).
- Verified `pytest tests/ -q` (487 passed, 1 skipped), `ruff check` clean, `mypy backtest/ strategies/ utils/` clean (31 source files).
- Working tree clean, branch up to date with origin/main (commit 2b96044).

## Current State (verified this session)
- `python3 -m pytest tests/ -q` -> 490 passed, 1 skipped, 0 failed
- `python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/` -> clean
- `python3 -m mypy backtest/ strategies/ utils/` -> clean (31 source files)
- Working tree clean, branch up to date with origin/main.

## Next Agent Task
Implement a walk-forward sweep "replay best" final confirmation run.

After a walk-forward sweep ranks parameter combos, add the ability to re-run the #1-ranked combo over the full dataset (single backtest via `engine.run`, backtest/engine.py:628) and emit a final performance summary so users can confirm the chosen parameters.

Scope:
- `backtest/sweep.py`: add optional `replay_best: bool = False` to `run_parameter_sweep`. When True and rows exist, rebuild the top-ranked strategy with its params and call `engine.run(strat, data, fee_rate=..., slippage=...)` over the full `data`; attach a `replay` block (params used + run metrics: total_return, sharpe_ratio, max_drawdown, calmar_ratio, final equity) to the result. Keep returned rows JSON-serializable. Validate `replay_best` is bool.
- `backtest/cli.py`: add `--replay-best` flag (store_true, default False) plus suppressed `--replay_best` alias; thread `replay_best=bool(args.replay_best)` into the `run_parameter_sweep` call at cli.py:680-693. Add config mapping in `_apply_config_from_dict` for `replay_best`.
- `tests/test_sweep_replay_best.py`: new tests — replay via CLI flag, via config `replay_best: true`, CLI-over-config precedence, and that replay uses top-ranked params / includes replay block.
- README: document `--replay-best` and config `replay_best: true` in "Parameter sweep (walk-forward)" section (README.md:72-160).
- Verify: `pytest tests/ -q`, `ruff check backtest/ data/ strategies/ utils/ tests/ examples/`, `mypy backtest/ strategies/ utils/` all clean; working tree clean, branch up to date with origin/main.

## Replay Best Implementation (COMPLETE)
- `backtest/sweep.py:129` — `replay_best: bool = False` parameter on `run_parameter_sweep`; validated at `sweep.py:206-207`.
- `backtest/sweep.py:276-298` — rebuilds top-ranked strategy via `_build_strategy`, runs `engine.run` over full data, attaches `replay` block (params, total_return, sharpe_ratio, max_drawdown, calmar_ratio, final_equity) to the top-ranked row.
- `backtest/cli.py:626-638` — `--replay-best` flag (store_true, default False) plus suppressed `--replay_best` alias.
- `backtest/cli.py:475` — config mapping `("replay_best", ("replay_best", "replayBest"))` in `_apply_config_from_dict`.
- `backtest/config.py:151-152` — schema entries for `replay_best` and `replayBest` (type bool).
- `tests/test_sweep_replay_best.py` (3 tests): replay via CLI flag, via config `replay_best: true`, CLI-over-config precedence, and that replay uses top-ranked params / includes replay block.
- README "Replay best sweep combo (full-dataset confirmation)" section documents `--replay-best`, config `replay_best: true`, YAML example, and the `replay` block fields.
- Verified: `pytest tests/ -q` (490 passed, 1 skipped), `ruff check` clean, `mypy` clean (31 source files).
- Working tree clean, branch up to date with origin/main.

(End of file)