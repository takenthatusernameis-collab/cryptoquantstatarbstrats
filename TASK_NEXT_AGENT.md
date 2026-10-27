# Task for Next Agent

## Status
All tasks complete and verified (251 tests pass, ruff clean, mypy clean on backtest/strategies/utils/). Monte Carlo robustness analysis is wired into CLI (`--monte-carlo N`) with summary report and JSON artifact output.

## Next task for the next agent
No assigned next task. Suggested next steps:
1. Add Monte Carlo integration tests in `tests/test_cli.py` covering `--monte-carlo` flag output.
2. Extend Monte Carlo to output percentile CI for drawdowns and risk-of-ruin metrics.
3. Add notebook demonstrating Monte Carlo robustness.

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
