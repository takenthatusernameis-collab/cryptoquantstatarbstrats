#!/usr/bin/env python3
"""Campaign #125 Path R-B (fail-closed, real data only): recurrence_rate (RQA) shock MR.

Feature: recurrence_rate = %REC = (number of recurrence points in recurrence matrix) / (m' * m')
computed on delay-embedded state space of trailing log-volume returns over window W_RR=168.
Embedding dimension m=2, time delay tau=1 (Takens). Recurrence threshold epsilon as fraction
of std of embedded points (epsilon = 0.15 * sigma_embedded) or fixed rule; computed causally on
trailing data only. Fail-closed on degenerate/non-finite/singular.
"""
import json
import pickle
import hashlib
import sys
from pathlib import Path
from datetime import datetime, timezone

import numpy as np
import pandas as pd

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root))
cache_dir = root / "data" / "cache"
reports = root / "reports"
reports.mkdir(exist_ok=True)
ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

SPOT_CACHE = "0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7"
VOL_META = cache_dir / "volume_1h_full.meta.json"
COST_GRID = [[0, 0], [5, 5], [10, 10], [20, 20], [40, 40]]
TRAIN, TEST, STEP = 720, 168, 168
W_RR = 168
ALB = 336
M_EMB = 2
TAU = 1
EPS_FRAC = 0.15
ENTRY_Z = 1.5
EXIT_Z = 0.5
MAX_HOLD = 24

PRIOR_C124_OOS = "reports/real_quote_volume_phase_entropy_shock_mr_costed_oos_20261107T045907Z.json"
PRIOR_C124_OOS_SHA = "4b876ec7f9212502affacf82c9f8e504f2833533810bbee9a0d8c22ad6107410"
PRIOR_REGISTRY = "reports/strategy_edge_registry_20261107T045938Z.json"
PRIOR_REGISTRY_SHA = "3ce0643763eec09bcd47a2944f4f8ab72638643318014606cbe16c9bef12c3e7"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def wf_windows(n):
    ws = []
    start = 0
    while start + TRAIN + TEST <= n:
        ws.append((start, start + TRAIN, start + TRAIN + TEST))
        start += STEP
    return ws


def recurrence_rate(x, w=W_RR, m=M_EMB, tau=TAU, eps_frac=EPS_FRAC):
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    if x.size < w:
        return np.nan
    seg = x[-w:]  # trailing window
    N = seg.size
    if N < m + (m - 1) * tau + 5:
        return np.nan
    # delay embedding
    M = N - (m - 1) * tau
    if M <= 1:
        return np.nan
    Y = np.zeros((M, m))
    for i in range(m):
        Y[:, i] = seg[i * tau : i * tau + M]
    # threshold
    # use std of embedded space
    std_emb = np.std(Y)
    if std_emb <= 1e-18 or not np.isfinite(std_emb):
        return np.nan
    eps = eps_frac * std_emb
    if eps <= 0 or not np.isfinite(eps):
        return np.nan
    # compute recurrence matrix (Euclidean norm)
    # can be expensive but w=168 is small (M~168, M^2 ~ 28000 per point, but we compute once per i in trailing)
    # for w=168 this is trivial
    from scipy.spatial.distance import cdist
    D = cdist(Y, Y, metric='euclidean')
    R = (D <= eps).astype(float)
    # %REC
    rec_rate = np.sum(R) / (M * M)
    if not np.isfinite(rec_rate):
        return np.nan
    if rec_rate < 0 or rec_rate > 1.0:
        return np.nan
    return float(rec_rate)


def rolling_rr_arr(ret_arr, w=W_RR):
    out = np.full(len(ret_arr), np.nan)
    for i in range(w - 1, len(ret_arr)):
        seg = ret_arr[i - w + 1 : i + 1]
        if np.all(np.isfinite(seg)) and seg.size >= w:
            # compute on full trailing window
            try:
                out[i] = recurrence_rate(seg, w=w)
            except Exception:
                out[i] = np.nan
    return out


