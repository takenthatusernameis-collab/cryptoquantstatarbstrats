#!/usr/bin/env python3
"""Campaign #96 R-B (fail-closed, real data only): real_quote_volume-conditioned
Rolling Katz Fractal Dimension (KFD) shock MR on log-volume changes (real
Binance spot quote volume klines col 5) + real cached spot 1h.

PRE-STATED HYPOTHESIS (fixed before seeing OOS results): "Volume Katz FD Shock MR"
- For each asset, compute log-volume changes x_t = ln(v_t) - ln(v_{t-1}) (v_t =
  quote_volume_usdt, positive finite). Over a causal trailing lookback W=168h
  compute Katz Fractal Dimension KFD of the 1D planar curve with unit time steps:
    n = N-1  (steps)
    L = sum_{i=1}^{n} sqrt(1 + (x_i - x_{i-1})^2)   (planar curve length)
    a = L / n                                         (average step length)
    d = max_{i>=0} sqrt(i^2 + (x_i - x_0)^2)         (max diameter from first point)
    KFD = log10(n) / (log10(n) + log10(d/a))         (in [~0,1], higher ~ rougher)
  Trade causal z-score shocks of KFD (W=168, ZLB=168) as MR:
    if dz >= ENTRY_Z (1.25): SHORT  (fade unusually HIGH Katz FD / rougher geometry)
    if dz <= -ENTRY_Z (-1.25): LONG  (fade unusually LOW Katz FD / smoother geometry)
  Exit: |dz| < EXIT_Z (0.25) OR hold >= MAX_HOLD (12h) OR signal flips.
- Execution shift t -> t+1. Walk-forward: rolling 720/168/168 (train/test/step).
- Cost grid bps (fee,slip): [[0,0],[5,5],[10,10],[20,20],[40,40]]. Benchmark: B&H
  per asset (gross) on union of OOS WF windows.
- Pre-stated edge rule (fail-closed): oos_edge_proven=true IFF OOS exposure>0 AND
  for ALL cost-grid slices OOS net sum > 0 AND mean OOS net mean beats mean B&H OOS
  mean on same WF windows. Else false. No in-sample tuning, no threshold weakening.

DISTINCTNESS (vs C23/C40-C95, mechanically stated) — NON-LOCATION, NON-TP,
NON-WALD–WOLFOWITZ-RUNS, NON-MEAN-RUN-LENGTH-PERSISTENCE, NON-VARIANCE-RATIO,
NON-BDS, NON-OU/HL, NON-LZ76, NON-HJORTH-MOBILITY/COMPLEXITY, NON-DISPERSION,
NON-ENTROPY (incl. spectral entropy as Shannon-over-PSD), NON-SKEW/KURTOSIS,
NON-SINGLE-LAG-ACF, NON-HURST/RS, NON-HIGUCHI-FD:
- Katz FD uses TOTAL planar curve length L plus MAX diameter d from the first point
  (self-similarity ratio log(n)/(log(n)+log(d/a))); it is a single global
  length/diameter fractal-dimension value. No sign-change counting as FD input, no
  multi-interval resampling.
- NON-TP / NOT sign-change counting (vs turning-point rate C87 area): TP counts
  interior peaks/troughs as a rate statistic I[(x_i-x_{i-1})*(x_{i+1}-x_i)<0].
  Katz is a length/diameter fractal-dimension value — different object; this
  implementation does not count sign changes/reversals.
- NON-HIGUCHI (vs C95 Higuchi FD): Higuchi uses k-interval L(k) curve-length
  resampling/scaling and a log(L(k))-log(1/k) slope across k. Katz uses one total
  planar length L and one max diameter d (no k resampling/slope fit).
- NON-HJORTH (vs C94): no derivative variance ratios.
- NON-HURST/RS: not rescaled-range/long-memory scaling of cumulative deviations.
- NON-ENTROPY (Shannon/perm/sample/Renyi2/spectral): no p*log p / ordinal
  frequencies / template matches / PSD-bin probs.
- NON-LZ76 (C93): no phrase parsing/dictionary.
- NON-WW-runs (C88) / NON-mean-run-length (C89): no run/reversal counts/durations.
- NON-BDS (C91): no delay embedding/correlation integral.
- NON-VARIANCE-RATIO (C90): not multi-horizon variance scaling.
- NON-OU/HL (C92): no AR(1)/mean-reversion half-life timescale.
- NON-SINGLE-LAG-ACF: not a normalized covariance/correlation at any lag.
- NON-LOCATION (C83-C86) / NON-DISPERSION-SKEW-KURTOSIS.
- Grep-verified absent before implementation: no prior katz/kfd/planar.*fractal/
  max_diameter.*fd in reports/real_quote_volume_*costed_oos* or
  scripts/run_real_quote_volume_*costed_oos*.py.
- Data source identical (real Binance spot quote volume) but TRANSFORM is
  mechanically different: rolling Katz Fractal Dimension of log-volume changes.
"""
from __future__ import annotations

