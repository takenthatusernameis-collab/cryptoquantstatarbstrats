#!/usr/bin/env python3
"""C277A: price-PnL tradability gate for the frozen C273 volume-RQA feature.

The C273 feature and all walk-forward / cost / max-hold parameters are reused
exactly. The only change is the return basis used for PnL: C273 used log
quote-volume returns; C277A uses real spot log-price returns on the same
aligned timestamps, the same positions, the same WF windows, and the same cost
grid. This decides whether the C273 "edge" is tradable.

Preflight: reproduce the C273 volume-return baseline on one asset (ADA) to
within 1e-9 before running all assets. Fail-closed on any mismatch.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
cache_dir = root / "data" / "cache"
reports = root / "reports"
reports.mkdir(exist_ok=True)

ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

C273_PATH = (
    root
    / "scripts"
    / "run_real_quote_volume_rqa_rte_over_white_diag_line_length_percentile_spread_shock_mr_costed_oos.py"
)
FROZEN_C273_OOS = (
    reports
    / "real_quote_volume_rqa_rte_over_white_diag_line_length_percentile_spread_shock_mr_costed_oos_20261112T050947Z.json"
)

_cache: dict = {}


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_c273_module():
    spec = importlib.util.spec_from_file_location("c273_runner", C273_PATH)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def load_spot(c273):
    return c273.load_spot()


def load_volume(c273):
    return c273.load_volume()


def compute_feature(r_vol: pd.Series, c273) -> pd.Series:
    """Exact C273 feature: WHITE diagonal segment-length percentile spread on
    the delay-embedded log-volume-return recurrence matrix."""
    W_RR = c273.W_RR
    ALB = c273.ALB
    EPS_SCALE = c273.EPS_SCALE
    W_MIN = c273.W_MIN
    feats = []
    for t in range(ALB, len(r_vol)):
        win = r_vol.iloc[t - W_RR : t].to_numpy(dtype=float)
        if win.size != W_RR or not np.all(np.isfinite(win)):
            feats.append(np.nan)
            continue
        std_w = float(np.std(win))
        if not np.isfinite(std_w) or std_w <= 0:
            feats.append(np.nan)
            continue
        X = np.column_stack([win[:-1], win[1:]])
        eps = EPS_SCALE * std_w
        # chebyshev == L_inf; identical to np.max(abs(diff)) but faster.
        from scipy.spatial.distance import cdist

        d = cdist(X, X, metric="chebyshev")
        R = (d <= eps + 1e-18).astype(float)
        feats.append(c273._white_diag_line_length_percentile_spread(R, W_MIN))
    feat = pd.Series(feats, index=r_vol.index[ALB : ALB + len(feats)])
    return feat.replace([np.inf, -np.inf], np.nan)


def build_positions(feat: pd.Series, rets_index: pd.Index, c273) -> pd.Series:
    """Exact C273 WF z-score positions with max-hold carry."""
    TRAIN = c273.TRAIN
    TEST = c273.TEST
    STEP = c273.STEP
    ENTRY_Z = c273.ENTRY_Z
    EXIT_Z = c273.EXIT_Z
    MAX_HOLD = c273.MAX_HOLD

    pos = pd.Series(0.0, index=feat.index)
    splits = c273.wf_splits(len(feat), TRAIN, TEST, STEP)
    for (s0, tr_e, te_e) in splits:
        f_tr = feat.iloc[s0:tr_e]
        f_te = feat.iloc[tr_e:te_e]
        f_tr_c = f_tr.dropna()
        if f_tr_c.shape[0] < 50:
            continue
        mu = float(f_tr_c.mean())
        sig = float(f_tr_c.std(ddof=0))
        if not np.isfinite(sig) or sig <= 0:
            continue
        z = (f_te - mu) / sig
        zc = z.dropna()
        for ti in zc.index:
            zz = float(zc.at[ti])
            if zz > ENTRY_Z:
                pos.at[ti] = -1.0
            elif zz < -ENTRY_Z:
                pos.at[ti] = 1.0
            else:
                pos.at[ti] = 0.0
    arr_pos = pos.to_numpy(dtype=float).copy()
    i = 1
    while i < len(arr_pos):
        if arr_pos[i - 1] != 0 and arr_pos[i] == 0:
            carry = arr_pos[i - 1]
            j = i
            held = 0
            while j < len(arr_pos) and arr_pos[j] == 0 and held < MAX_HOLD:
                arr_pos[j] = carry
                j += 1
                held += 1
            i = j
        else:
            i += 1
    pos = pd.Series(arr_pos, index=feat.index)
    return pos


def evaluate(pos: pd.Series, rets: pd.Series, splits, c273) -> dict:
    """Exact C273 PnL / cost / B&H evaluation, on the supplied return series."""
    COST_GRID = c273.COST_GRID
    npn = rets.to_numpy(dtype=float)
    ppn = pos.to_numpy(dtype=float)
    bh = npn.copy()

    oos_mask_all = np.zeros(len(npn), dtype=bool)
    for (_s0, tr_e, te_e) in splits:
        oos_mask_all[tr_e:te_e] = True

    per_cost = {}
    gross_oos = float((ppn * npn)[oos_mask_all].sum()) if oos_mask_all.any() else float("nan")
    for fee, slp in COST_GRID:
        tc = (fee + slp) / 10000.0
        trades = np.abs(np.diff(np.concatenate([[0.0], ppn])))
        strat = ppn * npn - trades * tc
        oos_strat = []
        oos_bh = []
        oos_trades = []
        for (_s0, tr_s, te_e) in splits:
            oos_strat.extend(strat[tr_s:te_e].tolist())
            oos_bh.extend(bh[tr_s:te_e].tolist())
            oos_trades.extend(trades[tr_s:te_e].tolist())
        oos_np = np.array(oos_strat, dtype=float)
        oos_bh_a = np.array(oos_bh, dtype=float)
        oos_tr_a = np.array(oos_trades, dtype=float)
        exp = float((np.abs(pos.shift(1).fillna(0.0)) > 0).sum())
        per_cost[f"fee{fee}_slip{slp}"] = {
            "oos_net_sum": float(oos_np.sum()),
            "oos_net_mean": float(oos_np.mean()) if oos_np.size else np.nan,
            "bh_oos_net_mean": float(oos_bh_a.mean()) if oos_bh_a.size else np.nan,
            "oos_n": int(oos_np.size),
            "exposure_bars": exp,
            "oos_turnover_sum": float(oos_tr_a.sum()),
            "oos_turnover_per_bar": float(oos_tr_a.mean()) if oos_tr_a.size else np.nan,
        }
    turnover_sum = float(
        np.abs(np.diff(np.concatenate([[0.0], ppn])))[oos_mask_all].sum()
    )
    breakeven_tc = (gross_oos / turnover_sum) if turnover_sum > 0 else float("nan")
    return {
        "per_cost": per_cost,
        "gross_oos_sum": gross_oos,
        "oos_turnover_sum": turnover_sum,
        "breakeven_total_cost_bps": float(breakeven_tc * 10000.0) if np.isfinite(breakeven_tc) else None,
        "bh_oos_net_mean": float(bh[oos_mask_all].mean()) if oos_mask_all.any() else np.nan,
    }


def prepare_asset(sym, spot_df, vol_df, c273):
    sp = spot_df[sym].dropna()
    vv = vol_df[sym].dropna()
    idx = sp.index.intersection(vv.index)
    sp = sp.loc[idx]
    vv = vv.loc[idx]
    r_vol = np.log(vv).diff().dropna()
    r_price = np.log(sp).diff().dropna()
    return sp, vv, r_vol, r_price


def main() -> None:
    c273 = load_c273_module()
    spot_df, spot_meta, spot_sha = load_spot(c273)
    vol_df, vol_report = load_volume(c273)

    common = sorted(set(spot_df.columns).intersection(set(vol_df.columns)))
    if len(common) == 0:
        raise SystemExit("NO_COMMON_ASSETS")

    TRAIN, TEST, STEP = c273.TRAIN, c273.TEST, c273.STEP
    per_asset = {}
    strat_means_price = []
    bh_means_price = []
    strat_means_vol = []
    bh_means_vol = []
    any_exposure = False

    # Preflight: ADA volume-return reproduction vs frozen C273 artifact.
    if "ADA" not in common:
        raise SystemExit("PREFLIGHT_ASSET_MISSING: ADA")
    sp, vv, r_vol, r_price = prepare_asset("ADA", spot_df, vol_df, c273)
    if len(r_vol) < c273.ALB + TRAIN + TEST + 50:
        raise SystemExit("PREFLIGHT_INSUFFICIENT_BARS")
    feat = compute_feature(r_vol, c273)
    rets_vol = r_vol.loc[feat.index].shift(-1).dropna()
    feat = feat.loc[rets_vol.index]
    pos = build_positions(feat, rets_vol.index, c273)
    splits = c273.wf_splits(len(feat), TRAIN, TEST, STEP)
    vol_eval = evaluate(pos, rets_vol, splits, c273)
    frozen = json.loads(FROZEN_C273_OOS.read_text())
    frozen_ada = frozen["per_asset"]["ADA"]["per_cost"]
    max_diff = 0.0
    for k, v in frozen_ada.items():
        got = vol_eval["per_cost"][k]["oos_net_sum"]
        max_diff = max(max_diff, abs(got - v["oos_net_sum"]))
    if max_diff > 1e-9:
        raise SystemExit(
            f"PREFLIGHT_FAIL: ADA volume-return mismatch max_abs_diff={max_diff:.3e} (>1e-9)"
        )
    preflight = {
        "asset": "ADA",
        "max_abs_diff_vs_frozen_c273": max_diff,
        "tolerance": 1e-9,
        "status": "PASS",
    }

    # Full run: feature identical (volume-driven); PnL on spot price returns.
    for sym in common:
        sp, vv, r_vol, r_price = prepare_asset(sym, spot_df, vol_df, c273)
        if len(r_vol) < c273.ALB + TRAIN + TEST + 50:
            per_asset[sym] = {"status": "insufficient"}
            continue
        feat = compute_feature(r_vol, c273)
        rets_vol = r_vol.loc[feat.index].shift(-1).dropna()
        feat = feat.loc[rets_vol.index]
        if feat.dropna().shape[0] < TRAIN + TEST + 10:
            per_asset[sym] = {"status": "feature_insufficient"}
            continue
        rets_price = r_price.loc[feat.index].shift(-1).dropna()
        feat = feat.loc[rets_price.index]
        pos = build_positions(feat, rets_price.index, c273)
        splits = c273.wf_splits(len(feat), TRAIN, TEST, STEP)
        if len(splits) == 0:
            per_asset[sym] = {"status": "no_splits"}
            continue
        price_eval = evaluate(pos, rets_price, splits, c273)
        vol_eval = evaluate(pos, rets_vol.loc[feat.index], splits, c273)
        exp = price_eval["per_cost"]["fee0_slip0"]["exposure_bars"]
        if exp > 0:
            any_exposure = True
        per_asset[sym] = {
            "status": "ok",
            "bars": int(len(sp)),
            "ratio_finite_bars": int(np.isfinite(feat.to_numpy()).sum()),
            "price_pnl": price_eval,
            "volume_return_pnl": vol_eval,
        }
        oos_mask = np.zeros(len(feat), dtype=bool)
        for (_s0, tr_e, te_e) in splits:
            oos_mask[tr_e:te_e] = True
        strat_means_price.append(
            float((pos.to_numpy(dtype=float) * rets_price.to_numpy(dtype=float))[oos_mask].mean())
            if oos_mask.any()
            else np.nan
        )
        bh_means_price.append(
            float(rets_price.to_numpy(dtype=float)[oos_mask].mean()) if oos_mask.any() else np.nan
        )
        strat_means_vol.append(
            float((pos.to_numpy(dtype=float) * rets_vol.loc[feat.index].to_numpy(dtype=float))[oos_mask].mean())
            if oos_mask.any()
            else np.nan
        )
        bh_means_vol.append(
            float(rets_vol.loc[feat.index].to_numpy(dtype=float)[oos_mask].mean())
            if oos_mask.any()
            else np.nan
        )

    cross_price = {}
    cross_vol = {}
    for fee, slp in c273.COST_GRID:
        key = f"fee{fee}_slip{slp}"
        cross_price[key] = float(
            sum(a["price_pnl"]["per_cost"][key]["oos_net_sum"]
                for a in per_asset.values() if a.get("status") == "ok")
        )
        cross_vol[key] = float(
            sum(a["volume_return_pnl"]["per_cost"][key]["oos_net_sum"]
                for a in per_asset.values() if a.get("status") == "ok")
        )
    all_pos_price = all(v > 0 for v in cross_price.values()) if cross_price else False
    all_beat_bh_price = (
        np.nanmean(strat_means_price) > np.nanmean(bh_means_price)
        if strat_means_price and bh_means_price
        else False
    )
    price_edge = bool(any_exposure and all_pos_price and all_beat_bh_price)

    out = {
        "generated_at_utc": ts,
        "campaign": 277,
        "sub_campaign": "C277A",
        "strategy_id": "VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_PERCENTILE_SPREAD_SHOCK_MR",
        "purpose": "Price-PnL tradability gate for frozen C273 volume-return metric.",
        "return_basis": "spot_price",
        "feature_source": "frozen C273 volume-RQA feature (unchanged)",
        "preflight": preflight,
        "walk_forward": {"train": TRAIN, "test": TEST, "step": STEP},
        "cost_grid_bps": c273.COST_GRID,
        "params": {
            "W_RR": c273.W_RR,
            "alb": c273.ALB,
            "m": c273.M_EMB,
            "tau": c273.TAU,
            "eps_scale": c273.EPS_SCALE,
            "w_min": c273.W_MIN,
            "entry_z": c273.ENTRY_Z,
            "exit_z": c273.EXIT_Z,
            "max_hold": c273.MAX_HOLD,
        },
        "data_sources": {
            "spot_cache": str(c273.SPOT_CACHE.relative_to(root)),
            "spot_cache_sha256": spot_sha,
            "spot_meta_sha256": sha256_file(c273.SPOT_META) if c273.SPOT_META.exists() else None,
            "volume_pkl_sha256": sha256_file(c273.VOL_PKL) if c273.VOL_PKL.exists() else None,
            "volume_meta_sha256": sha256_file(c273.VOL_META) if c273.VOL_META.exists() else None,
            "volume_provenance_sha256": sha256_file(c273.VOL_PROV) if c273.VOL_PROV.exists() else None,
            "volume_validation": vol_report,
        },
        "per_asset": per_asset,
        "cross_asset_price_pnl": {"oos_net_sums": cross_price},
        "cross_asset_volume_return_pnl": {"oos_net_sums": cross_vol},
        "price_pnl_edge_proven": price_edge,
        "any_exposure_oos": bool(any_exposure),
        "all_cost_slices_positive_price_oos_net_sum": bool(all_pos_price),
        "all_cost_slices_price_beat_bh_mean_rule": bool(all_beat_bh_price),
        "edge_rule": (
            "price_pnl_edge_proven=true IFF OOS exposure>0 AND for ALL cost slices "
            "price PnL OOS net sum > 0 AND mean price PnL OOS net > mean B&H spot-price "
            "return on the same WF windows. Real data only."
        ),
        "frozen_c273_volume_return_cross": cross_vol,
        "frozen_c273_volume_return_reference": {
            "path": str(FROZEN_C273_OOS.relative_to(root)),
            "sha256": sha256_file(FROZEN_C273_OOS),
        },
    }

    out_name = f"campaign277_c273_price_pnl_revalidation_{ts}.json"
    out_path = reports / out_name
    out_path.write_text(json.dumps(out, indent=2, default=str) + "\n")
    out_sha = sha256_file(out_path)

    finding = {
        "generated_at_utc": ts,
        "campaign": 277,
        "sub_campaign": "C277A",
        "finding": "C273 METRIC VALIDITY",
        "verdict": "NON_TRADABLE_METRIC_UNTIL_PRICE_PNL_GATE",
        "verdict_resolved_by": str(out_path.relative_to(root)),
        "verdict_resolved_by_sha256": out_sha,
        "price_pnl_edge_proven": price_edge,
        "evidence": {
            "c273_script": str(C273_PATH.relative_to(root)),
            "c273_script_sha256": sha256_file(C273_PATH),
            "c273_volume_return_basis_line": "scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_percentile_spread_shock_mr_costed_oos.py:199",
            "c273_volume_return_basis_code": "r = np.log(vv).diff().dropna()  # vv = quote volume",
            "c273_pnl_line": "scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_percentile_spread_shock_mr_costed_oos.py:271-277",
            "c273_pnl_code": "npn = rets; strat = ppn * npn - trades * tc  # rets are volume returns",
            "spot_price_used_for_pnl_in_c273": False,
            "frozen_c273_oos": str(FROZEN_C273_OOS.relative_to(root)),
            "frozen_c273_oos_sha256": sha256_file(FROZEN_C273_OOS),
        },
        "conclusion": (
            "C273 oos_edge_proven=true is a volume-return metric. C277A recomputes the "
            "same feature/positions/WF/cost grid with spot-price returns; price_pnl_edge_proven="
            f"{price_edge}. Volume-return-only candidates remain NOT_TRADABLE."
        ),
    }
    finding_name = f"campaign273_metric_validity_finding_{ts}.json"
    finding_path = reports / finding_name
    finding_path.write_text(json.dumps(finding, indent=2, default=str) + "\n")
    finding_sha = sha256_file(finding_path)

    print(
        json.dumps(
            {
                "preflight": preflight,
                "price_pnl_edge_proven": price_edge,
                "any_exposure_oos": bool(any_exposure),
                "all_cost_slices_positive_price_oos_net_sum": bool(all_pos_price),
                "all_cost_slices_price_beat_bh_mean_rule": bool(all_beat_bh_price),
                "cross_asset_price_pnl": cross_price,
                "cross_asset_volume_return_pnl": cross_vol,
                "artifact": str(out_path.relative_to(root)),
                "artifact_sha256": out_sha,
                "finding": str(finding_path.relative_to(root)),
                "finding_sha256": finding_sha,
                "c273_script_sha256": sha256_file(C273_PATH),
                "generated_at_utc": ts,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()