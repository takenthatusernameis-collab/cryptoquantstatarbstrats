#!/usr/bin/env python3
"""Campaign #79 R-B (fail-closed, real data only): real_quote_volume-conditioned
Rolling Bimodality Coefficient shock mean reversion on real Binance spot quote
volume (klines col 5) + real cached spot 1h.

PRE-STATED HYPOTHESIS (fixed before seeing OOS results): "Volume Bimodality
Coefficient (Sarle's BC) Shock Mean Reversion"
- For each asset, compute rolling Sarle's Bimodality Coefficient over quote_volume_usdt
  window W=48h:
    g = skewness(x), k_ex = excess kurtosis(x) (Fisher; sample moments, ddof=0 style
    over window values x_i>0), n_w = count(x_i>0)
    BC = (g^2 + 1) / (k_ex + 3*(n_w-1)^2 / ((n_w-2)*(n_w-3)))  for n_w > 3
  BC in (0,1]; values > 5/9 (~0.555) suggest bimodality/uniformity vs unimodality.
- Causal z-score of BC_t (lookback ZLB=168h). Trade BC SHOCKS as MR:
    if dz >= ENTRY_Z (1.25): SHORT (fade bimodality/distribution-shape shock)
    if dz <= -ENTRY_Z (-1.25): LONG (fade unimodality-concentration shock)
  Exit: |dz| < EXIT_Z (0.25) OR hold >= MAX_HOLD (12h) OR signal flips.
- Execution shift t -> t+1. Walk-forward: rolling 720/168/168 (train/test/step).
- Cost grid bps (fee,slip): [[0,0],[5,5],[10,10],[20,20],[40,40]]. Benchmark: B&H
  per asset (gross) on union of OOS WF windows.
- Pre-stated edge rule (fail-closed): oos_edge_proven=true IFF OOS exposure>0 AND
  for ALL cost-grid slices OOS net sum > 0 AND mean OOS net mean beats mean B&H OOS
  mean on same OOS windows. Else false. No in-sample tuning, no threshold weakening.

DISTINCTNESS (vs C23/C40-C78): Sarle's BC = (g^2+1)/(k_ex + c(n_w)) is a *composite
shape* statistic jointly mapping skewness (3rd) and excess kurtosis (4th) moments into
a bimodality indicator with a sample-size correction c(n_w)=3*(n_w-1)^2/((n_w-2)*(n_w-3)).
This is NOT the raw 3rd/4th moment signal and NOT a monotonic transform of a single prior:
- C45 used CV (σ/μ, 2nd moment ratio); C48 is referenced in distinctness as kurtosis-area
  but C79 uses BC, a nonlinear joint function (g^2+1)/(k_ex+c) — different object/value
  distribution and z-dynamics than CV or raw kurtosis alone.
- C51 Gini (pairwise L1), C76 Theil L GE(0), C74 Theil T GE(1), C75 Rényi-2, C78 Hoover
  L1 share deviation: all inequality/concentration indices on shares; BC is a distribution
  *shape/bimodality* coefficient on raw window values, not share inequality.
- C41 Shannon binned, C42/43 permutation/sample entropy, C66-73 quantile
  dispersions/asymmetries, corr/beta/lead-lag/level/ROC/ratio/cumulative/partition/
  imbalance transforms in prior campaigns — none use Sarle's bimodality coefficient.
Not tested in C23/C40-C78."""
from __future__ import annotations

import hashlib, json, pickle, sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
CACHE_DIR = ROOT / "data" / "cache"
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)
TS = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

SPOT_CACHE = "0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7"
VOL_META = CACHE_DIR / "volume_1h_full.meta.json"
COST_GRID = [[0, 0], [5, 5], [10, 10], [20, 20], [40, 40]]
TRAIN, TEST, STEP = 720, 168, 168
W, ZLB, ENTRY_Z, EXIT_Z, MAX_HOLD = 48, 168, 1.25, 0.25, 12


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


def bimodality_coeff(arr: np.ndarray) -> float:
    x = arr[np.isfinite(arr) & (arr > 0)]
    n = x.size
    if n < 4:
        return np.nan
    mu = x.mean()
    dif = x - mu
    m2 = np.mean(dif ** 2)
    if m2 <= 1e-18:
        return np.nan
    m3 = np.mean(dif ** 3)
    m4 = np.mean(dif ** 4)
    g = m3 / (m2 ** 1.5)  # skewness (population style)
    k_ex = m4 / (m2 ** 2) - 3.0  # excess kurtosis
    denom_corr = 3.0 * (n - 1) ** 2 / ((n - 2) * (n - 3))
    denom = k_ex + denom_corr
    if not np.isfinite(denom) or abs(denom) <= 1e-18:
        return np.nan
    bc = (g ** 2 + 1.0) / denom
    if not np.isfinite(bc):
        return np.nan
    return float(np.clip(bc, 0.0, 1.5))


