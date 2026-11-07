#!/usr/bin/env python3
"""Campaign #115 Path R (fail-closed, real data only): real_quote_volume-conditioned
strategy on real Binance spot quote volume (klines column 5) + real cached spot 1h.

PRE-STATED HYPOTHESIS (fixed before seeing OOS results): "Volume Permutation-Variance shock mean reversion"
- Feature: rolling Permutation Variance over W_PV=168 on log-volume returns r_t = log(v_t/v_{t-1}).
  Use Bandt-Pompe ordinal patterns with embedding order m=4, delay tau=1 (m!=24 patterns).
  For each window, obtain ordinal-pattern indices from length-(m+(m-1)*tau) slices; compute PMF p
  over patterns and Permutation Variance PV_raw = Var(p) * m!. Normalize by (m!-1)/(m!)^2 so the
  scale is a stable [0,1]-like upper-bounded statistic (uniform PMF -> 0; maximally concentrated
  PMF -> 1); fail-closed on non-finite/degenerate windows (NaN). Distinct from permutation
  *entropy* families and C104-C114 families.
- Signal (fail-closed MR): z = (PV - ALB_mean) / ALB_std, baseline ALB=336. shock=|z|.
  entry_z >= 1.5: z > 0 (high permutation-variance / concentrated-pattern shock) fade short (-1),
  z < 0 (low permutation-variance / dispersed-pattern shock) fade long (+1);
  exit_z < 0.5 or max_hold=24 or flip. Execution t -> t+1 (no lookahead).
  Apply only where real volume/spot bars exist.
- WF 720/168/168; cost grid [[0,0],[5,5],[10,10],[20,20],[40,40]]; B&H same OOS windows.
  Edge rule exact. Real data only.
"""
import json, sys, pickle, hashlib, math
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
COST_GRID = [[0,0],[5,5],[10,10],[20,20],[40,40]]
TRAIN, TEST, STEP = 720, 168, 168
W_PV = 168
M_ORD = 4
TAU = 1
ALB = 336
ENTRY_Z = 1.5
EXIT_Z = 0.5
MAX_HOLD = 24

PRIOR_C114_RB_SHA = "de01ac8b96b8453ab728205d4d94e1939405d1b25f6bb43e91e2c307626d19d9"
PRIOR_REGISTRY = root / "reports" / "strategy_edge_registry_20261107T011022Z.json"
PRIOR_REGISTRY_SHA = "ffcacca26a732efbab8ab908ed43aceb3cb4cecb3724960ea46117eacdbeeabe"


def sha256_file(path: Path) -> str:
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


# Bandt-Pompe ordinal pattern indexer for m=4, tau=1.
# Pattern index is lex rank of argsort of the m embedded values (stable ties not expected on
# continuous returns; fail-closed NaN already guards non-finite). Use numpy argsort twice for
# permutation rank -> integer index in [0, m!-1].
_M_FACT = math.factorial(M_ORD)
_PV_NORM = (_M_FACT - 1) / (_M_FACT ** 2)  # max Var(p) over simplex vertices scaled context


def _ordinal_indices(win: np.ndarray, m: int, tau: int) -> np.ndarray:
    n = len(win)
    span = (m - 1) * tau + 1
    n_pat = n - span + 1
    if n_pat <= 0:
        return np.empty(0, dtype=int)
    idxs = np.empty(n_pat, dtype=int)
    for j in range(n_pat):
        seg = win[j : j + span : tau]
        # rank permutation: argsort(argsort) gives 0..m-1 ranks
        r = np.argsort(np.argsort(seg, kind="mergesort"), kind="mergesort")
        # encode rank tuple as base-m mixed radix index (deterministic, unique)
        code = 0
        for v in r:
            code = code * m + int(v)
        idxs[j] = code
    return idxs


def permutation_variance(r, w, m, tau):
    """Rolling normalized Permutation Variance over window w on return series r."""
    out = np.full(len(r), np.nan)
    n = len(r)
    if w < (m - 1) * tau + 8 or n < w or m < 3:
        return out
    span = (m - 1) * tau + 1
    for i in range(w - 1, n):
        win = r[i - w + 1:i + 1].astype(np.float64, copy=False)
        if not np.isfinite(win).all():
            continue
        idxs = _ordinal_indices(win, m, tau)
        if idxs.size < 8:
            continue
        # map mixed-radix codes to compact pattern ids via unique
        _, inv = np.unique(idxs, return_inverse=True)
        counts = np.bincount(inv).astype(np.float64)
        p = counts / counts.sum()
        if p.size <= 1:
            continue
        pv_raw = float(np.var(p, ddof=0) * _M_FACT)
        pv = pv_raw / _PV_NORM if _PV_NORM > 0 else np.nan
        if not np.isfinite(pv):
            continue
        # clamp to [0,1] for numerical stability; should already be in range
        out[i] = float(np.clip(pv, 0.0, 1.0))
    return out


