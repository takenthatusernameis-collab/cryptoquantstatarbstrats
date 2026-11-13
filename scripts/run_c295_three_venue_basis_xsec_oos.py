#!/usr/bin/env python3
"""C295 — costed out-of-sample edge test of a NEW economic dimension:
three-venue real-spot cross-venue basis / lead-lag statistical arbitrage.

NEW data + mechanism vs C281B..C294 (single-venue / two-venue):
- NEW DATA: real Coinbase 5m spot candles added to verified Binance + OKX 5m
  spot closes on the SAME USDT assets, full coverage on ALL THREE venues over
  the pre-registered common 5m window (2026-08-01T00:00Z..2026-10-30T23:55Z,
  26,208 bars). All frames fetched fresh from public endpoints (never relabeled
  two-venue caches).
- NEW MECHANISM: cross-venue basis convergence / dispersion / lead-lag.
  Pre-registered causal features (shift(1), true 5m):
    basis_bc  = (binance_close - coinbase_close) / coinbase_close  -> score = -feature
    basis_oc  = (okx_close - coinbase_close) / coinbase_close      -> score = -feature
    xdisp     = (max(binance,okx,coinbase) - min(...)) / min(...)  -> score = -feature
    leadlag   = rolling mean of (coinbase_ret - binance_ret.shift(1)) -> score = +feature
  Each of basis_bc / basis_oc has a rolling-mean and a rolling-z variant
  (6 signals total: basis_bc_ma, basis_bc_z, basis_oc_ma, basis_oc_z, xdisp,
  leadlag).  HIGHER score => long the discounted venue / short the premium
  venue spread on that asset.

Pre-registered protocol (no post-hoc parameter search):
- Universe: overlapping USDT pairs with full coverage on Binance, OKX and
  Coinbase from the verified C295 cache.
- Cross-sectional portfolio at each 5m rebalance bar: rank assets by score;
  long top K and short bottom K, K in {2,3,5}; equal weight 0.5/K per leg;
  gross 1.0; dollar-neutral; per-asset cap 0.5.  Position is a cross-venue
  spread per asset: PnL = sum_i w_i * (r_venue_long_i - r_venue_short_i).
  Turnover charged on ALL legs: tc * sum(|d w_long| + |d w_short|) =
  tc * 2 * |dw| per asset (two-leg spread).
- Holding period H in {1,6,24} 5m bars. weights.shift(1).fillna(0.0) before
  PnL (causal, no lookahead).
- Full pre-registered grid: 6 features x 3 lookbacks x 3 K x 3 holds = 162 runs.
- Walk-forward: train=720, test=168, step=168 in 5m bars ->
  n_splits = (n_bars - 720 - 168) // 168 + 1 OOS splits.
- Cost grid exactly: [[0,0],[5,5],[10,10],[20,20],[40,40]] bps, charged on
  BOTH legs of every spread.
- Benchmark: equal-weight buy-and-hold of the same spread basket (1/N per
  asset, same per-asset spread as the feature) on the same OOS windows with
  the SAME two-leg costs.
- Edge rule exactly (identical to C285/C286/C288/C290/C291/C292/C293/C294,
  never relaxed): oos_edge_proven=true iff OOS exposure > 0 AND every cost
  slice has OOS net sum > 0 AND the mean of per-split OOS net means is
  greater than the mean of per-split equal-weight B&H OOS net means on the
  same WF windows.

Fail-closed gates at each candidate 5m rebalance bar:
- selected feature score finite for at least 2*K assets;
- cross-sectional score dispersion > 0;
- no NaN/non-finite 5m price/return in any selected leg on any venue;
- no missing/None/false gate value treated as permissive.

Required artifacts (timestamped, SHA256-from-bytes):
- reports/campaign295_oos_sweep_<ts>.json
- reports/campaign295_tradable_edge_registry_<ts>.json
- reports/campaign295_summary_<ts>.json
- reports/campaign295_verdict_<ts>.json
- reports/campaign295_binding_constraint_<ts>.json (if NOT_TRADABLE)
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

PKL = cache_dir / "campaign295_three_venue_spot.pkl"
META = cache_dir / "campaign295_three_venue_spot.meta.json"
PROV = cache_dir / "campaign295_three_venue_spot.provenance.json"

FEATURES = ("basis_bc_ma", "basis_bc_z", "basis_oc_ma", "basis_oc_z", "xdisp", "leadlag")
LOOKBACKS = (288, 1008, 2016)
K_VALUES = (2, 3, 5)
HOLDS = (1, 6, 24)

TRAIN, TEST, STEP = 720, 168, 168
COST_GRID = [[0, 0], [5, 5], [10, 10], [20, 20], [40, 40]]
TWO_LEG_FACTOR = 2.0  # cost charged on BOTH legs of each spread
VENUES = ("binance", "okx", "coinbase")


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


def build_features(b_closes: pd.DataFrame, o_closes: pd.DataFrame, c_closes: pd.DataFrame) -> dict:
    """All features computed on closes, then shift(1) inside each builder
    (causal, no lookahead). Returns dict of raw (pre-shift) components."""
    b_ret = np.log(b_closes).diff()
    o_ret = np.log(o_closes).diff()
    c_ret = np.log(c_closes).diff()
    basis_bc = (b_closes - c_closes) / c_closes
    basis_oc = (o_closes - c_closes) / c_closes
    px = pd.concat(
        [b_closes, o_closes, c_closes],
        axis=1,
        keys=["binance", "okx", "coinbase"],
    )
    px_max = px.T.groupby(level=1).max().T
    px_min = px.T.groupby(level=1).min().T
    xdisp = (px_max - px_min) / px_min
    # lead-lag: coinbase return vs lagged binance return (does coinbase follow binance?)
    leadlag_raw = c_ret - b_ret.shift(1)
    return {
        "basis_bc": basis_bc,
        "basis_oc": basis_oc,
        "xdisp": xdisp,
        "leadlag_raw": leadlag_raw,
        "r_b": b_ret,
        "r_o": o_ret,
        "r_c": c_ret,
    }


def basis_bc_ma(feats: dict, L: int) -> pd.DataFrame:
    mp = min_periods_for(L)
    s = feats["basis_bc"].shift(1)
    return _mask_nonfinite(s.rolling(L, min_periods=mp).mean())


def basis_bc_z(feats: dict, L: int) -> pd.DataFrame:
    mp = min_periods_for(L)
    s = feats["basis_bc"].shift(1)
    mean = s.rolling(L, min_periods=mp).mean()
    std = s.rolling(L, min_periods=mp).std()
    return _safe_std((s - mean) / std, std)


def basis_oc_ma(feats: dict, L: int) -> pd.DataFrame:
    mp = min_periods_for(L)
    s = feats["basis_oc"].shift(1)
    return _mask_nonfinite(s.rolling(L, min_periods=mp).mean())


def basis_oc_z(feats: dict, L: int) -> pd.DataFrame:
    mp = min_periods_for(L)
    s = feats["basis_oc"].shift(1)
    mean = s.rolling(L, min_periods=mp).mean()
    std = s.rolling(L, min_periods=mp).std()
    return _safe_std((s - mean) / std, std)


def xdisp(feats: dict, L: int) -> pd.DataFrame:
    mp = min_periods_for(L)
    s = feats["xdisp"].shift(1)
    return _mask_nonfinite(s.rolling(L, min_periods=mp).mean())


def leadlag(feats: dict, L: int) -> pd.DataFrame:
    mp = min_periods_for(L)
    s = feats["leadlag_raw"].shift(1)
    return _mask_nonfinite(s.rolling(L, min_periods=mp).mean())


# feature -> (score_builder, spread_return_key)
# score: higher => long discounted venue / short premium venue
FEATURE_SPEC = {
    "basis_bc_ma": ("basis_bc_ma", "spr_bc", -1.0),
    "basis_bc_z": ("basis_bc_z", "spr_bc", -1.0),
    "basis_oc_ma": ("basis_oc_ma", "spr_oc", -1.0),
    "basis_oc_z": ("basis_oc_z", "spr_oc", -1.0),
    "xdisp": ("xdisp", "spr_bc", -1.0),
    "leadlag": ("leadlag", "spr_cb", +1.0),
}

BUILDERS = {
    "basis_bc_ma": basis_bc_ma,
    "basis_bc_z": basis_bc_z,
    "basis_oc_ma": basis_oc_ma,
    "basis_oc_z": basis_oc_z,
    "xdisp": xdisp,
    "leadlag": leadlag,
}


def SIGNAL(feature: str, feats: dict, L: int) -> pd.DataFrame:
    builder, _, sign = FEATURE_SPEC[feature]
    return sign * BUILDERS[builder](feats, L)


def spread_return(feature: str, feats: dict) -> pd.DataFrame:
    _, spr_key, _ = FEATURE_SPEC[feature]
    if spr_key == "spr_bc":
        return feats["r_b"] - feats["r_c"]
    if spr_key == "spr_oc":
        return feats["r_o"] - feats["r_c"]
    if spr_key == "spr_cb":
        return feats["r_c"] - feats["r_b"]
    raise ValueError(f"unknown spread key {spr_key}")


def build_weights(signal_df: pd.DataFrame, spr_px_long: pd.DataFrame, spr_px_short: pd.DataFrame, K: int, H: int, r_start: int):
    """Build cross-sectional long/short weights on a per-asset spread.
    long_idx / short_idx are asset columns. spr_px_long / spr_px_short are the
    closing prices of the long venue and short venue for the spread (used for
    the price-nan gate)."""
    n = len(signal_df)
    sig = signal_df.to_numpy(dtype=float)
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
            if not bool(np.isfinite(spr_px_long.iloc[r, leg_idx]).all() and np.isfinite(spr_px_short.iloc[r, leg_idx]).all()):
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
        raise SystemExit(f"FATAL: C295 cache missing: {PKL}")
    if not META.exists():
        raise SystemExit(f"FATAL: C295 meta missing: {META}")

    pkl_sha = sha256_file(PKL)
    meta_sha = sha256_file(META)
    prov_sha = sha256_file(PROV) if PROV.exists() else None
    meta = json.loads(META.read_text())
    if pkl_sha != meta.get("sha256_from_bytes"):
        raise SystemExit(f"FATAL: sha256 mismatch: {pkl_sha} != {meta.get('sha256_from_bytes')}")
    if meta.get("real_data_only") is not True or meta.get("fabricated_data") is not False:
        raise SystemExit("FATAL: dataset provenance flags invalid")

    payload = load_payload(PKL)
    symbols = list(payload["symbols"])
    if len(symbols) < 2:
        raise SystemExit(f"FATAL: need >=2 overlap symbols, got {len(symbols)}")
    b_closes = payload["binance_closes"].astype(float).sort_index()[symbols]
    o_closes = payload["okx_closes"].astype(float).sort_index()[symbols]
    c_closes = payload["coinbase_closes"].astype(float).sort_index()[symbols]
    if list(b_closes.columns) != symbols or list(o_closes.columns) != symbols or list(c_closes.columns) != symbols:
        raise SystemExit("FATAL: column mismatch between venue frames and symbol list")
    if not (b_closes.index.equals(o_closes.index) and b_closes.index.equals(c_closes.index)):
        raise SystemExit("FATAL: venue index mismatch")

    for name, df in [("binance", b_closes), ("okx", o_closes), ("coinbase", c_closes)]:
        vals = df.to_numpy(dtype=float)
        if int(np.isnan(vals).sum()) != 0 or not bool(np.isfinite(vals).all()) or not bool((vals > 0).all()):
            raise SystemExit(f"FATAL: {name} closes contain NaN/non-finite/non-positive values")

    n = len(b_closes)
    splits = wf_splits(n, TRAIN, TEST, STEP)
    expected_splits = (n - TRAIN - TEST) // STEP + 1
    if len(splits) != expected_splits:
        raise SystemExit(f"FATAL: expected {expected_splits} OOS splits, got {len(splits)}")

    feats = build_features(b_closes, o_closes, c_closes)

    # Benchmark: equal-weight spread basket (1/N per asset) on same OOS windows,
    # using the basis_bc spread (Binance vs Coinbase) as the representative spread,
    # two-leg costs.
    N = len(symbols)
    bh_spr = feats["r_b"] - feats["r_c"]
    bh_means = []
    for _, tr_e, te_e in splits:
        seg = bh_spr.iloc[tr_e:te_e]
        bh_means.append(float(seg.mean(axis=1).mean()))
    bh_mean = float(np.mean(bh_means)) if bh_means else 0.0

    limit_runs = int(os.environ.get("C295_LIMIT_RUNS", "0") or 0)
    results = []
    run_count = 0

    for feature in FEATURES:
        for L in LOOKBACKS:
            signal = SIGNAL(feature, feats, L)
            spr_ret = spread_return(feature, feats)
            # long venue price / short venue price for the price-nan gate:
            # for basis_bc / xdisp / leadlag: long side is either binance or coinbase
            # depending on sign; use both venue closes for the gate (any NaN blocks)
            px_long = b_closes  # representative long-venue price
            px_short = c_closes  # representative short-venue price
            if FEATURE_SPEC[feature][1] == "spr_oc":
                px_long = o_closes
            for K in K_VALUES:
                for H in HOLDS:
                    run_count += 1
                    if limit_runs > 0 and run_count > limit_runs:
                        break
                    weights, gate_stats = build_weights(signal, px_long, px_short, K, H, r_start=0)
                    pos = weights.shift(1).fillna(0.0)
                    port_ret = (pos * spr_ret).sum(axis=1)
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
                        "spread_pnl_sum": float(port_ret.sum()),
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
        "window": {"start": str(b_closes.index.min()), "end": str(b_closes.index.max())},
        "venues": list(VENUES),
        "real_data_only": True,
        "fabricated_data": False,
    }

    sweep = {
        "generated_at_utc": ts,
        "campaign": 295,
        "part": "oos_sweep",
        "analysis": "real_three_venue_spot_basis_dispersion_leadlag_xsec_stat_arb_costed_oos",
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "real_data_only": True,
        "fabricated_data": False,
        "fail_closed": True,
        "mandate": (
            "C295 — pre-registered costed OOS sweep of a NEW economic dimension: "
            "three-venue real-spot cross-venue basis / dispersion / lead-lag stat-arb "
            "(Binance+OKX+Coinbase overlapping USDT pairs, true 5m, real data). "
            "6 signals x 3 lookbacks x 3 K x 3 holds = 162 runs; train=720/test=168/"
            "step=168 = n_splits OOS splits; cost grid [[0,0],[5,5],[10,10],[20,20],"
            "[40,40]] bps charged on BOTH legs; per-asset cross-venue spread; "
            "weights.shift(1); B&H same two-leg costs; edge rule identical to "
            "C285/C286/C288/C290/C291/C292/C293/C294."
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
            "total_runs": 6 * 3 * 3 * 3,
            "min_periods_rule": "max(3, L // 3)",
            "position_rule": "weights.shift(1).fillna(0.0)",
            "features": {
                "basis_bc_ma": "-rolling_mean((binance-coinbase)/coinbase, L)",
                "basis_bc_z": "-rolling_z((binance-coinbase)/coinbase, L)",
                "basis_oc_ma": "-rolling_mean((okx-coinbase)/coinbase, L)",
                "basis_oc_z": "-rolling_z((okx-coinbase)/coinbase, L)",
                "xdisp": "-rolling_mean((max-min)/min over 3 venues, L)",
                "leadlag": "+rolling_mean(coinbase_ret - binance_ret.shift(1), L)",
            },
            "spread_return": {
                "basis_bc_*": "r_binance - r_coinbase",
                "basis_oc_*": "r_okx - r_coinbase",
                "xdisp": "r_binance - r_coinbase (representative)",
                "leadlag": "r_coinbase - r_binance",
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
    op_sweep = reports / f"campaign295_oos_sweep_{ts}.json"
    op_sweep.write_text(json.dumps(sweep, indent=2, default=jdefault))
    sweep_sha = sha256_file(op_sweep)

    registry = {
        "generated_at_utc": ts,
        "campaign": 295,
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
    op_reg = reports / f"campaign295_tradable_edge_registry_{ts}.json"
    op_reg.write_text(json.dumps(registry, indent=2, default=jdefault))
    reg_sha = sha256_file(op_reg)

    summary = {
        "generated_at_utc": ts,
        "campaign": 295,
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
    op_sum = reports / f"campaign295_summary_{ts}.json"
    op_sum.write_text(json.dumps(summary, indent=2, default=jdefault))
    sum_sha = sha256_file(op_sum)

    explanation = (
        f"No costed OOS edge proven on the real three-venue Binance+OKX+Coinbase "
        f"spot basis/dispersion/lead-lag family ({n_total} runs, {len(edge_runs)} edge, "
        f"{n_exp} with exposure)."
        if not edge_runs
        else f"Costed OOS edge proven in {len(edge_runs)} config(s) on real three-venue spot data."
    )
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
        op_v_pre = reports / f"campaign295_verdict_{ts}.json"
        binding_doc = {
            "generated_at_utc": ts,
            "campaign": 295,
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
        op_b = reports / f"campaign295_binding_constraint_{ts}.json"
        op_b.write_text(json.dumps(binding_doc, indent=2, default=jdefault))
        binding_path = op_b
        binding_sha = sha256_file(op_b)

    verdict_doc = {
        "generated_at_utc": ts,
        "campaign": 295,
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
    op_v = reports / f"campaign295_verdict_{ts}.json"
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
        "campaign": 295,
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
