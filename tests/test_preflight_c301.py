"""Tests for C301 preflight (scripts/preflight_c301.py): fail-closed
verification of the real 2023-01 .. 2023-02 USDT-M perp aggTrades-derived
5m OFI feature cache before the C301 order-flow-imbalance / trade-sign
autocorrelation per-asset time-series campaign runs.

These tests never fetch, impute, resample, or fabricate data. They assert the
on-disk preflight result is ready:true with no blocked reasons, that the cache
schema/flags/SHA256-from-bytes/push-limit are intact, and that the preflight
exits non-zero (fail-closed) when a gate value is falsified.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import preflight_c301 as pf  # noqa: E402


def _run_preflight():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "preflight_c301.py"), "--json"],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout.strip())


def test_preflight_exit_zero_ready_true():
    out = _run_preflight()
    assert out.get("ready") is True
    assert out.get("blocked_reasons") == []


def test_preflight_cache_schema_and_flags():
    out = _run_preflight()
    meta = out["checks"]["meta"]
    assert meta["interval"] == "5m"
    assert meta["source_interval"] == "aggTrades_ms"
    assert meta["n_symbols"] == 3
    assert meta["window_start_utc"] == "2023-01-01T00:00:00Z"
    assert meta["window_end_utc"] == "2023-02-28T23:55:00Z"
    assert meta["real_data_only"] is True
    assert meta["fabricated_data"] is False
    assert meta["executed_fills"] is False
    assert meta["cache_format"] == "plain_numpy_ndarrays_no_pandas_legs"
    assert meta["under_push_limit"] is True
    assert meta["cache_pkl_mb"] < 100.0
    assert meta["sha256_from_bytes"] == meta["actual_sha256"]
    assert meta["c300_cache_sha256"] == meta["c300_cache_actual_sha256"]
    assert meta["c300_cache_actual_sha256"] == "2c86accda2f32b466d32c6d520f3424b24952f10e93ea1da9bf803f154cfb873"


def test_preflight_per_asset_frames_full_window_no_close_nan():
    out = _run_preflight()
    detail = out["checks"]["assets"]["detail"]
    assert len(detail) == 3
    for s, d in detail.items():
        assert d["n_bars"] == 16992, s
        assert d["expected_bars"] == 16992, s
        assert d["fields"]["perp_close"]["nan_count"] == 0, s
        assert d["fields"]["perp_close"]["all_positive"], s
        assert d["fields"]["perp_close"]["all_finite"], s
        assert d["fields"]["perp_close"]["exact_index"], s
        assert d["fields"]["ofi"]["n_gap_bars"] == 0, s
        assert d["fields"]["ofi"]["signed_equals_buy_minus_sell"], s
        assert d["fields"]["ofi"]["trade_count_positive_on_trade_bars"], s
        assert d["fields"]["ofi"]["vwap_finite_positive_on_trade_bars"], s
        assert d["fields"]["ofi"]["abs_trade_sign_sum_le_trade_count"], s
        assert d["fields"]["ofi"]["ok"], s
        assert d["funding"]["ok"], s
        assert d["funding"]["funding_rows"] >= 90, s
        assert d["funding"]["hour_multiple_of_8"], s
        assert d["funding"]["stale_ok"], s


def test_preflight_wf_splits_fit_window():
    out = _run_preflight()
    detail = out["checks"]["assets"]["detail"]
    assert detail["BTCUSDT"]["walk_forward"]["ok"]
    assert detail["BTCUSDT"]["walk_forward"]["train"] == 2880
    assert detail["BTCUSDT"]["walk_forward"]["test"] == 1152
    assert detail["BTCUSDT"]["walk_forward"]["step"] == 1152
    assert detail["BTCUSDT"]["walk_forward"]["n_splits"] == 12
    for s, d in detail.items():
        assert d["walk_forward"]["n_splits"] == 12, s
        assert d["walk_forward"]["ok"], s


def test_preflight_feature_warmup_before_first_oos_test_bar():
    out = _run_preflight()
    wu = out["checks"]["assets"]["detail"]["BTCUSDT"]["feature_warmup"]
    assert wu["ok"]
    assert set(wu["lookbacks_5m"]) == {288, 1008, 2016}
    for L in ("L=288", "L=1008", "L=2016"):
        assert wu["warmup"][L]["warm_before_first_test_bar"] is True
        assert wu["warmup"][L]["ok"] is True


def test_preflight_provenance_present():
    out = _run_preflight()
    assert out["checks"]["provenance"]["exists"] is True
    assert out["checks"]["provenance"]["ok"] is True


def test_preflight_fails_closed_when_meta_flag_falsified(tmp_path, monkeypatch):
    """A falsified real_data_only flag must make the preflight fail-closed.

    Calls preflight.main() in-process with PXL_META monkeypatched to a falsified
    meta copy (a subprocess would not inherit the monkeypatch).
    """
    import preflight_c301 as p

    real_meta = p.PXL_META.read_text()
    fake_meta = tmp_path / "campaign301_aggtrades_ofi.meta.json"
    fake_meta.write_text(real_meta.replace('"real_data_only": true', '"real_data_only": false'))
    monkeypatch.setattr(p, "PXL_META", fake_meta)
    monkeypatch.setattr(sys, "argv", ["preflight_c301.py"])
    rc = p.main()
    assert rc != 0, "preflight must fail-closed on falsified real_data_only"
