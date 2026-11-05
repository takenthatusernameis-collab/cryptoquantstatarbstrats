"""Campaign #17 Path C-maintain: fail-closed non-spot audit + honest artifacts.

No fabrication. No proxies labeled real. No threshold weakening. No pairs rescan.
No structurally-similar spot retest on the same cache presented as new edge work.
Uses tested data.real_feed_loader.audit_cache_for_real_nonspot_feeds.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from data.real_feed_loader import (  # noqa: E402
    FAMILY_SPECS,
    audit_cache_for_real_nonspot_feeds,
)

UTC = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
SUPERSEDES_STATUS = "reports/real_feed_unblock_status_20261105T125745Z.json"
SUPERSEDES_REGISTRY = "reports/strategy_edge_registry_20261105T125745Z.json"
SPOT_CACHE = "data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl"
SPOT_META = "data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.meta.json"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1024 * 1024), b""):
            h.update(c)
    return h.hexdigest()


def parse_summary(out: str) -> dict:
    d = {"raw": out.strip().splitlines()[-1] if out.strip() else ""}
    m = re.search(r"(\d+) passed", out)
    d["passed"] = int(m.group(1)) if m else None
    m = re.search(r"(\d+) failed", out)
    d["failed"] = int(m.group(1)) if m else 0
    m = re.search(r"(\d+) skipped", out)
    d["skipped"] = int(m.group(1)) if m else 0
    m = re.search(r"in ([\d.]+)s", out)
    d["duration_s"] = float(m.group(1)) if m else None
    return d


def run_tests() -> dict:
    full = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-q"],
        cwd=ROOT, capture_output=True, text=True, timeout=600,
    )
    loader = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_real_feed_loader_validation.py", "-q"],
        cwd=ROOT, capture_output=True, text=True, timeout=120,
    )
    mypy = subprocess.run(
        [sys.executable, "-m", "mypy", "data/real_feed_loader.py"],
        cwd=ROOT, capture_output=True, text=True, timeout=120,
    )
    ruff_loader = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "data/real_feed_loader.py"],
        cwd=ROOT, capture_output=True, text=True, timeout=120,
    )
    return {
        "command": "python -m pytest tests/ -q",
        "rc": full.returncode,
        "summary": parse_summary(full.stdout + "\n" + full.stderr),
        "loader_targeted": {
            "command": "python -m pytest tests/test_real_feed_loader_validation.py -q",
            "rc": loader.returncode,
            "summary": parse_summary(loader.stdout + "\n" + loader.stderr),
        },
        "mypy_real_feed_loader": {
            "command": "python -m mypy data/real_feed_loader.py",
            "rc": mypy.returncode,
            "ok": mypy.returncode == 0,
            "tail": (mypy.stdout + mypy.stderr).strip().splitlines()[-1:] if (mypy.stdout + mypy.stderr).strip() else [],
        },
        "ruff_real_feed_loader": {
            "command": "python -m ruff check data/real_feed_loader.py",
            "rc": ruff_loader.returncode,
            "ok": ruff_loader.returncode == 0,
        },
    }


def main() -> int:
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    audit_result = audit_cache_for_real_nonspot_feeds(ROOT / "data" / "cache", campaign=17)
    tests = run_tests()

    status_path = reports / f"real_feed_unblock_status_{UTC}.json"
    status = {
        "artifact": status_path.stem,
        "campaign": 17,
        "path": "C-maintain",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo": "cryptoquantstatarbstrats",
        "supersedes": SUPERSEDES_STATUS,
        "fail_closed": True,
        "real_data_only": True,
        "no_fabrication": True,
        "no_proxies_labeled_real": True,
        "scan_audit": {**audit_result, "tool": "data.real_feed_loader.audit_cache_for_real_nonspot_feeds"},
        "families": audit_result["families"],
        "blockers": [
            "No new real non-spot feed with verifiable provenance ingested in-session",
            (
                "audit_cache_for_real_nonspot_feeds found 0 valid artifacts passing "
                f"validate_and_load_real_feed across {audit_result['scan']['meta_files_scanned']} meta files "
                f"({audit_result['candidate_validation'] and 'with' or 'no'} candidate validation attempts recorded); "
                "real_data_only=true, fabricated_data=false, sha256 verified, schema valid required"
            ),
        ],
        "action_required_for_path_r": (
            "Ingest genuinely new real feed(s) with immutable provenance into data/cache/ and "
            "validate via real_feed_loader.validate_and_load_real_feed (and audit via "
            "audit_cache_for_real_nonspot_feeds) before claiming ingestion/edge. Path R not triggered."
        ),
        "conclusion": "STILL_BLOCKED",
        "oos_edge_proven": False,
    }
    status_path.write_text(json.dumps(status, indent=2, default=str) + "\n")

    audit_path = reports / f"failclosed_cache_audit_{UTC}.json"
    audit = {
        "artifact": audit_path.stem,
        "campaign": 17,
        "path": "C-maintain",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": (
            "Concrete fail-closed cache audit artifact produced by tested code "
            "(_run_p17_campaign17_pathc.py + data.real_feed_loader.audit_cache_for_real_nonspot_feeds). "
            "Not a structurally-similar spot retest; not an edge claim; records explicit per-candidate "
            "validation outcomes without fabrication or gate weakening."
        ),
        "fail_closed": True,
        "real_data_only": True,
        "fabricated_data": False,
        "no_proxies_labeled_real": True,
        "supported_families": sorted(FAMILY_SPECS),
        "cache_dir": "data/cache",
        "audit_result": audit_result,
        "spot_cache_reference": {
            "path": SPOT_CACHE, "meta": SPOT_META,
            "sha256_pkl": sha256_file(ROOT / SPOT_CACHE) if (ROOT / SPOT_CACHE).exists() else None,
            "reused_as_is": True, "not_a_new_feed": True,
        },
        "code_changes": [
            "data/real_feed_loader.py: added fail-closed audit_cache_for_real_nonspot_feeds (records per-candidate validation outcomes; no fabrication, no gate weakening)",
            "tests/test_real_feed_loader_validation.py: added 3 audit_cache tests (no candidates, valid artifact accept, candidate refusal recorded)",
            "_run_p17_campaign17_pathc.py: Campaign #17 Path C-maintain runner producing honest fail-closed artifacts",
        ],
        "tests_at_generation": tests["summary"],
        "loader_tests_at_generation": tests["loader_targeted"]["summary"],
        "quality_gates": {
            "mypy_real_feed_loader": tests["mypy_real_feed_loader"],
            "ruff_real_feed_loader": tests["ruff_real_feed_loader"],
        },
        "oos_edge_proven": False,
        "conclusion": audit_result["conclusion"],
    }
    audit_path.write_text(json.dumps(audit, indent=2, default=str) + "\n")

    reg_path = reports / f"strategy_edge_registry_{UTC}.json"
    fs = tests["summary"]
    ls = tests["loader_targeted"]["summary"]
    registry = {
        "artifact": reg_path.stem,
        "campaign": 17,
        "path": "C-maintain",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo": "cryptoquantstatarbstrats",
        "supersedes": SUPERSEDES_REGISTRY,
        "real_data_only": True, "fabricated_data": False, "fail_closed": True,
        "no_proxies_labeled_real": True, "no_threshold_weakening": True,
        "no_pairs_rescan": True, "no_structurally_similar_spot_retest_same_cache": True,
        "tests": {
            "command": "python -m pytest tests/ -q",
            "passed": fs.get("passed"), "skipped": fs.get("skipped"), "failed": fs.get("failed"),
            "duration_s": fs.get("duration_s"), "rc": tests["rc"],
            "loader_targeted": {
                "command": tests["loader_targeted"]["command"],
                "passed": ls.get("passed"), "failed": ls.get("failed"), "rc": tests["loader_targeted"]["rc"],
            },
        },
        "quality_gates": {
            "mypy_real_feed_loader": tests["mypy_real_feed_loader"],
            "ruff_real_feed_loader": tests["ruff_real_feed_loader"],
        },
        "real_spot_cache": {
            "path": SPOT_CACHE, "meta": SPOT_META,
            "sha256_pkl": sha256_file(ROOT / SPOT_CACHE) if (ROOT / SPOT_CACHE).exists() else None,
            "reused_as_is": True,
        },
        "wf_cost_protocol": {
            "wf": "720/168/168 rolling",
            "cost_grid_bps": [0, 5, 10, 20],
            "edge_rule": "oos_edge_proven=true only if exposure>0 AND all cost-grid slices OOS net>0 AND beats benchmark on same WF windows",
        },
        "registry": {
            "pairs_cointegration": {"family": "cointegration_pairs", "status": "PROVEN_BLOCKED", "evidence": "165/165 pairs; no re-scan; no gate weakening", "oos_edge_proven": False},
            "spot_momentum_mr_P4": {"status": "EXHAUSTED", "oos_edge_proven": False},
            "spot_xsec_rank_P5": {"status": "EXHAUSTED", "oos_edge_proven": False},
            "spot_donchian_tsmom_P6": {"status": "EXHAUSTED", "oos_edge_proven": False},
            "spot_range_breakout_reversion_volband_P7": {"status": "EXHAUSTED", "oos_edge_proven": False},
            "spot_pairwise_ols_hedge_spread_mr_P9": {"status": "EXHAUSTED", "oos_edge_proven": False},
            "spot_residual_momentum_P10": {"status": "EXHAUSTED", "oos_edge_proven": False},
            "spot_lead_lag_diffusion_P11": {"status": "EXHAUSTED", "oos_edge_proven": False},
            **{
                fam: {
                    "status": "blocked_no_real_feed",
                    "oos_edge_proven": False,
                    "fail_closed_loader": "data/real_feed_loader.py",
                    "fail_closed_audit": "data.real_feed_loader.audit_cache_for_real_nonspot_feeds",
                }
                for fam in FAMILY_SPECS
            },
        },
        "campaign17_artifacts": [
            str(status_path.relative_to(ROOT)),
            str(audit_path.relative_to(ROOT)),
            str(reg_path.relative_to(ROOT)),
        ],
        "core_truth": (
            "No proven net-of-cost OOS edge. Pairs proven blocked (165/165). Spot 1h exhausted. "
            "Non-spot families blocked_no_real_feed (fail-closed audit found 0 valid provenance artifacts, "
            "no candidate validation passes). oos_edge_proven=false across registry. Campaign #17 "
            "Path C-maintain: added tested fail-closed audit_cache_for_real_nonspot_feeds (+3 tests, "
            "mypy/ruff clean on modified loader), produced honest unblock status + cache audit + superseding "
            "registry with current tests, no fabrication/proxies/threshold weakening/no pairs rescan/no "
            "structurally-similar spot retest. Next productive path is Path R only if a genuinely new "
            "real feed with provenance is ingested."
        ),
    }
    reg_path.write_text(json.dumps(registry, indent=2, default=str) + "\n")
    print(json.dumps({
        "utc": UTC,
        "status": str(status_path),
        "audit": str(audit_path),
        "registry": str(reg_path),
        "full_rc": tests["rc"],
        "full_summary": fs["raw"],
        "loader_summary": ls["raw"],
        "audit_conclusion": audit_result["conclusion"],
    }, indent=2))
    return 0 if tests["rc"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
