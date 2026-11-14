"""Tests for the C297 preflight script.

The C297 preflight is the fail-closed gate that must pass before the daily
multi-year cross-sectional campaign runs. These tests keep it honest: the script
must exist, pin the daily/multi-year invariants, and report ready=true on the
verified real ingested daily OHLCV cache.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "preflight_c297.py"
META = ROOT / "data" / "cache" / "campaign297_daily_ohlcv.meta.json"


def test_preflight_script_pins_campaign_invariants() -> None:
    assert SCRIPT.exists(), f"missing C297 preflight script: {SCRIPT}"
    text = SCRIPT.read_text(encoding="utf-8")
    assert 'EXPECTED_INTERVAL = "1d"' in text
    assert "LOOKBACKS_DAILY = (20, 60, 120)" in text
    assert "WF_TRAIN = 504" in text
    assert "WF_TEST = 126" in text
    assert "WF_STEP = 126" in text
    assert "spacing_1d_ok" in text
    assert "sha256_from_bytes" in text


def test_meta_records_real_data_only_and_daily_window() -> None:
    assert META.exists(), f"missing C297 meta: {META}"
    meta = json.loads(META.read_text())
    assert meta["real_data_only"] is True
    assert meta["fabricated_data"] is False
    assert meta["interval"] == "1d"
    assert meta["horizon"] == "daily_1d_multi_year"
    assert meta["rows"] > 2000  # multi-year daily window
    assert meta["window_start_utc"] == "2021-01-01T00:00:00Z"
    assert meta["window_end_utc"] == "2026-11-13T00:00:00Z"
    assert len(meta["symbols"]) >= 8
    assert meta["source_host"] == "https://data-api.binance.vision"


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
    assert checks["frames"]["ok"] is True
    assert checks["frames"]["n_symbols"] >= 8
    for frame in checks["frames"]["detail"].values():
        assert frame["ok"] is True
        assert frame["all_positive"] is True
        assert frame["nan_count"] == 0
        assert frame["spacing_1d_ok"] is True
    assert checks["walk_forward"]["n_splits"] >= 4
    assert checks["walk_forward"]["ok"] is True
    assert checks["feature_warmup"]["ok"] is True