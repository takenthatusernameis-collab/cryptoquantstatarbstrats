# Task for Next Agent

## Context
The crypto stat-arb framework is fully implemented and verified:
- 12 tests pass, ruff clean, `examples/compare.py` runs.

## Task
**Add transaction-cost modeling and walk-forward validation to the backtest engine, plus risk metrics.**

### Requirements
1. `BacktestEngine.run` accepts `fee_rate` and `slippage` params; subtract costs from portfolio returns.
2. Add `walk_forward` method splitting data into train/test windows.
3. Add `max_drawdown_duration`, `calmar_ratio` to result dict.
4. Tests in `tests/test_strategies.py` for costs reduce returns and walk-forward returns dict.
5. Update `examples/compare.py` to print new metrics.

### Constraints
- Keep ruff clean and all tests green.
- Do not modify `.github/workflows/main.yml`.

### Verification
```bash
python3 -m pytest tests/ -v
python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python3 examples/compare.py
```
