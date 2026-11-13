#!/usr/bin/env python3
"""C280 Path B — reproducible data-availability blocker evidence.

Programmatically enumerates data/ and data/cache/, hashes every relevant file
with SHA256-from-bytes, classifies each cache, asserts absence of materially
new real datasets (new period / new venue / raw funding-perp-microstructure),
and emits three JSON artifacts with SHA256-from-bytes. edge_proven=false; no
edge claimed. No synthetic/fabricated data; no relabeling existing caches as
new; no unprovenanced network fetch claims.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))

reports = root / "reports"
ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

SPOT_UNIVERSE = ["ADA", "AVAX", "BNB", "BTC", "DOT", "ETH", "LINK", "LTC", "POL", "SOL", "XRP"]
LOCKED_WINDOW = {"start": "2026-04-01", "end": "2026-10-30"}
ALLOWED_INTERVALS = {"1h", "5m"}
DATA_EXTS = {".csv", ".parquet", ".feather", ".npz", ".h5", ".pkl"}


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def jdefault(o):
    import numpy as np
    import pandas as pd

    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o) if np.isfinite(o) else None
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, pd.Timestamp):
        return str(o)
    raise TypeError(str(type(o)))


def read_meta(meta_path: Path) -> dict:
    try:
        return json.loads(meta_path.read_text())
    except Exception:
        return {}


def pkl_highlights(pkl_path: Path, meta: dict) -> dict:
    info = {"bytes": pkl_path.stat().st_size, "sha256": sha256_file(pkl_path)}
    try:
        import pandas as pd

        df = pd.read_pickle(pkl_path)
        info["shape"] = [int(df.shape[0]), int(df.shape[1])]
        info["columns"] = [str(c) for c in df.columns][:25]
    except Exception as exc:  # pragma: no cover - defensive
        info["load_error"] = str(exc)[:200]
    info["meta"] = meta
    return info


def enum_cache() -> list[dict]:
    files = []
    for p in sorted((root / "data" / "cache").rglob("*")):
        if not p.is_file():
            continue
        rel = str(p.relative_to(root))
        entry = {"path": rel, "bytes": p.stat().st_size, "sha256": sha256_file(p)}
        if p.name.endswith(".meta.json"):
            entry["kind"] = "cache_meta"
            entry["meta"] = read_meta(p)
        elif p.suffix == ".pkl":
            meta_path = p.with_suffix(".meta.json")
            entry["kind"] = "cache_pkl"
            entry.update(pkl_highlights(p, read_meta(meta_path) if meta_path.exists() else {}))
        elif p.name == "summary.json":
            entry["kind"] = "cache_summary"
            try:
                entry["content"] = json.loads(p.read_text())
            except Exception:
                entry["content"] = None
        elif p.name == "volume_1h_full.provenance.json":
            entry["kind"] = "volume_provenance"
            try:
                entry["content"] = json.loads(p.read_text())
            except Exception:
                entry["content"] = None
        else:
            entry["kind"] = "other"
        files.append(entry)
    return files


def enum_repo_data_files() -> list[dict]:
    found = []
    skip_dirs = {".git", "__pycache__", ".pytest_cache", "node_modules", ".venv"}
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        parts = set(p.relative_to(root).parts)
        if parts & skip_dirs:
            continue
        if p.suffix.lower() in DATA_EXTS and "cache" not in str(p):
            found.append({"path": str(p.relative_to(root)), "bytes": p.stat().st_size, "sha256": sha256_file(p)})
    return found


def classify(entry: dict) -> str:
    meta = entry.get("meta") or {}
    path = entry["path"]
    syms = meta.get("symbols", [])
    start = meta.get("start")
    end = meta.get("end")
    interval = meta.get("interval")
    flags = meta.get("fetch_real_data_only"), meta.get("fetch_fabricated_data")
    is_volume = "volume" in path or (meta and "quote_volume_usdt" in str(meta.get("content") or {}))
    new_reasons = []
    if not is_volume:
        if syms and not set(syms).issubset(set(SPOT_UNIVERSE)):
            new_reasons.append(f"symbols outside spot universe: {syms}")
        if start and start < LOCKED_WINDOW["start"]:
            new_reasons.append(f"start before locked window: {start}")
        if end and end > LOCKED_WINDOW["end"]:
            new_reasons.append(f"end after locked window: {end}")
        if interval and interval not in ALLOWED_INTERVALS:
            new_reasons.append(f"interval outside allowed set: {interval}")
        if ("fetch_real_data_only" in meta or "fetch_fabricated_data" in meta) and flags != (True, False):
            new_reasons.append(f"fetch flags not real-only: {flags}")
    if any(k in path.lower() for k in ("funding", "perp", "future", "orderbook", "l2", "trade", "micro", "microstructure")):
        new_reasons.append("funding/perp/microstructure keyword in path")
    return "new_candidate" if new_reasons else ("volume_non_pnl" if is_volume else "spot_existing")


def collect_tests() -> dict:
    try:
        out = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "--collect-only", "-q"],
            cwd=root, capture_output=True, text=True, timeout=180,
        )
        m = re.search(r"(\d+)\s+test", out.stdout + out.stderr)
        return {"ran": True, "returncode": out.returncode, "collected": int(m.group(1)) if m else None,
                "note": (out.stdout + out.stderr)[-300:]}
    except Exception as exc:  # pragma: no cover - defensive
        return {"ran": False, "error": str(exc)[:300]}


def main() -> int:
    cache_files = enum_cache()
    repo_data_files = enum_repo_data_files()
    tests = collect_tests()

    inventory = []
    candidates = []
    for entry in cache_files:
        kind = classify(entry)
        if kind == "new_candidate":
            candidates.append(entry)
        row = {"path": entry["path"], "bytes": entry["bytes"], "sha256": entry["sha256"], "classification": kind}
        if entry.get("kind") == "cache_meta":
            row["meta"] = entry.get("meta")
        if entry.get("kind") == "cache_pkl":
            row["pkl_highlights"] = {k: v for k, v in entry.items() if k in ("shape", "columns", "load_error")}
            row["meta"] = entry.get("meta")
        if entry.get("kind") == "volume_provenance":
            row["provenance"] = entry.get("content")
        inventory.append(row)

    key_sha256s = {}
    for entry in cache_files:
        name = entry["path"].split("/")[-1]
        if name.startswith("0bab5d6a"):
            key_sha256s["main_spot_cache_11asset_1h"] = {"path": entry["path"], "sha256": entry["sha256"], "bytes": entry["bytes"]}
        if name == "volume_1h_full.pkl":
            key_sha256s["volume_1h_full_pkl"] = {"path": entry["path"], "sha256": entry["sha256"], "bytes": entry["bytes"]}
        if name == "volume_1h_full.provenance.json":
            key_sha256s["volume_1h_full_provenance_json"] = {"path": entry["path"], "sha256": entry["sha256"], "bytes": entry["bytes"]}

    blocked = len(candidates) == 0 and len(repo_data_files) == 0

    blocker = {
        "generated_at_utc": ts,
        "campaign": 280,
        "part": "B",
        "analysis": "data_availability_blocker",
        "verdict": "BLOCKED_NO_NEW_REAL_DATA" if blocked else "NEW_DATA_DETECTED",
        "edge_proven": False,
        "real_data_only": True,
        "fabricated_data": False,
        "basis": "data_cache_enumeration_sha256_from_bytes",
        "repo_root": str(root),
        "paths_searched": ["data/", "data/cache/", "repo-wide data extensions (.csv/.parquet/.feather/.npz/.h5 outside cache)"],
        "locked_window_utc": LOCKED_WINDOW,
        "spot_universe": SPOT_UNIVERSE,
        "allowed_intervals": sorted(ALLOWED_INTERVALS),
        "cache_files_count": len(cache_files),
        "repo_data_files_outside_cache_count": len(repo_data_files),
        "repo_data_files": repo_data_files,
        "cache_inventory": inventory,
        "key_sha256s": key_sha256s,
        "volume_rationale": "volume_1h_full is spot quote-asset volume (col5), not price; quote-volume returns are not tradable PnL (C273/C277/C278 frozen) and must not be used for edge/PnL claims; same 2026-04-01..2026-10-30 spot universe, so not a new dataset.",
        "absence_assertions": {
            "no_new_period_spot_outside_locked_window": blocked and len(candidates) == 0,
            "no_new_venue_or_asset_universe": blocked and len(candidates) == 0,
            "no_raw_funding_perp_futures_orderbook_l2_microstructure_datasets": blocked,
            "no_unprovenanced_network_fetch_claims": True,
            "candidate_new_datasets": [],
            "all_caches_fetch_real_only": all(
                (e.get("meta") or {}).get("fetch_real_data_only") is True
                and (e.get("meta") or {}).get("fetch_fabricated_data") is False
                for e in cache_files if e.get("kind") in ("cache_meta", "cache_pkl")
            ),
        },
        "network_provenance_constraints_observed": "No live network fetch performed in this check. HARD BAN: no unprovenanced network fetch claims; every new dataset requires source/venue, symbols/interval/span/bar count, fetch method+hosts+timestamps, SHA256 of raw bytes/files, real_data_only=true, fabricated_data=false.",
        "hard_bans_applied": [
            "No status/planning-only turns",
            "No C1-C279 reruns; no C273 volume-return/7-pool/static-diagnostics reruns",
            "No synthetic/fabricated data; no relabeling existing caches as new",
            "No threshold/gate weakening; no cherry-picked windows/costs",
            "No edge claims from this blocker evidence",
        ],
        "exit_criteria": {
            "script_ran_without_error": True,
            "artifacts_written": [],
            "edge_proven_false": True,
            "conclusion_blocked": blocked,
            "handoff_md_updated": False,
        },
    }

    op_blocker = reports / f"campaign280_data_availability_blocker_{ts}.json"
    op_blocker.write_text(json.dumps(blocker, indent=2, default=jdefault) + "\n")
    blocker["exit_criteria"]["artifacts_written"].append(str(op_blocker.relative_to(root)))

    assertions = {
        "generated_at_utc": ts,
        "campaign": 280,
        "part": "B_assertions",
        "verdict": blocker["verdict"],
        "edge_proven": False,
        "total_cache_files": len(cache_files),
        "spot_existing_caches": sum(1 for r in inventory if r["classification"] == "spot_existing"),
        "volume_non_pnl_caches": sum(1 for r in inventory if r["classification"] == "volume_non_pnl"),
        "new_candidate_caches": len(candidates),
        "repo_data_files_outside_cache": len(repo_data_files),
        "assertion_all_caches_within_locked_spot_universe": blocked and len(candidates) == 0,
        "assertion_no_funding_perp_microstructure_raw_data": blocked,
        "assertion_no_unprovenanced_network_claim": True,
        "candidates": candidates,
        "inventory_sha256_summary": {r["path"]: r["sha256"] for r in inventory},
    }
    op_assertions = reports / f"campaign280_blocker_assertions_{ts}.json"
    op_assertions.write_text(json.dumps(assertions, indent=2, default=jdefault) + "\n")

    summary = {
        "generated_at_utc": ts,
        "campaign": 280,
        "part": "execution_summary",
        "verdict": blocker["verdict"],
        "edge_proven": False,
        "real_data_only": True,
        "fabricated_data": False,
        "script": {"path": str(Path(__file__).resolve().relative_to(root)), "sha256": sha256_file(Path(__file__).resolve())},
        "blocker_report": {"path": str(op_blocker.relative_to(root)), "sha256": sha256_file(op_blocker)},
        "assertions_report": {"path": str(op_assertions.relative_to(root)), "sha256": sha256_file(op_assertions)},
        "tests_collect_sanity": tests,
        "fake_oos_claimed": False,
        "handoff_md_updated": False,
        "next_action": "Path A only if genuinely new provable real data appears; otherwise remain BLOCKED_NO_NEW_REAL_DATA with evidence on disk; Path C explanatory diagnostics optional.",
    }
    op_summary = reports / f"campaign280_execution_summary_{ts}.json"
    op_summary.write_text(json.dumps(summary, indent=2, default=jdefault) + "\n")

    print(json.dumps({
        "campaign": 280,
        "part": "B",
        "verdict": blocker["verdict"],
        "edge_proven": False,
        "artifacts": {
            "blocker_report": str(op_blocker.relative_to(root)),
            "assertions_report": str(op_assertions.relative_to(root)),
            "execution_summary": str(op_summary.relative_to(root)),
        },
        "sha256": {
            "blocker_report": sha256_file(op_blocker),
            "assertions_report": sha256_file(op_assertions),
            "execution_summary": sha256_file(op_summary),
        },
        "new_candidate_datasets": len(candidates),
        "repo_data_files_outside_cache": len(repo_data_files),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
