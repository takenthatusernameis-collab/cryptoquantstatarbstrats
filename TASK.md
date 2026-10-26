# Task for Next Agent

## Context
Reporting and visualization utilities have been added:
- `utils/reporting.py` provides `generate_report`, `report_to_dict`, and `plot_equity_curve` (matplotlib is optional/lazily imported).
- `examples/compare.py` prints text reports and saves plots to `examples/reports/`.
- `tests/test_reporting.py` covers reporting utilities; all 23 tests pass, ruff clean.

Current state: 23 tests pass, ruff clean, `examples/compare.py` and `examples/optimize.py` run successfully.

## Task
**Enhance risk reporting and add CLI summary.**

### Requirements
1. Extend `utils/reporting.py`:
   - Add `generate_risk_report(result: dict) -> str` — human-readable risk summary including VaR, CVaR, max drawdown, max drawdown duration, and Calmar ratio. Format as a clean table-like text block.
   - Add `risk_report_to_dict(result: dict) -> dict` — serializable dict with keys `var`, `cvar`, `max_drawdown`, `max_drawdown_duration`, `calmar_ratio` (all float/int/str only).
   - Update `report_to_dict` to be compatible (already exists) but ensure both functions are exported and work with missing keys gracefully (default to 0).
2. Add a simple CLI entry point `examples/risk_report.py` that:
   - Loads sample data, runs a quick backtest (e.g., MeanReversionStrategy on BTC), generates both full and risk reports, and prints them.
   - Creates `examples/reports/` if needed and saves risk report to `examples/reports/risk_report.txt`.
3. Add tests in `tests/test_reporting.py` for `generate_risk_report` and `risk_report_to_dict` (basic sanity checks).
4. Keep ruff clean and all tests green; do not modify `.github/workflows/main.yml`.

### Verification
```bash
python3 -m pytest tests/ -v
python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python3 examples/risk_report.py
```
