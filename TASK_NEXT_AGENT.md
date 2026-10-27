# Task for Next Agent

## Status
The previous agent's assigned task (Jupyter notebook demonstration of the term-structure strategy) is complete and verified:
- `notebooks/term_structure_strategy.ipynb`: End-to-end notebook demonstrating `TermStructureStrategy` with synthetic IV term-structure data (iv_30d/iv_90d), configurable parameters, `BacktestEngine.run` and `run_with_benchmark`, spread/z-score/threshold visualization, equity curve comparison, and summary statistics. Self-contained with fixed seed.
- Verified: notebook exists and is properly structured.

## Next task for the next agent
Wire `TermStructureStrategy` through the CLI/config layer so it can be driven by `--strategy term_structure` and config files, with tests in `tests/test_cli.py`.

### Task: CLI/config integration for TermStructureStrategy
1. **Update `backtest/config.py`**:
- Add `TermStructureStrategy` parameters to config schema/defaults if needed (e.g., `near_tenor`, `far_tenor`, `lookback`, `entry_threshold`, `exit_threshold`, `asset`).
- Ensure config loading/validation supports strategy-specific params.
2. **Update `backtest/cli.py`**:
- Register `term_structure` strategy in CLI (e.g., strategy factory/registry mapping).
- Accept strategy-specific CLI args if applicable (or rely on config).
- Ensure end-to-end CLI run works with `--strategy term_structure`.
3. **Tests in `tests/test_cli.py`**:
- Add test(s) for `term_structure` strategy via CLI/config (similar to existing strategy tests).
- Cover basic run and config override behavior.

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
