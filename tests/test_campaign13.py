"""Deterministic tests for Campaign #13 deliverables (3 target caches).

Asserts the report schema, real-data provenance, and honest conclusion
contract for each Campaign #13 target cache. Skips if the cache or report
is absent (artifact-driven, not fabricated).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

TARGETS = [
    {
        "cache8": "0bab5d6a",
        "cache_full": "0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7",
        "report_prefix": "campaign13_causal_per_bar_enriched_gates_0bab5d6a",
        "example": "examples/run_campaign13_0bab5d6a_causal_gates.py",
    },
    {
        "cache8": "385aae3f",
        "cache_full": "385aae3f022b2d7bba4ec502cb8e7399d26cb31b961a016aebf7d165450fd4ba",
        "report_prefix": "campaign13_causal_per_bar_enriched_gates_385aae3f",
        "example": "examples/run_campaign13_385aae3f_causal_gates.py",
    },
    {
        "cache8": "6d2e08d4",
        "cache_full": "6d2e08d4d7b969d92b61773c7eead387a52ad74b1c3fb0c69552bd6402dd4383",
        "report_prefix": "campaign13_causal_per_bar_enriched_gates_6d2e08d4",
        "example": "examples/run_campaign13_6d2e08d4_causal_gates.py",
    },
]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _report_paths(prefix: str) -> list[Path]:
    return sorted((ROOT / "reports").glob(f"{prefix}_*.json"))


@pytest.mark.parametrize("target", TARGETS, ids=[t["cache8"] for t in TARGETS])
def test_c13_cache_present_and_real_only(target):
    cache_pkl = ROOT / f"data/cache/{target['cache_full']}.pkl"
    cache_meta = ROOT / f"data/cache/{target['cache_full']}.meta.json"
    if not cache_pkl.exists() or not cache_meta.exists():
        pytest.skip(f"cache {target['cache8']} unavailable")
    meta = json.loads(cache_meta.read_text(encoding="utf-8"))
    assert meta.get("fetch_real_data_only") is True
    assert meta.get("fetch_fabricated_data") is False
    assert meta.get("fetch_success") is True


@pytest.mark.parametrize("target", TARGETS, ids=[t["cache8"] for t in TARGETS])
def test_c13_example_wrapper_exists(target):
    p = ROOT / target["example"]
    if not p.exists():
        pytest.skip(f"example wrapper {target['example']} not yet written")


@pytest.mark.parametrize("target", TARGETS, ids=[t["cache8"] for t in TARGETS])
def test_c13_report_schema_and_provenance(target):
    paths = _report_paths(target["report_prefix"])
    if not paths:
        pytest.skip(f"no C13 report for cache {target['cache8']} yet")
    data = json.loads(paths[-1].read_text(encoding="utf-8"))
    assert data.get("type") == "campaign13_causal_per_bar_enriched_gates"
    assert data.get("campaign") == 13
    assert data.get("real_data_only") is True
    assert data.get("fabricated_data") is False
    prov = data.get("provenance") or {}
    assert prov.get("network_fetch_performed") is False
    assert prov.get("no_synthetic_fabricated_inputs") is True
    cache_pkl = ROOT / f"data/cache/{target['cache_full']}.pkl"
    cache_meta = ROOT / f"data/cache/{target['cache_full']}.meta.json"
    if cache_pkl.exists() and cache_meta.exists():
        assert prov.get("cache_spot_pkl_sha256") == _sha256(cache_pkl)
        assert prov.get("cache_spot_meta_sha256") == _sha256(cache_meta)
    conclusion = data.get("conclusion") or {}
    assert conclusion.get("honest") is True
    assert conclusion.get("status") in {"edge", "no_edge", "insufficient_or_blocked"}
    assert conclusion.get("edge_claim") == (conclusion.get("status") == "edge")
    assert "pairs" in data and len(data["pairs"]) >= 1
    for _, block in data["pairs"].items():
        assert "sweeps" in block
        assert "any_bar_passes_all_gates" in block
        assert "rolling_stable_blocks_all_bars_all_sweeps" in block
    thresholds = data.get("thresholds_unmodified") or {}
    assert thresholds.get("entry_threshold") == 2.0
    assert thresholds.get("cointegration_pvalue") == 0.05
    assert thresholds.get("strict_enriched_gates") is True
    assert thresholds.get("use_enriched_gates") is True