#!/usr/bin/env python3
"""PRIORITY 4 (HEAVY): net-of-cost walk-forward IS/OOS + benchmark-relative
validation for momentum & mean_reversion on REAL cached Binance spot 1h.

Real data only. No fabrication. No threshold weakening. Fail-closed.
Leaves a concrete JSON artifact in reports/.
"""
from __future__ import annotations

import glob
import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backtest.engine import BacktestEngine  # noqa: E402
from strategies.momentum import MomentumStrategy  # noqa: E402
from strategies.mean_reversion import MeanReversionStrategy  # noqa: E402

CACHE_DIR = ROOT / "data" / "cache"
REPORTS = ROOT / "reports"
WINDOW = "2026-04-01_2026-10-30"
INTERVAL = "1h"
# Cost grid (fee, slippage) in fraction of notional per turnover side-pair convention
# used by engine (cost = turnover * (fee_rate + slippage)). Sweep {0,5,10,20} bps combos.
COST_GRID_BPS = [(0, 0), (5, 0), (0, 5), (5, 5), (10, 0), (0, 10), (10, 10), (20, 0), (0, 20), (20, 20)]
# Walk-forward: explicit train/test/step (rolling). 5112 bars 1h ~ 213 days.
# 30d train, 7d test, step=test (rolling, non-overlapping tests).
TRAIN = 24 * 30  # 720
TEST = 24 * 7    # 168
STEP = 168       # equals test_period (engine advances by test_period)
MIN_ASSETS_REPORT = ["BTC", "ETH", "SOL", "BNB"]

PROVENANCE = {
    "real_data_only": True,
    "fabricated_data": False,
    "fail_closed": True,
    "no_threshold_weakening": True,
    "data_source": "real cached Binance spot 1h (data/cache/*_2026-04-01_2026-10-30_1h.pkl)",
    "window": "2026-04-01..2026-10-30",
    "bars_expected": 5112,
    "interval": "1h",
    "assets_expected": 11,
}


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def load_real_spot() -> tuple[dict[str, pd.Series], list[dict[str, Any]]]:
    meta = []
    series = {}
    for p in sorted(glob.glob(str(CACHE_DIR / f"*_{WINDOW}_{INTERVAL}.pkl"))):
        sym = os.path.basename(p).split("_")[0]
        s = pd.read_pickle(p)
        if isinstance(s, pd.DataFrame):
            if sym in s.columns:
                s = s[sym]
            elif s.shape[1] == 1:
                s = s.iloc[:, 0]
            else:
                raise ValueError(f"Ambiguous cached frame for {sym}: {list(s.columns)}")
        s = s.astype(float)
        mpath = p.replace(".pkl", ".meta.json")
        m = {}
        if os.path.exists(mpath):
            m = json.load(open(mpath))
        if not m.get("real_data_only", False) or m.get("fabricated_data", True):
            raise RuntimeError(f"Cache meta fails real-data provenance for {sym}: {m}")
        series[sym] = s
        meta.append({
            "symbol": sym,
            "bars": int(len(s)),
            "first": str(s.index[0]),
            "last": str(s.index[-1]),
            "meta": {k: m.get(k) for k in ["real_data_only", "fabricated_data", "source", "market", "host"]},
        })
    if len(series) != 11:
        raise RuntimeError(f"Expected 11 cached assets, found {len(series)}: {sorted(series)}")
    return series, meta


def _to_bps_frac(bps: int) -> float:
    return float(bps) / 10000.0


def _weights_from_signals(signals: pd.DataFrame, asset: str, index: pd.Index) -> pd.DataFrame:
    col = asset if asset in signals.columns else None
    if col is None:
        # fallback: long-short
        w = signals.get("long", 0).astype(float) - signals.get("short", 0).astype(float)
    else:
        w = signals[col].astype(float)
    df = pd.DataFrame({asset: w.reindex(index).fillna(0.0)}, index=index)
    return df


