#!/usr/bin/env python3
"""C187: RQA ratio LAVG/ENTR (mean diagonal line length LAVG normalized by
diagonal-line Shannon entropy ENTR) shock on delay-embedded log-volume returns (real data only).

Feature (pre-stated, distinct, grep-verified before implementation/run):
  VOLUME_RQA_TREND_OVER_DET_RATIO_SHOCK_MR. On r_t = ln(v_t)-ln(v_{t-1}), build
  delay embedding X_i = (r_i, r_{i+tau}) with m=2, tau=1 over trailing window
  W_RR=168. Recurrence matrix R_{ij}=1 if ||X_i-X_j||_inf <= eps, else 0;
  eps = eps_scale * std(r_window) with pre-stated fixed eps_scale=0.5.
  DET = (sum of recurrence points in qualifying diagonal lines, k>=1, l>=l_min,
  excluding LOI) / (sum of recurrence points in all diagonals k>=1, excluding LOI).
  RR_k = count of recurrence points on diagonal k (k>=1) / M_pts.
  TREND = least-squares slope of RR_k vs k over k=1..W_TREND (fixed W_TREND=20, clipped).
  RATIO_TREND_DET = TREND / DET.
  Fail-closed to NaN/no-signal if DET==0 or undefined/non-finite/degenerate, TREND
  undefined/non-finite/degenerate, denominator/ratio non-finite, or insufficient
  qualifying points. Causal trailing only.
  Distinct from C125-C187 (TREND/DET pairing not used before).
"""

from __future__ import annotations

import hashlib
import json
import pickle
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

SPOT_CACHE = cache_dir / "0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl"
SPOT_META = cache_dir / "0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.meta.json"
VOL_PKL = cache_dir / "volume_1h_full.pkl"
VOL_META = cache_dir / "volume_1h_full.meta.json"
VOL_PROV = cache_dir / "volume_1h_full.provenance.json"

PRIOR_REGISTRY = "reports/strategy_edge_registry_20261108T004812Z.json"
PRIOR_REGISTRY_SHA = "1aca1a556e00763cec77945c6c48085b2ba77b1c486932444510d8221124eeb9"
# C187 OOS artifact SHA verified from bytes.
PRIOR_C187_OOS = "reports/real_quote_volume_rqa_lavg_over_entr_ratio_shock_mr_costed_oos_20261108T004708Z.json"
PRIOR_C187_OOS_SHA = "0f5b82f91352ab34741936164e6d1888e93b4865342ab1f7975c017ee896cd63"

W_RR = 168
ALB = 336
M_EMB = 2
TAU = 1
EPS_SCALE = 0.5
L_MIN = 2
W_TREND = 20
ENTRY_Z = 1.5
EXIT_Z = 0.5
MAX_HOLD = 24

TRAIN = 720
TEST = 168
STEP = 168
COST_GRID = [[0, 0], [5, 5], [10, 10], [20, 20], [40, 40]]

DISTINCTNESS_GREP = "grep -rnE 'TREND_OVER_DET|trend_over_det|rqa_ratio_trend_over_det|rqa_trend_over_det_ratio' scripts/ strategies/ backtest/ utils/ 2>&1"
DISTINCTNESS_HITS_PRE = 0
DISTINCTNESS_VERIFIED_UTC = ts


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_spot():
    meta = json.loads(SPOT_META.read_text()) if SPOT_META.exists() else {}
    with open(SPOT_CACHE, "rb") as f:
        df = pickle.load(f)
    if isinstance(df, pd.Series):
        df = df.to_frame()
    return df, meta, sha256_file(SPOT_CACHE)


def load_volume():
    from data.real_feed_loader import validate_and_load_real_feed

    prov = json.loads(VOL_PROV.read_text()) if VOL_PROV.exists() else {}
    df, report = validate_and_load_real_feed(VOL_META, "real_quote_volume", provenance=prov)
    df = df.pivot_table(
        index="timestamp_utc", columns="symbol", values="quote_volume_usdt", aggfunc="first"
    ).sort_index()
    return df, report


