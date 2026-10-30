# CryptoQuant Stat Arb Strategies

A research framework for cryptocurrency statistical-arbitrage experiments.

## Research data versus demonstration data

The command-line backtest uses **free public Binance spot candles by default**.
It does not require a Binance API key. Symbols such as BTC, ETH, and SOL are
mapped to USDT-quoted spot markets.

```bash
python -m pip install -e ".[dev]"

# Historical Binance spot candles
cryptoquant --strategy pairs --pair BTC ETH --start 2024-01-01 \
  --end 2024-06-01 --freq 1h --fee-rate 0.001 --slippage 0.0005 \
  --walk-forward --output json --output-path reports/btc_eth.json

# Explicit CSV input (timestamp/date/time column plus price columns)
cryptoquant --data-source csv --data-csv data/prices.csv \
  --strategy mean_reversion --asset BTC

# Synthetic data is for tests and demonstrations only
cryptoquant --data-source synthetic --strategy mean_reversion --asset BTC
```

Synthetic runs print a warning to stderr. Their metrics are **not evidence of
real-market performance**. The Python method DataLoader.load_data() remains
available for test fixtures and example scripts; use
DataLoader.load_binance_data() or CLI Binance mode for actual historical
spot prices.

The term-structure strategy requires actual iv_30d and iv_90d columns in
the input CSV. The CLI deliberately does not fabricate implied-volatility
series when they are missing.

## Validation notes

- Strategy target weights are applied starting on the next bar, not against
  the close-to-close return that was used to compute the signal.
- The pairs strategy estimates a rolling hedge ratio from trailing observations
  and emits explicit opposing legs. The engine does not overwrite explicit
  asset weights with generic long/short flags.
- The default price loader is a free public data source, but this project is
  still a research framework. A successful backtest or passing unit tests do
  not establish a profitable strategy. Validate unseen periods, transaction
  costs, funding where relevant, execution assumptions, and data quality.
- The provided examples/optimize.py is a small synthetic demonstration. Its
  top-ranked parameter set is not an out-of-sample strategy recommendation.

## Development

```bash
python -m pytest tests/ -v
python -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python -m mypy backtest/ strategies/ utils/
```

## CI

