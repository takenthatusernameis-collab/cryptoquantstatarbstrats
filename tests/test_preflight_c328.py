"""Preflight C328 tests (scripts/preflight_c328.py): verify the real C328
USDT-M cross-sectional intraday sign-streak seasonality cache structure, flags,
and raw-feature integrity / zero-NaN policy on the committed real-data shards
(no network, no fabrication)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import preflight_c328 as PF  # noqa: E402


def _load_meta():
    return json.loads(PF.CACHE_META.read_text())


def test_c328_meta_flags_and_source():
    m = _load_meta()
    assert m["campaign"] == 328
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
    assert m["fields"] == ["index_ms", "perp_close", "log_return",
                           "sign_run", "sign_chg", "funding_rate"]


def test_c328_shards_exist_and_manifest_matches():
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


def test_c328_shard_contents_and_zero_nan_policy():
    m = _load_meta()
    for s in m["symbols"]:
        with np.load(PF.CACHE_DIR / f"{s}.npz") as z:
            assert set(z.files) == {"index_ms", "perp_close", "log_return",
                                    "sign_run", "sign_chg", "funding_rate"}
            pc = np.asarray(z["perp_close"], dtype=float)
            lr = np.asarray(z["log_return"], dtype=float)
            sr = np.asarray(z["sign_run"], dtype=float)
            sc = np.asarray(z["sign_chg"], dtype=float)
            fr = np.asarray(z["funding_rate"], dtype=float)
        assert np.isfinite(pc).all() and (pc > 0).all()
        assert np.isfinite(lr).all()
        assert lr[0] == 0.0
        assert np.isfinite(sr).all()
        assert np.isfinite(sc).all()
        # sign_chg is binary 0/1
        assert ((sc == 0.0) | (sc == 1.0)).all()
        assert sr[0] == 0.0
        assert sc[0] == 0.0
        # exact sign-sequence reset identities (fail-closed on imputation)
        sgn = np.sign(lr)
        exp_sr = np.zeros(len(lr), dtype=float)
        for t in range(1, len(lr)):
            if sgn[t] != 0 and sgn[t] == sgn[t - 1]:
                exp_sr[t] = exp_sr[t - 1] + 1.0
            else:
                exp_sr[t] = 1.0 if sgn[t] != 0 else 0.0
        assert np.allclose(sr, exp_sr, rtol=0, atol=1e-9)
        exp_sc = np.zeros(len(lr), dtype=float)
        for t in range(1, len(lr)):
            exp_sc[t] = 1.0 if (sgn[t] != 0 and sgn[t - 1] != 0 and sgn[t] != sgn[t - 1]) else 0.0
        assert np.allclose(sc, exp_sc, rtol=0, atol=1e-9)
        assert np.isnan(fr).all()
        # raw fields carry zero NaN
        assert int(np.isnan(lr).sum()) == 0
        assert int(np.isnan(sr).sum()) == 0
        assert int(np.isnan(sc).sum()) == 0


def test_c328_grid_and_window():
    m = _load_meta()
    assert m["n_grid_bars"] == 315648
    assert str(m["grid_start_utc"]).startswith("2023-01")
    assert str(m["grid_end_utc"]).startswith("2025-12")


def test_c328_provenance_exists():
    assert PF.CACHE_PROV.exists()
    p = json.loads(PF.CACHE_PROV.read_text())
    assert p["real_data_only"] is True and p["fabricated_data"] is False
    assert p["campaign"] == 328


def test_c328_preflight_ready():
    import subprocess
    import sys as _sys
    r = subprocess.run([_sys.executable, "scripts/preflight_c328.py", "--json"],
                       cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    obj = json.loads(r.stdout)
    assert obj["ready"] is True
    assert obj["blocked_reasons"] == []


def test_c328_feature_integrity_reported():
    """Preflight must report per-shard raw-feature integrity and assert zero NaN
    plus the exact sign-sequence identities (fail-closed gate)."""
    import subprocess
    import sys as _sys
    r = subprocess.run([_sys.executable, "scripts/preflight_c328.py", "--json"],
                       cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    obj = json.loads(r.stdout)
    fi = obj["checks"]["feature_integrity"]
    assert fi["ok"] is True
    assert fi["raw_nan_total"] == 0
    assert len(fi["per_shard"]) >= 10
    for s, rep in fi["per_shard"].items():
        assert rep["ok"] is True, s
        assert rep["sign_run_identity_ok"] is True, s
        assert rep["sign_chg_identity_ok"] is True, s
        assert rep["sign_chg_binary"] is True, s
        assert rep["sign_run_first_zero"] is True, s
        assert rep["sign_chg_first_zero"] is True, s
        assert rep["funding_all_nan_control_only"] is True, s