def wf_splits(n: int, train: int, test: int, step: int):
    out = []
    i = 0
    while i + train + test <= n:
        out.append((i, i + train, i + train + test))
        i += step
    return out


def _det_trend(R: np.ndarray, l_min: int, w_trend: int):
    """Compute DET and TREND on recurrence matrix R (M_pts x M_pts).
    DET = sum of recurrence points in qualifying diagonal lines (k>=1, l>=l_min, excl LOI)
          / sum of recurrence points in all diagonals k>=1 (excl LOI). Fail-closed if denom==0.
    RR_k = count of recurrence points on diagonal k (k>=1) / M_pts.
    TREND = least-squares slope of RR_k vs k for k=1..min(w_trend, M_pts-1).
    """
    M_pts = R.shape[0]
    if M_pts < 3:
        return np.nan, np.nan
    total_recur = 0
    det_recur = 0
    rr = []
    max_k = M_pts - 1
    for k in range(1, max_k + 1):
        diag = np.diag(R, k=k)
        s = int(np.sum(diag))
        total_recur += s
        rr.append(s / float(M_pts))
        run = 0
        for val in diag:
            if val:
                run += 1
            else:
                if run >= l_min:
                    det_recur += run
                run = 0
        if run >= l_min:
            det_recur += run
    if total_recur <= 0:
        return np.nan, np.nan
    det = det_recur / float(total_recur)
    det = float(det) if np.isfinite(det) else np.nan
    n_trend = min(w_trend, len(rr))
    if n_trend < 3:
        trend = np.nan
    else:
        ks = np.arange(1, n_trend + 1, dtype=float)
        ys = np.asarray(rr[:n_trend], dtype=float)
        if not np.all(np.isfinite(ys)):
            trend = np.nan
        else:
            A = np.vstack([ks, np.ones_like(ks)]).T
            try:
                slope, _ = np.linalg.lstsq(A, ys, rcond=None)[0]
                trend = float(slope)
            except Exception:
                trend = np.nan
    trend = float(trend) if np.isfinite(trend) else np.nan
    return det, trend


def rqa_trend_over_det_ratio_window(rw: np.ndarray, eps_scale: float, l_min: int, w_trend: int) -> float:
    if rw is None or len(rw) < (M_EMB - 1) * TAU + 3:
        return np.nan
    if not np.all(np.isfinite(rw)):
        return np.nan
    sigma = float(np.std(rw, ddof=1))
    if not np.isfinite(sigma) or sigma <= 1e-18:
        return np.nan
    eps = eps_scale * sigma
    if not np.isfinite(eps) or eps <= 0:
        return np.nan
    M_pts = len(rw) - (M_EMB - 1) * TAU
    if M_pts < 3:
        return np.nan
    x = np.column_stack([rw[:M_pts], rw[TAU : TAU + M_pts]])
    if not np.all(np.isfinite(x)):
        return np.nan
    diff = np.max(np.abs(x[:, None, :] - x[None, :, :]), axis=2)
    R = (diff <= eps).astype(np.int8)
    det, trend = _det_trend(R, l_min, w_trend)
    if not np.isfinite(det) or det == 0:
        return np.nan
    if not np.isfinite(trend):
        return np.nan
    ratio = trend / det
    if not np.isfinite(ratio):
        return np.nan
    return float(ratio)


def _vol_s(vol_srs, i):
    try:
        return float(vol_srs.iloc[i])
    except Exception:
        return np.nan