def rolling_bc(v: np.ndarray, w: int) -> np.ndarray:
    out = np.full(len(v), np.nan)
    for i in range(w - 1, len(v)):
        out[i] = bimodality_coeff(v[i - w + 1 : i + 1])
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
    p, v = p[mask], v[mask]
    n = len(p)
    ret = p.pct_change().fillna(0.0).values
    vv = v.values.astype(float)
    bc = rolling_bc(vv, W)
    dz = rolling_z(bc, ZLB)
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
    edge = bool(((np.abs(sig[oos_union]) > 0).sum() > 0 if oos_union.any() else False)
                and all(s["oos_net_gt_zero"] and s["oos_net_beats_bh_mean"] for s in slices.values()))
    return {
        "n_bars": n, "window_start": str(idx[0]) if n else None, "window_end": str(idx[-1]) if n else None,
        "n_wf_folds": len(ws),
        "has_exposure_oos": bool((np.abs(sig[oos_union]) > 0).sum() > 0) if oos_union.any() else False,
        "n_active_bars_oos": int((np.abs(sig[oos_union]) > 0).sum()) if oos_union.any() else 0,
        "bh_oos_sum": bh_oos, "bh_oos_mean": bh_oos_mean,
        "cost_slices": slices, "oos_edge_proven": edge,
    }


def main():
    spot = pickle.load(open(CACHE_DIR / f"{SPOT_CACHE}.pkl", "rb"))
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
    by_asset = {a: run_asset(spot[a], vol_wide[a]) for a in assets}
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
    mean_bh_mean = float(np.mean([by_asset[a]["bh_oos_mean"] for a in assets])) if assets else 0.0
    beats_bh_rule = all(agg[k]["mean_oos_net_mean_across_assets"] > mean_bh_mean for k in agg)
    oos_edge_proven = bool(any_exposure and all_costs_positive and beats_bh_rule)
    report = {
        "artifact": f"reports/real_quote_volume_bimodality_coeff_shock_mr_costed_oos_{TS}.json",
        "tool": "scripts.run_real_quote_volume_bimodality_coeff_shock_mr_costed_oos",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "campaign": 79, "path": "R-B", "family": "real_quote_volume",
        "real_data_only": True, "fabricated_data": False, "fail_closed": True, "no_proxies_labeled_real": True,
        "hypothesis": {
            "name": "Volume Bimodality Coefficient (Sarle's BC) Shock Mean Reversion",
            "family": "rolling_volume_bimodality_coeff_shock_mr",
            "pre_stated": True,
            "formula": "BC=(g^2+1)/(k_ex + 3*(n-1)^2/((n-2)*(n-3))), g=skew, k_ex=excess kurtosis, W=48; z(dz,168)->fade shocks dz>=1.25 SHORT, <=-1.25 LONG; t->t+1",
            "params": {"W": W, "ZLB": ZLB, "ENTRY_Z": ENTRY_Z, "EXIT_Z": EXIT_Z, "MAX_HOLD": MAX_HOLD, "WF_TRAIN": TRAIN, "WF_TEST": TEST, "WF_STEP": STEP},
            "distinctness": [
                "Sarle's BC=(g^2+1)/(k_ex+c(n)) is a composite bimodality/shape statistic jointly using skewness (3rd) and excess kurtosis (4th) with sample-size correction — a nonlinear joint mapping, not raw CV (C45, 2nd), not raw kurtosis signal, not a single-moment or monotonic single-index transform.",
                "BC targets distribution SHAPE/bimodality of raw window volume values; distinct from share-inequality/concentration indices: C51 Gini pairwise L1, C76 Theil L GE(0), C74 Theil T GE(1), C75 Rényi-2 collision H2, C78 Hoover/Robin Hood L1 share deviation from uniform.",
                "Distinct from C41 Shannon binned, C42/43 permutation/sample entropy, C66-73 quantile dispersions/asymmetries, and corr/beta/lead-lag/level/ROC/ratio/cumulative/partition/imbalance transforms in C23/C40-C78.",
                "Not tested in C23/C40-C78: no prior Sarle bimodality coefficient transform on real_quote_volume."
            ],
            "cost_grid_bps": COST_GRID,
        },
        "data": {
            "spot_cache": {"path": f"data/cache/{SPOT_CACHE}.pkl", "sha256": spot_sha, "bars": int(len(spot)), "assets": list(spot.columns)},
            "volume_feed": {"meta": "data/cache/volume_1h_full.meta.json", "validation": {k: vol_report.get(k) for k in ["ok", "refused", "reason", "rows", "family_spec"]}, "real_data_only": True},
            "assets": assets, "n_assets": len(assets),
        },
        "config": {"walk_forward": {"mode": "rolling", "train_bars": TRAIN, "test_bars": TEST, "step_bars": STEP}, "cost_grid_bps_fee_slippage": COST_GRID, "benchmark": "buy-and-hold per asset (gross) on union of OOS WF windows"},
        "edge_rule_pre_stated": "oos_edge_proven=true IFF OOS exposure>0 AND for ALL cost slices mean OOS net sum across assets > 0 AND mean OOS net mean beats mean B&H OOS mean on same windows. Fail-closed.",
        "per_asset": by_asset, "aggregate": agg,
        "any_exposure": any_exposure, "all_costs_positive": all_costs_positive, "beats_bh_rule": beats_bh_rule,
        "oos_edge_proven": oos_edge_proven,
    }
    out = REPORTS / f"real_quote_volume_bimodality_coeff_shock_mr_costed_oos_{TS}.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n")
    print(out)
    print(json.dumps({"oos_edge_proven": oos_edge_proven, "any_exposure": any_exposure, "all_costs_positive": all_costs_positive, "beats_bh_rule": beats_bh_rule, "sha256": sha256_file(out)}, indent=2))


if __name__ == "__main__":
    main()
