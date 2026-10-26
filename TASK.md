# Task for Next Agent

## Context
The crypto stat-arb framework is complete with risk management and advanced risk metrics:
- 21 tests pass, ruff clean, `examples/compare.py` and `examples/optimize.py` run.
- Strategies: `CointegrationPairs`, `MeanReversionStrategy`, `CrossExchangeArb`, `MomentumStrategy`.
- `BacktestEngine` supports `fee_rate`/`slippage`, `walk_forward`, `max_drawdown_duration`, `calmar_ratio`, optional `risk_manager`, and returns `sortino_ratio`/`var`/`cvar`.
- `RiskManager` provides `max_position_size` and `stop_loss`. `examples/compare.py` uses `RiskManager(max_weight=0.25)`.
- `utils/metrics.py` provides `sortino_ratio`, `var`, `cvar`, `max_drawdown_duration_from_curve`.

## Task
**Add reporting and visualization utilities.**

### Requirements
1. Add `utils/reporting.py` with functions:
   - `generate_report(result: dict) -> str` — human-readable text summary of a backtest result (total return, Sharpe, Sortino, VaR(95%), CVaR(95%), max drawdown, max drawdown duration, Calmar).
   - `report_to_dict(result: dict) -> dict` — serializable dict of key metrics (float/int/str only, no DataFrames/Series).
   - `plot_equity_curve(result: dict, save_path: str | None = None)` — plot equity curve and drawdown using matplotlib; matplotlib must be an optional, lazily-imported dependency (guarded with try/except) so the module imports and tests run without it installed.
2. Update `examples/compare.py` to print a text report via `generate_report` and save one equity-curve plot per strategy to `examples/reports/` (create dir if needed).
3. Add tests in `tests/test_reporting.py` for `generate_report` and `report_to_dict` (basic sanity checks using a synthetic result dict).
4. Keep ruff clean and all tests green; do not modify `.github/workflows/main.yml`.

### Verification
```bash
python3 -m pytest tests/ -v
python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python3 examples/compare.py
python3 examples/optimize.py
```

(End of file)
