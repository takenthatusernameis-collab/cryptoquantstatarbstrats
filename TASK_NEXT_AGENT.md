# Task for Next Agent

## Status
All tasks complete and verified (243 tests pass, ruff clean, mypy clean on backtest/strategies/utils/). CLI/config integration for `TermStructureStrategy` is wired and tested.

## Next task for the next agent
Monte Carlo robustness analysis for strategy equity curves:
1. Add `utils/monte_carlo.py` with a function to bootstrap trade returns / shuffle trade sequences and compute distribution of final equity, max drawdown, and Sharpe.
2. Integrate into `BacktestEngine` or CLI as `--monte-carlo N` producing a summary report.
3. Add tests in `tests/test_monte_carlo.py`.

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
