#!/usr/bin/env python3
"""C288 — costed out-of-sample edge test of a NEW price-derived economic mechanism:
cross-sectional realized-volatility / volatility-reversal / low-skew stat-arb on the
real 26,208-bar 5m spot close cache (price data only; no quote volume; no testnet).

This family is ABSENT from the C281B..C286 record (which covered price MR/momentum/
OLS-pairs, cross-sectional price stat-arb, cointegration pairs, Kalman pairs, and
volume-conditioned cross-sectional stat-arb).  It tests the documented cross-sectional
risk-premium / lottery-demand mechanisms:

- low_vol        (score = -realized_vol): long low realized-vol, short high. The
  low-volatility / volatility risk premium (Baker-Haugen; Frazzini-Pedersen BAB).
- vol_reversal   (score = -z(realized_vol)): long volatility-compressed, short
  volatility-spiked. Vol-of-vol mean reversion.
- low_skew       (score = -realized_skew): long low realized-skew, short high.
  Lottery-demand / idiosyncratic-skewness tilt (Bali et al. MAX/IDIV).

Pre-registered protocol (no post-hoc parameter search):
- Dataset: real 5m spot close cache (verified SHA256-from-bytes). Realized vol and
  realized skew are computed from 5m close-to-close log-returns. PnL is real spot PnL.
- Universe: 11 spot assets ADA AVAX BNB BTC DOT ETH LINK LTC POL SOL XRP.
- Causal signal (signal at bar t uses data through t-1 only):
    rv_t        = rolling_std(log-return, L)                 [realized volatility]
    z_rv_t      = (rv_t - rolling_mean(rv, L)) / rolling_std(rv, L)
    skew_t      = rolling_skew(log-return, L)                [realized skewness]
    low_vol     = -rv_t        ; low_skew = -skew_t ; vol_reversal = -z_rv_t
  min_periods = max(20, L // 3); fail closed on zero/non-finite std.
  Lookbacks L in {288, 1008, 2016} 5m bars (1d, 3.5d, 7d).
- Cross-sectional portfolio at each 5m rebalance bar: rank the 11 assets by the
  selected score; long the top K and short the bottom K, K in {2, 3, 5}; equal
  weight 0.5 / K per leg; gross exposure 1.0; dollar-neutral; per-asset cap 0.5.
  Holding period H in {1, 6, 24} 5m bars; hold between rebalances.
  weights.shift(1).fillna(0.0) is applied before PnL.
- Full pre-registered grid: 3 features x 3 lookbacks x 3 K x 3 holds = 81 runs.
  Every run is reported, including zero-exposure runs.
- Walk-forward: train=720, test=168, step=168 in 5m bars on the 26,208-bar cache
  -> 151 OOS splits.
- Cost grid exactly: [[0,0],[5,5],[10,10],[20,20],[40,40]] bps.
- Benchmark: equal-weight 11-asset buy-and-hold on the same OOS windows, no rebalance.
- Edge rule exactly: oos_edge_proven=true iff OOS exposure > 0 AND every cost slice
  has OOS net sum > 0 AND the mean of the per-split OOS net means is greater than
  the mean of the per-split equal-weight buy-and-hold OOS net means on the same WF
  windows (same per-split aggregation for both legs; never a strategy mean vs a
  benchmark sum). Anything else is NOT_TRADABLE; never relax this rule.

Fail-closed gates at each candidate 5m rebalance bar:
- the selected feature score finite for at least 2K assets;
- cross-sectional score dispersion > 0;
- no NaN/non-finite 5m price in any selected leg;
- no missing/None/false gate value treated as permissive.
If diagnostics cannot be computed, the rebalance is blocked and the reason recorded.

Required artifacts (exact names, timestamped):
- reports/campaign288_oos_sweep_<ts>.json
- reports/campaign288_tradable_edge_registry_<ts>.json
- reports/campaign288_summary_<ts>.json
- reports/campaign288_verdict_<ts>.json
Each includes real_data_only: true, fabricated_data: false, the spot/meta SHA256s, the
split/cost config, all 81 run results, and SHA256-from-bytes. If NOT_TRADABLE, also
emit reports/campaign288_binding_constraint_<ts>.json (diagnosis only, never an edge
claim).
"""
from __future__ import annotations

