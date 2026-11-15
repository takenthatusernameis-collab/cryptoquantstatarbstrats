"""Tests for C304 preflight (scripts/preflight_c304.py): fail-closed
verification of the real cross-sectional mark/index basis cache before the
C304 runner executes.

These tests never fetch, impute, resample, or fabricate data. They assert the
on-disk preflight result is ready:true with no blocked reasons, that the cache
schema/flags/SHA256-from-bytes/push-limit are intact, that the common
intersection grid supports K in {2,3,5}, and that the preflight exits non-zero
(fail-closed) when a gate value is falsified.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import preflight_c304 as pf  # noqa: E402


def _run_preflight():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "preflight_c304.py"), "--json"],
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
    assert meta["interval"] == "1h"
    assert meta["source_interval"] == "mark_index_1h"
    assert meta["n_symbols"] is not None and int(meta["n_symbols"]) >= 1
    assert meta["common_grid_bars"] is not None and int(meta["common_grid_bars"]) > 0
    assert meta["real_data_only"] is True
    assert meta["fabricated_data"] is False
    assert meta["executed_fills"] is False
    assert meta["cache_format"] == "plain_numpy_ndarrays_no_pandas_legs"
    assert meta["under_push_limit"] is True
    assert meta["cache_pkl_mb"] < 100.0
    assert meta["sha256_from_bytes"] == meta["actual_sha256"]
    assert meta["source_host"] == "https://data.binance.vision"


def test_preflight_common_grid_supports_k_2_3_5():
    out = _run_preflight()
    cov = out["checks"]["coverage"]
    assert int(cov["n_symbols"]) >= 10
    assert set(cov["k_values"]) == {2, 3, 5}
    assert cov["min_required_for_max_k"] == 10
    assert cov["coverage_ok"] is True


def _detail_symbols(out):
    return list(out["checks"]["assets"]["detail"].keys())


def test_preflight_per_asset_frames_on_common_grid_present_finite():
    out = _run_preflight()
    meta = out["checks"]["meta"]
    n_bars = int(meta["common_grid_bars"])
    detail = out["checks"]["assets"]["detail"]
    assert len(detail) == int(meta["n_symbols"])
    for s, d in detail.items():
        assert d["n_bars"] == n_bars, s
        for leg in ("mark_open", "mark_high", "mark_low", "mark_close",
                    "index_open", "index_high", "index_low", "index_close",
                    "basis"):
            f = d["fields"][leg]
            assert f["all_finite_present"] is True, (s, leg)
            assert f["duplicate"] == 0, (s, leg)
            assert f["ok"], (s, leg)
        assert d["perp_close"]["ok"], s
        c = d["perp_close"]
        assert c["nan_count"] >= 0, s
        assert c["all_finite_present"] is True, s
        assert c["all_positive_present"] is True, s
        assert d["funding"]["ok"], s
        assert d["funding"]["funding_rows"] >= 90, s
        assert d["funding"]["hour_multiple_of_8"], s


def test_preflight_wf_splits_fit_window():
    out = _run_preflight()
    detail = out["checks"]["assets"]["detail"]
    for s, d in detail.items():
        assert d["walk_forward"]["n_splits"] >= 1, s
        assert d["walk_forward"]["ok"], s


def test_preflight_feature_warmup_before_first_oos_test_bar():
    out = _run_preflight()
    wu = out["checks"]["assets"]["detail"][_detail_symbols(out)[0]]["feature_warmup"]
    assert wu["ok"]
    assert set(wu["lookbacks_1h"]) == {24, 48, 96, 168, 336, 720, 1440, 2160}
    for L in ("L=24", "L=48", "L=96", "L=168", "L=336", "L=720", "L=1440", "L=2160"):
        assert wu["warmup"][L]["warm_before_first_test_bar"] is True
        assert wu["warmup"][L]["ok"] is True


def test_preflight_provenance_present():
    out = _run_preflight()
    assert out["checks"]["provenance"]["exists"] is True
    assert out["checks"]["provenance"]["ok"] is True


def test_preflight_fails_closed_when_meta_flag_falsified(tmp_path, monkeypatch):
    """A falsified real_data_only flag must make the preflight fail-closed."""
    import preflight_c304 as p

    real_meta = p.PXL_META.read_text()
    fake_meta = tmp_path / "campaign304_mark_index_basis_xsec.meta.json"
    fake_meta.write_text(real_meta.replace('"real_data_only": true', '"real_data_only": false'))
    monkeypatch.setattr(p, "PXL_META", fake_meta)
    monkeypatch.setattr(sys, "argv", ["preflight_c304.py"])
    rc = p.main()
    assert rc != 0, "preflight must fail-closed on falsified real_data_only"
