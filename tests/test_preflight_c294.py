"""Tests for the C294 preflight script.

The C294 preflight is the fail-closed gate that must pass before the real implied-
volatility (Deribit DVOL) variance-risk-premium campaign runs.  These tests keep it
honest: the script must exist, pin the dataset shape/window/WF/lookback invariants,
require a real-IV definition (and refuse a realized-vol-as-IV proxy), and report
ready=true on the verified real ingested DVOL + Binance spot 1h cache.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "preflight_c294.py"
META = ROOT / "data" / "cache" / "campaign294_deribit_dvol.meta.json"


def test_preflight_script_pins_campaign_invariants() -> None:
    assert SCRIPT.exists(), f"missing C294 preflight script: {SCRIPT}"
    text = SCRIPT.read_text(encoding="utf-8")
    assert 'EXPECTED_INTERVAL = "1h"' in text
    assert "REQUIRED_SYMBOLS" in text
    assert "LOOKBACKS_1H = (24, 168, 720)" in text
    assert "WF_TRAIN = 720" in text
    assert "WF_TEST = 168" in text
    assert "WF_STEP = 168" in text
    assert 'IV_DEFINITION = "deribit_dvol_index"' in text
    assert "_check_term_structure_not_realized_vol_proxy" in text
    assert "RealFeedValidationError" in text
    assert "sha256_from_bytes" in text
    assert "real_data_only" in text
    assert "fabricated_data" in text


def test_meta_records_real_data_only_and_full_shape() -> None:
    assert META.exists(), f"missing C294 meta: {META}"
    meta = json.loads(META.read_text())
    assert meta["real_data_only"] is True
    assert meta["fabricated_data"] is False
    assert meta["interval"] == "1h"
    assert meta["n_symbols"] == 2
    assert meta["symbols"] == ["BTC", "ETH"]
    assert meta["iv_definition"] == "deribit_dvol_index"
    assert meta["rows"] > 0
    assert meta["rows"] == meta["expected_rows"]
    assert "sha256_from_bytes" in meta
    assert meta["window_start_utc"].startswith("2023-03-24")
    assert meta["window_end_utc"].startswith("2026-11-13")


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
    assert checks["index"]["ok"] is True
    assert checks["index"]["exact_1h_spacing"] is True
    assert checks["alignment"]["ok"] is True
    assert checks["frames"]["ok"] is True
    assert checks["frames"]["dvol_all_finite"] is True
    assert checks["frames"]["spot_all_positive"] is True
    assert checks["realized_vol"]["ok"] is True
    assert checks["coverage"]["ok"] is True
    assert set(checks["coverage"]["detail"]) == {"BTC", "ETH"}
    # Real-IV provenance: DVOL accepted, realized-vol proxy refused
    assert checks["real_iv_provenance"]["dvol_definition_accepted"] is True
    assert checks["real_iv_provenance"]["realized_vol_proxy_refused"] is True
    assert checks["walk_forward"]["ok"] is True
    assert checks["walk_forward"]["n_bars"] > 720 + 168