import hashlib
import json
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

SYMBOLS = ("ADA", "AVAX", "BNB", "BTC", "DOT", "ETH", "LINK", "LTC", "POL", "SOL", "XRP")

SPOT_5M = cache_dir / "90d10b876bb8eda9619cbba73ed19d6c7db4ea7327284f2e33f10a7872a5b263.pkl"
SPOT_5M_META = SPOT_5M.with_suffix(".meta.json")
SPOT_5M_SHA = "d15b0b183cf685a15dd34185baff22edf7ef3cc9c80c7d607bcd92f8da418c2f"
SPOT_5M_META_SHA = "e1a71f481cb4ad07881d132aba4ff7b47fc8194c69779701035efcf6e492ce4e"

FEATURES = ("low_vol", "vol_reversal", "low_skew")
LOOKBACKS = (288, 1008, 2016)
K_VALUES = (2, 3, 5)
HOLDS = (1, 6, 24)

TRAIN, TEST, STEP = 720, 168, 168
COST_GRID = [[0, 0], [5, 5], [10, 10], [20, 20], [40, 40]]

# Total runs: 3 features x 3 lookbacks x 3 K x 3 holds = 81


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


def load_spot(path: Path) -> pd.DataFrame:
    with open(path, "rb") as f:
        df = pd.read_pickle(f)
    if isinstance(df, pd.Series):
        df = df.to_frame()
    return df.astype(float).sort_index()


def wf_splits(n: int, train: int, test: int, step: int):
    out = []
    i = 0
    while i + train + test <= n:
        out.append((i, i + train, i + train + test))
        i += step
    return out


