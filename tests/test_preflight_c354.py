"""Tests for C354 preflight (scripts/preflight_c354.py): fail-closed verification
of the real C354 USDT-M cross-sectional intraday HIGUCHI FRACTAL DIMENSION ×
seasonal-dislocation feature cache.

Runs the real preflight as a subprocess and asserts ready:true, the pre-registered
NaN policy, provenance flags, the higuchi parameter schema, and that the raw
fields are genuinely distinct (price-only, volume-free) from every prior frozen
campaign. No network, no fabricated market data."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run_preflight() -> dict:
    out = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "preflight_c354.py"), "--json"],
        cwd=str(ROOT), capture_output=True, text=True,
    )
    assert out.returncode == 0, out.stderr + out.stdout
    return json.loads(out.stdout)


def test_preflight_ready_on_real_cache():
    d = _run_preflight()
    assert d["ready"] is True
    assert d["blocked_reasons"] == []
    assert d["campaign"] == 354
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
                              "abs_ret", "funding_rate"]
    assert meta["source_campaign"] == 312
    assert meta["network_ingest"] is False and meta["resample"] is False
    assert meta["total_shard_mb"] < 100.0


def test_preflight_nan_policy():
    d = _run_preflight()
    fi = d["checks"]["feature_integrity"]
    assert fi["ok"] is True
    assert fi["raw_nan_total"] == 0
    for sym, rep in fi["per_shard"].items():
        assert rep["perp_close_all_finite"] is True, sym
        assert rep["perp_close_all_positive"] is True, sym
        assert rep["log_return_all_finite"] is True, sym
        assert rep["log_return_first_zero"] is True, sym
        assert rep["abs_ret_all_finite"] is True, sym
        assert rep["abs_ret_nonnegative"] is True, sym
        assert rep["funding_all_nan_control_only"] is True, sym


def test_preflight_provenance_present():
    prov = ROOT / "data" / "cache" / "campaign354_higuchi_fractal_5m.provenance.json"
    assert prov.exists()
    meta_path = ROOT / "data" / "cache" / "campaign354_higuchi_fractal_5m.meta.json"
    meta = json.loads(meta_path.read_text())
    assert meta["campaign"] == 354
    assert meta["source_campaign"] == 312
    assert meta["real_data_only"] is True
    assert meta["fabricated_data"] is False
    assert meta["network_ingest"] is False
    assert meta["resample"] is False


def test_preflight_hfd_params_registered():
    meta_path = ROOT / "data" / "cache" / "campaign354_higuchi_fractal_5m.meta.json"
    meta = json.loads(meta_path.read_text())
    hfp = meta["hfd_params"]
    assert hfp["window_W"] == 256
    assert hfp["kmax"] == 16
    assert list(hfp["scales_k"]) == list(range(1, 17))


def test_cache_meta_fields_are_genuinely_distinct():
    meta_path = ROOT / "data" / "cache" / "campaign354_higuchi_fractal_5m.meta.json"
    meta = json.loads(meta_path.read_text())
    assert meta["campaign"] == 354
    assert meta["source_campaign"] == 312
    for f in ("index_ms", "perp_close", "log_return", "abs_ret", "funding_rate"):
        assert f in meta["fields"]
    # higuchi fractal dimension is runner-derived from perp_close; the cache must
    # stay price-only and volume-free, and must NOT relabel any prior campaign's
    # derived fields.
    for f in ("hfd", "hfd_norm"):  # C354 higuchi
        assert f not in meta["fields"]
    for f in ("vr8", "vr16", "vr", "variance_ratio"):  # C353 variance ratio
        assert f not in meta["fields"]
    for f in ("lw", "lw_abs", "d", "d_hat"):        # C352 local-Whittle
        assert f not in meta["fields"]
    for f in ("gph", "gph_abs"):                    # C351 GPH
        assert f not in meta["fields"]
    for f in ("dfa", "dfa_norm", "alpha"):          # C350 DFA
        assert f not in meta["fields"]
    for f in ("rs_norm", "rs_dir", "rs_raw"):       # C346 rescaled range
        assert f not in meta["fields"]
    for f in ("perm_ent", "perm_ent_norm"):         # C349 permutation entropy
        assert f not in meta["fields"]
    for f in ("ret_acf", "signed_ret_acf"):         # C326 return autocorr
        assert f not in meta["fields"]
    for f in ("vcl1", "vcl5", "vcr"):               # C343 vol clustering
        assert f not in meta["fields"]
    for f in ("chop", "mrv", "sq_ret"):             # C344 chop
        assert f not in meta["fields"]
    for f in ("dd_long", "dd_frac", "dd_long_norm"):  # C347 drawdown duration
        assert f not in meta["fields"]
    for f in ("hhi", "hhi_norm"):                   # C348 realized-var conc
        assert f not in meta["fields"]
    for f in ("pid", "vwvol", "price_impact"):      # C341/C334 price impact
        assert f not in meta["fields"]
    for f in ("vw_ret", "skew", "kurt"):            # C342 vol-wtd moments
        assert f not in meta["fields"]
