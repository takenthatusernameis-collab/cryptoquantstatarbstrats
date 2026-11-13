"""Tests for the C293 preflight script.

The C293 preflight is the fail-closed gate that must pass before the cross-venue
perp funding-carry campaign runs. These tests keep it honest: the script
must exist, pin the dataset shape/window/WF/lookback invariants, and report
ready=true on the verified real ingested Binance+OKX cross-venue funding cache.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "preflight_c293.py"
META = ROOT / "data" / "cache" / "campaign293_crossvenue_funding.meta.json"


def test_preflight_script_pins_campaign_invariants() -> None:
    assert SCRIPT.exists(), f"missing C293 preflight script: {SCRIPT}"
    text = SCRIPT.read_text(encoding="utf-8")
    assert "EXPECTED_ROWS = 23424" in text
    assert "EXPECTED_WF_SPLITS = 135" in text
    assert "LOOKBACKS_5M = (8, 24, 60)" in text
    assert "WF_TRAIN = 720" in text
    assert "WF_TEST = 168" in text
    assert "WF_STEP = 168" in text
    assert '"binance_closes"' in text or "'binance_closes'" in text
    assert '"okx_closes"' in text or "'okx_closes'" in text
    assert '"binance_funding_rates"' in text or "'binance_funding_rates'" in text
    assert '"okx_funding_rates"' in text or "'okx_funding_rates'" in text
    assert "sha256_from_bytes" in text
    assert "real_data_only" in text
    assert "PARTIAL_SYMBOLS" in text
    assert "BNBUSDT" in text
    assert "TAOUSDT" in text
    assert "ONDOUSDT" in text
    assert "PUMPUSDT" in text


def test_meta_records_real_data_only_and_full_shape() -> None:
    assert META.exists(), f"missing C293 meta: {META}"
    meta = json.loads(META.read_text())
    assert meta["real_data_only"] is True
    assert meta["fabricated_data"] is False
    assert meta["interval"] == "5m"
    assert meta["rows"] == 23424
    assert meta["expected_rows"] == 23424
    assert meta["window_start_utc"] == "2026-08-10T16:00:00Z"
    assert meta["window_end_utc"] == "2026-10-30T23:55:00Z"
    assert meta["n_symbols"] == 24
    assert set(meta["venues"]) == {"binance", "okx"} if "venues" in meta else True
    assert "sha256_from_bytes" in meta
    assert meta["sha256_from_bytes"] == "ea4e5f178f573c8bec9f14e4c6848ad64d7ee9fef9a0c03e1752fe5656f6b554"


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
    assert checks["frames"]["ok"] is True
    assert len(checks["frames"]["detail"]) == 4
    for frame in checks["frames"]["detail"].values():
        assert frame["ok"] is True
        if not frame.get("is_funding", False):
            assert frame["all_positive"] is True
            assert frame["nan_count"] == 0
        assert frame["exact_5m_spacing"] is True
    assert checks["funding_boundary_minute_zero"]["ok"] is True
    assert checks["funding_coverage"]["ok"] is True
    assert checks["funding_coverage"]["excluded_symbols"] == ["BNBUSDT", "ONDOUSDT", "PUMPUSDT", "TAOUSDT"]
    assert checks["active_symbols"]["n"] == 20
    assert checks["walk_forward"]["n_splits"] == 135
    assert checks["walk_forward"]["ok"] is True