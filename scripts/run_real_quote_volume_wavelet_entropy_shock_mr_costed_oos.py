#!/usr/bin/env python3
"""Campaign #104 Path R (fail-closed, real data only): real_quote_volume-conditioned
strategy on real Binance spot quote volume (klines column 5) + real cached spot 1h.

PRE-STATED HYPOTHESIS (fixed before seeing OOS results): "Volume Wavelet-Entropy shock mean reversion"
- Feature: Wavelet energy-distribution entropy over scales on rolling windows of
  log-volume changes dlogv. Use discrete/continuous wavelet to get scale-wise energy
  E_s, normalize to distribution p_s = E_s/sum E_s, Shannon entropy H_w = -sum p_s log p_s
  (normalized). Distinct from spectral/PSD entropy (C103) and from time-domain entropies.
- Signal: shock = |z(wavelet_entropy)| relative to longer baseline; fade extremes
  (high wavelet entropy = energy spread across scales/unpredictable -> short;
   low = concentrated -> long), execution t->t+1.
- WF 720/168/168, cost grid [[0,0],[5,5],[10,10],[20,20],[40,40]]; edge rule exact as specified.
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
W_WAV = 168
ALB = 336
ENTRY_Z = 1.5
EXIT_Z = 0.5
MAX_HOLD = 24
MIN_OBS = 168


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


def wavelet_energy_entropy(x):
    """Wavelet scale energy distribution entropy."""
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    n = x.size
    if n < 32:
        return np.nan
    try:
        import pywt
        # Use discrete wavelet transform levels
        max_level = min(6, pywt.dwt_max_level(n, 'db4'))
        if max_level < 1:
            raise ValueError("low level")
        coeffs = pywt.wavedec(x - np.mean(x), 'db4', level=max_level)
        energies = []
        for c in coeffs:
            energies.append(np.sum(c**2))
        energies = np.array(energies)
        Esum = np.sum(energies)
        if Esum <= 0 or not np.isfinite(Esum):
            raise ValueError("bad energies")
        p = energies / Esum
        p = p[p > 0]
        if p.size == 0:
            return np.nan
        H = -np.sum(p * np.log(p))
        Hn = H / np.log(len(energies)) if len(energies) > 1 else np.nan
        if not np.isfinite(Hn):
            return np.nan
        return float(Hn)
    except Exception:
        # Fallback: CWT Morlet style via scipy
        try:
            x0 = x - np.mean(x)
            widths = np.arange(1, min(17, n//4))
            if len(widths) == 0:
                return np.nan
            cwtmatr = signal.cwt(x0, signal.morlet2, widths)
            energies = np.sum(np.abs(cwtmatr)**2, axis=1)
            Esum = np.sum(energies)
            if Esum <= 0 or not np.isfinite(Esum):
                return np.nan
            p = energies / Esum
            p = p[p > 0]
            if p.size == 0:
                return np.nan
            H = -np.sum(p * np.log(p))
            Hn = H / np.log(len(energies)) if len(energies) > 1 else np.nan
            if not np.isfinite(Hn):
                return np.nan
            return float(Hn)
        except Exception:
            return np.nan


def rolling_wavelet_entropy(x, w):
    out = np.full(len(x), np.nan)
    for i in range(w - 1, len(x)):
        win = x[i - w + 1:i + 1]
        if not np.isfinite(win).all():
            continue
        out[i] = wavelet_energy_entropy(win)
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
    wav_ent = rolling_wavelet_entropy(dlogv, W_WAV)
    sz = rolling_z(wav_ent, ALB)
    sig = np.zeros(n)
    cur = 0.0
    hold = 0
    warm = max(W_WAV, ALB) + 10
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
        "tool": "real_quote_volume_wavelet_entropy_shock_mr_costed_oos",
        "generated_at_utc": ts,
        "campaign": 104,
        "candidate": "VOLUME_WAVELET_ENTROPY_SHOCK_MR (Wavelet energy-distribution entropy of log-volume changes, scale-wise energy normalized Shannon entropy; fade wavelet-entropy shocks vs baseline)",
        "pre_stated_distinctness": "Grep-verified absent before impl: wavelet_entropy not present in prior real_quote_volume costed OOS reports/scripts. Distinct from spectral/PSD entropy (C103) and time-domain entropies; uses wavelet scale energy distribution.",
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
        "params": {"w_wav": W_WAV, "alb": ALB, "entry_z": ENTRY_Z, "exit_z": EXIT_Z, "max_hold": MAX_HOLD, "train": TRAIN, "test": TEST, "step": STEP, "cost_grid": COST_GRID},
        "references": {
            "prior_unblock": "reports/real_feed_unblock_status_20261106T130243Z.json",
            "latest_registry": "reports/strategy_edge_registry_20261106T204555Z.json",
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
    fn = reports / f"real_quote_volume_wavelet_entropy_shock_mr_costed_oos_{ts}.json"
    fn.write_text(json.dumps(out, indent=2))
    print(json.dumps({"artifact": str(fn), "sha256": sha256_file(fn), "oos_edge_proven": oos_edge}, indent=2))


if __name__ == "__main__":
    main()