import hashlib
import json
import math
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
W_KFD, ZLB, ENTRY_Z, EXIT_Z, MAX_HOLD = 168, 168, 1.25, 0.25, 12
CAMPAIGN = 96
PRIOR_UNBLOCK = "reports/real_feed_unblock_status_20261106T130243Z.json"
PRIOR_UNBLOCK_SHA = "49699fad6ce626b2b3edf99650e21a5f305778c55b9b83e1980ddbdfd67a6d80"
PRIOR_REGISTRY = "reports/strategy_edge_registry_20261106T151843Z.json"
PRIOR_REGISTRY_SHA = "6ca9ab15e22c36314d616d3715c8db79222499d6b1db7bc1c60bf676d307ed3e"
PRIOR_C95_RB = "reports/real_quote_volume_higuchi_fd_shock_mr_costed_oos_20261106T151757Z.json"
PRIOR_C95_RB_SHA = "13b30af38961878eaf1fce6bdc0ac9ff7b7257ddf7e9060bb7d18d6ef8a4e90f"


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


def katz_fd(x: np.ndarray) -> float:
    """Katz Fractal Dimension of 1D planar curve (unit time steps). Fail-closed NaN."""
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    N = x.size
    n = N - 1
    if n < 2:
        return np.nan
    diffs = np.diff(x)
    L = float(np.sum(np.sqrt(1.0 + diffs * diffs)))  # planar curve length
    a = L / n
    if a <= 0.0 or not math.isfinite(a):
        return np.nan
    idx = np.arange(N, dtype=float)
    diam = np.sqrt(idx * idx + (x - x[0]) ** 2)
    d = float(np.max(diam))
    if d <= 0.0 or not math.isfinite(d):
        return np.nan
    denom = math.log10(n) + math.log10(d / a)
    if denom == 0.0 or not math.isfinite(denom):
        return np.nan
    kfd = math.log10(n) / denom
    if not math.isfinite(kfd):
        return np.nan
    return kfd


