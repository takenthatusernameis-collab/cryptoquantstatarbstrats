"""Preflight C323 tests (scripts/preflight_c323.py): verify the real C323
intraday order-flow / trade-activity seasonality cache structure, flags, and
zero-activity NaN policy on the committed real-data shards (no network, no
fabrication)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import preflight_c323 as PF  # noqa: E402


def _load_meta():
    return json.loads(PF.CACHE_META.read_text())


def test_c323_meta_flags_and_source():
    m = _load_meta()
    assert m["campaign"] == 323
    assert m["interval"] == "5m"
    assert m["source_campaign"] == 312
    assert m["source_interval"] == "usdt_m_5m_klines_taker_delta_ms"
    assert m["network_ingest"] is False
    assert m["resample"] is False
    assert m["real_data_only"] is True
    assert m["fabricated_data"] is False
    assert m["executed_fills"] is False
    assert m["n_symbols"] >= 10
    assert m["under_push_limit"] is True
    assert m["under_cache_budget"] is True
    assert m["fields"] == ["index_ms", "perp_close", "log_return", "ofi_ratio",
                           "tss_ratio", "log_tc", "log_notional", "funding_rate"]


def test_c323_shards_exist_and_manifest_matches():
    m = _load_meta()
    shard_sha = m["shard_sha256"]
    shard_bytes = m["shard_bytes"]
    assert len(shard_sha) >= 10
    import hashlib
    manifest = {s: shard_sha[s] for s in sorted(shard_sha)}
    manifest_sha = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()
    assert manifest_sha == m["manifest_sha256"]
    for s in shard_sha:
        sp = PF.CACHE_DIR / f"{s}.npz"
        assert sp.exists()
        assert PF.sha256_file(sp) == shard_sha[s]
        assert sp.stat().st_size == int(shard_bytes[s])
        assert sp.stat().st_size < PF.PUSH_LIMIT_BYTES


def test_c323_shard_contents_and_zero_activity_nan_policy():
    m = _load_meta()
    for s in m["symbols"]:
        with np.load(PF.CACHE_DIR / f"{s}.npz") as z:
            assert set(z.files) == {"index_ms", "perp_close", "log_return", "ofi_ratio",
                                    "tss_ratio", "log_tc", "log_notional", "funding_rate"}
            pc = np.asarray(z["perp_close"], dtype=float)
            lr = np.asarray(z["log_return"], dtype=float)
            ofi = np.asarray(z["ofi_ratio"], dtype=float)
            tss = np.asarray(z["tss_ratio"], dtype=float)
            tc = np.asarray(z["log_tc"], dtype=float)
            no = np.asarray(z["log_notional"], dtype=float)
            fr = np.asarray(z["funding_rate"], dtype=float)
        assert np.isfinite(pc).all() and (pc > 0).all()
        assert np.isfinite(lr).all()
        assert lr[0] == 0.0
        assert np.isnan(fr).all()
        # NaN policy cross-checked against the real C312 source shards
        src = np.load(PF.SRC_DIR / f"{s}.npz")
        tv = np.asarray(src["total_volume"], dtype=float)
        tc_src = np.asarray(src["trade_count"], dtype=float)
        no_src = np.asarray(src["notional"], dtype=float)
        # ofi_ratio NaN exactly where total_volume==0, share < 0.1%
        ofi_nan = np.isnan(ofi)
        assert ofi_nan.mean() < PF.NAN_MAX_SHARE
        assert int((ofi_nan & (tv > 0)).sum()) == 0
        assert int((np.isfinite(ofi) & ~(tv > 0)).sum()) == 0
        # tss_ratio NaN exactly where trade_count==0
        tss_nan = np.isnan(tss)
        assert tss_nan.mean() < PF.NAN_MAX_SHARE
        assert int((tss_nan & (tc_src > 0)).sum()) == 0
        assert int((np.isfinite(tss) & ~(tc_src > 0)).sum()) == 0
        # log_tc NaN exactly where trade_count<=0
        tc_nan = np.isnan(tc)
        assert tc_nan.mean() < PF.NAN_MAX_SHARE
        assert int((tc_nan & (tc_src > 0)).sum()) == 0
        assert int((np.isfinite(tc) & ~(tc_src > 0)).sum()) == 0
        # log_notional NaN exactly where notional<=0
        no_nan = np.isnan(no)
        assert no_nan.mean() < PF.NAN_MAX_SHARE
        assert int((no_nan & (no_src > 0)).sum()) == 0
        assert int((np.isfinite(no) & ~(no_src > 0)).sum()) == 0


def test_c323_grid_and_window():
    m = _load_meta()
    assert m["n_grid_bars"] == 315648
    assert str(m["grid_start_utc"]).startswith("2023-01")
    assert str(m["grid_end_utc"]).startswith("2025-12")


def test_c323_provenance_exists():
    assert PF.CACHE_PROV.exists()
    p = json.loads(PF.CACHE_PROV.read_text())
    assert p["real_data_only"] is True and p["fabricated_data"] is False
    assert p["campaign"] == 323


def test_c323_preflight_ready():
    import subprocess
    import sys as _sys
    r = subprocess.run([_sys.executable, "scripts/preflight_c323.py", "--json"],
                       cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    obj = json.loads(r.stdout)
    assert obj["ready"] is True
    assert obj["blocked_reasons"] == []


def test_c323_nan_policy_all_shards_reported():
    """Preflight must report per-shard per-field NaN counts/shares and assert
    100% explained by zero-activity bars (fail-closed gate)."""
    import subprocess
    import sys as _sys
    r = subprocess.run([_sys.executable, "scripts/preflight_c323.py", "--json"],
                       cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    obj = json.loads(r.stdout)
    nap = obj["checks"]["zero_activity_nan_policy"]
    assert nap["ok"] is True
    assert len(nap["per_shard"]) >= 10
    for s, rep in nap["per_shard"].items():
        assert rep["ok"] is True, s
        for fname in ("ofi_ratio", "tss_ratio", "log_tc", "log_notional"):
            fr = rep["per_field"][fname]
            assert fr["ok"] is True, (s, fname)
            assert fr["all_nans_explained"] is True, (s, fname)
            assert fr["nan_share"] < PF.NAN_MAX_SHARE, (s, fname)