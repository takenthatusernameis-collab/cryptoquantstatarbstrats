#!/usr/bin/env python3
"""Generate a risk report from a quick backtest."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backtest.engine import BacktestEngine
from data.loader import DataLoader
from strategies.mean_reversion import MeanReversionStrategy
from utils.reporting import generate_report, generate_risk_report


def main() -> None:
    loader = DataLoader()
    data = loader.load_data(["BTC", "ETH", "SOL"], "2024-01-01", "2024-02-01", freq="1h")
    data = loader.clean_data(data)

    strategy = MeanReversionStrategy("BTC")
    engine = BacktestEngine(initial_capital=100_000)
    result = engine.run(strategy, data)

    print(generate_report(result))
    print()
    print(generate_risk_report(result))

    reports_dir = Path(__file__).resolve().parent / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "risk_report.txt").write_text(generate_risk_report(result))


if __name__ == "__main__":
    main()