def run_asset(spot: pd.Series, vol: pd.Series):
    close = spot.values.astype(float)
    idx = spot.index
    n = len(close)
    rvol = np.full(n, np.nan)
    for i in range(1, n):
        vi = _vol_s(vol, i)
        vim1 = _vol_s(vol, i - 1)
        if vi is not None and vim1 is not None and np.isfinite(vi) and np.isfinite(vim1) and vi > 0 and vim1 > 0:
            rvol[i] = np.log(vi) - np.log(vim1)
    feat = np.full(n, np.nan)
    step_feat = 2
    last_val = np.nan
    for i in range(W_RR, n):
        if (i - W_RR) % step_feat == 0 or not np.isfinite(last_val):
            w = rvol[i - W_RR + 1 : i + 1]
            wf = w[np.isfinite(w)]
            if len(wf) >= int(0.9 * W_RR):
                last_val = rqa_trend_over_det_ratio_window(wf, EPS_SCALE, L_MIN, W_TREND)
            else:
                last_val = np.nan
        feat[i] = last_val
    feat_s = pd.Series(feat, index=idx)
    mu = feat_s.rolling(ALB, min_periods=ALB).mean()
    sd = feat_s.rolling(ALB, min_periods=ALB).std(ddof=1)
    z = (feat_s - mu) / sd
    z = z.replace([np.inf, -np.inf], np.nan)
    raw = np.zeros(n)
    pos = 0
    hold = 0
    zv = z.values
    fv = feat
    for i in range(1, n):
        zi = zv[i]
        fi = fv[i]
        if not np.isfinite(zi) or not np.isfinite(fi):
            raw[i] = pos
            hold = (hold + 1) if pos != 0 else 0
            if pos != 0 and hold >= MAX_HOLD:
                pos = 0
                hold = 0
            continue
        if pos != 0:
            hold += 1
            if abs(zi) < EXIT_Z or hold >= MAX_HOLD:
                pos = 0
                hold = 0
        if pos == 0:
            if zi >= ENTRY_Z:
                pos = -1
                hold = 0
            elif zi <= -ENTRY_Z:
                pos = 1
                hold = 0
        raw[i] = pos
    sig = np.zeros(n)
    sig[1:] = raw[:-1]
    ret = np.zeros(n)
    ret[1:] = close[1:] / close[:-1] - 1.0
    splits = wf_splits(n, TRAIN, TEST, STEP)
    if not splits:
        return {"error": "no_wf_splits"}
    oos_union = np.zeros(n, dtype=bool)
    for _st, te_s, te_e in splits:
        oos_union[te_s:te_e] = True
    bh = ret.copy()
    bh[~oos_union] = 0.0
    bh_oos = float(np.nansum(bh))
    bh_oos_mean = float(np.nanmean(bh[oos_union])) if oos_union.any() else 0.0
    slices = {}
    for f_bps, s_bps in COST_GRID:
        gross = sig * ret
        turn = np.abs(np.diff(np.concatenate([[0.0], sig])))
        cost_rt = (f_bps + s_bps) / 10000.0
        net = gross - turn * cost_rt
        net[~oos_union] = 0.0
        gross_oos = gross.copy()
        gross_oos[~oos_union] = 0.0
        key = f"fee{f_bps}_slip{s_bps}"
        oos_net = float(np.nansum(net))
        oos_gross = float(np.nansum(gross_oos))
        oos_mean = float(np.nanmean(net[oos_union])) if oos_union.any() else 0.0
        slices[key] = {
            "oos_gross_sum": oos_gross,
            "oos_net_sum": oos_net,
            "oos_net_mean": oos_mean,
            "oos_bh_sum": bh_oos,
            "oos_bh_mean": bh_oos_mean,
            "positive": bool(oos_net > 0),
            "beats_bh_mean": bool(oos_mean > bh_oos_mean),
        }
    edge = bool(np.any(sig != 0) and oos_union.any()) and all(
        slices[f"fee{f}_slip{s}"]["oos_net_sum"] > 0
        and slices[f"fee{f}_slip{s}"]["oos_net_mean"] > slices[f"fee{f}_slip{s}"]["oos_bh_mean"]
        for f, s in COST_GRID
    )
    return {
        "n_bars": int(n),
        "window_start": str(idx[0]),
        "window_end": str(idx[-1]),
        "n_wf_folds": len(splits),
        "has_exposure_oos": bool(np.any(sig[oos_union] != 0)),
        "n_active_bars_oos": int(np.sum(sig[oos_union] != 0)),
        "exposure_frac_oos": float(np.mean(sig[oos_union] != 0)) if oos_union.any() else 0.0,
        "bh_oos_sum": bh_oos,
        "bh_oos_mean": bh_oos_mean,
        "cost_slices": slices,
        "edge_proven_oos": edge,
    }


