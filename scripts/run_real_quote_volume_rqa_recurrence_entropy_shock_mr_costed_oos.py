#!/usr/bin/env python3
"""C130: RQA recurrence entropy ENTR on delay-embedded log-volume returns (real data only).

Feature (pre-stated, distinct, grep-verified 20261107T062733Z before implementation/run):
  VOLUME_RQA_RECURRENCE_ENTROPY_SHOCK_MR. On r_t = ln(v_t)-ln(v_{t-1}), build delay
  embedding X_i = (r_i, r_{i+tau}) with m=2, tau=1 over trailing window W_RR=168.
  Recurrence matrix R_{ij}=1 if ||X_i-X_j||_inf <= eps, else 0;
  eps = eps_scale * std(r_window) with pre-stated fixed eps_scale=0.5.
  Find diagonal line lengths l >= l_min, l_min=2 (pre-stated), excluding the main
  diagonal (both upper/lower k!=0). Let n(l) be count of diagonal lines of length
  l, N=Σ n(l), p(l)=n(l)/N. ENTR = -Σ_{l:l_min} p(l)*ln(p(l)) (natural log).
  Fail-closed to NaN/no-signal on non-finite, degenerate std/eps, N==0, or
  undefined entropy (state rule). Causal trailing only.

Distinctness (grep-zero pre-implementation): recurrence_entropy|ENTR_RQA|diag_entropy|diagonal_entropy|rqa_entr
  over scripts/ strategies/ backtest/ utils/ returned zero hits (recorded).
  Distinct from C125 %REC (density), C126 %DET (diagonal-line fraction), C127 L_MEAN
  (diagonal mean length), C128 %LAM (vertical fraction), C129 TT (vertical mean
  length) — C130 measures complexity/uncertainty of the diagonal-line-length
  distribution (Shannon entropy of p(l)); distinct from permutation/sample/approx/
  SVD/spectral/wavelet/phase/Fisher entropy families and BDS/C104–C124.

Signal (fail-closed MR): z = (feature - ALB_mean) / ALB_std, ALB=336.
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

PRIOR_REGISTRY = "reports/strategy_edge_registry_20261107T062733Z.json"
PRIOR_REGISTRY_SHA = "434e1530cb282a045f4b80ef7c62fca385df3285b5d3fe3e37847c43f8e93d5c"
PRIOR_C129_OOS = "reports/real_quote_volume_rqa_trapping_time_shock_mr_costed_oos_20261107T062741Z.json"
PRIOR_C129_OOS_SHA = "e9bff8c9625689a129b09b6cedff349b484941151f1f1a76a49aea3c443afa04"

# C130 pre-stated params
W_RR = 168  # recurrence window
ALB = 336  # adaptive baseline for z
M_EMB = 2
TAU = 1
EPS_SCALE = 0.5  # eps = EPS_SCALE * std(r_window), pre-stated fixed
L_MIN = 2  # minimum diagonal line length, pre-stated
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


def rqa_recurrence_entropy_window(rw: np.ndarray, eps_scale: float, l_min: int) -> float:
    """ENTR on a 1-D log-return window using delay embedding (m=2,tau=1).
    ENTR = Shannon entropy of diagonal-line length distribution p(l) over
    qualifying diagonal lines l>=l_min (main diagonal excluded, k!=0).
    Fail-closed: NaN on non-finite, degenerate, zero recurrence, N==0, or undefined entropy."""
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
    # delay embedding m=2, tau=1
    M_pts = len(rw) - (M_EMB - 1) * TAU
    if M_pts < 3:
        return np.nan
    x = np.column_stack([rw[:M_pts], rw[TAU : TAU + M_pts]])
    if not np.all(np.isfinite(x)):
        return np.nan
    # recurrence matrix (Chebyshev / L-inf)
    diff = np.max(np.abs(x[:, None, :] - x[None, :, :]), axis=2)
    R = (diff <= eps).astype(np.int8)
    # exclude main diagonal for recurrence-point denominator
    offdiag = R.copy()
    np.fill_diagonal(offdiag, 0)
    total_rec = float(offdiag.sum())
    if total_rec <= 0:
        return np.nan
    # diagonal lines of length >= l_min (both upper/lower diagonals, k != 0)
    counts = {}
    for k in range(-(M_pts - 1), M_pts):
        if k == 0:
            continue
        diag = np.diag(R, k=k)
        run = 0
        for val in diag:
            if val:
                run += 1
            else:
                if run >= l_min:
                    counts[run] = counts.get(run, 0) + 1
                run = 0
        if run >= l_min:
            counts[run] = counts.get(run, 0) + 1
    N = sum(counts.values())
    if N <= 0:
        return np.nan
    entr = 0.0
    for n_l in counts.values():
        p = n_l / N
        if p > 0.0:
            entr -= p * np.log(p)
    if not np.isfinite(entr):
        return np.nan
    return float(entr)


def _vol_s(vol_srs, i):
    try:
        return float(vol_srs.iloc[i])
    except Exception:
        return np.nan


def run_asset(spot: pd.Series, vol: pd.Series):
    close = spot.values.astype(float)
    v = vol.reindex(spot.index).values.astype(float)
    idx = spot.index
    n = len(close)
    rvol = np.full(n, np.nan)
    for i in range(1, n):
        vi = _vol_s(vol, i)
        vim1 = _vol_s(vol, i - 1)
        if vi is not None and vim1 is not None and np.isfinite(vi) and np.isfinite(vim1) and vi > 0 and vim1 > 0:
            rvol[i] = np.log(vi) - np.log(vim1)
    feat = np.full(n, np.nan)
    for i in range(W_RR, n):
        w = rvol[i - W_RR + 1 : i + 1]
        if np.sum(np.isfinite(w)) >= int(0.9 * W_RR):
            wf = w[np.isfinite(w)]
            feat[i] = rqa_recurrence_entropy_window(wf, EPS_SCALE, L_MIN)
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
            fold_stats.append(
                {
                    "fold": fi,
                    "train_start": str(idx[tr_s]),
                    "test_start": str(idx[te_s]),
                    "test_end": str(idx[te_e - 1]),
                    "oos_net_sum": float(np.nansum(seg)),
                    "oos_net_mean": float(np.nanmean(seg)) if len(seg) else 0.0,
                    "oos_bh_sum": float(np.nansum(ret[te_s:te_e])),
                }
            )
        slices[key] = {
            "fee_bps": f,
            "slip_bps": s,
            "oos_net_sum": oos_sum,
            "oos_net_mean": oos_mean,
            "oos_win_rate": win,
            "oos_bh_sum": bh_oos,
            "oos_bh_mean": bh_oos_mean,
            "folds": fold_stats,
        }
    edge = False
    if (np.abs(sig[oos_union]) > 0).sum() > 0:
        all_pos = all(slices[f"fee{f}_slip{s}"]["oos_net_sum"] > 0 for f, s in COST_GRID)
        all_beat = all(
            slices[f"fee{f}_slip{s}"]["oos_net_mean"] > bh_oos_mean for f, s in COST_GRID
        )
        edge = all_pos and all_beat
    return {
        "n_bars": n,
        "window_start": str(idx[0]) if n else None,
        "window_end": str(idx[-1]) if n else None,
        "n_wf_folds": len(splits),
        "has_exposure_oos": bool((np.abs(sig[oos_union]) > 0).sum() > 0) if oos_union.any() else False,
        "n_active_bars_oos": int((np.abs(sig[oos_union]) > 0).sum()) if oos_union.any() else 0,
        "exposure_frac_oos": float((np.abs(sig[oos_union]) > 0).mean()) if oos_union.any() else 0.0,
        "bh_oos_sum": bh_oos,
        "bh_oos_mean": bh_oos_mean,
        "cost_slices": slices,
        "oos_edge_proven": edge,
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
        except Exception:
            continue
    fee_slip_list = COST_GRID
    any_exp = any(v.get("has_exposure_oos") for v in res.values())
    sums = {}
    means = {}
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
        "tool": "real_quote_volume_rqa_recurrence_entropy_shock_mr_costed_oos",
        "generated_at_utc": ts,
        "campaign": 130,
        "strategy_id": "VOLUME_RQA_RECURRENCE_ENTROPY_SHOCK_MR",
        "candidate": "VOLUME_RQA_RECURRENCE_ENTROPY_SHOCK_MR (RQA recurrence entropy ENTR on delay-embedded log-volume returns; m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2; fade shocks vs ALB=336)",
        "feature_definition": "ENTR = -sum p(l)*ln(p(l)) over diagonal-line length distribution p(l)=n(l)/N, l>=l_min, delay embedding m=2 tau=1 over trailing window W_RR=168, L-inf recurrence with eps=EPS_SCALE*std(window), main diagonal excluded both upper/lower k!=0 diagonals; causal trailing only; fail-closed on degenerate/non-finite/zero-recurrence/N==0/undefined-entropy",
        "pre_stated_distinctness": {
            "grep_cmd": "grep -rn 'recurrence_entropy|ENTR_RQA|diag_entropy|diagonal_entropy|rqa_entr' scripts/ strategies/ backtest/ utils/ 2>/dev/null | head",
            "grep_hits_at_selection": 0,
            "grep_verified_at_utc": "20261107T062733Z",
            "selection_note": "Pre-selected in HANDOFF C130; grep-zero confirmed before implementation/run.",
            "family": "RQA recurrence entropy (Shannon entropy of diagonal-line-length distribution)",
            "distinct_from_c125": "C125 %REC is recurrence density (no line-structure).",
            "distinct_from_c126": "C126 %DET quantifies diagonal-line predictability structure (fraction).",
            "distinct_from_c127": "C127 L_MEAN is diagonal mean line length (average, not entropy).",
            "distinct_from_c128": "C128 %LAM is vertical-line fraction (stuck-state structure), not diagonal entropy.",
            "distinct_from_c129": "C129 TT is mean length of qualifying vertical lines, not diagonal entropy.",
            "distinct_from_bds": "BDS uses correlation-integral dependence; no recurrence-matrix diagonal-line distribution entropy.",
            "distinct_from_c104_c124": "Different from Hilbert phase/envelope entropy, distribution/fuzzy/multiscale/sample/approx entropy, SVD/Fisher/attention/increment/permutation-variance/fluctuation-complexity/range/CRE/DispEn, spectral/permutation/bubble/slope/DFA/Hurst/Higuchi/Petrosian/Katz FD, LZ76, Hjorth/TKEO/OU/VR families.",
            "uses_diagonal_structure": True,
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
            "w_rr": W_RR,
            "alb": ALB,
            "m_emb": M_EMB,
            "tau": TAU,
            "eps_scale": EPS_SCALE,
            "l_min": L_MIN,
            "entry_z": ENTRY_Z,
            "exit_z": EXIT_Z,
            "max_hold": MAX_HOLD,
            "train": TRAIN,
            "test": TEST,
            "step": STEP,
            "cost_grid": COST_GRID,
        },
        "references": {
            "prior_registry": PRIOR_REGISTRY,
            "prior_registry_sha256": PRIOR_REGISTRY_SHA,
            "c129_oos": PRIOR_C129_OOS,
            "c129_oos_sha256": PRIOR_C129_OOS_SHA,
        },
        "per_asset": res,
        "aggregate": {
            "n_assets": len(res),
            "any_exposure_oos": any_exp,
            "all_cost_slices_positive_oos_net_sum": all_pos,
            "mean_bh_oos_mean_across_assets": mean_bh,
            "all_cost_slices_beat_bh_mean_rule": beats_bh,
            "oos_edge_proven": oos_edge,
            "cross_asset_sum_oos_net_sum": sums,
            "cross_asset_mean_oos_net_mean": mean_m,
        },
        "oos_edge_proven": oos_edge,
        "edge_claim_top": "NONE",
        "any_exposure_oos": any_exp,
        "all_cost_slices_positive_oos_net_sum_top": all_pos,
        "all_cost_slices_beat_bh_mean_rule_top": beats_bh,
        "cross_asset_oos_net_sums": sums,
    }
    fn = reports / f"real_quote_volume_rqa_recurrence_entropy_shock_mr_costed_oos_{ts}.json"
    fn.write_text(json.dumps(out, indent=2))
    print(
        json.dumps(
            {
                "artifact": str(fn),
                "sha256": sha256_file(fn),
                "oos_edge_proven": oos_edge,
                "any_exposure": any_exp,
                "all_pos": all_pos,
                "beats_bh": beats_bh,
                "sums": sums,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
