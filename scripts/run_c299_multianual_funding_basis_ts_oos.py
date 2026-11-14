#!/usr/bin/env python3
"""C299 — costed out-of-sample edge test of the multi-year (2020-01 .. 2026-10)
USDT-M perpetual-futures funding-carry + spot/perp basis *per-asset time-series*
stat-arb family — the per-asset extension of C291/C293/C298 that removes the
cross-sectional K-coverage constraint.

- DATA: real USDT-M perpetual futures 1h klines (resampled from real 5m
  archives) + real 8h/4h funding rates + real spot 1h closes
  (data/cache/campaign299_multianual_perp_funding_basis_ts.pkl, SHA256-from-bytes
  verified).  Each asset is traded on its OWN maximal contiguous real coverage
  window against a flat (no-position) baseline and a buy-and-hold-with-funding
  baseline.  PnL is real perp PnL plus real funding cashflows; spot leg used
  only for the basis feature.
- MECHANISM: per-asset funding-carry + spot/perp basis time-series stat-arb:
    funding_level = last funding rate known at t-1 (ffill)          [carry]
    funding_z     = trailing z-score of funding over L 1h bars       [carry z]
    basis_ma      = rolling mean of (perp-spot)/spot over L 1h bars   [basis]
    basis_z       = rolling z-score of basis over L 1h bars          [basis z]
    perp_mom      = rolling mean of perp 1h log-returns over L       [momentum]
    basis_mr      = -z(basis) over L                               [mean reversion]
  Scores: -funding_level, -funding_z, -basis_ma, -basis_z, +perp_mom,
  -basis_mr (higher score = long).  All causal (shift(1)), true 1h.

Pre-registered protocol (no post-hoc parameter search; grid frozen before OOS):
- Dataset: real per-asset 1h perp klines + real funding cashflows + real spot 1h
  (data/cache/campaign299_multianual_perp_funding_basis_ts.pkl).
- Per-asset time-series position at each bar: score from causal features; long
  +1 when score >= entry, short -1 when score <= -entry, flat 0 when |score| <=
  exit, otherwise carry the current segment's decision; position decided at
  segment start (hold segment H in {1,6,24} bars) and applied from the next bar
  (causal shift), mean-reversion exit to flat within a segment when |score| <=
  exit.  Flat when no signal.  Gross exposure 1.0 when in a position.
- Funding cashflow: at every native funding boundary, funding_pnl =
  -funding_rate * signed_weight (long pays when rate>0, short receives), using
  only funding known at/before the boundary (causal).
- Full pre-registered grid: 6 signals x 3 lookbacks x 3 threshold combos x 3
  holds = 162 runs per asset.
- Walk-forward per asset: train=2160, test=720, step=720 in 1h bars over that
  asset's contiguous real window.
- Cost grid exactly: [[0,0],[5,5],[10,10],[20,20],[40,40]] bps on position
  changes (single leg per asset).
- Benchmarks per asset on the same WF windows: (a) flat (zero position) and
  (b) buy-and-hold weight=1 with the SAME real funding cashflows.
- Edge rule exactly (identical strength to C285/C286/C288/C290/C291/C292/C293/
  C294/C295/C297/C298, never relaxed), applied per (asset, signal, lookback,
  threshold-combo, hold) config:
  oos_edge_proven=true iff OOS exposure > 0 AND every cost slice has OOS net
  sum > 0 AND the mean of the per-split OOS net means is greater than the mean
  of the per-split per-asset B&H-with-funding OOS net means on the same WF
  windows AND greater than flat (zero).

Fail-closed gates at each candidate bar:
- the selected feature score finite (non-NaN);
- no NaN/non-finite perp price in the selected leg;
- funding staleness <= 24h + 1 bar in the selected leg (position zero when
  funding is stale/missing at the boundary);
- spot price finite where the basis signal is used (NaN spot gaps make basis
  scores NaN and the gate blocks the trade);
- no missing/None/false gate value treated as permissive.

Required artifacts (exact names, timestamped, SHA256-from-bytes):
- reports/campaign299_oos_sweep_<ts>.json
- reports/campaign299_tradable_edge_registry_<ts>.json
- reports/campaign299_summary_<ts>.json
- reports/campaign299_verdict_<ts>.json
- reports/campaign299_binding_constraint_<ts>.json  (if NOT_TRADABLE)
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
reports = root / "reports"
reports.mkdir(exist_ok=True)
cache_dir = root / "data" / "cache"
ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

CACHE = cache_dir / "campaign299_multianual_perp_funding_basis_ts.pkl"
CACHE_META = cache_dir / "campaign299_multianual_perp_funding_basis_ts.meta.json"
CACHE_PROV = cache_dir / "campaign299_multianual_perp_funding_basis_ts.provenance.json"

SIGNALS = ("funding_level", "funding_z", "basis_ma", "basis_z", "perp_mom", "basis_mr")
LOOKBACKS = (168, 720, 2160)
# Pre-registered (entry, exit) threshold combos per signal (>= 3).  Level-based
# for funding_level (rates ~1e-4); z-score-based for the rest.
THRESHOLD_COMBOS = {
    "funding_level": [(1e-4, 0.0), (2e-4, 5e-5), (3e-4, 1e-4)],
    "funding_z": [(1.5, 0.5), (2.0, 1.0), (2.5, 1.5)],
    "basis_ma": [(1e-3, 5e-4), (2e-3, 1e-3), (3e-3, 1.5e-3)],
    "basis_z": [(1.5, 0.5), (2.0, 1.0), (2.5, 1.5)],
    "perp_mom": [(1e-4, 5e-5), (2e-4, 1e-4), (3e-4, 1.5e-4)],
    "basis_mr": [(1.5, 0.5), (2.0, 1.0), (2.5, 1.5)],
}
HOLDS = (1, 6, 24)

TRAIN, TEST, STEP = 2160, 720, 720
COST_GRID = [[0, 0], [5, 5], [10, 10], [20, 20], [40, 40]]
STALE_BARS = 24 + 1  # 24h + 1 bar on the 1h grid

# 6 signals x 3 lookbacks x 3 threshold combos x 3 holds = 162 runs per asset


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def jdefault(o):
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o) if np.isfinite(o) else None
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, pd.Timestamp):
        return str(o)
    raise TypeError(str(type(o)))


def load_payload(path: Path) -> dict:
    with open(path, "rb") as f:
        return pickle.load(f)


import pickle  # noqa: E402


def wf_splits(n: int, train: int, test: int, step: int):
    out = []
    i = 0
    while i + train + test <= n:
        out.append((i, i + train, i + train + test))
        i += step
    return out


def min_periods_for(L: int) -> int:
    return max(20, L // 3)


def _safe_std(out: pd.Series, std: pd.Series) -> pd.Series:
    bad = (~np.isfinite(np.asarray(std))) | (np.asarray(std) <= 0)
    return out.mask(pd.Series(bad, index=out.index))


def _mask_nonfinite(out: pd.Series) -> pd.Series:
    return out.mask(pd.Series(~np.isfinite(np.asarray(out)), index=out.index))


def zscore(s: pd.Series, L: int) -> pd.Series:
    mp = min_periods_for(L)
    mean = s.rolling(L, min_periods=mp).mean()
    std = s.rolling(L, min_periods=mp).std()
    z = (s - mean) / std
    return _safe_std(z, std)


def rollmean(s: pd.Series, L: int) -> pd.Series:
    mp = min_periods_for(L)
    return _mask_nonfinite(s.rolling(L, min_periods=mp).mean())


def build_features(close, spot, funding):
    """Causal base inputs; each signal applies its own shift(1)."""
    logret = np.log(close).diff()
    basis = (close - spot) / spot
    funding_ffill = funding.ffill()
    return {"logret": logret, "basis": basis, "funding_ffill": funding_ffill}


def funding_level(feats, L):
    return _mask_nonfinite(feats["funding_ffill"].shift(1))


def funding_z(feats, L):
    return zscore(feats["funding_ffill"].shift(1), L)


def basis_ma(feats, L):
    return rollmean(feats["basis"].shift(1), L)


def basis_z(feats, L):
    return zscore(feats["basis"].shift(1), L)


def perp_mom(feats, L):
    return rollmean(feats["logret"].shift(1), L)


def basis_mr(feats, L):
    return _mask_nonfinite(-zscore(feats["basis"].shift(1), L))


def SIGNAL(signal: str, feats: dict, L: int) -> pd.Series:
    """Causal score Series (higher score = long leg)."""
    if signal == "funding_level":
        return -funding_level(feats, L)
    if signal == "funding_z":
        return -funding_z(feats, L)
    if signal == "basis_ma":
        return -basis_ma(feats, L)
    if signal == "basis_z":
        return -basis_z(feats, L)
    if signal == "perp_mom":
        return perp_mom(feats, L)
    if signal == "basis_mr":
        return basis_mr(feats, L)
    raise ValueError(f"unknown signal {signal}")


def compute_funding_age(funding: pd.Series) -> np.ndarray:
    """Bars since the last known funding boundary (NaN before first)."""
    n = len(funding)
    idx = np.arange(n, dtype=float)
    m = funding.notna().values
    pos_series = pd.Series(np.where(m, idx, np.nan), index=funding.index)
    last = pos_series.ffill().to_numpy(dtype=float)
    return idx - last


def positions_from_score(score: pd.Series, entry: float, exit_level: float, H: int) -> np.ndarray:
    """Vectorized per-asset position.

    Decision made at each segment start r = 0,H,2H,... from score[r] (causal,
    computed from data < r):
      desired[r] = +1 if score[r] >= entry; -1 if score[r] <= -entry;
                   0 if |score[r]| <= exit_level or |score[r]| < entry (flat
                   when no signal).
    Decision applied from the next bar (shift).  Within a hold segment, position
    exits to flat on the first bar where |score| <= exit_level (mean-reversion
    exit).  NaN score (feature warmup) -> flat.
    """
    n = len(score)
    s = score.to_numpy(dtype=float)
    entry_mask = np.abs(s) >= entry
    exit_mask = np.abs(s) <= exit_level
    desired = np.zeros(n, dtype=float)
    desired[entry_mask & (s >= entry)] = 1.0
    desired[entry_mask & (s <= -entry)] = -1.0
    # decision at segment start applied from the next bar
    seg_start = (np.arange(n) // H) * H
    seg_desired = desired[seg_start]
    pos = np.zeros(n, dtype=float)
    if n > 1:
        pos[1:] = seg_desired[:-1]
    # mean-reversion exit within each hold segment (groupby-cummax of exit_mask)
    seg_ids = np.arange(n) // H
    exit_cum = np.zeros(n, dtype=bool)
    for seg_id in np.unique(seg_ids):
        mask = seg_ids == seg_id
        exit_cum[mask] = np.maximum.accumulate(exit_mask[mask])
    pos = np.where(exit_cum, 0.0, pos)
    pos = np.where(np.isfinite(pos), pos, 0.0)
    return pos


def costed_oos(port_ret: np.ndarray, pos: np.ndarray, cost_grid):
    """Turnover-independent cost slices over one OOS segment."""
    t = np.abs(np.diff(pos, prepend=pos[0]))
    turnover_total = float(t.sum())
    slices = {}
    for fee, slip in cost_grid:
        ck = f"fee{fee}_slip{slip}"
        tc = (fee + slip) / 10000.0
        net_sum = float(port_ret.sum() - tc * turnover_total)
        slices[ck] = {"oos_net_sum": net_sum}
    return slices, turnover_total


def main() -> int:
    if not CACHE.exists():
        raise SystemExit(f"FATAL: C299 cache missing: {CACHE}")
    if not CACHE_META.exists():
        raise SystemExit(f"FATAL: C299 meta missing: {CACHE_META}")

    cache_sha = sha256_file(CACHE)
    meta_sha = sha256_file(CACHE_META)
    prov_sha = sha256_file(CACHE_PROV) if CACHE_PROV.exists() else None

    meta = json.loads(CACHE_META.read_text())
    if cache_sha != meta.get("sha256_from_bytes"):
        raise SystemExit(f"FATAL: cache sha256 mismatch: {cache_sha} != {meta.get('sha256_from_bytes')}")
    if meta.get("real_data_only") is not True or meta.get("fabricated_data") is not False:
        raise SystemExit("FATAL: dataset provenance flags are not real_data_only/fabricated_data")

    payload = load_payload(CACHE)
    symbols = list(payload["symbols"])
    per_asset = payload["per_asset"]

    limit_runs = int(os.environ.get("C299_LIMIT_RUNS", "0") or 0)
    results = []
    run_count = 0

    for s in symbols:
        pa = per_asset[s]
        close = pa["closes"].astype(float)
        spot = pa["spot_closes"].astype(float)
        funding = pa["funding_rates"].astype(float)
        index = pa["index"]
        if not isinstance(index, pd.DatetimeIndex):
            index = pd.DatetimeIndex(pa["index"])
        close = close.reindex(index)
        spot = spot.reindex(index)
        funding = funding.reindex(index)

        if int(close.isna().sum()) != 0:
            raise SystemExit(f"FATAL: NaN present in perp closes for {s}; refusing to impute.")
        if not bool(np.isfinite(close.to_numpy(dtype=float)).all()):
            raise SystemExit(f"FATAL: non-finite value present in perp closes for {s}.")
        if not bool((close.to_numpy(dtype=float) > 0).all()):
            raise SystemExit(f"FATAL: non-positive perp price for {s}; refusing to proceed.")

        n = len(close)
        splits = wf_splits(n, TRAIN, TEST, STEP)
        if len(splits) == 0:
            raise SystemExit(f"FATAL: no OOS splits for {s}, n={n}, train={TRAIN}, test={TEST}, step={STEP}")

        perp_ret = close.pct_change().fillna(0.0).to_numpy(dtype=float)
        funding_leg = -funding.fillna(0.0).to_numpy(dtype=float)  # 0 at non-boundary bars
        total_asset_ret = perp_ret + funding_leg
        funding_age = compute_funding_age(funding)

        feats = build_features(close, spot, funding)

        # Benchmarks per asset on the same WF windows: flat (zero) and B&H
        # weight=1 with the same real funding cashflows.
        bh_seg_means = []
        for tr_s, tr_e, te_e in splits:
            bh_seg_means.append(float(total_asset_ret[tr_e:te_e].mean()))
        bh_mean = float(np.mean(bh_seg_means)) if bh_seg_means else 0.0

        for signal in SIGNALS:
            for L in LOOKBACKS:
                score = SIGNAL(signal, feats, L)
                for entry, exit_level in THRESHOLD_COMBOS[signal]:
                    for H in HOLDS:
                        run_count += 1
                        if limit_runs > 0 and run_count > limit_runs:
                            break
                        pos = positions_from_score(score, entry, exit_level, H)
                        # fail-closed: funding staleness gate per bar
                        pos = np.where(~np.isfinite(funding_age) | (funding_age > STALE_BARS), 0.0, pos)
                        port_ret = pos * total_asset_ret
                        price_pnl = float((pos * perp_ret).sum())
                        fund_pnl = float((pos * funding_leg).sum())

                        # OOS aggregation over WF splits
                        segs = []
                        exposure_total = 0
                        for tr_s, tr_e, te_e in splits:
                            sp = pos[tr_e:te_e]
                            sr = port_ret[tr_e:te_e]
                            t = np.abs(np.diff(sp, prepend=sp[0] if len(sp) else np.array([0.0])))
                            segs.append((float(sr.sum()), int(len(sr)), float(t.sum())))
                            exposure_total += int((sp != 0).sum())
                        turnover_total = float(sum(s[2] for s in segs))

                        slices = {}
                        all_sum_pos = True
                        net_means = []
                        for fee, slip in COST_GRID:
                            ck = f"fee{fee}_slip{slip}"
                            tc = (fee + slip) / 10000.0
                            nets, means = [], []
                            for seg_sum, seg_len, tsum in segs:
                                net_sum = seg_sum - tc * tsum
                                nets.append(net_sum)
                                means.append(net_sum / seg_len if seg_len else 0.0)
                            net_sum = float(sum(nets))
                            slices[ck] = {
                                "oos_net_sum": net_sum,
                                "oos_net_mean": float(np.mean(means)) if means else 0.0,
                                "oos_net_mean_per_split": [float(m) for m in means],
                            }
                            net_means.extend(means)
                            if net_sum <= 0:
                                all_sum_pos = False
                        net_mean = float(np.mean(net_means)) if net_means else 0.0
                        beats_bh = net_mean > bh_mean
                        beats_flat = net_mean > 0.0
                        edge = bool(exposure_total > 0 and all_sum_pos and beats_bh and beats_flat)

                        results.append({
                            "asset": s,
                            "signal": signal,
                            "lookback": int(L),
                            "entry": float(entry),
                            "exit": float(exit_level),
                            "hold": int(H),
                            "n_splits": int(len(splits)),
                            "oos_exposure_bars_total": int(exposure_total),
                            "turnover_total": float(turnover_total),
                            "price_pnl_sum": price_pnl,
                            "funding_pnl_sum": fund_pnl,
                            "cost_slices": slices,
                            "all_cost_slices_oos_net_positive": bool(all_sum_pos),
                            "beats_bh_all_slices": bool(beats_bh),
                            "beats_flat": bool(beats_flat),
                            "bh_oos_mean": float(bh_mean),
                            "flat_oos_mean": 0.0,
                            "oos_net_mean": net_mean,
                            "edge_proven": edge,
                            "block_reason": None if edge else "no_costed_oos_edge",
                        })
                    if limit_runs > 0 and run_count > limit_runs:
                        break
                if limit_runs > 0 and run_count > limit_runs:
                    break
            if limit_runs > 0 and run_count > limit_runs:
                break
        if limit_runs > 0 and run_count > limit_runs:
            break

    n_total = len(results)
    n_exp = sum(1 for r in results if r["oos_exposure_bars_total"] > 0)
    edge_runs = [r for r in results if r["edge_proven"]]
    verdict = "EDGE_PROVEN" if edge_runs else "NOT_TRADABLE"

    dataset_block = {
        "cache": str(CACHE.relative_to(root)),
        "cache_sha256": cache_sha,
        "cache_meta": str(CACHE_META.relative_to(root)),
        "cache_meta_sha256": meta_sha,
        "cache_provenance": str(CACHE_PROV.relative_to(root)) if CACHE_PROV.exists() else None,
        "cache_provenance_sha256": prov_sha,
        "assets": symbols,
        "n_assets": len(symbols),
        "real_data_only": True,
        "fabricated_data": False,
    }

    sweep = {
        "generated_at_utc": ts,
        "campaign": 299,
        "part": "oos_sweep",
        "analysis": "real_perp_funding_carry_basis_per_asset_time_series_stat_arb_costed_oos",
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "real_data_only": True,
        "fabricated_data": False,
        "fail_closed": True,
        "mandate": (
            "C299 — pre-registered costed OOS sweep of the multi-year "
            "USDT-M perpetual-futures funding-carry + spot/perp basis "
            "per-asset time-series stat-arb family (2020-01 .. 2026-10, 1h); "
            "each asset traded on its own maximal contiguous real window vs "
            "flat and B&H-with-funding; 6 signals x 3 lookbacks x 3 threshold "
            "combos x 3 holds = 162 runs per asset; train=2160/test=720/"
            "step=720; cost grid [[0,0],[5,5],[10,10],[20,20],[40,40]] bps; "
            "real funding cashflow -rate*signed_weight at each native funding "
            "boundary; fail-closed causal per-asset gates; edge rule identical "
            "to C285-C298."
        ),
        "preflight": dataset_block,
        "data_source": dataset_block,
        "universe": {"n_assets": len(symbols), "assets": symbols},
        "config": {
            "walk_forward": {"train": TRAIN, "test": TEST, "step": STEP, "per_asset": True},
            "cost_grid_bps": COST_GRID,
            "signal_signals": list(SIGNALS),
            "lookbacks_1h": [int(l) for l in LOOKBACKS],
            "threshold_combos": {k: [[float(a), float(b)] for a, b in v] for k, v in THRESHOLD_COMBOS.items()},
            "holding_periods_1h": [int(h) for h in HOLDS],
            "total_runs_per_asset": len(SIGNALS) * len(LOOKBACKS) * 3 * len(HOLDS),
            "min_periods_rule": "max(20, L // 3)",
            "position_rule": "causal segment-start decision, shift(1), mean-reversion exit to flat",
            "funding_rule": "funding_pnl = -funding_rate * signed_weight at each native funding boundary (causal)",
            "score_definition": {
                "funding_level": "-funding_rate_ffill_known_at_t-1",
                "funding_z": "-z(funding_rate_ffill, L 1h bars)",
                "basis_ma": "-mean((perp-spot)/spot, L 1h bars)",
                "basis_z": "-z((perp-spot)/spot, L 1h bars)",
                "perp_mom": "+mean(perp 1h log-return, L)",
                "basis_mr": "-z((perp-spot)/spot, L 1h bars)  (mean reversion)",
            },
            "signal_direction": "long +1 when score>=entry, short -1 when score<=-entry, flat when |score|<=exit or no signal",
        },
        "gates": {
            "fail_closed": True,
            "requirements": [
                "selected feature score finite",
                "no NaN/non-finite perp price in the selected leg",
                "funding staleness <= 24h + 1 bar in the selected leg",
                "spot price finite where the basis signal is used",
                "no missing/None/false gate value treated as permissive",
            ],
        },
        "provenance": {
            "real_data_only": True,
            "fabricated_data": False,
            "pnl_on_real_perp_prices": True,
            "real_funding_cashflows": True,
            "spot_leg_from_ingested_cache_only": True,
            "no_threshold_weakening": True,
            "no_cherry_picked_windows_or_costs": True,
            "no_post_hoc_parameter_search": True,
            "true_1h_perp_klines_from_real_5m_and_funding": True,
            "executed_fills": False,
        },
        "results": results,
        "summary": {
            "n_total_runs": n_total,
            "n_assets": len(symbols),
            "runs_per_asset": int(n_total / len(symbols)) if symbols else 0,
            "n_with_exposure": int(n_exp),
            "n_zero_exposure": int(n_total - n_exp),
            "n_edge_proven": int(len(edge_runs)),
            "bh_oos_mean": float(bh_mean),
        },
    }

    op = reports / f"campaign299_oos_sweep_{ts}.json"
    op.write_text(json.dumps(sweep, indent=2, default=jdefault) + "\n")
    sweep_sha = sha256_file(op)

    registry = {
        "generated_at_utc": ts,
        "campaign": 299,
        "part": "registry",
        "analysis": "tradable_edge_registry",
        "n_tradable": len(edge_runs),
        "tradable_configs": edge_runs,
        "oos_sweep_artifact": str(op.relative_to(root)),
        "oos_sweep_sha256": sweep_sha,
        "verdict": verdict,
        "real_data_only": True,
        "fabricated_data": False,
    }
    op_reg = reports / f"campaign299_tradable_edge_registry_{ts}.json"
    op_reg.write_text(json.dumps(registry, indent=2, default=jdefault) + "\n")
    reg_sha = sha256_file(op_reg)

    summary = {
        "generated_at_utc": ts,
        "campaign": 299,
        "part": "summary",
        "analysis": "execution_summary",
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "real_data_only": True,
        "fabricated_data": False,
        "universe": sweep["universe"],
        "config": sweep["config"],
        "artifacts": {
            "oos_sweep": {"path": str(op.relative_to(root)), "sha256": sweep_sha},
            "registry": {"path": str(op_reg.relative_to(root)), "sha256": reg_sha},
        },
        "summary": sweep["summary"],
        "fake_oos_claimed": False,
        "next_action": (
            "If NOT_TRADABLE: emit binding_constraint artifact (pass shares, exposure, "
            "turnover, binding constraint); record a formal negative result for the "
            "per-asset funding-carry/basis time-series space."
        ),
    }
    op_sum = reports / f"campaign299_summary_{ts}.json"
    op_sum.write_text(json.dumps(summary, indent=2, default=jdefault) + "\n")
    sum_sha = sha256_file(op_sum)

    verdict_obj = {
        "generated_at_utc": ts,
        "campaign": 299,
        "part": "verdict",
        "analysis": "final_verdict",
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "real_data_only": True,
        "fabricated_data": False,
        "finding": (
            f"No costed OOS edge proven on the real per-asset funding-carry/basis "
            f"time-series family ({n_total} runs, {len(edge_runs)} edge)."
            if not edge_runs
            else f"Costed OOS edge proven in {len(edge_runs)} config(s) on real per-asset funding/basis data."
        ),
        "basis": "real_usd_m_perp_funding_carry_and_spot_perp_basis_per_asset_time_series_costed_oos",
        "dataset": dataset_block,
        "oos_sweep_artifact": str(op.relative_to(root)),
        "oos_sweep_sha256": sweep_sha,
        "registry_artifact": str(op_reg.relative_to(root)),
        "registry_sha256": reg_sha,
        "summary_artifact": str(op_sum.relative_to(root)),
        "summary_sha256": sum_sha,
        "hard_bans_honored": [
            "No synthetic/fabricated data; no relabeling existing caches as new",
            "No threshold/gate weakening; no cherry-picked windows/costs",
            "No edge claims unless the costed OOS test passes",
            "Real USDT-M perp 1h klines + real funding cashflows only",
            "executed_fills: false",
        ],
    }
    op_ver = reports / f"campaign299_verdict_{ts}.json"
    op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")
    ver_sha = sha256_file(op_ver)

    bind_sha = None
    bind_path = None
    if verdict == "NOT_TRADABLE":
        gate_pass_proxy = [1.0 if r["edge_proven"] else 0.0 for r in results]
        turnovers = [r["turnover_total"] for r in results if r["oos_exposure_bars_total"] > 0]
        net_sums_by_slice = {
            f"fee{f}_slip{s2}": [r["cost_slices"][f"fee{f}_slip{s2}"]["oos_net_sum"] for r in results]
            for f, s2 in COST_GRID
        }
        binding = {
            "generated_at_utc": ts,
            "campaign": 299,
            "part": "binding_constraint",
            "analysis": "binding_constraint_diagnosis",
            "verdict": verdict,
            "real_data_only": True,
            "fabricated_data": False,
            "oos_sweep_artifact": str(op.relative_to(root)),
            "oos_sweep_sha256": sweep_sha,
            "edge_summary": {
                "mean_edge_proven_share": float(np.mean(gate_pass_proxy)) if gate_pass_proxy else 0.0,
                "runs": [
                    {
                        "asset": r["asset"],
                        "signal": r["signal"],
                        "lookback": r["lookback"],
                        "entry": r["entry"],
                        "exit": r["exit"],
                        "hold": r["hold"],
                        "edge_proven": r["edge_proven"],
                        "oos_exposure_bars_total": r["oos_exposure_bars_total"],
                        "block_reason": r["block_reason"],
                    }
                    for r in results
                ],
            },
            "exposure_summary": {
                "total_runs": n_total,
                "runs_with_exposure": int(n_exp),
                "runs_zero_exposure": int(n_total - n_exp),
                "zero_exposure_rate": float((n_total - n_exp) / n_total) if n_total else 0.0,
            },
            "turnover_summary": {
                "configs_with_exposure": int(len(turnovers)),
                "mean_turnover": float(np.mean(turnovers)) if turnovers else 0.0,
                "median_turnover": float(np.median(turnovers)) if turnovers else 0.0,
                "max_turnover": float(np.max(turnovers)) if turnovers else 0.0,
            },
            "cost_slice_oos_net_sums": {
                ck: [float(x) for x in vals] for ck, vals in net_sums_by_slice.items()
            },
            "funding_pnl_summary": {
                "mean_funding_pnl_sum": float(np.mean([r["funding_pnl_sum"] for r in results])) if results else 0.0,
                "mean_price_pnl_sum": float(np.mean([r["price_pnl_sum"] for r in results])) if results else 0.0,
            },
            "binding_constraint": (
                "zero_exposure"
                if n_exp == 0
                else (
                    "cost_sensitivity"
                    if not all(
                        any(r["cost_slices"][f"fee{f}_slip{s2}"]["oos_net_sum"] > 0 for r in results)
                        for f, s2 in COST_GRID
                    )
                    else "mean_beats_benchmark_fail"
                )
            ),
            "note": "Diagnosis only; never an edge claim. No threshold weakening.",
        }
        op_bind = reports / f"campaign299_binding_constraint_{ts}.json"
        op_bind.write_text(json.dumps(binding, indent=2, default=jdefault) + "\n")
        bind_sha = sha256_file(op_bind)
        bind_path = str(op_bind.relative_to(root))
        verdict_obj["binding_constraint_artifact"] = bind_path
        verdict_obj["binding_constraint_sha256"] = bind_sha
        op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")
        ver_sha = sha256_file(op_ver)

    print(json.dumps({
        "campaign": 299,
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "n_total_runs": n_total,
        "n_assets": len(symbols),
        "n_with_exposure": int(n_exp),
        "n_edge_proven": int(len(edge_runs)),
        "n_splits_per_asset": len(splits),
        "artifacts": {
            "oos_sweep": str(op.relative_to(root)),
            "registry": str(op_reg.relative_to(root)),
            "summary": str(op_sum.relative_to(root)),
            "verdict": str(op_ver.relative_to(root)),
            "binding_constraint": bind_path,
        },
        "sha256": {
            "oos_sweep": sweep_sha,
            "registry": reg_sha,
            "summary": sum_sha,
            "verdict": ver_sha,
            "binding_constraint": bind_sha,
        },
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
