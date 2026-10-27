# Task for Next Agent

## Status
All previous tasks complete and verified (267 tests pass, 1 skipped, ruff/mypy clean). Monte Carlo robustness analysis reports percentile confidence intervals for max drawdown (ci95/ci99) and risk-of-ruin metrics; CLI displays them in text output and writes JSON artifact. Strategy performance attribution (`utils/attribution.py`: `brinson_attribution`, `factor_attribution`) is implemented, wired into `BacktestEngine`, `utils/reporting.py`, the CLI (`--benchmark-weights-csv`/`--factor-returns-csv`), and `backtest/config.py` schema; comprehensive tests added in `tests/test_attribution.py` (15 tests).

## Next task for the next agent

### Walk-forward portfolio reoptimization

Wire the `reoptimize`/`optimizer` path of `BacktestEngine.walk_forward_portfolio` (already accepted but unused) through the portfolio optimization utilities in `utils/optimization.py` so each train window re-derives optimal weights instead of reusing static weights.

### Objective
Enable re-optimizing portfolio weights on each walk-forward train window, configurable via CLI and config, with tests.

### Requirements
1. Expose optimizer callables in `utils/optimization.py` (or a new `utils/walk_forward_optimize.py`) that accept `train_data` and return a weights DataFrame/Series aligned to assets (e.g. mean-variance, risk-parity, equal-weight).
2. `BacktestEngine.walk_forward_portfolio` already accepts `reoptimize: bool` and `optimizer`; ensure the path is exercised end-to-end and weights are reindexed/aligned to each test window.
3. Add CLI flags: `--reoptimize` (bool) and `--optimizer` (choice of available optimizers), wired through `backtest/cli.py` `build_parser()`/`main()`/`_apply_config` to `walk_forward_portfolio`.
4. Add config keys: `reoptimize`, `optimizer` (and aliases) to `backtest/config.py` `CONFIG_SCHEMA`/`validate_config`.
5. Add comprehensive tests in `tests/test_walk_forward_reoptimize.py` covering: reoptimize=True/False, each optimizer, backward compatibility (static weights when reoptimize=False), CLI/config driving, and weight alignment per window.
6. Keep public API backward compatible; all existing tests must still pass.

### Constraints
- Follow existing code style (4-space indent, `from __future__ import annotations`, type hints on public functions).
- Keep public API backward compatible.
- All existing tests must still pass; ruff and mypy must remain clean.
- Do not add `# type: ignore` to suppress real bugs.

### Verification
```bash
python3 -m pytest tests/ -q
python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python3 -m mypy backtest/ strategies/ utils/
```

### Notes
`walk_forward_portfolio` in `backtest/engine.py:685` already accepts `reoptimize` and `optimizer` but no CLI/config wiring or optimizer implementations exist yet; `utils/optimization.py` already has portfolio optimization utilities to build on.
