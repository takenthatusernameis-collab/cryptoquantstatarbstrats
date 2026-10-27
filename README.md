# CryptoQuant Stat Arb Strategies

A research framework for cryptocurrency statistical-arbitrage experiments.

## Research data versus demonstration data

The command-line backtest uses **free public Binance spot candles by default**.
It does not require a Binance API key. Symbols such as BTC, ETH, and SOL are
mapped to USDT-quoted spot markets.

\`\`\`bash
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
\`\`\`

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

\`\`\`bash
python -m pytest tests/ -v
python -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python -m mypy backtest/ strategies/ utils/
\`\`\`

## CI

[![CI](https://github.com/takenthatusernameis-collab/cryptoquantstatarbstrats/actions/workflows/ci.yml/badge.svg)](https://github.com/takenthatusernameis-collab/cryptoquantstatarbstrats/actions/workflows/ci.yml)

GitHub Actions runs Ruff, mypy, and the test suite across Python 3.10, 3.11,
and 3.12.

## Disclaimer

This software is for educational and research purposes only. It does not
provide investment advice and is not intended for live trading without
independent validation.
