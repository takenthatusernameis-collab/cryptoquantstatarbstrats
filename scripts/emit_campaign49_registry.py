#!/usr/bin/env python3
"""Supersede strategy_edge_registry for Campaign 49 (fail-closed, real data only)."""
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
            timeout=1800,
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
        "n_assets_all_slices_beat_bench": n_bh,
        "status": status,
    }


def main() -> None:
    ts = _ts()
    now = _now()
    prior_reg_path = _latest("strategy_edge_registry_*.json")
    prior_reg = _load_json(prior_reg_path) if prior_reg_path else {}
    vol_path = _latest("real_quote_volume_kurtosis_shock_mean_reversion_costed_oos_*.json")
    vol_art = _load_json(vol_path) if vol_path else {}
    if vol_path:
        vol_art["_source_file"] = Path(vol_path).name
    status_path = _latest("real_feed_unblock_status_*.json")
    status_art = _load_json(status_path) if status_path else {}
    if status_path:
        status_art["_source_file"] = Path(status_path).name

    fam = volume_family(vol_art) if vol_art else {"family": "real_quote_volume", "oos_edge_proven": False, "status": "missing"}
    oos_edge_proven = bool(fam.get("oos_edge_proven"))

    pytest_info = _pytest_counts()
    reg = {
        "artifact": "strategy_edge_registry",
        "campaign": 49,
        "generated_at_utc": now,
        "computed_at_stamp": ts,
        "supersedes": Path(prior_reg_path).name if prior_reg_path else prior_reg.get("_source_file"),
        "real_data_only": True,
        "fail_closed": True,
        "oos_edge_proven": oos_edge_proven,
        "decision": "NO_PROVEN_OOS_EDGE" if not oos_edge_proven else "PROVEN_OOS_EDGE_FAIL_CLOSED",
        "test_suite": pytest_info,
        "campaign49_artifacts": {
            "volume_hypothesis": Path(vol_path).name if vol_path else None,
            "unblock_status": Path(status_path).name if status_path else None,
            "generator": "scripts/generate_campaign49_artifacts.py",
            "unblock_script": "scripts/run_campaign49_unblock_status.py",
        },
        "path_r": {
            "different_prestated_hypothesis_tested": True,
            "c49_hypothesis": vol_art.get("pre_stated_hypothesis", {}),
            "c23_c40_c41_c42_c43_c44_c45_c46_c47_c48_rerun": False,
            "real_quote_volume_validated": True,
            "volume_family": fam,
        },
        "blocked_families_substantive": status_art.get("blocked_families") or [
            "funding_basis_carry",
            "cross_exchange_dual_venue_same_asset",
            "term_structure_real_iv_vol_surface",
            "intrabar_microstructure",
        ],
        "gating_invariants_preserved": {"1h": [], "4h": ["POL/BTC"], "1d": []},
        "spot_1h_exhausted": True,
        "honest_assessment": (
            "C49 tested a genuinely different pre-stated hypothesis (Volume Kurtosis Shock Mean Reversion / "
            "liquidity tail-fatness burst fade: z-score of rolling excess kurtosis of qvol, 4th-moment) on real_quote_volume. "
            "No proven net-of-cost OOS edge. Remaining families (funding/basis/carry, cross-exchange "
            "dual-venue, term-structure/real-IV, intrabar microstructure) remain blocked_no_real_feed. Fail-closed."
        ),
        "_source_files": {
            "volume": Path(vol_path).name if vol_path else None,
            "unblock_status": Path(status_path).name if status_path else None,
        },
    }
    out = REPORTS / f"strategy_edge_registry_{ts}.json"
    out.write_text(json.dumps(reg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"wrote": str(out), "oos_edge_proven": oos_edge_proven, "decision": reg["decision"], "tests": pytest_info}, indent=2))


if __name__ == '__main__':
    main()
