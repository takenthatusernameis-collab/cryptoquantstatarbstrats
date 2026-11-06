#!/usr/bin/env python3
"""Campaign #78 R-B (fail-closed, real data only): real_quote_volume-conditioned
Rolling Hoover (Robin Hood) Index shock mean reversion on real Binance spot quote
volume (klines col 5) + real cached spot 1h.

PRE-STATED HYPOTHESIS (fixed before seeing OOS results): "Volume Hoover/Robin Hood
Share-Deviation Shock Mean Reversion"
- For each asset, compute rolling Hoover index over quote_volume_usdt window W=48h:
  H_t = 0.5 * sum_{i in W, x_i>0} |p_i - 1/n|, p_i = x_i / sum(x), n=count(x_i>0).
  (L1 deviation of volume shares from uniform; Robin Hood index = fraction of total
  volume that would need reallocation to equalize.)
- Causal z-score of H_t (lookback ZLB=168h). Trade Hoover inequality SHOCKS as MR:
  fade extreme positive shocks (concentration spike -> expect normalization):
    if d_z >= ENTRY_Z (1.25): SHORT (fade concentration shock)
    if d_z <= -ENTRY_Z (-1.25): LONG (fade uniformity shock / dispersion collapse)
  Exit: |d_z| < EXIT_Z (0.25) OR hold >= MAX_HOLD (12h) OR signal flips.
- Execution shift t -> t+1. Walk-forward: rolling 720/168/168 (train/test/step).
- Cost grid bps (fee,slip): [[0,0],[5,5],[10,10],[20,20],[40,40]] (0-40bps round-trip
  on turnover). Benchmark: buy-and-hold per asset (gross) on union of OOS WF windows.
- Pre-stated edge rule (fail-closed): oos_edge_proven=true IFF executed exposure>0 AND
  for ALL cost-grid slices OOS net sum > 0 AND OOS net mean return beats B&H OOS mean
  on same OOS windows (aggregate mean_oos_net > mean_oos_bh). Else false. No in-sample
  tuning, no threshold weakening, no fabricated data/proxies.

DISTINCTNESS (vs C23/C40-C77): Hoover = 0.5*Σ|p_i-1/n| (L1 deviation of normalized
shares from uniform distribution). Different object/functional form from:
C51 Gini mean-difference (pairwise L1 |x_i-x_j|, no share-vs-uniform baseline);
C76 Theil L GE(0) mean(ln(μ/x)) log-ratio; C74 Theil T GE(1) mean(r*ln r) upper-tail;
C41 Shannon binned histogram entropy -Σq log q; C75 Rényi-2 -ln(Σp^2) collision HHI;
C42/43 permutation/sample entropy; C45 CV (σ/μ) second moment; C48 kurtosis;
C52/53 Lorenz asymmetry? (if tested) — Hoover is the max vertical Lorenz gap (Robin Hood)
not an asymmetry coefficient. Quantile dispersions (C66/67/68/69/70/71 IDR/decile/LQD/UQD
etc.), quantile asymmetries (C72 Bowley, C73 Kelly), corr/beta/lead-lag (C29-40ish),
level/ROC/ratio/cumulative/partition/imbalance/z-accel transforms in prior campaigns.
Not a monotonic reparameterization producing identical z-scores in practice to C76/C74/C51
(given finite window + clipping/zero handling + different nonlinearity)."""
from __future__ import annotations

import hashlib
import json
import pickle
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "data" / "cache"
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)
TS = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

SPOT_CACHE = "0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7"
VOL_META = CACHE_DIR / "volume_1h_full.meta.json"
COST_GRID = [[0, 0], [5, 5], [10, 10], [20, 20], [40, 40]]
TRAIN, TEST, STEP = 720, 168, 168
W, ZLB, ENTRY_Z, EXIT_Z, MAX_HOLD = 48, 168, 1.25, 0.25, 12
NAMED = ["BTC", "ETH", "SOL", "BNB"]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def wf_windows(n):
    ws = []
    st = 0
    while st + TRAIN + TEST <= n:
        ws.append((st, st + TRAIN, st + TRAIN + TEST))
        st += STEP
    return ws


def hoover_index(arr: np.ndarray) -> float:
    x = arr[np.isfinite(arr) & (arr > 0)]
    n = x.size
    if n < 2:
        return np.nan
    s = x.sum()
    if s <= 1e-18:
        return np.nan
    p = x / s
    return float(0.5 * np.abs(p - 1.0 / n).sum())


def rolling_hoover(v: np.ndarray, w: int) -> np.ndarray:
    out = np.full(len(v), np.nan)
    for i in range(w - 1, len(v)):
        out[i] = hoover_index(v[i - w + 1 : i + 1])
    return out


