#!/usr/bin/env python3
"""C297 — costed out-of-sample edge test of a NEW economic regime: DAILY-horizon
multi-year cross-sectional statistical arbitrage on real mainnet public spot
OHLCV.

The entire C281B..C296 record tested cross-sectional stat-arb at 5m / 1h horizons
over a single ~3-month window (2026-08 .. 2026-10).  C297 tests the SAME
cross-sectional mechanism at a **daily horizon over a multi-year window**
(2021-01-01 .. 2026-11-13) spanning multiple market regimes (2021 bull, 2022
bear, 2023-2024 recovery, 2025-2026).  Daily horizon => far lower turnover and a
different cost-sensitivity regime, so this is NOT a relabeling of a closed
5m/1h family; it is a genuinely different economic test.

- Real daily features (causal, shift(1)):
    mom            = close_t / close_{t-L} - 1                        [trailing return]
    vol_scaled_mom = mom / rolling_std(L of log-return)               [risk-adj. momentum]
    resid_mom      = mom - beta_L * market_mom_L                       [residual momentum]
    low_vol        = -rolling_std(L of log-return)                     [low-vol tilt]
    reversal       = -(close_t / close_{t-k} - 1), k=max(2,L//6)      [short-term reversal]

Pre-registered protocol (no post-hoc parameter search):
- Dataset: real mainnet public Binance spot 1d OHLCV cache
  (data/cache/campaign297_daily_ohlcv.pkl, SHA256-from-bytes verified).
- Cross-sectional portfolio at each daily rebalance bar: rank assets by the
  selected score; long top K, short bottom K, K in {3,5,8}; equal weight 0.5/K
  per leg; gross 1.0; dollar-neutral; per-asset cap 0.5. Holding period H in
  {1,5,20} days; hold between rebalances. weights.shift(1).fillna(0.0) before PnL.
- Full pre-registered grid: 5 features x 3 lookbacks x 3 K x 3 holds = 135 runs.
  Every run is reported, including zero-exposure runs.
- Walk-forward: train=504, test=126, step=126 in DAILY bars.
- Cost grid exactly: [[0,0],[5,5],[10,10],[20,20],[40,40]] bps.
- Benchmark: equal-weight buy-and-hold on the same OOS windows, no rebalance.
- Edge rule exactly (identical to C285/C286/C288/C290/C291/C292/C293/C294/C295,
  never relaxed): oos_edge_proven=true iff OOS exposure > 0 AND every cost slice
  has OOS net sum > 0 AND the mean of the per-split OOS net means is greater than
  the mean of the per-split equal-weight B&H OOS net means on the same WF windows.
  Anything else is NOT_TRADABLE.

Fail-closed gates at each candidate daily rebalance bar:
- the selected feature score finite for at least 2K assets;
- cross-sectional score dispersion > 0;
- no NaN/non-finite daily price in any selected leg;
- no missing/None/false gate value treated as permissive.
If diagnostics cannot be computed, the rebalance is blocked and the reason recorded.

Required artifacts (exact names, timestamped, SHA256-from-bytes):
- reports/campaign297_oos_sweep_<ts>.json
- reports/campaign297_tradable_edge_registry_<ts>.json
- reports/campaign297_summary_<ts>.json
- reports/campaign297_verdict_<ts>.json
- reports/campaign297_binding_constraint_<ts>.json  (if NOT_TRADABLE)
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

OHLCV = cache_dir / "campaign297_daily_ohlcv.pkl"
OHLCV_META = cache_dir / "campaign297_daily_ohlcv.meta.json"
OHLCV_PROV = cache_dir / "campaign297_daily_ohlcv.provenance.json"

FEATURES = ("mom", "vol_scaled_mom", "resid_mom", "low_vol", "reversal")
LOOKBACKS = (20, 60, 120)
K_VALUES = (3, 5, 8)
HOLDS = (1, 5, 20)

TRAIN, TEST, STEP = 504, 126, 126
COST_GRID = [[0, 0], [5, 5], [10, 10], [20, 20], [40, 40]]

# Total runs: 5 features x 3 lookbacks x 3 K x 3 holds = 135


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
    return max(20, L // 3)


def _mask_nonfinite(out: pd.DataFrame) -> pd.DataFrame:
    arr = out.to_numpy(dtype=float)
    bad = ~np.isfinite(arr)
    return out.mask(pd.DataFrame(bad, index=out.index, columns=out.columns))


def build_features(closes: pd.DataFrame) -> dict:
    logret = np.log(closes).diff()
    mkt_ret = logret.mean(axis=1)
    return {"closes": closes, "logret": logret, "mkt_ret": mkt_ret}


def _mom(closes: pd.DataFrame, L: int) -> pd.DataFrame:
    return closes / closes.shift(L) - 1.0


def _vol(logret: pd.DataFrame, L: int) -> pd.DataFrame:
    mp = min_periods_for(L)
    std = logret.rolling(L, min_periods=mp).std()
    return _mask_nonfinite(std)


def _reversal(closes: pd.DataFrame, L: int) -> pd.DataFrame:
    k = max(2, L // 6)
    return closes / closes.shift(k) - 1.0


def _resid_mom(closes: pd.DataFrame, logret: pd.DataFrame, mkt_ret: pd.Series, L: int) -> pd.DataFrame:
    mp = min_periods_for(L)
    asset_mom = _mom(closes, L)
    mkt_mom = np.exp(mkt_ret.rolling(L, min_periods=mp).sum()) - 1.0
    mean_a = logret.rolling(L, min_periods=mp).mean()
    mean_m = mkt_ret.rolling(L, min_periods=mp).mean()
    mean_am = logret.mul(mkt_ret, axis=0).rolling(L, min_periods=mp).mean()
    mean_mm = (mkt_ret * mkt_ret).rolling(L, min_periods=mp).mean()
    cov_am = mean_am.sub(mean_a.mul(mean_m, axis=0))
    var_m = mean_mm.sub(mean_m * mean_m)
    var_ok = var_m > 0
    beta = cov_am.div(var_m.where(var_ok), axis=0)
    resid = asset_mom.sub(beta.mul(mkt_mom, axis=0))
    return _mask_nonfinite(resid)


def SIGNAL(feature: str, feats: dict, L: int) -> pd.DataFrame:
    """Return a causal daily score DataFrame (higher score = long leg)."""
    closes = feats["closes"]
    logret = feats["logret"]
    mkt_ret = feats["mkt_ret"]
    if feature == "mom":
        raw = _mom(closes, L)
    elif feature == "vol_scaled_mom":
        raw = _mom(closes, L) / _vol(logret, L)
    elif feature == "resid_mom":
        raw = _resid_mom(closes, logret, mkt_ret, L)
    elif feature == "low_vol":
        raw = -_vol(logret, L)
    elif feature == "reversal":
        raw = -_reversal(closes, L)
    else:
        raise ValueError(f"unknown feature {feature}")
    # causal: use data through t-1 only
    return raw.shift(1).fillna(np.nan)


def build_weights(
    signal_df: pd.DataFrame,
    price_df: pd.DataFrame,
    K: int,
    H: int,
    r_start: int,
):
    n = len(signal_df)
    sig = signal_df.to_numpy(dtype=float)
    px = price_df.to_numpy(dtype=float)
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
            if not bool(np.isfinite(px[r][leg_idx]).all()):
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
    if not OHLCV.exists():
        raise SystemExit(f"FATAL: C297 OHLCV cache missing: {OHLCV}")
    if not OHLCV_META.exists():
        raise SystemExit(f"FATAL: C297 meta missing: {OHLCV_META}")

    ohlcv_sha = sha256_file(OHLCV)
    meta_sha = sha256_file(OHLCV_META)
    meta = json.loads(OHLCV_META.read_text())
    if ohlcv_sha != meta.get("sha256_from_bytes"):
        raise SystemExit(f"FATAL: ohlcv sha256 mismatch: {ohlcv_sha} != {meta.get('sha256_from_bytes')}")
    if meta.get("real_data_only") is not True or meta.get("fabricated_data") is not False:
        raise SystemExit("FATAL: dataset provenance flags are not real_data_only/fabricated_data")

    payload = load_payload(OHLCV)
    symbols = list(payload["symbols"])
    closes = payload["closes"].astype(float).sort_index()

    if int(closes.isna().sum().sum()) != 0:
        raise SystemExit("FATAL: NaN present in closes; refusing to impute.")
    if not bool(np.isfinite(closes.to_numpy(dtype=float)).all()):
        raise SystemExit("FATAL: non-finite value present in closes; refusing to proceed.")
    if not bool((closes.to_numpy(dtype=float) > 0).all()):
        raise SystemExit("FATAL: non-positive price in closes; refusing to proceed.")

    n = len(closes)
    splits = wf_splits(n, TRAIN, TEST, STEP)
    if len(splits) < 4:
        raise SystemExit(f"FATAL: expected >=4 OOS splits, got {len(splits)}")

    returns_full = closes.pct_change().fillna(0.0)
    feats = build_features(closes)

    # Benchmark: equal-weight buy-and-hold on the same OOS windows, no rebalance.
    bh_means = []
    for _, tr_e, te_e in splits:
        seg_ret = returns_full.iloc[tr_e:te_e]
        bh_means.append(float(seg_ret.mean(axis=1).mean()))
    bh_mean = float(np.mean(bh_means)) if bh_means else 0.0

    limit_runs = int(os.environ.get("C297_LIMIT_RUNS", "0") or 0)
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
                    weights, gate_stats = build_weights(signal, closes, K, H, r_start=0)
                    pos = weights.shift(1).fillna(0.0)
                    slices, exposure_total, turnover_total, all_sum_pos, all_mean_beats, _ = costed_oos(
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
    total_runs = len(FEATURES) * len(LOOKBACKS) * len(K_VALUES) * len(HOLDS)

    dataset_block = {
        "ohlcv_cache": str(OHLCV.relative_to(root)),
        "ohlcv_cache_sha256": ohlcv_sha,
        "meta": str(OHLCV_META.relative_to(root)),
        "meta_sha256": meta_sha,
        "provenance": str(OHLCV_PROV.relative_to(root)) if OHLCV_PROV.exists() else None,
        "bars": int(n),
        "interval": "1d",
        "horizon": "daily_multi_year",
        "assets": symbols,
        "window": {"start": str(closes.index.min()), "end": str(closes.index.max())},
        "real_data_only": True,
        "fabricated_data": False,
    }

    sweep = {
        "generated_at_utc": ts,
        "campaign": 297,
        "part": "oos_sweep",
        "analysis": "daily_multi_year_ohlcv_cross_sectional_stat_arb_costed_oos",
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "real_data_only": True,
        "fabricated_data": False,
        "fail_closed": True,
        "mandate": (
            "C297 — pre-registered costed OOS sweep of a NEW economic regime: DAILY-horizon "
            "multi-year cross-sectional statistical arbitrage on real mainnet public spot OHLCV; "
            "multi-year 1d window (2021-01-01 .. 2026-11-13) spanning multiple market regimes; "
            "5 daily features x 3 lookbacks x 3 K x 3 holds = 135 runs; train=504/test=126/step=126 "
            "in daily bars; cost grid [[0,0],[5,5],[10,10],[20,20],[40,40]] bps; fail-closed causal "
            "cross-sectional gates; edge rule: OOS exposure>0 AND all cost slices net sum>0 AND mean "
            "per-split OOS net mean > mean per-split equal-weight B&H OOS net mean on the same WF windows."
        ),
        "preflight": dataset_block,
        "data_source": dataset_block,
        "universe": {"n_assets": len(symbols), "assets": symbols},
        "config": {
            "walk_forward": {"train": TRAIN, "test": TEST, "step": STEP, "n_splits": len(splits)},
            "cost_grid_bps": COST_GRID,
            "signal_features": list(FEATURES),
            "lookbacks_daily": [int(l) for l in LOOKBACKS],
            "cross_sectional_K": [int(k) for k in K_VALUES],
            "holding_periods_daily": [int(h) for h in HOLDS],
            "total_runs": total_runs,
            "min_periods_rule": "max(20, L // 3)",
            "position_rule": "weights.shift(1).fillna(0.0)",
            "score_definition": {
                "mom": "close_t/close_{t-L}-1",
                "vol_scaled_mom": "mom / rolling_std(L of log-return)",
                "resid_mom": "mom - beta_L * market_mom_L",
                "low_vol": "-rolling_std(L of log-return)",
                "reversal": "-(close_t/close_{t-max(2,L//6)}-1)",
            },
            "signal_direction": "long top-K, short bottom-K by score (higher score = long)",
        },
        "gates": {
            "fail_closed": True,
            "requirements": [
                "selected feature score finite for at least 2K assets",
                "cross-sectional score dispersion > 0",
                "no NaN/non-finite daily price in any selected leg",
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
            "daily_multi_year_window": True,
            "distinct_from_5m_1h_closure": True,
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

    op = reports / f"campaign297_oos_sweep_{ts}.json"
    op.write_text(json.dumps(sweep, indent=2, default=jdefault) + "\n")
    sweep_sha = sha256_file(op)

    registry = {
        "generated_at_utc": ts,
        "campaign": 297,
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
    op_reg = reports / f"campaign297_tradable_edge_registry_{ts}.json"
    op_reg.write_text(json.dumps(registry, indent=2, default=jdefault) + "\n")
    reg_sha = sha256_file(op_reg)

    summary = {
        "generated_at_utc": ts,
        "campaign": 297,
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
            "If NOT_TRADABLE: emit binding_constraint artifact (pass shares, exposure, turnover, "
            "binding constraint); record a formal daily multi-year negative result. If EDGE_PROVEN: "
            "escalate to external execution (C287 testnet gateway), which requires valid testnet "
            "credentials + non-451 egress."
        ),
    }
    op_sum = reports / f"campaign297_summary_{ts}.json"
    op_sum.write_text(json.dumps(summary, indent=2, default=jdefault) + "\n")
    sum_sha = sha256_file(op_sum)

    verdict_obj = {
        "generated_at_utc": ts,
        "campaign": 297,
        "part": "verdict",
        "analysis": "final_verdict",
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "real_data_only": True,
        "fabricated_data": False,
        "finding": (
            f"No costed OOS edge proven on the daily multi-year cross-sectional family "
            f"({n_total} runs, {len(edge_runs)} edge)."
            if not edge_runs
            else f"Costed OOS edge proven in {len(edge_runs)} config(s) on daily multi-year data."
        ),
        "basis": "daily_multi_year_ohlcv_cross_sectional_stat_arb_real_spot_costed_oos",
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
            "Real mainnet public Binance spot 1d OHLCV only; no testnet",
            "C297 is a NEW daily multi-year regime absent from the C281B..C296 5m/1h record",
        ],
    }
    op_ver = reports / f"campaign297_verdict_{ts}.json"
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
            "campaign": 297,
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
                else (
                    "cost_sensitivity"
                    if not all(
                        any(r["cost_slices"][f"fee{f}_slip{s}"]["oos_net_sum"] > 0 for r in results)
                        for f, s in COST_GRID
                    )
                    else "mean_beats_benchmark_fail"
                )
            ),
            "note": "Diagnosis only; never an edge claim. No threshold weakening.",
        }
        op_bind = reports / f"campaign297_binding_constraint_{ts}.json"
        op_bind.write_text(json.dumps(binding, indent=2, default=jdefault) + "\n")
        bind_sha = sha256_file(op_bind)
        bind_path = str(op_bind.relative_to(root))
        verdict_obj["binding_constraint_artifact"] = bind_path
        verdict_obj["binding_constraint_sha256"] = bind_sha
        op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")
        ver_sha = sha256_file(op_ver)

    print(json.dumps({
        "campaign": 297,
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "n_total_runs": n_total,
        "n_with_exposure": int(n_exp),
        "n_edge_proven": int(len(edge_runs)),
        "n_splits": len(splits),
        "bars": n,
        "n_assets": len(symbols),
        "window": {"start": str(closes.index.min()), "end": str(closes.index.max())},
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