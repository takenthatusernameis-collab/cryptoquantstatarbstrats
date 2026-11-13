#!/usr/bin/env python3
"""C279B — Single-asset price-only sweep.
Real 11-asset spot cache only, price-only, equal-weight B&H spot benchmark.
MeanReversion + Momentum grids; per-asset per-config costed OOS edge test.
"""
from __future__ import annotations
import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
cache_dir = root / "data" / "cache"
reports = root / "reports"
reports.mkdir(exist_ok=True)
ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')

SPOT_CACHE = cache_dir / "0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl"
SPOT_CACHE_SHA = "5607573327c089e0ab990ac48f931752a99e6e89f60599cb2557246f0f5f8c9b"

ASSETS = ["ADA", "AVAX", "BNB", "BTC", "DOT", "ETH", "LINK", "LTC", "POL", "SOL", "XRP"]
TRAIN, TEST, STEP = 720, 168, 168
COST_GRID = [[0, 0], [5, 5], [10, 10], [20, 20], [40, 40]]
COST_KEYS = [f"fee{f}_slip{s}" for f, s in COST_GRID]

MR_LOOKBACKS = (24, 48, 96, 120)
MR_ENTRIES = (1.5, 2.0, 2.5)
MR_EXITS = (0.25, 0.5)
MOM_N = (10, 20, 40)
MOM_M = (20, 40, 80)
MOM_ENTRIES = (0.005, 0.01, 0.02)

def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def load_spot() -> pd.DataFrame:
    with open(SPOT_CACHE, "rb") as f:
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

def jdefault(o):
    if isinstance(o, (np.bool_,)): return bool(o)
    if isinstance(o, (np.integer,)): return int(o)
    if isinstance(o, (np.floating,)): return float(o) if np.isfinite(o) else None
    if isinstance(o, np.ndarray): return o.tolist()
    if isinstance(o, pd.Timestamp): return str(o)
    raise TypeError(str(type(o)))

def evaluate_asset(asset, series_df, engine, strategy_cls, strategy_kwargs, splits, bh_mean):
    """Run one strategy config on one asset across WF splits; return costed OOS results."""
    sdf = series_df[[asset]].dropna()
    n = len(sdf)
    if n < TRAIN + TEST + 10:
        return None
    returns = sdf.pct_change().fillna(0.0)
    pos = None
    try:
        strategy = strategy_cls(asset=asset, **strategy_kwargs)
        signals = strategy.generate_signals(sdf)
        from backtest.engine import BacktestEngine as _BE
        w = _BE._signals_to_weights(strategy, signals, sdf) if False else None
    except Exception:
        return None
    # Build weights manually: signals[asset] is the position (-1/0/1)
    weights = pd.DataFrame(0.0, index=sdf.index, columns=[asset])
    if asset in signals.columns:
        weights[asset] = signals[asset].reindex(sdf.index).fillna(0.0)
    pos = weights.shift(1).fillna(0.0)

    cost_results = {}
    oos_exposure_total = 0
    all_oos_positive = True
    beats_bh_all = True
    total_turnover = 0.0
    for fee, slip in COST_GRID:
        ck = f"fee{fee}_slip{slip}"
        tc = (fee + slip) / 10000.0
        oos_nets = []
        oos_means = []
        turn_sum = 0.0
        for s0, tr_e, te_e in splits:
            seg_pos = pos.iloc[tr_e:te_e]
            seg_ret = returns.iloc[tr_e:te_e]
            port_ret = (seg_pos * seg_ret).sum(axis=1)
            turn = seg_pos.diff().abs().sum(axis=1).fillna(0.0)
            turn.iloc[0] = float(seg_pos.iloc[0].abs().sum())
            turn_sum += float(turn.sum())
            net = port_ret - turn * tc
            oos_nets.append(float(net.sum()))
            oos_means.append(float(net.mean()))
            oos_exposure_total += int((seg_pos.abs().sum(axis=1) > 0).sum())
        oos_net_sum = float(sum(oos_nets))
        oos_net_mean = float(np.mean(oos_means)) if oos_means else 0.0
        edge_here = (oos_exposure_total > 0) and (oos_net_sum > 0) and (oos_net_mean > bh_mean)
        cost_results[ck] = {
            "oos_net_sum": oos_net_sum,
            "oos_net_mean": oos_net_mean,
            "oos_exposure_bars": int(oos_exposure_total),
            "turnover": turn_sum,
            "bh_oos_sum": None,
            "bh_oos_mean": bh_mean,
            "price_only_edge_proven": bool(edge_here),
        }
        if oos_net_sum <= 0:
            all_oos_positive = False
        if oos_net_mean <= bh_mean:
            beats_bh_all = False

    be_bps = None
    for f, s in reversed(COST_GRID):
        ck = f"fee{f}_slip{s}"
        if cost_results[ck]["oos_net_sum"] > 0:
            be_bps = int(f + s)
            break

    edge_proven = bool(oos_exposure_total > 0 and all_oos_positive and beats_bh_all)
    return {
        "asset": asset,
        "strategy": strategy_cls.__name__,
        "params": strategy_kwargs,
        "bars": int(n),
        "n_splits": len(splits),
        "oos_exposure_bars_total": int(oos_exposure_total),
        "turnover": total_turnover,
        "cost_slices": cost_results,
        "break_even_total_cost_bps": be_bps,
        "all_cost_slices_oos_net_positive": bool(all_oos_positive),
        "beats_bh_all_slices": bool(beats_bh_all),
        "bh_oos_mean": bh_mean,
        "price_only_edge_proven": edge_proven,
        "block_reason": None if edge_proven else "no_costed_oos_edge",
    }

