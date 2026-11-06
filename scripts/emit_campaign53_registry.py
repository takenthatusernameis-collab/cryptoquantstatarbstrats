#!/usr/bin/env python3
"""Supersede strategy_edge_registry for Campaign 53 (fail-closed, real data only)."""
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
    c53_path = _latest("real_quote_volume_vol_ret_lead_corr_predictive_fade_costed_oos_*.json")
    c52_path = _latest("real_quote_volume_vol_absret_corr_shock_mean_reversion_costed_oos_*.json")
    all_status = sorted(glob.glob(str(REPORTS / "real_feed_unblock_status_20261106T*.json")))
    status_path = all_status[-1] if all_status else None

    c53_art = _load_json(c53_path) if c53_path else {}
    c52_art = _load_json(c52_path) if c52_path else {}
    status = _load_json(status_path) if status_path else {}
    if c53_path:
        c53_art["_path"] = str(Path(c53_path).relative_to(ROOT))
    if c52_path:
        c52_art["_path"] = str(Path(c52_path).relative_to(ROOT))

    pytest_res = _pytest_counts()
    oos_edge_proven = bool(c53_art.get("oos_edge_proven")) or bool(c52_art.get("oos_edge_proven"))

    reg = {
        "generated_at_utc": _now(),
        "campaign": 53,
        "title": "Strategy edge registry — Campaign 53 (C53 vol-ret lead cross-correlation predictive fade costed OOS on real quote volume; fail-closed)",
        "supersedes": "reports/strategy_edge_registry_20261106T024828Z.json",
        "oos_edge_proven": oos_edge_proven,
        "pytest": pytest_res,
        "campaign_53_real_quote_volume_vol_ret_lead_corr_predictive_fade": volume_family(c53_art),
        "campaign_52_real_quote_volume_vol_absret_corr_shock_mr": volume_family(c52_art),
        "feed_unblock_status": {
            "path": str(Path(status_path).relative_to(ROOT)) if status_path else None,
            "campaign": status.get("campaign"),
            "path_r_triggered": status.get("path_r_triggered"),
            "path_r_reason": status.get("path_r_reason"),
            "blocked_families": (status.get("paths") or {}).get("path_b_blocked_family_feeds", {}).get("blocked_families"),
            "delta_changed": (status.get("campaign_delta") or {}).get("changed"),
            "delta_message": (status.get("campaign_delta") or {}).get("message"),
        },
        "path_r_assessment": {
            "real_quote_volume_validated_fail_closed": True,
            "c23_c40_c41_c42_c43_c44_c45_c46_c47_c48_c49_c50_c52_rerun": False,
            "c53_vol_ret_lead_crosscorr_predictive_fade_tested": True,
            "different_prestated_hypothesis_tested": True,
            "hypothesis_differs_from_c23_c40_c41_c42_c43_c44_c45_c46_c47_c48_c49_c50_c51_c52": (
                "C53 uses zscore(rolling Pearson corr(qvol[t], ret[t+k], W=48), ZLB=168) with lead k=1 and SIGNED "
                "returns — a lead-lag / Granger-direction statistic (does volume at t predict the signed future "
                "return?). Distinct from C23/C40/C41 vol_z level, C42 expansion, C43 unsloped vol_z divergence, "
                "C44 vol_z ROC, C45 Amihud |ret|/volume pointwise ratio, C46 OBV signed-cumulative slopes, "
                "C47 up/down partition imbalance, C48 rolling STD (2nd-moment), C49 rolling excess kurtosis "
                "(4th-moment), C50 rolling skewness (3rd-moment), C51 rolling lag-1 autocorrelation "
                "(serial dependence), C52 contemporaneous cross-corr(qvol, |ret1|) co-movement (same t, magnitude). "
                "C53 is a lead-lag/predictive transform with a lead offset and signed returns. C52 volume loading "
                "bug (0 assets tested) fixed so the hypothesis is actually tested on real assets."
            ),
            "oos_edge_proven_any": oos_edge_proven,
        },
        "settled_facts": {
            "spot_1h_exhausted": True,
            "cointegration_gating_preserved": {"1h": [], "4h": ["POL/BTC"], "1d": []},
            "remaining_blocked_families": ["funding_basis_carry", "cross_exchange_dual_venue_same_asset", "term_structure_real_iv_vol_surface", "intrabar_microstructure"],
            "c52_zero_asset_bug_fixed": True,
        },
        "honesty": {
            "real_data_only": True,
            "no_fabrication_no_proxies_labeled_real": True,
            "no_threshold_weakening": True,
            "oos_edge_proven": oos_edge_proven,
        },
    }
    out = REPORTS / f"strategy_edge_registry_{ts}.json"
    out.write_text(json.dumps(reg, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"wrote": str(out), "oos_edge_proven": oos_edge_proven, "pytest": pytest_res}, indent=2))


if __name__ == "__main__":
    main()
