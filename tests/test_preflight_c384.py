"""Tests for C384 preflight (scripts/preflight_c384.py): schema/flag validation of
emitted real-data artifacts. No network, no fabricated market data."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import preflight_c384 as P  # noqa: E402


def test_preflight_ready_true_on_real_cache():
    """Integration test: preflight exits 0 with ready:true on the real C384 cache."""
    result = subprocess.run(
        [sys.executable, "-m", "scripts.preflight_c384"],
        cwd=ROOT, capture_output=True, text=True, timeout=60
    )
    assert result.returncode == 0, f"preflight failed: {result.stderr}"
    out = json.loads(result.stdout)
    assert out["ready"] is True
    assert out["campaign"] == 384
    assert out["real_data_only"] is True
    assert out["fabricated_data"] is False
    assert out["executed_fills"] is False


def test_preflight_artifact_flags():
    """Verify emitted artifacts carry required flags."""
    result = subprocess.run(
        [sys.executable, "-m", "scripts.preflight_c384", "--json"],
        cwd=ROOT, capture_output=True, text=True, timeout=60
    )
    assert result.returncode == 0
    out = json.loads(result.stdout)
    assert out["ready"] is True
    checks = out["checks"]
    assert checks["meta"]["ok"] is True
    assert checks["shards"]["ok"] is True
    assert checks["manifest"]["ok"] is True
    assert checks["per_symbol"]["ok"] is True
    assert checks["feature_integrity"]["ok"] is True
    assert checks["provenance"]["ok"] is True
    assert out["blocked_reasons"] == []


if __name__ == "__main__":
    test_preflight_ready_true_on_real_cache()
    test_preflight_artifact_flags()
    print("All C384 preflight tests passed")