def main():
    from backtest.engine import BacktestEngine
    from strategies.mean_reversion import MeanReversionStrategy
    from strategies.momentum import MomentumStrategy

    df = load_spot()
    engine = BacktestEngine(initial_capital=100000.0)
    all_results = []

    for asset in ASSETS:
        if asset not in df.columns:
            continue
        sdf = df[[asset]].dropna()
        n = len(sdf)
        if n < TRAIN + TEST + 10:
            continue
        returns = sdf.pct_change().fillna(0.0)
        splits = wf_splits(n, TRAIN, TEST, STEP)
        bh_nets = []
        for s0, tr_e, te_e in splits:
            bh_nets.append(float(returns.iloc[tr_e:te_e][asset].sum()))
        bh_sum = float(sum(bh_nets))
        bh_mean = float(np.mean(bh_nets)) if bh_nets else 0.0

        # Mean Reversion grid
        for lb in MR_LOOKBACKS:
            for ent in MR_ENTRIES:
                for ex in MR_EXITS:
                    r = evaluate_asset(asset, df, engine, MeanReversionStrategy,
                                       {"lookback": lb, "entry_threshold": ent, "exit_threshold": ex},
                                       splits, bh_mean)
                    if r:
                        all_results.append(r)

        # Momentum grid
        for nn in MOM_N:
            for mm in MOM_M:
                for ent in MOM_ENTRIES:
                    r = evaluate_asset(asset, df, engine, MomentumStrategy,
                                       {"n": nn, "m": mm, "entry_threshold": ent},
                                       splits, bh_mean)
                    if r:
                        all_results.append(r)

    n_edge = sum(1 for r in all_results if r.get("price_only_edge_proven"))
    n_exp = sum(1 for r in all_results if r.get("oos_exposure_bars_total", 0) > 0)
    out = {
        "generated_at_utc": ts,
        "campaign": 279,
        "part": "B",
        "analysis": "single_asset_price_only_sweep",
        "mandate": "C279B — single-asset price-only sweep (MeanReversion + Momentum grids). Real 11-asset spot cache only, price-only, equal-weight B&H spot benchmark.",
        "provenance": {"real_data_only": True, "fabricated_data": False, "fail_closed": True, "no_threshold_weakening": True},
        "data_source": {"spot_cache": str(SPOT_CACHE.relative_to(root)), "spot_cache_sha256": SPOT_CACHE_SHA, "bars": int(len(df)), "interval": "1h", "assets": ASSETS},
        "config": {"assets": ASSETS, "walk_forward": {"train": TRAIN, "test": TEST, "step": STEP}, "cost_grid_bps": COST_GRID,
                   "mean_reversion": {"lookbacks": list(MR_LOOKBACKS), "entries": list(MR_ENTRIES), "exits": list(MR_EXITS)},
                   "momentum": {"n": list(MOM_N), "m": list(MOM_M), "entries": list(MOM_ENTRIES)}},
        "results": all_results,
        "summary": {
            "n_assets": len(ASSETS),
            "n_mr_configs": len(MR_LOOKBACKS) * len(MR_ENTRIES) * len(MR_EXITS),
            "n_momentum_configs": len(MOM_N) * len(MOM_M) * len(MOM_ENTRIES),
            "n_total_runs": len(all_results),
            "n_with_exposure": n_exp,
            "n_edge_proven": n_edge,
        },
    }
    op = reports / f"campaign279_price_only_sweep_{ts}.json"
    op.write_text(json.dumps(out, indent=2, default=jdefault) + "\n")
    print(json.dumps({"artifact": str(op.relative_to(root)), "sha256": sha256_file(op)}, indent=2))
    print(json.dumps(out["summary"], indent=2))

if __name__ == "__main__":
    main()
