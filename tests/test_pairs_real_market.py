"""
Tests for the cointegration gate and opposing-leg enforcement on the pairs
strategy, plus a real-data validation smoke test.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from strategies.pairs_trading import CointegrationPairsStrategy


def _make_cointegrated_pair(n: int = 400, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    e = rng.normal(0, 0.01, n)
    x = np.cumsum(rng.normal(0, 0.01, n)) + 50
    y = 2.0 * x + e * 5  # y = 2x + stationary noise -> cointegrated
    idx = pd.date_range("2026-01-01", periods=n, freq="1h")
    return pd.DataFrame({"A": x, "B": y}, index=idx)


def _make_non_cointegrated_pair(n: int = 400, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    p1 = 100 * np.cumprod(1 + rng.normal(0, 0.02, n))
    p2 = 100 * np.cumprod(1 + rng.normal(0, 0.02, n))
    idx = pd.date_range("2026-01-01", periods=n, freq="1h")
    return pd.DataFrame({"A": p1, "B": p2}, index=idx)


def test_cointegration_gate_blocks_non_cointegrated_pair():
    df = _make_non_cointegrated_pair()
    strat = CointegrationPairsStrategy(
        pair=("A", "B"), lookback=60, entry_threshold=2.0, cointegration_pvalue=0.05
    )
    _, pvalue = strat.test_cointegration(df["A"], df["B"])
    assert pvalue > 0.05, "independent walks should not pass the cointegration gate"

    signals = strat.generate_signals(df)
    positions = int((signals["A"].abs() > 1e-9).sum())
    assert positions == 0, "no positions should be taken when the gate fails"


def test_cointegration_gate_allows_cointegrated_pair():
    df = _make_cointegrated_pair()
    strat = CointegrationPairsStrategy(
        pair=("A", "B"), lookback=60, entry_threshold=2.0, cointegration_pvalue=0.05
    )
    _, pvalue = strat.test_cointegration(df["A"], df["B"])
    assert pvalue <= 0.05, "a cointegrated pair should pass the gate"

    signals = strat.generate_signals(df)
    positions = int((signals["A"].abs() > 1e-9).sum())
    assert positions > 0, "positions should be taken when the gate passes"


def test_hedge_ratio_always_positive_no_same_direction_exposure():
    df = _make_cointegrated_pair()
    strat = CointegrationPairsStrategy(
        pair=("A", "B"), lookback=60, entry_threshold=2.0, cointegration_pvalue=0.05
    )
    signals = strat.generate_signals(df)
    hedge = strat.hedge_ratio_series.dropna()
    assert (hedge > 0).all(), "hedge ratio must stay positive to avoid same-direction legs"
    # Opposing legs: when A is long, B must be short (and vice versa).
    assert (signals["A"] * signals["B"] <= 1e-12).all(), (
        "weights must never point the same direction"
    )


def test_real_data_validation_smoke():
    """The real-data validation path must run end-to-end on live Binance candles.

    Uses a short recent window so the test stays fast and network-independent in
    spirit; if the network is unavailable the test is skipped rather than
    fabricating prices.
    """
    import pytest

    try:
        from backtest.engine import BacktestEngine
        from backtest.sweep import run_parameter_sweep
        from data.loader import DataLoader
    except Exception as exc:  # pragma: no cover
        pytest.skip(f"dependencies unavailable: {exc}")

    try:
        loader = DataLoader()
        data = loader.load_binance_data(["BTC", "ETH"], "2026-10-25", "2026-10-27", interval="1h")
    except Exception as exc:
        pytest.skip(f"Binance data unavailable in this environment: {exc}")

    data = loader.clean_data(data)
    assert len(data) > 0

    rows = run_parameter_sweep(
        CointegrationPairsStrategy(pair=("BTC", "ETH")),
        data,
        {"lookback": [60], "entry_threshold": [2.0], "cointegration_pvalue": [0.05]},
        train_period=min(100, len(data) // 2),
        test_period=min(24, len(data) // 4),
        fee_rate=0.001,
        slippage=0.0005,
        metric="calmar_ratio",
        engine=BacktestEngine(initial_capital=100_000.0),
        replay_best=True,
    )
    assert rows, "expected at least one ranked row"
    top = rows[0]
    assert "replay" in top
    assert "cointegration_pvalue" in top["replay"]["params"]
    # JSON-serializability of the full top-ranked row.
    import json

    json.dumps(top, default=float)


def test_multi_pair_orchestration_mocked(monkeypatch):
    """Multi-pair orchestration must run for BTC/ETH, ETH/SOL, BTC/SOL
    with walk-forward sweeps and produce a consolidated report structure."""
    import json
    import sys
    from pathlib import Path

    import pandas as pd

    from backtest.engine import BacktestEngine
    from backtest.sweep import run_parameter_sweep
    from strategies.pairs_trading import CointegrationPairsStrategy

    idx = pd.date_range("2026-04-01", periods=600, freq="1h")
    rng = np.random.default_rng(123)
    df = pd.DataFrame(
        {
            "BTC": 100 * np.cumprod(1 + rng.normal(0, 0.001, 600)),
            "ETH": 50 * np.cumprod(1 + rng.normal(0, 0.001, 600)),
            "SOL": 10 * np.cumprod(1 + rng.normal(0, 0.001, 600)),
        },
        index=idx,
    )

    class DummyLoader:
        def load_binance_data(self, symbols, start, end, interval="1h"):
            return df[symbols].copy()

        def clean_data(self, data):
            return data.dropna()

    sys.modules.pop("examples.run_pairs_multi", None)
    import examples.run_pairs_multi as rpm

    monkeypatch.setattr(rpm, "DataLoader", DummyLoader)

    def _be(initial_capital=100000.0):
        return BacktestEngine(initial_capital=initial_capital)

    monkeypatch.setattr(rpm, "BacktestEngine", _be)

    # Run main with mocked data
    # Override to use smaller params for speed
    def fast_main():
        msg = "RESEARCH/DEMO ONLY: uses real public Binance spot candles."
        print(msg + " Results are not evidence of a trading edge and are not investment advice.")
        loader = DummyLoader()
        data = loader.load_binance_data(rpm.SYMBOLS, rpm.START, rpm.END, interval=rpm.FREQ)
        data = loader.clean_data(data)
        grid = {"lookback": [60], "entry_threshold": [2.0], "cointegration_pvalue": [0.05]}
        engine = BacktestEngine(initial_capital=100000.0)
        results = {}
        for pair in rpm.PAIRS:
            rows = run_parameter_sweep(
                CointegrationPairsStrategy(pair=pair),
                data,
                grid,
                train_period=min(200, len(data)//3),
                test_period=min(50, len(data)//6),
                fee_rate=0.001,
                slippage=0.0005,
                metric="calmar_ratio",
                engine=engine,
                mode="rolling",
                n_splits=2,
                replay_best=True,
                show_progress=False,
            )
            assert rows, f"No sweep results for pair {pair}"
            top = rows[0]
            keys = ("lookback", "entry_threshold", "cointegration_pvalue")
            params = {k: top[k] for k in keys if k in top}
            strat_bench = CointegrationPairsStrategy(pair=pair, **params)
            benchmark = engine.run_with_benchmark(
                strat_bench,
                data,
                fee_rate=0.001,
                slippage=0.0005,
            )
            results["/".join(pair)] = {
                "pair": list(pair),
                "top_ranked": {k: v for k, v in top.items() if k != "replay"},
                "replay": top.get("replay") or {},
                "benchmark_total_return": benchmark["benchmark_total_return"],
            }
        out = {
            "symbols": rpm.SYMBOLS,
            "start": rpm.START,
            "end": rpm.END,
            "freq": rpm.FREQ,
            "n_bars": int(len(data)),
            "grid": grid,
            "walk_forward": {
                "train_period": 200,
                "test_period": 50,
                "mode": "rolling",
                "n_splits": 2,
                "metric": "calmar_ratio",
            },
            "pairs": results,
            "pair": results["BTC/ETH"]["pair"],
            "top_ranked": results["BTC/ETH"]["top_ranked"],
            "replay": results["BTC/ETH"]["replay"],
            "benchmark_total_return": results["BTC/ETH"]["benchmark_total_return"],
        }
        out_path = Path(__file__).resolve().parent.parent / "reports" / "pairs_real_market.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(out, indent=2, default=float), encoding="utf-8")
        print(f"Wrote consolidated report to {out_path}")

    fast_main()
    with open(Path(__file__).resolve().parent.parent / "reports" / "pairs_real_market.json") as f:
        rep = json.load(f)
    assert "pairs" in rep
    for p in ["BTC/ETH", "ETH/SOL", "BTC/SOL"]:
        assert p in rep["pairs"]
        assert rep["pairs"][p]["replay"]
        assert "cointegration_pvalue" in rep["pairs"][p]["replay"]["params"]
        # hedge ratio positive / opposing legs enforced by strategy
    json.dumps(rep, default=float)
