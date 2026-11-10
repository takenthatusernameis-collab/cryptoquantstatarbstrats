#!/usr/bin/env python3
"""Generate deterministic per-cache Campaign #12 deliverables (wrapper scripts
and tests) for all 5 target caches.

The wrapper scripts delegate to ``examples/run_campaign12_causal_gates.py``
and the tests assert the report schema/provenance/honesty contract. Nothing
here fabricates data, weakens thresholds, or re-runs C1-C11.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

C12_TARGETS = [
    "90d10b876bb8eda9619cbba73ed19d6c7db4ea7327284f2e33f10a7872a5b263",
    "595e501ade340390c6c3310634c01a4f50de9056b16ccc5af5e16123215b14d5",
    "4fd3e87f85cbd8141cbf73591bec7696ea81cbd325b8ba45baf200b56d35ca9d",
    "4c3bc2f1ad1323961abdc5280080e595fc9f9b5791d8b7f642a1303eac6d26cd",
    "dcd5764a",
]

WRAPPER_TEMPLATE = '''#!/usr/bin/env python3
"""Campaign #12 causal per-bar enriched-gate evaluation for cache __CACHE8__.

Wraps ``examples/run_campaign12_causal_gates.py`` for cache
``__CACHE_FULL__``. Real cached spot only; no network refetch; no synthetic
inputs; gate thresholds unmodified.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    cmd = [
        sys.executable,
        str(ROOT / "examples" / "run_campaign12_causal_gates.py"),
        "--cache",
        "__CACHE_FULL__",
    ]
    return subprocess.call(cmd, cwd=str(ROOT))


if __name__ == "__main__":
    raise SystemExit(main())
'''

TEST_TEMPLATE = '''"""Deterministic test for Campaign #12 cache __CACHE8__ deliverable.

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
CACHE_FULL = "__CACHE_FULL__"
CACHE8 = "__CACHE8__"
CACHE_PKL = ROOT / f"data/cache/{CACHE_FULL}.pkl"
CACHE_META = ROOT / f"data/cache/{CACHE_FULL}.meta.json"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _report_paths() -> list[Path]:
    return sorted((ROOT / "reports").glob(f"campaign12_causal_per_bar_enriched_gates_{CACHE8}_*.json"))


def test_c12___CACHE8___cache_present_and_real_only():
    if not CACHE_PKL.exists() or not CACHE_META.exists():
        pytest.skip(f"cache {CACHE8} unavailable")
    meta = json.loads(CACHE_META.read_text(encoding="utf-8"))
    assert meta.get("fetch_real_data_only") is True
    assert meta.get("fetch_fabricated_data") is False


def test_c12___CACHE8___report_schema_and_provenance():
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
'''


def main() -> None:
    for full in C12_TARGETS:
        c8 = full[:8]
        ex_path = ROOT / f"examples/run_campaign12_{c8}_causal_gates.py"
        ex_path.write_text(
            WRAPPER_TEMPLATE.replace("__CACHE8__", c8).replace("__CACHE_FULL__", full),
            encoding="utf-8",
        )
        ex_path.chmod(0o755)
        t_path = ROOT / f"tests/test_campaign12_{c8}.py"
        t_path.write_text(
            TEST_TEMPLATE.replace("__CACHE8__", c8).replace("__CACHE_FULL__", full),
            encoding="utf-8",
        )
        print(f"wrote {ex_path.relative_to(ROOT)}")
        print(f"wrote {t_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()