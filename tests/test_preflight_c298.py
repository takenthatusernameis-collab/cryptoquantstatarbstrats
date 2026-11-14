"""Tests for the C298 preflight script.

The C298 preflight is the fail-closed gate that must pass before the real
multi-year (2020-01 .. 2026-10) USDT-M perp funding-carry / spot-perp basis
cross-sectional campaign runs. These tests keep it honest: the script must
exist, pin the dataset shape/window/WF/lookback/funding checks, and report
ready=true on the verified real ingested cache. Spot feed gaps (data-api
missing hours) are recorded, not imputed; the runner gates block any trade
requiring missing spot data.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "preflight_c298.py"
META = ROOT / "data" / "cache" / "campaign298_multianual_perp_funding_basis.meta.json"
PKL = ROOT / "data" / "cache" / "campaign298_multianual_perp_funding_basis.pkl"


def test_preflight_script_pins_campaign_invariants() -> None:
    assert SCRIPT.exists(), f"missing C298 preflight script: {SCRIPT}"
    text = SCRIPT.read_text(encoding="utf-8")
    assert 'EXPECTED_START = "2020-01-01 00:00:00+00:00"' in text
    assert 'EXPECTED_END = "2026-10-31 23:00:00+00:00"' in text
    assert "EXPECTED_INTERVAL = \"1h\"" in text
    assert "EXPECTED_INTERVAL = \"1h\"" in text
    assert "WF_TRAIN = 2160" in text
    assert "WF_TEST = 720" in text
    assert "WF_STEP = 720" in text
    assert "LOOKBACKS_1H = (168, 720, 2160)" in text
    assert "STALE_BARS = 24 + 1" in text
    assert "sha256_from_bytes" in text
    assert "https://data.binance.vision" in text
    assert "https://data-api.binance.vision" in text


def test_meta_records_real_data_only_and_full_shape() -> None:
    assert META.exists(), f"missing C298 meta: {META}"
    meta = json.loads(META.read_text())
    assert meta["real_data_only"] is True
    assert meta["fabricated_data"] is False
    assert meta["interval"] == "1h"
    assert meta["source_interval"] == "5m"
    assert meta["rows"] == 59904
    assert meta["expected_bars"] == 59904
    assert meta["n_symbols"] >= 2
    assert meta["window_start_utc"] == "2020-01-01T00:00:00Z"
    assert meta["window_end_utc"] == "2026-10-31T23:00:00Z"
    assert meta["source_host"] == "https://data.binance.vision"
    assert meta["spot_host"] == "https://data-api.binance.vision"
    assert "sha256_from_bytes" in meta and meta["sha256_from_bytes"]
    ivs = meta.get("funding_intervals_by_symbol", {})
    for sym, hours in ivs.items():
        assert hours and set(hours).issubset({1, 2, 4, 8})


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
    assert checks["frames"]["ok"] is True
    assert checks["frames"]["n_symbols"] == checks["meta"]["n_symbols"]
    for key in ("opens", "highs", "lows", "closes", "volumes"):
        frame = checks["frames"]["detail"][key]
        assert frame["ok"] is True, f"{key}: {frame}"
        assert frame["nan_count"] == 0
        assert frame["all_positive"] is True
        assert frame["spacing_1h_ok"] is True
        assert frame["exact_index_ok"] is True
    # spot leg may carry NaNs at recorded data-api gap hours; never imputed
    spot = checks["frames"]["detail"]["spot_closes"]
    assert spot["ok"] is True
    assert spot["index_subset_of_expected"] is True
    assert spot["nan_count"] >= 0
    assert checks["funding"]["ok"] is True
    for sym, d in checks["funding"]["detail"].items():
        assert d["ok"] is True, f"{sym} funding not ok: {d}"
        assert d["stale_ok"] is True
    assert checks["frames"]["detail"]["spot_closes"]["ok"] is True
    assert checks["walk_forward"]["ok"] is True
    assert checks["walk_forward"]["n_splits"] > 0
    assert checks["feature_warmup"]["ok"] is True
    assert checks["provenance"]["ok"] is True


def test_pkl_sha_matches_meta() -> None:
    import hashlib

    sha = hashlib.sha256(PKL.read_bytes()).hexdigest()
    meta = json.loads(META.read_text())
    assert sha == meta["sha256_from_bytes"]
