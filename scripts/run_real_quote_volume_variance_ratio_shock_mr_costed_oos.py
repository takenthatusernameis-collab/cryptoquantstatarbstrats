#!/usr/bin/env python3
"""Campaign #90 R-B (fail-closed, real data only): real_quote_volume-conditioned
Rolling VARIANCE-RATIO (Lo/Craig–MacKinlay style VR(q) on log-volume changes)
mean-reversion/random-walk-deviation shock MR on real Binance spot quote volume
(klines col 5) + real cached spot 1h.

PRE-STATED HYPOTHESIS (fixed before seeing OOS results): "Volume Variance-Ratio MR Shock"
- For each asset, define log-volume first differences r_t = ln(v_t) - ln(v_{t-1})
  (v_t = quote_volume_usdt, positive finite). Over a causal trailing lookback
  W_VR=168h compute:
    VR(q) = Var(r^(q)_t over window) / (q * Var(r_t over window)),
  where r^(q)_t = sum_{j=0}^{q-1} r_{t-j} are overlapping q-horizon aggregated
  returns, q=24h. Under a random-walk null VR(q)=1; VR(q)<1 indicates
  mean-reverting/negatively-serially-correlated structure across horizon q;
  VR(q)>1 indicates trending/persistent structure.
- Causal z-score of VR(q) (lookback ZLB=168h). Trade VR MEAN-REVERSION SHOCKS
  (deviations of random-walk/variance structure from its recent norm) as MR:
    if dz >= ENTRY_Z (1.25): SHORT  (fade unusually high VR/persistence shock)
    if dz <= -ENTRY_Z (-1.25): LONG  (fade unusually low VR/mean-reversion shock)
  Exit: |dz| < EXIT_Z (0.25) OR hold >= MAX_HOLD (12h) OR signal flips.
- Execution shift t -> t+1. Walk-forward: rolling 720/168/168 (train/test/step).
- Cost grid bps (fee,slip): [[0,0],[5,5],[10,10],[20,20],[40,40]]. Benchmark: B&H
  per asset (gross) on union of OOS WF windows.
- Pre-stated edge rule (fail-closed): oos_edge_proven=true IFF OOS exposure>0 AND
  for ALL cost-grid slices OOS net sum > 0 AND mean OOS net mean beats mean B&H OOS
  mean on same WF windows. Else false. No in-sample tuning, no threshold weakening.

DISTINCTNESS (vs C23/C40-C89, mechanically stated) — NON-LOCATION, NON-TP,
NON-WALD–WOLFOWITZ-RUNS, NON-MEAN-RUN-LENGTH-PERSISTENCE, NON-DISPERSION,
NON-ENTROPY, NON-SKEW/KURTOSIS, NON-AUTOCORR TRANSFORM:
- VR(q)=Var(r^(q))/(q*Var(r)) is a VARIANCE-RATIO / RANDOM-WALK-DEVIATION test
  across aggregation HORIZON q (Lo/Craig–MacKinlay family): it compares q-horizon
  aggregated variance to q times 1-step variance. It answers "does variance scale
  linearly with horizon (random walk) or show multi-horizon mean reversion/
  persistence?" — a SPECTRAL/SCALING variance functional across horizons, NOT a
  location, NOT a run-count/run-duration on a dichotomy, NOT a single-lag linear
  autocorrelation coefficient, NOT a dispersion level of deviations, NOT entropy.
- NON-MEAN-RUN-LENGTH-PERSISTENCE (vs C89): C89 L_mean=n_kept/R is the mean
  DURATION of contiguous above/below-median runs on a MEDIAN-DICHOTOMIZED
  sequence (run-length persistence). VR(q) operates on CONTINUOUS log-volume
  CHANGES, aggregates over horizon q, and forms a VARIANCE RATIO across
  horizons. Different object (binary dichotomy run lengths vs continuous-change
  variance scaling), different functional (duration average vs q-horizon variance
  ratio), different phenomenon (run persistence vs random-walk variance scaling).
- NON-WW-RUNS (vs C88): C88 Z_WW=(R-mu_R)/sigma_R is a STANDARDIZED TOTAL-RUN-
  COUNT randomness statistic on a median dichotomy (random-expectation null).
  VR(q) is a continuous multi-horizon variance ratio — no dichotomy, no run
  count, no WW null normalization.
- NON-TP (vs C87): C87 TP=(1/(n-2))*sum I[(dx_{i-1})*(dx_i)<0] counts LOCAL
  PEAK/TROUGH REVERSALS of consecutive raw differences (triplet oscillation).
  VR(q) aggregates returns over horizon q and compares variances — different
  operation (horizon aggregation + variance ratio) and different phenomenon
  (multi-horizon variance scaling vs reversal frequency).
- NON-LOCATION (explicitly NOT used): distinct from exhausted location family —
  C86 Hodges–Lehmann HL=median{(x_i+x_j)/2} (Walsh-average-median rank
  LOCATION), C85 Gastwirth G=0.3*Q(1/3)+0.4*Q(0.5)+0.3*Q(2/3) (tercile
  L-estimator LOCATION), C84 Midhinge MH=(Q1+Q3)/2 (quartile LOCATION), C83
  Tukey trimean TM=(Q1+2*Q2+Q3)/4 (quartile+median LOCATION). VR(q) is a
  variance ratio/scaling functional, not a level/center functional.
- NON-AUTOCORR (vs ACF/serial correlation families): ACF(k) is a SINGLE-LAG
  LINEAR covariance/correlation coefficient rho_k = Cov(r_t,r_{t-k})/Var(r_t).
  VR(q) = 1 + 2*sum_{j=1}^{q-1}(1-j/q)*rho_j is a WEIGHTED SUM OF MULTI-LAG
  autocorrelations / a variance-scaling ratio across horizon q (a joint
  multi-horizon structure test), not a single-lag linear ACF coefficient used as
  a direct signal. The transform/signal is the horizon variance ratio (and its
  causal z), mechanically distinct from single-lag ACF features.
- NON-DISPERSION (vs C80 MAD, C82 AAD, C66-C73 quantile dispersions/IDR/IQR/
  range/semi-var/Gini/Theil/CV region): those measure cross-sectional/level
  DISPERSION (scale of deviations or spreads) of a window. VR(q) is a RATIO of
  q-horizon to 1-horizon VARIANCE (a scaling/structure relation across
  horizons), not a dispersion magnitude.
- NON-ENTROPY (vs C41/C42/C43 Shannon/permutation/sample/Renyi entropy):
  entropy maps patterns/symbols to PROBABILITIES (information/complexity
  distributional measures). VR(q) is a moment/variance-scaling ratio across
  horizons, not distributional entropy.
- NON-SKEW/KURTOSIS (vs skewness/Bowley/Kelly/kurtosis families): shape/
  asymmetry/tail moments or quantile-ratio asymmetries; VR(q) is a variance-
  scaling structure test, not shape.
- Data source identical (real Binance spot quote volume) but TRANSFORM is
  mechanically different: rolling variance ratio VR(q) on log-volume changes.
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
Q, W_VR, ZLB, ENTRY_Z, EXIT_Z, MAX_HOLD = 24, 168, 168, 1.25, 0.25, 12
CAMPAIGN = 90
PRIOR_UNBLOCK = "reports/real_feed_unblock_status_20261106T130243Z.json"
PRIOR_REGISTRY = "reports/strategy_edge_registry_20261106T131733Z.json"
PRIOR_REGISTRY_SHA = "b7f2ee34ccaf3cafcabec24c58ace5f93b7250d9ae18196d30bba40be8713661"
PRIOR_C89_RB = "reports/real_quote_volume_mean_run_length_persistence_shock_mr_costed_oos_20261106T131620Z.json"


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


def variance_ratio_window(r: np.ndarray, q: int) -> float:
    """VR(q)=Var(r^q)/(q*Var(r)) on 1d return window r (causal)."""
    r = np.asarray(r, dtype=float)
    r = r[np.isfinite(r)]
    if r.size < max(q + 10, 30):
        return np.nan
    var1 = np.var(r, ddof=1)
    if var1 <= 1e-18 or not np.isfinite(var1):
        return np.nan
    rq = np.convolve(r, np.ones(q, dtype=float), mode="valid")
    if rq.size < 5:
        return np.nan
    varq = np.var(rq, ddof=1)
    if not np.isfinite(varq) or varq < 0:
        return np.nan
    vr = varq / (q * var1)
    return float(vr) if np.isfinite(vr) else np.nan


def rolling_vr(logv: np.ndarray, w: int, q: int) -> np.ndarray:
    out = np.full(len(logv), np.nan)
    r_all = np.diff(logv)  # length n-1, r_all[i-1] corresponds to i
    for i in range(w, len(logv)):
        # use returns up to i-1 => logv differences over [i-w, i] -> w returns
        win_r = r_all[i - w : i]
        win_r = win_r[np.isfinite(win_r)]
        out[i] = variance_ratio_window(win_r, q)
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
    logv = np.log(vv)
    feat = rolling_vr(logv, W_VR, Q)
    dz = rolling_z(feat, ZLB)
    sig = np.zeros(n)
    cur = 0.0
    hold = 0
    warm = max(W_VR, ZLB, Q) + 4
    for i in range(warm, n):
        z = dz[i]
        if not np.isfinite(z):
            nxt = cur
            hold = hold + 1 if cur != 0 else 0
        else:
            desired = 0.0
            if z >= ENTRY_Z:
                desired = -1.0  # fade high VR/persistence shock
            elif z <= -ENTRY_Z:
                desired = 1.0   # fade low VR/mean-reversion shock
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
        "tool": "scripts/run_real_quote_volume_variance_ratio_shock_mr_costed_oos.py",
        "generated_at_utc": TS,
        "campaign": CAMPAIGN,
        "prior_unblock": PRIOR_UNBLOCK,
        "prior_registry": PRIOR_REGISTRY,
        "prior_registry_sha256": PRIOR_REGISTRY_SHA,
        "prior_c89_rb": PRIOR_C89_RB,
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
            "id": "VOLUME_VARIANCE_RATIO_SHOCK_MR",
            "description": "Fade causal z-score shocks of variance ratio VR(q)=Var(r^(q))/(q*Var(r)) on log-volume changes (q=24, W_VR=168) as mean-reversion/random-walk-deviation shocks; t->t+1.",
            "q_horizon": Q,
            "vr_window": W_VR,
            "entry_z": ENTRY_Z,
            "exit_z": EXIT_Z,
            "max_hold": MAX_HOLD,
            "z_lookback": ZLB,
            "walkforward": {"train": TRAIN, "test": TEST, "step": STEP},
            "cost_grid_bps": COST_GRID,
            "benchmark": "buy_and_hold_gross_same_oos_windows",
        },
        "distinctness_mechanical": {
            "variance_ratio": "VR(q)=Var(r^(q))/(q*Var(r)) on continuous log-volume changes r_t=ln(v_t)-ln(v_{t-1}), overlapping q-horizon aggregation r^(q). Random-walk null VR=1; VR<1 mean reversion, VR>1 persistence across horizon q. A multi-horizon VARIANCE-SCALING / random-walk-deviation functional (Lo/Craig–MacKinlay family), not location, not run-count/run-duration dichotomy, not single-lag ACF, not dispersion magnitude, not entropy.",
            "non_mean_run_length_persistence_vs_C89": "C89 L_mean=n_kept/R is mean DURATION of contiguous above/below-median runs on a MEDIAN-DICHOTOMIZED sequence (run-length persistence). VR(q) uses CONTINUOUS log-volume CHANGES, aggregates over horizon q, and forms a VARIANCE RATIO across horizons — different object, functional, phenomenon (run persistence vs multi-horizon variance scaling).",
            "non_WW_runs_vs_C88": "C88 Z_WW=(R-mu_R)/sigma_R is a standardized TOTAL-RUN-COUNT randomness statistic on a median dichotomy (random-expectation null). VR(q) is a continuous multi-horizon variance ratio — no dichotomy, no run count, no WW null normalization.",
            "non_TP_vs_C87": "C87 TP counts local peak/trough REVERSALS of consecutive raw differences (triplet oscillation). VR(q) aggregates returns over horizon q and compares variances — multi-horizon variance scaling vs reversal frequency.",
            "non_location_explicit": "NOT a location estimator. Distinct from C86 Hodges–Lehmann HL (Walsh-average-median rank LOCATION), C85 Gastwirth (tercile L-estimator LOCATION), C84 Midhinge (quartile LOCATION), C83 Tukey trimean (quartile+median LOCATION). VR(q) is a variance ratio/scaling functional, not a level/center.",
            "non_autocorr": "ACF(k) is a SINGLE-LAG linear covariance/correlation coefficient. VR(q)=1+2*sum_{j=1}^{q-1}(1-j/q)*rho_j is a weighted MULTI-LAG/multi-horizon variance-scaling ratio (joint structure across horizon q), not a single-lag ACF signal.",
            "non_dispersion": "MAD/AAD/IQR/IDR/range/semi-variance/Gini/Theil/CV measure dispersion MAGNITUDE of a window. VR(q) is a RATIO of q-horizon to 1-horizon variance (scaling/structure relation across horizons), not a dispersion level.",
            "non_entropy": "Shannon/permutation/sample/Renyi entropy are distributional symbol-probability (information/complexity) measures. VR(q) is a moment/variance-scaling ratio across horizons.",
            "non_skew_kurtosis": "Skewness/Bowley/Kelly/kurtosis are shape/asymmetry/tail; VR(q) is a variance-scaling structure test.",
            "vs_C23_C40_C89": "Mechanically distinct rolling variance-ratio (multi-horizon variance scaling) transform on log-volume changes; not in C23/C40-C89 families (location/TP/WW-runs/mean-run-length/dispersion/entropy/skew/kurtosis/autocorr/volume-divergence).",
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
    out = REPORTS / f"real_quote_volume_variance_ratio_shock_mr_costed_oos_{TS}.json"
    out.write_text(json.dumps(artifact, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps({
        "out": str(out.relative_to(ROOT)),
        "sha256": sha256_file(out),
        "oos_edge_proven": edge,
        "n_assets": len(per),
        "any_exposure": any_exp,
        "all_pos": all_pos,
        "beats_bh": beats,
        "bh_mean": bh_mean,
        "agg_net_sum": agg["oos_net_sum"],
    }, indent=2))


if __name__ == "__main__":
    main()
