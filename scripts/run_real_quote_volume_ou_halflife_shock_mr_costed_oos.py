#!/usr/bin/env python3
"""Campaign #92 R-B (fail-closed, real data only): real_quote_volume-conditioned
Rolling ORNSTEIN–UHLENBECK (OU) half-life / AR(1) mean-reversion SPEED shock MR on
real Binance spot quote volume (klines col 5) log-volume LEVELS + real cached spot 1h.

PRE-STATED HYPOTHESIS (fixed before seeing OOS results): "Volume OU Half-Life
Mean-Reversion Speed Shock MR"
- For each asset, define log-volume LEVELS x_t = ln(v_t) (v_t = quote_volume_usdt,
  positive finite). Over a causal trailing lookback W=168h fit the AR(1)/OU discrete
  regression on levels: Δx_t = a + b*x_{t-1} + e_t (OLS). Mean-reversion speed
  theta = -b. When theta > 0 and finite (mean-reverting), characteristic timescale
  HL = ln(2)/theta (bars). When theta <= 0 or unstable/non-finite, mark
  non-mean-reverting (NaN) — fail-closed, no fabrication.
- Causal z-score of HL (lookback ZLB=168h) over finite HL values. Trade OU
  half-life / mean-reversion SPEED SHOCKS as MR (fade extreme timescale shocks):
    if dz >= ENTRY_Z (1.25): SHORT  (fade unusually SLOW mean-reversion / long HL shock)
    if dz <= -ENTRY_Z (-1.25): LONG  (fade unusually FAST mean-reversion / short HL shock)
  Exit: |dz| < EXIT_Z (0.25) OR hold >= MAX_HOLD (12h) OR signal flips.
- Execution shift t -> t+1. Walk-forward: rolling 720/168/168 (train/test/step).
- Cost grid bps (fee,slip): [[0,0],[5,5],[10,10],[20,20],[40,40]]. Benchmark: B&H
  per asset (gross) on union of OOS WF windows.
- Pre-stated edge rule (fail-closed): oos_edge_proven=true IFF OOS exposure>0 AND
  for ALL cost-grid slices OOS net sum > 0 AND mean OOS net mean beats mean B&H OOS
  mean on same WF windows. Else false. No in-sample tuning, no threshold weakening.

DISTINCTNESS (vs C23/C40-C91, mechanically stated) — NON-LOCATION, NON-TP,
NON-WALD–WOLFOWITZ-RUNS, NON-MEAN-RUN-LENGTH-PERSISTENCE, NON-VARIANCE-RATIO,
NON-BDS, NON-DISPERSION, NON-ENTROPY, NON-SKEW/KURTOSIS, NON-SINGLE-LAG-ACF TRANSFORM:
- OU half-life HL = ln(2)/theta, theta=-b from the parametric AR(1) regression
  Δx_t = a + b*x_{t-1} + e_t on log-volume LEVELS, is a CONTINUOUS-LEVEL
  MEAN-REVERSION SPEED / CHARACTERISTIC TIMESCALE (a rate/half-life). It is derived
  from a regression on levels (estimating the pull-back coefficient b) and converted
  to a timescale — mechanically a parametric reversion-speed/half-life measure, NOT
  a correlation coefficient, NOT a variance ratio, NOT an embedding-space integral,
  NOT a dichotomized run/duration/count statistic, NOT a reversal count, NOT entropy.
- NON-BDS (vs C91): C91 BDS V_m=C_m(eps)-C_1(eps)^m is a CORRELATION-INTEGRAL /
  EMBEDDING-DIMENSION NONLINEAR-INDEPENDENCE test on log-volume CHANGES (m-dimensional
  delay-embedding pair proximity). OU/HL is a parametric AR(1) LEVELS regression
  yielding a reversion SPEED/timescale (theta, HL). Different input transform
  (levels/regression vs change-embeddings), different functional (regression
  coefficient -> half-life vs correlation integral C_m-C_1^m), different phenomenon
  (linear mean-reversion speed of the level process vs nonlinear/higher-order
  embedding dependence).
- NON-VARIANCE-RATIO (vs C90): C90 VR(q)=Var(r^(q))/(q*Var(r)) is a multi-horizon
  VARIANCE-SCALING ratio (second-moment). OU/HL estimates a LEVEL pull-back rate b
  from an AR(1) regression and maps to a half-life — a timescale/reversion-speed,
  not a variance ratio across horizons.
- NON-MEAN-RUN-LENGTH-PERSISTENCE (vs C89): C89 L_mean=n_kept/R is mean DURATION of
  contiguous runs on a MEDIAN-DICHOTOMIZED sequence. OU/HL is a continuous parametric
  regression-derived timescale on levels — no dichotomy, no run lengths/counts.
- NON-WW-RUNS (vs C88): C88 Z_WW is a standardized TOTAL-RUN-COUNT randomness
  statistic on a median dichotomy. OU/HL is not a run count and uses no dichotomy.
- NON-TP (vs C87): C87 TP counts LOCAL PEAK/TROUGH REVERSALS of consecutive raw
  differences (triplet oscillation). OU/HL is a regression-derived reversion
  timescale from levels, not a reversal frequency.
- NON-SINGLE-LAG-ACF (explicit): a raw single-lag linear ACF coefficient (used
  directly as a correlation signal in ACF families) is a normalized covariance at
  lag k. OU/HL is obtained by fitting the AR(1) LEVELS regression Δx=a+b*x_{t-1}+e
  (including an intercept on the level) and transforming the pull-back coefficient
  to a MEAN-REVERSION SPEED/HALF-LIFE timescale (HL=ln(2)/(-b)) with a
  mean-reversion gate (theta>0). This is a regression-derived parametric
  characteristic time (rate/half-life of the level process), mechanically distinct
  from using a raw single-lag ACF correlation value directly as the signal.
- NON-LOCATION (explicitly NOT used): not C86 Hodges–Lehmann, C85 Gastwirth,
  C84 Midhinge, C83 Tukey trimean. OU/HL is a reversion-speed/timescale, not a level.
- NON-DISPERSION/ENTROPY/SKEW/KURTOSIS: not MAD/AAD/IQR/IDR/range/semi-variance/
  Gini/Theil/CV (dispersion magnitude), not Shannon/permutation/sample/Renyi
  entropy (information/complexity), not skewness/Bowley/Kelly/kurtosis (shape).
  OU/HL is a parametric reversion timescale.
- Data source identical (real Binance spot quote volume) but TRANSFORM is
  mechanically different: rolling OU half-life (AR(1) regression on log-volume
  levels -> reversion speed/timescale).
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
W_OU, ZLB, ENTRY_Z, EXIT_Z, MAX_HOLD = 168, 168, 1.25, 0.25, 12
CAMPAIGN = 92
PRIOR_UNBLOCK = "reports/real_feed_unblock_status_20261106T130243Z.json"
PRIOR_REGISTRY = "reports/strategy_edge_registry_20261106T142235Z.json"
PRIOR_REGISTRY_SHA = "8e50e58d73f52f7d3cfedda461daacb1847d0e6b0402717bc71dbd2e5f2300"
PRIOR_C91_RB = "reports/real_quote_volume_bds_nonlinear_independence_shock_mr_costed_oos_20261106T142103Z.json"
PRIOR_C91_RB_SHA = "c8625a2ab93c15f780aa8f1ac17eeaf2b48fd99f2ad42b096d4b8df3f33a6"


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


def ou_halflife(x: np.ndarray) -> float:
    """OU half-life from AR(1) regression Δx_t = a + b*x_{t-1}+e on levels x.
    Returns HL=ln(2)/theta when theta=-b > 0 (mean-reverting); else NaN."""
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    if len(x) < 30:
        return np.nan
    dx = np.diff(x)
    xlag = x[:-1]
    if len(dx) < 20:
        return np.nan
    # OLS with intercept: dx = a + b*xlag
    X = np.column_stack([np.ones(len(xlag)), xlag])
    try:
        beta, _, rank, _ = np.linalg.lstsq(X, dx, rcond=None)
    except Exception:
        return np.nan
    if rank < 2 or not np.all(np.isfinite(beta)):
        return np.nan
    b = float(beta[1])
    theta = -b
    if not np.isfinite(theta) or theta <= 1e-12:
        return np.nan
    hl = np.log(2.0) / theta
    if not np.isfinite(hl) or hl <= 0 or hl > 1e6:
        return np.nan
    return float(hl)


def rolling_ou_hl(logv: np.ndarray, w: int) -> np.ndarray:
    out = np.full(len(logv), np.nan)
    for i in range(w, len(logv)):
        out[i] = ou_halflife(logv[i - w : i])
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
    logv = np.log(v.values.astype(float))
    feat = rolling_ou_hl(logv, W_OU)
    dz = rolling_z(feat, ZLB)
    sig = np.zeros(n)
    cur = 0.0
    hold = 0
    warm = max(W_OU, ZLB) + 4
    for i in range(warm, n):
        z = dz[i]
        if not np.isfinite(z):
            nxt = cur
            hold = hold + 1 if cur != 0 else 0
        else:
            desired = 0.0
            if z >= ENTRY_Z:
                desired = -1.0  # fade unusually SLOW mean-reversion (long HL) shock
            elif z <= -ENTRY_Z:
                desired = 1.0   # fade unusually FAST mean-reversion (short HL) shock
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
        "tool": "scripts/run_real_quote_volume_ou_halflife_shock_mr_costed_oos.py",
        "generated_at_utc": TS,
        "campaign": CAMPAIGN,
        "prior_unblock": PRIOR_UNBLOCK,
        "prior_registry": PRIOR_REGISTRY,
        "prior_registry_sha256": PRIOR_REGISTRY_SHA,
        "prior_c91_rb": PRIOR_C91_RB,
        "prior_c91_rb_sha256": PRIOR_C91_RB_SHA,
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
            "id": "VOLUME_OU_HALFLIFE_MEAN_REVERSION_SPEED_SHOCK_MR",
            "description": "Fade causal z-score shocks of rolling OU half-life HL=ln(2)/(-b) from AR(1) regression Δx=a+b*x_{t-1}+e on log-volume LEVELS (theta=-b>0 => mean-reverting; NaN otherwise, W=168) as mean-reversion speed/timescale shocks; t->t+1.",
            "ou_window": W_OU,
            "entry_z": ENTRY_Z,
            "exit_z": EXIT_Z,
            "max_hold": MAX_HOLD,
            "z_lookback": ZLB,
            "walkforward": {"train": TRAIN, "test": TEST, "step": STEP},
            "cost_grid_bps": COST_GRID,
            "benchmark": "buy_and_hold_gross_same_oos_windows",
        },
        "distinctness_mechanical": {
            "ou_halflife": "OU half-life HL=ln(2)/theta, theta=-b from parametric AR(1) regression Δx_t=a+b*x_{t-1}+e on log-volume LEVELS. A CONTINUOUS-LEVEL MEAN-REVERSION SPEED / CHARACTERISTIC TIMESCALE (rate/half-life) derived from a regression on levels (pull-back coefficient b -> timescale), not a correlation coefficient, variance ratio, embedding-space integral, dichotomized run/duration/count, reversal count, or entropy.",
            "non_bds_vs_C91": "C91 BDS V_m=C_m-C_1^m is a CORRELATION-INTEGRAL/EMBEDDING-DIMENSION NONLINEAR-INDEPENDENCE test on log-volume CHANGES (m-dim delay-embedding pair proximity). OU/HL is a parametric AR(1) LEVELS regression yielding reversion SPEED/timescale (theta,HL). Different input (levels/regression vs change-embeddings), functional (regression coeff->half-life vs C_m-C_1^m), phenomenon (linear mean-reversion speed of level process vs nonlinear/higher-order embedding dependence).",
            "non_variance_ratio_vs_C90": "C90 VR(q)=Var(r^(q))/(q*Var(r)) is multi-horizon VARIANCE-SCALING (second-moment). OU/HL estimates LEVEL pull-back rate b via AR(1) regression and maps to half-life — a timescale/reversion-speed, not a variance ratio across horizons.",
            "non_mean_run_length_persistence_vs_C89": "C89 L_mean=n_kept/R is mean DURATION of contiguous runs on a MEDIAN-DICHOTOMIZED sequence. OU/HL is a continuous parametric regression-derived timescale on levels — no dichotomy, no run lengths/counts.",
            "non_WW_runs_vs_C88": "C88 Z_WW is a standardized TOTAL-RUN-COUNT randomness statistic on a median dichotomy. OU/HL is not a run count and uses no dichotomy.",
            "non_TP_vs_C87": "C87 TP counts local peak/trough REVERSALS of consecutive raw differences (triplet oscillation). OU/HL is a regression-derived reversion timescale from levels, not a reversal frequency.",
            "non_single_lag_acf_explicit": "Raw single-lag linear ACF (ACF families) is a normalized covariance at lag k used directly as a correlation signal. OU/HL fits AR(1) LEVELS regression Δx=a+b*x_{t-1}+e (with intercept on level) and transforms pull-back coefficient to a MEAN-REVERSION SPEED/HALF-LIFE (HL=ln(2)/(-b), theta>0 gate). A regression-derived parametric characteristic time (rate/half-life of the level process), mechanically distinct from a raw single-lag ACF correlation value used directly.",
            "non_location_explicit": "NOT a location estimator. Distinct from C86 Hodges–Lehmann, C85 Gastwirth, C84 Midhinge, C83 Tukey trimean. OU/HL is a reversion-speed/timescale, not a level.",
            "non_dispersion_entropy_skew_kurtosis": "Not MAD/AAD/IQR/IDR/range/semi-variance/Gini/Theil/CV (dispersion magnitude), not Shannon/permutation/sample/Renyi entropy (information/complexity), not skewness/Bowley/Kelly/kurtosis (shape). OU/HL is a parametric reversion timescale.",
            "vs_C23_C40_C91": "Mechanically distinct rolling OU half-life (AR(1) regression on log-volume levels -> reversion speed/timescale) transform; not in C23/C40-C91 families.",
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
    out = REPORTS / f"real_quote_volume_ou_halflife_shock_mr_costed_oos_{TS}.json"
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
