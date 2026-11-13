"""Tests for C289: OOS multiple-testing & minimum-detectable-edge closure
(scripts/run_c289_closure.py) and its preflight.

Covers the statistical primitives (block-bootstrap p-value, Holm, BH, deflated
Sharpe, MDE), preflight SHA pinning, and artifact persistence/SHA256-from-bytes.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import run_c289_closure as c289  # noqa: E402


def test_block_bootstrap_pvalue_detects_positive_and_null():
    rng = np.random.default_rng(0)
    pos = rng.normal(0.01, 0.01, size=151)
    null = rng.normal(0.0, 0.01, size=151)
    p_pos = c289.block_bootstrap_pvalue(pos, n_boot=2000, seed=1)
    p_null = c289.block_bootstrap_pvalue(null, n_boot=2000, seed=2)
    assert p_pos < 0.05
    assert p_null > 0.10


def test_holm_controls_fwer():
    # m=4; p=[0.01,0.04,0.03,0.005] at alpha=0.05
    p = np.array([0.01, 0.04, 0.03, 0.005])
    rej = c289.holm_reject(p, alpha=0.05)
    # sorted: 0.005 (rank0, thr 0.05/4=0.0125) reject; 0.01 (rank1, thr 0.05/3=0.0167) reject;
    # 0.03 (rank2, thr 0.05/2=0.025) not reject -> step-down stops; 0.04 not.
    assert rej[3] and rej[0]
    assert not rej[2] and not rej[1]


def test_bh_controls_fdr():
    p = np.array([0.001, 0.002, 0.003, 0.2])
    rej = c289.bh_reject(p, alpha=0.05)
    assert rej[0] and rej[1] and rej[2]
    assert not rej[3]


def test_deflated_sharpe_high_for_strong_independent_signal():
    # Trials scattered near zero (null-consistent): expected max under null is small,
    # so a Sharpe far above the cloud deflates to a high DSR.
    sr_trials = np.array([0.02, -0.01, 0.03, -0.02, 0.01, 0.0, -0.03, 0.02, -0.01, 0.015])
    dsr_high = c289.deflated_sharpe_ratio(0.5, sr_trials, skew=0.0, kurt=3.0, n_obs=151)
    assert dsr_high > 0.95
    # A Sharpe below the null cloud deflates to a low DSR.
    dsr_low = c289.deflated_sharpe_ratio(-0.05, sr_trials, skew=0.0, kurt=3.0, n_obs=151)
    assert dsr_low < 0.5


def test_mde_decreases_with_sample_size():
    x = np.random.default_rng(0).normal(0.0, 0.01, size=600)
    sd = float(np.std(x, ddof=1))
    mde_small = (c289.Z_975 + c289.Z_80) * sd / np.sqrt(50)
    mde_large = (c289.Z_975 + c289.Z_80) * sd / np.sqrt(500)
    assert mde_large < mde_small


def test_c289_preflight_ready_and_pins_sources():
    import subprocess

    script = ROOT / "scripts" / "preflight_c289.py"
    assert script.exists()
    proc = subprocess.run(
        [sys.executable, str(script), "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert proc.returncode == 0, f"preflight failed: {proc.stdout}\n{proc.stderr}"
    result = json.loads(proc.stdout)
    assert result["ready"] is True
    assert result["blocked_reasons"] == []
    assert result["total_configs"] == 162
    assert result["checks"]["c286_oos_sweep"]["sha_ok"] is True
    assert result["checks"]["c288_oos_sweep"]["sha_ok"] is True


def test_c289_artifacts_exist_with_real_data_flags_and_sha256():
    parts = ("closure", "summary", "verdict")
    paths = {}
    for part in parts:
        matches = sorted(ROOT.glob(f"reports/campaign289_{part}_*.json"))
        assert matches, f"missing C289 artifact for {part}"
        paths[part] = matches[-1]
        payload = json.loads(paths[part].read_text())
        assert payload.get("real_data_only") is True
        assert payload.get("fabricated_data") is False

    verdict = json.loads(paths["verdict"].read_text())
    assert verdict["campaign"] == 289
    assert "economic_space_closed" in verdict
    for key, path_key in (
        ("closure_sha256", "closure_artifact"),
        ("summary_sha256", "summary_artifact"),
    ):
        artifact_path = verdict.get(path_key)
        assert artifact_path
        p = ROOT / artifact_path
        assert p.exists()
        assert c289.sha256_file(p) == verdict[key]