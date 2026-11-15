"""Tests for C307 preflight (scripts/preflight_c307.py): fail-closed
verification of the real COIN-M multi-asset term-structure + cross-sectional
funding-carry cache before the C307 runner executes.

These tests never fetch, impute, resample, or fabricate data. They assert the
on-disk preflight result is ready:true with no blocked reasons, that the cache
schema/flags/SHA256-from-bytes/push-limit are intact, that the common
term-structure grids (Leg A) and funding grid (Leg B) have required properties,
and that the preflight exits non-zero (fail-closed) when a gate value is falsified.
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

import preflight_c307 as pf  # noqa: E402


def _run_preflight():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "preflight_c307.py"), "--json"],
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
    assert meta["source_interval"] == "coin_m_klines_1h"
    assert meta["n_assets"] is not None and int(meta["n_assets"]) >= 1
    assert meta["real_data_only"] is True
    assert meta["fabricated_data"] is False
    assert meta["executed_fills"] is False
    assert meta["cache_format"] == "plain_numpy_ndarrays_no_pandas_legs"
    assert meta["under_push_limit"] is True
    assert meta["cache_pkl_mb"] < 100.0
    assert meta["sha256_from_bytes"] == meta["actual_sha256"]
    assert meta["source_host"] == "https://data.binance.vision"


def test_preflight_leg_a_contracts_overlap_ge_2():
    out = _run_preflight()
    contracts = out["checks"]["leg_a_contracts"]
    assert contracts["ok"] is True
    for a, d in contracts["detail"].items():
        assert d["n_contracts"] >= 2, (a, d)
        assert d["bars_ge2_contracts"] > 0, (a, d)


def test_preflight_leg_a_per_asset_frames_on_common_grid_present_finite():
    out = _run_preflight()
    detail = out["checks"]["leg_a_assets"]["detail"]
    assert len(detail) > 0
    for a, d in detail.items():
        assert d["n_bars"] > 0, a
        assert d["perp_close"]["ok"], a
        c = d["perp_close"]
        assert c["nan_count"] >= 0, a
        assert c["all_finite_present"] is True, a
        assert c["all_positive_present"] is True, a
        assert d["n_contracts_at_bar"]["bars_ge2"] > 0, a
        assert d["walk_forward"]["ok"], a


def test_preflight_leg_a_wf_splits_fit_window():
    out = _run_preflight()
    detail = out["checks"]["leg_a_assets"]["detail"]
    for a, d in detail.items():
        assert d["walk_forward"]["n_splits"] >= 1, a
        assert d["walk_forward"]["ok"], a


def test_preflight_leg_a_feature_warmup_before_first_oos_test_bar():
    out = _run_preflight()
    first_asset = list(out["checks"]["leg_a_assets"]["detail"].keys())[0]
    wu = out["checks"]["leg_a_assets"]["detail"][first_asset]["feature_warmup"]
    assert wu["ok"]
    # Data-window constraint: min_periods(L) = max(20, L // 3) must fit within
    # train=720 bars; L=4320/8640 are degenerate (flat through the whole
    # training set) and excluded rather than passed with a weakened gate.
    expected_lookbacks = [24, 48, 168, 336, 720, 1440]
    assert set(wu["lookbacks_1h"]) == set(expected_lookbacks), wu["lookbacks_1h"]
    for L in ("L=24", "L=48", "L=168", "L=336", "L=720", "L=1440"):
        assert wu["warmup"][L]["warm_before_first_test_bar"] is True, L
        assert wu["warmup"][L]["ok"] is True, L


def test_preflight_leg_b_funding_grid_nonempty_and_in_window():
    out = _run_preflight()
    leg_b = out["checks"]["leg_b"]
    assert leg_b["ok"] is True
    assert leg_b["n_symbols"] >= 11  # all 11 perps
    assert leg_b["n_bars"] > 0
    assert leg_b["n_assets_with_funding"] >= 2
    assert leg_b["window_start_utc"] >= "2022-07-01"
    assert leg_b["window_end_utc"] < "2026-07-01"


def test_preflight_leg_b_per_symbol_frames_present_finite():
    out = _run_preflight()
    leg_b_detail = out["checks"]["leg_b"]["detail"]
    assert len(leg_b_detail) >= 11
    for s, d in leg_b_detail.items():
        assert d["ok"], (s, d)
        assert d["fields"][f"perp_close_{s}"]["ok"], (s, d)
        assert d["fields"][f"funding_rate_{s}"]["ok"], (s, d)
        assert d["fields"][f"funding_present_{s}"]["ok"], (s, d)


def test_preflight_leg_b_feature_warmup():
    out = _run_preflight()
    wu = out["checks"]["leg_b_feature_warmup"]
    assert wu["ok"]
    expected_lookbacks = [24, 48, 168, 336, 720, 1440]
    assert set(wu["lookbacks_1h"]) == set(expected_lookbacks), wu["lookbacks_1h"]
    for L in ("L=24", "L=48", "L=168", "L=336", "L=720", "L=1440"):
        assert wu["warmup"][L]["warm_before_first_test_bar"] is True, L
        assert wu["warmup"][L]["ok"] is True, L


def test_preflight_leg_b_walk_forward_splits_fit():
    out = _run_preflight()
    wf = out["checks"]["leg_b_walk_forward"]
    assert wf["ok"] is True
    assert wf["n_splits"] >= 1
    assert wf["bars"] >= 720 + 168


def test_preflight_leg_b_cross_sectional_k_support():
    out = _run_preflight()
    leg_b = out["checks"]["leg_b"]
    # Need >= 10 finite assets for K=5 (2*K)
    assert leg_b["n_assets_with_funding"] >= 10


def test_preflight_provenance_present():
    out = _run_preflight()
    assert out["checks"]["provenance"]["exists"] is True
    assert out["checks"]["provenance"]["ok"] is True


def test_preflight_fails_closed_when_meta_flag_falsified(tmp_path, monkeypatch):
    """A falsified real_data_only flag must make the preflight fail-closed."""
    import preflight_c307 as p

    real_meta = p.PXL_META.read_text()
    fake_meta = tmp_path / "campaign307_coinm_multiasset_term_structure_carry.meta.json"
    fake_meta.write_text(real_meta.replace('"real_data_only": true', '"real_data_only": false'))
    monkeypatch.setattr(p, "PXL_META", fake_meta)
    monkeypatch.setattr(sys, "argv", ["preflight_c307.py"])
    rc = p.main()
    assert rc != 0, "preflight must fail-closed on falsified real_data_only"