"""
End-to-end CLI walk-forward integration tests for the portfolio path via
config file.

Exercises ``main(["--config", ...])`` with ``--walk-forward``,
``--rebalance-frequency``, ``anchor``, ``n_splits`` and ``mode`` flowing
through ``_apply_config_from_dict`` into ``engine.walk_forward_portfolio`` and
asserts exit code 0 and that the returned window counts reflect anchor/n_splits.
"""

from __future__ import annotations

import contextlib
import io
import json

import pytest

from backtest.cli import main


def _run_cli(argv: list[str]) -> tuple[int, str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = main(argv)
    return int(code or 0), buf.getvalue()


def _base_config() -> dict:
    return {
        "data_source": "synthetic",
        "strategy": "mean_reversion",
        "symbols": ["BTC", "ETH", "SOL"],
        "start": "2024-01-01",
        "end": "2024-01-11",
        "freq": "1h",
        "walk_forward": True,
        "rebalance_frequency": "1d",
        "train_period": 100,
        "test_period": 40,
        "output": "json",
    }


def _write_config(tmp_path, name: str, cfg: dict) -> str:
    p = tmp_path / name
    p.write_text(json.dumps(cfg))
    return str(p)


def _summary_count(tmp_path, cfg: dict) -> int:
    cfg_path = _write_config(tmp_path, "config.json", cfg)
    code, out = _run_cli(["--config", cfg_path])
    assert code == 0, out
    data = json.loads(out)
    return len(data.get("summary", []))


def test_walk_forward_portfolio_config_anchor_none_default_window_count(tmp_path):
    # 240 rows, train=100, test=40, rolling: origins 0, 40, 80 -> 3 windows.
    cfg = _base_config()
    assert _summary_count(tmp_path, cfg) == 3


def test_walk_forward_portfolio_config_anchor_int_shifts_windows(tmp_path):
    # Anchor at row 40 drops the first window -> 2 windows.
    cfg = _base_config()
    cfg["anchor"] = 40
    assert _summary_count(tmp_path, cfg) == 2


def test_walk_forward_portfolio_config_n_splits_caps_windows(tmp_path):
    # n_splits=2 caps the available 3 windows to 2.
    cfg = _base_config()
    cfg["n_splits"] = 2
    assert _summary_count(tmp_path, cfg) == 2


def test_walk_forward_portfolio_config_anchor_and_n_splits_combined(tmp_path):
    # Anchor 40 allows at most 2 windows; n_splits=1 caps to 1.
    cfg = _base_config()
    cfg["anchor"] = 40
    cfg["n_splits"] = 1
    assert _summary_count(tmp_path, cfg) == 1


def test_walk_forward_portfolio_config_mode_expanding(tmp_path):
    # mode=expanding still runs portfolio walk-forward through the config path.
    cfg = _base_config()
    cfg["mode"] = "expanding"
    cfg["anchor"] = 10
    count = _summary_count(tmp_path, cfg)
    assert count >= 1


def test_walk_forward_portfolio_config_invalid_anchor_raises(tmp_path):
    cfg = _base_config()
    cfg["anchor"] = "not-a-date"
    cfg_path = _write_config(tmp_path, "config_bad.json", cfg)
    with pytest.raises(ValueError):
        main(["--config", cfg_path])


def test_walk_forward_portfolio_config_cli_overrides_config(tmp_path):
    # Config sets anchor=40 (would give 2 windows). CLI overrides anchor to 0
    # giving the default 3 windows.
    cfg = _base_config()
    cfg["anchor"] = 40
    cfg_path = _write_config(tmp_path, "config.json", cfg)
    code, out = _run_cli(["--config", cfg_path, "--anchor", "0"])
    assert code == 0, out
    data = json.loads(out)
    assert len(data.get("summary", [])) == 3

    # Config sets n_splits=1, CLI overrides to larger value
    cfg2 = _base_config()
    cfg2["n_splits"] = 1
    cfg_path2 = _write_config(tmp_path, "config2.json", cfg2)
    code, out = _run_cli(["--config", cfg_path2, "--n-splits", "3"])
    assert code == 0, out
    data = json.loads(out)
    assert len(data.get("summary", [])) == 3

    # Config sets mode=rolling, CLI overrides to expanding
    cfg3 = _base_config()
    cfg3["mode"] = "rolling"
    cfg_path3 = _write_config(tmp_path, "config3.json", cfg3)
    code, out = _run_cli(["--config", cfg_path3, "--mode", "expanding"])
    assert code == 0, out
    data = json.loads(out)
    assert len(data.get("summary", [])) >= 1
