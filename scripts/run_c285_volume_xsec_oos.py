#!/usr/bin/env python3
"""C285 — costed out-of-sample edge test of volume-conditioned cross-sectional stat-arb.

Pre-registered protocol (no post-hoc parameter search):
- Dataset: real 1h spot close cache (verified SHA256-from-bytes) + real 1h
  quote-volume cache (Binance klines column 5, USDT; verified SHA256-from-bytes).
  Quote volume is an exogenous signal ONLY; PnL is measured on real spot prices.
- Universe: 11 spot assets ADA AVAX BNB BTC DOT ETH LINK LTC POL SOL XRP.
- C285 overlap: inner join of the 1h spot and volume indexes = 5112 bars,
  2026-04-01 00:00 -> 2026-10-30 23:00Z. The last 315 spot bars have no volume
  and are blocked, never imputed.
- Causal quote-volume signals (data through t-1 only at bar t):
  Feature A — z_logqv: (log_qv - rolling_mean(log_qv, L)) / rolling_std(log_qv, L),
    min_periods = max(20, L // 3); fail closed on zero/non-finite std.
  Feature B — qv_ratio: qv / rolling_median(qv, L); fail closed on non-positive
    or non-finite median.
  Feature C — qv_vol: rolling_std(log_qv.diff(), L); fail closed on non-finite values.
  Lookbacks L in {168, 336, 720} 1h bars.
- Cross-sectional portfolio at each rebalance bar: rank the 11 assets by the
  selected feature; long the top K and short the bottom K, K in {2, 3, 5};
  equal weight 0.5 / K per leg; gross exposure 1.0; dollar-neutral; per-asset cap 0.5.
  Holding period H in {1, 6, 24} 1h bars; hold between rebalances.
  weights.shift(1).fillna(0.0) is applied before PnL.
- Full pre-registered grid: 3 features x 3 lookbacks x 3 K x 3 holds = 81 runs.
  Every run is reported, including zero-exposure runs.
- Walk-forward: train=720, test=168, step=168 on the 5112-bar overlap -> 26 OOS splits.
- Cost grid exactly: [[0,0],[5,5],[10,10],[20,20],[40,40]] bps.
- Benchmark: equal-weight 11-asset buy-and-hold on the same OOS windows, no rebalance.
- Edge rule exactly: oos_edge_proven=true iff OOS exposure > 0 AND every cost slice
  has OOS net sum > 0 AND the mean of the per-split OOS net means is greater than
  the mean of the per-split equal-weight buy-and-hold OOS net means on the same WF
  windows (same per-split aggregation for both legs; never a strategy mean vs a
  benchmark sum). Anything else is NOT_TRADABLE; never relax this rule.

Fail-closed gates at each candidate rebalance bar:
- all 11 quote-volume observations finite and strictly positive;
- the selected signal finite for at least 2K assets;
- cross-sectional signal dispersion > 0;
- no NaN/non-finite price in any selected leg;
- no missing/None/false gate value treated as permissive.
If diagnostics cannot be computed, the rebalance is blocked and the reason recorded.

Required artifacts (exact names, timestamped):
- reports/campaign285_oos_sweep_<ts>.json
- reports/campaign285_tradable_edge_registry_<ts>.json
- reports/campaign285_summary_<ts>.json
- reports/campaign285_verdict_<ts>.json
Each includes real_data_only: true, fabricated_data: false, the spot/volume/meta/
provenance SHA256s, the split/cost config, all 81 run results, and SHA256-from-bytes
for the sweep/registry/summary. If NOT_TRADABLE, also emit
reports/campaign285_binding_constraint_<ts>.json with signal pass shares, exposure,
turnover, and the binding constraint (diagnosis only, never an edge claim).
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

SPOT_1H = cache_dir / "26736ab8fbb16974dd59f123855ab7e4810026d12712a05a363eabacd814ade2.pkl"
SPOT_1H_META = SPOT_1H.with_suffix(".meta.json")
SPOT_1H_SHA = "9355aed62b00a56b46ebba70eec4f9855620e8fea1b6eeae417ec6d7dea349df"
SPOT_1H_META_SHA = "95baf25daae1656a8c6f074acdcd909250565ddda8e86920b00d85163646afd1"

VOLUME = cache_dir / "volume_1h_full.pkl"
VOLUME_META = VOLUME.with_suffix(".meta.json")
VOLUME_PROVENANCE = VOLUME.with_suffix(".provenance.json")
VOLUME_SHA = "4365895387de4e542165fd331e39da40d455a3de24c7254eb67ba890053d193c"
VOLUME_META_SHA = "4d321584d3c687ad9956908c0179a1eae7d629c296c491e1e5ad1259a890c616"
VOLUME_PROVENANCE_SHA = "c7ff2f27ec5a668128e4856f809efde4922563dba87be0648be6d802c6d21c89"

FEATURES = ("z_logqv", "qv_ratio", "qv_vol")
LOOKBACKS = (168, 336, 720)
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


def load_volume(path: Path) -> dict:
    volume = pickle_load(path)
    if not isinstance(volume, dict):
        raise TypeError("volume cache is not a dict of symbol -> series")
    out = {}
    for symbol in SYMBOLS:
        series = volume.get(symbol)
        if series is None:
            raise KeyError(f"volume cache missing symbol {symbol}")
        out[symbol] = pd.Series(series).astype(float).sort_index()
    return out


def pickle_load(path: Path):
    import pickle

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
    return max(20, L // 3)


def signal_z_logqv(logqv: pd.DataFrame, L: int) -> pd.DataFrame:
    mp = min_periods_for(L)
    s = logqv.shift(1)  # signal at t uses data through t-1 only
    mean = s.rolling(L, min_periods=mp).mean()
    std = s.rolling(L, min_periods=mp).std()
    out = (s - mean) / std
    bad = (~np.isfinite(np.asarray(std))) | (np.asarray(std) <= 0)
    return out.mask(pd.DataFrame(bad, index=out.index, columns=out.columns))


def signal_qv_ratio(qv: pd.DataFrame, L: int) -> pd.DataFrame:
    mp = min_periods_for(L)
    s = qv.shift(1)  # signal at t uses data through t-1 only
    med = s.rolling(L, min_periods=mp).median()
    out = s / med
    bad = (~np.isfinite(np.asarray(med))) | (np.asarray(med) <= 0)
    return out.mask(pd.DataFrame(bad, index=out.index, columns=out.columns))


def signal_qv_vol(logqv: pd.DataFrame, L: int) -> pd.DataFrame:
    mp = min_periods_for(L)
    d = logqv.diff()
    s = d.shift(1)  # signal at t uses data through t-1 only
    std = s.rolling(L, min_periods=mp).std()
    bad = ~np.isfinite(np.asarray(std))
    return std.mask(pd.DataFrame(bad, index=std.index, columns=std.columns))


def SIGNAL(feature: str, logqv: pd.DataFrame, qv: pd.DataFrame, L: int) -> pd.DataFrame:
    if feature == "z_logqv":
        return signal_z_logqv(logqv, L)
    if feature == "qv_ratio":
        return signal_qv_ratio(qv, L)
    if feature == "qv_vol":
        return signal_qv_vol(logqv, L)
    raise ValueError(f"unknown feature {feature}")


def build_weights(
    signal_df: pd.DataFrame,
    price_df: pd.DataFrame,
    qv_df: pd.DataFrame,
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
        qv_now = qv_df.iloc[r]
        px_now = price_df.iloc[r]

        arr = sig.to_numpy(dtype=float)
        finite_mask = np.isfinite(arr)
        qv_arr = qv_now.to_numpy(dtype=float)
        px_arr = px_now.to_numpy(dtype=float)

        ok = True
        reason = None

        # Gate 1: all 11 quote-volume observations finite and strictly positive.
        if not (bool(np.isfinite(qv_arr).all()) and bool((qv_arr > 0).all())):
            ok = False
            reason = "qv_gate"

        # Gate 2: selected signal finite for at least 2K assets.
        if ok and int(finite_mask.sum()) < 2 * K:
            ok = False
            reason = "signal_coverage"

        # Gate 3: cross-sectional signal dispersion > 0.
        vals = None
        if ok:
            vals = arr[finite_mask]
            dispersion = float(vals.max() - vals.min()) if len(vals) else 0.0
            if not (np.isfinite(dispersion) and dispersion > 0.0):
                ok = False
                reason = "zero_dispersion"

        # Gate 4: no NaN/non-finite price in any selected leg.
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
            "turnover": turn,
            "bh_oos_mean": float(bh_mean),
        }
        if net_sum <= 0:
            all_sum_pos = False
        if net_mean <= bh_mean:
            all_mean_beats = False
    return slices, exposure_total, turnover_total, all_sum_pos, all_mean_beats, per_split_nets


def main() -> int:
    # ---- preflight: verify every cache SHA and the causal overlap ----
    if not SPOT_1H.exists():
        raise SystemExit(f"FATAL: C285 spot cache missing: {SPOT_1H}")
    if not SPOT_1H_META.exists():
        raise SystemExit(f"FATAL: C285 spot meta missing: {SPOT_1H_META}")
    if not VOLUME.exists():
        raise SystemExit(f"FATAL: C285 volume cache missing: {VOLUME}")
    if not VOLUME_META.exists():
        raise SystemExit(f"FATAL: C285 volume meta missing: {VOLUME_META}")
    if not VOLUME_PROVENANCE.exists():
        raise SystemExit(f"FATAL: C285 volume provenance missing: {VOLUME_PROVENANCE}")

    spot_sha = sha256_file(SPOT_1H)
    spot_meta_sha = sha256_file(SPOT_1H_META)
    volume_sha = sha256_file(VOLUME)
    volume_meta_sha = sha256_file(VOLUME_META)
    volume_prov_sha = sha256_file(VOLUME_PROVENANCE)
    if spot_sha != SPOT_1H_SHA:
        raise SystemExit(f"FATAL: spot cache sha256 mismatch: {spot_sha} != {SPOT_1H_SHA}")
    if spot_meta_sha != SPOT_1H_META_SHA:
        raise SystemExit(f"FATAL: spot meta sha256 mismatch: {spot_meta_sha} != {SPOT_1H_META_SHA}")
    if volume_sha != VOLUME_SHA:
        raise SystemExit(f"FATAL: volume cache sha256 mismatch: {volume_sha} != {VOLUME_SHA}")
    if volume_meta_sha != VOLUME_META_SHA:
        raise SystemExit(f"FATAL: volume meta sha256 mismatch: {volume_meta_sha} != {VOLUME_META_SHA}")
    if volume_prov_sha != VOLUME_PROVENANCE_SHA:
        raise SystemExit(f"FATAL: volume provenance sha256 mismatch: {volume_prov_sha} != {VOLUME_PROVENANCE_SHA}")

    spot_meta = json.loads(SPOT_1H_META.read_text())
    volume_meta = json.loads(VOLUME_META.read_text())
    volume_prov = json.loads(VOLUME_PROVENANCE.read_text())

    spot = load_spot(SPOT_1H)
    volume = load_volume(VOLUME)

    spot_index = pd.DatetimeIndex(spot.index)
    volume_index = pd.DatetimeIndex(pd.to_datetime(next(iter(volume.values())).index, utc=True))
    overlap = spot_index.intersection(volume_index)
    if len(overlap) != 5112:
        raise SystemExit(f"FATAL: C285 overlap is {len(overlap)} bars, expected 5112")

    spot_o = spot.loc[overlap].sort_index()
    qv_df = pd.DataFrame({s: volume[s].reindex(overlap) for s in SYMBOLS}, index=overlap)

    if int(spot_o.isna().sum().sum()) != 0:
        raise SystemExit("FATAL: NaN present in overlap spot cache; refusing to impute.")
    qv_arr_all = qv_df.to_numpy(dtype=float)
    if not (bool(np.isfinite(qv_arr_all).all()) and bool((qv_arr_all > 0).all())):
        raise SystemExit("FATAL: quote-volume cache has non-finite or non-positive values; refusing to proceed.")

    n = len(spot_o)
    splits = wf_splits(n, TRAIN, TEST, STEP)
    if len(splits) != 26:
        raise SystemExit(f"FATAL: expected 26 OOS splits, got {len(splits)}")

    returns_full = spot_o.pct_change().fillna(0.0)

    # Benchmark: equal-weight 11-asset buy-and-hold on the same OOS windows, no rebalance.
    bh_means = []
    for _, tr_e, te_e in splits:
        seg_ret = returns_full.iloc[tr_e:te_e]
        bh_means.append(float(seg_ret.mean(axis=1).mean()))
    bh_mean = float(np.mean(bh_means)) if bh_means else 0.0

    logqv = np.log(qv_df)

    limit_runs = int(os.environ.get("C285_LIMIT_RUNS", "0") or 0)
    results = []
    run_count = 0

    for feature in FEATURES:
        for L in LOOKBACKS:
            signal_df = SIGNAL(feature, logqv, qv_df, L)
            r_start = L  # full trailing lookback available; fully causal
            for K in K_VALUES:
                for H in HOLDS:
                    run_count += 1
                    if limit_runs > 0 and run_count > limit_runs:
                        break
                    weights, gate_stats = build_weights(
                        signal_df, spot_o, qv_df, K, H, r_start
                    )
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
        "campaign": 285,
        "part": "oos_sweep",
        "analysis": "volume_conditioned_cross_sectional_stat_arb_costed_oos",
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "real_data_only": True,
        "fabricated_data": False,
        "fail_closed": True,
        "mandate": (
            "C285 — pre-registered costed OOS sweep of volume-conditioned cross-sectional "
            "stat-arb on real Binance 1h spot + quote-volume caches; quote volume is a "
            "signal only, PnL is real spot price PnL; 11 assets; 3 features x 3 lookbacks "
            "x 3 K x 3 holds = 81 runs; train=720/test=168/step=168 = 26 OOS splits; "
            "cost grid [[0,0],[5,5],[10,10],[20,20],[40,40]] bps; fail-closed causal "
            "cross-sectional gates; edge rule: OOS exposure>0 AND all cost slices net "
            "sum>0 AND mean per-split OOS net mean > mean per-split equal-weight B&H "
            "OOS net mean on the same WF windows."
        ),
        "preflight": {
            "spot_cache": str(SPOT_1H.relative_to(root)),
            "spot_cache_sha256": spot_sha,
            "spot_meta_sha256": spot_meta_sha,
            "volume_cache": str(VOLUME.relative_to(root)),
            "volume_cache_sha256": volume_sha,
            "volume_meta_sha256": volume_meta_sha,
            "volume_provenance_sha256": volume_prov_sha,
            "spot_meta": spot_meta,
            "volume_meta": volume_meta,
            "volume_provenance": volume_prov,
            "overlap_bars": int(len(overlap)),
            "overlap_window": {"start": str(overlap.min()), "end": str(overlap.max())},
            "bars": int(n),
            "interval": "1h",
            "assets": list(SYMBOLS),
            "real_data_only": True,
            "fabricated_data": False,
            "sha256_from_bytes_verified": True,
        },
        "data_source": {
            "spot_cache": str(SPOT_1H.relative_to(root)),
            "spot_cache_sha256": spot_sha,
            "spot_meta_sha256": spot_meta_sha,
            "volume_cache": str(VOLUME.relative_to(root)),
            "volume_cache_sha256": volume_sha,
            "volume_meta_sha256": volume_meta_sha,
            "volume_provenance_sha256": volume_prov_sha,
            "bars": int(n),
            "interval": "1h",
            "assets": list(SYMBOLS),
            "window": {"start": str(spot_o.index.min()), "end": str(spot_o.index.max())},
        },
        "universe": {
            "n_assets": len(SYMBOLS),
            "assets": list(SYMBOLS),
            "overlap_bars": int(len(overlap)),
        },
        "config": {
            "walk_forward": {"train": TRAIN, "test": TEST, "step": STEP, "n_splits": len(splits)},
            "cost_grid_bps": COST_GRID,
            "signal_features": list(FEATURES),
            "lookbacks_1h": [int(l) for l in LOOKBACKS],
            "cross_sectional_K": [int(k) for k in K_VALUES],
            "holding_periods_1h": [int(h) for h in HOLDS],
            "total_runs": 3 * 3 * 3 * 3,
            "min_periods_rule": "max(20, L // 3)",
            "position_rule": "weights.shift(1).fillna(0.0)",
        },
        "gates": {
            "fail_closed": True,
            "requirements": [
                "all 11 quote-volume observations finite and strictly positive",
                "selected signal finite for at least 2K assets",
                "cross-sectional signal dispersion > 0",
                "no NaN/non-finite price in any selected leg",
                "no missing/None/false gate value treated as permissive",
            ],
        },
        "provenance": {
            "real_data_only": True,
            "fabricated_data": False,
            "quote_volume_signal_only": True,
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

    op = reports / f"campaign285_oos_sweep_{ts}.json"
    op.write_text(json.dumps(sweep, indent=2, default=jdefault) + "\n")
    sweep_sha = sha256_file(op)

    registry = {
        "generated_at_utc": ts,
        "campaign": 285,
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
    op_reg = reports / f"campaign285_tradable_edge_registry_{ts}.json"
    op_reg.write_text(json.dumps(registry, indent=2, default=jdefault) + "\n")
    reg_sha = sha256_file(op_reg)

    summary = {
        "generated_at_utc": ts,
        "campaign": 285,
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
            "If NOT_TRADABLE: emit binding_constraint artifact with signal pass shares, "
            "exposure, turnover, and binding constraint; record a formal negative result "
            "for the volume-conditioned cross-sectional family and stop; do not start a "
            "new parameter search in the same session. C286/C287 are the next campaigns."
        ),
    }
    op_sum = reports / f"campaign285_summary_{ts}.json"
    op_sum.write_text(json.dumps(summary, indent=2, default=jdefault) + "\n")
    sum_sha = sha256_file(op_sum)

    verdict_obj = {
        "generated_at_utc": ts,
        "campaign": 285,
        "part": "verdict",
        "analysis": "final_verdict",
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "real_data_only": True,
        "fabricated_data": False,
        "finding": (
            f"No costed OOS edge proven on real spot data with quote-volume signals "
            f"({n_total} runs, {len(edge_runs)} edge)."
            if not edge_runs
            else f"Costed OOS edge proven in {len(edge_runs)} config(s) on real spot data with quote-volume signals."
        ),
        "basis": "quote_volume_signal_real_spot_price_costed_oos_cross_sectional",
        "dataset": {
            "spot_cache": str(SPOT_1H.relative_to(root)),
            "spot_cache_sha256": spot_sha,
            "volume_cache": str(VOLUME.relative_to(root)),
            "volume_cache_sha256": volume_sha,
            "overlap_window": "2026-04-01 00:00 -> 2026-10-30 23:00Z",
            "overlap_bars": int(len(overlap)),
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
            "Quote volume is a signal only; PnL is real spot price PnL",
        ],
    }
    op_ver = reports / f"campaign285_verdict_{ts}.json"
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
            "campaign": 285,
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
        op_bind = reports / f"campaign285_binding_constraint_{ts}.json"
        op_bind.write_text(json.dumps(binding, indent=2, default=jdefault) + "\n")
        bind_sha = sha256_file(op_bind)
        bind_path = str(op_bind.relative_to(root))
        verdict_obj["binding_constraint_artifact"] = bind_path
        verdict_obj["binding_constraint_sha256"] = bind_sha
        op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")
        ver_sha = sha256_file(op_ver)

    print(json.dumps({
        "campaign": 285,
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "n_total_runs": n_total,
        "n_with_exposure": int(n_exp),
        "n_edge_proven": int(len(edge_runs)),
        "n_splits": len(splits),
        "bars": n,
        "window": {"start": str(spot_o.index.min()), "end": str(spot_o.index.max())},
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
