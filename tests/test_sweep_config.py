"""
Tests for `--config` file support on the `cryptoquant sweep` CLI subcommand.

Covers config-driven sweeps, walk-forward option threading, CLI-over-config
precedence, and invalid-config rejection.
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


def test_sweep_config_driven_exits_zero_and_produces_ranked_rows(tmp_path):
    cfg_path = _write_config(tmp_path, _BASE_CONFIG)
    code, out, err = _run_sweep(["sweep", "--config", cfg_path, "--grid", '{"lookback":[20,30]}'])
    assert code == 0, err
    assert "WARNING" in err
    rows = json.loads(out)
    assert isinstance(rows, list)
    assert len(rows) == 2
    assert rows[0]["rank"] == 1
    assert rows[1]["rank"] == 2
    assert "oos_mean_return" in rows[0]


def test_sweep_config_honors_walk_forward_options(tmp_path, monkeypatch):
    captured: dict = {}

    def fake_sweep(strategy, data, grid, train_period, test_period, fee_rate=0.0,
                   slippage=0.0, metric="calmar_ratio", engine=None, **kwargs):
        captured.update(
            train_period=train_period,
            test_period=test_period,
            fee_rate=fee_rate,
            slippage=slippage,
            metric=metric,
            mode=kwargs.get("mode"),
            n_splits=kwargs.get("n_splits"),
            anchor=kwargs.get("anchor"),
        )
        return []

    monkeypatch.setattr("backtest.sweep.run_parameter_sweep", fake_sweep)

    config = dict(_BASE_CONFIG)
    config.update({"anchor": 40, "n_splits": 3, "mode": "expanding"})
    cfg_path = _write_config(tmp_path, config)
    code, _, err = _run_sweep(["sweep", "--config", cfg_path, "--grid", '{"lookback":[20]}'])
    assert code == 0, err
    assert captured["train_period"] == 60
    assert captured["test_period"] == 20
    assert captured["mode"] == "expanding"
    assert captured["n_splits"] == 3
    assert captured["anchor"] == 40


def test_sweep_config_cli_overrides_config_precedence(tmp_path, monkeypatch):
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
    config.update({"anchor": 50, "n_splits": 4, "mode": "rolling"})
    cfg_path = _write_config(tmp_path, config)
    code, _, err = _run_sweep(
        ["sweep", "--config", cfg_path, "--grid", '{"lookback":[20]}',
         "--anchor", "10", "--n-splits", "2", "--mode", "expanding"]
    )
    assert code == 0, err
    # CLI flags win over config values (each CLI value differs from its parser
    # default, so it is treated as explicitly overridden).
    assert captured["anchor"] == "10"
    assert captured["n_splits"] == 2
    assert captured["mode"] == "expanding"


def test_sweep_config_output_path_writes_file(tmp_path):
    cfg_path = _write_config(tmp_path, _BASE_CONFIG)
    out_path = tmp_path / "sweep_out.json"
    code, out, err = _run_sweep(
        ["sweep", "--config", cfg_path, "--grid", '{"lookback":[20]}',
         "--output-path", str(out_path)]
    )
    assert code == 0, err
    assert out_path.exists()
    rows = json.loads(out_path.read_text(encoding="utf-8"))
    assert isinstance(rows, list)
    assert len(rows) == 1


def test_sweep_config_rejects_invalid_config(tmp_path):
    config = dict(_BASE_CONFIG)
    config["strategy"] = "not_a_strategy"
    cfg_path = _write_config(tmp_path, config)
    code, _, err = _run_sweep(["sweep", "--config", cfg_path, "--grid", '{"lookback":[20]}'])
    assert code != 0
    assert "Invalid config" in err


def test_sweep_config_rejects_unknown_config_key(tmp_path):
    cfg_path = tmp_path / "sweep.json"
    cfg_path.write_text(json.dumps({"totally_made_up_key": 1}), encoding="utf-8")
    code, _, err = _run_sweep(["sweep", "--config", str(cfg_path), "--grid", '{"lookback":[20]}'])
    assert code != 0
    assert "Invalid config" in err


def test_sweep_config_rejects_invalid_anchor(tmp_path):
    config = dict(_BASE_CONFIG)
    config["anchor"] = True  # bool rejected for anchor
    cfg_path = _write_config(tmp_path, config)
    code, _, err = _run_sweep(["sweep", "--config", cfg_path, "--grid", '{"lookback":[20]}'])
    assert code != 0
    assert "Invalid config" in err
