"""Tests for C343 preflight (scripts/preflight_c343.py): fail-closed verification
of the real C343 USDT-M intraday VOLATILITY-CLUSTERING / ABSOLUTE-RETURN
AUTOCORRELATION SEASONAL DISLOCATION feature cache.

Runs the real preflight as a subprocess and asserts ready:true, the pre-registered
NaN policy, provenance flags, and the volatility-clustering schema. No network,
no fabricated market data."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run_preflight() -> dict:
    out = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "preflight_c343.py"), "--json"],
        cwd=str(ROOT), capture_output=True, text=True,
    )
    assert out.returncode == 0, out.stderr + out.stdout
    return json.loads(out.stdout)


def test_preflight_ready_on_real_cache():
    d = _run_preflight()
    assert d["ready"] is True
    assert d["blocked_reasons"] == []
    assert d["campaign"] == 343
    assert d["real_data_only"] is True
    assert d["fabricated_data"] is False
    assert d["executed_fills"] is False


def test_preflight_grid_and_shards():
    d = _run_preflight()
    grid = d["checks"]["grid"]
    assert grid["n_symbols"] == 10
    assert grid["n_grid_bars"] == 315648
    assert grid["grid_start_utc"].startswith("2023-01")
    assert grid["grid_end_utc"].startswith("2025-12")
    assert d["checks"]["shards"]["ok"] is True
    assert d["checks"]["shards"]["n_shards"] == 10
    meta = d["checks"]["meta"]
    assert meta["fields"] == ["index_ms", "perp_close", "log_return",
                              "abs_ret", "sq_ret", "funding_rate"]
    assert meta["source_campaign"] == 312
    assert meta["network_ingest"] is False and meta["resample"] is False
    assert meta["total_shard_mb"] < 100.0


def test_preflight_nan_policy():
    d = _run_preflight()
    fi = d["checks"]["feature_integrity"]
    assert fi["ok"] is True
    assert fi["raw_nan_total"] == 0
    per = fi["per_shard"]
    for sym, rep in per.items():
        assert rep["log_return_all_finite"] is True, sym
        assert rep["log_return_first_zero"] is True, sym
        assert rep["abs_ret_all_finite"] is True, sym
        assert rep["abs_ret_nonnegative"] is True, sym
        assert rep["sq_ret_all_finite"] is True, sym
        assert rep["sq_ret_nonnegative"] is True, sym
        assert rep["funding_all_nan_control_only"] is True, sym
        assert rep["perp_close_all_positive"] is True, sym


def test_preflight_provenance_present():
    prov = ROOT / "data" / "cache" / "campaign343_volatility_clustering_5m.provenance.json"
    assert prov.exists()
    meta = json.loads((ROOT / "data" / "cache" / "campaign343_volatility_clustering_5m.meta.json").read_text())
    assert meta["campaign"] == 343
    assert meta["source_campaign"] == 312
    assert meta["real_data_only"] is True
    assert meta["fabricated_data"] is False
    assert meta["network_ingest"] is False
    assert meta["resample"] is False


def test_cache_meta_fields_are_genuinely_distinct():
    meta = json.loads((ROOT / "data" / "cache" / "campaign343_volatility_clustering_5m.meta.json").read_text())
    assert meta["campaign"] == 343
    assert meta["source_campaign"] == 312
    for f in ("index_ms", "perp_close", "log_return", "abs_ret", "sq_ret", "funding_rate"):
        assert f in meta["fields"]
    # genuinely-distinct from C341 price-impact / vwvol fields
    for f in ("pid", "vwvol", "price_impact"):
        assert f not in meta["fields"]
    # genuinely-distinct from C340 activity-dispersion CV fields
    for f in ("vol_cv", "notional_cv", "flow_cv", "tc_cv"):
        assert f not in meta["fields"]
    # genuinely-distinct from C342 volume-weighted return moments fields
    for f in ("vw_ret", "skew", "kurt"):
        assert f not in meta["fields"]
    # genuinely-distinct from C326 signed-return autocorr fields
    for f in ("ret_acf", "signed_ret_acf"):
        assert f not in meta["fields"]
