#!/usr/bin/env python3
"""C282 — cross-sectional statistical arbitrage on refreshed real spot data.

Motivation (from C281C): the cointegration-pairs core is blocked by the
fail-closed ``rolling_stable_ok`` gate (0.29% pooled pass share) and longer
trailing windows do NOT fix it (probe: 720/960/1440/2160/2880-bar trailing
samples all ``stable=False`` for representative pairs). Weakening that gate is
forbidden. C282 therefore tests a materially different, pre-registered
stat-arb hypothesis on the SAME real data:

    Cross-sectional momentum / short-term reversal across the 11 real spot
    assets, formed on strictly trailing returns, dollar-neutral, equal or
    inverse-volatility risk-adjusted, rebalanced every bar, costed OOS.

Protocol is identical in spirit to C281B: same 720/168/168 walk-forward, same
cost grid, same edge rule, real data only, fail-closed (NaN formation returns
never traded), no cherry-picked windows/costs, every config reported.

Edge rule (unchanged):
    oos_edge_proven=true IFF OOS exposure > 0 AND for EVERY cost slice the OOS
    net sum > 0 AND mean OOS net > mean equal-weight buy-and-hold OOS net on
    the same WF windows.

Artifacts:
    campaign282_oos_sweep_<ts>.json
    campaign282_tradable_edge_registry_<ts>.json
    campaign282_summary_<ts>.json
    campaign282_verdict_<ts>.json

Smoke test (narrows the pre-registered grid only; never changes the rule):
    C282_SMOKE=1 python3 scripts/run_c282_cross_sectional_stat_arb.py
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

NEW_CACHE = cache_dir / "26736ab8fbb16974dd59f123855ab7e4810026d12712a05a363eabacd814ade2.pkl"
NEW_CACHE_META = NEW_CACHE.with_suffix(".meta.json")
NEW_CACHE_SHA_EXPECTED = "9355aed62b00a56b46ebba70eec4f9855620e8fea1b6eeae417ec6d7dea349df"
PORTFOLIO = root / "reports" / "portfolio_real.json"

TRAIN, TEST, STEP = 720, 168, 168
COST_GRID = [[0, 0], [5, 5], [10, 10], [20, 20], [40, 40]]

# Pre-registered grid (all reported; no post-hoc selection).
# HOLDS attacks the C281B finding: 369/663 runs are gross-positive at 0 bps but
# every one fails by the 5-10 bps slice, i.e. turnover is the binding constraint.
LOOKBACKS = (24, 96, 168, 336)
TOPK = (2, 3)
DIRECTIONS = ("momentum", "reversal")
WEIGHTINGS = ("equal", "inverse_vol")
HOLDS = (1, 6, 24, 168)  # bars between rebalances


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


def bh_oos(returns_df: pd.DataFrame, splits) -> tuple[float, float]:
    nets = []
    for s0, tr_e, te_e in splits:
        seg = returns_df.iloc[tr_e:te_e]
        nets.append(
            float(seg.mean(axis=1).sum()) if len(seg.columns) > 1 else float(seg.iloc[:, 0].sum())
        )
    return float(sum(nets)), (float(np.mean(nets)) if nets else 0.0)


def costed_oos(pos, returns, splits, cost_grid, bh_mean):
    slices = {}
    exposure = 0
    all_sum_pos = True
    all_mean_beats = True
    for fee, slip in cost_grid:
        ck = f"fee{fee}_slip{slip}"
        tc = (fee + slip) / 10000.0
        nets, means, turn = [], [], 0.0
        for tr_e, te_e in [(t, e) for _, t, e in splits]:
            seg_pos = pos.iloc[tr_e:te_e]
            seg_ret = returns.iloc[tr_e:te_e]
            port_ret = (seg_pos * seg_ret).sum(axis=1)
            t = seg_pos.diff().abs().sum(axis=1).fillna(0.0)
            t.iloc[0] = float(seg_pos.iloc[0].abs().sum())
            turn += float(t.sum())
            net = port_ret - t * tc
            nets.append(float(net.sum()))
            means.append(float(net.mean()))
        exposure += int((pos.abs().sum(axis=1) > 0).sum())
        net_sum = float(sum(nets))
        net_mean = float(np.mean(means)) if means else 0.0
        slices[ck] = {
            "oos_net_sum": net_sum,
            "oos_net_mean": net_mean,
            "oos_exposure_bars": int((pos.abs().sum(axis=1) > 0).sum()),
            "turnover": turn,
            "bh_oos_mean": bh_mean,
        }
        if net_sum <= 0:
            all_sum_pos = False
        if net_mean <= bh_mean:
            all_mean_beats = False
    return slices, exposure, all_sum_pos, all_mean_beats


def cross_sectional_weights(prices: pd.DataFrame, lookback: int, k: int, direction: str, weighting: str) -> pd.DataFrame:
    """Strictly causal dollar-neutral cross-sectional weights.

    Formation signal at bar t uses prices[t-lookback]/prices[t] only (trailing).
    Positions are shifted by one bar by the caller so bar-t weights are applied
    to bar-t+1 returns.
    """
    assets = list(prices.columns)
    n = len(prices)
    if lookback <= 0 or lookback >= n:
        return pd.DataFrame(0.0, index=prices.index, columns=assets)

    if weighting == "equal":
        score = prices.div(prices.shift(lookback)).sub(1.0)
    elif weighting == "inverse_vol":
        ret = prices.pct_change().fillna(0.0)
        vol = ret.rolling(lookback, min_periods=max(2, lookback // 2)).std().replace(0.0, np.nan)
        raw = prices.div(prices.shift(lookback)).sub(1.0)
        score = raw.div(vol)
        score = score.replace([np.inf, -np.inf], np.nan)
    else:
        raise ValueError(f"unknown weighting {weighting}")

    if direction == "reversal":
        score = -score

    rank = score.rank(axis=1, ascending=False)  # 1 = best
    valid = score.notna()
    long_mask = valid & (rank <= k)
    short_mask = valid & (rank > (len(assets) - k))

    w = pd.DataFrame(0.0, index=prices.index, columns=assets)
    # Equal risk budget per leg: +0.5 gross long, -0.5 gross short.
    if weighting == "equal":
        w[long_mask] = 0.5 / k
        w[short_mask] = -0.5 / k
    else:
        # Inverse-vol weights within each leg, normalized to 0.5 gross per leg.
        inv = 1.0 / prices.pct_change().rolling(lookback, min_periods=max(2, lookback // 2)).std().replace(0.0, np.nan)
        inv = inv.replace([np.inf, -np.inf], np.nan)
        long_w = (inv * long_mask).div((inv * long_mask).sum(axis=1).replace(0.0, np.nan), axis=0) * 0.5
        short_w = (inv * short_mask).div((inv * short_mask).sum(axis=1).replace(0.0, np.nan), axis=0) * 0.5
        w = long_w.fillna(0.0) - short_w.fillna(0.0)
    return w.fillna(0.0)


def main():
    if not NEW_CACHE.exists() or not NEW_CACHE_META.exists():
        raise SystemExit("FATAL: C281A cache/meta missing")
    cache_sha = sha256_file(NEW_CACHE)
    meta_sha = sha256_file(NEW_CACHE_META)
    if cache_sha != NEW_CACHE_SHA_EXPECTED:
        raise SystemExit(f"FATAL: cache sha256 mismatch {cache_sha}")

    meta = json.loads(NEW_CACHE_META.read_text())
    df = load_spot(NEW_CACHE)
    n = len(df)
    nan_count = int(df.isna().sum().sum())
    if not meta.get("fetch_real_data_only") or meta.get("fetch_fabricated_data"):
        raise SystemExit("FATAL: provenance flags are not real-data-only")
    if nan_count:
        raise SystemExit("FATAL: NaN in real cache; refusing to impute/fabricate")

    portfolio = json.loads(PORTFOLIO.read_text())
    assets = list(portfolio.get("symbols", []))
    missing = [a for a in assets if a not in df.columns]
    if missing:
        raise SystemExit(f"FATAL: portfolio assets missing from cache: {missing}")

    smoke = os.environ.get("C282_SMOKE", "") == "1"
    lookbacks = (24,) if smoke else LOOKBACKS
    topk = (2,) if smoke else TOPK
    directions = ("momentum",) if smoke else DIRECTIONS
    weightings = ("equal",) if smoke else WEIGHTINGS
    holds = (1,) if smoke else HOLDS

    prices = df[assets]
    returns = prices.pct_change().fillna(0.0)
    splits = wf_splits(n, TRAIN, TEST, STEP)
    bh_sum, bh_mean = bh_oos(returns, splits)

    results = []
    bar_index = np.arange(n)
    for lookback in lookbacks:
        for k in topk:
            for direction in directions:
                for weighting in weightings:
                    w_raw = cross_sectional_weights(prices, lookback, k, direction, weighting)
                    for hold in holds:
                        if hold > 1:
                            rebalance = pd.Series(bar_index % hold == 0, index=prices.index)
                            w = w_raw.where(rebalance).ffill().fillna(0.0)
                        else:
                            w = w_raw
                        pos = w.shift(1).fillna(0.0)
                        slices, exposure, all_sum_pos, all_mean_beats = costed_oos(
                            pos, returns, splits, COST_GRID, bh_mean
                        )
                        edge = bool(exposure > 0 and all_sum_pos and all_mean_beats)
                        results.append({
                            "lookback": int(lookback),
                            "top_k": int(k),
                            "direction": direction,
                            "weighting": weighting,
                            "hold_bars": int(hold),
                            "n_assets": len(assets),
                            "bars": int(n),
                            "n_splits": len(splits),
                            "oos_exposure_bars_total": int(exposure),
                            "cost_slices": slices,
                            "all_cost_slices_oos_net_positive": bool(all_sum_pos),
                            "beats_bh_all_slices": bool(all_mean_beats),
                            "bh_oos_mean": bh_mean,
                            "price_only_edge_proven": edge,
                            "block_reason": None if edge else "no_costed_oos_edge",
                        })

    edge_runs = [r for r in results if r.get("price_only_edge_proven")]
    n_total = len(results)
    n_exp = sum(1 for r in results if r.get("oos_exposure_bars_total", 0) > 0)
    verdict = "EDGE_PROVEN" if edge_runs else "NOT_TRADABLE"

    sweep = {
        "generated_at_utc": ts,
        "campaign": 282,
        "part": "cross_sectional_stat_arb",
        "analysis": "cross_sectional_momentum_reversal_costed_oos",
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "real_data_only": True,
        "fabricated_data": False,
        "fail_closed": True,
        "mandate": (
            "C282 — pre-registered cross-sectional momentum/reversal stat-arb on the C281A real "
            "spot cache; strictly causal trailing formation returns; dollar-neutral; equal or "
            "inverse-vol weighting; hold_bars in {1,6,24,168} to attack turnover; same 720/168/168 "
            "WF, cost grid and edge rule as C281B. Motivated by C281B (369/663 runs gross-positive "
            "at 0 bps but all fail by 5-10 bps: turnover is binding) and C281C (pairs blocked by "
            "rolling_stable_ok; longer windows do not help). Gates are never weakened."
        ),
        "preflight": {
            "cache_path": str(NEW_CACHE.relative_to(root)),
            "cache_sha256": cache_sha,
            "meta_sha256": meta_sha,
            "bars": n,
            "nan_count": nan_count,
            "start": str(df.index.min()),
            "end": str(df.index.max()),
            "real_data_only": True,
            "fabricated_data": False,
        },
        "data_source": {
            "spot_cache": str(NEW_CACHE.relative_to(root)),
            "spot_cache_sha256": cache_sha,
            "meta_sha256": meta_sha,
            "window": {"start": str(df.index.min()), "end": str(df.index.max())},
            "assets": assets,
        },
        "universe": {"assets": assets, "n_assets": len(assets), "smoke": smoke},
        "config": {
            "walk_forward": {"train": TRAIN, "test": TEST, "step": STEP},
            "n_splits": len(splits),
            "cost_grid_bps": COST_GRID,
            "lookbacks": list(lookbacks),
            "top_k": list(topk),
            "directions": list(directions),
            "weightings": list(weightings),
            "hold_bars": list(holds),
            "formation": "trailing price[t-lookback]/price[t]-1, shifted 1 bar",
            "gross_leg": 0.5,
            "turnover_control": "hold_bars>1 rebalances only every H bars and holds otherwise",
        },
        "provenance": {
            "real_data_only": True,
            "fabricated_data": False,
            "no_threshold_weakening": True,
            "no_gate_weakening": True,
            "no_cherry_picked_windows_or_costs": True,
            "all_pre_registered_configs_reported": True,
        },
        "results": results,
        "summary": {
            "n_total_runs": n_total,
            "n_with_exposure": n_exp,
            "n_edge_proven": len(edge_runs),
            "bh_oos_mean_full_universe": bh_mean,
        },
    }

    op = reports / f"campaign282_oos_sweep_{ts}.json"
    op.write_text(json.dumps(sweep, indent=2, default=jdefault) + "\n")
    sweep_sha = sha256_file(op)

    registry = {
        "generated_at_utc": ts,
        "campaign": 282,
        "part": "registry",
        "analysis": "tradable_edge_registry",
        "n_tradable": len(edge_runs),
        "tradable_configs": edge_runs,
        "oos_sweep_artifact": str(op.relative_to(root)),
        "oos_sweep_sha256": sweep_sha,
        "verdict": verdict,
    }
    op_reg = reports / f"campaign282_tradable_edge_registry_{ts}.json"
    op_reg.write_text(json.dumps(registry, indent=2, default=jdefault) + "\n")
    reg_sha = sha256_file(op_reg)

    summary = {
        "generated_at_utc": ts,
        "campaign": 282,
        "part": "summary",
        "analysis": "execution_summary",
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "universe": sweep["universe"],
        "summary": sweep["summary"],
        "artifacts": {
            "oos_sweep": {"path": str(op.relative_to(root)), "sha256": sweep_sha},
            "registry": {"path": str(op_reg.relative_to(root)), "sha256": reg_sha},
        },
        "fake_oos_claimed": False,
        "next_action": (
            "If NOT_TRADABLE: run C283 (pre-registered next hypothesis) on the same data; do not "
            "weaken gates, do not re-run C281B/C282. If EDGE_PROVEN: promote per registry rules."
        ),
    }
    op_sum = reports / f"campaign282_summary_{ts}.json"
    op_sum.write_text(json.dumps(summary, indent=2, default=jdefault) + "\n")
    sum_sha = sha256_file(op_sum)

    verdict_obj = {
        "generated_at_utc": ts,
        "campaign": 282,
        "part": "verdict",
        "analysis": "final_verdict",
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "finding": (
            f"No costed OOS edge proven for cross-sectional stat-arb on refreshed real spot data "
            f"({n_total} pre-registered configs, {len(edge_runs)} edge)."
            if not edge_runs
            else f"Costed OOS edge proven in {len(edge_runs)} config(s)."
        ),
        "basis": "cross_sectional_spot_price_only_costed_oos",
        "dataset": {
            "path": str(NEW_CACHE.relative_to(root)),
            "sha256": cache_sha,
            "window": "2026-04-01->2026-11-13T02:00Z",
            "bars": n,
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
            "No edge claims unless costed OOS test passes",
        ],
    }
    op_ver = reports / f"campaign282_verdict_{ts}.json"
    op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")
    ver_sha = sha256_file(op_ver)

    print(json.dumps({
        "campaign": 282,
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "n_total_runs": n_total,
        "n_with_exposure": n_exp,
        "n_edge_proven": len(edge_runs),
        "n_splits": len(splits),
        "bars": n,
        "artifacts": {
            "oos_sweep": str(op.relative_to(root)),
            "registry": str(op_reg.relative_to(root)),
            "summary": str(op_sum.relative_to(root)),
            "verdict": str(op_ver.relative_to(root)),
        },
        "sha256": {
            "oos_sweep": sweep_sha,
            "registry": reg_sha,
            "summary": sum_sha,
            "verdict": ver_sha,
        },
    }, indent=2))


if __name__ == "__main__":
    main()