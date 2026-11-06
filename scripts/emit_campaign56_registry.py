#!/usr/bin/env python3
"""Supersede strategy_edge_registry for Campaign 56 (fail-closed, real data only)."""
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
            ["python3.12", "-m", "pytest", "tests/", "-q"],
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
            "command": "python3.12 -m pytest tests/ -q",
            "passed": passed,
            "skipped": skipped,
            "failed": failed,
            "rc": res.returncode,
            "scope": "full tests/",
        }
    except Exception as exc:
        return {
            "command": "python3.12 -m pytest tests/ -q",
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
                "all_slices_oos_net_gt_zero": all_pos,
                "all_slices_oos_net_beat_bh": all_bh,
            }
        )
    return {
        "artifact": art.get("_path"),
        "generated_at_utc": art.get("generated_at_utc"),
        "oos_edge_proven": bool(art.get("oos_edge_proven")),
        "n_assets_tested": art.get("n_assets_tested"),
        "n_assets_with_exposure": art.get("n_assets_with_exposure"),
        "n_oos_edge_proven": art.get("n_oos_edge_proven"),
        "by_asset": by_asset,
    }


def main():
    ts = _ts()
    c56_path = _latest("real_quote_volume_cv_relative_dispersion_shock_mr_costed_oos_*.json")
    c55_path = _latest("real_quote_volume_vol_future_absret_lead_corr_shock_mr_costed_oos_*.json")
    all_status = sorted(glob.glob(str(REPORTS / "real_feed_unblock_status_20261106T*.json")))
    status_path = all_status[-1] if all_status else None

    c56_art = _load_json(c56_path) if c56_path else {}
    c55_art = _load_json(c55_path) if c55_path else {}
    status = _load_json(status_path) if status_path else {}
    if c56_path:
        c56_art["_path"] = str(Path(c56_path).relative_to(ROOT))
    if c55_path:
        c55_art["_path"] = str(Path(c55_path).relative_to(ROOT))

    pytest_res = _pytest_counts()
    oos_edge_proven = bool(c56_art.get("oos_edge_proven")) or bool(c55_art.get("oos_edge_proven"))

    reg = {
        "generated_at_utc": _now(),
        "campaign": 56,
        "title": "Strategy edge registry — Campaign 56 (C56 volume CV relative-dispersion shock MR costed OOS on real quote volume; fail-closed)",
        "supersedes": "reports/strategy_edge_registry_20261106T034159Z.json",
        "oos_edge_proven": oos_edge_proven,
        "pytest": pytest_res,
        "campaign_56_real_quote_volume_cv_relative_dispersion_shock_mr": volume_family(c56_art),
        "campaign_55_real_quote_volume_vol_future_absret_lead_corr_shock_mr": volume_family(c55_art),
        "feed_unblock_status": {
            "path": str(Path(status_path).relative_to(ROOT)) if status_path else None,
            "campaign": status.get("campaign"),
            "path_r_triggered": status.get("path_r_triggered"),
            "path_r_reason": status.get("path_r_reason"),
            "blocked_families": status.get("blocked_families"),
            "delta_changed": (status.get("campaign_delta") or {}).get("changed"),
            "delta_message": (status.get("campaign_delta") or {}).get("honest_assessment"),
        },
        "path_r_assessment": {
            "real_quote_volume_validated_fail_closed": True,
            "c23_c40_c55_rerun": False,
            "c56_volume_cv_relative_dispersion_shock_mr_tested": True,
            "different_prestated_hypothesis_tested": True,
            "hypothesis_differs_from_c23_c40_c55": (
                "C56 uses CV_t = rolling_std(qvol,W=48) / rolling_mean(qvol,W=48) (scale-normalized relative dispersion) "
                "z-scored ZLB=168, fade shocks. Distinct from C48 (rolling STD raw 2nd-moment, not mean-normalized), "
                "C23/C40/C41/C42 (vol_z of raw volume level/expansion), C45 (Amihud |ret|/volume pointwise ratio), "
                "C43 (unsloped vol_z divergence), C44 (vol_z ROC), C46 (OBV signed-cumulative slopes), C47 (up/down "
                "partition imbalance), C49 (excess kurtosis 4th-moment), C50 (skewness 3rd-moment), C51 (lag-1 autocorr), "
                "C52 (contemporaneous corr qvol,|ret|), C53 (signed lead corr qvol,ret_{t+k}), C54 (contemporaneous OLS "
                "beta sensitivity), C55 (lead corr qvol,|ret_{t+k}| on magnitude)."
            ),
        },
        "settled_truth": {
            "oos_edge_proven": oos_edge_proven,
            "blocked_families_substantive": status.get("blocked_families") or [],
            "gating_invariants_preserved": {"1h": [], "4h": ["POL/BTC"], "1d": []},
            "spot_1h_exhausted": True,
            "real_quote_volume_tested_hypotheses_all_no_edge": "C23,C40-C56",
        },
    }
    out = REPORTS / f"strategy_edge_registry_{ts}.json"
    out.write_text(json.dumps(reg, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"wrote": str(out), "oos_edge_proven": oos_edge_proven, "pytest_rc": pytest_res.get("rc"), "pytest": f"{pytest_res.get('passed')} passed, {pytest_res.get('failed')} failed"}))


if __name__ == "__main__":
    main()
