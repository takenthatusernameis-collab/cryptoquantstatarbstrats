#!/usr/bin/env python3
"""Campaign #95 R-B (fail-closed, real data only): real_quote_volume-conditioned
Rolling Higuchi Fractal Dimension (HFD) shock MR on log-volume changes (real
Binance spot quote volume klines col 5) + real cached spot 1h.

PRE-STATED HYPOTHESIS (fixed before seeing OOS results): "Volume Higuchi FD
Shock MR"
- For each asset, compute log-volume changes x_t = ln(v_t) - ln(v_{t-1}) (v_t =
  quote_volume_usdt, positive finite). Over a causal trailing lookback W=168h
  compute Higuchi Fractal Dimension D (1 <= D <= 2, curve-length scaling):
    for k=1..k_max, Lm(k) = (sum_{i=1}^{floor((N-m)/k)} |x(m+i*k)-x(m+(i-1)*k)|) * (N-1)/(floor((N-m)/k)*k)
    L(k) = mean_m Lm(k); D = slope of linear fit log(L(k)) ~ log(1/k).
  Trade causal z-score shocks of HFD (W=168, ZLB=168) as MR:
    if dz >= ENTRY_Z (1.25): SHORT  (fade unusually HIGH fractal dimension / geometric roughness)
    if dz <= -ENTRY_Z (-1.25): LONG  (fade unusually LOW fractal dimension / smoother geometry)
  Exit: |dz| < EXIT_Z (0.25) OR hold >= MAX_HOLD (12h) OR signal flips.
- Execution shift t -> t+1. Walk-forward: rolling 720/168/168 (train/test/step).
- Cost grid bps (fee,slip): [[0,0],[5,5],[10,10],[20,20],[40,40]]. Benchmark: B&H
  per asset (gross) on union of OOS WF windows.
- Pre-stated edge rule (fail-closed): oos_edge_proven=true IFF OOS exposure>0 AND
  for ALL cost-grid slices OOS net sum > 0 AND mean OOS net mean beats mean B&H OOS
  mean on same WF windows. Else false. No in-sample tuning, no threshold weakening.

DISTINCTNESS (vs C23/C40-C94, mechanically stated) — NON-LOCATION, NON-TP,
NON-WALD–WOLFOWITZ-RUNS, NON-MEAN-RUN-LENGTH-PERSISTENCE, NON-VARIANCE-RATIO,
NON-BDS, NON-OU/HL, NON-LZ76, NON-HJORTH-MOBILITY/COMPLEXITY, NON-DISPERSION,
NON-ENTROPY (incl. spectral entropy as Shannon-over-PSD), NON-SKEW/KURTOSIS,
NON-SINGLE-LAG-ACF, NON-HURST/RS:
- Higuchi Fractal Dimension estimates geometric curve-length scaling D via
  L(k) ~ k^{-D} (multi-interval k resampling of the curve). D measures trajectory
  geometric roughness/space-filling over scales k — NOT a probability-distribution
  information measure (no p*log p, no ordinal-pattern frequencies), NOT derivative
  variance ratios.
- NON-HJORTH (vs C94 Mobility/Complexity): Hjorth uses variance ratios of
  derivatives sqrt(var(dx)/var(x)) / variance-of-higher-differences (time-domain
  second-moment shape). HFD uses MULTI-INTERVAL CURVE-LENGTH RESAMPLING and a
  log(L(k))-log(1/k) scaling slope across k — different mathematical object and
  estimator (geometric scaling vs derivative variance ratios).
- NON-HURST/RS: Hurst/RS is rescaled-range (R/S) or related long-memory scaling of
  cumulative deviations. HFD is Higuchi curve-length scaling of the series itself;
  different estimator and phenomenon (curve roughness vs long-memory range scaling).
- NON-ENTROPY (vs Shannon/permutation/sample/Renyi2 and spectral-entropy-as-Shannon
  -over-PSD): entropy families are distribution/information measures (p*log p,
  ordinal pattern frequencies, template matches, PSD bin probs). HFD is geometric
  multi-scale curve-length scaling — not an information measure.
- NON-LZ76 (vs C93): no phrase parsing/dictionary/parsing.
- NON-WW-runs (vs C88) / NON-mean-run-length (vs C89) / NON-TP (vs C87): no run/
  reversal counts or durations.
- NON-BDS (vs C91): no delay embedding, no correlation integral C_m, no V_m.
- NON-VARIANCE-RATIO (vs C90): VR(q) is multi-horizon variance scaling of returns;
  HFD is multi-k curve-length scaling slope — different construction.
- NON-OU/HL (vs C92): no AR(1) regression, no mean-reversion half-life timescale.
- NON-SINGLE-LAG-ACF: not a normalized covariance/correlation at any lag.
- NON-LOCATION (C83-C86): not a location estimator.
- NON-DISPERSION/SKEW/KURTOSIS: not MAD/AAD/IQR/IDR/range/semi-variance/Gini/Theil/
  CV, not skewness/Bowley/Kelly/kurtosis.
- Data source identical (real Binance spot quote volume) but TRANSFORM is
  mechanically different: rolling Higuchi Fractal Dimension of log-volume changes.
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
W_HFD, K_MAX, ZLB, ENTRY_Z, EXIT_Z, MAX_HOLD = 168, 8, 168, 1.25, 0.25, 12
CAMPAIGN = 95
PRIOR_UNBLOCK = "reports/real_feed_unblock_status_20261106T130243Z.json"
PRIOR_UNBLOCK_SHA = "49699fad6ce626b2b3edf99650e21a5f305778c55b9b83e1980ddbdfd67a6d80"
PRIOR_REGISTRY = "reports/strategy_edge_registry_20261106T150449Z.json"
PRIOR_REGISTRY_SHA = "d4e35f01d538fa5471220642855c6cb2bfc0b1d876c4be9d5b79f5b2add444b5"
PRIOR_C94_RB = "reports/real_quote_volume_hjorth_mobility_shock_mr_costed_oos_20261106T150449Z.json"
PRIOR_C94_RB_SHA = "35aec05286b79246be83268ecc6992676f542861d09879cf56cb97f06bf97546"


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


def higuchi_fd(x: np.ndarray, k_max: int = 8) -> float:
    """Higuchi Fractal Dimension of 1D series x. Fail-closed NaN on degenerate."""
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    N = x.size
    if N < max(24, k_max * 4):
        return np.nan
    k_max = min(k_max, max(2, N // 4))
    lk = []
    ks = []
    for k in range(1, k_max + 1):
        lm = []
        for m in range(1, k + 1):
            n_m = (N - m) // k
            if n_m < 2:
                continue
            idxs = m - 1 + np.arange(0, n_m + 1) * k
            diffs = np.abs(np.diff(x[idxs]))
            if diffs.size == 0:
                continue
            length = diffs.sum() * (N - 1) / (n_m * k)
            lm.append(length)
        if lm:
            mean_l = float(np.mean(lm))
            if mean_l > 0 and math.isfinite(mean_l):
                lk.append(math.log(mean_l))
                ks.append(math.log(1.0 / k))
    if len(ks) < 3:
        return np.nan
    ks_a = np.asarray(ks)
    lk_a = np.asarray(lk)
    # linear fit
    A = np.vstack([ks_a, np.ones_like(ks_a)]).T
    slope, _ = np.linalg.lstsq(A, lk_a, rcond=None)[0]
    d = float(slope)
    if not math.isfinite(d):
        return np.nan
    return d


def rolling_hfd(x: np.ndarray, w: int, k_max: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    for i in range(w, len(x)):
        win = x[i - w + 1 : i + 1]
        if not np.isfinite(win).all() or len(win) < w:
            continue
        out[i] = higuchi_fd(win, k_max=k_max)
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
    feat = rolling_hfd(dlogv, W_HFD, K_MAX)
    dz = rolling_z(feat, ZLB)
    sig = np.zeros(n)
    cur = 0.0
    hold = 0
    warm = max(W_HFD, ZLB) + 4
    for i in range(warm, n):
        z = dz[i]
        if not np.isfinite(z):
            nxt = cur
            hold = hold + 1 if cur != 0 else 0
        else:
            desired = 0.0
            if z >= ENTRY_Z:
                desired = -1.0  # fade unusually HIGH HFD / geometric roughness shock
            elif z <= -ENTRY_Z:
                desired = 1.0   # fade unusually LOW HFD / smoother geometry shock
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
        "tool": "scripts/run_real_quote_volume_higuchi_fd_shock_mr_costed_oos.py",
        "generated_at_utc": TS,
        "campaign": CAMPAIGN,
        "prior_unblock": PRIOR_UNBLOCK,
        "prior_unblock_sha256": PRIOR_UNBLOCK_SHA,
        "prior_registry": PRIOR_REGISTRY,
        "prior_registry_sha256": PRIOR_REGISTRY_SHA,
        "prior_c94_rb": PRIOR_C94_RB,
        "prior_c94_rb_sha256": PRIOR_C94_RB_SHA,
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
            "id": "VOLUME_HIGUCHI_FD_SHOCK_MR",
            "description": "Fade causal z-score shocks of rolling Higuchi Fractal Dimension (curve-length scaling L(k)~k^{-D} over k=1..k_max) of log-volume changes (W=168) as geometric roughness shocks; t->t+1.",
            "hfd_window": W_HFD,
            "hfd_k_max": K_MAX,
            "entry_z": ENTRY_Z,
            "exit_z": EXIT_Z,
            "max_hold": MAX_HOLD,
            "z_lookback": ZLB,
            "walkforward": {"train": TRAIN, "test": TEST, "step": STEP},
            "cost_grid_bps": COST_GRID,
            "benchmark": "buy_and_hold_gross_same_oos_windows",
        },
        "distinctness_mechanical": {
            "higuchi_fd": "Higuchi Fractal Dimension estimates geometric curve-length scaling D via L(k) ~ k^{-D} (multi-interval k resampling of the curve) and slope of log(L(k)) vs log(1/k). D measures trajectory geometric roughness/space-filling over scales k — NOT a probability-distribution information measure (no p*log p) and NOT derivative variance ratios.",
            "non_hjorth_vs_C94": "C94 Hjorth Mobility/Complexity uses variance ratios of derivatives sqrt(var(dx)/var(x)) (time-domain second-moment shape). HFD uses MULTI-INTERVAL CURVE-LENGTH RESAMPLING and a log(L(k))-log(1/k) scaling slope across k — different mathematical object/estimator (geometric scaling vs derivative variance ratios).",
            "non_hurst_rs": "Hurst/RS is rescaled-range (R/S) / long-memory scaling of cumulative deviations. HFD is Higuchi curve-length scaling of the series itself; different estimator and phenomenon.",
            "non_entropy_vs_Shannon_perm_sample_Renyi2_spectral": "Entropy families are distribution/information measures (p*log p, ordinal pattern frequencies, template matches, PSD bin probs). HFD is geometric multi-scale curve-length scaling — not an information measure.",
            "non_lz76_vs_C93": "C93 LZ76 is phrase parsing/dictionary (combinatorial compression). HFD is multi-k curve-length scaling slope — no parsing/dictionary.",
            "non_WW_runs_vs_C88_non_mean_run_length_vs_C89_non_TP_vs_C87": "No run/reversal counts or durations.",
            "non_bds_vs_C91": "No delay embedding, no correlation integral C_m, no V_m.",
            "non_variance_ratio_vs_C90": "VR(q) is multi-horizon variance scaling; HFD is multi-k curve-length scaling slope — different construction.",
            "non_ou_hl_vs_C92": "No AR(1) regression, no mean-reversion half-life timescale.",
            "non_single_lag_acf_explicit": "Not a normalized covariance/correlation at any lag.",
            "non_location_explicit": "NOT a location estimator (C83-C86).",
            "non_dispersion_skew_kurtosis": "Not dispersion magnitude (MAD/AAD/IQR/IDR/range/semi-variance/Gini/Theil/CV) and not skewness/Bowley/Kelly/kurtosis.",
            "vs_C23_C40_C94": "Mechanically distinct rolling Higuchi Fractal Dimension (geometric curve-length scaling) transform; not in C23/C40-C94 families. Grep-verified no higuchi/hfd/fractal_dimension in prior RQV costed_oos artifacts/scripts before implementation.",
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
    out = REPORTS / f"real_quote_volume_higuchi_fd_shock_mr_costed_oos_{TS}.json"
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
