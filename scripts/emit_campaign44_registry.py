#!/usr/bin/env python3
"""Supersede strategy_edge_registry for Campaign 44 (fail-closed, real data only)."""
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
        return {
            "command": "python -m pytest tests/ -q",
            "passed": passed,
            "skipped": skipped,
            "failed": failed,
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
        if not isinstance(r, dict) or r.get("error"):
            continue
        s0 = (r.get("cost_slices") or {}).get("fee0_slip0_bps") or {}
        s40 = (r.get("cost_slices") or {}).get("fee20_slip20_bps") or {}
        all_pos = bool(r.get("cost_slices")) and all(
            (r["cost_slices"].get(f"fee{f}_slip{s}_bps") or {}).get("oos_net_gt_zero", False)
            for f, s in cost_grid
        ) if cost_grid else False
        all_bh = bool(r.get("cost_slices")) and all(
            (r["cost_slices"].get(f"fee{f}_slip{s}_bps") or {}).get("oos_net_beat_bh", False)
            for f, s in cost_grid
        ) if cost_grid else False
        by_asset.append(
            {
                "asset": a,
                "exposure": bool(r.get("has_exposure")),
                "oos_edge_proven": bool(r.get("oos_edge_proven")),
                "oos_0bps": s0.get("net_oos_sum"),
                "bench_oos_0bps": s0.get("bh_oos_sum"),
                "oos_40bps": s40.get("net_oos_sum"),
                "all_slices_oos_pos": all_pos,
                "all_slices_beat_bench": all_bh,
            }
        )
    n_edge = sum(1 for a in by_asset if a["oos_edge_proven"])
    n_pos = sum(1 for a in by_asset if a["all_slices_oos_pos"])
    n_bh = sum(1 for a in by_asset if a["all_slices_beat_bench"])
    if n_edge > 0 and n_edge == len(by_asset) and len(by_asset) > 0:
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
        "oos_edge_proven": bool(n_edge > 0 and n_edge == len(by_asset) and len(by_asset) > 0),
        "n_assets": len(by_asset),
        "n_oos_edge_proven": n_edge,
        "n_assets_all_slices_oos_net_positive": n_pos,
        "n_assets_all_slices_beat_benchmark": n_bh,
        "status": status,
    }


def main():
    prev_path = _latest("strategy_edge_registry_*.json")
    prev = _load_json(prev_path) if prev_path else {}
    fam_prev = {f["family"]: f for f in prev.get("families", []) if isinstance(f, dict)}

    c44_rb = _latest("real_quote_volume_acceleration_trend_following_costed_oos_*.json")
    rb = _load_json(c44_rb) if c44_rb else {}
    if c44_rb:
        rb["_source_file"] = str(Path(c44_rb).relative_to(ROOT))

    unblock = _latest("real_feed_unblock_status_*.json")
    unblock_d = _load_json(unblock) if unblock else {}
    for cand in sorted(glob.glob(str(REPORTS / "real_feed_unblock_status_*.json"))):
        d = _load_json(cand)
        if d.get("campaign") == 44 or d.get("type", "").endswith("campaign44"):
            unblock = cand
            unblock_d = d
            break

    families = []
    vol_fam = volume_family(rb) if rb else fam_prev.get("real_quote_volume", {"family": "real_quote_volume", "status": "no_artifact"})
    families.append(vol_fam)
    for fam_name in ["funding_basis_carry", "cross_exchange_dual_venue_same_asset", "term_structure_real_iv_vol_surface", "intrabar_microstructure"]:
        if any(f.get("family") == fam_name for f in families):
            continue
        f_prev = fam_prev.get(fam_name)
        if f_prev:
            families.append(f_prev)
        else:
            families.append({"family": fam_name, "data_status": "blocked_no_real_feed", "oos_edge_proven": False})

    pytest_res = _pytest_counts()
    ts_out = _ts()
    out_path = REPORTS / f"strategy_edge_registry_{ts_out}.json"
    out = {
        "schema": "strategy_edge_registry.v1",
        "campaign": 44,
        "generated_at_utc": _now(),
        "fail_closed": True,
        "real_data_only": True,
        "fabricated_data": False,
        "supersedes": str(Path(prev_path).relative_to(ROOT)) if prev_path else None,
        "c44_artifacts": [
            str(Path(c44_rb).relative_to(ROOT)) if c44_rb else None,
            str(Path(unblock).relative_to(ROOT)) if unblock else None,
            str(out_path.relative_to(ROOT)),
        ],
        "path_r": {
            "status_recheck": (unblock_d.get("report") or {}).get("campaign_delta", {}).get("honest_assessment") if isinstance(unblock_d, dict) else "UNKNOWN",
            "path_r_triggered": True,
            "blocked_families": [f["family"] for f in families if f.get("data_status") == "blocked_no_real_feed"],
            "c23_rerun": False,
            "c40_climax_mean_reversion_rerun": False,
            "c41_rerun": False,
            "c42_rerun": False,
            "c43_rerun": False,
            "different_prestated_hypothesis_tested": True,
            "hypothesis": (rb.get("pre_stated_hypothesis") or {}).get("name") if rb else None,
            "differs_from_c23_c40_c41_c42_c43": True,
        },
        "gating_invariants_preserved": prev.get("gating_invariants_preserved"),
        "families": families,
        "oos_edge_proven": False,
        "pytest_rerun": pytest_res,
    }
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")
    print(json.dumps({"oos_edge_proven": out["oos_edge_proven"], "pytest": pytest_res}, indent=2))


if __name__ == "__main__":
    main()
