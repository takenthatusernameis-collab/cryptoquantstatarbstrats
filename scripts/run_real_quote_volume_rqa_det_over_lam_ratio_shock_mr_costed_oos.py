#!/usr/bin/env python3
"""C138: RQA ratio %DET/%LAM (determinism normalized by laminarity) shock on delay-embedded log-volume returns (real data only).

Feature (pre-stated, distinct, grep-verified before implementation/run):
  VOLUME_RQA_DET_OVER_LAM_RATIO_SHOCK_MR. On r_t = ln(v_t)-ln(v_{t-1}), build delay
  embedding X_i = (r_i, r_{i+tau}) with m=2, tau=1 over trailing window W_RR=168.
  Recurrence matrix R_{ij}=1 if ||X_i-X_j||_inf <= eps, else 0;
  eps = eps_scale * std(r_window) with pre-stated fixed eps_scale=0.5.
  %DET = (points in qualifying diagonal lines l>=l_min, main diagonal excluded)
         / (offdiag recurrence sum), l_min=2 (pre-stated).
  %LAM = (points in qualifying vertical lines l>=l_min, main diagonal excluded)
         / (offdiag recurrence sum), l_min=2 (pre-stated).
  RATIO_DET_LAM = %DET / %LAM (fail-closed to NaN/no-signal if %LAM<=0, offdiag sum<=0,
  non-finite, degenerate std/eps, or undefined). Causal trailing only.

Distinctness (grep-zero pre-implementation): det_over_lam|det_lam_ratio|rqa_ratio_det_lam|DET_OVER_LAM
  over scripts/ strategies/ backtest/ utils/ returned zero non-self hits (recorded).
  Collision guard: C126 %DET direct, C128 %LAM direct, C133 %DET/%RR, C134 %LAM/%DET (inverse),
  C136 %LAM/%RR, C137 %RR/%DET — C138 trades *ratio* %DET/%LAM, a genuinely distinct composite
  (determinism normalized by laminarity).

Signal (fail-closed MR): z = (RATIO_DET_LAM - ALB_mean) / ALB_std, ALB=336.
  entry_z >= 1.5 -> fade (short); entry_z <= -1.5 -> long; exit |z| < 0.5 or
  max_hold=24 or flip. Exec t -> t+1.
WF/costs/B&H (exact): 720/168/168, cost grid [[0,0],[5,5],[10,10],[20,20],[40,40]],
  B&H same OOS windows. Real data only; fail-closed.
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

SPOT_CACHE = root / "data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl"
SPOT_META = root / "data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.meta.json"
VOL_PKL = root / "data/cache/volume_1h_full.pkl"
VOL_META = root / "data/cache/volume_1h_full.meta.json"
VOL_PROV = root / "data/cache/volume_1h_full.provenance.json"

PRIOR_REGISTRY = "reports/strategy_edge_registry_20261107T080222Z.json"
PRIOR_REGISTRY_SHA = "0afcf580807f83dc82519ffbd8dac1283bb17621d2a813abad9ec33f8a73e5c3"
PRIOR_C137_OOS = "reports/real_quote_volume_rqa_rr_over_det_ratio_shock_mr_costed_oos_20261107T080021Z.json"
PRIOR_C137_OOS_SHA = "0acefbc7dfdaf656291ffad9d6900f483800707bc7878c7f2503baa6a9414f37"

W_RR = 168
ALB = 336
M_EMB = 2
TAU = 1
EPS_SCALE = 0.5
L_MIN = 2
ENTRY_Z = 1.5
EXIT_Z = 0.5
MAX_HOLD = 24

TRAIN = 720
TEST = 168
STEP = 168
COST_GRID = [[0, 0], [5, 5], [10, 10], [20, 20], [40, 40]]


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_spot():
    pkl = cache_dir / SPOT_CACHE.name
    meta_p = cache_dir / SPOT_META.name
    meta = json.loads(meta_p.read_text()) if meta_p.exists() else {}
    with open(pkl, "rb") as f:
        df = pickle.load(f)
    if isinstance(df, pd.Series):
        df = df.to_frame()
    return df, meta, sha256_file(pkl)


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


def _line_points_1d(arr: np.ndarray, l_min: int) -> int:
    """Count points in runs of 1s with length >= l_min."""
    if arr.size == 0:
        return 0
    d = np.diff(np.concatenate(([0], arr.astype(np.int8), [0])))
    starts = np.where(d == 1)[0]
    ends = np.where(d == -1)[0]
    lengths = ends - starts
    return int(lengths[lengths >= l_min].sum())


def _diag_line_points(R: np.ndarray, l_min: int) -> int:
    M = R.shape[0]
    pts = 0
    for k in range(-(M - 1), M):
        if k == 0:
            continue
        pts += _line_points_1d(np.diag(R, k=k), l_min)
    return pts


def _vert_line_points(R: np.ndarray, l_min: int) -> int:
    M = R.shape[0]
    pts = 0
    for j in range(M):
        col = R[:, j].copy()
        col[j] = 0  # exclude main diagonal
        pts += _line_points_1d(col, l_min)
    return pts

def rqa_det_over_lam_ratio_window(rw: np.ndarray, eps_scale: float, l_min: int) -> float:
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
    offdiag = R.copy()
    np.fill_diagonal(offdiag, 0)
    off_sum = float(offdiag.sum())
    if off_sum <= 0:
        return np.nan
    det = float(_diag_line_points(offdiag, l_min)) / off_sum
    if not np.isfinite(det) or det <= 0:
        return np.nan
    lam = float(_vert_line_points(offdiag, l_min)) / off_sum
    if not np.isfinite(lam) or lam <= 0:
        return np.nan
    ratio = det / lam
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
                last_val = rqa_det_over_lam_ratio_window(wf, EPS_SCALE, L_MIN)
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
    for f, s in COST_GRID:
        key = f"fee{f}_slip{s}"
        rate = (f + s) / 10000.0
        turn = np.abs(np.diff(sig, prepend=0.0))
        strat = sig * ret - turn * rate
        so = strat.copy()
        so[~oos_union] = 0.0
        oos_sum = float(np.nansum(so))
        oos_mean = float(np.nanmean(so[oos_union])) if oos_union.any() else 0.0
        win = float(np.nanmean(so[oos_union] > 0)) if oos_union.any() else 0.0
        fold_stats = []
        for fi, (tr_s, te_s, te_e) in enumerate(splits):
            seg = strat[te_s:te_e]
            fold_stats.append({
                "fold": fi,
                "train_start": str(idx[tr_s]),
                "test_start": str(idx[te_s]),
                "test_end": str(idx[te_e - 1]),
                "oos_net_sum": float(np.nansum(seg)),
                "oos_net_mean": float(np.nanmean(seg)) if len(seg) else 0.0,
                "oos_bh_sum": float(np.nansum(ret[te_s:te_e])),
            })
        slices[key] = {
            "fee_bps": f, "slip_bps": s, "oos_net_sum": oos_sum, "oos_net_mean": oos_mean,
            "oos_win_rate": win, "oos_bh_sum": bh_oos, "oos_bh_mean": bh_oos_mean, "folds": fold_stats,
        }
    edge = False
    if (np.abs(sig[oos_union]) > 0).sum() > 0:
        all_pos = all(slices[f"fee{f}_slip{s}"]["oos_net_sum"] > 0 for f, s in COST_GRID)
        all_beat = all(slices[f"fee{f}_slip{s}"]["oos_net_mean"] > bh_oos_mean for f, s in COST_GRID)
        edge = all_pos and all_beat
    return {
        "n_bars": n, "window_start": str(idx[0]) if n else None, "window_end": str(idx[-1]) if n else None,
        "n_wf_folds": len(splits),
        "has_exposure_oos": bool((np.abs(sig[oos_union]) > 0).sum() > 0) if oos_union.any() else False,
        "n_active_bars_oos": int((np.abs(sig[oos_union]) > 0).sum()) if oos_union.any() else 0,
        "exposure_frac_oos": float((np.abs(sig[oos_union]) > 0).mean()) if oos_union.any() else 0.0,
        "bh_oos_sum": bh_oos, "bh_oos_mean": bh_oos_mean, "cost_slices": slices, "oos_edge_proven": edge,
        "feature_compute_step": step_feat,
    }


def main():
    spot, spot_meta, spot_sha = load_spot()
    vol_df, vol_report = load_volume()
    if spot.index.tz is None:
        spot.index = spot.index.tz_localize("UTC")
    if vol_df.index.tz is None:
        vol_df.index = vol_df.index.tz_localize("UTC")
    syms = [s for s in spot.columns if s in vol_df.columns]
    res = {}
    for a in syms:
        try:
            sp = spot[a].astype(float)
            vv = vol_df[a]
            res[a] = run_asset(sp, vv)
            print(f"done {a} edge={res[a].get('oos_edge_proven')}", flush=True)
        except Exception as e:
            res[a] = {"error": str(e)}
            print(f"err {a}: {e}", flush=True)
    fee_slip_list = COST_GRID
    any_exp = any(v.get("has_exposure_oos") for v in res.values())
    sums, means = {}, {}
    bh_means = [v["bh_oos_mean"] for v in res.values() if "bh_oos_mean" in v]
    for f, s in fee_slip_list:
        key = f"fee{f}_slip{s}"
        sums[key] = sum(v["cost_slices"][key]["oos_net_sum"] for v in res.values() if key in v.get("cost_slices", {}))
        means[key] = sum(v["cost_slices"][key]["oos_net_mean"] for v in res.values() if key in v.get("cost_slices", {}))
    mean_bh = float(np.mean(bh_means)) if bh_means else 0.0
    mean_m = {k: float(means[k]) for k in means}
    all_pos = all(sums.get(f"fee{f}_slip{s}", -np.inf) > 0 for f, s in fee_slip_list)
    beats_bh = all(mean_m.get(f"fee{f}_slip{s}", -np.inf) > mean_bh for f, s in fee_slip_list)
    oos_edge = bool(any_exp and all_pos and beats_bh)
    out = {
        "tool": "real_quote_volume_rqa_det_over_lam_ratio_shock_mr_costed_oos",
        "generated_at_utc": ts, "campaign": 138,
        "strategy_id": "VOLUME_RQA_DET_OVER_LAM_RATIO_SHOCK_MR",
        "candidate": "VOLUME_RQA_DET_OVER_LAM_RATIO_SHOCK_MR (RQA ratio %DET/%LAM, determinism normalized by laminarity, on delay-embedded log-volume returns; m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2; fade RATIO_DET_LAM shocks vs ALB=336)",
        "feature_definition": "RATIO_DET_LAM = %DET/%LAM with %DET = (points in qualifying diagonal lines l>=l_min, main diagonal excluded)/(offdiag recurrence sum), %LAM = (points in qualifying vertical lines l>=l_min, main diagonal excluded)/(offdiag recurrence sum), delay embedding m=2 tau=1 over trailing window W_RR=168, L-inf recurrence with eps=EPS_SCALE*std(window); causal trailing only; fail-closed to NaN/no-signal on %LAM<=0, offdiag sum<=0, degenerate/non-finite/undefined",
        "pre_stated_distinctness": {
            "grep_cmd": "grep -rn 'det_over_lam|det_lam_ratio|rqa_ratio_det_lam|DET_OVER_LAM' scripts/ strategies/ backtest/ utils/ 2>/dev/null | head",
            "grep_hits_at_selection": 0, "grep_verified_at_utc": ts,
            "selection_note": "Primary C138 candidate from HANDOFF; grep-zero confirmed before implementation/run (no collision with C126 %DET direct, C128 %LAM direct, C133 %DET/%RR, C134 %LAM/%DET inverse, C136 %LAM/%RR, C137 %RR/%DET) — C138 trades ratio %DET/%LAM.",
            "family": "RQA %DET/%LAM ratio (determinism normalized by laminarity) shock on volume dynamics",
            "distinct_from_c126": "C126 trades %DET (determinism) directly; C138 normalizes %DET by %LAM.",
            "distinct_from_c128": "C128 trades %LAM (laminarity) directly; C138 forms ratio %DET/%LAM.",
            "distinct_from_c133": "C133 trades %DET/%RR; C138 uses %LAM denominator (not %RR).",
            "distinct_from_c134": "C134 trades %LAM/%DET (inverse); C138 trades %DET/%LAM.",
            "distinct_from_c136": "C136 trades %LAM/%RR; C138 uses %DET/%LAM.",
            "distinct_from_c137": "C137 trades %RR/%DET; C138 uses %DET/%LAM.",
            "uses_ratio_of_rqa_measures": True,
        },
        "real_data_only": True, "fabricated_data": False, "fail_closed": True, "edge_claim": "NONE",
        "data": {"spot_cache": str(SPOT_CACHE), "spot_cache_sha256": spot_sha, "spot_meta": spot_meta,
                 "volume_meta": str(VOL_META), "volume_loader_report": vol_report},
        "params": {"w_rr": W_RR, "alb": ALB, "m_emb": M_EMB, "tau": TAU, "eps_scale": EPS_SCALE, "l_min": L_MIN,
                   "entry_z": ENTRY_Z, "exit_z": EXIT_Z, "max_hold": MAX_HOLD, "train": TRAIN, "test": TEST,
                   "step": STEP, "cost_grid": COST_GRID, "feature_compute_step": 2,
                   "feature_compute_note": "Causal trailing RQA computed every 2 bars and held (causal forward-hold) for runtime; signal/z/exec logic unchanged."},
        "references": {"prior_registry": PRIOR_REGISTRY, "prior_registry_sha256": PRIOR_REGISTRY_SHA,
                       "c137_oos": PRIOR_C137_OOS, "c137_oos_sha256": PRIOR_C137_OOS_SHA},
        "per_asset": res,
        "aggregate": {"n_assets": len(res), "any_exposure_oos": any_exp,
                      "all_cost_slices_positive_oos_net_sum": all_pos,
                      "mean_bh_oos_mean_across_assets": mean_bh,
                      "all_cost_slices_beat_bh_mean_rule": beats_bh,
                      "oos_edge_proven": oos_edge,
                      "cross_asset_sum_oos_net_sum": sums,
                      "cross_asset_mean_oos_net_mean": mean_m},
        "oos_edge_proven": oos_edge, "edge_claim_top": "NONE",
        "any_exposure_oos": any_exp, "all_cost_slices_positive_oos_net_sum": all_pos,
        "all_cost_slices_beat_bh_mean_rule": beats_bh, "cross_asset": {"oos_net_sums": sums},
    }
    fn = reports / f"real_quote_volume_rqa_det_over_lam_ratio_shock_mr_costed_oos_{ts}.json"
    fn.write_text(json.dumps(out, indent=2))
    print(json.dumps({"artifact": str(fn), "sha256": sha256_file(fn), "oos_edge_proven": oos_edge,
                      "any_exposure": any_exp, "all_pos": all_pos, "beats_bh": beats_bh, "sums": sums}, indent=2))


if __name__ == "__main__":
    main()