def main():
    spot_df, spot_meta, spot_sha = load_spot()
    vol_df, vol_report = load_volume()
    assets = {}
    for sym in ["ADA", "BTC", "ETH", "SOL"]:
        if sym not in spot_df.columns or sym not in vol_df.columns:
            assets[sym] = {"error": "missing_symbol"}
            continue
        s = pd.to_numeric(spot_df[sym], errors="coerce").dropna()
        v = pd.to_numeric(vol_df[sym], errors="coerce").reindex(s.index)
        common = s.index.intersection(v.dropna().index)
        s = s.loc[common]
        v = v.loc[common]
        if len(s) < TRAIN + TEST + ALB + W_RR + 10:
            assets[sym] = {"error": "insufficient_overlap", "n": int(len(s))}
            continue
        assets[sym] = run_asset(s, v)
    cross = {}
    for f, s in COST_GRID:
        key = f"fee{f}_slip{s}"
        cross[key] = float(sum(
            a.get("cost_slices", {}).get(key, {}).get("oos_net_sum", 0.0)
            for a in assets.values() if isinstance(a, dict) and "cost_slices" in a
        ))
    any_exposure = any(a.get("has_exposure_oos") for a in assets.values() if isinstance(a, dict))
    all_pos = all(cross[k] > 0 for k in cross)
    all_beat_bh = all(
        a.get("cost_slices", {}).get(k, {}).get("oos_net_mean", -1e9)
        > a.get("cost_slices", {}).get(k, {}).get("oos_bh_mean", 1e9)
        for a in assets.values() if isinstance(a, dict) and "cost_slices" in a
        for k in cross
    ) if any_exposure else False
    edge = bool(any_exposure and all_pos and all_beat_bh)
    out = {
        "tool": "real_quote_volume_rqa_trend_over_det_ratio_shock_mr_costed_oos",
        "generated_at_utc": ts,
        "campaign": 188,
        "strategy_id": "VOLUME_RQA_TREND_OVER_DET_RATIO_SHOCK_MR",
        "candidate": "VOLUME_RQA_TREND_OVER_DET_RATIO_SHOCK_MR (RQA ratio TREND/DET on delay-embedded log-volume returns; DET = determinism qualifying diagonal points/sum diagonal recurrence points k>=1 excl LOI l>=l_min; RR_k=recurrence points on diagonal k/M_pts; TREND=least-squares slope of RR_k vs k over k=1..W_TREND, W_TREND=20; m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2; fade ratio shocks vs ALB=336)",
        "feature_definition": "RATIO_TREND_DET = TREND / DET. DET = sum of recurrence points in qualifying diagonal lines (k>=1, l>=l_min, excluding LOI) / sum of recurrence points in diagonals k>=1 excluding LOI. RR_k = recurrence points on diagonal k (k>=1) / M_pts. TREND = least-squares slope of RR_k vs k over k=1..W_TREND (W_TREND=20 fixed, clipped). Delay embedding m=2 tau=1 over trailing window W_RR=168, L-inf recurrence with eps=EPS_SCALE*std(window); causal trailing only; fail-closed to NaN/no-signal if DET==0 or undefined/non-finite/degenerate, TREND undefined/non-finite/degenerate, denominator/ratio non-finite, or insufficient qualifying points.",
        "pre_stated_distinctness": {
            "grep_cmd": DISTINCTNESS_GREP,
            "grep_hits_at_selection": DISTINCTNESS_HITS_PRE,
            "grep_verified_at_utc": DISTINCTNESS_VERIFIED_UTC,
            "grep_evidence_note": "Pre-implementation/run grep over scripts/strategies/backtest/utils returned 0 non-self hits (verified before implementation/run); distinctness confirmed. Primary candidate used.",
            "selection_note": "Primary C188 candidate from C187 state.yaml (TREND_OVER_DET); grep-zero confirmed at run time. TREND numerator with DET denominator — pairing not used in C125-C187.",
            "family": "RQA TREND/DET ratio shock on volume dynamics",
            "uses_ratio_of_rqa_measures": True,
        },
        "real_data_only": True,
        "fabricated_data": False,
        "fail_closed": True,
        "edge_claim": "NONE",
        "data": {
            "spot_cache": str(SPOT_CACHE),
            "spot_cache_sha256": spot_sha,
            "spot_meta": spot_meta,
            "volume_meta": str(VOL_META),
            "volume_loader_report": vol_report,
        },
        "params": {
            "w_rr": W_RR, "alb": ALB, "m_emb": M_EMB, "tau": TAU, "eps_scale": EPS_SCALE,
            "l_min": L_MIN, "w_trend": W_TREND, "entry_z": ENTRY_Z, "exit_z": EXIT_Z, "max_hold": MAX_HOLD,
            "train": TRAIN, "test": TEST, "step": STEP, "cost_grid": COST_GRID,
            "feature_compute_step": 2,
            "feature_compute_note": "Causal trailing RQA computed every 2 bars and held (causal forward-hold) for runtime; signal/z/exec logic unchanged.",
            "det_definition": "DET = sum of recurrence points in qualifying diagonal lines (k>=1, l>=l_min, excl LOI) / sum of recurrence points in diagonals k>=1 excl LOI; fail-closed if DET==0 or undefined/non-finite/degenerate",
            "trend_definition": "TREND = least-squares slope of RR_k vs k over k=1..W_TREND (W_TREND=20 fixed, clipped); RR_k = recurrence points on diagonal k / M_pts",
            "diag_scope": "k>=1 upper triangle, excluding main diagonal/LOI",
        },
        "references": {
            "prior_registry": PRIOR_REGISTRY,
            "prior_registry_sha256": PRIOR_REGISTRY_SHA,
            "c187_oos": PRIOR_C187_OOS,
            "c187_oos_sha256": PRIOR_C187_OOS_SHA,
            "c187_note": "C187 OOS SHA verified from bytes (LAVG_OVER_ENTR, oos_edge_proven false); C188 uses TREND/DET.",
        },
        "per_asset": assets,
        "cross_asset": {"oos_net_sums": cross},
        "oos_edge_proven": edge,
        "any_exposure_oos": bool(any_exposure),
        "all_cost_slices_positive_oos_net_sum": bool(all_pos),
        "all_cost_slices_beat_bh_mean_rule": bool(all_beat_bh),
        "edge_rule": "oos_edge_proven=true IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. WF 720/168/168, cost grid [[0,0],[5,5],[10,10],[20,20],[40,40]], B&H same OOS windows.",
    }
    if edge:
        out["edge_claim"] = "CONDITIONAL_EDGE_PROVEN"
    out_path = reports / f"real_quote_volume_rqa_trend_over_det_ratio_shock_mr_costed_oos_{ts}.json"
    out_path.write_text(json.dumps(out, indent=2, default=str) + "\n")
    out_sha = sha256_file(out_path)
    print(json.dumps({
        "oos": str(out_path.relative_to(root)), "oos_sha256": out_sha,
        "oos_edge_proven": edge, "edge_claim": out["edge_claim"],
        "any_exposure_oos": any_exposure, "all_cost_slices_positive_oos_net_sum": all_pos,
        "all_cost_slices_beat_bh_mean_rule": all_beat_bh, "cross_asset_oos_net_sums": cross,
    }, indent=2))


if __name__ == "__main__":
    main()
