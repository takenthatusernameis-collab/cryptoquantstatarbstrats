#!/usr/bin/env python3
"""Campaign #87 R-B (fail-closed, real data only): real_quote_volume-conditioned
Rolling Turning-Point Rate (path oscillation / local non-monotonicity, NON-location)
shock mean reversion on real Binance spot quote volume (klines col 5) + real cached spot 1h.

PRE-STATED HYPOTHESIS (fixed before seeing OOS results): "Volume Turning-Point Rate Shock MR"
- For each asset, compute rolling TURNING-POINT RATE of quote_volume_usdt over
  window W=48h on the positive finite window values:
    TP_t = (1/(n-2)) * sum_{i=2}^{n-1} I[(x_i - x_{i-1})*(x_{i+1} - x_i) < 0]
  i.e. the fraction of interior points that are local peaks or troughs (a local
  direction-reversal / oscillation-frequency measure of the volume path).
- Causal z-score of TP_t (lookback ZLB=168h). Trade TP oscillation SHOCKS as MR:
    if dz >= ENTRY_Z (1.25): SHORT (fade oscillation/turning-rate spike)
    if dz <= -ENTRY_Z (-1.25): LONG (fade oscillation/turning-rate compression shock)
  Exit: |dz| < EXIT_Z (0.25) OR hold >= MAX_HOLD (12h) OR signal flips.
- Execution shift t -> t+1. Walk-forward: rolling 720/168/168 (train/test/step).
- Cost grid bps (fee,slip): [[0,0],[5,5],[10,10],[20,20],[40,40]]. Benchmark: B&H
  per asset (gross) on union of OOS WF windows.
- Pre-stated edge rule (fail-closed): oos_edge_proven=true IFF OOS exposure>0 AND
  for ALL cost-grid slices OOS net sum > 0 AND mean OOS net mean beats mean B&H OOS
  mean on same OOS windows. Else false. No in-sample tuning, no threshold weakening.

DISTINCTNESS (vs C23/C40-C86, mechanically stated) — NON-LOCATION TRANSFORM:
- Turning-Point Rate TP=(1/(n-2))*sum I[(dx_{i-1})*(dx_i)<0] is a PATH
  OSCILLATION / LOCAL NON-MONOTONICITY measure (count of local direction reversals
  over interior triplets). It answers "how frequently does the volume path reverse
  locally?" — a shape-of-path / randomness-oscillation functional, NOT a location,
  NOT a scale-of-level, NOT an inequality share, NOT an entropy/probability measure.
- LOCATION family exhausted (explicitly NOT used): distinct from C86 Hodges–Lehmann
  HL=median{(x_i+x_j)/2:i<=j} (rank-based Walsh-average-median LOCATION),
  C85 Gastwirth G=0.3*Q(1/3)+0.4*Q(0.5)+0.3*Q(2/3) (tercile L-estimator LOCATION),
  C84 Midhinge MH=(Q1+Q3)/2 (quartile L-estimator LOCATION, weights 0.5/0/0.5),
  C83 Tukey trimean TM=(Q1+2*Q2+Q3)/4 (quartile+median L-estimator LOCATION).
  TP is a reversal COUNT/RATE, not a level/center functional.
- vs ACF/serial correlation (autocorr report exists): ACF(1)/serial correlation is a
  LINEAR lag-1 covariance/correlation magnitude. TP counts LOCAL SIGN REVERSALS of
  consecutive differences (a nonlinear, rank/sign-like oscillation count on triplets)
  — different statistic, different sensitivity (monotone drift can have high ACF but
  zero turning points; rapid oscillation yields high TP regardless of linear corr).
- vs C41/C42/C43 entropy (Shannon binned/permutation/sample, per C86 distinctness):
  permutation entropy maps ordinal patterns to SYMBOL PROBABILITIES over all n!
  permutations and computes entropy — an information/complexity measure. TP is a
  simple COUNT of peak/trough reversals (a single frequency statistic), not a
  distributional entropy over ordinal symbols.
- vs C80 MAD=median(|x-median|), C82 AAD=mean(|x-mean|): SCALE/DISPERSION of
  deviations from a center, not oscillation frequency.
- vs C66-C73 quantile DISPERSIONS/ASYMMETRIES (spreads/ratios): TP is a temporal
  path-oscillation measure, not a cross-sectional quantile spread/asymmetry.
- vs skewness (moment, Bowley, Kelly exist): distributional ASYMMETRY, not local
  turning/reversal frequency. vs kurtosis (exists): tail/peakedness shape.
- vs C79 Sarle BC / C45 CV / C51,C74-C78 inequality (Gini/Theil/GE/Atkinson/HHI/
  Hoover): shape/scale/inequality-concentration, not temporal oscillation rate.
- Data source identical (real Binance spot quote volume) but TRANSFORM is mechanically
  different: rolling fraction of local turning points (path reversal rate).
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

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
CACHE_DIR = ROOT / "data" / "cache"
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)
TS = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

SPOT_CACHE = "0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7"
VOL_META = CACHE_DIR / "volume_1h_full.meta.json"
VOL_PROV = CACHE_DIR / "volume_1h_full.provenance.json"
COST_GRID = [[0, 0], [5, 5], [10, 10], [20, 20], [40, 40]]
TRAIN, TEST, STEP = 720, 168, 168
W, ZLB, ENTRY_Z, EXIT_Z, MAX_HOLD = 48, 168, 1.25, 0.25, 12
CAMPAIGN = 87
PRIOR_UNBLOCK = "reports/real_feed_unblock_status_20261106T120340Z.json"
PRIOR_REGISTRY = "reports/strategy_edge_registry_20261106T120340Z.json"


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


def turning_point_rate(arr: np.ndarray) -> float:
    """TP = fraction of interior points that are local peaks/troughs.

    Path oscillation / local non-monotonicity: count of direction reversals
    over consecutive-difference triplets, normalized by (n-2).
    """
    x = arr[np.isfinite(arr) & (arr > 0)]
    n = x.size
    if n < 4:
        return np.nan
    dx = np.diff(x)
    # turning point where consecutive diffs change sign (product < 0)
    turns = (dx[:-1] * dx[1:]) < 0
    rate = float(np.mean(turns))
    return rate if np.isfinite(rate) else np.nan


def rolling_tp(v: np.ndarray, w: int) -> np.ndarray:
    out = np.full(len(v), np.nan)
    for i in range(w - 1, len(v)):
        out[i] = turning_point_rate(v[i - w + 1 : i + 1])
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
    feat = rolling_tp(vv, W)
    dz = rolling_z(feat, ZLB)
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
    spot_sha = sha256_file(CACHE_DIR / f"{SPOT_CACHE}.pkl")
    from data.real_feed_loader import validate_and_load_real_feed

    prov = json.loads(VOL_PROV.read_text(encoding="utf-8"))
    vol_df, vol_report = validate_and_load_real_feed(VOL_META, "real_quote_volume", provenance=prov)
    vol_wide = (
        vol_df.pivot_table(index="timestamp_utc", columns="symbol", values="quote_volume_usdt", aggfunc="first")
        .sort_index()
    )
    if spot.index.tz is None:
        spot.index = spot.index.tz_localize("UTC")
    if vol_wide.index.tz is None:
        vol_wide.index = vol_wide.index.tz_localize("UTC")
    per = {}
    syms = [s for s in spot.columns if s in vol_wide.columns]
    for sym in syms:
        per[sym] = run_asset(spot[sym], vol_wide[sym])
    agg = {k: {sk: 0.0 for sk in [f"fee{f}_slip{s}" for f, s in COST_GRID]} for k in ["oos_net_sum", "oos_net_mean"]}
    for sym, r in per.items():
        for sk, v in r["cost_slices"].items():
            agg["oos_net_sum"][sk] += v["oos_net_sum"]
            agg["oos_net_mean"][sk] += v["oos_net_mean"]
    n = max(1, len(per))
    for sk in agg["oos_net_mean"]:
        agg["oos_net_mean"][sk] /= n
    any_exp = any(r["has_exposure_oos"] for r in per.values())
    all_pos = all(agg["oos_net_sum"][sk] > 0 for sk in agg["oos_net_sum"])
    bh_mean = float(np.mean([r["bh_oos_mean"] for r in per.values()])) if per else 0.0
    beats = all(agg["oos_net_mean"][sk] > bh_mean for sk in agg["oos_net_mean"])
    edge = bool(any_exp and all_pos and beats)
    artifact = {
        "tool": "scripts/run_real_quote_volume_turning_point_rate_shock_mr_costed_oos.py",
        "generated_at_utc": TS,
        "campaign": CAMPAIGN,
        "prior_unblock": PRIOR_UNBLOCK,
        "prior_registry": PRIOR_REGISTRY,
        "data_source": {
            "spot_cache": SPOT_CACHE,
            "spot_cache_sha256": spot_sha,
            "volume_meta": str(VOL_META.relative_to(ROOT)),
            "volume_provenance": str(VOL_PROV.relative_to(ROOT)),
            "volume_loader_report": vol_report,
            "real_data_only": True,
            "fabricated_data": False,
            "no_proxies_labeled_real": True,
        },
        "hypothesis_prestated": {
            "id": "VOLUME_TURNING_POINT_RATE_SHOCK_MR",
            "description": "Fade turning-point rate TP=(1/(n-2))*sum I[(dx_{i-1})*(dx_i)<0] (W=48) z-score shocks of real quote volume; path oscillation/local non-monotonicity mean reversion, t->t+1.",
            "entry_z": ENTRY_Z,
            "exit_z": EXIT_Z,
            "max_hold": MAX_HOLD,
            "tp_window": W,
            "z_lookback": ZLB,
            "walkforward": {"train": TRAIN, "test": TEST, "step": STEP},
            "cost_grid_bps": COST_GRID,
            "benchmark": "buy_and_hold_gross_same_oos_windows",
        },
        "distinctness_mechanical": {
            "turning_point_rate": "TP=(1/(n-2))*sum_{i=2}^{n-1} I[(x_i-x_{i-1})*(x_{i+1}-x_i)<0] = fraction of interior local peaks/troughs (path oscillation/local direction-reversal frequency). NON-LOCATION, non-scale, non-inequality, non-entropy.",
            "non_location_explicit": "NOT a location estimator. Distinct from exhausted location family: C86 Hodges–Lehmann HL=median{(x_i+x_j)/2} (Walsh-average-median rank LOCATION), C85 Gastwirth G=0.3*Q(1/3)+0.4*Q(0.5)+0.3*Q(2/3) (tercile L-estimator LOCATION), C84 Midhinge MH=(Q1+Q3)/2 (quartile LOCATION), C83 Tukey trimean TM=(Q1+2*Q2+Q3)/4 (quartile+median LOCATION). TP is a reversal count/rate.",
            "vs_autocorr": "ACF(1)/serial correlation is LINEAR lag-1 covariance/correlation; TP counts LOCAL SIGN REVERSALS of consecutive differences (triplet oscillation count) — different statistic/sensitivity (monotone drift: high ACF, zero TP; rapid oscillation: high TP regardless of linear corr).",
            "vs_C41C42C43_entropy": "Permutation/sample/Shannon entropy map patterns to symbol probabilities (information/complexity distributional measures). TP is a single reversal-frequency count, not distributional entropy over ordinal symbols.",
            "vs_C82_AAD_C80_MAD": "AAD/MAD are SCALE/DISPERSION of deviations, not oscillation frequency.",
            "vs_C66_C73_quantile_dispersions_asymmetries": "temporal path-oscillation, not cross-sectional quantile spread/asymmetry.",
            "vs_skewness_bowley_kelly_kurtosis": "distributional asymmetry/tail shape, not local turning frequency.",
            "vs_C79_SarleBC_C45_CV_C51C74C75C76C78_inequality": "shape/scale/inequality-concentration, not temporal oscillation rate.",
            "vs_C23_other_RQV": "rolling local turning-point rate on volume path; different transform family.",
            "data_source_identical_transform_mechanically_different": True,
        },
        "edge_rule_exact": "oos_edge_proven=true IFF OOS exposure>0 AND all cost slices OOS net sum>0 AND mean OOS net mean beats mean B&H OOS mean on same WF windows; else false.",
        "aggregate": {
            "n_assets": len(per),
            "any_exposure_oos": any_exp,
            "all_cost_slices_positive_oos_net_sum": all_pos,
            "mean_bh_oos_mean_across_assets": bh_mean,
            "all_cost_slices_beat_bh_mean_rule": beats,
            "oos_edge_proven": edge,
            "cross_asset_sum_oos_net_sum": agg["oos_net_sum"],
            "cross_asset_mean_oos_net_mean": agg["oos_net_mean"],
        },
        "per_asset": per,
        "fail_closed": True,
        "oos_edge_proven": edge,
        "conclusion": "OOS_EDGE_PROVEN" if edge else "NO_OOS_EDGE_PROVEN_FAIL_CLOSED",
    }
    out = REPORTS / f"real_quote_volume_turning_point_rate_shock_mr_costed_oos_{TS}.json"
    out.write_text(json.dumps(artifact, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(out.relative_to(ROOT)), "sha256": sha256_file(out),
                      "oos_edge_proven": edge, "n_assets": len(per), "any_exposure": any_exp,
                      "all_pos": all_pos, "beats_bh": beats, "bh_mean": bh_mean,
                      "agg_net_sum": agg["oos_net_sum"]}, indent=2))


if __name__ == "__main__":
    main()
