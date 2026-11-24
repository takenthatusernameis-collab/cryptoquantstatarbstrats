"""Tests for C428 preflight (scripts/preflight_c428.py): schema/flag validation of
emitted real-data artifacts. No network, no fabricated market data."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import preflight_c428 as P  # noqa: E402


def test_preflight_ready_true_on_real_cache():
    """Integration test: preflight exits 0 with ready:true on the real C428 cache."""
    result = subprocess.run(
        [sys.executable, "-m", "scripts.preflight_c428"],
        cwd=ROOT, capture_output=True, text=True, timeout=60
    )
    assert result.returncode == 0, f"preflight failed: {result.stderr}"
    out = json.loads(result.stdout)
    assert out["ready"] is True
    assert out["campaign"] == 428
    assert out["real_data_only"] is True
    assert out["fabricated_data"] is False
    assert out["executed_fills"] is False


def test_preflight_artifact_flags():
    """Verify emitted artifacts carry required flags."""
    result = subprocess.run(
        [sys.executable, "-m", "scripts.preflight_c428", "--json"],
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
    assert checks["meta"]["ptlt_params"]["window_W"] == 256
    assert checks["meta"]["ptlt_params"]["n_bins"] == 32
    assert checks["feature_integrity"]["ok"] is True
    assert checks["feature_integrity"]["raw_nan_total"] == 0
    assert checks["per_symbol"]["ok"] is True
    assert checks["provenance"]["ok"] is True


def test_cache_meta_ptlt_params_distinct():
    """Verify C428 cache meta has distinct PTLT params (not other campaign params)."""
    meta_path = ROOT / "data" / "cache" / "campaign428_ptlt_5m.meta.json"
    if not meta_path.exists():
        return
    meta = json.loads(meta_path.read_text())
    assert meta["campaign"] == 428
    assert meta["source_campaign"] == 312
    assert meta["ptlt_params"]["window_W"] == 256
    assert meta["ptlt_params"]["n_bins"] == 32
    for other in ("wlmf_params", "rqa_params", "loctime_params", "iesd_params", "runlen_params", "zcrpath_params", "coh_params",
                  "rcf_params", "qreg_params", "taildep_params", "tailbeta_params",
                  "signpower_params", "semcorr_params", "xcorr_params", "residvol_params",
                  "leadlag_params", "cdom_params", "ktrend_params", "cbreak_params",
                  "specfm_params", "magnet_params", "ces_params", "vterm_params",
                  "ddrun_params", "semicov_params", "qspread_params", "rvquart_params",
                  "rvq_params", "rqv_params", "lvac_params", "hill_params", "rskek_params",
                  "opte_params", "qatm_params", "dsrv_params", "ker_params", "domfreq_params",
                  "bpv_params", "rmad_params", "gmd_params", "rskrkt_params", "tirv_params",
                  "rlrv_params", "signrun_params", "acovk_params", "pslope_params",
                  "vovr_params", "curv_params", "tailmem_params", "turningpt_params",
                  "extpos_params", "prrough_params", "halfrange_params", "bandx_params",
                  "madr_params", "minrv_params", "xcoex_params", "xskew3_params",
                  "ou_params", "ou_halflife_params", "lmom_params", "tscale_params",
                  "rar_params", "asymcurv_params", "betaasym_params", "beta_params",
                  "market_beta_params", "coskew_params", "cokurt_params", "xsrank_params",
                  "signcomotion_params"):
        assert other not in meta, f"meta must not contain {other} (prior campaign params)"


if __name__ == "__main__":
    test_preflight_ready_true_on_real_cache()
    test_preflight_artifact_flags()
    test_cache_meta_ptlt_params_distinct()
    print("All C428 PTLT preflight tests passed")
