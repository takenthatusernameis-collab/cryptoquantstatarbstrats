# CryptoQuant Stat Arb Strategies

A collection of statistical arbitrage strategies for cryptocurrency markets.

## Overview

This repository contains implementations of various statistical arbitrage trading strategies, focusing on:
- Pairs trading
- Cointegration-based strategies
- Mean reversion strategies
- Cross-exchange arbitrage

## Structure

```
cryptoquantstatarbstrats/
├── strategies/          # Strategy implementations
│   ├── base.py          # Strategy & PairStrategy base classes
│   └── pairs_trading.py # Cointegration pairs trading strategy
├── data/                # Data collection and processing
│   └── loader.py        # DataLoader with synthetic/clean data helpers
├── backtest/            # Backtesting framework
│   └── engine.py        # BacktestEngine that consumes strategy signals
├── utils/               # Utility functions (returns, z-score, metrics)
├── tests/               # Unit tests (pytest)
├── examples/            # End-to-end example scripts
├── pyproject.toml       # Project metadata, deps, tooling config
└── requirements.txt     # Pinned runtime dependencies
```

## Getting Started

```bash
# Install dependencies
python3 -m pip install -e ".[dev]"

# Run the example backtest
python3 examples/run_pairs.py

# Run the test suite
python3 -m pytest tests/ -v

# Lint
python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/

# Type check
python3 -m mypy backtest/ strategies/ utils/
```

## CI

[![CI](https://github.com/Kilo-Org/cryptoquantstatarbstrats/actions/workflows/ci.yml/badge.svg)](https://github.com/Kilo-Org/cryptoquantstatarbstrats/actions/workflows/ci.yml)

The CI workflow (`.github/workflows/ci.yml`) runs on push and pull requests, executing `ruff check`, `mypy backtest/ strategies/ utils/`, and `pytest tests/ -q` across Python 3.10/3.11/3.12.

## Disclaimer

This software is for educational and research purposes only. Use at your own risk.