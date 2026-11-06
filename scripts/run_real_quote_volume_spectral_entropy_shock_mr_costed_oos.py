#!/usr/bin/env python3
"""Campaign #103 Path R (fail-closed, real data only): real_quote_volume-conditioned
strategy on real Binance spot quote volume (klines column 5) + real cached spot 1h.

PRE-STATED HYPOTHESIS (fixed before seeing OOS results): "Volume Spectral-Entropy shock mean reversion"
- Feature: Spectral (power spectral density) entropy of log-volume changes dlogv on
  rolling windows. Compute PSD via periodogram/Welch (periodogram on window), normalize
  to probability distribution over frequency bins, compute Shannon entropy H = -sum p_i log p_i
  (or normalized). Spectral entropy is frequency-domain entropy, distinct from
  time-domain entropies (ApEn/SampleEn/Shannon/Permutation/Renyi block-frequency entropy),
  DFA/C101, Hurst/RS, Higuchi/Katz/Petrosian FD, LZ76, Hjorth/TKEO, ZCR/C100.
- Signal: on rolling window compute spectral entropy; shock = |z(spectral_entropy)|
  relative to longer baseline; fade extremes (high spectral entropy = more spread across
  frequencies/unpredictable in freq domain -> short; low spectral entropy = concentrated
  power -> long) similar to ApEn logic but freq-domain.
- Execution shift t->t+1; walk-forward rolling 720/168/168; cost grid
  [[0,0],[5,5],[10,10],[20,20],[40,40]]; edge rule exact: oos_edge_proven true IFF
  exposure>0 AND all cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net on
  same WF windows. Real data only; no proxies/fabrication; grep-verified distinct.
"""
import json, os, pickle, hashlib, math
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
import pandas as pd
from scipy import signal

root = Path(__file__).resolve().parent.parent
cache_dir = root / "data" / "cache"
reports = root / "reports"
reports.mkdir(exist_ok=True)
ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

SPOT_CACHE = "0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7"
VOL_META = cache_dir / "volume_1h_full.meta.json"
COST_GRID = [[0,0],[5,5],[10,10],[20,20],[40,40]]
TRAIN, TEST, STEP = 720, 168, 168
W_SPEC = 168  # spectral window
ALB = 336     # baseline
ENTRY_Z = 1.5
EXIT_Z = 0.5
MAX_HOLD = 24
MIN_OBS = 168
PRIOR_C100_RB_SHA = "c3caf4dfdf66fedfb522f61233172c541f6cae7852c78173c6a41156bbc55951"
PRIOR_C101_RB_SHA = "41dc8fc858acb19e6c36679359c6a304ea3dfb24477332c9b12d4bb4a01265c7"
PRIOR_C102_RB_SHA = "0a344a04425f075fa3fd2f3122091d747e9243edf0842488f8497d905782cc41"


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


def spectral_entropy(x):
    """Power spectral density Shannon entropy (normalized over positive freqs)."""
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    n = x.size
    if n < 32:
        return np.nan
    # Remove mean
    x0 = x - np.mean(x)
    # Periodogram
    try:
        f, Pxx = signal.periodogram(x0, fs=1.0)
    except Exception:
        return np.nan
    # Use positive frequencies (exclude DC)
    if len(Pxx) < 2:
        return np.nan
    P = Pxx[1:]  # skip DC
    Psum = np.sum(P)
    if Psum <= 0 or not np.isfinite(Psum):
        return np.nan
    p = P / Psum
    # Avoid log(0)
    p = p[p > 0]
    if p.size == 0:
        return np.nan
    H = -np.sum(p * np.log(p))  # natural log
    # Normalize by log of number of bins for comparability
    Hn = H / np.log(len(P)) if len(P) > 1 else np.nan
    if not np.isfinite(Hn):
        return np.nan
    return float(Hn)


def rolling_spectral_entropy(x, w):
    out = np.full(len(x), np.nan)
    for i in range(w - 1, len(x)):
        win = x[i - w + 1:i + 1]
        if not np.isfinite(win).all():
            continue
        out[i] = spectral_entropy(win)
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
    dlogv = np.diff(logv, prepend=logv[0])
    dlogv[0] = 0.0
    spec_ent = rolling_spectral_entropy(dlogv, W_SPEC)
    sz = rolling_z(spec_ent, ALB)
    sig = np.zeros(n)
    cur = 0.0
    hold = 0
    warm = max(W_SPEC, ALB) + 10
    for i in range(warm, n):
        z = sz[i]
        if not np.isfinite(z):
            nxt = cur
            hold = hold + 1 if cur != 0 else 0
        else:
            desired = 0.0
            if z >= ENTRY_Z:  # high spectral entropy -> more spread, fade short
                desired = -1.0
            elif z <= -ENTRY_Z:  # low spectral entropy -> concentrated, fade long
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
        "tool": "real_quote_volume_spectral_entropy_shock_mr_costed_oos",
        "generated_at_utc": ts,
        "campaign": 103,
        "candidate": "VOLUME_SPECTRAL_ENTROPY_SHOCK_MR (Spectral/PDS entropy of log-volume changes, periodogram normalized Shannon entropy over positive freqs, fade spectral-entropy shocks vs baseline)",
        "pre_stated_distinctness": "Grep-verified absent before impl: spectral_entropy|power_spectral.*entropy|psd.*entropy not present in prior real_quote_volume costed OOS reports/scripts. Distinct from ApEn/SampleEn/permutation/shannon/renyi block-frequency entropies, DFA(C101), Hurst/RS, Higuchi/Katz/Petrosian FD, LZ76, Hjorth/TKEO, ZCR(C100). Frequency-domain entropy vs time-domain.",
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
        "params": {"w_spec": W_SPEC, "alb": ALB, "entry_z": ENTRY_Z, "exit_z": EXIT_Z, "max_hold": MAX_HOLD, "train": TRAIN, "test": TEST, "step": STEP, "cost_grid": COST_GRID},
        "references": {
            "prior_unblock": "reports/real_feed_unblock_status_20261106T130243Z.json",
            "prior_unblock_sha256": "49699fad6ce626b2b3edf99650e21a5f305778c55b9b83e1980ddbdfd67a6d80",
            "prior_registry": "reports/strategy_edge_registry_20261106T202343Z.json",
            "prior_registry_sha256": "ce1d2d411542eaad47c2829b5983a89f007bef277f631c7ebd86927be0b9b0c5",
            "c100_rb": "reports/real_quote_volume_zcr_shock_mr_costed_oos_20261106T174105Z.json",
            "c100_rb_sha256": PRIOR_C100_RB_SHA,
            "c101_rb": "reports/real_quote_volume_dfa_shock_mr_costed_oos_20261106T200334Z.json",
            "c101_rb_sha256": PRIOR_C101_RB_SHA,
            "c102_rb": "reports/real_quote_volume_approximate_entropy_shock_mr_costed_oos_20261106T201839Z.json",
            "c102_rb_sha256": PRIOR_C102_RB_SHA,
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
    fn = reports / f"real_quote_volume_spectral_entropy_shock_mr_costed_oos_{ts}.json"
    fn.write_text(json.dumps(out, indent=2))
    print(json.dumps({"artifact": str(fn), "sha256": sha256_file(fn), "oos_edge_proven": oos_edge}, indent=2))


if __name__ == "__main__":
    main()