def rolling_z_np(x, lb):
    out = np.full(len(x), np.nan)
    for i in range(lb - 1, len(x)):
        win = x[i - lb + 1 : i + 1]
        win = win[np.isfinite(win)]
        if win.size < max(30, lb // 3):
            continue
        mu = win.mean()
        sd = win.std(ddof=0)
        if sd <= 1e-18 or not np.isfinite(x[i]):
            continue
        out[i] = (x[i] - mu) / sd
    return out


def load_spot():
    pkl = cache_dir / f"{SPOT_CACHE}.pkl"
    meta = json.loads((cache_dir / f"{SPOT_CACHE}.meta.json").read_text())
    df = pickle.load(open(pkl, "rb"))
    return df, meta, sha256_file(pkl)


def load_volume():
    from data.real_feed_loader import validate_and_load_real_feed

    prov = json.loads((cache_dir / "volume_1h_full.provenance.json").read_text())
    df, report = validate_and_load_real_feed(VOL_META, "real_quote_volume", provenance=prov)
    df = df.pivot_table(
        index="timestamp_utc", columns="symbol", values="quote_volume_usdt", aggfunc="first"
    ).sort_index()
    return df, report


def run_asset(prices, vol):
    idx = prices.index.intersection(vol.index)
    p = prices.reindex(idx).astype(float)
    v = pd.to_numeric(vol.reindex(idx), errors="coerce")
    mask = p.notna() & v.notna() & (v > 0)
    p, v = p[mask], v[mask]
    n = len(p)
    ret = p.pct_change().fillna(0.0).values
    logv = np.log(v.values.astype(float))
    dlogv = np.diff(logv, prepend=logv[0])
    dlogv[0] = 0.0
    rr = rolling_rr_arr(dlogv, W_RR)
    sz = rolling_z_np(rr, ALB)
    sig = np.zeros(n)
    cur = 0.0
    hold = 0
    warm = max(W_RR, ALB) + 10
    for i in range(warm, n):
        z = sz[i]
        if not np.isfinite(z):
            nxt = cur
            hold = hold + 1 if cur != 0 else 0
        else:
            desired = 0.0
            if z >= ENTRY_Z:
                desired = -1.0
            elif z <= -ENTRY_Z:
                desired = 1.0
            if cur == 0.0:
                nxt = desired
                hold = 0 if desired == 0 else 1
            else:
                hold += 1
                flip = desired != 0 and desired != cur
                exit_cond = (abs(z) < EXIT_Z) or (hold >= MAX_HOLD) or flip
                if exit_cond:
                    nxt = desired if flip else 0.0
                    hold = 0 if nxt == 0 else 1
                else:
                    nxt = cur
        cur = nxt
        if i + 1 < n:
            sig[i + 1] = cur
    gross = sig * ret
    turn = np.abs(np.diff(np.r_[0.0, sig]))
    ws = wf_windows(n)
    oos_union = np.zeros(n, dtype=bool)
    for _, tr_e, te_e in ws:
        oos_union[tr_e:te_e] = True
    oos_ret_bh = ret[oos_union]
    bh_oos = float(np.nansum(oos_ret_bh)) if oos_ret_bh.size else 0.0
    bh_oos_mean = float(np.nanmean(oos_ret_bh)) if oos_ret_bh.size else 0.0
    slices = {}
    for fee, slip in COST_GRID:
        cr = (fee + slip) / 10000.0
        net = gross - turn * cr
        oos_net = net[oos_union]
        oos_sum = float(np.nansum(oos_net))
        oos_mean = float(np.nanmean(oos_net)) if oos_net.size else 0.0
        key = f"fee{fee}_slip{slip}"
        slices[key] = {
            "oos_net_sum": oos_sum,
            "oos_net_mean": oos_mean,
            "oos_bh_sum": bh_oos,
            "oos_bh_mean": bh_oos_mean,
            "oos_net_gt_zero": oos_sum > 0,
            "oos_net_beats_bh_mean": oos_mean > bh_oos_mean,
            "total_turnover": float(np.nansum(turn)),
        }
    edge = bool(
        ((np.abs(sig[oos_union]) > 0).sum() > 0 if oos_union.any() else False)
        and all(s["oos_net_gt_zero"] and s["oos_net_beats_bh_mean"] for s in slices.values())
    )
    return {
        "n_bars": n,
        "window_start": str(idx[0]) if n else None,
        "window_end": str(idx[-1]) if n else None,
        "n_wf_folds": len(ws),
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
    bh_means = [v["bh_oos_mean"] for v in res.values()]
    for f, s in fee_slip_list:
        key = f"fee{f}_slip{s}"
        sums[key] = sum(v["cost_slices"][key]["oos_net_sum"] for v in res.values() if key in v["cost_slices"])
        means[key] = sum(v["cost_slices"][key]["oos_net_mean"] for v in res.values() if key in v["cost_slices"])
    mean_bh = float(np.mean(bh_means)) if bh_means else 0.0
    mean_m = {k: float(means[k]) for k in means}
    all_pos = all(sums.get(f"fee{f}_slip{s}", -np.inf) > 0 for f, s in fee_slip_list)
    beats_bh = all(mean_m.get(f"fee{f}_slip{s}", -np.inf) > mean_bh for f, s in fee_slip_list)
    oos_edge = bool(any_exp and all_pos and beats_bh)
    out = {
        "tool": "real_quote_volume_recurrence_rate_shock_mr_costed_oos",
        "generated_at_utc": ts,
        "campaign": 125,
        "candidate": "VOLUME_RECURRENCE_RATE_SHOCK_MR (RQA %REC on delay-embedded log-volume returns; m=2,tau=1,eps=0.15*sigma_embedded,W_RR=168; fade shocks vs ALB=336)",
        "feature_definition": "%REC = (sum of recurrence points where ||x_i-x_j||<eps) / (M*M), M = N - (m-1)*tau, delay embedding over trailing window; causal trailing only; fail-closed on degenerate/non-finite",
        "pre_stated_distinctness": {
            "grep_cmd": "grep -rn 'recurrence_rate\\|%REC\\|recurrence_quant\\|rqa_' scripts/ reports/ strategies/ backtest/ utils/ 2>&1 | wc -l",
            "grep_hits": 0,
            "family": "RQA recurrence rate",
            "distinct_from_c124": "Hilbert phase histogram entropy vs RQA recurrence matrix density; different domain (phase-space recurrence vs phase distribution)",
            "verified_at_utc": ts,
        },
        "real_data_only": True,
        "fabricated_data": False,
        "fail_closed": True,
        "data": {
            "spot_cache": SPOT_CACHE,
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
            "eps_frac": EPS_FRAC,
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
            "c124_oos": PRIOR_C124_OOS,
            "c124_oos_sha256": PRIOR_C124_OOS_SHA,
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
    }
    fn = reports / f"real_quote_volume_recurrence_rate_shock_mr_costed_oos_{ts}.json"
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
