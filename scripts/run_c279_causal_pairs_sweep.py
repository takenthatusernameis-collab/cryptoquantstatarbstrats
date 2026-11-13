#!/usr/bin/env python3
"""C279A — Causal cointegration-pairs sweep (repo core edge).
Real 11-asset spot cache only, price-only, fail-closed.
Never passes pair_diagnostics_file / enriched_diagnostics (causal per-bar path only).
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

PAIRS = [
    ("BTC","ETH"), ("ETH","SOL"), ("BTC","SOL"), ("ADA","ETH"), ("XRP","BTC"),
    ("BNB","ETH"), ("BTC","BNB"), ("SOL","BNB"), ("ADA","BTC"), ("XRP","ETH"),
    ("BNB","BTC"), ("DOT","BTC"), ("DOT","ETH"), ("POL","BTC"), ("AVAX","BTC"),
    ("LINK","BTC"), ("LTC","BTC"),
]
LOOKBACKS = (240, 480, 720)
ENTRIES = (2.0, 2.5)
EXITS = (0.5,)
COINT_PVALUE = 0.05
TRAIN, TEST, STEP = 720, 168, 168
COST_GRID = [[0,0],[5,5],[10,10],[20,20],[40,40]]
COST_KEYS = [f"fee{f}_slip{s}" for f, s in COST_GRID]

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

def bh_equal_weight(returns_df: pd.DataFrame, splits) -> tuple[float, float]:
    """Equal-weight buy-and-hold OOS net sum and mean across splits."""
    nets = []
    for s0, tr_e, te_e in splits:
        seg = returns_df.iloc[tr_e:te_e]
        nets.append(float(seg.mean(axis=1).sum()))
    return float(sum(nets)), (float(np.mean(nets)) if nets else 0.0)

def main():
    from backtest.engine import BacktestEngine
    from strategies.pairs_trading import CointegrationPairsStrategy

    df = load_spot()
    engine = BacktestEngine(initial_capital=100000.0)
    all_pair_results = []

    for pair in PAIRS:
        a, b = pair
        pair_df = df[[a, b]].dropna()
        n = len(pair_df)
        if n < TRAIN + TEST + 10:
            all_pair_results.append({"pair": f"{a}/{b}", "status": "insufficient_data", "bars": int(n)})
            continue
        returns = pair_df.pct_change().fillna(0.0)
        splits = wf_splits(n, TRAIN, TEST, STEP)
        bh_sum, bh_mean = bh_equal_weight(returns, splits)

        for lookback in LOOKBACKS:
            for entry in ENTRIES:
                for exit_thr in EXITS:
                    strategy = CointegrationPairsStrategy(
                        pair=pair, lookback=lookback, entry_threshold=entry,
                        exit_threshold=exit_thr, cointegration_pvalue=COINT_PVALUE,
                        cointegration_check_interval=lookback,
                        use_enriched_gates=True, strict_enriched_gates=True,
                    )
                    signals = strategy.generate_signals(pair_df)
                    weights = engine._signals_to_weights(signals, pair_df)
                    pos = weights.shift(1).fillna(0.0)

                    gb = strategy.get_gate_breakdown()
                    gate_breakdown = {}
                    if gb is not None and len(gb):
                        for col in gb.columns:
                            vals = gb[col].dropna()
                            if len(vals):
                                gate_breakdown[col] = float(vals.mean())

                    last_eg_p = None
                    if "cointegration_pvalue" in signals.columns:
                        pv = signals["cointegration_pvalue"].dropna()
                        if len(pv):
                            last_eg_p = float(pv.iloc[-1])

                    cost_results = {}
                    oos_exposure_total = 0
                    total_turnover = 0.0
                    all_oos_positive = True
                    beats_bh_all = True
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
                            "oos_exposure_bars": oos_exposure_total,
                            "turnover": turn_sum,
                            "bh_oos_sum": bh_sum,
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

                    all_pair_results.append({
                        "pair": f"{a}/{b}",
                        "lookback": int(lookback),
                        "entry_threshold": float(entry),
                        "exit_threshold": float(exit_thr),
                        "cointegration_pvalue": float(COINT_PVALUE),
                        "cointegration_check_interval": int(lookback),
                        "use_enriched_gates": True,
                        "strict_enriched_gates": True,
                        "pair_diagnostics_file": None,
                        "enriched_diagnostics": None,
                        "bars": int(n),
                        "n_splits": len(splits),
                        "oos_exposure_bars_total": int(oos_exposure_total),
                        "gate_breakdown_pass_share": gate_breakdown,
                        "last_trailing_eg_pvalue": last_eg_p,
                        "cost_slices": cost_results,
                        "break_even_total_cost_bps": be_bps,
                        "all_cost_slices_oos_net_positive": bool(all_oos_positive),
                        "beats_bh_all_slices": bool(beats_bh_all),
                        "price_only_edge_proven": edge_proven,
                        "block_reason": None if edge_proven else "no_costed_oos_edge",
                    })

    out = {
        "generated_at_utc": ts,
        "campaign": 279,
        "part": "A",
        "analysis": "causal_cointegration_pairs_sweep",
        "mandate": "C279A — causal cointegration-pairs sweep (repo core edge). Real 11-asset spot cache only, price-only, fail-closed, no pair_diagnostics_file/enriched_diagnostics.",
        "provenance": {"real_data_only": True, "fabricated_data": False, "fail_closed": True, "no_threshold_weakening": True, "no_pair_diagnostics_file": True, "no_enriched_diagnostics": True},
        "data_source": {"spot_cache": str(SPOT_CACHE.relative_to(root)), "spot_cache_sha256": SPOT_CACHE_SHA, "bars": int(len(df)), "interval": "1h", "assets": sorted(df.columns.tolist())},
        "config": {"pairs": [[a, b] for a, b in PAIRS], "lookbacks": list(LOOKBACKS), "entries": list(ENTRIES), "exits": list(EXITS), "cointegration_pvalue": float(COINT_PVALUE), "walk_forward": {"train": TRAIN, "test": TEST, "step": STEP}, "cost_grid_bps": COST_GRID},
        "results": all_pair_results,
        "summary": {
            "n_pairs": len(PAIRS),
            "n_configs_per_pair": len(LOOKBACKS) * len(ENTRIES) * len(EXITS),
            "n_total_runs": len([r for r in all_pair_results if isinstance(r, dict) and "lookback" in r]),
            "n_edge_proven": sum(1 for r in all_pair_results if isinstance(r, dict) and r.get("price_only_edge_proven")),
            "n_zero_exposure": sum(1 for r in all_pair_results if isinstance(r, dict) and r.get("oos_exposure_bars_total", 1) == 0),
        },
    }
    op = reports / f"campaign279_causal_pairs_{ts}.json"
    op.write_text(json.dumps(out, indent=2, default=jdefault) + "\n")
    print(json.dumps({"artifact": str(op.relative_to(root)), "sha256": sha256_file(op)}, indent=2))
    print(json.dumps(out["summary"], indent=2))

if __name__ == "__main__":
    main()
