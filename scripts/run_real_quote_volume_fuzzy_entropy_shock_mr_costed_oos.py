#!/usr/bin/env python3
"""Campaign #121 Path R-B (fail-closed, real data only): real_quote_volume-conditioned
strategy on real Binance spot quote volume (klines column 5) + real cached spot 1h.

PRE-STATED HYPOTHESIS (fixed before seeing OOS results): "Volume Fuzzy-Entropy shock mean reversion"
- Feature: Fuzzy Entropy (FuzzyEn; Chen et al. 2007/2009) on log-volume returns
  r_t = log(v_t/v_{t-1}) over rolling window W_FE=168. Embedding m=2, delay=1.
  Distance d_{ij}^m = Chebyshev(max-norm) between demeaned m-vectors
  x_i = [r_i - mu_i, ..., r_{i+m-1} - mu_i]. Fuzzy similarity
  A_{ij}^m = exp(-(d_{ij}^m / r)^n), r = R_SCALE*std(window), n=2 (fuzzy power).
  phi^m = mean_{i!=j} A_{ij}^m (self-matches excluded). FuzzyEn = ln(phi^m) - ln(phi^(m+1)).
- Signal: shock = z(FuzzyEn) relative to longer baseline ALB=336; fade extremes.
  z >= ENTRY_Z (high irregularity / less predictable volume structure) -> short (-1);
  z <= -ENTRY_Z (high regularity / more predictable) -> long (+1);
  exit if |z| < EXIT_Z or max_hold=24 or flip.
- Execution shift t->t+1; walk-forward rolling 720/168/168; cost grid
  [[0,0],[5,5],[10,10],[20,20],[40,40]]; edge rule exact: oos_edge_proven true IFF
  exposure>0 AND all cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net on
  same WF windows. Real data only; no proxies/fabrication; grep-verified distinct.
Distinctness (pre-stated, grep-verified): no fuzzy_entropy/fuzzyen/FuzzyEn in scripts/
or reports/ before implementation (grep check Step 0). Distinct from C102 Approximate
Entropy/ApEn (hard Heaviside tolerance, includes self-matches in template counts) and
C106/C120 Sample/Multiscale Sample Entropy (hard tolerance, self-matches excluded, SampEn
= -ln(A/B)); FuzzyEn uses continuous exponential membership exp(-(d/r)^n) on demeaned
vectors, a different similarity functional (not monotonic transform of ApEn/SampEn/MSE).
Distinct from all C104–C120 lineage families (wavelet entropy, Hurst RS, sample/multiscale
sample entropy, SVD entropy, Fisher Information, attention entropy, increment entropy,
permutation variance, fluctuation complexity, range entropy, cumulative residual entropy,
dispersion entropy) and other prior families (spectral, permutation entropy, bubble, slope,
DFA, Higuchi/Petrosian/Katz FD, LZ76, Hjorth/TKEO, ZCR, OU halflife, variance ratio, etc.).
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
W_FE = 168
ALB = 336
M = 2
R_SCALE = 0.2
N_FUZZY = 2.0
ENTRY_Z = 1.5
EXIT_Z = 0.5
MAX_HOLD = 24

PRIOR_C120_OOS = "reports/real_quote_volume_multiscale_sample_entropy_shock_mr_costed_oos_20261107T030455Z.json"
PRIOR_C120_OOS_SHA = "53103aa54e3f937c42904a6e3aaa1e2b3a6bb1f5562cd89d551fa77699e9b382"
PRIOR_REGISTRY = "reports/strategy_edge_registry_20261107T030825Z.json"
PRIOR_REGISTRY_SHA = "0b5aa8bd669e31480ffdc5ff0b34fd5f328e914fc9e0854adab538f54147836a"


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


def _phi_fuzzy(x: np.ndarray, m: int, r: float, n_pow: float) -> float:
    """Mean fuzzy similarity phi^m with self-matches excluded; demeaned vectors, Chebyshev distance."""
    N = x.size
    T = N - m
    if T <= 1:
        return np.nan
    X = np.lib.stride_tricks.sliding_window_view(x, m)[:T].astype(float)
    X = X - X.mean(axis=1, keepdims=True)
    total = 0.0
    count = 0
    for i in range(T - 1):
        d = np.max(np.abs(X[i + 1 :] - X[i]), axis=1)
        a = np.exp(-np.power(d / r, n_pow))
        total += float(a.sum())
        count += a.size
    if count == 0:
        return np.nan
    val = total / count
    if not np.isfinite(val) or val <= 0:
        return np.nan
    return val


def fuzzy_entropy(x: np.ndarray, m: int = M, r_scale: float = R_SCALE, n_pow: float = N_FUZZY) -> float:
    """FuzzyEn(m, r, n) = ln(phi^m) - ln(phi^(m+1)), fail-closed NaN on degenerate/non-finite."""
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    if x.size < m + 20:
        return np.nan
    sd = np.std(x, ddof=0)
    if sd <= 1e-18 or not np.isfinite(sd):
        return np.nan
    r = r_scale * sd
    phi_m = _phi_fuzzy(x, m, r, n_pow)
    phi_m1 = _phi_fuzzy(x, m + 1, r, n_pow)
    if not (np.isfinite(phi_m) and np.isfinite(phi_m1) and phi_m > 0 and phi_m1 > 0):
        return np.nan
    val = float(np.log(phi_m) - np.log(phi_m1))
    if not np.isfinite(val):
        return np.nan
    return val


def rolling_fuzzy_entropy(r: np.ndarray, w: int = W_FE, m: int = M, r_scale: float = R_SCALE, n_pow: float = N_FUZZY) -> np.ndarray:
    out = np.full(len(r), np.nan)
    for i in range(w - 1, len(r)):
        win = r[i - w + 1 : i + 1]
        if not np.isfinite(win).all():
            continue
        out[i] = fuzzy_entropy(win, m=m, r_scale=r_scale, n_pow=n_pow)
    return out


def rolling_z(x, lb):
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


def run_asset(prices: pd.Series, vol: pd.Series):
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
    fe = rolling_fuzzy_entropy(dlogv, W_FE, M, R_SCALE, N_FUZZY)
    sz = rolling_z(fe, ALB)
    sig = np.zeros(n)
    cur = 0.0
    hold = 0
    warm = max(W_FE, ALB) + 10
    for i in range(warm, n):
        z = sz[i]
        if not np.isfinite(z):
            nxt = cur
            hold = hold + 1 if cur != 0 else 0
        else:
            desired = 0.0
            if z >= ENTRY_Z:
                desired = -1.0  # high irregularity shock -> fade short
            elif z <= -ENTRY_Z:
                desired = 1.0  # high regularity shock -> fade long
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
            sig[i + 1] = cur  # t -> t+1 execution
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
        except Exception:
            continue
        try:
            vv = vol_df[a]
        except Exception:
            continue
        res[a] = run_asset(sp, vv)
    fee_slip_list = [(0, 0), (5, 5), (10, 10), (20, 20), (40, 40)]
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
        "tool": "real_quote_volume_fuzzy_entropy_shock_mr_costed_oos",
        "generated_at_utc": ts,
        "campaign": 121,
        "candidate": "VOLUME_FUZZY_ENTROPY_SHOCK_MR (Fuzzy Entropy Chen et al. 2007/2009 on log-volume returns, W_FE=168, m=2, r=0.2*std, n=2, demeaned m-vectors, Chebyshev distance, A=exp(-(d/r)^n), self-matches excluded, FuzzyEn=ln(phi^m)-ln(phi^(m+1)), fade shocks vs ALB=336)",
        "pre_stated_distinctness": "Grep-verified absent before impl: fuzzy_entropy/fuzzyen/FuzzyEn not present in scripts/ or reports/. Distinct from C102 Approximate Entropy/ApEn (hard Heaviside tolerance, includes self-matches) and C106/C120 Sample/Multiscale Sample Entropy (hard tolerance, SampEn=-ln(A/B), C120 coarse-grains tau={2,3,5}): FuzzyEn uses continuous exponential membership exp(-(d/r)^n) on demeaned vectors (max-norm), a different similarity functional not monotonic with ApEn/SampEn/MSE. Distinct from C104-C120 lineage (wavelet entropy, Hurst RS, sample/multiscale sample entropy, SVD entropy, Fisher Information, attention entropy, increment entropy, permutation variance, fluctuation complexity, range entropy, cumulative residual entropy, dispersion entropy) and prior families (spectral, permutation entropy, bubble, slope, DFA, Higuchi/Petrosian/Katz FD, LZ76, Hjorth/TKEO, ZCR, OU halflife, variance ratio).",
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
            "w_fe": W_FE,
            "alb": ALB,
            "m_emb": M,
            "r_scale": R_SCALE,
            "n_fuzzy": N_FUZZY,
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
            "c120_oos": PRIOR_C120_OOS,
            "c120_oos_sha256": PRIOR_C120_OOS_SHA,
            "c106_sampen": "reports/real_quote_volume_sample_entropy_shock_mr_costed_oos_20261106T225102Z.json",
            "c102_apen": "reports/real_quote_volume_approximate_entropy_shock_mr_costed_oos_20261106T201839Z.json",
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
    fn = reports / f"real_quote_volume_fuzzy_entropy_shock_mr_costed_oos_{ts}.json"
    fn.write_text(json.dumps(out, indent=2))
    print(json.dumps({"artifact": str(fn), "sha256": sha256_file(fn), "oos_edge_proven": oos_edge}, indent=2))


if __name__ == "__main__":
    main()
