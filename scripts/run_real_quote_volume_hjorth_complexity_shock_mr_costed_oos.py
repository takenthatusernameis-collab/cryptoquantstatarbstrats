#!/usr/bin/env python3
"""Campaign #101 R-B (fail-closed, real data only): real_quote_volume-conditioned
Rolling Hjorth Complexity shock MR on log-volume changes (real Binance spot
quote volume klines col 5) + real cached spot 1h.

PRE-STATED HYPOTHESIS (fixed before seeing OOS results): "Volume Hjorth Complexity Shock MR"
- For each asset, compute log-volume changes r_t = ln(v_t) - ln(v_{t-1}) (v_t =
  quote_volume_usdt, positive finite). Over a causal trailing lookback W=168h
  compute Hjorth parameters:
    Activity   = var(r_{t-W+1:t})
    Mobility   = sqrt(var(diff(r)) / var(r))
    Complexity = Mobility(diff(r)) / Mobility(r)
  Trade causal z-score shocks of Hjorth Complexity (W=168, ZLB=168) as MR:
    if dz >= ENTRY_Z (1.25): SHORT  (fade unusually HIGH complexity / shape-irregularity shock)
    if dz <= -ENTRY_Z (-1.25): LONG  (fade unusually LOW complexity / shape-regularity shock)
  Exit: |dz| < EXIT_Z (0.25) OR hold >= MAX_HOLD (12h) OR signal flips.
- Execution shift t -> t+1. Walk-forward: rolling 720/168/168 (train/test/step).
- Cost grid bps (fee,slip): [[0,0],[5,5],[10,10],[20,20],[40,40]]. Benchmark: B&H
  per asset (gross) on union of OOS WF windows.
- Pre-stated edge rule (fail-closed): oos_edge_proven=true IFF OOS exposure>0 AND
  for ALL cost-grid slices OOS net sum > 0 AND mean OOS net mean beats mean B&H OOS
  mean on same WF windows. Else false. No in-sample tuning, no threshold weakening.

DISTINCTNESS (vs C23/C40-C100, mechanically stated) — TRADES HJORTH COMPLEXITY
(Mobility(ddx)/Mobility(dx), a second-order derivative-variance ratio of shape
change) AS ITS OWN STANDALONE SIGNAL/FAMILY. This is NOT C94 Hjorth Mobility.
- NON-HJORTH-MOBILITY (C94 traded signal): C94 traded rolling Hjorth Mobility =
  sqrt(var(dx)/var(x)) (first-order derivative variance ratio / roughness). C101
  trades Hjorth Complexity = Mobility(diff(x))/Mobility(x) — a RATIO OF MOBILITIES
  (second-order shape: how the roughness itself changes). Different estimator,
  different traded feature, different hypothesis object.
- NON-LZ76 (C93): no phrase parsing/dictionary/Kolmogorov proxy; variance ratios of
  derivatives.
- NON-PFD (C99), NON-ZCR (C100), NON-TP (C87), NON-WW-runs (C88), NON-MRL (C89):
  no sign-change-in-diff, no zero-crossing rate of x, no interior peaks/troughs,
  no runs.
- NON-KATZ-FD (C97), NON-HIGUCHI (C95), NON-TKEO (C98): no FD curve length, no
  k-scaling slope, no nonlinear energy operator.
- NON-HURST/RS, NON-DFA (not previously traded as RQV costed OOS family in
  reports/scripts grep): Hjorth Complexity is local variance-ratio-of-derivatives,
  not rescaled-range or detrended fluctuation scaling.
- NON-ENTROPY (Shannon/perm/sample/Renyi2/spectral as distribution measures),
  NON-BDS, NON-VR, NON-OU/HL, NON-single-lag-ACF, NON-LOCATION/DISPERSION/
  SKEW/KURTOSIS as in prior campaigns.
- Grep precheck (before implementation): `hjorth_complexity_shock_mr_costed_oos|
  VOLUME_HJORTH_COMPLEXITY_SHOCK|volume_hjorth_complexity_shock` absent in
  reports/real_quote_volume_*costed_oos* and scripts/run_real_quote_volume_*costed_oos*.py.
- Data source identical (real Binance spot quote volume) but TRANSFORM is
  mechanically different: rolling Hjorth Complexity of log-volume changes traded
  as standalone MR shock signal.
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
CAMPAIGN = 101
PRIOR_UNBLOCK = "reports/real_feed_unblock_status_20261106T130243Z.json"
PRIOR_UNBLOCK_SHA = "49699fad6ce626b2b3edf99650e21a5f305778c55b9b83e1980ddbdfd67a6d80"
PRIOR_REGISTRY = "reports/strategy_edge_registry_20261106T174241Z.json"
PRIOR_REGISTRY_SHA = "28ae0a7bc9b11afd145f43907f70f464d2a41e76168fb24a6edeeebbf0e8dd3d"
PRIOR_C100_RB = "reports/real_quote_volume_zcr_shock_mr_costed_oos_20261106T174105Z.json"
PRIOR_C100_RB_SHA = "c3caf4dfdf66fedfb522f61233172c541f6cae7852c78173c6a41156bbc55951"


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


def hjorth_complexity(x: np.ndarray) -> float:
    """Hjorth Complexity = Mobility(diff(x)) / Mobility(x). Fail-closed NaN."""
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    if x.size < 6:
        return np.nan
    dx = np.diff(x)
    ddx = np.diff(dx)
    vx = float(np.var(x))
    vdx = float(np.var(dx))
    vddx = float(np.var(ddx))
    if vx <= 1e-18 or vdx <= 1e-18 or not (math.isfinite(vx) and math.isfinite(vdx) and math.isfinite(vddx)):
        return np.nan
    mob_x = math.sqrt(vdx / vx)
    if mob_x <= 1e-18 or not math.isfinite(mob_x):
        return np.nan
    mob_dx = math.sqrt(vddx / vdx)
    if not math.isfinite(mob_dx):
        return np.nan
    c = mob_dx / mob_x
    if not math.isfinite(c):
        return np.nan
    return c


def rolling_hjorth_complexity(x: np.ndarray, w: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    for i in range(w, len(x)):
        win = x[i - w + 1 : i + 1]
        if not np.isfinite(win).all() or len(win) < w:
            continue
        out[i] = hjorth_complexity(win)
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
    feat = rolling_hjorth_complexity(dlogv, W_HJ)
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
                desired = -1.0  # fade unusually HIGH complexity / shape-irregularity
            elif z <= -ENTRY_Z:
                desired = 1.0   # fade unusually LOW complexity / shape-regularity
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
        "tool": "scripts/run_real_quote_volume_hjorth_complexity_shock_mr_costed_oos.py",
        "generated_at_utc": TS,
        "campaign": CAMPAIGN,
        "prior_unblock": PRIOR_UNBLOCK,
        "prior_unblock_sha256": PRIOR_UNBLOCK_SHA,
        "prior_registry": PRIOR_REGISTRY,
        "prior_registry_sha256": PRIOR_REGISTRY_SHA,
        "prior_c100_rb": PRIOR_C100_RB,
        "prior_c100_rb_sha256": PRIOR_C100_RB_SHA,
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
            "id": "VOLUME_HJORTH_COMPLEXITY_SHOCK_MR",
            "description": "Fade causal z-score shocks of rolling Hjorth Complexity (Mobility(diff(x))/Mobility(x), ratio of derivative-variance mobilities) of log-volume changes as shape-irregularity shocks; t->t+1.",
            "hjorth_complexity_form": "Complexity = Mobility(diff(r))/Mobility(r), Mobility(y)=sqrt(var(diff(y))/var(y))",
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
            "hjorth_complexity": "Hjorth Complexity = Mobility(diff(x))/Mobility(x) is a SECOND-ORDER derivative-variance ratio (shape-change-of-roughness). Trades complexity, not mobility.",
            "non_hjorth_mobility_vs_C94": "C94 traded Hjorth Mobility sqrt(var(dx)/var(x)) (first-order roughness). C101 trades Complexity=Mobility(ddx-context via Mobility(diff(x))/Mobility(x)) — different estimator/feature/hypothesis; grep precheck confirmed no prior standalone hjorth_complexity_shock_mr_costed_oos family.",
            "non_lz76_vs_C93": "No phrase parsing/dictionary/Kolmogorov proxy; variance ratios of derivatives.",
            "non_pfd_vs_C99_non_zcr_vs_C100_non_tp_vs_C87": "No sign-change-in-diff (PFD), no zero-crossing rate of x (ZCR), no interior peaks/troughs (TP).",
            "non_ww_runs_vs_C88_non_mrl_vs_C89": "No runs/durations.",
            "non_katz_vs_C97_non_higuchi_vs_C95_non_tkeo_vs_C98": "No FD curve length, no k-scaling slope, no nonlinear energy.",
            "non_hurst_rs_non_dfa": "Not rescaled-range or detrended fluctuation scaling; local derivative-variance ratio.",
            "non_entropy_vs_Shannon_perm_sample_Renyi2_spectral": "No p*log p, ordinal frequencies, template matches, or PSD-bin probs.",
            "non_bds_vs_C91_non_vr_vs_C90_non_ou_hl_vs_C92": "No embedding/correlation integral, no multi-horizon variance scaling, no AR(1) regression/timescale.",
            "non_single_lag_acf_explicit": "Not a normalized covariance/correlation at any lag.",
            "non_location_explicit": "NOT a location estimator.",
            "non_dispersion_skew_kurtosis": "Not dispersion magnitude and not skewness/Bowley/Kelly/kurtosis.",
            "grep_precheck": "grep -rn 'hjorth_complexity_shock_mr_costed_oos|VOLUME_HJORTH_COMPLEXITY_SHOCK|volume_hjorth_complexity_shock' reports/real_quote_volume_*costed_oos* scripts/run_real_quote_volume_*costed_oos*.py -> empty before implementation.",
            "vs_C23_C40_C100": "Mechanically distinct rolling Hjorth Complexity (standalone traded signal) transform; not in C23/C40-C100 families.",
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
    out = REPORTS / f"real_quote_volume_hjorth_complexity_shock_mr_costed_oos_{TS}.json"
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
