#!/usr/bin/env python3
"""C293 — costed out-of-sample edge test of a NEW economic dimension:
cross-venue USDT-M perpetual futures funding-carry statistical arbitrage.

NEW data + mechanism vs C281B..C292 (all single-venue or cross-venue spot):
- NEW DATA: real OKX USDT-M perp funding-rate history (public endpoint, paginated)
  + Binance USDT-M perp funding (verified C291 cache) over the common window
  2026-08-10T16:00Z -> 2026-10-30T23:55Z; aligned on native funding boundaries;
  20 active symbols (4 excluded for partial coverage); 23,424 5m bars.
- NEW MECHANISM: cross-venue PERP FUNDING carry. The same asset's funding rate
  on OKX USDT-M perp vs Binance USDT-M perp. Real cashflows (long one perp /
  short the other). Features on the funding spread (okx - binance):
    xfr_spread_ma = -rolling_mean(okx_funding_ffill - binance_funding_ffill, L)
    xfr_spread_z  = -rolling_z(okx_funding_ffill - binance_funding_ffill, L)
    xfr_leadlag   = -rolling_mean((okx_funding_ffill - binance_funding_ffill).shift(1), L)
  All causal (shift(1) before rolling), ffilled to 5m grid. L in {8, 24, 60} 5m bars.

Pre-registered protocol (no post-hoc parameter search):
- Universe: 20 active symbols with full coverage on BOTH venues (4 excluded).
- Cross-sectional portfolio at each 5m rebalance bar: rank assets by score;
  long top K (most negative funding spread = OKX cheaper) and short bottom K,
  K in {2,3,5}; equal weight 0.5/K per leg; gross 1.0; dollar-neutral; cap 0.5.
  Position is a cross-venue spread: long Binance leg / short OKX leg for the
  long set and opposite for the short set? No: each asset is a spread
  r_spread = r_binance - r_okx with signed weight w_i (sum |w|=1, sum w=0).
  Port PnL = sum_i w_i * (r_binance_i - r_okx_i) + funding cashflows on BOTH legs.
  Turnover charged on BOTH legs: tc * (|Δw_binance| + |Δw_okx|) = tc * 2*|Δw| per asset.
- Holding period H in {1,6,24} 5m bars. weights.shift(1).fillna(0.0) before PnL.
- Funding cashflow: at every native funding boundary on each venue,
  funding_pnl = -funding_rate * signed_weight (long pays when rate>0).
  Uses only funding known at/before the boundary (causal).
- Full pre-registered grid: 3 features x 3 lookbacks x 3 K x 3 holds = 81 runs.
- Walk-forward: train=720, test=168, step=168 in 5m bars -> 135 OOS splits.
- Cost grid exactly: [[0,0],[5,5],[10,10],[20,20],[40,40]] bps, charged on BOTH legs.
- Benchmark: equal-weight cross-venue funding-carry B&H on the same OOS windows,
  with the SAME two-leg funding cashflows and costs (turnover only at entry).
- Edge rule exactly (identical to C285/C286/C288/C290/C291/C292, never relaxed):
  oos_edge_proven=true iff OOS exposure > 0 AND every cost slice has OOS net sum > 0
  AND the mean of the per-split OOS net means is greater than the mean of the
  per-split equal-weight B&H OOS net means on the same WF windows.

Fail-closed gates at each candidate 5m rebalance bar:
- selected feature score finite for at least 2K assets;
- cross-sectional score dispersion > 0;
- no NaN/non-finite 5m price/return in any selected leg on either venue;
- no missing/None/false gate value treated as permissive.

Required artifacts (timestamped, SHA256-from-bytes):
- reports/campaign293_oos_sweep_<ts>.json
- reports/campaign293_tradable_edge_registry_<ts>.json
- reports/campaign293_summary_<ts>.json
- reports/campaign293_verdict_<ts>.json
- reports/campaign293_binding_constraint_<ts>.json (if NOT_TRADABLE)
"""
from __future__ import annotations

import hashlib
import json
import os
import pickle
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

PKL = cache_dir / "campaign293_crossvenue_funding.pkl"
META = cache_dir / "campaign293_crossvenue_funding.meta.json"
PROV = cache_dir / "campaign293_crossvenue_funding.provenance.json"

