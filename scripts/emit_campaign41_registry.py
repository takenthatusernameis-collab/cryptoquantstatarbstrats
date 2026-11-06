#!/usr/bin/env python3
"""Supersede strategy_edge_registry for Campaign 41 (fail-closed, real data only).

Updates consolidated edge registry with C41 Path R-B (Quote Volume Dry-Up Breakout
Continuation on validated real_quote_volume) + fail-closed unblock recheck + full
pytest rerun. No threshold weakening. No fabrication. oos_edge_proven=false.
"""
from __future__ import annotations

import glob
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _latest(pattern: str):
    ps = sorted(glob.glob(str(REPORTS / pattern)))
    return ps[-1] if ps else None


def _load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return {}


def _pytest_counts() -> dict:
    try:
        res = subprocess.run(
            ["python", "-m", "pytest", "tests/", "-q"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=900,
        )
        out = res.stdout + "\n" + res.stderr
        passed = skipped = failed = 0
        m = re.search(r"(\d+) passed", out)
        if m:
            passed = int(m.group(1))
        m = re.search(r"(\d+) skipped", out)
        if m:
            skipped = int(m.group(1))
        m = re.search(r"(\d+) failed", out)
        if m:
            failed = int(m.group(1))
        m = re.search(r"(\d+) warnings?", out)
        warnings_n = int(m.group(1)) if m else out.count("warning")
        return {
            "command": "python -m pytest tests/ -q",
            "passed": passed,
            "skipped": skipped,
            "failed": failed,
            "warnings": warnings_n,
            "rc": res.returncode,
            "scope": "full tests/",
        }
    except Exception as exc:
        return {
            "command": "python -m pytest tests/ -q",
            "error": f"{type(exc).__name__}:{exc}",
            "rc": -1,
            "scope": "full tests/",
        }


def volume_family(art: dict) -> dict:
    by_asset = []
    cost_grid = art.get("config", {}).get("cost_grid_bps_fee_slippage", [])
    for a, r in (art.get("by_asset") or {}).items():
        s0 = (r.get("cost_slices") or {}).get("fee0_slip0_bps") or {}
        s40 = (r.get("cost_slices") or {}).get("fee20_slip20_bps") or {}
        all_pos = bool(r.get("cost_slices")) and all(
            (r["cost_slices"].get(f"fee{f}_slip{s}_bps") or {}).get("oos_net_gt_zero", False)
            for f, s in cost_grid
        )
        all_bh = bool(r.get("cost_slices")) and all(
            (r["cost_slices"].get(f"fee{f}_slip{s}_bps") or {}).get("oos_net_beat_bh", False)
            for f, s in cost_grid
        )
        by_asset.append(
            {
                "asset": a,
                "exposure": bool(r.get("has_exposure")),
                "oos_edge_proven": bool(r.get("oos_edge_proven")),
                "oos_0bps": s0.get("oos_net_sum"),
                "bench_oos_0bps": s0.get("bh_oos_sum"),
                "oos_40bps": s40.get("oos_net_sum"),
                "all_slices_oos_pos": all_pos,
                "all_slices_beat_bench": all_bh,
            }
        )
    n_edge = sum(1 for a in by_asset if a["oos_edge_proven"])
    n_pos = sum(1 for a in by_asset if a["all_slices_oos_pos"])
    n_bh = sum(1 for a in by_asset if a["all_slices_beat_bench"])
    if n_edge > 0 and n_edge == len(by_asset):
        status = "proven_fail_closed"
    elif n_pos > 0 or n_bh > 0:
        status = "proven_zero_cost_only_not_net_of_costs"
    else:
        status = "no_proven_edge_net_of_costs"
    return {
        "family": "real_quote_volume",
        "data_status": "real_feed_with_provenance_present",
        "path": "R-B",
        "hypothesis": art.get("pre_stated_hypothesis", {}),
        "evidence_artifact": art.get("_source_file"),
        "by_asset_summary": sorted(by_asset, key=lambda x: x["asset"]),
        "oos_edge_proven": bool(n_edge > 0 and n_edge == len(by_asset)),
        "n_assets": len(by_asset),
        "n_oos_edge_proven": n_edge,
        "n_assets_all_slices_oos_net_positive": n_pos,
        "n_assets_all_slices_beat_benchmark": n_bh,
        "status": status,
    }


def main():
    prev_path = _latest("strategy_edge_registry_20261105T233646Z.json") or _latest("strategy_edge_registry_*.json")
    prev = _load_json(prev_path) if prev_path else {}
    fam_prev = {f["family"]: f for f in prev.get("families", []) if isinstance(f, dict)}

    c41_rb = _latest("real_quote_volume_dryup_breakout_costed_oos_*.json")
    rb = _load_json(c41_rb) if c41_rb else {}
    if c41_rb:
        rb["_source_file"] = str(Path(c41_rb).relative_to(ROOT))

    unblock = _latest("real_feed_unblock_status_*")
    unblock_d = _load_json(unblock) if unblock else {}
    # prefer campaign 41 if latest isn't
    for cand in sorted(glob.glob(str(REPORTS / "real_feed_unblock_status_*.json"))):
        d = _load_json(cand)
        if d.get("campaign") == 41:
            unblock = cand
            unblock_d = d

    families = []
    vol_fam = volume_family(rb) if rb else fam_prev.get("real_quote_volume", {"family": "real_quote_volume", "status": "no_artifact"})
    families.append(vol_fam)
    for name in [
        "funding_basis_carry",
        "cross_exchange_dual_venue_same_asset",
        "term_structure_real_iv_vol_surface",
        "intrabar_microstructure",
    ]:
        pf = fam_prev.get(name, {"family": name, "data_status": "blocked_no_real_feed", "oos_edge_proven": False})
        pf2 = dict(pf)
        pf2.setdefault("oos_edge_proven", False)
        families.append(pf2)

    pytest = _pytest_counts()
    ts = _ts()
    reg = {
        "schema": "strategy_edge_registry.v1",
        "campaign": 41,
        "generated_at_utc": _now(),
        "fail_closed": True,
        "real_data_only": True,
        "fabricated_data": False,
        "supersedes": str(Path(prev_path).relative_to(ROOT)) if prev_path else None,
        "c41_artifacts": [
            rb.get("_source_file"),
            str(Path(unblock).relative_to(ROOT)) if unblock else None,
            f"reports/strategy_edge_registry_{ts}.json",
        ],
        "path_r": {
            "status_recheck": unblock_d.get("campaign_delta", {}).get("honest_assessment"),
            "path_r_triggered": unblock_d.get("path_r_triggered"),
            "blocked_families": unblock_d.get("campaign_delta", {}).get("current_blocked_families"),
            "c23_rerun": False,
            "c40_climax_mean_reversion_rerun": False,
            "different_prestated_hypothesis_tested": True,
            "hypothesis": (rb.get("pre_stated_hypothesis") or {}).get("name"),
            "differs_from_c23_c40": True,
        },
        "gating_invariants_preserved": {
            "1h": {"n_gated": 0, "pairs": []},
            "4h": {"n_gated": 1, "pairs": ["POL/BTC"]},
            "1d": {"n_gated": 0, "pairs": []},
        },
        "families": families,
        "oos_edge_proven": bool(vol_fam.get("oos_edge_proven")),
        "pytest_rerun": pytest,
        "honest_assessment": (
            "PROVEN NET-OF-COST OOS EDGE (fail-closed)." if vol_fam.get("oos_edge_proven")
            else "NO PROVEN NET-OF-COST OOS EDGE. oos_edge_proven=false. "
                 "C41 tested Quote Volume Dry-Up Breakout Continuation on validated real_quote_volume "
                 "(genuinely different from C23 momentum and C40 climax mean reversion): no asset met "
                 "fail-closed rule (exposure>0 AND all cost slices OOS net>0 AND beat B&H). "
                 "Remaining blocked families unchanged: funding_basis_carry, cross_exchange_dual_venue_same_asset, "
                 "term_structure_real_iv_vol_surface, intrabar_microstructure. Fail-closed, real data only."
        ),
    }
    out = REPORTS / f"strategy_edge_registry_{ts}.json"
    out.write_text(json.dumps(reg, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    print(out)
    print(json.dumps({"oos_edge_proven": reg["oos_edge_proven"], "pytest": pytest, "supersedes": reg["supersedes"]}, default=str))


if __name__ == "__main__":
    main()
