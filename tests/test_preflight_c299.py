"""Tests for the C299 preflight script.

The C299 preflight is the fail-closed gate that must pass before the real
per-asset (2020-01 .. 2026-10) USDT-M perp funding-carry / spot-perp basis
time-series campaign runs. These tests keep it honest: the script must exist,
pin the dataset shape/window/WF/lookback/funding checks, and report
ready=true on the verified real ingested cache. Spot feed gaps (data-api
missing hours) are recorded, not imputed; funding is NaN at non-boundary
hours by design; the runner's fail-closed gates block any trade requiring
missing spot or stale funding data.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "preflight_c299.py"
META = ROOT / "data" / "cache" / "campaign299_multianual_perp_funding_basis_ts.meta.json"
PKL = ROOT / "data" / "cache" / "campaign299_multianual_perp_funding_basis_ts.pkl"
PROV = ROOT / "data" / "cache" / "campaign299_multianual_perp_funding_basis_ts.provenance.json"


def _latest_ts(part: str) -> str:
    matches = sorted(ROOT.glob(f"reports/campaign299_{part}_*.json"))
    assert matches, f"missing C299 artifact for {part}"
    return matches[-1].name.split(f"campaign299_{part}_")[1].split(".json")[0]


def test_preflight_script_pins_campaign_invariants() -> None:
    assert SCRIPT.exists(), f"missing C299 preflight script: {SCRIPT}"
    text = SCRIPT.read_text(encoding="utf-8")
    assert "EXPECTED_INTERVAL = \"1h\"" in text
    assert "WF_TRAIN = 2160" in text
    assert "WF_TEST = 720" in text
    assert "WF_STEP = 720" in text
    assert "LOOKBACKS_1H = (168, 720, 2160)" in text
    assert "STALE_BARS = 24 + 1" in text
    assert "MIN_BARS = 2880" in text
    assert "sha256_from_bytes" in text
    assert "https://data.binance.vision" in text
    assert "https://data-api.binance.vision" in text


def test_meta_records_real_data_only_and_per_asset_shape() -> None:
    assert META.exists(), f"missing C299 meta: {META}"
    meta = json.loads(META.read_text())
    assert meta["real_data_only"] is True
    assert meta["fabricated_data"] is False
    assert meta["interval"] == "1h"
    assert meta["source_interval"] == "5m"
    assert meta["n_symbols"] >= 1
    assert meta["total_bars"] > 0
    assert meta["window_start_utc"] == "2020-01-01T00:00:00Z"
    assert meta["window_end_utc"] == "2026-10-31T23:00:00Z"
    assert meta["source_host"] == "https://data.binance.vision"
    assert meta["spot_host"] == "https://data-api.binance.vision"
    assert "sha256_from_bytes" in meta and meta["sha256_from_bytes"]
    ivs = meta.get("valid_funding_intervals", [])
    assert set(ivs).issubset({1, 2, 4, 8})


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
    assert checks["assets"]["ok"] is True
    assert checks["assets"]["n_symbols"] == checks["meta"]["n_symbols"]
    for sym, d in checks["assets"]["detail"].items():
        assert d["ok"], f"{sym} asset not ok: {d}"
        for key in ("opens", "highs", "lows", "closes"):
            frame = d["fields"][key]
            assert frame["ok"] is True, f"{sym}/{key}: {frame}"
            assert frame["nan_count"] == 0
            assert frame["all_positive_present"] is True
            assert frame["spacing_1h_ok"] is True
            assert frame["exact_index_ok"] is True
        # spot leg may carry NaNs at recorded data-api gap hours; never imputed
        spot = d["fields"]["spot_closes"]
        assert spot["ok"] is True, f"{sym} spot: {spot}"
        assert spot["index_in_window"] is True
        assert spot["nan_count"] >= 0
        # funding may be NaN at non-boundary hours by design; staleness bounded
        fund = d["funding"]
        assert fund["ok"] is True, f"{sym} funding: {fund}"
        assert fund["stale_ok"] is True
        assert d["walk_forward"]["ok"] is True
        assert d["walk_forward"]["n_splits"] > 0
        assert d["feature_warmup"]["ok"] is True
    assert checks["provenance"]["ok"] is True


def test_pkl_sha_matches_meta() -> None:
    import hashlib

    sha = hashlib.sha256(PKL.read_bytes()).hexdigest()
    meta = json.loads(META.read_text())
    assert sha == meta["sha256_from_bytes"]


def test_artifacts_reference_consistent_sha256() -> None:
    ts = _latest_ts("verdict")
    verdict = json.loads((ROOT / f"reports/campaign299_verdict_{ts}.json").read_text())
    assert verdict.get("verdict") == "NOT_TRADABLE"
    assert verdict.get("edge_proven") is False
    assert verdict.get("campaign") == 299
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
        import hashlib
        assert hashlib.sha256(p.read_bytes()).hexdigest() == verdict[key], f"sha256 mismatch for {artifact_path}"
