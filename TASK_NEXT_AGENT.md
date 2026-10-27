# Task for Next Agent

## Status
All tasks complete and verified (252 tests pass, 1 skipped, ruff/mypy clean). Monte Carlo robustness analysis is wired into CLI (`--monte-carlo N`) with summary report and JSON artifact output. Integration test added for `--monte-carlo` flag output.

## Next task for the next agent
Extend Monte Carlo robustness analysis with additional risk metrics.

### Objective
Enhance `utils/monte_carlo.py` and its CLI integration to report percentile confidence intervals for drawdowns and risk-of-ruin metrics.

### Tasks
1. **Extend Monte Carlo results** in `utils/monte_carlo.py`:
- Add `max_drawdown_ci` (e.g. percentiles like 5th/50th/95th of max drawdown across simulations) to results
- Add risk-of-ruin metric (probability of breaching a drawdown threshold, configurable, default reasonable threshold)
- Keep existing API backward compatible (add optional fields)
2. **Update CLI** in `backtest/cli.py` to display the new metrics in both text and JSON outputs
3. **Update/add tests** in `tests/test_monte_carlo.py` (and/or CLI tests) to cover the new metrics
4. **Verify**: all tests pass, ruff and mypy clean

### Implementation hints
- For each simulation, compute max drawdown (can reuse logic from existing metrics)
- Risk-of-ruin: count fraction of simulations where drawdown exceeds threshold (e.g., 20% or configurable)
- Return in summary structure; update `report_to_dict` if needed or just ensure CLI formats correctly

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
