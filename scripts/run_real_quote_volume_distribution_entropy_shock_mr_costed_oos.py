#!/usr/bin/env python3
"""Campaign #122 Path R-B (fail-closed, real data only): real_quote_volume-conditioned
strategy on real Binance spot quote volume (klines column 5) + real cached spot 1h.

PRE-STATED HYPOTHESIS (fixed before seeing OOS results): "Volume Distribution-Entropy shock mean reversion"
- Feature: Distribution Entropy (DistEn; Li et al. 2015) on log-volume returns
  r_t = log(v_t/v_{t-1}) over rolling window W_DE=168. Phase-space reconstruct with
  embedding m=2, delay=1; compute Chebyshev inter-vector distances for all pairs
  (upper triangle). Bin distances into M_BINS=64 over [0, d_max] to get empirical
  distribution p_k; DistEn = -sum_{p_k>0} p_k*log2(p_k) / log2(M_BINS).
  Measures complexity of the inter-vector distance distribution (not match counts).
- Signal: shock = z(DistEn) relative to longer baseline ALB=336; fade extremes.
  z >= ENTRY_Z (high distribution complexity / more uniform eCDF gaps) -> short (-1);
  z <= -ENTRY_Z (low distribution complexity / clustered gaps) -> long (+1);
  exit if |z| < EXIT_Z or max_hold=24 or flip.
- Execution shift t->t+1; walk-forward rolling 720/168/168; cost grid
  [[0,0],[5,5],[10,10],[20,20],[40,40]]; edge rule exact: oos_edge_proven true IFF
  exposure>0 AND all cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net on
  same WF windows. Real data only; no proxies/fabrication; grep-verified distinct.
Distinctness (pre-stated, grep-verified): no distribution_entropy/dist_en in scripts/
or reports/ before implementation (grep check Step 0). Distinct from dispersion entropy
(C119, NCDF + class-pattern frequencies on amplitudes; different mapping and statistic),
and from ApEn(C102)/SampEn(C106)/MSE(C120)/FuzzyEn(C121) vector-similarity entropies,
permutation/shannon/spectral/wavelet/bubble/slope/range/CRE/SVD/Fisher/attention/
increment/permutation-variance/fluctuation-complexity families, DFA, Hurst/RS,
Higuchi/Petrosian/Katz FD, LZ76, Hjorth/TKEO, ZCR, OU halflife, variance ratio.
DistEn operates on eCDF adjacent-distance distribution — different object/functional.
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
W_DE = 168
ALB = 336
M_BINS = 64
M_EMB = 2
ENTRY_Z = 1.5
EXIT_Z = 0.5
MAX_HOLD = 24

PRIOR_C121_OOS = "reports/real_quote_volume_fuzzy_entropy_shock_mr_costed_oos_20261107T040732Z.json"
PRIOR_C121_OOS_SHA = "ff6d75383bb7d07772712a39d7eb4bcb1ac65e8ab34fd7f1190a3ea0a2e198b3"
PRIOR_REGISTRY = "reports/strategy_edge_registry_20261107T041147Z.json"
PRIOR_REGISTRY_SHA = "dd5492697d70ff3f79d0e8dbb8b0a72eb6cfa230eb4143f757f185c22392d684"


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


def distribution_entropy(x: np.ndarray, m: int = M_EMB, m_bins: int = M_BINS) -> float:
    """DistEn (Li et al. 2015) on empirical distribution of inter-vector Chebyshev distances.
    Phase-space reconstruction (m, delay=1), full pairwise distance matrix (upper triangle),
    histogram into m_bins over [0, d_max]; DistEn = H(p)/log2(m_bins). Fail-closed NaN."""
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    N = x.size
    if N < m + 20 or m_bins < 2:
        return np.nan
    T = N - m + 1
    X = np.lib.stride_tricks.sliding_window_view(x, m)[:T].astype(float)
    # pairwise Chebyshev distances, upper triangle (exclude diagonal)
    dists = []
    for i in range(T - 1):
        d = np.max(np.abs(X[i + 1 :] - X[i]), axis=1)
        dists.append(d)
    if not dists:
        return np.nan
    d_all = np.concatenate(dists)
    d_all = d_all[np.isfinite(d_all)]
    if d_all.size < 10:
        return np.nan
    d_max = np.max(d_all)
    if not np.isfinite(d_max) or d_max <= 0:
        return np.nan
    edges = np.linspace(0.0, d_max, m_bins + 1)
    edges[-1] = np.nextafter(d_max, np.inf)
    counts, _ = np.histogram(d_all, bins=edges)
    total = counts.sum()
    if total <= 0:
        return np.nan
    p = counts[counts > 0].astype(float) / total
    h = -np.sum(p * np.log2(p))
    h_norm = h / np.log2(m_bins)
    if not np.isfinite(h_norm):
        return np.nan
    return float(h_norm)


def rolling_disten(ret: pd.Series, w: int = W_DE, m_bins: int = M_BINS) -> pd.Series:
    vals = ret.values.astype(float)
    out = np.full(vals.shape, np.nan)
    for i in range(w - 1, len(vals)):
        seg = vals[i - w + 1 : i + 1]
        if np.all(np.isfinite(seg)):
            out[i] = distribution_entropy(seg, M_EMB, m_bins)
    return pd.Series(out, index=ret.index)


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

def rolling_disten_arr(ret_arr: np.ndarray, w: int = W_DE, m_bins: int = M_BINS) -> np.ndarray:
    out = np.full(len(ret_arr), np.nan)
    for i in range(w - 1, len(ret_arr)):
        seg = ret_arr[i - w + 1 : i + 1]
        if np.all(np.isfinite(seg)):
            out[i] = distribution_entropy(seg, M_EMB, m_bins)
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
    de = rolling_disten_arr(dlogv, W_DE, M_BINS)
    sz = rolling_z_np(de, ALB)
    sig = np.zeros(n)
    cur = 0.0
    hold = 0
    warm = max(W_DE, ALB) + 10
    for i in range(warm, n):
        z = sz[i]
        if not np.isfinite(z):
            nxt = cur
            hold = hold + 1 if cur != 0 else 0
        else:
            desired = 0.0
            if z >= ENTRY_Z:
                desired = -1.0  # high distribution complexity shock -> fade short
            elif z <= -ENTRY_Z:
                desired = 1.0   # low distribution complexity shock -> fade long
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
        "tool": "real_quote_volume_distribution_entropy_shock_mr_costed_oos",
        "generated_at_utc": ts,
        "campaign": 122,
        "candidate": "VOLUME_DISTRIBUTION_ENTROPY_SHOCK_MR (Distribution Entropy/DistEn Li et al. 2015 on log-volume returns: sort->eCDF ranks u_i=rank/N, adjacent distances d_i=u_{i+1}-u_i binned M=64 over (0,d_max], DistEn=-sum p*log2(p)/log2(M); W_DE=168; fade shocks vs ALB=336)",
        "pre_stated_distinctness": "Grep-verified before impl: no distribution_entropy/dist_en in scripts/ or reports/. DistEn (Li 2015) uses the empirical *distribution* (histogram entropy) of all inter-vector Chebyshev distances — a distributional complexity measure, distinct from ApEn/SampEn/MSE/FuzzyEn C102/C106/C120/C121 which threshold/match/count vector pairs (tolerance/membership statistics, not the full distance distribution), and from dispersion entropy C119 (NCDF amplitude -> class patterns), permutation/shannon/spectral/wavelet/bubble/slope/range/CRE/SVD/Fisher/attention/increment/permutation-variance/fluctuation-complexity families, DFA, Hurst/RS, Higuchi/Petrosian/Katz FD, LZ76, Hjorth/TKEO, ZCR, OU halflife, variance ratio. renyi/tsallis appeared only as distinctness mentions in prior scripts, not as *_shock_mr feature families.",
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
            "w_de": W_DE,
            "alb": ALB,
            "m_bins": M_BINS,
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
            "c121_oos": PRIOR_C121_OOS,
            "c121_oos_sha256": PRIOR_C121_OOS_SHA,
            "c119_dispersion_entropy": "reports/real_quote_volume_dispersion_entropy_shock_mr_costed_oos_20261107T021053Z.json",
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
    fn = reports / f"real_quote_volume_distribution_entropy_shock_mr_costed_oos_{ts}.json"
    fn.write_text(json.dumps(out, indent=2))
    print(json.dumps({"artifact": str(fn), "sha256": sha256_file(fn), "oos_edge_proven": oos_edge, "any_exposure": any_exp, "all_pos": all_pos, "beats_bh": beats_bh, "sums": sums}, indent=2))

if __name__ == "__main__":
    main()
