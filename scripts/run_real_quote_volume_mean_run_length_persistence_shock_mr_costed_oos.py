#!/usr/bin/env python3
"""Campaign #89 R-B (fail-closed, real data only): real_quote_volume-conditioned
Rolling MEAN RUN LENGTH (above/below-median contiguous run-length persistence/duration,
NON-location, NON-TP, NON-Wald–Wolfowitz standardized total-run-count) shock mean
reversion on real Binance spot quote volume (klines col 5) + real cached spot 1h.

PRE-STATED HYPOTHESIS (fixed before seeing OOS results): "Volume Mean Run-Length Persistence Shock MR"
- For each asset, compute rolling MEAN RUN LENGTH L_mean of quote_volume_usdt over
  window W=48h on the positive finite window values:
    m = median(x); dichotomize s_i = sign(x_i - m) in {+1,-1}, dropping x_i==m;
    identify contiguous same-sign runs r_1,...,r_R with lengths l_1,...,l_R (sum l_k = n_kept);
    L_mean = (1/R) * sum_k l_k = n_kept / R  (mean duration/persistence of above/below-median runs).
- Causal z-score of L_mean (lookback ZLB=168h). Trade run-length PERSISTENCE SHOCKS as MR:
    if dz >= ENTRY_Z (1.25): SHORT (fade unusually persistent/long runs relative to recent norm)
    if dz <= -ENTRY_Z (-1.25): LONG (fade unusually choppy/short runs relative to recent norm)
  Exit: |dz| < EXIT_Z (0.25) OR hold >= MAX_HOLD (12h) OR signal flips.
- Execution shift t -> t+1. Walk-forward: rolling 720/168/168 (train/test/step).
- Cost grid bps (fee,slip): [[0,0],[5,5],[10,10],[20,20],[40,40]]. Benchmark: B&H
  per asset (gross) on union of OOS WF windows.
- Pre-stated edge rule (fail-closed): oos_edge_proven=true IFF OOS exposure>0 AND
  for ALL cost-grid slices OOS net sum > 0 AND mean OOS net mean beats mean B&H OOS
  mean on same OOS windows. Else false. No in-sample tuning, no threshold weakening.

DISTINCTNESS (vs C23/C40-C88, mechanically stated) — NON-LOCATION, NON-TP, NON-WW-RUNS TRANSFORM:
- MEAN RUN LENGTH L_mean = n_kept/R is a RUN-LENGTH PERSISTENCE/DURATION functional on
  the median-dichotomized sequence: it averages the LENGTHS (durations) of contiguous
  above/below-median runs. It answers "how persistent/long are same-side runs on
  average?" — a duration/persistence measure, NOT a standardized randomness test,
  NOT a location, NOT a path turning-point rate, NOT linear autocorrelation, NOT entropy.
- NON-WW-RUNS (vs C88 Wald–Wolfowitz): C88 computes Z_WW=(R-mu_R)/sigma_R, a
  STANDARDIZED TOTAL-RUN-COUNT randomness statistic (counts R runs, normalizes by the
  random-expectation mean/variance mu_R,var_R). C89 computes L_mean=n_kept/R, the raw
  MEAN DURATION of those runs (a run-length/persistence level) and z-scores that
  duration series causally. Different functional (total-count randomness test vs mean
  run-length persistence), different quantity (R standardized vs average l_k), different
  information (WW's randomness deviation vs run persistence/duration). While R and
  L_mean are algebraically linked (L_mean=n_kept/R), C88 uses WW's randomness
  normalization/null (mu_R,var_R depending on n1,n2) and C89 uses the causal
  z-score of L_mean itself — mechanically distinct transforms/signals.
- NON-LOCATION (explicitly NOT used): distinct from exhausted location family —
  C86 Hodges–Lehmann HL=median{(x_i+x_j)/2:i<=j} (rank-based Walsh-average-median
  LOCATION), C85 Gastwirth G=0.3*Q(1/3)+0.4*Q(0.5)+0.3*Q(2/3) (tercile L-estimator
  LOCATION), C84 Midhinge MH=(Q1+Q3)/2 (quartile L-estimator LOCATION), C83 Tukey
  trimean TM=(Q1+2*Q2+Q3)/4 (quartile+median L-estimator LOCATION). L_mean is a
  run-duration/persistence functional on a dichotomy, not a level/center functional.
- NON-TP (vs C87 Turning-Point Rate): C87 TP=(1/(n-2))*sum I[(dx_{i-1})*(dx_i)<0]
  counts LOCAL PEAK/TROUGH REVERSALS of consecutive raw differences (triplet
  oscillation on the original series). L_mean dichotomizes vs median then measures
  mean CONTIGUOUS SAME-SIDE RUN DURATION — different operation (median dichotomy +
  run-length averaging) and different phenomenon (persistence/duration vs reversal
  frequency).
- vs ACF/serial correlation (autocorr exists): ACF(1) is LINEAR lag-1 covariance/
  correlation of the continuous series. L_mean operates on a BINARY dichotomized
  sequence and measures RUN DURATIONS (nonlinear persistence structure), not linear
  covariance.
- vs C41/C42/C43 entropy (Shannon binned/permutation/sample): permutation/sample
  entropy map ordinal patterns to SYMBOL PROBABILITIES (information/complexity
  distributional measures). L_mean is a single mean run-duration on a median
  dichotomy, not distributional entropy over ordinal symbols.
- vs C80 MAD=median(|x-median|), C82 AAD=mean(|x-mean|): SCALE/DISPERSION of
  deviations, not run-length persistence of the dichotomized sequence.
- vs C66-C73 quantile DISPERSIONS/ASYMMETRIES (spreads/ratios): L_mean is a
  dichotomized-sequence run-duration measure, not a cross-sectional quantile spread.
- vs skewness (moment, Bowley, Kelly), kurtosis: distributional shape/asymmetry/tail,
  not run persistence. vs C79 Sarle BC/C45 CV/C51,C74-C78 inequality: shape/scale/
  concentration, not temporal run-length persistence.
- Data source identical (real Binance spot quote volume) but TRANSFORM is mechanically
  different: rolling mean run length (persistence/duration) on median-dichotomized volume.
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
CAMPAIGN = 89
PRIOR_UNBLOCK = "reports/real_feed_unblock_status_20261106T130243Z.json"
PRIOR_REGISTRY = "reports/strategy_edge_registry_20261106T130830Z.json"


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


def mean_run_length(arr: np.ndarray) -> float:
    x = np.asarray(arr, dtype=float)
    x = x[np.isfinite(x) & (x > 0)]
    if x.size < 12:
        return np.nan
    m = np.median(x)
    dif = x - m
    # drop ties to median for a clean dichotomy
    dif = dif[dif != 0]
    if dif.size < 8:
        return np.nan
    signs = np.sign(dif)
    changes = np.diff(signs.astype(np.int8))
    runs = int(np.sum(changes != 0) + 1)
    if runs <= 0:
        return np.nan
    lmean = float(dif.size) / float(runs)
    return lmean if np.isfinite(lmean) else np.nan


def rolling_mean_run(v: np.ndarray, w: int) -> np.ndarray:
    out = np.full(len(v), np.nan)
    for i in range(w - 1, len(v)):
        out[i] = mean_run_length(v[i - w + 1 : i + 1])
    return out


def rolling_z(x: np.ndarray, lb: int) -> np.ndarray:
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


def run_asset(prices: pd.Series, vol: pd.Series):
    idx = prices.index.intersection(vol.index)
    p = prices.reindex(idx).astype(float)
    v = pd.to_numeric(vol.reindex(idx), errors="coerce")
    mask = p.notna() & v.notna() & (v > 0)
    p, v = p[mask], v[mask]
    n = len(p)
    ret = p.pct_change().fillna(0.0).values
    vv = v.values.astype(float)
    feat = rolling_mean_run(vv, W)
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
        "tool": "scripts/run_real_quote_volume_mean_run_length_persistence_shock_mr_costed_oos.py",
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
            "id": "VOLUME_MEAN_RUN_LENGTH_PERSISTENCE_SHOCK_MR",
            "description": "Fade mean contiguous above/below-median run length L_mean=n_kept/R (W=48, median-dichotomized run-length persistence/duration) z-score shocks of real quote volume; run-duration persistence mean reversion, t->t+1.",
            "entry_z": ENTRY_Z,
            "exit_z": EXIT_Z,
            "max_hold": MAX_HOLD,
            "runs_window": W,
            "z_lookback": ZLB,
            "walkforward": {"train": TRAIN, "test": TEST, "step": STEP},
            "cost_grid_bps": COST_GRID,
            "benchmark": "buy_and_hold_gross_same_oos_windows",
        },
        "distinctness_mechanical": {
            "mean_run_length": "L_mean = n_kept/R on median-dichotomized sequence (drop ties): R=contiguous same-sign runs, L_mean is mean DURATION/PERSISTENCE of above/below-median runs (n_kept/R). NON-LOCATION, NON-TP, NON-WW-standardized-total-run-count, non-ACF, non-entropy.",
            "non_WW_runs_vs_C88": "C88 computes Z_WW=(R-mu_R)/sigma_R, a STANDARDIZED TOTAL-RUN-COUNT randomness statistic (counts R, normalizes by random-expectation mu_R,var_R depending on n1,n2). C89 computes L_mean=n_kept/R, the raw MEAN DURATION of runs, and causally z-scores that duration series. Different functional (total-count randomness test vs mean run-length persistence), different quantity (R standardized vs average l_k), different information (randomness deviation vs run persistence/duration). Mechanically distinct transforms/signals despite algebraic link L_mean=n_kept/R.",
            "non_location_explicit": "NOT a location estimator. Distinct from exhausted location family: C86 Hodges–Lehmann HL=median{(x_i+x_j)/2} (Walsh-average-median rank LOCATION), C85 Gastwirth G=0.3*Q(1/3)+0.4*Q(0.5)+0.3*Q(2/3) (tercile L-estimator LOCATION), C84 Midhinge MH=(Q1+Q3)/2 (quartile LOCATION), C83 Tukey trimean TM=(Q1+2*Q2+Q3)/4 (quartile+median LOCATION). L_mean is a run-duration/persistence functional on a dichotomy, not a level/center functional.",
            "non_TP_vs_C87": "C87 TP=(1/(n-2))*sum I[(dx_{i-1})*(dx_i)<0] counts LOCAL PEAK/TROUGH REVERSALS of consecutive raw differences (triplet oscillation). L_mean dichotomizes vs median then measures mean CONTIGUOUS SAME-SIDE RUN DURATION — different operation (median dichotomy + run-length averaging) and different phenomenon (persistence/duration vs reversal frequency).",
            "vs_autocorr": "ACF(1) is LINEAR lag-1 covariance/correlation of the continuous series; L_mean operates on a BINARY dichotomized sequence and measures RUN DURATIONS (nonlinear persistence), not linear covariance.",
            "vs_C41C42C43_entropy": "Permutation/sample/Shannon entropy map patterns to symbol probabilities (information/complexity). L_mean is a single mean run-duration on a median dichotomy, not distributional entropy over ordinal symbols.",
            "vs_C82_AAD_C80_MAD": "AAD/MAD are SCALE/DISPERSION of deviations, not run-length persistence of a dichotomized sequence.",
            "vs_C66_C73_quantile_dispersions_asymmetries": "dichotomized-sequence run-duration measure, not cross-sectional quantile spread/asymmetry.",
            "vs_skewness_bowley_kelly_kurtosis": "distributional shape/asymmetry/tail, not run persistence.",
            "vs_C79_SarleBC_C45_CV_C51C74C75C76C78_inequality": "shape/scale/concentration, not temporal run-length persistence.",
            "vs_C23_other_RQV": "rolling mean run length (persistence/duration) on median-dichotomized volume path; different transform family.",
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
    out = REPORTS / f"real_quote_volume_mean_run_length_persistence_shock_mr_costed_oos_{TS}.json"
    out.write_text(json.dumps(artifact, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(out.relative_to(ROOT)), "sha256": sha256_file(out),
                      "oos_edge_proven": edge, "n_assets": len(per), "any_exposure": any_exp,
                      "all_pos": all_pos, "beats_bh": beats, "bh_mean": bh_mean,
                      "agg_net_sum": agg["oos_net_sum"]}, indent=2))


if __name__ == "__main__":
    main()
