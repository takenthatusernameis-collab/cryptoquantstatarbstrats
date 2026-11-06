#!/usr/bin/env python3
"""Campaign #94 R-B (fail-closed, real data only): real_quote_volume-conditioned
Rolling Hjorth Mobility (and Complexity) shock MR on log-volume changes (real
Binance spot quote volume klines col 5) + real cached spot 1h.

PRE-STATED HYPOTHESIS (fixed before seeing OOS results): "Volume Hjorth Mobility
Shock MR"
- For each asset, compute log-volume changes r_t = ln(v_t) - ln(v_{t-1}) (v_t =
  quote_volume_usdt, positive finite). Over a causal trailing lookback W=168h
  compute Hjorth parameters:
    Activity   = var(r_{t-W+1:t})
    Mobility   = sqrt(var(diff(r)) / var(r))   [variance-of-derivative / level-variance ratio]
    Complexity = Mobility(diff(r)) / Mobility(r)
  Trade causal z-score shocks of Hjorth Mobility (W=168, ZLB=168) as MR:
    if dz >= ENTRY_Z (1.25): SHORT  (fade unusually HIGH mobility / roughness shock)
    if dz <= -ENTRY_Z (-1.25): LONG  (fade unusually LOW mobility / smoothness shock)
  Exit: |dz| < EXIT_Z (0.25) OR hold >= MAX_HOLD (12h) OR signal flips.
- Execution shift t -> t+1. Walk-forward: rolling 720/168/168 (train/test/step).
- Cost grid bps (fee,slip): [[0,0],[5,5],[10,10],[20,20],[40,40]]. Benchmark: B&H
  per asset (gross) on union of OOS WF windows.
- Pre-stated edge rule (fail-closed): oos_edge_proven=true IFF OOS exposure>0 AND
  for ALL cost-grid slices OOS net sum > 0 AND mean OOS net mean beats mean B&H OOS
  mean on same WF windows. Else false. No in-sample tuning, no threshold weakening.

DISTINCTNESS (vs C23/C40-C93, mechanically stated) — NON-LOCATION, NON-TP,
NON-WALD–WOLFOWITZ-RUNS, NON-MEAN-RUN-LENGTH-PERSISTENCE, NON-VARIANCE-RATIO,
NON-BDS, NON-OU/HL, NON-LZ76, NON-DISPERSION, NON-ENTROPY (incl. spectral entropy
as Shannon-over-PSD), NON-SKEW/KURTOSIS, NON-SINGLE-LAG-ACF, NON-HURST/RS:
- Hjorth Mobility = sqrt(var(dx)/var(x)) is a TIME-DOMAIN VARIANCE-OF-DERIVATIVE /
  DERIVATIVE-RATIO statistic (a signal-shape / spectral-moment proxy derived from
  first/second differences' variances). It measures local smoothness/roughness of
  the trajectory via variance ratios of derivatives — NOT a probability-distribution
  information measure (no p*log p, no symbol/ordinal-pattern frequencies).
- NON-ENTROPY (vs C-scope Shannon/permutation/sample/Renyi2 entropy families and
  spectral-entropy-as-Shannon-over-PSD): entropy measures are SYMBOL-PROBABILITY /
  ORDINAL-PATTERN INFORMATION measures computed from distributions (p*log(p) over
  symbols, ordinal pattern frequencies, template-match probabilities, PSD bin
  probabilities). Hjorth Mobility/Complexity uses VARIANCE RATIOS of derivatives —
  a second-moment time-domain shape statistic, not a distribution/information
  measure. Different mathematical object and phenomenon.
- NON-LZ76 (vs C93): LZ76 counts parsed dictionary phrases via left-to-right
  substring parsing (combinatorial compression/Kolmogorov proxy). Hjorth Mobility
  is sqrt(var(dx)/var(x)) — variance ratios of derivatives, no parsing, no
  dictionary, no phrase count.
- NON-WW-runs (vs C88) / NON-mean-run-length (vs C89) / NON-TP (vs C87): C88 is a
  standardized total-run-count randomness statistic; C89 is mean run duration;
  C87 counts local peak/trough reversals of consecutive differences. Hjorth Mobility
  is a variance-of-derivative ratio — it does NOT count runs, run durations, or
  reversals.
- NON-BDS (vs C91): BDS V_m=C_m-C_1^m is a correlation-integral /
  embedding-dimension nonlinear-independence test on delay-embedded change vectors.
  Hjorth Mobility is a 1D variance-ratio of derivatives — no embedding, no
  correlation integral, no C_m.
- NON-VARIANCE-RATIO (vs C90): VR(q) is multi-horizon variance scaling (ratio of
  variance at horizon q to q times variance at horizon 1). Hjorth Mobility is
  var(dx)/var(x) — variance of first difference vs variance of level, a local
  shape/roughness measure, not multi-horizon variance scaling.
- NON-OU/HL (vs C92): OU/HL is a parametric AR(1) levels regression yielding a
  mean-reversion speed/half-life timescale. Hjorth Mobility is a variance-ratio of
  derivatives — no regression, no timescale, no AR(1).
- NON-SINGLE-LAG-ACF: not a normalized covariance/correlation at any single lag k;
  uses variance ratios of derivatives.
- NON-HURST/RS: Hurst/RS is a rescaled-range / rescaled-variance long-memory
  estimator. Hjorth Mobility is a local variance-of-derivative ratio, not R/S.
- NON-LOCATION (C83-C86): not a location estimator (trimean, midhinge, Gastwirth,
  Hodges–Lehmann).
- NON-DISPERSION/SKEW/KURTOSIS: not MAD/AAD/IQR/IDR/range/semi-variance/Gini/Theil/
  CV (dispersion magnitude), not skewness/Bowley/Kelly/kurtosis (shape).
- Data source identical (real Binance spot quote volume) but TRANSFORM is
  mechanically different: rolling Hjorth Mobility (and Complexity) of log-volume
  changes.
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
W_HJ, ZLB, ENTRY_Z, EXIT_Z, MAX_HOLD = 168, 168, 1.25, 0.25, 12
CAMPAIGN = 94
PRIOR_UNBLOCK = "reports/real_feed_unblock_status_20261106T130243Z.json"
PRIOR_UNBLOCK_SHA = "49699fadedfd0802ad4bf43fcf95eaff4a67ddfbc9611513221800aafc7a6d80"
PRIOR_REGISTRY = "reports/strategy_edge_registry_20261106T143520Z.json"
PRIOR_REGISTRY_SHA = "d61a7337c7098f341b0e4f01e29954b22d8e5af515d073831b59e186e89635fd"
PRIOR_C93_RB = "reports/real_quote_volume_lz76_complexity_shock_mr_costed_oos_20261106T143358Z.json"
PRIOR_C93_RB_SHA = "f784dde095495895bb6a0f9401da50315e9e95a6696bb6e193537d47f78a7335"


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


def hjorth_params(x: np.ndarray) -> tuple:
    """Return (activity, mobility, complexity) for a 1D array x.
    Activity = var(x); Mobility = sqrt(var(diff(x))/var(x));
    Complexity = Mobility(diff(x)) / Mobility(x). Fail-closed NaN if degenerate."""
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    n = len(x)
    if n < 8:
        return (np.nan, np.nan, np.nan)
    act = float(np.var(x))
    if act <= 1e-18 or not math.isfinite(act):
        return (act, np.nan, np.nan)
    dx = np.diff(x)
    dx = dx[np.isfinite(dx)]
    if dx.size < 4:
        return (act, np.nan, np.nan)
    var_dx = float(np.var(dx))
    mob = math.sqrt(var_dx / act) if act > 0 else np.nan
    if not math.isfinite(mob):
        return (act, mob, np.nan)
    ddx = np.diff(dx)
    ddx = ddx[np.isfinite(ddx)]
    if ddx.size < 4:
        return (act, mob, np.nan)
    var_ddx = float(np.var(ddx))
    mob_dx = math.sqrt(var_ddx / var_dx) if var_dx > 0 else np.nan
    if not math.isfinite(mob_dx):
        return (act, mob, np.nan)
    comp = mob_dx / mob if mob > 0 else np.nan
    return (act, mob, comp)


def rolling_hjorth_mobility(x: np.ndarray, w: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    for i in range(w, len(x)):
        win = x[i - w + 1 : i + 1]
        if not np.isfinite(win).all() or len(win) < w:
            continue
        _, mob, _ = hjorth_params(win)
        out[i] = mob
    return out


def rolling_hjorth_complexity(x: np.ndarray, w: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    for i in range(w, len(x)):
        win = x[i - w + 1 : i + 1]
        if not np.isfinite(win).all() or len(win) < w:
            continue
        _, _, comp = hjorth_params(win)
        out[i] = comp
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
    feat = rolling_hjorth_mobility(logv, W_HJ)
    dz = rolling_z(feat, ZLB)
    sig = np.zeros(n)
    cur = 0.0
    hold = 0
    warm = max(W_HJ, ZLB) + 4
    for i in range(warm, n):
        z = dz[i]
        if not np.isfinite(z):
            nxt = cur
            hold = hold + 1 if cur != 0 else 0
        else:
            desired = 0.0
            if z >= ENTRY_Z:
                desired = -1.0  # fade unusually HIGH mobility/roughness shock
            elif z <= -ENTRY_Z:
                desired = 1.0   # fade unusually LOW mobility/smoothness shock
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
        "tool": "scripts/run_real_quote_volume_hjorth_mobility_shock_mr_costed_oos.py",
        "generated_at_utc": TS,
        "campaign": CAMPAIGN,
        "prior_unblock": PRIOR_UNBLOCK,
        "prior_unblock_sha256": PRIOR_UNBLOCK_SHA,
        "prior_registry": PRIOR_REGISTRY,
        "prior_registry_sha256": PRIOR_REGISTRY_SHA,
        "prior_c93_rb": PRIOR_C93_RB,
        "prior_c93_rb_sha256": PRIOR_C93_RB_SHA,
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
            "id": "VOLUME_HJORTH_MOBILITY_SHOCK_MR",
            "description": "Fade causal z-score shocks of rolling Hjorth Mobility (sqrt(var(diff)/var)) of log-volume changes (W=168) as mobility/roughness shocks; t->t+1.",
            "hjorth_window": W_HJ,
            "entry_z": ENTRY_Z,
            "exit_z": EXIT_Z,
            "max_hold": MAX_HOLD,
            "z_lookback": ZLB,
            "walkforward": {"train": TRAIN, "test": TEST, "step": STEP},
            "cost_grid_bps": COST_GRID,
            "benchmark": "buy_and_hold_gross_same_oos_windows",
        },
        "distinctness_mechanical": {
            "hjorth_mobility": "Hjorth Mobility = sqrt(var(dx)/var(x)) is a TIME-DOMAIN VARIANCE-OF-DERIVATIVE / DERIVATIVE-RATIO statistic (signal-shape / spectral-moment proxy from first/second differences' variances). Measures local smoothness/roughness via variance ratios of derivatives — NOT a probability-distribution information measure (no p*log p).",
            "non_entropy_vs_Shannon_perm_sample_Renyi2_spectral": "Entropy families (Shannon/permutation/sample/Renyi2, incl. spectral-entropy-as-Shannon-over-PSD) are SYMBOL-PROBABILITY / ORDINAL-PATTERN INFORMATION measures from distributions (p*log p, ordinal pattern frequencies, template-match probs, PSD bin probs). Hjorth Mobility/Complexity uses VARIANCE RATIOS of derivatives — a second-moment time-domain shape statistic, not a distribution/information measure.",
            "non_lz76_vs_C93": "C93 LZ76 counts parsed dictionary phrases via left-to-right substring parsing (combinatorial compression / Kolmogorov proxy). Hjorth Mobility = sqrt(var(dx)/var(x)) — variance ratios of derivatives, no parsing, no dictionary, no phrase count.",
            "non_WW_runs_vs_C88_non_mean_run_length_vs_C89_non_TP_vs_C87": "C88 = standardized TOTAL-RUN-COUNT randomness. C89 = mean DURATION of contiguous runs. C87 = LOCAL PEAK/TROUGH REVERSAL count. Hjorth Mobility is a variance-of-derivative ratio — NOT run/reversal counts or durations.",
            "non_bds_vs_C91": "C91 BDS V_m=C_m-C_1^m is a CORRELATION-INTEGRAL/EMBEDDING-DIMENSION test on delay-embedded vectors. Hjorth Mobility is a 1D variance-ratio of derivatives — no embedding, no correlation integral, no C_m.",
            "non_variance_ratio_vs_C90": "C90 VR(q) is multi-horizon variance scaling (var at horizon q / q*var at horizon 1). Hjorth Mobility is var(dx)/var(x) — local shape/roughness, not multi-horizon variance scaling.",
            "non_ou_hl_vs_C92": "C92 OU/HL is a parametric AR(1) levels regression -> mean-reversion speed/half-life timescale. Hjorth Mobility is a variance-ratio of derivatives — no regression, no timescale.",
            "non_single_lag_acf_explicit": "Not a normalized covariance/correlation at any lag.",
            "non_hurst_rs": "Hurst/RS is a rescaled-range long-memory estimator. Hjorth Mobility is a local variance-of-derivative ratio, not R/S.",
            "non_location_explicit": "NOT a location estimator. Distinct from C86 Hodges–Lehmann, C85 Gastwirth, C84 Midhinge, C83 Tukey trimean.",
            "non_dispersion_skew_kurtosis": "Not MAD/AAD/IQR/IDR/range/semi-variance/Gini/Theil/CV (dispersion), not skewness/Bowley/Kelly/kurtosis (shape).",
            "vs_C23_C40_C93": "Mechanically distinct rolling Hjorth Mobility (variance-of-derivative ratio) transform; not in C23/C40-C93 families.",
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
    out = REPORTS / f"real_quote_volume_hjorth_mobility_shock_mr_costed_oos_{TS}.json"
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