def rolling_z(x: np.ndarray, lb: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    for i in range(lb - 1, len(x)):
        w = x[i - lb + 1 : i + 1]
        w = w[np.isfinite(w)]
        if w.size < max(30, lb // 3):
            continue
        mu = w.mean()
        sd = w.std(ddof=0)
        if sd <= 1e-18 or not np.isfinite(x[i]):
            continue
        out[i] = (x[i] - mu) / sd
    return out


def run_asset(prices: pd.Series, vol: pd.Series):
    idx = prices.index.intersection(vol.index)
    p = prices.reindex(idx).astype(float)
    v = pd.to_numeric(vol.reindex(idx), errors="coerce")
    mask = p.notna() & v.notna() & (v > 0)
    p = p[mask]
    v = v[mask]
    n = len(p)
    ret = p.pct_change().fillna(0.0).values
    vv = v.values.astype(float)
    hv = rolling_hoover(vv, W)
    dz = rolling_z(hv, ZLB)
    sig = np.zeros(n)
    cur = 0.0
    hold = 0
    warm = max(W, ZLB) + 2
    for i in range(warm, n):
        z = dz[i]
        if not np.isfinite(z):
            nxt = cur
            hold = hold + 1 if cur != 0 else 0
        else:
            desired = 0.0
            if z >= ENTRY_Z:
                desired = -1.0  # fade concentration shock
            elif z <= -ENTRY_Z:
                desired = 1.0  # fade uniformity shock
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
    has_exp = bool((np.abs(sig[oos_union]) > 0).sum() > 0) if oos_union.any() else bool((np.abs(sig) > 0).sum() > 0)
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
    edge = bool(has_exp and all(s["oos_net_gt_zero"] and s["oos_net_beats_bh_mean"] for s in slices.values()))
    return {
        "n_bars": n,
        "window_start": str(idx[0]) if n else None,
        "window_end": str(idx[-1]) if n else None,
        "n_wf_folds": len(ws),
        "has_exposure_oos": bool((np.abs(sig[oos_union]) > 0).sum() > 0) if oos_union.any() else False,
        "n_active_bars_oos": int((np.abs(sig[oos_union]) > 0).sum()) if oos_union.any() else 0,
        "bh_oos_sum": bh_oos,
        "bh_oos_mean": bh_oos_mean,
        "cost_slices": slices,
        "oos_edge_proven": edge,
    }


def main():
    spot = pickle.load(open(CACHE_DIR / f"{SPOT_CACHE}.pkl", "rb"))
    spot_meta = json.loads((CACHE_DIR / f"{SPOT_CACHE}.meta.json").read_text())
    spot_sha = sha256_file(CACHE_DIR / f"{SPOT_CACHE}.pkl")
    from data.real_feed_loader import validate_and_load_real_feed
    prov = json.loads((CACHE_DIR / "volume_1h_full.provenance.json").read_text())
    vol_df, vol_report = validate_and_load_real_feed(VOL_META, "real_quote_volume", provenance=prov)
    vol_wide = vol_df.pivot_table(index="timestamp_utc", columns="symbol", values="quote_volume_usdt", aggfunc="first").sort_index()
    if spot.index.tz is None:
        spot.index = spot.index.tz_localize("UTC")
    if vol_wide.index.tz is None:
        vol_wide.index = vol_wide.index.tz_localize("UTC")
    assets = [a for a in spot.columns if a in vol_wide.columns]
    by_asset = {}
    for a in assets:
        by_asset[a] = run_asset(spot[a], vol_wide[a])
    agg = {}
    for fee, slip in COST_GRID:
        key = f"fee{fee}_slip{slip}"
        vals = [by_asset[a]["cost_slices"][key] for a in assets]
        agg[key] = {
            "mean_oos_net_across_assets": float(np.mean([v["oos_net_sum"] for v in vals])),
            "mean_oos_net_mean_across_assets": float(np.mean([v["oos_net_mean"] for v in vals])),
            "mean_oos_bh_across_assets": float(np.mean([v["oos_bh_sum"] for v in vals])),
            "mean_frac_beats_bh": float(np.mean([1.0 if v["oos_net_beats_bh_mean"] else 0.0 for v in vals])),
            "n_assets": len(vals),
        }
    any_exposure = any(by_asset[a]["has_exposure_oos"] for a in assets)
    all_costs_positive = all(agg[k]["mean_oos_net_across_assets"] > 0 for k in agg)
    beats_bh_rule = all(agg[k]["mean_oos_net_mean_across_assets"] > agg[k]["mean_oos_bh_across_assets"] / max(1, by_asset[assets[0]]["n_bars"] - TRAIN) for k in agg) if assets else False
    # stricter: use aggregate mean_oos_net_mean vs mean bh mean
    mean_bh_mean = float(np.mean([by_asset[a]["bh_oos_mean"] for a in assets])) if assets else 0.0
    beats_bh_rule = all(agg[k]["mean_oos_net_mean_across_assets"] > mean_bh_mean for k in agg)
    oos_edge_proven = bool(any_exposure and all_costs_positive and beats_bh_rule)

    report = {
        "artifact": f"reports/real_quote_volume_hoover_robin_hood_shock_mr_costed_oos_{TS}.json",
        "tool": "scripts.run_real_quote_volume_hoover_robin_hood_shock_mr_costed_oos",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "campaign": 78,
        "path": "R-B",
        "family": "real_quote_volume",
        "real_data_only": True,
        "fabricated_data": False,
        "fail_closed": True,
        "no_proxies_labeled_real": True,
        "hypothesis": {
            "name": "Volume Hoover (Robin Hood) Share-Deviation Shock Mean Reversion",
            "family": "rolling_hoover_robin_hood_volume_shock_mr",
            "pre_stated": True,
            "formula": "H_t=0.5*Σ|p_i-1/n|, p_i=x_i/Σx_i, W=48 (L1 share deviation from uniform); z(d_z,168)->fade shocks d_z>=1.25 SHORT, <=-1.25 LONG; t->t+1",
            "params": {"W": W, "ZLB": ZLB, "ENTRY_Z": ENTRY_Z, "EXIT_Z": EXIT_Z, "MAX_HOLD": MAX_HOLD, "WF_TRAIN": TRAIN, "WF_TEST": TEST, "WF_STEP": STEP},
            "distinctness": [
                "Hoover/Robin Hood H_t = 0.5*Σ|p_i-1/n|: L1 deviation of volume shares from uniform (max vertical Lorenz gap). Different baseline/object from pairwise or log-ratio inequality.",
                "C51 Gini: pairwise L1 mean-difference |x_i-x_j|, no share-vs-uniform normalization baseline.",
                "C76 Theil L GE(0): mean(ln(μ/x)) log-ratio (lower-tail GE); C74 Theil T GE(1): mean(r*ln r) upper-tail. Hoover uses absolute share deviation, no logs, no GE order.",
                "C41 Shannon binned histogram entropy; C75 Rényi-2 collision -ln(Σp^2) (HHI/quadratic) — different functional (L1 vs log/quadratic).",
                "C42/43 permutation/sample entropy: ordinal/embedding complexity, not share inequality.",
                "C45 CV σ/μ (second moment), C48 kurtosis; C66-71 quantile dispersions (IDR/decile/LQD/UQD etc.); C72 Bowley/C73 Kelly quantile asymmetries — Hoover is distributional share deviation, not quantile spread/asymmetry.",
                "Not tested in C23/C40-C77: no prior Hoover/Robin Hood/Lorenz-max-gap transform on real_quote_volume.",
            ],
            "cost_grid_bps": COST_GRID,
        },
        "data": {
            "spot_cache": {"path": f"data/cache/{SPOT_CACHE}.pkl", "sha256": spot_sha, "bars": int(len(spot)), "assets": list(spot.columns)},
            "volume_feed": {
                "meta": "data/cache/volume_1h_full.meta.json",
                "validation": {k: vol_report.get(k) for k in ["ok", "refused", "reason", "rows", "family_spec"]},
                "real_data_only": True,
            },
            "assets": assets,
            "n_assets": len(assets),
        },
        "config": {
            "walk_forward": {"mode": "rolling", "train_bars": TRAIN, "test_bars": TEST, "step_bars": STEP},
            "cost_grid_bps_fee_slippage": COST_GRID,
            "benchmark": "buy-and-hold per asset (gross) on union of OOS WF windows",
        },
        "edge_rule_pre_stated": "oos_edge_proven=true IFF exposure>0 (OOS) AND for ALL cost slices mean OOS net sum across assets > 0 AND mean OOS net mean beats mean B&H OOS mean on same windows. Fail-closed.",
        "per_asset": by_asset,
        "aggregate": agg,
        "any_exposure": any_exposure,
        "all_costs_positive": all_costs_positive,
        "beats_bh_rule": beats_bh_rule,
        "oos_edge_proven": oos_edge_proven,
    }
    out = REPORTS / f"real_quote_volume_hoover_robin_hood_shock_mr_costed_oos_{TS}.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n")
    print(out)
    print(json.dumps({"oos_edge_proven": oos_edge_proven, "any_exposure": any_exposure, "all_costs_positive": all_costs_positive, "beats_bh_rule": beats_bh_rule, "sha256": sha256_file(out)}, indent=2))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(ROOT))
    main()
