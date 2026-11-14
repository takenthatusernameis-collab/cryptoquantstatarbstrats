#!/usr/bin/env python3
"""C298 — costed out-of-sample edge test of the multi-year (2020-01 .. 2026-10)
USDT-M perpetual-futures funding-carry + spot/perp basis cross-sectional
stat-arb family — the deep intraday depth extension of C291/C293.

- DATA: real USDT-M perpetual futures 1h klines (resampled from real 5m
  archives) + real 8h/4h funding rates + real spot 1h closes
  (data/cache/campaign298_multianual_perp_funding_basis.pkl, SHA256-from-bytes
  verified).  PnL is real perp PnL plus real funding cashflows; spot leg used
  only for the basis feature.
- MECHANISM: funding carry + spot/perp basis cross-sectional stat-arb:
    funding_level = last funding rate known at t-1 (ffill)          [carry]
    funding_z     = trailing z-score of funding over L 1h bars       [carry z]
    basis_ma      = rolling mean of (perp-spot)/spot over L 1h bars   [basis]
    basis_z       = rolling z-score of basis over L 1h bars          [basis z]
    perp_mom      = rolling mean of perp 1h log-returns over L       [momentum]
    perp_lowvol   = rolling std of perp 1h log-returns over L        [low vol]
  Scores: -funding_level, -funding_z, -basis_ma, -basis_z, +perp_mom,
  -perp_lowvol (higher score = long leg).  All causal (shift(1)), true 1h.

Pre-registered protocol (no post-hoc parameter search):
- Dataset: real USDT-M perp 1h klines + real funding cashflows + real spot 1h
  (data/cache/campaign298_multianual_perp_funding_basis.pkl).
- Cross-sectional portfolio at each 1h rebalance bar: rank the selected perps by
  the selected score; long top K and short bottom K, K in {2,3,5}; equal weight
  0.5/K per leg; gross 1.0; dollar-neutral; per-asset cap 0.5.  Holding period H
  in {1,6,24} 1h bars.  weights.shift(1).fillna(0.0) before PnL.
- Funding cashflow: at every native funding boundary, funding_pnl =
  -funding_rate * signed_weight (long pays when rate>0, short receives), using
  only funding known at/before the boundary (causal).
- Full pre-registered grid: 6 features x 3 lookbacks x 3 K x 3 holds = 162 runs.
- Walk-forward: train=2160, test=720, step=720 in 1h bars over 2020-01..2026-10.
- Cost grid exactly: [[0,0],[5,5],[10,10],[20,20],[40,40]] bps.
- Benchmark: equal-weight buy-and-hold of the same universe on the same OOS
  windows, with the SAME funding cashflows, no rebalance.
- Edge rule exactly (identical to C285/C286/C288/C290/C291/C292/C293/C294/C295/C297,
  never relaxed):
  oos_edge_proven=true iff OOS exposure > 0 AND every cost slice has OOS net sum > 0
  AND the mean of the per-split OOS net means is greater than the mean of the
  per-split equal-weight B&H OOS net means on the same WF windows.

Fail-closed gates at each candidate 1h rebalance bar:
- the selected feature score finite for at least 2K assets;
- cross-sectional score dispersion > 0;
- no NaN/non-finite 1h price in any selected leg (perp or spot);
- funding staleness <= 24h + 1 bar in every selected leg;
- no missing/None/false gate value treated as permissive.

Required artifacts (exact names, timestamped, SHA256-from-bytes):
- reports/campaign298_oos_sweep_<ts>.json
- reports/campaign298_tradable_edge_registry_<ts>.json
- reports/campaign298_summary_<ts>.json
- reports/campaign298_verdict_<ts>.json
- reports/campaign298_binding_constraint_<ts>.json  (if NOT_TRADABLE)
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

CACHE = cache_dir / "campaign298_multianual_perp_funding_basis.pkl"
CACHE_META = cache_dir / "campaign298_multianual_perp_funding_basis.meta.json"
CACHE_PROV = cache_dir / "campaign298_multianual_perp_funding_basis.provenance.json"

FEATURES = ("funding_level", "funding_z", "basis_ma", "basis_z", "perp_mom", "perp_lowvol")
LOOKBACKS = (168, 720, 2160)
K_VALUES = (2, 3, 5)
HOLDS = (1, 6, 24)

TRAIN, TEST, STEP = 2160, 720, 720
COST_GRID = [[0, 0], [5, 5], [10, 10], [20, 20], [40, 40]]
STALE_BARS = 24 + 1  # 24h + 1 bar on the 1h grid

# 6 features x 3 lookbacks x 3 K x 3 holds = 162 runs


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


def _safe_std(out: pd.DataFrame, std: pd.DataFrame) -> pd.DataFrame:
    bad = (~np.isfinite(np.asarray(std))) | (np.asarray(std) <= 0)
    return out.mask(pd.DataFrame(bad, index=out.index, columns=out.columns))


def _mask_nonfinite(out: pd.DataFrame) -> pd.DataFrame:
    return out.mask(pd.DataFrame(~np.isfinite(np.asarray(out)), index=out.index, columns=out.columns))


def build_features(perp_closes, spot_closes, funding_rates):
    """All inputs are wide DataFrames aligned on the same 1h index.

    Returns a dict of base inputs; each SIGNAL() applies its own causal shift(1).
    """
    logret = np.log(perp_closes).diff()
    basis = (perp_closes - spot_closes) / spot_closes
    funding_ffill = funding_rates.ffill()  # 8h/4h forward-fill of the funding rate
    return {"logret": logret, "basis": basis, "funding_ffill": funding_ffill}


def funding_level(feats: dict, L: int) -> pd.DataFrame:
    """Last funding rate known at t-1 (8h/4h forward-filled), causal."""
    s = feats["funding_ffill"].shift(1)
    return _mask_nonfinite(s)


def funding_z(feats: dict, L: int) -> pd.DataFrame:
    """Trailing z-score of the forward-filled funding level over L 1h bars, causal."""
    mp = min_periods_for(L)
    s = feats["funding_ffill"].shift(1)
    mean = s.rolling(L, min_periods=mp).mean()
    std = s.rolling(L, min_periods=mp).std()
    z = (s - mean) / std
    return _safe_std(z, std)


def basis_ma(feats: dict, L: int) -> pd.DataFrame:
    """Rolling mean of (perp-spot)/spot over L 1h bars, causal."""
    mp = min_periods_for(L)
    s = feats["basis"].shift(1)
    out = s.rolling(L, min_periods=mp).mean()
    return _mask_nonfinite(out)


def basis_z(feats: dict, L: int) -> pd.DataFrame:
    """Rolling z-score of basis over L 1h bars, causal."""
    mp = min_periods_for(L)
    s = feats["basis"].shift(1)
    mean = s.rolling(L, min_periods=mp).mean()
    std = s.rolling(L, min_periods=mp).std()
    z = (s - mean) / std
    return _safe_std(z, std)


def perp_mom(feats: dict, L: int) -> pd.DataFrame:
    """Rolling mean of perp 1h log-returns over L, causal."""
    mp = min_periods_for(L)
    s = feats["logret"].shift(1)
    out = s.rolling(L, min_periods=mp).mean()
    return _mask_nonfinite(out)


def perp_lowvol(feats: dict, L: int) -> pd.DataFrame:
    """Rolling std of perp 1h log-returns over L, causal."""
    mp = min_periods_for(L)
    s = feats["logret"].shift(1)
    std = s.rolling(L, min_periods=mp).std()
    return _mask_nonfinite(std)


def SIGNAL(feature: str, feats: dict, L: int) -> pd.DataFrame:
    """Return a causal score DataFrame (higher score = long leg)."""
    if feature == "funding_level":
        return -funding_level(feats, L)
    if feature == "funding_z":
        return -funding_z(feats, L)
    if feature == "basis_ma":
        return -basis_ma(feats, L)
    if feature == "basis_z":
        return -basis_z(feats, L)
    if feature == "perp_mom":
        return perp_mom(feats, L)
    if feature == "perp_lowvol":
        return -perp_lowvol(feats, L)
    raise ValueError(f"unknown feature {feature}")


def compute_funding_age(funding_rates: pd.DataFrame) -> pd.DataFrame:
    """Bars since the last known funding boundary, per symbol (NaN before first)."""
    n = len(funding_rates)
    idx = pd.Series(np.arange(n, dtype=float), index=funding_rates.index)
    out = {}
    for s in funding_rates.columns:
        m = funding_rates[s].notna().values
        pos_series = pd.Series(np.where(m, np.arange(n, dtype=float), np.nan), index=funding_rates.index)
        last = pos_series.ffill()
        out[s] = idx - last
    return pd.DataFrame(out, index=funding_rates.index)


def build_weights(
    signal_df: pd.DataFrame,
    price_df: pd.DataFrame,
    K: int,
    H: int,
    r_start: int,
    funding_age: pd.DataFrame | None = None,
):
    n = len(signal_df)
    sig = signal_df.to_numpy(dtype=float)
    px = price_df.to_numpy(dtype=float)
    age = funding_age.to_numpy(dtype=float) if funding_age is not None else None
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
        if ok and age is not None:
            leg_idx = np.concatenate([long_idx, short_idx])
            leg_age = age[r][leg_idx]
            if not bool(np.all(np.isfinite(leg_age) & (leg_age <= STALE_BARS))):
                ok = False
                reason = "funding_stale"
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

    port_ret already includes real perp price PnL + real funding cashflows.
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
        tc = (fee + slip) / 10000.0
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
        }
        if net_sum <= 0:
            all_sum_pos = False
        if net_mean <= bh_mean:
            all_mean_beats = False
    return slices, exposure_total, turnover_total, all_sum_pos, all_mean_beats


def main() -> int:
    if not CACHE.exists():
        raise SystemExit(f"FATAL: C298 cache missing: {CACHE}")
    if not CACHE_META.exists():
        raise SystemExit(f"FATAL: C298 meta missing: {CACHE_META}")

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
    closes = payload["closes"].astype(float).sort_index()
    funding_rates = payload["funding_rates"].astype(float).reindex(closes.index)
    spot_closes = payload["spot_closes"].astype(float).reindex(closes.index)[symbols]

    missing_spot = [s for s in symbols if s not in spot_closes.columns]
    if missing_spot:
        raise SystemExit(f"FATAL: spot leg missing symbols: {missing_spot}")

    if int(closes.isna().sum().sum()) != 0:
        raise SystemExit("FATAL: NaN present in perp closes; refusing to impute.")
    if not bool(np.isfinite(closes.to_numpy(dtype=float)).all()):
        raise SystemExit("FATAL: non-finite value present in perp closes.")
    if not bool((closes.to_numpy(dtype=float) > 0).all()):
        raise SystemExit("FATAL: non-positive perp price; refusing to proceed.")
    # spot gaps (data-api missing hours) are NOT imputed: they stay NaN in the
    # spot leg, which makes basis-based scores NaN at those bars and the
    # fail-closed gates block any trade requiring missing spot data.  Price PnL
    # uses perp returns only and is unaffected.
    spot_nan = int(spot_closes.isna().sum().sum())

    n = len(closes)
    splits = wf_splits(n, TRAIN, TEST, STEP)
    if len(splits) == 0:
        raise SystemExit(f"FATAL: no OOS splits for n={n}, train={TRAIN}, test={TEST}, step={STEP}")

    perp_returns = closes.pct_change().fillna(0.0)
    # funding cashflow leg: -rate at every native funding boundary, 0 elsewhere
    funding_leg = -funding_rates.fillna(0.0)
    # total per-bar asset return including funding = price return + funding leg
    total_asset_ret = perp_returns + funding_leg
    funding_age = compute_funding_age(funding_rates)

    feats = build_features(closes, spot_closes, funding_rates)

    # Benchmark: equal-weight buy-and-hold of the same universe on the same OOS
    # windows, WITH the same funding cashflows, no rebalance.  weight 1/N per asset.
    bh_means = []
    for _, tr_e, te_e in splits:
        seg = total_asset_ret.iloc[tr_e:te_e]
        bh_means.append(float(seg.mean(axis=1).mean()))
    bh_mean = float(np.mean(bh_means)) if bh_means else 0.0

    limit_runs = int(os.environ.get("C298_LIMIT_RUNS", "0") or 0)
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
                    weights, gate_stats = build_weights(signal, closes, K, H, r_start=0, funding_age=funding_age)
                    pos = weights.shift(1).fillna(0.0)
                    port_ret = (pos * total_asset_ret).sum(axis=1)
                    slices, exposure_total, turnover_total, all_sum_pos, all_mean_beats = costed_oos(
                        port_ret, pos, splits, COST_GRID, bh_mean
                    )
                    edge = bool(exposure_total > 0 and all_sum_pos and all_mean_beats)
                    price_pnl = float((pos * perp_returns).sum(axis=1).sum())
                    fund_pnl = float((pos * funding_leg).sum(axis=1).sum())
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
                        "price_pnl_sum": price_pnl,
                        "funding_pnl_sum": fund_pnl,
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
        "cache": str(CACHE.relative_to(root)),
        "cache_sha256": cache_sha,
        "cache_meta": str(CACHE_META.relative_to(root)),
        "cache_meta_sha256": meta_sha,
        "cache_provenance": str(CACHE_PROV.relative_to(root)) if CACHE_PROV.exists() else None,
        "cache_provenance_sha256": prov_sha,
        "bars": int(n),
        "interval": "1h",
        "assets": symbols,
        "n_assets": len(symbols),
        "window": {"start": str(closes.index.min()), "end": str(closes.index.max())},
        "funding_total_rows": int(funding_rates.notna().sum().sum()),
        "funding_intervals_by_symbol": meta.get("funding_intervals_by_symbol"),
        "real_data_only": True,
        "fabricated_data": False,
    }

    sweep = {
        "generated_at_utc": ts,
        "campaign": 298,
        "part": "oos_sweep",
        "analysis": "real_perp_funding_carry_basis_cross_sectional_stat_arb_costed_oos",
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "real_data_only": True,
        "fabricated_data": False,
        "fail_closed": True,
        "mandate": (
            "C298 — pre-registered costed OOS sweep of the multi-year "
            "USDT-M perpetual-futures funding-carry + spot/perp basis "
            "cross-sectional stat-arb family (2020-01 .. 2026-10, 1h); "
            "6 features x 3 lookbacks x 3 K x 3 holds = 162 runs; train=2160/"
            "test=720/step=720 = n OOS splits; cost grid [[0,0],[5,5],[10,10],"
            "[20,20],[40,40]] bps; real funding cashflow -rate*signed_weight at "
            "each native funding boundary; fail-closed causal cross-sectional "
            "gates; edge rule identical to C285/C286/C288/C290/C291/C292/C293/"
            "C294/C295/C297."
        ),
        "preflight": dataset_block,
        "data_source": dataset_block,
        "universe": {"n_assets": len(symbols), "assets": symbols},
        "config": {
            "walk_forward": {"train": TRAIN, "test": TEST, "step": STEP, "n_splits": len(splits)},
            "cost_grid_bps": COST_GRID,
            "signal_features": list(FEATURES),
            "lookbacks_1h": [int(l) for l in LOOKBACKS],
            "cross_sectional_K": [int(k) for k in K_VALUES],
            "holding_periods_1h": [int(h) for h in HOLDS],
            "total_runs": 6 * 3 * 3 * 3,
            "min_periods_rule": "max(20, L // 3)",
            "position_rule": "weights.shift(1).fillna(0.0)",
            "funding_rule": "funding_pnl = -funding_rate * signed_weight at each native funding boundary (causal)",
            "score_definition": {
                "funding_level": "-funding_rate_ffill_known_at_t-1",
                "funding_z": "-z(funding_rate_ffill, L 1h bars)",
                "basis_ma": "-mean((perp-spot)/spot, L 1h bars)",
                "basis_z": "-z((perp-spot)/spot, L 1h bars)",
                "perp_mom": "+mean(perp 1h log-return, L)",
                "perp_lowvol": "-std(perp 1h log-return, L)",
            },
            "signal_direction": "long top-K, short bottom-K by score (higher score = long)",
        },
        "gates": {
            "fail_closed": True,
            "requirements": [
                "selected feature score finite for at least 2K assets",
                "cross-sectional score dispersion > 0",
                "no NaN/non-finite 1h price in any selected leg",
                "funding staleness <= 24h + 1 bar in every selected leg",
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

    op = reports / f"campaign298_oos_sweep_{ts}.json"
    op.write_text(json.dumps(sweep, indent=2, default=jdefault) + "\n")
    sweep_sha = sha256_file(op)

    registry = {
        "generated_at_utc": ts,
        "campaign": 298,
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
    op_reg = reports / f"campaign298_tradable_edge_registry_{ts}.json"
    op_reg.write_text(json.dumps(registry, indent=2, default=jdefault) + "\n")
    reg_sha = sha256_file(op_reg)

    summary = {
        "generated_at_utc": ts,
        "campaign": 298,
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
            "multi-year USDT-M perp funding-carry/basis space."
        ),
    }
    op_sum = reports / f"campaign298_summary_{ts}.json"
    op_sum.write_text(json.dumps(summary, indent=2, default=jdefault) + "\n")
    sum_sha = sha256_file(op_sum)

    verdict_obj = {
        "generated_at_utc": ts,
        "campaign": 298,
        "part": "verdict",
        "analysis": "final_verdict",
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "real_data_only": True,
        "fabricated_data": False,
        "finding": (
            f"No costed OOS edge proven on the real multi-year funding-carry/basis "
            f"cross-sectional family ({n_total} runs, {len(edge_runs)} edge)."
            if not edge_runs
            else f"Costed OOS edge proven in {len(edge_runs)} config(s) on real multi-year funding/basis data."
        ),
        "basis": "real_usd_m_perp_funding_carry_and_spot_perp_basis_costed_oos",
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
    op_ver = reports / f"campaign298_verdict_{ts}.json"
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
            "campaign": 298,
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
                        any(r["cost_slices"][f"fee{f}_slip{s}"]["oos_net_sum"] > 0 for r in results)
                        for f, s in COST_GRID
                    )
                    else "mean_beats_benchmark_fail"
                )
            ),
            "note": "Diagnosis only; never an edge claim. No threshold weakening.",
        }
        op_bind = reports / f"campaign298_binding_constraint_{ts}.json"
        op_bind.write_text(json.dumps(binding, indent=2, default=jdefault) + "\n")
        bind_sha = sha256_file(op_bind)
        bind_path = str(op_bind.relative_to(root))
        verdict_obj["binding_constraint_artifact"] = bind_path
        verdict_obj["binding_constraint_sha256"] = bind_sha
        op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")
        ver_sha = sha256_file(op_ver)

    print(json.dumps({
        "campaign": 298,
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
