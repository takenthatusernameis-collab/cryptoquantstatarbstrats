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
