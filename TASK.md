# Task for Next Agent

## Context
The crypto stat-arb framework is fully implemented with risk management:
- 20 tests pass, ruff clean, `examples/compare.py` and `examples/optimize.py` run.
- Strategies: `CointegrationPairs`, `MeanReversionStrategy`, `CrossExchangeArb`, `MomentumStrategy`.
- `BacktestEngine` supports `fee_rate`/`slippage`, `walk_forward`, `max_drawdown_duration`, `calmar_ratio`, and optional `risk_manager`.
- `RiskManager` provides `max_position_size` and `stop_loss`. `examples/compare.py` uses `RiskManager(max_weight=0.25)`.

## Task
**Add advanced risk metrics and reporting.**

### Requirements
1. Add `utils/metrics.py` with functions:
   - `sortino_ratio(returns, risk_free_rate=0.0, periods_per_year=252)` — use downside deviation (only negative returns).
   - `var(returns, confidence=0.95)` — historical Value at Risk.
   - `cvar(returns, confidence=0.95)` — Conditional VaR (expected shortfall).
   - `max_drawdown_duration_from_curve(equity_curve)` — compute max drawdown duration from equity curve (can reuse logic).
2. Extend `BacktestEngine.run` to return these metrics in the result dict: `sortino_ratio`, `var`, `cvar`. Keep existing keys unchanged.
3. Update `examples/compare.py` to display `Sortino`, `VaR(95%)`, `CVaR(95%)` columns.
4. Add tests in `tests/test_strategies.py` (or new `tests/test_metrics.py`) for the new metrics (basic sanity checks).
5. Keep ruff clean and all tests green; do not modify `.github/workflows/main.yml`.

### Verification
```bash
python3 -m pytest tests/ -v
python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python3 examples/compare.py
python3 examples/optimize.py
```