def rolling_kfd(x: np.ndarray, w: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    for i in range(w, len(x)):
        win = x[i - w + 1 : i + 1]
        if not np.isfinite(win).all() or len(win) < w:
            continue
        out[i] = katz_fd(win)
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
    dlogv = np.diff(logv, prepend=logv[0])
    dlogv[0] = 0.0
    feat = rolling_kfd(dlogv, W_KFD)
    dz = rolling_z(feat, ZLB)
    sig = np.zeros(n)
    cur = 0.0
    hold = 0
    warm = max(W_KFD, ZLB) + 4
    for i in range(warm, n):
        z = dz[i]
        if not np.isfinite(z):
            nxt = cur
            hold = hold + 1 if cur != 0 else 0
        else:
            desired = 0.0
            if z >= ENTRY_Z:
                desired = -1.0  # fade unusually HIGH Katz FD / rougher geometry shock
            elif z <= -ENTRY_Z:
                desired = 1.0   # fade unusually LOW Katz FD / smoother geometry shock
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
        "tool": "scripts/run_real_quote_volume_katz_fd_shock_mr_costed_oos.py",
        "generated_at_utc": TS,
        "campaign": CAMPAIGN,
        "prior_unblock": PRIOR_UNBLOCK,
        "prior_unblock_sha256": PRIOR_UNBLOCK_SHA,
        "prior_registry": PRIOR_REGISTRY,
        "prior_registry_sha256": PRIOR_REGISTRY_SHA,
        "prior_c95_rb": PRIOR_C95_RB,
        "prior_c95_rb_sha256": PRIOR_C95_RB_SHA,
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
            "id": "VOLUME_KATZ_FD_SHOCK_MR",
            "description": "Fade causal z-score shocks of rolling Katz Fractal Dimension (planar curve length L + max diameter d, unit time steps; KFD=log10(n)/(log10(n)+log10(d/a))) of log-volume changes (W=168) as geometric roughness shocks; t->t+1.",
            "kfd_window": W_KFD,
            "kfd_formula": "n=N-1; L=sum sqrt(1+dx^2); a=L/n; d=max_i sqrt(i^2+(x_i-x_0)^2); KFD=log10(n)/(log10(n)+log10(d/a))",
            "unit_time_step_convention": "time step = 1 bar (1h) for planar curve",
            "entry_z": ENTRY_Z,
            "exit_z": EXIT_Z,
            "max_hold": MAX_HOLD,
            "z_lookback": ZLB,
            "walkforward": {"train": TRAIN, "test": TEST, "step": STEP},
            "cost_grid_bps": COST_GRID,
            "benchmark": "buy_and_hold_gross_same_oos_windows",
        },
        "distinctness_mechanical": {
            "katz_fd": "Katz FD uses TOTAL planar curve length L plus MAX diameter d from the first point (self-similarity ratio log10(n)/(log10(n)+log10(d/a))); single global length/diameter fractal-dimension value. No sign-change counting as FD input, no multi-interval resampling.",
            "non_tp_not_sign_change_counting_vs_turning_point_rate": "TP counts interior peaks/troughs I[(x_i-x_{i-1})*(x_{i+1}-x_i)<0] as a rate statistic. Katz is a length/diameter fractal-dimension value — different object; implementation does not count sign changes/reversals.",
            "non_higuchi_vs_C95": "C95 Higuchi uses k-interval L(k) curve-length resampling/scaling and log(L(k))-log(1/k) slope across k. Katz uses one total planar length L and one max diameter d (no k resampling/slope fit).",
            "non_hjorth_vs_C94": "C94 Hjorth uses derivative variance ratios; Katz uses length/diameter, no derivatives/variance ratios.",
            "non_hurst_rs": "Not rescaled-range/long-memory scaling of cumulative deviations.",
            "non_entropy_vs_Shannon_perm_sample_Renyi2_spectral": "No p*log p, ordinal frequencies, template matches, or PSD-bin probs — not an information measure.",
            "non_lz76_vs_C93": "No phrase parsing/dictionary.",
            "non_WW_runs_vs_C88_non_mean_run_length_vs_C89": "No run/reversal counts or durations.",
            "non_bds_vs_C91": "No delay embedding, no correlation integral C_m, no V_m.",
            "non_variance_ratio_vs_C90": "Not multi-horizon variance scaling.",
            "non_ou_hl_vs_C92": "No AR(1) regression, no mean-reversion half-life timescale.",
            "non_single_lag_acf_explicit": "Not a normalized covariance/correlation at any lag.",
            "non_location_explicit": "NOT a location estimator (C83-C86).",
            "non_dispersion_skew_kurtosis": "Not dispersion magnitude and not skewness/Bowley/Kelly/kurtosis.",
            "grep_precheck": "grep -rn 'katz\\|kfd\\|planar.*fractal\\|max_diameter.*fd' reports/real_quote_volume_*costed_oos* scripts/run_real_quote_volume_*costed_oos*.py -> no prior Katz/KFD transform (verified before implementation).",
            "vs_C23_C40_C95": "Mechanically distinct rolling Katz Fractal Dimension (planar length + max diameter) transform; not in C23/C40-C95 families.",
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
    out = REPORTS / f"real_quote_volume_katz_fd_shock_mr_costed_oos_{TS}.json"
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
