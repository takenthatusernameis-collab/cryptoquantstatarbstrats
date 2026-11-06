#!/usr/bin/env python3
"""Campaign #86 R-B (fail-closed, real data only): real_quote_volume-conditioned
Rolling Hodges–Lehmann Location (rank-based robust LOCATION) shock mean reversion on
real Binance spot quote volume (klines col 5) + real cached spot 1h.

PRE-STATED HYPOTHESIS (fixed before seeing OOS results): "Volume Hodges–Lehmann
Location Shock MR"
- For each asset, compute rolling Hodges–Lehmann location of quote_volume_usdt over
  window W=48h: HL_t = median{(x_i + x_j)/2 : 1 <= i <= j <= n} over the positive
  finite window values (Walsh-average median; rank-based robust LOCATION level).
- Causal z-score of HL_t (lookback ZLB=168h). Trade HL LOCATION SHOCKS as MR:
    if dz >= ENTRY_Z (1.25): SHORT (fade robust-location level spike)
    if dz <= -ENTRY_Z (-1.25): LONG (fade robust-location level compression shock)
  Exit: |dz| < EXIT_Z (0.25) OR hold >= MAX_HOLD (12h) OR signal flips.
- Execution shift t -> t+1. Walk-forward: rolling 720/168/168 (train/test/step).
- Cost grid bps (fee,slip): [[0,0],[5,5],[10,10],[20,20],[40,40]]. Benchmark: B&H
  per asset (gross) on union of OOS WF windows.
- Pre-stated edge rule (fail-closed): oos_edge_proven=true IFF OOS exposure>0 AND
  for ALL cost-grid slices OOS net sum > 0 AND mean OOS net mean beats mean B&H OOS
  mean on same OOS windows. Else false. No in-sample tuning, no threshold weakening.

DISTINCTNESS (vs C23/C40-C85, mechanically stated):
- Hodges–Lehmann location HL=median{(x_i+x_j)/2 : i<=j} is a RANK-BASED ROBUST
  LOCATION (level) estimator — the median of all Walsh averages (pairwise means).
  It answers "where is the pair-averaged center of the volume level?" Mechanically
  distinct from ALL L-estimator quantile-weighted locations:
  - C85 Gastwirth G=0.3*Q(1/3)+0.4*Q(0.5)+0.3*Q(2/3): TERCILE quantile points
    Q(1/3),Q(2/3) + median Q(0.5), weights 0.3/0.4/0.3 (L-estimator on order stats).
    HL is NOT an L-estimator (not a weighted sum of fixed order statistics); it is
    the median of all pairwise means — a rank-based functional with a different
    influence function and breakdown behavior.
  - C84 Midhinge MH=(Q1+Q3)/2: quartiles Q(0.25),Q(0.75), excludes median, weights
    0.5/0/0.5. HL uses all pairwise means, not two order statistics.
  - C83 Tukey trimean TM=(Q1+2*Q2+Q3)/4: quartiles Q(0.25),Q(0.75)+median Q(0.5),
    weights 0.25/0.5/0.25 (L-estimator). HL uses pairwise Walsh averages, not fixed
    order-statistic weights.
- C80 MAD=median(|x-median|), C82 AAD=mean(|x-mean|): SCALE/DISPERSION of
  deviations, not a location level functional.
- C66-C73 quantile DISPERSIONS/ASYMMETRIES (spreads/ratios e.g. IQR, Bowley/Kelly):
  HL is a LOCATION functional, not a spread/asymmetry/shape ratio.
- C79 Sarle BC (joint skew+kurtosis shape), C45 CV=sigma/mu (L2 scale),
  C51/C74/C75/C76/C78 share-inequality (Gini/Theil/GE/Atkinson/HHI/Hoover):
  concentration/inequality/shape, not pair-averaged location.
- C41/C42/C43 entropy (Shannon binned/permutation/sample): information/complexity.
- C23 and other prior RQV transforms (level/ROC/ratio/cumulative/partition/imbalance/
  corr/beta/lead-lag etc.): HL is a specific rank-based Walsh-average-median
  robust location, a different transform family.
- Data source identical (real Binance spot quote volume) but TRANSFORM is mechanically
  different: rank-based Hodges–Lehmann Walsh-average-median location of volume level.
- Complexity pre-stated: O(W^2 log W) per window via Walsh averages (W=48 -> 1176
  pairs); feasible for W=48 over ~11 assets. Verified distinct vs C23/C40-C85 before
  use (stated above).
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
CAMPAIGN = 86
PRIOR_UNBLOCK = "reports/real_feed_unblock_status_20261106T112342Z.json"
PRIOR_REGISTRY = "reports/strategy_edge_registry_20261106T112634Z.json"


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


def hodges_lehmann_location(arr: np.ndarray) -> float:
    """HL = median{(x_i+x_j)/2 : 1<=i<=j<=n} over positive finite values.

    Rank-based robust LOCATION: median of all Walsh averages (pairwise means).
    O(n^2) pairs per window; W=48 -> 1176 pairs. Not an L-estimator (not a
    weighted sum of fixed order statistics).
    """
    x = arr[np.isfinite(arr) & (arr > 0)]
    if x.size < 2:
        return np.nan
    ii = np.arange(x.size)
    iu = np.triu_indices(x.size)
    walsh = (x[iu[0]] + x[iu[1]]) / 2.0
    m = np.median(walsh)
    return float(m) if np.isfinite(m) else np.nan


def rolling_hl(v: np.ndarray, w: int) -> np.ndarray:
    out = np.full(len(v), np.nan)
    for i in range(w - 1, len(v)):
        out[i] = hodges_lehmann_location(v[i - w + 1 : i + 1])
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
    feat = rolling_hl(vv, W)
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
        "tool": "scripts/run_real_quote_volume_hodges_lehmann_location_shock_mr_costed_oos.py",
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
            "id": "VOLUME_HODGES_LEHMANN_LOCATION_SHOCK_MR",
            "description": "Fade Hodges–Lehmann location HL=median{(x_i+x_j)/2:i<=j} (W=48) Walsh-average-median robust-location z-score shocks of real quote volume; rank-based robust-location mean reversion, t->t+1.",
            "entry_z": ENTRY_Z,
            "exit_z": EXIT_Z,
            "max_hold": MAX_HOLD,
            "hl_window": W,
            "z_lookback": ZLB,
            "walkforward": {"train": TRAIN, "test": TEST, "step": STEP},
            "cost_grid_bps": COST_GRID,
            "benchmark": "buy_and_hold_gross_same_oos_windows",
        },
        "distinctness_mechanical": {
            "hodges_lehmann": "HL=median{(x_i+x_j)/2:1<=i<=j<=n} Walsh-average-median rank-based robust LOCATION (level); NOT an L-estimator (no fixed order-statistic weights); median of all pairwise means.",
            "vs_C85_gastwirth": "C85 G=0.3*Q(1/3)+0.4*Q(0.5)+0.3*Q(2/3) tercile+median L-estimator on order stats (weights 0.3/0.4/0.3). HL uses ALL pairwise Walsh averages (rank-based), different functional, different influence/breakdown.",
            "vs_C84_midhinge": "C84 MH=(Q1+Q3)/2 quartiles Q(0.25),Q(0.75) excludes median weights 0.5/0/0.5; HL uses all pairwise means, not two order statistics.",
            "vs_C83_trimean": "C83 TM=(Q1+2*Q2+Q3)/4 quartiles+median L-estimator weights 0.25/0.5/0.25; HL uses pairwise Walsh averages, not fixed order-statistic weights.",
            "vs_C82_AAD_C80_MAD": "AAD=mean(|x-mean|), MAD=median(|x-median|) are SCALE/DISPERSION of deviations, not location level.",
            "vs_C66_C73_quantile_dispersions_asymmetries": "HL is a LOCATION functional, not a spread/asymmetry/shape ratio (e.g. IQR).",
            "vs_C79_SarleBC_C45_CV_C51C74C75C76C78_inequality": "shape/scale/inequality-concentration, not pair-averaged location.",
            "vs_C41C42C43_entropy": "information/complexity, not location.",
            "vs_C23_other_RQV": "rank-based Walsh-average-median robust location shock on volume level; different transform family.",
            "data_source_identical_transform_mechanically_different": True,
            "complexity_prestated": "O(W^2) Walsh pairs per window (W=48 -> 1176 pairs); feasible over ~11 assets.",
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
    out = REPORTS / f"real_quote_volume_hodges_lehmann_location_shock_mr_costed_oos_{TS}.json"
    out.write_text(json.dumps(artifact, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(out.relative_to(ROOT)), "sha256": sha256_file(out),
                      "oos_edge_proven": edge, "n_assets": len(per), "any_exposure": any_exp,
                      "all_pos": all_pos, "beats_bh": beats, "bh_mean": bh_mean,
                      "agg_net_sum": agg["oos_net_sum"]}, indent=2))


if __name__ == "__main__":
    main()
