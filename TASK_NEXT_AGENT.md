# Task for Next Agent

## Status
The previous agent's assigned task (volatility term-structure / calendar spread mean-reversion strategy) is complete and verified:
- `strategies/term_structure.py`: `TermStructureStrategy(Strategy)` trading on IV term-structure spread mean-reversion (spread = far - near tenor; entry/exit on rolling z-score). Robust column resolution with informative error on missing columns; emits a per-asset weight column so auxiliary IV columns are not mistaken for tradable assets.
- Exported from `strategies/__init__.py`.
- `tests/test_term_structure.py`: 5 tests covering signal generation columns, position sizes, end-to-end `BacktestEngine.run`, missing-column error path, and custom tenor aliases.
- Verified: 243 tests pass (1 skipped), `ruff check` clean, `mypy backtest/ strategies/ utils/` clean.

## Next task for the next agent
Add a Jupyter notebook demonstrating the term-structure strategy end-to-end.

### Task: `notebooks/term_structure_strategy.ipynb`
Create a notebook in `notebooks/` that demonstrates `TermStructureStrategy`:
- Generate or load synthetic IV term-structure data (near-term vs far-term IV columns, e.g. `iv_30d` / `iv_90d`).
- Instantiate `TermStructureStrategy` with configurable parameters (`near_tenor`, `far_tenor`, `lookback`, `entry_threshold`, `exit_threshold`).
- Run `BacktestEngine.run` (optionally with `run_with_benchmark` for a buy-and-hold comparison) and display the result metrics.
- Plot the spread, its rolling z-score with entry/exit thresholds, and the equity curve vs. benchmark.
- Keep cells executable and self-contained (no external data downloads; use synthetic data with a fixed seed for reproducibility).

### Suggested follow-up (optional, if time permits)
- Wire `TermStructureStrategy` through the CLI/config layer (`backtest/cli.py`, `backtest/config.py`) so it can be driven by `--strategy term_structure` and config files, with tests in `tests/test_cli.py`.
- Add execution-model support (VWAP/TWAP/LOB) to the notebook via `--order-type` / `ExecutionSimulator`.

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