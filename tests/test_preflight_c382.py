"""Tests for C382 preflight (scripts/preflight_c382.py): schema/flag validation of
emitted real-data artifacts. No network, no fabricated market data."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import preflight_c382 as P  # noqa: E402


def test_preflight_ready_true_on_real_cache():
    """Integration test: preflight exits 0 with ready:true on the real C382 cache."""
    result = subprocess.run(
        [sys.executable, "-m", "scripts.preflight_c382"],
        cwd=ROOT, capture_output=True, text=True, timeout=60
    )
    assert result.returncode == 0, f"preflight failed: {result.stderr}"
    out = json.loads(result.stdout)
    assert out["ready"] is True
    assert out["campaign"] == 382
    assert out["real_data_only"] is True
    assert out["fabricated_data"] is False
    assert out["executed_fills"] is False


def test_preflight_artifact_flags():
    """Verify emitted artifacts carry required flags."""
    result = subprocess.run(
        [sys.executable, "-m", "scripts.preflight_c382", "--json"],
        cwd=ROOT, capture_output=True, text=True, timeout=60
    )
    assert result.returncode == 0
    out = json.loads(result.stdout)
    assert out["ready"] is True
    checks = out["checks"]
    assert checks["meta"]["real_data_only"] is True
    assert checks["meta"]["fabricated_data"] is False
    assert checks["meta"]["network_ingest"] is False
    assert checks["meta"]["resample"] is False
    assert checks["meta"]["executed_fills"] is False
    assert checks["meta"]["under_push_limit"] is True
    assert checks["meta"]["under_cache_budget"] is True
    assert checks["meta"]["tailmem_params"]["window_W"] == 256
    assert checks["meta"]["tailmem_params"]["tail_q"] == 0.90
    assert checks["meta"]["tailmem_params"]["lags"] == [1, 4]
    assert checks["feature_integrity"]["ok"] is True
    assert checks["feature_integrity"]["raw_nan_total"] == 0
    assert checks["per_symbol"]["ok"] is True
    assert checks["provenance"]["ok"] is True


def test_cache_meta_tailmem_params_distinct():
    """Verify C382 cache meta has distinct TAILMEM params (not other campaign params)."""
    meta_path = ROOT / "data" / "cache" / "campaign382_tailmem_5m.meta.json"
    if not meta_path.exists():
        return
    meta = json.loads(meta_path.read_text())
    assert meta["campaign"] == 382
    assert meta["source_campaign"] == 312
    assert "tailmem_params" in meta
    assert meta["tailmem_params"]["window_W"] == 256
    assert meta["tailmem_params"]["tail_q"] == 0.90
    assert meta["tailmem_params"]["lags"] == [1, 4]
    for other in ("qspread_params", "rar_params", "lvac_params", "hill_params", "rskek_params",
                  "opte_params", "qatm_params", "dsrv_params", "ker_params",
                  "rqv_params", "bpv_params", "rmad_params", "gmd_params",
                  "rskrkt_params", "tirv_params", "rlrv_params", "signrun_params",
                  "acovk_params", "pslope_params", "vovr_params", "curv_params",
                  "semicov_params"):
        assert other not in meta


if __name__ == "__main__":
    test_preflight_ready_true_on_real_cache()
    test_preflight_artifact_flags()
    test_cache_meta_tailmem_params_distinct()
    print("All C382 preflight tests passed")