def run_one(family: str, asset: str, price: pd.Series) -> dict[str, Any]:
    data = pd.DataFrame({asset: price.astype(float)})
    data = data.loc[~data.index.duplicated()].sort_index()
    engine = BacktestEngine(initial_capital=100000.0)
    # strict enriched gates = default True (fail-closed). Momentum/MR build internal
    # permissive diagnostics when none supplied (per implementation) — we keep defaults
    # (no threshold weakening) and record actual gate behavior.
    if family == "momentum":
        strat = MomentumStrategy(asset=asset)
    elif family == "mean_reversion":
        strat = MeanReversionStrategy(asset=asset)
    else:
        raise ValueError(family)
    signals = strat.generate_signals(data)
    weights = _weights_from_signals(signals, asset, data.index)
    # exposure stats
    wshift = weights.shift(1).fillna(0.0)
    active = (wshift[asset].abs() > 0)
    n_active_bars = int(active.sum())
    trades = int((wshift[asset].diff().abs().fillna(wshift[asset].abs()) > 0).sum())
    enriched_ok = signals.get("enriched_gates_ok")
    gates_all_ok = bool(enriched_ok.astype(float).min() >= 1.0) if enriched_ok is not None else None

    cost_results = []
    bench_results = []
    bh_weights = pd.DataFrame({asset: 1.0}, index=data.index)
    for fee_bps, slip_bps in COST_GRID_BPS:
        fee = _to_bps_frac(fee_bps)
        slip = _to_bps_frac(slip_bps)
        res = engine.walk_forward_portfolio(
            weights, data,
            train_period=TRAIN, test_period=TEST,
            fee_rate=fee, slippage=slip,
            mode="rolling",
        )
        bres = engine.walk_forward_portfolio(
            bh_weights, data,
            train_period=TRAIN, test_period=TEST,
            fee_rate=fee, slippage=slip,
            mode="rolling",
        )
        cost_results.append({
            "fee_bps": fee_bps, "slippage_bps": slip_bps,
            "fee_rate": fee, "slippage": slip,
            "total_cost_bps": fee_bps + slip_bps,
            "is_mean_return": res.get("is_mean_return"),
            "oos_mean_return": res.get("oos_mean_return"),
            "mean_return": res.get("mean_return"),
            "oos_is_ratio": res.get("oos_is_ratio"),
            "positive_periods": res.get("positive_periods"),
            "total_periods": res.get("total_periods"),
            "windows": len(res.get("results", [])),
        })
        bench_results.append({
            "fee_bps": fee_bps, "slippage_bps": slip_bps,
            "benchmark_oos_mean_return": bres.get("oos_mean_return"),
            "benchmark_is_mean_return": bres.get("is_mean_return"),
        })
    # merge bench
    for c, b in zip(cost_results, bench_results):
        c.update(b)
        c["beats_benchmark_oos"] = (
            c.get("oos_mean_return") is not None and b.get("benchmark_oos_mean_return") is not None
            and float(c["oos_mean_return"]) > float(b["benchmark_oos_mean_return"])
        )
        c["oos_net_positive"] = (c.get("oos_mean_return") is not None and float(c["oos_mean_return"]) > 0)

    all_oos_pos = all(r["oos_net_positive"] for r in cost_results)
    all_beat_bench = all(r["beats_benchmark_oos"] for r in cost_results)
    has_exposure = n_active_bars > 0 and trades > 0
    # Pre-stated fail-closed rule
    rule = (
        "oos_edge_proven=true IFF (all cost-grid slices: OOS net mean_return > 0) "
        "AND (all cost-grid slices: OOS net mean_return > buy-and-hold benchmark OOS mean_return on same WF windows) "
        "AND (executed exposure/trades > 0). Else false (fail-closed)."
    )
    oos_edge_proven = bool(all_oos_pos and all_beat_bench and has_exposure)
    return {
        "family": family,
        "asset": asset,
        "provenance": PROVENANCE,
        "params": strat.params if hasattr(strat, "params") else {},
        "strategy_defaults": {
            "use_enriched_gates": getattr(strat, "use_enriched_gates", None),
            "strict_enriched_gates": getattr(strat, "strict_enriched_gates", None),
            "enriched_gates_all_ok_observed": gates_all_ok,
        },
        "walk_forward": {
            "mode": "rolling",
            "train_bars": TRAIN, "test_bars": TEST, "step_bars": STEP,
            "train_days_approx": 30, "test_days_approx": 7,
            "engine_advances_by": "test_period (non-overlapping test windows)",
        },
        "exposure": {"n_active_bars_executed": n_active_bars, "n_turnover_events": trades, "bars": int(len(data))},
        "cost_grid_bps": COST_GRID_BPS,
        "cost_grid_results": cost_results,
        "summary": {
            "all_cost_slices_oos_net_positive": all_oos_pos,
            "all_cost_slices_beat_benchmark_oos": all_beat_bench,
            "has_exposure": has_exposure,
            "oos_edge_proven": oos_edge_proven,
            "pre_stated_rule": rule,
        },
    }


