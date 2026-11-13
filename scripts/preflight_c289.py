#!/usr/bin/env python3
"""C289 preflight: verify the real OOS sweep artifacts that the multiple-testing /
minimum-detectable-edge closure consumes.

C289 is the statistical-closure campaign: it answers whether ANY of the
accumulated costed out-of-sample results is a real edge beyond data-mining, and
what the smallest statistically resolvable edge is versus the 5m cost floor.

Scope (methodologically coherent): the two 5m-executed campaigns on the same
26,208-bar real cache with the same 151 WF splits and the same 5m cost grid —
  - C286 (volume-conditioned cross-sectional stat-arb, 81 runs)
  - C288 (realized-volatility / skewness cross-sectional stat-arb, 81 runs)
C285 (1h execution, 26 splits) and the heterogeneous C281B..C284 sweeps are out of
scope for the unified 5m closure and remain summarized in their own verdicts.

This preflight verifies:
- both source sweep artifacts exist and parse as JSON;
- each contains exactly 81 run records with the shared schema
  (feature/lookback/K/hold + cost_slices[<ck>].oos_net_mean_per_split);
- the 5m cost grid is exactly [[0,0],[5,5],[10,10],[20,20],[40,40]];
- the per-split series length equals each run's n_splits (151 for 5m);
- SHA256-from-bytes of both source artifacts (recorded for provenance).

Exit code 0 iff every check passes; any mismatch/missing file is a fail-closed
blocker.  No data is fetched, imputed, resampled, or fabricated.
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"

COST_GRID = [[0, 0], [5, 5], [10, 10], [20, 20], [40, 40]]
EXPECTED_RUNS_PER_CAMPAIGN = 81
EXPECTED_SPLITS_5M = 151

# Pinned SHA256-from-bytes of the frozen source artifacts used by the closure.
PINNED = {
    "c286_oos_sweep": "c153042e619793de4aaa024b967b387b7a37c26ed6864884d14240ea42f17aca",
    "c288_oos_sweep": "75c06a7ee1ea42155e8c0674d58c70f17175e47e31b750db464815a35bb0188d",
}


def sha256_file(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def latest(pattern: str):
    matches = sorted(glob.glob(str(REPORTS / pattern)))
    return matches[-1] if matches else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.parse_args()

    checks: dict = {}
    blocked: list[str] = []

    sources = {
        "c286_oos_sweep": "campaign286_oos_sweep_*.json",
        "c288_oos_sweep": "campaign288_oos_sweep_*.json",
    }

    parsed: dict[str, dict] = {}
    for key, pattern in sources.items():
        path = latest(pattern)
        entry = {"pattern": pattern, "path": path}
        if path is None:
            entry["ok"] = False
            entry["error"] = "no artifact found"
            checks[key] = entry
            blocked.append(f"{key}: no artifact found")
            continue
        actual = sha256_file(path)
        entry["sha256"] = actual
        entry["pinned_sha256"] = PINNED[key]
        entry["sha_ok"] = actual == PINNED[key]
        if not entry["sha_ok"]:
            blocked.append(f"{key}: sha256 mismatch ({actual} != {PINNED[key]})")
        try:
            payload = json.loads(Path(path).read_text())
            runs = payload.get("results", [])
            schema_ok = all(
                {"feature", "lookback", "K", "hold", "n_splits", "cost_slices"} <= set(r)
                for r in runs
            )
            split_ok = all(
                len(r["cost_slices"][f"fee{f}_slip{s}"]["oos_net_mean_per_split"]) == r["n_splits"]
                for r in runs
                for f, s in COST_GRID
                if f"fee{f}_slip{s}" in r["cost_slices"]
            )
            slices_present = all(
                {f"fee{f}_slip{s}" for f, s in COST_GRID} <= set(r["cost_slices"]) for r in runs
            )
            entry.update({
                "n_results": len(runs),
                "n_splits": sorted({int(r["n_splits"]) for r in runs}),
                "schema_ok": schema_ok,
                "slices_present": slices_present,
                "per_split_length_matches_n_splits": split_ok,
                "ok": (
                    entry["sha_ok"]
                    and len(runs) == EXPECTED_RUNS_PER_CAMPAIGN
                    and schema_ok
                    and slices_present
                    and split_ok
                    and {int(r["n_splits"]) for r in runs} == {EXPECTED_SPLITS_5M}
                ),
            })
            if not entry["ok"]:
                blocked.append(f"{key}: run count/schema/slices/splits check failed")
            parsed[key] = payload
        except Exception as exc:  # noqa: BLE001
            entry["ok"] = False
            entry["error"] = f"{type(exc).__name__}: {exc}"
            checks[key] = entry
            blocked.append(f"{key}: could not be parsed")
            continue
        checks[key] = entry

    total_configs = sum(len(parsed[k]["results"]) for k in parsed) if len(parsed) == 2 else 0
    ready = not blocked and total_configs == 2 * EXPECTED_RUNS_PER_CAMPAIGN
    result = {
        "ready": ready,
        "real_data_only": True,
        "fabricated_data": False,
        "campaign": 289,
        "part": "preflight",
        "scope": "5m-executed campaigns C286 + C288 (162 configs, 151 splits, 5m cost grid)",
        "total_configs": int(total_configs),
        "checks": checks,
        "blocked_reasons": blocked,
    }
    print(json.dumps(result, indent=2, default=str))
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())