# Task for Next Agent

## Status
All previous tasks complete and verified (252 tests pass, 1 skipped, ruff/mypy clean). Monte Carlo robustness analysis reports percentile confidence intervals for max drawdown (ci95/ci99) and risk-of-ruin metrics; CLI displays them in text output and writes JSON artifact.

## Next task for the next agent
**Add strategy performance attribution & factor decomposition**

### Objective
Implement portfolio/strategy performance attribution (Brinson-like or regression-based factor attribution) and integrate into reporting/CLI.

### Requirements
1. Add `utils/attribution.py` with:
   - `brinson_attribution(returns, weights, benchmark_weights, asset_returns)` returning allocation/selection/interaction effects
   - `factor_attribution(returns, factor_returns, ...)` using regression (e.g. CAPM/multi-factor) to decompose alpha/beta/exposures
   - Robust handling of missing data, alignment by dates
2. Integrate into `BacktestEngine` or post-processing to attach attribution results when benchmark/factors provided
3. Extend `utils/reporting.py` (`generate_report`/`generate_risk_report`/HTML/PDF) to display attribution tables/summary
4. Add CLI flags: `--benchmark-weights-csv`, `--factor-returns-csv` (and optional config keys) to drive attribution
5. Add comprehensive tests in `tests/test_attribution.py` and CLI tests if wired
6. Keep public API backward compatible; all existing tests must still pass

### Constraints
- Follow existing code style (4-space indent, `from __future__ import annotations`, type hints on public functions)
- Keep public API backward compatible
- All existing tests must still pass; ruff and mypy must remain clean
- Do not add `# type: ignore` to suppress real bugs

### Verification
```bash
python3 -m pytest tests/ -q
python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python3 -m mypy backtest/ strategies/ utils/
```

## Notes
Repository is currently clean and all checks pass. This is a suggested next enhancement building on existing reporting/CLI infrastructure.