def aggregate(family: str, per_asset: list[dict[str, Any]]) -> dict[str, Any]:
    # aggregate across all 11 by averaging OOS/IS per cost slice (equal-weight assets)
    by_cost = {}
    for r in per_asset:
        for c in r["cost_grid_results"]:
            k = (c["fee_bps"], c["slippage_bps"])
            by_cost.setdefault(k, {"fee_bps": k[0], "slippage_bps": k[1], "oos": [], "is": [], "bench_oos": [], "beat": [], "pos": []})
            by_cost[k]["oos"].append(c.get("oos_mean_return"))
            by_cost[k]["is"].append(c.get("is_mean_return"))
            by_cost[k]["bench_oos"].append(c.get("benchmark_oos_mean_return"))
            by_cost[k]["beat"].append(bool(c.get("beats_benchmark_oos")))
            by_cost[k]["pos"].append(bool(c.get("oos_net_positive")))
    agg_rows = []
    for k, v in sorted(by_cost.items()):
        def _m(x):
            x = [float(i) for i in x if i is not None]
            return float(np.mean(x)) if x else None
        agg_rows.append({
            "fee_bps": v["fee_bps"], "slippage_bps": v["slippage_bps"],
            "mean_oos_mean_return_across_assets": _m(v["oos"]),
            "mean_is_mean_return_across_assets": _m(v["is"]),
            "mean_benchmark_oos_mean_return_across_assets": _m(v["bench_oos"]),
            "assets_beating_benchmark_oos": int(sum(v["beat"])),
            "assets_oos_net_positive": int(sum(v["pos"])),
            "n_assets": len(v["oos"]),
        })
    any_proven = any(r["summary"]["oos_edge_proven"] for r in per_asset)
    all_proven = all(r["summary"]["oos_edge_proven"] for r in per_asset)
    n_proven = sum(1 for r in per_asset if r["summary"]["oos_edge_proven"])
    return {
        "family": family,
        "n_assets": len(per_asset),
        "assets": [r["asset"] for r in per_asset],
        "per_cost_equal_weight_asset_mean": agg_rows,
        "n_assets_oos_edge_proven": n_proven,
        "any_asset_oos_edge_proven": any_proven,
        "all_assets_oos_edge_proven": all_proven,
        "aggregate_oos_edge_proven_fail_closed": bool(all_proven),
        "rule_note": "Aggregate marked proven only if ALL assets pass pre-stated per-asset rule (fail-closed). Per-asset results are authoritative.",
    }


def main():
    t0 = time.time()
    series, cache_meta = load_real_spot()
    families = ["momentum", "mean_reversion"]
    all_results = {"momentum": [], "mean_reversion": []}
    for fam in families:
        for sym in sorted(series.keys()):
            print(f"[run] {fam} {sym}", flush=True)
            r = run_one(fam, sym, series[sym])
            all_results[fam].append(r)
    aggs = {fam: aggregate(fam, res) for fam, res in all_results.items()}
    # pytest counts rerun marker placeholder filled by outer; we record command intent
    out = {
        "report": "momentum_mr_costed_oos",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "mandate": "PRIORITY 4 Deliverable A — heavy net-of-cost walk-forward IS/OOS + benchmark-relative on real cached Binance spot 1h; fail-closed, real data only, no threshold weakening",
        "provenance": PROVENANCE,
        "cache_inventory": cache_meta,
        "config": {
            "families": families,
            "assets": sorted(series.keys()),
            "min_assets_reported_explicitly": MIN_ASSETS_REPORT,
            "cost_grid_bps_fee_slippage": COST_GRID_BPS,
            "walk_forward": {"mode": "rolling", "train_bars": TRAIN, "test_bars": TEST, "step_bars": STEP},
            "benchmark": "buy-and-hold constant weight 1.0 on same asset, same WF windows/cost grid",
            "strategy_defaults_honored": "MomentumStrategy/MeanReversionStrategy defaults (use_enriched_gates=True, strict_enriched_gates=True) — no threshold weakening",
        },
        "pre_stated_oos_edge_rule": (
            "oos_edge_proven=true IFF (all cost-grid slices: OOS net mean_return > 0) "
            "AND (all cost-grid slices: OOS net mean_return > buy-and-hold benchmark OOS mean_return on same WF windows) "
            "AND (executed exposure/trades > 0). Else false (fail-closed)."
        ),
        "per_family_per_asset": all_results,
        "aggregates": aggs,
        "runtime_seconds": round(time.time() - t0, 2),
        "environment": {"python": sys.version, "platform": platform.platform()},
    }
    # sanity: min assets present
    for fam in families:
        got = {r["asset"] for r in all_results[fam]}
        missing = [a for a in MIN_ASSETS_REPORT if a not in got]
        if missing:
            raise RuntimeError(f"Missing required assets for {fam}: {missing}")
    REPORTS.mkdir(parents=True, exist_ok=True)
    path = REPORTS / f"momentum_mr_costed_oos_{_now_utc()}.json"
    path.write_text(json.dumps(out, indent=2, default=str))
    print(f"[artifact] {path}")
    # brief stdout summary
    for fam in families:
        print(f"[summary] {fam} n_proven={aggs[fam]['n_assets_oos_edge_proven']}/{aggs[fam]['n_assets']} agg_proven={aggs[fam]['aggregate_oos_edge_proven_fail_closed']}")
    return str(path)

if __name__ == "__main__":
    main()