[![CI](https://github.com/takenthatusernameis-collab/cryptoquantstatarbstrats/actions/workflows/ci.yml/badge.svg)](https://github.com/takenthatusernameis-collab/cryptoquantstatarbstrats/actions/workflows/ci.yml)

GitHub Actions runs Ruff, mypy, and the test suite across Python 3.10, 3.11,
and 3.12.

## Real-market validation

The pairs strategy (`CointegrationPairsStrategy`) was validated on **real public
Binance spot candles** (BTC, ETH, SOL at 1h, 2026-04-01 to 2026-10-28, 5,064
shared bars) with an out-of-sample walk-forward sweep and a full-dataset replay
across all three pairs. Results are consolidated in `reports/pairs_real_market.json`
and reproduced by `examples/run_pairs_multi.py` (or `examples/run_pairs.py`
for the original BTC/ETH run).

```bash
python examples/run_pairs_multi.py
```

Walk-forward sweep (rolling, train=500 / test=100 bars, 4 splits, fees 0.10%,
slippage 0.05%):

| Pair | Combo (lookback, entry_threshold, coint_pvalue) | OOS mean return | OOS/IS ratio |
| ---- | ------------------------------------------------| --------------- | ------------ |
| BTC/ETH | 120 / 2.5 / 0.05 (rank 1) | +0.0021% | -0.018 |
| ETH/SOL | 120 / 2.5 / 0.05 (rank 1) | -0.0066% | -0.263 |
| BTC/SOL | 120 / 2.0 / 0.1 (rank 1) | +0.0997% | +0.560 |

Replay of the top-ranked combo over the full dataset:

| Pair | total_return | sharpe_ratio | max_drawdown | calmar_ratio | final_equity |
| ---- | ------------ | ------------ | ------------ | ------------ | ------------ |
| BTC/ETH | -1.75% | -2.09 | -2.48% | -1.22 | 98,246 |
| ETH/SOL | -0.32% | -1.07 | -0.37% | -1.49 | 99,682 |
| BTC/SOL | +4.42% | +2.29 | -1.35% | +5.78 | 104,422 |

Benchmark (equal-weighted buy-and-hold over the same window):
- BTC/ETH: **+15.50% total return**
- ETH/SOL: **+17.60% total return**
- BTC/SOL: **+21.59% total return**

Findings:

- The cointegration screen (Engle-Granger p-value gate) is active across all
  pairs: positions are only taken when the trailing window passes `pvalue <= 0.05`,
  keeping the strategy mostly in cash by design.
- The hedge ratio was positive for every valid window across all pairs (no
  same-direction exposure emitted), so the opposing legs were preserved.
- On these windows the pairs strategy underperformed the buy-and-hold benchmarks.
  This is a legitimate research outcome, not evidence of a trading edge.

## Disclaimer

This software is for educational and research purposes only. It does not
provide investment advice and is not intended for live trading without
independent validation.

## Parameter sweep (walk-forward)

Run an out-of-sample parameter grid search with walk-forward validation (CLI):

```bash
cryptoquant sweep \
  --strategy mean_reversion \
  --asset BTC \
  --grid '{"lookback":[20,30,50],"entry_threshold":[1.5,2.0]}' \
  --walk-forward \
  --train-period 60 \
  --test-period 20 \
  --n-splits 3 \
  --anchor 40 \
  --mode expanding \
  --metric calmar_ratio \
  --data-source synthetic \
  --output json \
  --output-path sweep_results.json
```

Sweep parameters can also be supplied through a config file passed via `--config` (YAML, TOML, or JSON). Config values fill in any sweep argument not overridden on the CLI, so CLI flags always win. Walk-forward can be enabled via `walk_forward: true` in the config alongside `train_period`, `test_period`, `n_splits`, `anchor`, and `mode`:

```yaml
# config/sweep.yaml
strategy: mean_reversion
asset: BTC
data_source: synthetic
start: "2024-01-01"
end: "2024-02-01"
freq: 1h
walk_forward: true
train_period: 60
test_period: 20
anchor: 40
n_splits: 3
mode: expanding
metric: calmar_ratio
output: json
output_path: sweep_results.json
```

```bash
cryptoquant sweep --config config/sweep.yaml \
  --grid '{"lookback":[20,30,50],"entry_threshold":[1.5,2.0]}'
```

Programmatic API is also available via `backtest.sweep.run_parameter_sweep`:

```python
from backtest.data_loader import DataLoader
from backtest.engine import BacktestEngine
from backtest.sweep import run_parameter_sweep
from strategies.mean_reversion import MeanReversionStrategy

loader = DataLoader()
data = loader.load_data(["BTC"], "2024-01-01", "2024-01-15", freq="1h")
data = loader.clean_data(data)

engine = BacktestEngine(initial_capital=100_000.0)
rows = run_parameter_sweep(
    MeanReversionStrategy(),
    data,
    {"lookback": [20, 30, 50], "entry_threshold": [1.5, 2.0]},
    train_period=60,
    test_period=20,
    fee_rate=0.0,
    slippage=0.0,
    metric="calmar_ratio",
    engine=engine,
    mode="rolling",  # or "expanding"
    n_splits=3,
    anchor=None,  # int offset, timestamp string, or None
)
```

Walk-forward options for `cryptoquant sweep`:

- `--anchor`: origin index for the first walk-forward window (integer row offset,
  timestamp string `YYYY-MM-DD[ HH:MM]`, or `None` for the start of the data).
  Negative offsets are clamped to 0.
- `--n-splits`: number of walk-forward splits (rolling/expanding).
- `--mode`: `rolling` (default) or `expanding` training window.
- `--train-period` / `--test-period`: sizes of train/test windows.

These options are also available in a config file passed via `--config`
(`anchor`, `n_splits`/`nSplits`, `mode`, `train_period`/`trainPeriod`,
`test_period`/`testPeriod`). The CLI also accepts them directly; config values
are applied when not overridden by CLI flags.

## Replay best sweep combo (full-dataset confirmation)

After a walk-forward sweep ranks parameter combos, `--replay-best` re-runs the
#1-ranked combo over the full dataset (single backtest via `engine.run`) and
attaches a `replay` block to the top-ranked row so you can confirm the chosen
parameters:

```bash
cryptoquant sweep \
  --strategy mean_reversion \
  --grid '{"lookback":[20,30,50]}' \
  --walk-forward \
  --train-period 60 \
  --test-period 20 \
  --replay-best \
  --output json \
  --output-path sweep_replay.json
```

The `replay` block on the top-ranked row contains the params used plus full
metrics: `total_return`, `sharpe_ratio`, `max_drawdown`, `calmar_ratio`, and
`final_equity`. Enable via config with `replay_best: true`; the
`--replay-best` CLI flag overrides the config value.

```yaml
# config/sweep_replay.yaml
strategy: mean_reversion
asset: BTC
data_source: synthetic
start: "2024-01-01"
end: "2024-02-01"
freq: 1h
walk_forward: true
train_period: 60
test_period: 20
replay_best: true
output: json
output_path: sweep_replay.json
```