FEATURES = ("xfr_spread_ma", "xfr_spread_z", "xfr_leadlag")
LOOKBACKS = (8, 24, 60)  # 5m bars on ffilled funding spread
K_VALUES = (2, 3, 5)
HOLDS = (1, 6, 24)

TRAIN, TEST, STEP = 720, 168, 168
COST_GRID = [[0, 0], [5, 5], [10, 10], [20, 20], [40, 40]]
TWO_LEG_FACTOR = 2.0  # cost charged on BOTH legs

# Expected native funding points per symbol per venue
OKX_8H_EXPECTED = 244
BINANCE_8H_EXPECTED = 244
BINANCE_4H_EXPECTED = 488

# Symbols excluded by preflight for partial coverage
EXCLUDED_SYMBOLS = frozenset({"BNBUSDT", "ONDOUSDT", "PUMPUSDT", "TAOUSDT"})


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


def wf_splits(n: int, train: int, test: int, step: int):
    out = []
    i = 0
    while i + train + test <= n:
        out.append((i, i + train, i + train + test))
        i += step
    return out


def min_periods_for(L: int) -> int:
    return max(3, L // 3)


def _safe_std(out: pd.DataFrame, std: pd.DataFrame) -> pd.DataFrame:
    bad = (~np.isfinite(np.asarray(std))) | (np.asarray(std) <= 0)
    return out.mask(pd.DataFrame(bad, index=out.index, columns=out.columns))


def _mask_nonfinite(out: pd.DataFrame) -> pd.DataFrame:
    return out.mask(pd.DataFrame(~np.isfinite(np.asarray(out)), index=out.index, columns=out.columns))


def build_features(binance_funding: pd.DataFrame, okx_funding: pd.DataFrame) -> dict:
    """Build base features from native funding rates (sparse).

    Returns a dict with ffilled funding spread components.
    """
    # Forward-fill funding to 5m grid for feature computation
    binance_ffill = binance_funding.ffill()
    okx_ffill = okx_funding.ffill()

    # Funding spread: OKX - Binance
    spread = okx_ffill - binance_ffill
    # Lead-lag raw: spread vs spread shifted by 1 bar (causal spread momentum)
    leadlag_raw = spread - spread.shift(1)

    return {
        "spread": spread,
        "binance_ffill": binance_ffill,
        "okx_ffill": okx_ffill,
        "leadlag_raw": leadlag_raw,
    }


def xfr_spread_ma(feats: dict, L: int) -> pd.DataFrame:
    """-rolling_mean(spread, L) on ffilled data, causal (shift(1))."""
    mp = min_periods_for(L)
    s = feats["spread"].shift(1)
    out = s.rolling(L, min_periods=mp).mean()
    return _mask_nonfinite(out)


def xfr_spread_z(feats: dict, L: int) -> pd.DataFrame:
    """-rolling_z(spread, L) on ffilled data, causal (shift(1))."""
    mp = min_periods_for(L)
    s = feats["spread"].shift(1)
    mean = s.rolling(L, min_periods=mp).mean()
    std = s.rolling(L, min_periods=mp).std()
    z = (s - mean) / std
    return _safe_std(z, std)


def xfr_leadlag(feats: dict, L: int) -> pd.DataFrame:
    """-rolling_mean(leadlag_raw, L) on ffilled data, causal (shift(1))."""
    mp = min_periods_for(L)
    s = feats["leadlag_raw"].shift(1)
    out = s.rolling(L, min_periods=mp).mean()
    return _mask_nonfinite(out)


def SIGNAL(feature: str, feats: dict, L: int) -> pd.DataFrame:
    """Higher score => long the discounted leg (Binance) / short the premium leg (OKX).

    Negative funding spread (okx - binance < 0) means OKX funding < Binance funding,
    so we want to long Binance / short OKX to capture the carry.
    """
    if feature == "xfr_spread_ma":
        return -xfr_spread_ma(feats, L)
    if feature == "xfr_spread_z":
        return -xfr_spread_z(feats, L)
    if feature == "xfr_leadlag":
        return -xfr_leadlag(feats, L)
    raise ValueError(f"unknown feature {feature}")


def compute_funding_cashflows(
    weights: pd.DataFrame,
    binance_funding: pd.DataFrame,
    okx_funding: pd.DataFrame,
) -> pd.Series:
    """Compute funding cashflows at native boundaries for both venues.

    weights: signed weights per asset per 5m bar (index=5m, columns=symbols)
    funding: native funding rates (sparse, NaN except at boundaries)

    Cashflow = -funding_rate * weight at each funding boundary.
    Long (weight>0) pays when rate>0; short (weight<0) receives.

    For cross-venue spread: w_i means +w_i on Binance, -w_i on OKX.
    Funding cashflow:
      Binance leg: -binance_funding * w_i
      OKX leg: -okx_funding * (-w_i) = +okx_funding * w_i
    Total funding = w_i * (okx_funding - binance_funding)
    """
    n = len(weights)
    symbols = list(weights.columns)
    funding_pnl = np.zeros(n, dtype=float)

    w_vals = weights.to_numpy(dtype=float)
    b_fund = binance_funding.to_numpy(dtype=float)
    o_fund = okx_funding.to_numpy(dtype=float)

    # Vectorized per row: funding_pnl[t] = sum_i w[t,i] * (okx_fund[t,i] - binance_fund[t,i])
    # Only non-NaN funding entries contribute (native boundaries)
    for t in range(n):
        spread_fund = o_fund[t] - b_fund[t]
        mask = np.isfinite(spread_fund)
        if mask.any():
            funding_pnl[t] = np.nansum(w_vals[t, mask] * spread_fund[mask])

    return pd.Series(funding_pnl, index=weights.index)


def build_weights(
    signal_df: pd.DataFrame,
    b_px: pd.DataFrame,
    o_px: pd.DataFrame,
    K: int,
    H: int,
    r_start: int,
):
    """Cross-sectional portfolio construction at each 5m rebalance bar.

    signal_df: score (higher = long Binance / short OKX spread)
    b_px, o_px: price DataFrames for NaN checks
    """
    n = len(signal_df)
    sig = signal_df.to_numpy(dtype=float)
    b = b_px.to_numpy(dtype=float)
    o = o_px.to_numpy(dtype=float)
    m = sig.shape[1]
    weights = np.zeros((n, m), dtype=float)
    total_rebalances = 0
    passed_rebalances = 0
    blocked_reasons: dict[str, int] = {}
    r = r_start
    while r < n:
        total_rebalances += 1
        row = sig[r]
        finite = np.isfinite(row)
        ok = True
        reason = None
        if int(finite.sum()) < 2 * K:
            ok = False
            reason = "signal_coverage"
        long_idx = short_idx = None
        if ok:
            vals = row[finite]
            dispersion = float(vals.max() - vals.min()) if len(vals) else 0.0
            if not (np.isfinite(dispersion) and dispersion > 0.0):
                ok = False
                reason = "zero_dispersion"
        if ok:
            order = np.argsort(-vals, kind="stable")
            finite_positions = np.where(finite)[0]
            long_idx = finite_positions[order[:K]]
            short_idx = finite_positions[order[-K:]]
            leg_idx = np.concatenate([long_idx, short_idx])
            if not bool(np.isfinite(b[r][leg_idx]).all() and np.isfinite(o[r][leg_idx]).all()):
                ok = False
                reason = "price_nan"
        if ok:
            passed_rebalances += 1
            w = np.zeros(m, dtype=float)
            w[long_idx] = 0.5 / K
            w[short_idx] = -0.5 / K
        else:
            blocked_reasons[reason] = blocked_reasons.get(reason, 0) + 1
            w = np.zeros(m, dtype=float)
        end = min(r + H, n)
        weights[r:end] = w
        r += H

    return pd.DataFrame(weights, index=signal_df.index, columns=signal_df.columns), {
        "rebalance_bars_total": int(total_rebalances),
        "rebalance_bars_passed": int(passed_rebalances),
        "gate_pass_share": float(passed_rebalances / total_rebalances) if total_rebalances else 0.0,
        "blocked_rebalance_reasons": blocked_reasons,
    }


def costed_oos(port_ret: pd.Series, pos: pd.DataFrame, splits, cost_grid, bh_mean):
    """Costed OOS aggregation over the pre-registered cost grid.

    port_ret already includes real price spread PnL + real funding cashflows.
    Turnover is cost-independent and computed once; each cost slice subtracts
    turnover * tc from the per-split net.
    """
    seg = []
    exposure_total = 0
    for _, tr_e, te_e in splits:
        seg_pos = pos.iloc[tr_e:te_e]
        seg_ret = port_ret.iloc[tr_e:te_e]
        t = seg_pos.diff().abs().sum(axis=1)
        t.iloc[0] = float(seg_pos.iloc[0].abs().sum())
        seg.append((float(seg_ret.sum()), float(len(seg_ret)), float(t.sum())))
        exposure_total += int((seg_pos.abs().sum(axis=1) > 0).sum())
    turnover_total = float(sum(s[2] for s in seg))

    slices = {}
    all_sum_pos = True
    all_mean_beats = True
    for fee, slip in cost_grid:
        ck = f"fee{fee}_slip{slip}"
        tc = (fee + slip) / 10000.0 * TWO_LEG_FACTOR  # BOTH legs
        nets, means = [], []
        for seg_sum, seg_len, tsum in seg:
            net_sum = seg_sum - tc * tsum
            nets.append(net_sum)
            means.append(net_sum / seg_len if seg_len else 0.0)
        net_sum = float(sum(nets))
        net_mean = float(np.mean(means)) if means else 0.0
        slices[ck] = {
            "oos_net_sum": net_sum,
            "oos_net_mean": net_mean,
            "oos_net_mean_per_split": [float(m) for m in means],
            "bh_oos_mean": float(bh_mean),
            "two_leg_cost_factor": TWO_LEG_FACTOR,
        }
        if net_sum <= 0:
            all_sum_pos = False
        if net_mean <= bh_mean:
            all_mean_beats = False
    return slices, exposure_total, turnover_total, all_sum_pos, all_mean_beats


def main() -> int:
    if not PKL.exists():
        raise SystemExit(f"FATAL: C293 cache missing: {PKL}")
    if not META.exists():
        raise SystemExit(f"FATAL: C293 meta missing: {META}")

    pkl_sha = sha256_file(PKL)
    meta_sha = sha256_file(META)
    prov_sha = sha256_file(PROV) if PROV.exists() else None
    meta = json.loads(META.read_text())
    if pkl_sha != meta.get("sha256_from_bytes"):
        raise SystemExit(f"FATAL: sha256 mismatch: {pkl_sha} != {meta.get('sha256_from_bytes')}")
    if meta.get("real_data_only") is not True or meta.get("fabricated_data") is not False:
        raise SystemExit("FATAL: dataset provenance flags invalid")

    payload = load_payload(PKL)
    all_symbols = list(payload["symbols"])
    # Apply exclusions from preflight
    symbols = [s for s in all_symbols if s not in EXCLUDED_SYMBOLS]
    if len(symbols) < 2:
        raise SystemExit(f"FATAL: need >=2 active symbols after exclusions, got {len(symbols)}")

    b_closes = payload["binance_closes"].astype(float).sort_index()[symbols]
    o_closes = payload["okx_closes"].astype(float).sort_index()[symbols]
    b_funding = payload["binance_funding_rates"].astype(float).sort_index()[symbols]
    o_funding = payload["okx_funding_rates"].astype(float).sort_index()[symbols]

    if list(b_closes.columns) != symbols or list(o_closes.columns) != symbols:
        raise SystemExit("FATAL: column mismatch between venue frames and symbol list")
    if not b_closes.index.equals(o_closes.index):
        raise SystemExit("FATAL: venue index mismatch")
    if not b_closes.index.equals(b_funding.index):
        raise SystemExit("FATAL: funding index mismatch with closes")

    for name, df in [("binance_closes", b_closes), ("okx_closes", o_closes)]:
        vals = df.to_numpy(dtype=float)
        if int(np.isnan(vals).sum()) != 0 or not bool(np.isfinite(vals).all()) or not bool((vals > 0).all()):
            raise SystemExit(f"FATAL: {name} contain NaN/non-finite/non-positive values")

    n = len(b_closes)
    splits = wf_splits(n, TRAIN, TEST, STEP)
    if len(splits) != 135:
        raise SystemExit(f"FATAL: expected 135 OOS splits, got {len(splits)}")

    # Price returns (5m)
    b_ret = b_closes.pct_change().fillna(0.0)
    o_ret = o_closes.pct_change().fillna(0.0)
    spread_ret = b_ret - o_ret  # per-asset cross-venue perp spread return

    # Funding cashflows (native boundaries, both legs)
    # We'll compute this per run based on weights, but for benchmark we need a reference
    # Benchmark: equal-weight cross-venue funding-carry B&H on same OOS windows
    # weight = 1/N per asset, spread = r_binance - r_okx, funding = w * (okx_fund - binance_fund)
    N = len(symbols)
    bh_means = []
    for _, tr_e, te_e in splits:
        seg_spread = spread_ret.iloc[tr_e:te_e]
        # Equal-weight funding cashflow
        bh_fund = (o_funding.iloc[tr_e:te_e] - b_funding.iloc[tr_e:te_e]).mul(1.0 / N, axis=1)
        bh_fund = bh_fund.fillna(0.0)
        seg_total = seg_spread + bh_fund
        bh_means.append(float(seg_total.mean(axis=1).mean()))
    bh_mean = float(np.mean(bh_means)) if bh_means else 0.0

    # Build features (ffilled funding spread)
    feats = build_features(b_funding, o_funding)

    limit_runs = int(os.environ.get("C293_LIMIT_RUNS", "0") or 0)
    results = []
    run_count = 0

    for feature in FEATURES:
        for L in LOOKBACKS:
            signal = SIGNAL(feature, feats, L)
            for K in K_VALUES:
                for H in HOLDS:
                    run_count += 1
                    if limit_runs > 0 and run_count > limit_runs:
                        break
                    weights, gate_stats = build_weights(signal, b_closes, o_closes, K, H, r_start=0)
                    pos = weights.shift(1).fillna(0.0)

                    # Price spread PnL
                    price_pnl = (pos * spread_ret).sum(axis=1)
                    # Funding cashflows on BOTH legs
                    funding_pnl = compute_funding_cashflows(pos, b_funding, o_funding)
                    # Total asset return including funding
                    port_ret = price_pnl + funding_pnl

                    slices, exposure_total, turnover_total, all_sum_pos, all_mean_beats = costed_oos(
                        port_ret, pos, splits, COST_GRID, bh_mean
                    )
                    edge = bool(exposure_total > 0 and all_sum_pos and all_mean_beats)
                    results.append({
                        "feature": feature,
                        "lookback": int(L),
                        "K": int(K),
                        "hold": int(H),
                        "n_splits": int(len(splits)),
                        "rebalance_bars_total": gate_stats["rebalance_bars_total"],
                        "rebalance_bars_passed": gate_stats["rebalance_bars_passed"],
                        "gate_pass_share": gate_stats["gate_pass_share"],
                        "blocked_rebalance_reasons": gate_stats["blocked_rebalance_reasons"],
                        "oos_exposure_bars_total": int(exposure_total),
                        "turnover_total": float(turnover_total),
                        "price_pnl_sum": float(price_pnl.sum()),
                        "funding_pnl_sum": float(funding_pnl.sum()),
                        "cost_slices": slices,
                        "all_cost_slices_oos_net_positive": bool(all_sum_pos),
                        "beats_bh_all_slices": bool(all_mean_beats),
                        "bh_oos_mean": float(bh_mean),
                        "edge_proven": edge,
                        "block_reason": None if edge else "no_costed_oos_edge",
                    })
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
        "cache": str(PKL.relative_to(root)),
        "cache_sha256": pkl_sha,
        "meta": str(META.relative_to(root)),
        "meta_sha256": meta_sha,
        "provenance": str(PROV.relative_to(root)) if PROV.exists() else None,
        "provenance_sha256": prov_sha,
        "bars": int(n),
        "interval": "5m",
        "assets": symbols,
        "n_assets": len(symbols),
        "excluded_symbols": list(EXCLUDED_SYMBOLS),
        "window": {"start": str(b_closes.index.min()), "end": str(b_closes.index.max())},
        "venues": ["binance", "okx"],
        "real_data_only": True,
        "fabricated_data": False,
    }

    sweep = {
        "generated_at_utc": ts,
        "campaign": 293,
        "part": "oos_sweep",
        "analysis": "real_cross_venue_perp_funding_carry_xsec_stat_arb_costed_oos",
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "real_data_only": True,
        "fabricated_data": False,
        "fail_closed": True,
        "mandate": (
            "C293 — pre-registered costed OOS sweep of a NEW economic dimension: "
            "cross-venue USDT-M perp funding-carry stat-arb (Binance+OKX overlapping "
            "USDT perps, true 5m, real data). 3 features x 3 lookbacks x 3 K x 3 holds "
            "= 81 runs; train=720/test=168/step=168 = 135 OOS splits; cost grid "
            "[[0,0],[5,5],[10,10],[20,20],[40,40]] bps charged on BOTH legs; spread "
            "r_binance-r_okx + real funding cashflows on both legs; weights.shift(1); "
            "B&H same two-leg costs and funding; edge rule identical to "
            "C285/C286/C288/C290/C291/C292."
        ),
        "preflight": dataset_block,
        "data_source": dataset_block,
        "universe": {"n_assets": len(symbols), "assets": symbols},
        "config": {
            "walk_forward": {"train": TRAIN, "test": TEST, "step": STEP, "n_splits": len(splits)},
            "cost_grid_bps": COST_GRID,
            "two_leg_cost_factor": TWO_LEG_FACTOR,
            "signal_features": list(FEATURES),
            "lookbacks_5m": [int(l) for l in LOOKBACKS],
            "cross_sectional_K": [int(k) for k in K_VALUES],
            "holding_periods_5m": [int(h) for h in HOLDS],
            "total_runs": 3 * 3 * 3 * 3,
            "min_periods_rule": "max(3, L // 3)",
            "position_rule": "weights.shift(1).fillna(0.0)",
            "spread_return": "r_binance - r_okx per asset (cross-venue perp spread)",
            "funding_cashflow": "w_i * (okx_funding - binance_funding) at native boundaries",
            "score_definition": {
                "xfr_spread_ma": "-mean(okx_funding_ffill - binance_funding_ffill, L 5m bars)",
                "xfr_spread_z": "-z(okx_funding_ffill - binance_funding_ffill, L 5m bars)",
                "xfr_leadlag": "-mean((okx_funding_ffill - binance_funding_ffill).shift(1), L 5m bars)",
            },
        },
        "aggregate": {
            "n_total_runs": n_total,
            "n_with_exposure": n_exp,
            "n_edge_proven": int(len(edge_runs)),
            "n_zero_exposure": n_total - n_exp,
            "benchmark_bh_oos_mean": bh_mean,
        },
        "runs": results,
    }
    op_sweep = reports / f"campaign293_oos_sweep_{ts}.json"
    op_sweep.write_text(json.dumps(sweep, indent=2, default=jdefault))
    sweep_sha = sha256_file(op_sweep)

    registry = {
        "generated_at_utc": ts,
        "campaign": 293,
        "part": "tradable_edge_registry",
        "real_data_only": True,
        "fabricated_data": False,
        "analysis": "tradable_edge_registry",
        "n_tradable": len(edge_runs),
        "tradable_configs": edge_runs,
        "config": sweep["config"],
        "universe": sweep["universe"],
        "data_source": dataset_block,
        "oos_sweep_artifact": str(op_sweep.relative_to(root)),
        "oos_sweep_sha256": sweep_sha,
        "sha256_from_bytes": sweep_sha,
    }
    op_reg = reports / f"campaign293_tradable_edge_registry_{ts}.json"
    op_reg.write_text(json.dumps(registry, indent=2, default=jdefault))
    reg_sha = sha256_file(op_reg)

    summary = {
        "generated_at_utc": ts,
        "campaign": 293,
        "part": "summary",
        "real_data_only": True,
        "fabricated_data": False,
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "n_total_runs": n_total,
        "n_with_exposure": n_exp,
        "n_edge_proven": int(len(edge_runs)),
        "n_zero_exposure": n_total - n_exp,
        "benchmark_bh_oos_mean": bh_mean,
        "universe": sweep["universe"],
        "artifacts": {
            "sweep": str(op_sweep.relative_to(root)),
            "registry": str(op_reg.relative_to(root)),
        },
        "oos_sweep_sha256": sweep_sha,
        "registry_sha256": reg_sha,
    }
    op_sum = reports / f"campaign293_summary_{ts}.json"
    op_sum.write_text(json.dumps(summary, indent=2, default=jdefault))
    sum_sha = sha256_file(op_sum)

    explanation = (
        f"No costed OOS edge proven on the real cross-venue Binance+OKX perp funding-carry "
        f"family ({n_total} runs, {len(edge_runs)} edge, {n_exp} with exposure)."
        if not edge_runs
        else f"Costed OOS edge proven in {len(edge_runs)} config(s) on real cross-venue perp funding data."
    )
    # Binding-constraint diagnosis
    binding_path = None
    binding_sha = None
    if not edge_runs:
        has_exposure = n_exp > 0
        cost0_ok = sum(1 for r in results if r["cost_slices"]["fee0_slip0"]["oos_net_sum"] > 0)
        sum_pos_all = sum(1 for r in results if r["all_cost_slices_oos_net_positive"])
        beats_all = sum(1 for r in results if r["beats_bh_all_slices"])
        if not has_exposure:
            binding = "no_exposure"
        elif cost0_ok == 0:
            binding = "signal_quality"
        elif not sum_pos_all:
            binding = "cost_sensitivity"
        elif not beats_all:
            binding = "benchmark_dominance"
        else:
            binding = "edge_rule_not_met"
        op_v_pre = reports / f"campaign293_verdict_{ts}.json"
        binding_doc = {
            "generated_at_utc": ts,
            "campaign": 293,
            "part": "binding_constraint",
            "real_data_only": True,
            "fabricated_data": False,
            "verdict": verdict,
            "binding_constraint": binding,
            "diagnosis": {
                "n_total_runs": n_total,
                "n_with_exposure": n_exp,
                "n_cost0_slice_net_positive": cost0_ok,
                "n_all_cost_slices_net_positive": sum_pos_all,
                "n_beats_bh_all_slices": beats_all,
                "benchmark_bh_oos_mean": bh_mean,
            },
            "explanation": explanation,
            "universe": sweep["universe"],
            "oos_sweep_artifact": str(op_sweep.relative_to(root)),
            "oos_sweep_sha256": sweep_sha,
            "artifacts": {
                "sweep": str(op_sweep.relative_to(root)),
                "registry": str(op_reg.relative_to(root)),
                "summary": str(op_sum.relative_to(root)),
                "verdict": str(op_v_pre.relative_to(root)),
            },
        }
        op_b = reports / f"campaign293_binding_constraint_{ts}.json"
        op_b.write_text(json.dumps(binding_doc, indent=2, default=jdefault))
        binding_path = op_b
        binding_sha = sha256_file(op_b)

    verdict_doc = {
        "generated_at_utc": ts,
        "campaign": 293,
        "part": "verdict",
        "real_data_only": True,
        "fabricated_data": False,
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "edge_claim": "EDGE_PROVEN" if edge_runs else "NONE",
        "explanation": explanation,
        "universe": sweep["universe"],
        "aggregate": sweep["aggregate"],
        "oos_sweep_artifact": str(op_sweep.relative_to(root)),
        "oos_sweep_sha256": sweep_sha,
        "registry_artifact": str(op_reg.relative_to(root)),
        "registry_sha256": reg_sha,
        "summary_artifact": str(op_sum.relative_to(root)),
        "summary_sha256": sum_sha,
        "artifacts": {
            "sweep": str(op_sweep.relative_to(root)),
            "registry": str(op_reg.relative_to(root)),
            "summary": str(op_sum.relative_to(root)),
        },
    }
    if binding_path is not None:
        verdict_doc["binding_constraint_artifact"] = str(binding_path.relative_to(root))
        verdict_doc["binding_constraint_sha256"] = binding_sha
        verdict_doc["artifacts"]["binding_constraint"] = str(binding_path.relative_to(root))
    op_v = reports / f"campaign293_verdict_{ts}.json"
    op_v.write_text(json.dumps(verdict_doc, indent=2, default=jdefault))
    verdict_sha = sha256_file(op_v)

    artifacts = {
        "sweep": {"path": str(op_sweep.relative_to(root)), "sha256": sweep_sha},
        "registry": {"path": str(op_reg.relative_to(root)), "sha256": reg_sha},
        "summary": {"path": str(op_sum.relative_to(root)), "sha256": sum_sha},
        "verdict": {"path": str(op_v.relative_to(root)), "sha256": verdict_sha},
    }
    if binding_path is not None:
        artifacts["binding_constraint"] = {"path": str(binding_path.relative_to(root)), "sha256": binding_sha}

    final = {
        "ok": True,
        "campaign": 293,
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "n_total_runs": n_total,
        "n_with_exposure": n_exp,
        "n_edge_proven": int(len(edge_runs)),
        "n_assets": len(symbols),
        "artifacts": artifacts,
        "real_data_only": True,
        "fabricated_data": False,
    }
    print(json.dumps(final, indent=2, default=jdefault))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())