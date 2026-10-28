"""
Tests for config schema validation.

Covers :func:`backtest.config.validate_config` and the
``ConfigValidationError`` raised by the CLI when a config file fails
validation.
"""

from __future__ import annotations

import pytest

from backtest.config import (
    CONFIG_SCHEMA,
    ConfigValidationError,
    validate_config,
)


def test_validate_config_accepts_valid_dict():
    cfg = {
        "symbols": ["BTC", "ETH"],
        "strategy": "mean_reversion",
        "output": "json",
        "initial_capital": 100_000.0,
        "fee_rate": 0.001,
    }
    assert validate_config(cfg) == cfg


def test_validate_config_accepts_camelcase_aliases():
    cfg = {
        "strategy": "pairs",
        "initialCapital": 50_000.0,
        "feeRate": 0.0005,
        "regimeMode": "trend",
        "regimeVolMode": "low_vol",
        "walkForwardReport": True,
    }
    assert validate_config(cfg) == cfg


def test_validate_config_rejects_unknown_key():
    with pytest.raises(ConfigValidationError) as exc:
        validate_config({"not_a_real_key": 1})
    assert "not_a_real_key" in str(exc.value)


def test_validate_config_rejects_multiple_unknown_keys():
    with pytest.raises(ConfigValidationError) as exc:
        validate_config({"foo": 1, "bar": 2})
    msg = str(exc.value)
    assert "foo" in msg
    assert "bar" in msg


def test_validate_config_rejects_wrong_type():
    with pytest.raises(ConfigValidationError) as exc:
        validate_config({"initial_capital": {"value": 100_000}})
    assert "initial_capital" in str(exc.value)


def test_validate_config_rejects_negative_capital():
    with pytest.raises(ConfigValidationError) as exc:
        validate_config({"initial_capital": -1000.0})
    assert "initial_capital" in str(exc.value)


def test_validate_config_rejects_fee_rate_above_one():
    with pytest.raises(ConfigValidationError) as exc:
        validate_config({"fee_rate": 1.5})
    assert "fee_rate" in str(exc.value)


def test_validate_config_accepts_fee_rate_at_boundary():
    assert validate_config({"fee_rate": 0.0})["fee_rate"] == 0.0
    assert validate_config({"fee_rate": 1.0})["fee_rate"] == 1.0


def test_validate_config_rejects_invalid_strategy_choice():
    with pytest.raises(ConfigValidationError) as exc:
        validate_config({"strategy": "not_a_strategy"})
    assert "strategy" in str(exc.value)


def test_validate_config_rejects_invalid_output_choice():
    with pytest.raises(ConfigValidationError) as exc:
        validate_config({"output": "xml"})
    assert "output" in str(exc.value)


def test_validate_config_rejects_invalid_order_type_choice():
    with pytest.raises(ConfigValidationError) as exc:
        validate_config({"order_type": "market_order"})
    assert "order_type" in str(exc.value)


def test_validate_config_rejects_participation_rate_out_of_range():
    with pytest.raises(ConfigValidationError) as exc:
        validate_config({"participation_rate": 2.0})
    assert "participation_rate" in str(exc.value)


def test_validate_config_rejects_non_numeric_range_field():
    with pytest.raises(ConfigValidationError) as exc:
        validate_config({"train_period": "abc"})
    assert "train_period" in str(exc.value)


def test_validate_config_rejects_non_dict():
    with pytest.raises(ConfigValidationError):
        validate_config(["BTC", "ETH"])  # type: ignore[arg-type]


def test_validate_config_allows_empty_dict():
    assert validate_config({}) == {}


def test_validate_config_rejects_bool_for_numeric_field():
    with pytest.raises(ConfigValidationError):
        # bool is a subclass of int but should not be accepted for numeric
        # fields that are validated via isinstance(..., (int, float)) checks.
        validate_config({"initial_capital": True})


def test_validate_config_rejects_none_value():
    with pytest.raises(ConfigValidationError):
        validate_config({"initial_capital": None})


def test_config_schema_covers_cli_aliases():
    """Every alias the CLI maps from config should appear in the schema."""
    aliases = {
        "start_date", "end_date", "frequency", "pairs", "initialCapital", "capital",
        "feeRate", "fee", "format", "report_type", "outputPath", "output_file",
        "artifactDir", "artifact_directory", "rebalance_freq", "rebal_freq",
        "offset", "volume", "volume_path", "high", "high_path", "low", "low_path",
        "use_execution_simulator", "regimeMode", "regimeLookback", "regimeVolMode",
        "rebalanceBenchmark", "walkForwardReport", "trainPeriod", "testPeriod",
    }
    missing = aliases - set(CONFIG_SCHEMA)
    assert not missing, f"Schema missing aliases: {missing}"


def test_cli_rejects_invalid_config(tmp_path):
    """The CLI surfaces validation errors instead of silently ignoring them."""
    import contextlib
    import io

    from backtest.cli import main

    cfg_path = tmp_path / "bad.yaml"
    cfg_path.write_text("strategy: not_a_strategy\n")
    buf = io.StringIO()
    with pytest.raises(SystemExit):
        with contextlib.redirect_stderr(buf):
            main(["--config", str(cfg_path)])
    assert "Invalid config" in buf.getvalue()


def test_cli_rejects_unknown_config_key(tmp_path):
    from backtest.cli import main

    cfg_path = tmp_path / "unknown.yaml"
    cfg_path.write_text("totally_made_up_key: 1\n")
    with pytest.raises(SystemExit):
        main(["--config", str(cfg_path)])


def test_apply_config_from_dict_walk_forward():
    import argparse

    from backtest.cli import _apply_config_from_dict

    parser = argparse.ArgumentParser()
    parser.add_argument("--anchor", default=None)
    parser.add_argument("--n-splits", type=int, default=None, dest="n_splits")
    parser.add_argument("--mode", choices=["rolling", "expanding"], default="rolling")
    args = parser.parse_args([])
    cfg = {"anchor": 40, "n_splits": 3, "mode": "expanding"}
    out = _apply_config_from_dict(args, parser, cfg)
    assert out.anchor == 40
    assert out.n_splits == 3
    assert out.mode == "expanding"


def test_apply_config_from_dict_walk_forward_anchor_and_n_splits_via_config_file(tmp_path):
    import argparse
    import json

    from backtest.cli import _apply_config_from_dict

    parser = argparse.ArgumentParser()
    parser.add_argument("--anchor", default=None)
    parser.add_argument("--n-splits", type=int, default=None, dest="n_splits")
    parser.add_argument("--mode", choices=["rolling", "expanding"], default="rolling")
    args = parser.parse_args([])
    cfg_path = tmp_path / "walk_forward.json"
    cfg_path.write_text(json.dumps({"anchor": 10, "n_splits": 4, "mode": "rolling"}))
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    out = _apply_config_from_dict(args, parser, cfg)
    assert out.anchor == 10
    assert out.n_splits == 4
    assert out.mode == "rolling"


def test_cli_rejects_bad_range_in_config(tmp_path):
    cfg_path = tmp_path / "range.yaml"
    cfg_path.write_text("fee_rate: 5.0\n")
    from backtest.cli import main
    with pytest.raises(SystemExit):
        main(["--config", str(cfg_path)])
