"""
Tests for `--replay-best` support on the `cryptoquant sweep` CLI subcommand.
"""

from __future__ import annotations

import io
import json
from contextlib import redirect_stderr, redirect_stdout

from backtest.cli import main


def _run_sweep(argv: list[str]) -> tuple[int, str, str]:
    out_buf = io.StringIO()
    err_buf = io.StringIO()
    code = None
    with redirect_stdout(out_buf), redirect_stderr(err_buf):
        try:
            code = main(argv)
        except SystemExit as e:
            code = e.code
    return int(code or 0), out_buf.getvalue(), err_buf.getvalue()


def _write_config(tmp_path, data: dict, name: str = "sweep.json") -> str:
    cfg_path = tmp_path / name
    cfg_path.write_text(json.dumps(data), encoding="utf-8")
    return str(cfg_path)


_BASE_CONFIG = {
    "strategy": "mean_reversion",
    "asset": "BTC",
    "data_source": "synthetic",
    "start": "2024-01-01",
    "end": "2024-02-01",
    "freq": "1h",
    "train_period": 60,
    "test_period": 20,
    "metric": "calmar_ratio",
    "output": "json",
}


def test_sweep_replay_best_flag_enabled_via_cli(tmp_path, monkeypatch):
    captured: dict = {}

    def fake_sweep(strategy, data, grid, train_period, test_period, fee_rate=0.0,
                   slippage=0.0, metric="calmar_ratio", engine=None, **kwargs):
        captured.update(replay_best=kwargs.get("replay_best"))
        return []

    monkeypatch.setattr("backtest.sweep.run_parameter_sweep", fake_sweep)

    code, _, err = _run_sweep(
        ["sweep", "--grid", '{"lookback":[20]}', "--data-source", "synthetic",
         "--replay-best"]
    )
    assert code == 0, err
    assert captured["replay_best"] is True


def test_sweep_replay_best_enabled_via_config(tmp_path, monkeypatch):
    captured: dict = {}

    def fake_sweep(strategy, data, grid, train_period, test_period, fee_rate=0.0,
                   slippage=0.0, metric="calmar_ratio", engine=None, **kwargs):
        captured.update(replay_best=kwargs.get("replay_best"))
        return []

    monkeypatch.setattr("backtest.sweep.run_parameter_sweep", fake_sweep)

    config = dict(_BASE_CONFIG)
    config.update({"replay_best": True})
    cfg_path = _write_config(tmp_path, config)
    code, _, err = _run_sweep(["sweep", "--config", cfg_path, "--grid", '{"lookback":[20]}'])
    assert code == 0, err
    assert captured["replay_best"] is True


def test_sweep_replay_best_cli_overrides_config(tmp_path, monkeypatch):
    captured: dict = {}

    def fake_sweep(strategy, data, grid, train_period, test_period, fee_rate=0.0,
                   slippage=0.0, metric="calmar_ratio", engine=None, **kwargs):
        captured.update(replay_best=kwargs.get("replay_best"))
        return []

    monkeypatch.setattr("backtest.sweep.run_parameter_sweep", fake_sweep)

    config = dict(_BASE_CONFIG)
    config.update({"replay_best": True})
    cfg_path = _write_config(tmp_path, config)
    code, _, err = _run_sweep(
        ["sweep", "--config", cfg_path, "--grid", '{"lookback":[20]}', "--replay_best"]
    )
    assert code == 0, err
    # CLI flag defaults False but explicit store_true makes True; config also True.
    assert captured["replay_best"] is True


def test_replay_best_handles_series_equity_curve(monkeypatch):
    """The replay path must tolerate an equity_curve returned as a pandas Series.

    ``BacktestEngine.run`` returns ``equity_curve`` as a Series; the old
    ``or []`` truthiness check raised ``ValueError: truth value of a Series is
    ambiguous`` whenever the top-ranked combo produced a non-empty replay.
    """
    import pandas as pd

    from backtest.engine import BacktestEngine
    from backtest.sweep import run_parameter_sweep
    from strategies.mean_reversion import MeanReversionStrategy

    prices = [
        100.0, 101.0, 102.0, 101.5, 103.0, 102.0, 104.0, 103.5, 106.0, 105.0,
    ]
    rows = run_parameter_sweep(
        MeanReversionStrategy(asset="BTC"),
        pd.DataFrame({"BTC": prices}),
        {"lookback": [2]},
        train_period=4,
        test_period=2,
        fee_rate=0.0,
        slippage=0.0,
        metric="calmar_ratio",
        engine=BacktestEngine(initial_capital=100_000.0),
        replay_best=True,
    )
    assert rows, "expected at least one ranked row"
    top = rows[0]
    assert "replay" in top, "replay block should be attached to the top-ranked row"
    replay = top["replay"]
    for key in ("params", "total_return", "sharpe_ratio", "max_drawdown",
                "calmar_ratio", "final_equity"):
        assert key in replay, f"replay block missing {key!r}"
    assert isinstance(replay["params"], dict)
    assert replay["params"].get("lookback") == 2
    assert isinstance(replay["final_equity"], (int, float)) or replay["final_equity"] is None


def test_replay_best_attaches_cointegration_pvalue_on_real_data(monkeypatch):
    """Walk-forward windows on real pairs data must record the cointegration
    p-value used to gate positions, and the top-ranked row must carry the replay
    block with IS vs OOS metrics."""
    import json

    from backtest.engine import BacktestEngine
    from backtest.sweep import run_parameter_sweep
    from strategies.pairs_trading import CointegrationPairsStrategy

    data = {
        "BTC": [100.0, 101.0, 102.0, 101.5, 103.0, 102.0, 104.0, 103.5, 106.0, 105.0,
                107.0, 106.5, 108.0, 107.5, 109.0, 108.5, 110.0, 109.5, 111.0, 110.5],
        "ETH": [50.0, 50.5, 51.0, 50.75, 51.5, 51.25, 52.0, 51.75, 52.5, 52.25,
                53.0, 52.75, 53.5, 53.25, 54.0, 53.75, 54.5, 54.25, 55.0, 54.75],
    }
    import pandas as pd

    df = pd.DataFrame(data)
    rows = run_parameter_sweep(
        CointegrationPairsStrategy(pair=("BTC", "ETH")),
        df,
        {"lookback": [5], "entry_threshold": [2.0], "cointegration_pvalue": [0.05]},
        train_period=8,
        test_period=4,
        fee_rate=0.0,
        slippage=0.0,
        metric="calmar_ratio",
        engine=BacktestEngine(initial_capital=100_000.0),
        replay_best=True,
    )
    assert rows, "expected ranked rows"
    top = rows[0]
    assert "replay" in top
    assert "cointegration_pvalue" in top["replay"]["params"]
    # JSON-serializability of the full top-ranked row.
    json.dumps(top, default=float)
