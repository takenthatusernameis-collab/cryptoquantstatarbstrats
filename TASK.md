# Task for Next Agent

## Context
You are continuing the **cryptoquantstatarbstrats** repository, a statistical-arbitrage framework for crypto markets. The previous agent completed the initial framework:

- `strategies/base.py` — `Strategy` / `PairStrategy` base classes
- `strategies/pairs_trading.py` — `CointegrationPairsStrategy` (OLS hedge ratio + z-score signals)
- `backtest/engine.py` — `BacktestEngine` consuming strategy signals with position-weighted returns
- `data/loader.py` — `DataLoader` with synthetic data + cleaning helpers
- `utils/__init__.py` — returns, z-score, half-life, annualized metrics
- `tests/test_strategies.py` — 5 passing pytest tests
- `examples/run_pairs.py` — end-to-end demo
- `pyproject.toml`, `requirements.txt`, updated `README.md`

All tests pass (`pytest` → 5 passed) and `ruff check` is clean.

## Task
**Implement a mean-reversion strategy and a cross-exchange arbitrage strategy, then add a comparative backtest harness.**

### Requirements
1. **New strategy: MeanReversionStrategy** (`strategies/mean_reversion.py`)
   - Subclass `Strategy` (not `PairStrategy`).
   - Generate entry/exit signals based on a rolling z-score or Bollinger Band of a single asset's returns/price.
   - Implement `calculate_position_sizes` returning per-asset weights.

2. **New strategy: CrossExchangeArb** (`strategies/cross_exchange.py`)
   - Subclass `Strategy`.
   - Model two price feeds for the same asset on different exchanges; signal when the spread exceeds a threshold minus estimated fees.
   - Implement `calculate_position_sizes`.

3. **Comparative harness** (`examples/compare.py`)
   - Load data for 2–3 assets via `DataLoader`.
   - Run each strategy through `BacktestEngine`.
   - Print a side-by-side comparison table of `total_return`, `sharpe_ratio`, `max_drawdown`.

4. **Tests** (`tests/test_strategies.py`)
   - Add tests for the two new strategies (signal shape, position sizes, harness runs).

### Constraints
- Follow existing conventions: `from __future__ import annotations`, type hints, `Strategy` ABC with abstract `generate_signals` and `calculate_position_sizes`.
- Keep `ruff check` clean and all `pytest` tests green.
- Do **not** modify `.github/workflows/main.yml`.
- Use lowercase `1h` for pandas frequency strings (pandas 2.x rejects `1H`).
- Prefer editing existing files over creating new ones; create new files only where required.

### Verification
```bash
python3 -m pip install -e ".[dev]"   # if needed
python3 -m pytest tests/ -v
python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python3 examples/compare.py
```