# Task for Next Agent

## Context
The crypto stat-arb framework is fully implemented and verified:
- 13 tests pass, ruff clean, `examples/compare.py` runs with cost/walk-forward/risk metrics.
- Strategies: `CointegrationPairs`, `MeanReversionStrategy`, `CrossExchangeArb`.
- `BacktestEngine` supports `fee_rate`/`slippage`, `walk_forward`, `max_drawdown_duration`, `calmar_ratio`.

## Task
**Add a real data feed (CSV) to `DataLoader` and a parameter-optimization harness.**

### Requirements
1. `DataLoader` gains a `load_csv(path: str)` classmethod that reads a CSV with a `timestamp` column + asset columns, parses timestamps, sets the index, and returns a `pd.DataFrame` aligned with the engine's expected shape.
2. Add `strategies/momentum.py` — `MomentumStrategy` (subclass of `Strategy`):
   - Single asset, signal = long when `close > close.shift(n).rolling(m).mean() * (1 + entry_threshold)`, short when below `close.shift(n).rolling(m).mean() * (1 - entry_threshold)`, exit on crossover of that mean.
   - `calculate_position_sizes` returns `{asset: ±1.0 or 0.0}`.
3. Add `examples/optimize.py` — grid-search harness:
   - Loads synthetic data via `DataLoader`, enumerates a small grid of strategy params (e.g. `window`, `threshold` for momentum; `z_window`, `entry_threshold` for mean reversion),
   - Runs each config through `BacktestEngine`, records `total_return`, `sharpe_ratio`, `max_drawdown`, `calmar_ratio`,
   - Prints a sorted DataFrame of the top 5 configs by `calmar_ratio`.
4. Tests in `tests/test_strategies.py` for `MomentumStrategy` signal shape, position sizes, backtest run, and that `optimize.py` returns a non-empty DataFrame.
5. Update `examples/compare.py` to include `MomentumStrategy` in the comparison table.

### Constraints
- Keep ruff clean and all tests green.
- Do not modify `.github/workflows/main.yml`.

### Verification
```bash
python3 -m pytest tests/ -v
python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python3 examples/compare.py
python3 examples/optimize.py
```