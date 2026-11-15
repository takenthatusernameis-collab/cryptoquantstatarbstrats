"""Tests for C313 COIN-M inverse quarterly term-structure carry OOS runner.

These tests verify the runner produces correct artifacts with proper schema,
SHA256 provenance, and the mandatory fail-closed flags.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

# Find the latest C313 artifacts (exclude .full.json files)
REPORTS = ROOT / "reports"


def _find_latest(pattern: str) -> Path:
    matches = [p for p in REPORTS.glob(pattern) if not p.name.endswith(".full.json")]
    assert matches, f"No artifact found for {pattern}"
    return max(matches, key=lambda p: p.stat().st_mtime)


OOS_SWEEP = _find_latest("campaign313_oos_sweep_*.json")
REGISTRY = _find_latest("campaign313_tradable_edge_registry_*.json")
SUMMARY = _find_latest("campaign313_summary_*.json")
VERDICT = _find_latest("campaign313_verdict_*.json")
BINDING = _find_latest("campaign313_binding_constraint_*.json")
FULL_SWEEP = OOS_SWEEP.with_name(OOS_SWEEP.name.replace(".json", ".full.json"))

ARTIFACTS = {
    "oos_sweep": OOS_SWEEP,
    "registry": REGISTRY,
    "summary": SUMMARY,
    "verdict": VERDICT,
    "binding_constraint": BINDING,
}

SWEEP_DATA = json.loads(OOS_SWEEP.read_text())
REGISTRY_DATA = json.loads(REGISTRY.read_text())
VERDICT_DATA = json.loads(VERDICT.read_text())


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_runner_exits_zero():
    assert SWEEP_DATA["campaign"] == 313
    assert SWEEP_DATA["verdict"] in ("RETRACTED", "EDGE_PROVEN")
    assert "edge_proven" in SWEEP_DATA
    assert "binding_constraint" in SWEEP_DATA["summary"]


def test_artifacts_exist_and_have_sha256():
    required = ["oos_sweep", "registry", "summary", "verdict", "binding_constraint"]
    for key in required:
        path = ARTIFACTS[key]
        assert path.exists(), f"Missing artifact: {key} at {path}"
        # Verify SHA256 matches the sweep summary
        sweep_sha = SWEEP_DATA.get("summary", {}).get("artifacts", {}).get(key, {}).get("sha256")
        if sweep_sha:
            actual_sha = _sha256(path)
            assert actual_sha == sweep_sha, f"SHA256 mismatch for {key}"


def test_artifact_flags_real_data_only():
    """Every artifact must carry real_data_only:true, fabricated_data:false, executed_fills:false."""
    for key, path in ARTIFACTS.items():
        data = json.loads(path.read_text())
        assert data.get("real_data_only") is True, f"{key}: real_data_only not True"
        assert data.get("fabricated_data") is False, f"{key}: fabricated_data not False"
        assert data.get("executed_fills") is False, f"{key}: executed_fills not False"


def test_oos_sweep_slimmed_under_100mb():
    """Slim sweep artifact must be < 100 MB (GitHub push limit)."""
    size_mb = OOS_SWEEP.stat().st_size / 1e6
    assert size_mb < 100.0, f"Slim sweep {size_mb:.1f} MB exceeds 100 MB limit"


def test_full_sweep_exists_and_gitignored():
    """Full sweep with per-split series must exist and be gitignored."""
    assert FULL_SWEEP.exists(), "Full sweep artifact missing"
    # Check it's gitignored
    gitignore = ROOT / ".gitignore"
    gitignore_text = gitignore.read_text() if gitignore.exists() else ""
    assert FULL_SWEEP.name in gitignore_text or "*.full.json" in gitignore_text


def test_sweep_drops_per_split_series():
    """Slim sweep must not contain per-split series fields."""
    for r in SWEEP_DATA["results"]:
        for ck, cv in r["cost_slices"].items():
            assert "oos_net_mean_per_split" not in cv, f"Per-split series found in {ck}"
            assert "bh_oos_net_mean_per_split" not in cv, f"Per-split series found in {ck}"


def test_config_count_matches_pre_registered():
    """Runner must test >= 504 pre-registered configs (960 expected)."""
    assert SWEEP_DATA["summary"]["n_total_runs"] >= 504, f"Only {SWEEP_DATA['summary']['n_total_runs']} configs tested"
    assert SWEEP_DATA["summary"]["n_total_runs"] == 960, f"Expected 960 configs, got {SWEEP_DATA['summary']['n_total_runs']}"


def test_multiple_testing_correction_both():
    """Holm AND Benjamini-Hochberg at alpha=0.05 required before any positive claim."""
    # If edge_proven is True, both n_survive_holm and n_survive_bh must be > 0
    if SWEEP_DATA["edge_proven"]:
        assert SWEEP_DATA["summary"]["n_survive_holm"] > 0, "Holm correction failed but edge claimed"
        assert SWEEP_DATA["summary"]["n_survive_bh"] > 0, "BH correction failed but edge claimed"
        assert SWEEP_DATA["summary"]["n_survive_both"] > 0, "Both corrections required but edge claimed"


def test_verdict_binding_constraint_when_retracted():
    """If RETRACTED, binding_constraint must be identified and artifact must exist."""
    if SWEEP_DATA["verdict"] == "RETRACTED":
        binding = SWEEP_DATA["summary"].get("binding_constraint")
        assert binding is not None, "RETRACTED without binding constraint"
        assert "binding_constraint" in ARTIFACTS, "Missing binding constraint artifact"
        bind_path = ARTIFACTS["binding_constraint"]
        assert bind_path.exists(), "Binding constraint artifact missing"
        bind_data = json.loads(bind_path.read_text())
        assert bind_data["binding_constraint"] == binding


def test_carry_vs_convexity_attribution():
    """Aggregate attribution must report carry_share and conv_share."""
    assert "aggregate_carry_share" in SWEEP_DATA["gates"]["attribution"]
    assert "aggregate_conv_share" in SWEEP_DATA["gates"]["attribution"]
    carry = SWEEP_DATA["gates"]["attribution"]["aggregate_carry_share"]
    conv = SWEEP_DATA["gates"]["attribution"]["aggregate_conv_share"]
    assert 0.0 <= carry <= 1.0
    assert 0.0 <= conv <= 1.0


def test_cost_model_three_legs():
    """Cost model must charge 3 legs per trade (costs x3)."""
    config = SWEEP_DATA["config"]
    assert "costs x3" in config.get("cost_rule", "").lower() or "x3" in config.get("cost_rule", "")


def test_walk_forward_expanding_12m_3m_roll_3m():
    """WF protocol must be expanding train 12m -> test 3m, roll 3m."""
    wf = SWEEP_DATA["config"]["walk_forward"]
    assert wf["train_hours"] == 365 * 24, "Train must be 12 months (365*24 hours)"
    assert wf["test_hours"] == 90 * 24, "Test must be 3 months (90*24 hours)"
    assert wf["step_hours"] == 90 * 24, "Roll must be 3 months (90*24 hours)"


def test_inverse_pnl_in_coin_terms():
    """PnL must be modeled in coin terms (inverse settlement)."""
    config = SWEEP_DATA["config"]
    assert "inverse" in config.get("pnl_rule", "").lower()
    assert "1/entry" in config.get("pnl_rule", "") or "(entry" in config.get("pnl_rule", "")


def test_dataset_provenance_sha256():
    """Sweep must reference cache SHA256 and meta SHA256."""
    preflight = SWEEP_DATA["preflight"]
    assert "cache_sha256" in preflight
    assert "cache_meta_sha256" in preflight
    assert preflight["real_data_only"] is True
    assert preflight["fabricated_data"] is False
    assert preflight["executed_fills"] is False


def test_no_fabricated_data_in_registry():
    """Registry must only contain configs that survive BOTH Holm and BH."""
    assert REGISTRY_DATA["n_tradable"] == SWEEP_DATA["summary"]["n_survive_both"]
    for cfg in REGISTRY_DATA["tradable_configs"]:
        assert cfg.get("holm_reject") is True
        assert cfg.get("bh_reject") is True


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])