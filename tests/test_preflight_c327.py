"""Preflight C327 tests (scripts/preflight_c327.py): verify the real C327
USDT-M cross-sectional intraday signed-jump-variation seasonality cache
structure, flags, and raw-feature integrity / zero-NaN policy on the committed
real-data shards (no network, no fabrication)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import preflight_c327 as PF  # noqa: E402


def _load_meta():
    return json.loads(PF.CACHE_META.read_text())


def test_c327_meta_flags_and_source():
    m = _load_meta()
    assert m["campaign"] == 327
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
    assert m["fields"] == ["index_ms", "perp_close", "log_return", "r2",
                           "abs_r", "signed_r2", "bipower", "funding_rate"]


def test_c327_shards_exist_and_manifest_matches():
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


def test_c327_shard_contents_and_zero_nan_policy():
    m = _load_meta()
    for s in m["symbols"]:
        with np.load(PF.CACHE_DIR / f"{s}.npz") as z:
            assert set(z.files) == {"index_ms", "perp_close", "log_return",
                                    "r2", "abs_r", "signed_r2", "bipower",
                                    "funding_rate"}
            pc = np.asarray(z["perp_close"], dtype=float)
            lr = np.asarray(z["log_return"], dtype=float)
            r2 = np.asarray(z["r2"], dtype=float)
            ar = np.asarray(z["abs_r"], dtype=float)
            sr = np.asarray(z["signed_r2"], dtype=float)
            bp = np.asarray(z["bipower"], dtype=float)
            fr = np.asarray(z["funding_rate"], dtype=float)
        assert np.isfinite(pc).all() and (pc > 0).all()
        assert np.isfinite(lr).all()
        assert lr[0] == 0.0
        assert np.isfinite(r2).all()
        assert np.isfinite(ar).all()
        assert np.isfinite(sr).all()
        assert np.isfinite(bp).all()
        # exact jump-variation identities (fail-closed on imputation)
        assert np.allclose(r2, lr * lr, rtol=1e-4, atol=1e-8)
        assert np.allclose(ar, np.abs(lr), rtol=1e-4, atol=1e-8)
        assert np.allclose(sr, lr * np.abs(lr), rtol=1e-4, atol=1e-8)
        assert bp[0] == 0.0
        assert np.allclose(bp[1:], np.abs(lr[1:]) * np.abs(lr[:-1]), rtol=1e-4, atol=1e-8)
        assert np.isnan(fr).all()
        # raw fields carry zero NaN
        assert int(np.isnan(lr).sum()) == 0
        assert int(np.isnan(r2).sum()) == 0
        assert int(np.isnan(ar).sum()) == 0
        assert int(np.isnan(sr).sum()) == 0
        assert int(np.isnan(bp).sum()) == 0


def test_c327_grid_and_window():
    m = _load_meta()
    assert m["n_grid_bars"] == 315648
    assert str(m["grid_start_utc"]).startswith("2023-01")
    assert str(m["grid_end_utc"]).startswith("2025-12")


def test_c327_provenance_exists():
    assert PF.CACHE_PROV.exists()
    p = json.loads(PF.CACHE_PROV.read_text())
    assert p["real_data_only"] is True and p["fabricated_data"] is False
    assert p["campaign"] == 327


def test_c327_preflight_ready():
    import subprocess
    import sys as _sys
    r = subprocess.run([_sys.executable, "scripts/preflight_c327.py", "--json"],
                       cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    obj = json.loads(r.stdout)
    assert obj["ready"] is True
    assert obj["blocked_reasons"] == []


def test_c327_feature_integrity_reported():
    """Preflight must report per-shard raw-feature integrity and assert zero NaN
    plus the exact jump-variation identities (fail-closed gate)."""
    import subprocess
    import sys as _sys
    r = subprocess.run([_sys.executable, "scripts/preflight_c327.py", "--json"],
                       cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    obj = json.loads(r.stdout)
    fi = obj["checks"]["feature_integrity"]
    assert fi["ok"] is True
    assert fi["raw_nan_total"] == 0
    assert len(fi["per_shard"]) >= 10
    for s, rep in fi["per_shard"].items():
        assert rep["ok"] is True, s
        assert rep["r2_equals_r_squared"] is True, s
        assert rep["abs_equals_abs_log_return"] is True, s
        assert rep["signed_r2_equals_r_abs_r"] is True, s
        assert rep["bipower_equals_prev_abs_product"] is True, s
        assert rep["bipower_first_zero"] is True, s
        assert rep["funding_all_nan_control_only"] is True, s