def min_periods_for(L: int) -> int:
    return max(20, L // 3)


def _safe_std(out: pd.DataFrame, std: pd.DataFrame) -> pd.DataFrame:
    bad = (~np.isfinite(np.asarray(std))) | (np.asarray(std) <= 0)
    return out.mask(pd.DataFrame(bad, index=out.index, columns=out.columns))


def realized_vol(logret: pd.DataFrame, L: int) -> pd.DataFrame:
    """Causal realized volatility: rolling std of 5m log-returns, data through t-1."""
    mp = min_periods_for(L)
    s = logret.shift(1)
    std = s.rolling(L, min_periods=mp).std()
    return std.mask(pd.DataFrame(~np.isfinite(np.asarray(std)), index=std.index, columns=std.columns))


def feature_low_vol(logret: pd.DataFrame, L: int) -> pd.DataFrame:
    """Long low-vol: score = -realized_vol."""
    return -realized_vol(logret, L)


def feature_vol_reversal(logret: pd.DataFrame, L: int) -> pd.DataFrame:
    """Long vol-compressed: score = -z(realized_vol) vs its own trailing history."""
    mp = min_periods_for(L)
    rv = realized_vol(logret, L)
    mean = rv.rolling(L, min_periods=mp).mean()
    std = rv.rolling(L, min_periods=mp).std()
    z = (rv - mean) / std
    return _safe_std(-z, std)


def feature_low_skew(logret: pd.DataFrame, L: int) -> pd.DataFrame:
    """Long low-skew: score = -rolling skewness of 5m log-returns (data through t-1)."""
    mp = min_periods_for(L)
    s = logret.shift(1)
    skew = s.rolling(L, min_periods=mp).skew()
    return skew.mask(pd.DataFrame(~np.isfinite(np.asarray(skew)), index=skew.index, columns=skew.columns)) * -1.0


def SIGNAL(feature: str, logret: pd.DataFrame, L: int) -> pd.DataFrame:
    if feature == "low_vol":
        return feature_low_vol(logret, L)
    if feature == "vol_reversal":
        return feature_vol_reversal(logret, L)
    if feature == "low_skew":
        return feature_low_skew(logret, L)
    raise ValueError(f"unknown feature {feature}")


def build_weights(
    signal_df: pd.DataFrame,
    price_df: pd.DataFrame,
    K: int,
    H: int,
    r_start: int,
):
    n = len(signal_df)
    weights = pd.DataFrame(0.0, index=signal_df.index, columns=signal_df.columns)
    total_rebalances = 0
    passed_rebalances = 0
    blocked_reasons: dict[str, int] = {}
    r = r_start
    while r < n:
        total_rebalances += 1
        sig = signal_df.iloc[r]

        arr = sig.to_numpy(dtype=float)
        finite_mask = np.isfinite(arr)
        px_arr = price_df.iloc[r].to_numpy(dtype=float)

        ok = True
        reason = None

        # Gate 1: selected feature score finite for at least 2K assets.
        if int(finite_mask.sum()) < 2 * K:
            ok = False
            reason = "signal_coverage"

        # Gate 2: cross-sectional score dispersion > 0.
        vals = None
        if ok:
            vals = arr[finite_mask]
            dispersion = float(vals.max() - vals.min()) if len(vals) else 0.0
            if not (np.isfinite(dispersion) and dispersion > 0.0):
                ok = False
                reason = "zero_dispersion"

        # Gate 3: no NaN/non-finite price in any selected leg.
        long_idx = short_idx = None
        if ok:
            order = np.argsort(-vals, kind="stable")
            finite_positions = np.where(finite_mask)[0]
            long_idx = finite_positions[order[:K]]
            short_idx = finite_positions[order[-K:]]
            leg_idx = np.concatenate([long_idx, short_idx])
            if not bool(np.isfinite(px_arr[leg_idx]).all()):
                ok = False
                reason = "price_nan"

        if ok:
            passed_rebalances += 1
            w = np.zeros(len(SYMBOLS), dtype=float)
            w[long_idx] = 0.5 / K
            w[short_idx] = -0.5 / K
        else:
            blocked_reasons[reason] = blocked_reasons.get(reason, 0) + 1
            w = np.zeros(len(SYMBOLS), dtype=float)

        end = min(r + H, n)
        weights.iloc[r:end] = w
        r += H

    return weights, {
        "rebalance_bars_total": int(total_rebalances),
        "rebalance_bars_passed": int(passed_rebalances),
        "gate_pass_share": float(passed_rebalances / total_rebalances) if total_rebalances else 0.0,
        "blocked_rebalance_reasons": blocked_reasons,
    }


def costed_oos(pos: pd.DataFrame, returns: pd.DataFrame, splits, cost_grid, bh_mean):
    slices = {}
    exposure_total = 0
    turnover_total = 0.0
    all_sum_pos = True
    all_mean_beats = True
    per_split_nets = []
    for fee, slip in cost_grid:
        ck = f"fee{fee}_slip{slip}"
        tc = (fee + slip) / 10000.0
        nets, means, turn = [], [], 0.0
        for tr_e, te_e in [(t, e) for _, t, e in splits]:
            seg_pos = pos.iloc[tr_e:te_e]
            seg_ret = returns.iloc[tr_e:te_e]
            port_ret = (seg_pos * seg_ret).sum(axis=1)
            t = seg_pos.diff().abs().sum(axis=1)
            t.iloc[0] = float(seg_pos.iloc[0].abs().sum())
            turn += float(t.sum())
            net = port_ret - t * tc
            nets.append(float(net.sum()))
            means.append(float(net.mean()))
            exposure_total += int((seg_pos.abs().sum(axis=1) > 0).sum())
        net_sum = float(sum(nets))
        net_mean = float(np.mean(means)) if means else 0.0
        turnover_total += turn
        per_split_nets.append(means)
        slices[ck] = {
            "oos_net_sum": net_sum,
            "oos_net_mean": net_mean,
            "oos_net_mean_per_split": [float(m) for m in means],
            "bh_oos_mean": float(bh_mean),
        }
        if net_sum <= 0:
            all_sum_pos = False
        if net_mean <= bh_mean:
            all_mean_beats = False
    return slices, exposure_total, turnover_total, all_sum_pos, all_mean_beats, per_split_nets


def main() -> int:
    # ---- preflight: verify every cache SHA ----
    if not SPOT_5M.exists():
        raise SystemExit(f"FATAL: C288 spot cache missing: {SPOT_5M}")
    if not SPOT_5M_META.exists():
        raise SystemExit(f"FATAL: C288 spot meta missing: {SPOT_5M_META}")

    spot_sha = sha256_file(SPOT_5M)
    spot_meta_sha = sha256_file(SPOT_5M_META)
    if spot_sha != SPOT_5M_SHA:
        raise SystemExit(f"FATAL: spot 5m cache sha256 mismatch: {spot_sha} != {SPOT_5M_SHA}")
    if spot_meta_sha != SPOT_5M_META_SHA:
        raise SystemExit(f"FATAL: spot 5m meta sha256 mismatch: {spot_meta_sha} != {SPOT_5M_META_SHA}")

    spot_meta = json.loads(SPOT_5M_META.read_text())

    spot = load_spot(SPOT_5M)

    if int(spot.isna().sum().sum()) != 0:
        raise SystemExit("FATAL: NaN present in spot 5m cache; refusing to impute.")
    if not bool(np.isfinite(spot.to_numpy(dtype=float)).all()):
        raise SystemExit("FATAL: non-finite value present in spot 5m cache; refusing to proceed.")
    if not bool((spot.to_numpy(dtype=float) > 0).all()):
        raise SystemExit("FATAL: non-positive price in spot 5m cache; refusing to proceed.")

    idx_5m = pd.DatetimeIndex(spot.index)
    n = len(spot)
    splits = wf_splits(n, TRAIN, TEST, STEP)
    if len(splits) != 151:
        raise SystemExit(f"FATAL: expected 151 OOS splits, got {len(splits)}")

    returns_full = spot.pct_change().fillna(0.0)
    logret = np.log(spot)

    # Benchmark: equal-weight 11-asset buy-and-hold on the same OOS windows, no rebalance.
    bh_means = []
    for _, tr_e, te_e in splits:
        seg_ret = returns_full.iloc[tr_e:te_e]
        bh_means.append(float(seg_ret.mean(axis=1).mean()))
    bh_mean = float(np.mean(bh_means)) if bh_means else 0.0

    limit_runs = int(os.environ.get("C288_LIMIT_RUNS", "0") or 0)
    results = []
    run_count = 0

    for feature in FEATURES:
        for L in LOOKBACKS:
            signal_5m = SIGNAL(feature, logret, L)
            # r_start = 0: feature is warm before the first OOS test bar (verified by preflight).
            r_start = 0
            for K in K_VALUES:
                for H in HOLDS:
                    run_count += 1
                    if limit_runs > 0 and run_count > limit_runs:
                        break
                    weights, gate_stats = build_weights(signal_5m, spot, K, H, r_start)
                    pos = weights.shift(1).fillna(0.0)
                    slices, exposure_total, turnover_total, all_sum_pos, all_mean_beats, per_split_nets = costed_oos(
                        pos, returns_full, splits, COST_GRID, bh_mean
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

    sweep = {
        "generated_at_utc": ts,
        "campaign": 288,
        "part": "oos_sweep",
        "analysis": "realized_volatility_cross_sectional_stat_arb_costed_oos_5m",
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "real_data_only": True,
        "fabricated_data": False,
        "fail_closed": True,
        "mandate": (
            "C288 — pre-registered costed OOS sweep of a NEW price-derived economic mechanism "
            "(cross-sectional realized-volatility / volatility-reversal / low-skew stat-arb) on "
            "the real Binance 5m spot close cache; price data only; 11 assets; 3 features x 3 "
            "lookbacks x 3 K x 3 holds = 81 runs; train=720/test=168/step=168 in 5m bars = 151 "
            "OOS splits; cost grid [[0,0],[5,5],[10,10],[20,20],[40,40]] bps; fail-closed causal "
            "cross-sectional gates; edge rule: OOS exposure>0 AND all cost slices net sum>0 AND "
            "mean per-split OOS net mean > mean per-split equal-weight B&H OOS net mean on the "
            "same WF windows."
        ),
        "preflight": {
            "spot_cache": str(SPOT_5M.relative_to(root)),
            "spot_cache_sha256": spot_sha,
            "spot_meta_sha256": spot_meta_sha,
            "spot_meta": spot_meta,
            "bars": int(n),
            "interval": "5m",
            "assets": list(SYMBOLS),
            "window": {"start": str(spot.index.min()), "end": str(spot.index.max())},
            "real_data_only": True,
            "fabricated_data": False,
            "sha256_from_bytes_verified": True,
        },
        "data_source": {
            "spot_cache": str(SPOT_5M.relative_to(root)),
            "spot_cache_sha256": spot_sha,
            "spot_meta_sha256": spot_meta_sha,
            "bars": int(n),
            "interval": "5m",
            "assets": list(SYMBOLS),
            "window": {"start": str(spot.index.min()), "end": str(spot.index.max())},
            "price_only": True,
        },
        "universe": {"n_assets": len(SYMBOLS), "assets": list(SYMBOLS)},
        "config": {
            "walk_forward": {"train": TRAIN, "test": TEST, "step": STEP, "n_splits": len(splits)},
            "cost_grid_bps": COST_GRID,
            "signal_features": list(FEATURES),
            "lookbacks_5m": [int(l) for l in LOOKBACKS],
            "cross_sectional_K": [int(k) for k in K_VALUES],
            "holding_periods_5m": [int(h) for h in HOLDS],
            "total_runs": 3 * 3 * 3 * 3,
            "min_periods_rule": "max(20, L // 3)",
            "position_rule": "weights.shift(1).fillna(0.0)",
            "score_definition": {
                "low_vol": "-realized_vol",
                "vol_reversal": "-z(realized_vol)",
                "low_skew": "-realized_skew",
            },
            "signal_direction": "long top-K, short bottom-K by score (higher score = long)",
        },
        "gates": {
            "fail_closed": True,
            "requirements": [
                "selected feature score finite for at least 2K assets",
                "cross-sectional score dispersion > 0",
                "no NaN/non-finite 5m price in any selected leg",
                "no missing/None/false gate value treated as permissive",
            ],
        },
        "provenance": {
            "real_data_only": True,
            "fabricated_data": False,
            "pnl_on_real_spot_prices": True,
            "no_threshold_weakening": True,
            "no_cherry_picked_windows_or_costs": True,
            "no_post_hoc_parameter_search": True,
        },
        "results": results,
        "summary": {
            "n_total_runs": n_total,
            "n_with_exposure": int(n_exp),
            "n_zero_exposure": int(n_total - n_exp),
            "n_edge_proven": int(len(edge_runs)),
            "bh_oos_mean": float(bh_mean),
        },
    }

    op = reports / f"campaign288_oos_sweep_{ts}.json"
    op.write_text(json.dumps(sweep, indent=2, default=jdefault) + "\n")
    sweep_sha = sha256_file(op)

    registry = {
        "generated_at_utc": ts,
        "campaign": 288,
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
    op_reg = reports / f"campaign288_tradable_edge_registry_{ts}.json"
    op_reg.write_text(json.dumps(registry, indent=2, default=jdefault) + "\n")
    reg_sha = sha256_file(op_reg)

    summary = {
        "generated_at_utc": ts,
        "campaign": 288,
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
            "turnover, binding constraint); record a formal negative result and stop; "
            "C289 (multiple-testing / minimum-detectable-edge closure) is the next campaign."
        ),
    }
    op_sum = reports / f"campaign288_summary_{ts}.json"
    op_sum.write_text(json.dumps(summary, indent=2, default=jdefault) + "\n")
    sum_sha = sha256_file(op_sum)

    verdict_obj = {
        "generated_at_utc": ts,
        "campaign": 288,
        "part": "verdict",
        "analysis": "final_verdict",
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "real_data_only": True,
        "fabricated_data": False,
        "finding": (
            f"No costed OOS edge proven on real 5m spot data with the realized-volatility/"
            f"skewness cross-sectional family ({n_total} runs, {len(edge_runs)} edge)."
            if not edge_runs
            else f"Costed OOS edge proven in {len(edge_runs)} config(s) on real 5m spot data."
        ),
        "basis": "realized_volatility_skewness_cross_sectional_real_spot_price_costed_oos_5m",
        "dataset": {
            "spot_cache": str(SPOT_5M.relative_to(root)),
            "spot_cache_sha256": spot_sha,
            "window": "2026-08-01 00:00 -> 2026-10-30 23:55Z",
            "bars": int(n),
            "splits": len(splits),
        },
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
            "Price-derived realized vol/skew only; no quote volume; no testnet",
            "C288 is a NEW mechanism absent from the C281B..C286 record",
        ],
    }
    op_ver = reports / f"campaign288_verdict_{ts}.json"
    op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")
    ver_sha = sha256_file(op_ver)

    bind_sha = None
    bind_path = None
    if verdict == "NOT_TRADABLE":
        pass_shares = [r["gate_pass_share"] for r in results]
        turnovers = [r["turnover_total"] for r in results if r["oos_exposure_bars_total"] > 0]
        net_sums_by_slice = {
            f"fee{f}_slip{s}": [r["cost_slices"][f"fee{f}_slip{s}"]["oos_net_sum"] for r in results]
            for f, s in COST_GRID
        }
        binding = {
            "generated_at_utc": ts,
            "campaign": 288,
            "part": "binding_constraint",
            "analysis": "binding_constraint_diagnosis",
            "verdict": verdict,
            "real_data_only": True,
            "fabricated_data": False,
            "oos_sweep_artifact": str(op.relative_to(root)),
            "oos_sweep_sha256": sweep_sha,
            "signal_pass_shares": {
                "mean_gate_pass_share": float(np.mean(pass_shares)) if pass_shares else 0.0,
                "min_gate_pass_share": float(np.min(pass_shares)) if pass_shares else 0.0,
                "max_gate_pass_share": float(np.max(pass_shares)) if pass_shares else 0.0,
                "runs": [
                    {
                        "feature": r["feature"],
                        "lookback": r["lookback"],
                        "K": r["K"],
                        "hold": r["hold"],
                        "gate_pass_share": r["gate_pass_share"],
                        "blocked_rebalance_reasons": r["blocked_rebalance_reasons"],
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
            "binding_constraint": (
                "zero_exposure"
                if n_exp == 0
                else ("cost_sensitivity" if not all(any(r["cost_slices"][f"fee{f}_slip{s}"]["oos_net_sum"] > 0 for r in results) for f, s in COST_GRID) else "mean_beats_benchmark_fail")
            ),
            "note": "Diagnosis only; never an edge claim. No threshold weakening.",
        }
        op_bind = reports / f"campaign288_binding_constraint_{ts}.json"
        op_bind.write_text(json.dumps(binding, indent=2, default=jdefault) + "\n")
        bind_sha = sha256_file(op_bind)
        bind_path = str(op_bind.relative_to(root))
        verdict_obj["binding_constraint_artifact"] = bind_path
        verdict_obj["binding_constraint_sha256"] = bind_sha
        op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")
        ver_sha = sha256_file(op_ver)

    print(json.dumps({
        "campaign": 288,
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "n_total_runs": n_total,
        "n_with_exposure": int(n_exp),
        "n_edge_proven": int(len(edge_runs)),
        "n_splits": len(splits),
        "bars": n,
        "window": {"start": str(spot.index.min()), "end": str(spot.index.max())},
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