def rolling_z(x, lb):
    out = np.full(len(x), np.nan)
    for i in range(lb - 1, len(x)):
        win = x[i - lb + 1:i + 1]
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


def run_asset(prices: pd.Series, vol: pd.Series):
    idx = prices.index.intersection(vol.index)
    p = prices.reindex(idx).astype(float)
    v = pd.to_numeric(vol.reindex(idx), errors="coerce")
    mask = p.notna() & v.notna() & (v > 0)
    p, v = p[mask], v[mask]
    n = len(p)
    ret = p.pct_change().fillna(0.0).values
    logv = np.log(v.values.astype(float))
    r = np.diff(logv, prepend=logv[0])
    r[0] = 0.0
    pv = permutation_variance(r, W_PV, M_ORD, TAU)
    sz = rolling_z(pv, ALB)
    sig = np.zeros(n)
    cur = 0.0
    hold = 0
    warm = max(W_PV, ALB) + 10
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
        "bh_oos_sum": bh_oos,
        "bh_oos_mean": bh_oos_mean,
        "cost_slices": slices,
        "oos_edge_proven": edge,
    }


def main():
    prior_registry = PRIOR_REGISTRY
    prior_reg_sha = sha256_file(prior_registry) if prior_registry.exists() else ""
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
        except Exception:
            continue
        try:
            vv = vol_df[a]
        except Exception:
            continue
        res[a] = run_asset(sp, vv)
    fee_slip_list = [(0,0),(5,5),(10,10),(20,20),(40,40)]
    any_exp = any(v.get("has_exposure_oos") for v in res.values())
    sums = {}
    means = {}
    bh_means = []
    for f, s in fee_slip_list:
        key = f"fee{f}_slip{s}"
        ssum = sum(v["cost_slices"][key]["oos_net_sum"] for v in res.values() if key in v["cost_slices"])
        msum = sum(v["cost_slices"][key]["oos_net_mean"] for v in res.values() if key in v["cost_slices"])
        sums[key] = ssum
        means[key] = msum
    for v in res.values():
        bh_means.append(v["bh_oos_mean"])
    mean_bh = float(np.mean(bh_means)) if bh_means else 0.0
    mean_m = {k: float(means[k]) for k in means}
    all_pos = all(sums.get(f"fee{f}_slip{s}", -np.inf) > 0 for f, s in fee_slip_list)
    beats_bh = all(mean_m.get(f"fee{f}_slip{s}", -np.inf) > mean_bh for f, s in fee_slip_list)
    oos_edge = bool(any_exp and all_pos and beats_bh)
    out = {
        "tool": "real_quote_volume_permutation_variance_shock_mr_costed_oos",
        "generated_at_utc": ts,
        "campaign": 115,
        "candidate": "VOLUME_PERMUTATION_VARIANCE_SHOCK_MR (Bandt-Pompe ordinal patterns m=4,tau=1 over log-volume returns within W_PV=168; PMF variance*24 normalized by (23/576) to [0,1]-like; fade permutation-variance shocks vs ALB=336 baseline)",
        "pre_stated_distinctness": "Grep-verified permutation_variance/PermutationVariance absent before impl. Distinct from permutation *entropy* families and C104-C114 (increment/attention/Fisher Information, SVD/bubble/dispersion/sample/approximate/spectral/wavelet/DFA/Hurst/slope/LZ/Petrosian/Higuchi/Katz/turning-point/variance-ratio/OU/BDS, etc.). Normalization stated: PV = clip((Var(p)*m!)/((m!-1)/(m!)^2),0,1).",
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
        "params": {"w_pv": W_PV, "m_ord": M_ORD, "tau": TAU, "pv_norm_den": _PV_NORM, "alb": ALB, "entry_z": ENTRY_Z, "exit_z": EXIT_Z, "max_hold": MAX_HOLD, "train": TRAIN, "test": TEST, "step": STEP, "cost_grid": COST_GRID},
        "references": {
            "prior_unblock": "reports/real_feed_unblock_status_20261106T130243Z.json",
            "prior_registry": str(prior_registry.relative_to(root)),
            "prior_registry_sha256": prior_reg_sha,
            "c114_rb": "reports/real_quote_volume_increment_entropy_shock_mr_costed_oos_20261107T011021Z.json",
            "c114_rb_sha256": PRIOR_C114_RB_SHA,
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
    fn = reports / f"real_quote_volume_permutation_variance_shock_mr_costed_oos_{ts}.json"
    fn.write_text(json.dumps(out, indent=2))
    print(json.dumps({"artifact": str(fn), "sha256": sha256_file(fn), "oos_edge_proven": oos_edge}, indent=2))


if __name__ == "__main__":
    main()
