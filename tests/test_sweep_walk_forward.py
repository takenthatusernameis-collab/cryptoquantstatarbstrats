"""
Tests for `--walk-forward` support on the `cryptoquant sweep` CLI subcommand.
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


def test_sweep_walk_forward_flag_enabled_via_cli(tmp_path, monkeypatch):
    captured: dict = {}

    def fake_sweep(strategy, data, grid, train_period, test_period, fee_rate=0.0,
                   slippage=0.0, metric="calmar_ratio", engine=None, **kwargs):
        captured.update(
            train_period=train_period,
            test_period=test_period,
            mode=kwargs.get("mode"),
            n_splits=kwargs.get("n_splits"),
            anchor=kwargs.get("anchor"),
        )
        return []

    monkeypatch.setattr("backtest.sweep.run_parameter_sweep", fake_sweep)

    code, _, err = _run_sweep(
        ["sweep", "--grid", '{"lookback":[20]}', "--data-source", "synthetic",
         "--walk-forward", "--train-period", "48", "--test-period", "12",
         "--mode", "rolling", "--n-splits", "2", "--anchor", "36"]
    )
    assert code == 0, err
    assert captured["train_period"] == 48
    assert captured["test_period"] == 12
    assert captured["mode"] == "rolling"
    assert captured["n_splits"] == 2
    assert captured["anchor"] == "36"


def test_sweep_walk_forward_enabled_via_config(tmp_path, monkeypatch):
    captured: dict = {}

    def fake_sweep(strategy, data, grid, train_period, test_period, fee_rate=0.0,
                   slippage=0.0, metric="calmar_ratio", engine=None, **kwargs):
        captured.update(
            train_period=train_period,
            test_period=test_period,
            mode=kwargs.get("mode"),
            n_splits=kwargs.get("n_splits"),
            anchor=kwargs.get("anchor"),
        )
        return []

    monkeypatch.setattr("backtest.sweep.run_parameter_sweep", fake_sweep)

    config = dict(_BASE_CONFIG)
    config.update({"walk_forward": True, "anchor": 30, "n_splits": 4, "mode": "expanding"})
    cfg_path = _write_config(tmp_path, config)
    code, _, err = _run_sweep(["sweep", "--config", cfg_path, "--grid", '{"lookback":[20]}'])
    assert code == 0, err
    assert captured["train_period"] == 60
    assert captured["test_period"] == 20
    assert captured["mode"] == "expanding"
    assert captured["n_splits"] == 4
    assert captured["anchor"] == 30


def test_sweep_walk_forward_cli_overrides_config(tmp_path, monkeypatch):
    captured: dict = {}

    def fake_sweep(strategy, data, grid, train_period, test_period, fee_rate=0.0,
                   slippage=0.0, metric="calmar_ratio", engine=None, **kwargs):
        captured.update(
            mode=kwargs.get("mode"),
            n_splits=kwargs.get("n_splits"),
            anchor=kwargs.get("anchor"),
        )
        return []

    monkeypatch.setattr("backtest.sweep.run_parameter_sweep", fake_sweep)

    config = dict(_BASE_CONFIG)
    config.update({"walk_forward": True, "anchor": 50, "n_splits": 5, "mode": "rolling"})
    cfg_path = _write_config(tmp_path, config)
    code, _, err = _run_sweep(
        ["sweep", "--config", cfg_path, "--grid", '{"lookback":[20]}',
         "--walk-forward", "--anchor", "10", "--n-splits", "2", "--mode", "expanding"]
    )
    assert code == 0, err
    assert captured["anchor"] == "10"
    assert captured["n_splits"] == 2
    assert captured["mode"] == "expanding"


def test_sweep_walk_forward_with_pairs_strategy(tmp_path, monkeypatch):
    captured: dict = {}

    def fake_sweep(strategy, data, grid, train_period, test_period, fee_rate=0.0,
                   slippage=0.0, metric="calmar_ratio", engine=None, **kwargs):
        captured["mode"] = kwargs.get("mode")
        return []

    monkeypatch.setattr("backtest.sweep.run_parameter_sweep", fake_sweep)

    code, _, err = _run_sweep(
        ["sweep", "--strategy", "pairs", "--pair", "BTC", "ETH",
         "--grid", '{"entry_threshold":[1.0,1.5]}', "--walk-forward",
         "--mode", "expanding", "--n-splits", "3"]
    )
    assert code == 0, err
    assert captured["mode"] == "expanding"
