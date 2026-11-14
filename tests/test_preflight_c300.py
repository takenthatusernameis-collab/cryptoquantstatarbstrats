"""Tests for the C300 preflight script.

The C300 preflight is the fail-closed gate that must pass before the real
per-asset (2020-01 .. 2026-10) USDT-M perp funding-carry / spot-perp basis
time-series campaign runs at NATIVE 5m. These tests keep it honest: the script
must exist, pin the dataset shape/window/WF/lookback/funding/push-limit checks,
and report ready=true on the verified real ingested cache (compact ndarray form
< 100 MB). Spot feed gaps (462 bars/asset across 12 months) are recorded, not
imputed; funding is NaN at non-boundary bars by design; the runner's fail-closed
gates block any trade requiring missing spot or stale funding data.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "preflight_c300.py"
META = ROOT / "data" / "cache" / "campaign300_multianual_perp_funding_basis_ts_5m.meta.json"
PKL = ROOT / "data" / "cache" / "campaign300_multianual_perp_funding_basis_ts_5m.pkl"
PROV = ROOT / "data" / "cache" / "campaign300_multianual_perp_funding_basis_ts_5m.provenance.json"


def _latest_ts(part: str) -> str:
    matches = sorted(ROOT.glob(f"reports/campaign300_{part}_*.json"))
    assert matches, f"missing C300 artifact for {part}"
    return matches[-1].name.split(f"campaign300_{part}_")[1].split(".json")[0]


def test_preflight_script_pins_campaign_invariants() -> None:
    assert SCRIPT.exists(), f"missing C300 preflight script: {SCRIPT}"
    text = SCRIPT.read_text(encoding="utf-8")
    assert 'EXPECTED_INTERVAL = "5m"' in text
    assert "WF_TRAIN = 25920" in text
    assert "WF_TEST = 8640" in text
    assert "WF_STEP = 8640" in text
    assert "LOOKBACKS_5M = (288, 1008, 2016)" in text
    assert "STALE_BARS = 24 * 12 + 1" in text
    assert "MIN_BARS = 34560" in text
    assert "PUSH_LIMIT_BYTES = 100_000_000" in text
    assert "sha256_from_bytes" in text
    assert "https://data.binance.vision" in text


def test_meta_records_real_data_only_and_per_asset_shape() -> None:
    assert META.exists(), f"missing C300 meta: {META}"
    meta = json.loads(META.read_text())
    assert meta["real_data_only"] is True
    assert meta["fabricated_data"] is False
    assert meta["executed_fills"] is False
    assert meta["interval"] == "5m"
    assert meta["source_interval"] == "5m"
    assert meta["n_symbols"] >= 1
    assert meta["total_bars"] > 0
    assert meta["window_start_utc"] == "2020-01-01T00:00:00Z"
    assert meta["window_end_utc"] == "2026-10-31T23:55:00Z"
    assert meta["source_host"] == "https://data.binance.vision"
    assert meta["cache_format"] == "plain_numpy_ndarrays_no_pandas_legs"
    assert meta["under_push_limit"] is True
    assert "sha256_from_bytes" in meta and meta["sha256_from_bytes"]
    ivs = meta.get("valid_funding_intervals", [])
    assert set(ivs).issubset({1, 2, 4, 8})


def test_cache_is_compact_ndarray_form_under_100mb() -> None:
    assert PKL.exists(), f"missing C300 cache: {PKL}"
    nbytes = PKL.stat().st_size
    assert nbytes < 100_000_000, f"cache {nbytes/1e6:.2f} MB >= 100 MB push limit"
    import pickle

    with open(PKL, "rb") as fh:
        payload = pickle.load(fh)
    assert payload["real_data_only"] is True
    assert payload["fabricated_data"] is False
    assert payload["executed_fills"] is False
    for sym, pa in payload["per_asset"].items():
        for key in ("perp_close", "spot_close", "funding_rates"):
            assert key in pa, f"{sym} missing {key}"
        # no pandas legs allowed (that is what blew the push limit)
        import numpy as np
        import pandas as pd

        for key in ("perp_close", "spot_close", "funding_rates", "index"):
            assert not isinstance(pa[key], (pd.Series, pd.DataFrame, pd.DatetimeIndex)), (
                f"{sym}.{key} is a pandas leg (must be ndarray): {type(pa[key])}"
            )
        assert np.issubdtype(np.asarray(pa["index"]).dtype, np.datetime64)


def test_preflight_reports_ready_on_ingested_cache() -> None:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert proc.returncode == 0, f"preflight failed: {proc.stdout}\n{proc.stderr}"
    result = json.loads(proc.stdout)
    assert result["ready"] is True
    assert result["blocked_reasons"] == []
    assert result["real_data_only"] is True
    assert result["fabricated_data"] is False
    checks = result["checks"]
    assert checks["meta"]["ok"] is True
    assert checks["meta"]["actual_sha256"] == checks["meta"]["sha256_from_bytes"]
    assert checks["meta"]["under_push_limit"] is True
    assert checks["assets"]["ok"] is True
    assert checks["assets"]["n_symbols"] == checks["meta"]["n_symbols"]
    for sym, d in checks["assets"]["detail"].items():
        assert d["ok"], f"{sym} asset not ok: {d}"
        perp = d["fields"]["perp_close"]
        assert perp["ok"] is True, f"{sym} perp_close: {perp}"
        assert perp["nan_count"] == 0
        assert perp["all_positive_present"] is True
        assert perp["spacing_5m_ok"] is True
        assert perp["exact_index_ok"] is True
        # spot leg carries the 462 un-imputed gap bars as NaN
        spot = d["fields"]["spot_close"]
        assert spot["ok"] is True, f"{sym} spot_close: {spot}"
        assert spot["nan_count"] == 462, f"{sym} spot gaps != 462: {spot['nan_count']}"
        assert d["spot_gaps"]["ok"] is True
        assert d["spot_gaps"]["gap_months_recorded"] > 0
        # funding may be NaN at non-boundary bars by design; staleness bounded
        fund = d["funding"]
        assert fund["ok"] is True, f"{sym} funding: {fund}"
        assert fund["funding_rows"] == 7488
        assert fund["stale_ok"] is True
        assert d["walk_forward"]["ok"] is True
        assert d["walk_forward"]["n_splits"] > 0
        assert d["feature_warmup"]["ok"] is True
    assert checks["provenance"]["ok"] is True


def test_pkl_sha_matches_meta() -> None:
    sha = hashlib.sha256(PKL.read_bytes()).hexdigest()
    meta = json.loads(META.read_text())
    assert sha == meta["sha256_from_bytes"]


def test_artifacts_reference_consistent_sha256() -> None:
    ts = _latest_ts("verdict")
    verdict = json.loads((ROOT / f"reports/campaign300_verdict_{ts}.json").read_text())
    assert verdict.get("verdict") == "NOT_TRADABLE"
    assert verdict.get("edge_proven") is False
    assert verdict.get("campaign") == 300
    for key, path_key in (
        ("oos_sweep_sha256", "oos_sweep_artifact"),
        ("registry_sha256", "registry_artifact"),
        ("summary_sha256", "summary_artifact"),
        ("binding_constraint_sha256", "binding_constraint_artifact"),
    ):
        artifact_path = verdict.get(path_key)
        assert artifact_path, f"verdict missing {path_key}"
        p = ROOT / artifact_path
        assert p.exists(), f"referenced artifact missing: {artifact_path}"
        assert hashlib.sha256(p.read_bytes()).hexdigest() == verdict[key], f"sha256 mismatch for {artifact_path}"