# Task for Next Agent

## Context
The crypto stat-arb framework is fully implemented and verified:
- 18 tests pass, ruff clean, `examples/compare.py` and `examples/optimize.py` run.
- Strategies: `CointegrationPairs`, `MeanReversionStrategy`, `CrossExchangeArb`, `MomentumStrategy`.
- `BacktestEngine` supports `fee_rate`/`slippage`, `walk_forward`, `max_drawdown_duration`, `calmar_ratio`.
- `DataLoader.load_csv` added; `optimize.py` grid search in place.

## Task
**Add a risk-management module and per-strategy position limits.**

### Requirements
1. Add `utils/risk.py` — `RiskManager` with:
   - `max_position_size(positions, capital, max_weight=0.2)` that scales positions so no single asset exceeds `max_weight` of capital.
   - `stop_loss(prices, entry_prices, threshold)` returning a boolean mask of assets breaching the stop.
2. `BacktestEngine.run` accepts an optional `risk_manager` and applies `max_position_size` to per-bar position sizes.
3. Tests in `tests/test_strategies.py` (or new `tests/test_risk.py`) covering scaling and stop-loss.
4. Update `examples/compare.py` to pass a `RiskManager(max_weight=0.25)` to each run.
5. Keep ruff clean and all tests green; do not modify `.github/workflows/main.yml`.

### Verification
```bash
python3 -m pytest tests/ -v
python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python3 examples/compare.py
python3 examples/optimize.py
```
