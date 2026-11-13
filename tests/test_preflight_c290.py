"""Tests for the C290 preflight script.

The C290 preflight is the fail-closed gate that must pass before the wider-universe
true-5m OHLCV cross-sectional campaign runs. These tests keep it honest: the script
must exist, pin the dataset shape/window/WF/lookback checks, and report ready=true on
the verified real ingested OHLCV cache.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "preflight_c290.py"
META = ROOT / "data" / "cache" / "campaign290_ohlcv.meta.json"


def test_preflight_script_pins_campaign_invariants() -> None:
    assert SCRIPT.exists(), f"missing C290 preflight script: {SCRIPT}"
    text = SCRIPT.read_text(encoding="utf-8")
    assert "EXPECTED_ROWS = 26208" in text
    assert "EXPECTED_WF_SPLITS = 151" in text
    assert "LOOKBACKS_5M = (288, 1008, 2016)" in text
    assert "WF_TRAIN = 720" in text
    assert "WF_TEST = 168" in text
    assert "WF_STEP = 168" in text
    assert '"quote_volumes"' in text or "'quote_volumes'" in text
    assert "sha256_from_bytes" in text


def test_meta_records_real_data_only_and_full_shape() -> None:
    assert META.exists(), f"missing C290 meta: {META}"
    meta = json.loads(META.read_text())
    assert meta["real_data_only"] is True
    assert meta["fabricated_data"] is False
    assert meta["interval"] == "5m"
    assert meta["rows"] == 26208
    assert meta["window_start_utc"] == "2026-08-01T00:00:00Z"
    assert meta["window_end_utc"] == "2026-10-30T23:55:00Z"
    assert len(meta["symbols"]) >= 20  # wider than the prior 11-asset universe
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
    assert checks["frames"]["n_symbols"] >= 20
    for frame in checks["frames"]["detail"].values():
        assert frame["ok"] is True
        assert frame["all_positive"] is True
        assert frame["nan_count"] == 0
    assert checks["walk_forward"]["n_splits"] == 151
    assert checks["walk_forward"]["ok"] is True
    assert checks["feature_warmup"]["ok"] is True