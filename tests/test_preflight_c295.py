"""Tests for the C295 preflight script.

The C295 preflight is the fail-closed gate that must pass before the real
three-venue spot cross-venue basis / lead-lag stat-arb campaign runs.  These
tests keep it honest: the script must exist, pin the dataset shape/window/WF/
lookback invariants, require the three-venue real-data cache (Binance+OKX+
Coinbase), and report ready=true on the verified ingested cache.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "preflight_c295.py"
META = ROOT / "data" / "cache" / "campaign295_three_venue_spot.meta.json"
PKL = ROOT / "data" / "cache" / "campaign295_three_venue_spot.pkl"
PROV = ROOT / "data" / "cache" / "campaign295_three_venue_spot.provenance.json"


def test_preflight_script_pins_campaign_invariants() -> None:
    assert SCRIPT.exists(), f"missing C295 preflight script: {SCRIPT}"
    text = SCRIPT.read_text(encoding="utf-8")
    assert 'EXPECTED_INTERVAL = "5m"' in text
    assert "REQUIRED_VENUES" in text
    assert "WF_TRAIN = 720" in text
    assert "WF_TEST = 168" in text
    assert "WF_STEP = 168" in text
    assert "MAX_LOOKBACK_5M = 2016" in text
    assert "sha256_from_bytes" in text
    assert "real_data_only" in text
    assert "fabricated_data" in text
    assert "blocked_reasons" in text


def test_meta_records_real_data_only_and_three_venues() -> None:
    assert META.exists(), f"missing C295 meta: {META}"
    meta = json.loads(META.read_text())
    assert meta["real_data_only"] is True
    assert meta["fabricated_data"] is False
    assert meta["interval"] == "5m"
    assert meta["n_symbols"] >= 1
    assert len(meta["symbols"]) == meta["n_symbols"]
    assert meta["rows"] > 0
    assert meta["rows"] == meta["expected_bars"]
    assert "sha256_from_bytes" in meta
    assert meta["venues"] == ["binance", "okx", "coinbase"]
    assert meta["window_start_utc"].startswith("2026-08-01")
    assert meta["window_end_utc"].startswith("2026-10-30")


def test_provenance_flags_real_data() -> None:
    assert PROV.exists(), f"missing C295 provenance: {PROV}"
    prov = json.loads(PROV.read_text())
    assert prov["real_data_only"] is True
    assert prov["fabricated_data"] is False


def test_pkl_sha_matches_meta() -> None:
    assert PKL.exists(), f"missing C295 pkl: {PKL}"
    import hashlib

    actual = hashlib.sha256(PKL.read_bytes()).hexdigest()
    meta = json.loads(META.read_text())
    assert actual == meta["sha256_from_bytes"]


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
    assert checks["provenance"]["ok"] is True
    assert checks["symbols"]["ok"] is True
    assert checks["window"]["ok"] is True
    assert checks["index"]["ok"] is True
    assert checks["index"]["exact_5m_spacing"] is True
    assert checks["alignment"]["ok"] is True
    assert checks["frames"]["ok"] is True
    assert checks["coverage"]["ok"] is True
    assert checks["walk_forward"]["ok"] is True
    assert checks["walk_forward"]["n_bars"] > 720 + 168
    # every venue must be fully covered
    for venue in ("binance", "okx", "coinbase"):
        assert checks["coverage"]["detail"][venue]["ok"] is True
