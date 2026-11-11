"""Deterministic test for Campaign #12 cache 4c3bc2f1 deliverable.

Asserts the report schema, real-data provenance, and honest conclusion
contract. Skips if the cache or report is absent (artifact-driven, not
fabricated).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CACHE_FULL = "4c3bc2f1ad1323961abdc5280080e595fc9f9b5791d8b7f642a1303eac6d26cd"
CACHE8 = "4c3bc2f1"
CACHE_PKL = ROOT / f"data/cache/{CACHE_FULL}.pkl"
CACHE_META = ROOT / f"data/cache/{CACHE_FULL}.meta.json"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _report_paths() -> list[Path]:
    pattern = f"campaign12_causal_per_bar_enriched_gates_{CACHE8}_*.json"
    return sorted((ROOT / "reports").glob(pattern))


def test_c12_4c3bc2f1_cache_present_and_real_only():
    if not CACHE_PKL.exists() or not CACHE_META.exists():
        pytest.skip(f"cache {CACHE8} unavailable")
    meta = json.loads(CACHE_META.read_text(encoding="utf-8"))
    assert meta.get("fetch_real_data_only") is True
    assert meta.get("fetch_fabricated_data") is False


def test_c12_4c3bc2f1_report_schema_and_provenance():
    paths = _report_paths()
    if not paths:
        pytest.skip(f"no C12 report for cache {CACHE8} yet")
    data = json.loads(paths[-1].read_text(encoding="utf-8"))
    assert data.get("type") == "campaign12_causal_per_bar_enriched_gates"
    assert data.get("campaign") == 12
    assert data.get("real_data_only") is True
    assert data.get("fabricated_data") is False
    prov = data.get("provenance") or {}
    assert prov.get("network_fetch_performed") is False
    assert prov.get("no_synthetic_fabricated_inputs") is True
    if CACHE_PKL.exists() and CACHE_META.exists():
        assert prov.get("cache_spot_pkl_sha256") == _sha256(CACHE_PKL)
        assert prov.get("cache_spot_meta_sha256") == _sha256(CACHE_META)
    conclusion = data.get("conclusion") or {}
    assert conclusion.get("honest") is True
    assert conclusion.get("status") in {"edge", "no_edge", "insufficient_or_blocked"}
    assert conclusion.get("edge_claim") == (conclusion.get("status") == "edge")
    assert "pairs" in data and len(data["pairs"]) >= 1
    for _, block in data["pairs"].items():
        assert "sweeps" in block
        assert "any_bar_passes_all_gates" in block
        assert "rolling_stable_blocks_all_bars_all_sweeps" in block
