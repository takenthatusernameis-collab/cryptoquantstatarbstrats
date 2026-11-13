#!/usr/bin/env python3
"""C281 — fresh real-data campaign for cryptoquantstatarbstrats.

Bottleneck removal: C280 left the programme `BLOCKED_NO_NEW_REAL_DATA` after
only checking *local disk*. This campaign re-tests that premise against the
live public Binance spot feed. If genuinely newer provable real data is
obtainable, it is fetched, cached with full provenance, SHA256-from-bytes
verified, and then subjected to a pre-registered costed out-of-sample edge
sweep. In parallel it runs a gate-feasibility diagnostic that quantifies why
the strict fail-closed enriched gates produce zero exposure (the binding
constraint behind the C279/C280 `NOT_TRADABLE` verdicts).

Everything is real-data-only, fail-closed, and honest:
- no fabricated/synthetic data, no relabeling old caches as new;
- no threshold/gate weakening;
- no cherry-picked windows/costs;
- SHA256-from-bytes for every new artifact;
- edge is claimed ONLY if the costed OOS rule passes on every cost slice.

The script is deliberately heavy: a fresh ~11-asset extended window fetch, a
~663-run costed OOS sweep, and a per-gate exposure-blocker diagnostic.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))

from data import cache as cachemod  # noqa: E402
from data.loader import DataLoader  # noqa: E402

reports = root / "reports"
reports.mkdir(exist_ok=True)
ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

SYMBOLS = ["ADA", "AVAX", "BNB", "BTC", "DOT", "ETH", "LINK", "LTC", "POL", "SOL", "XRP"]
START = "2026-04-01"
END = "2026-11-13"
INTERVAL = "1h"
QUOTE = "USDT"

TRAIN, TEST, STEP = 720, 168, 168
COST_GRID = [[0, 0], [5, 5], [10, 10], [20, 20], [40, 40]]
PAIRS = [
    ("BTC", "ETH"), ("ETH", "SOL"), ("BTC", "SOL"), ("ADA", "ETH"),
    ("XRP", "BTC"), ("BNB", "ETH"), ("BTC", "BNB"), ("SOL", "BNB"),
    ("ADA", "BTC"), ("XRP", "ETH"), ("BNB", "BTC"), ("DOT", "BTC"),
    ("DOT", "ETH"), ("POL", "BTC"), ("AVAX", "BTC"), ("LINK", "BTC"),
    ("LTC", "BTC"),
]
LOOKBACKS = (240, 480, 720)
ENTRIES = (2.0, 2.5)
EXITS = (0.5,)
MR_LOOKBACKS = (24, 48, 96, 120)
MR_ENTRIES = (1.5, 2.0, 2.5)
MR_EXITS = (0.25, 0.5)
MOM_N = (10, 20, 40)
MOM_M = (20, 40, 80)
MOM_ENTRIES = (0.005, 0.01, 0.02)

# Canonical config used only for the exposure-blocker diagnostic (not a sweep).
DIAG_LOOKBACK = 480
DIAG_ENTRY = 2.0
DIAG_EXIT = 0.5


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def jdefault(o):
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o) if np.isfinite(o) else None
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, pd.Timestamp):
        return str(o)
    raise TypeError(str(type(o)))


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
        nets.append(float(seg.mean(axis=1).sum()) if len(seg.columns) > 1 else float(seg.iloc[:, 0].sum()))
    return float(sum(nets)), (float(np.mean(nets)) if nets else 0.0)


def costed_oos(pos, returns, splits, cost_grid, bh_mean):
    slices = {}
    exposure = 0
    all_sum_pos = True
    all_mean_beats = True
    for fee, slip in cost_grid:
        ck = f"fee{fee}_slip{slip}"
        nets, means, turn = [], [], 0.0
        for tr_e, te_e in [(t, e) for _, t, e in splits]:
            seg_pos = pos.iloc[tr_e:te_e]
            seg_ret = returns.iloc[tr_e:te_e]
            port_ret = (seg_pos * seg_ret).sum(axis=1)
            t = seg_pos.diff().abs().sum(axis=1).fillna(0.0)
            t.iloc[0] = float(seg_pos.iloc[0].abs().sum())
            turn += float(t.sum())
            net = port_ret - t * ((fee + slip) / 10000.0)
            nets.append(float(net.sum()))
            means.append(float(net.mean()))
        exposure += int(((pos.abs().sum(axis=1) > 0)).sum())
        net_sum = float(sum(nets))
        net_mean = float(np.mean(means)) if means else 0.0
        slices[ck] = {
            "oos_net_sum": net_sum,
            "oos_net_mean": net_mean,
            "oos_exposure_bars": int(((pos.abs().sum(axis=1) > 0)).sum()),
            "turnover": turn,
            "bh_oos_mean": bh_mean,
        }
        if net_sum <= 0:
            all_sum_pos = False
        if net_mean <= bh_mean:
            all_mean_beats = False
    return slices, exposure, all_sum_pos, all_mean_beats


def part1_fetch_fresh_data() -> dict:
    loader = DataLoader()
    df, prov = cachemod.load_cached(
        loader, SYMBOLS, START, END, interval=INTERVAL, quote_asset=QUOTE,
        use_cache=True, write_cache=True,
    )
    df = df.astype(float).sort_index()
    key = prov.get("cache_key")
    pkl = root / "data" / "cache" / f"{key}.pkl"
    meta = root / "data" / "cache" / f"{key}.meta.json"
    idx_max = df.index.max()
    idx_min = df.index.min()
    new_tail = pd.Timestamp("2026-11-09 00:00:00", tz="UTC")
    extends_beyond_1109 = bool(idx_max > new_tail)

    meta_obj = json.loads(meta.read_text()) if meta.exists() else {}
    out = {
        "generated_at_utc": ts,
        "campaign": 281,
        "part": "1_fetch",
        "analysis": "fresh_real_data_availability",
        "real_data_only": True,
        "fabricated_data": False,
        "verdict": "NEW_REAL_DATA_FETCHED" if extends_beyond_1109 else "NO_NEW_REAL_DATA",
        "new_real_data_available": extends_beyond_1109,
        "bottleneck_premise": "BLOCKED_NO_NEW_REAL_DATA (C280) tested for falsification against live feed",
        "dataset": {
            "cache_key": key,
            "path": str(pkl.relative_to(root)) if pkl.exists() else None,
            "sha256": sha256_file(pkl) if pkl.exists() else None,
            "bytes": pkl.stat().st_size if pkl.exists() else None,
            "meta_path": str(meta.relative_to(root)) if meta.exists() else None,
            "meta_sha256": sha256_file(meta) if meta.exists() else None,
            "symbols": list(df.columns),
            "bars": int(len(df)),
            "window": {"start": str(idx_min), "end": str(idx_max)},
            "extends_beyond_2026_11_09": extends_beyond_1109,
            "days_beyond_c280_exhausted": float((idx_max - new_tail).total_seconds() / 86400.0),
        },
        "provenance_assertions": {
            "fetch_real_data_only": bool(meta_obj.get("fetch_real_data_only")),
            "fetch_fabricated_data": bool(meta_obj.get("fetch_fabricated_data")),
            "blocked_hosts": prov.get("blocked_hosts", []),
            "blocked_routes": prov.get("blocked_routes", []),
            "errors": prov.get("errors", []),
            "cache_hit": bool(prov.get("cache_hit")),
        },
    }
    op = reports / f"campaign281_data_provenance_{ts}.json"
    op.write_text(json.dumps(out, indent=2, default=jdefault) + "\n")
    print(json.dumps({"artifact": str(op.relative_to(root)), "sha256": sha256_file(op)}, indent=2))
    return {"df": df, "prov": prov, "key": key, "out": out, "extends": extends_beyond_1109}


def part2_oos(df: pd.DataFrame, key: str) -> dict:
    from backtest.engine import BacktestEngine
    from strategies.pairs_trading import CointegrationPairsStrategy
    from strategies.mean_reversion import MeanReversionStrategy
    from strategies.momentum import MomentumStrategy

    assets = [a for a in SYMBOLS if a in df.columns]
    n = len(df)
    splits = wf_splits(n, TRAIN, TEST, STEP)
    returns = df.pct_change().fillna(0.0)
    bh_sum, bh_mean = bh_oos(returns, splits)
    engine = BacktestEngine(initial_capital=100000.0)
    results = []

    for a, b in PAIRS:
        if a not in df.columns or b not in df.columns:
            results.append({"pair": f"{a}/{b}", "status": "insufficient_data"})
            continue
        pair_df = df[[a, b]].dropna()
        nn = len(pair_df)
        if nn < TRAIN + TEST + 10:
            results.append({"pair": f"{a}/{b}", "status": "insufficient_data", "bars": int(nn)})
            continue
        pret = pair_df.pct_change().fillna(0.0)
        for lookback in LOOKBACKS:
            for entry in ENTRIES:
                for exit_thr in EXITS:
                    strategy = CointegrationPairsStrategy(
                        pair=(a, b), lookback=lookback, entry_threshold=entry,
                        exit_threshold=exit_thr, cointegration_pvalue=0.05,
                        cointegration_check_interval=lookback,
                        use_enriched_gates=True, strict_enriched_gates=True,
                    )
                    signals = strategy.generate_signals(pair_df)
                    weights = engine._signals_to_weights(signals, pair_df)
                    pos = weights.shift(1).fillna(0.0)
                    slices, exposure, all_sum_pos, all_mean_beats = costed_oos(
                        pos, pret, splits, COST_GRID, bh_mean)
                    edge = bool(exposure > 0 and all_sum_pos and all_mean_beats)
                    results.append({
                        "pair": f"{a}/{b}", "lookback": int(lookback),
                        "entry_threshold": float(entry), "exit_threshold": float(exit_thr),
                        "bars": int(nn), "n_splits": len(splits),
                        "oos_exposure_bars_total": int(exposure),
                        "cost_slices": slices,
                        "all_cost_slices_oos_net_positive": bool(all_sum_pos),
                        "beats_bh_all_slices": bool(all_mean_beats),
                        "bh_oos_mean": bh_mean,
                        "price_only_edge_proven": edge,
                        "block_reason": None if edge else "no_costed_oos_edge",
                    })

    for asset in assets:
        sdf = df[[asset]].dropna()
        nn = len(sdf)
        if nn < TRAIN + TEST + 10:
            continue
        aret = sdf.pct_change().fillna(0.0)
        _, bh_a_mean = bh_oos(aret, splits)
        for lb in MR_LOOKBACKS:
            for ent in MR_ENTRIES:
                for ex in MR_EXITS:
                    strategy = MeanReversionStrategy(
                        asset=asset, lookback=lb, entry_threshold=ent, exit_threshold=ex)
                    signals = strategy.generate_signals(sdf)
                    weights = pd.DataFrame(0.0, index=sdf.index, columns=[asset])
                    if asset in signals.columns:
                        weights[asset] = signals[asset].reindex(sdf.index).fillna(0.0)
                    pos = weights.shift(1).fillna(0.0)
                    slices, exposure, all_sum_pos, all_mean_beats = costed_oos(
                        pos, aret, splits, COST_GRID, bh_a_mean)
                    edge = bool(exposure > 0 and all_sum_pos and all_mean_beats)
                    results.append({
                        "asset": asset, "strategy": "MeanReversionStrategy",
                        "params": {"lookback": int(lb), "entry_threshold": float(ent), "exit_threshold": float(ex)},
                        "bars": int(nn), "n_splits": len(splits),
                        "oos_exposure_bars_total": int(exposure),
                        "cost_slices": slices,
                        "all_cost_slices_oos_net_positive": bool(all_sum_pos),
                        "beats_bh_all_slices": bool(all_mean_beats),
                        "bh_oos_mean": bh_a_mean,
                        "price_only_edge_proven": edge,
                        "block_reason": None if edge else "no_costed_oos_edge",
                    })
        for nn_ in MOM_N:
            for mm in MOM_M:
                for ent in MOM_ENTRIES:
                    strategy = MomentumStrategy(
                        asset=asset, n=int(nn_), m=int(mm), entry_threshold=float(ent))
                    signals = strategy.generate_signals(sdf)
                    weights = pd.DataFrame(0.0, index=sdf.index, columns=[asset])
                    if asset in signals.columns:
                        weights[asset] = signals[asset].reindex(sdf.index).fillna(0.0)
                    pos = weights.shift(1).fillna(0.0)
                    slices, exposure, all_sum_pos, all_mean_beats = costed_oos(
                        pos, aret, splits, COST_GRID, bh_a_mean)
                    edge = bool(exposure > 0 and all_sum_pos and all_mean_beats)
                    results.append({
                        "asset": asset, "strategy": "MomentumStrategy",
                        "params": {"n": int(nn_), "m": int(mm), "entry_threshold": float(ent)},
                        "bars": int(nn), "n_splits": len(splits),
                        "oos_exposure_bars_total": int(exposure),
                        "cost_slices": slices,
                        "all_cost_slices_oos_net_positive": bool(all_sum_pos),
                        "beats_bh_all_slices": bool(all_mean_beats),
                        "bh_oos_mean": bh_a_mean,
                        "price_only_edge_proven": edge,
                        "block_reason": None if edge else "no_costed_oos_edge",
                    })

    edge_runs = [r for r in results if isinstance(r, dict) and r.get("price_only_edge_proven")]
    n_exp = sum(1 for r in results if isinstance(r, dict) and r.get("oos_exposure_bars_total", 0) > 0)
    sweep = {
        "generated_at_utc": ts,
        "campaign": 281,
        "part": "2_oos",
        "analysis": "costed_oos_sweep_on_fresh_extended_data",
        "verdict": "EDGE_PROVEN" if edge_runs else "NOT_TRADABLE",
        "edge_proven": bool(edge_runs),
        "real_data_only": True,
        "fabricated_data": False,
        "fail_closed": True,
        "mandate": "C281 — costed OOS sweep on freshly fetched real spot data extending beyond 2026-11-09; strict enriched gates; no pair_diagnostics_file/enriched_diagnostics; edge rule: OOS exposure>0 AND all cost slices net sum>0 AND mean OOS net > mean B&H OOS net.",
        "data_source": {
            "spot_cache_key": key,
            "bars": int(n),
            "interval": INTERVAL,
            "assets": sorted(df.columns.tolist()),
            "window": {"start": str(df.index.min()), "end": str(df.index.max())},
        },
        "config": {
            "walk_forward": {"train": TRAIN, "test": TEST, "step": STEP},
            "n_splits": len(splits),
            "cost_grid_bps": COST_GRID,
            "pairs": [[a, b] for a, b in PAIRS],
            "lookbacks": list(LOOKBACKS), "entries": list(ENTRIES), "exits": list(EXITS),
            "assets": assets,
            "mean_reversion": {"lookbacks": list(MR_LOOKBACKS), "entries": list(MR_ENTRIES), "exits": list(MR_EXITS)},
            "momentum": {"n": list(MOM_N), "m": list(MOM_M), "entries": list(MOM_ENTRIES)},
        },
        "results": results,
        "summary": {
            "n_total_runs": len([r for r in results if isinstance(r, dict) and "price_only_edge_proven" in r]),
            "n_with_exposure": n_exp,
            "n_edge_proven": len(edge_runs),
        },
    }
    op = reports / f"campaign281_oos_sweep_{ts}.json"
    op.write_text(json.dumps(sweep, indent=2, default=jdefault) + "\n")
    print(json.dumps({"artifact": str(op.relative_to(root)), "sha256": sha256_file(op),
                      "runs": sweep["summary"]["n_total_runs"],
                      "exposure": sweep["summary"]["n_with_exposure"],
                      "edge": sweep["summary"]["n_edge_proven"]}, indent=2))
    return {"sweep": sweep, "path": op, "sha": sha256_file(op), "edge_runs": edge_runs}


def part3_gate_diagnostic(df: pd.DataFrame) -> dict:
    from strategies.pairs_trading import CointegrationPairsStrategy
    from backtest.engine import BacktestEngine

    engine = BacktestEngine(initial_capital=100000.0)
    gate_names = [
        "eg_pass", "johansen_pass", "spread_mr_pass", "hl_bounds_pass",
        "leg_stationarity_ok", "rolling_stable_ok", "no_structural_break",
    ]
    per_pair = []
    for a, b in PAIRS:
        if a not in df.columns or b not in df.columns:
            continue
        pair_df = df[[a, b]].dropna()
        if len(pair_df) < DIAG_LOOKBACK + 10:
            per_pair.append({"pair": f"{a}/{b}", "status": "insufficient_data", "bars": int(len(pair_df))})
            continue
        strategy = CointegrationPairsStrategy(
            pair=(a, b), lookback=DIAG_LOOKBACK, entry_threshold=DIAG_ENTRY,
            exit_threshold=DIAG_EXIT, cointegration_pvalue=0.05,
            cointegration_check_interval=DIAG_LOOKBACK,
            use_enriched_gates=True, strict_enriched_gates=True,
        )
        signals = strategy.generate_signals(pair_df)
        weights = engine._signals_to_weights(signals, pair_df)
        pos = weights.shift(1).fillna(0.0)
        exposure = int((pos.abs().sum(axis=1) > 0).sum())
        breakdown = strategy.get_gate_breakdown()
        rec = {
            "pair": f"{a}/{b}", "bars": int(len(pair_df)),
            "oos_exposure_bars": exposure,
            "exposure_present": exposure > 0,
        }
        if breakdown is not None and len(breakdown):
            rec["gate_pass_share"] = {
                g: float(breakdown[g].mean()) for g in gate_names if g in breakdown.columns
            }
            if "all_pass" in breakdown.columns:
                rec["all_pass_share"] = float(breakdown["all_pass"].mean())
            # Which gate is the most binding (lowest pass share) on this pair.
            shares = {g: float(breakdown[g].mean()) for g in gate_names if g in breakdown.columns}
            if shares:
                rec["binding_gate"] = min(shares, key=shares.get)
        else:
            rec["note"] = "no per-bar breakdown recorded (cached/static path)"
        per_pair.append(rec)

    # Aggregate: how often does each gate block across all pairs?
    agg = {g: {"pairs": 0, "mean_pass_share": None} for g in gate_names}
    for g in gate_names:
        vals = [r["gate_pass_share"][g] for r in per_pair if "gate_pass_share" in r and g in r["gate_pass_share"]]
        agg[g]["pairs"] = len(vals)
        agg[g]["mean_pass_share"] = float(np.mean(vals)) if vals else None
    n_pairs = len([r for r in per_pair if "gate_pass_share" in r])
    n_exposure = len([r for r in per_pair if r.get("exposure_present")])
    diag = {
        "generated_at_utc": ts,
        "campaign": 281,
        "part": "3_gate_diagnostic",
        "analysis": "exposure_blocker_gate_feasibility",
        "real_data_only": True,
        "fabricated_data": False,
        "edge_claim": "NONE (diagnostic only)",
        "config": {
            "lookback": DIAG_LOOKBACK, "entry_threshold": DIAG_ENTRY,
            "exit_threshold": DIAG_EXIT, "strict_enriched_gates": True,
        },
        "finding": (
            "Strict enriched gates block entries; per-gate pass shares below identify the binding constraint."
            if n_exposure == 0 else
            f"{n_exposure}/{n_pairs} pairs produced non-zero exposure under strict gates."
        ),
        "pairs_analyzed": n_pairs,
        "pairs_with_exposure": n_exposure,
        "aggregate_gate_pass_share": agg,
        "per_pair": per_pair,
    }
    op = reports / f"campaign281_gate_diagnostic_{ts}.json"
    op.write_text(json.dumps(diag, indent=2, default=jdefault) + "\n")
    print(json.dumps({"artifact": str(op.relative_to(root)), "sha256": sha256_file(op),
                      "pairs": n_pairs, "pairs_with_exposure": n_exposure}, indent=2))
    return {"diag": diag, "path": op, "sha": sha256_file(op)}


def main():
    p1 = part1_fetch_fresh_data()
    if not p1["extends"]:
        out = {
            "generated_at_utc": ts, "campaign": 281,
            "verdict": "BLOCKED_NO_NEW_REAL_DATA",
            "finding": "Live feed did not provide data beyond 2026-11-09; C280 evidence stands.",
            "provenance": p1["out"],
        }
        op = reports / f"campaign281_verdict_{ts}.json"
        op.write_text(json.dumps(out, indent=2, default=jdefault) + "\n")
        print(json.dumps({"artifact": str(op.relative_to(root)), "sha256": sha256_file(op)}, indent=2))
        return

    p2 = part2_oos(p1["df"], p1["key"])
    p3 = part3_gate_diagnostic(p1["df"])

    registry = {
        "generated_at_utc": ts,
        "campaign": 281,
        "part": "registry",
        "analysis": "tradable_edge_registry",
        "n_tradable": len(p2["edge_runs"]),
        "tradable_configs": p2["edge_runs"],
        "oos_sweep_artifact": str(p2["path"].relative_to(root)),
        "oos_sweep_sha256": p2["sha"],
        "verdict": p2["sweep"]["verdict"],
    }
    op_reg = reports / f"campaign281_tradable_edge_registry_{ts}.json"
    op_reg.write_text(json.dumps(registry, indent=2, default=jdefault) + "\n")

    summary = {
        "generated_at_utc": ts,
        "campaign": 281,
        "part": "summary",
        "analysis": "execution_summary",
        "verdict": p2["sweep"]["verdict"],
        "edge_proven": p2["sweep"]["edge_proven"],
        "real_data_only": True,
        "fabricated_data": False,
        "new_real_data_fetched": True,
        "fresh_window_end": str(p1["df"].index.max()),
        "bottleneck_removed": "BLOCKED_NO_NEW_REAL_DATA falsified against live feed",
        "artifacts": {
            "data_provenance": {"path": str((reports / f"campaign281_data_provenance_{ts}.json").relative_to(root)), "sha256": sha256_file(reports / f"campaign281_data_provenance_{ts}.json")},
            "oos_sweep": {"path": str(p2["path"].relative_to(root)), "sha256": p2["sha"]},
            "gate_diagnostic": {"path": str(p3["path"].relative_to(root)), "sha256": p3["sha"]},
            "registry": {"path": str(op_reg.relative_to(root)), "sha256": sha256_file(op_reg)},
        },
        "oos_summary": p2["sweep"]["summary"],
        "gate_diagnostic_summary": {
            "pairs_analyzed": p3["diag"]["pairs_analyzed"],
            "pairs_with_exposure": p3["diag"]["pairs_with_exposure"],
            "aggregate_gate_pass_share": p3["diag"]["aggregate_gate_pass_share"],
        },
    }
    op_sum = reports / f"campaign281_summary_{ts}.json"
    op_sum.write_text(json.dumps(summary, indent=2, default=jdefault) + "\n")

    verdict = {
        "generated_at_utc": ts,
        "campaign": 281,
        "part": "verdict",
        "verdict": p2["sweep"]["verdict"],
        "edge_proven": p2["sweep"]["edge_proven"],
        "finding": (
            f"Costed OOS edge proven in {len(p2['edge_runs'])} config(s) on fresh real data through {p1['df'].index.max()}."
            if p2["edge_runs"] else
            f"No costed OOS edge on fresh real spot data through {p1['df'].index.max()}."
        ),
        "bottleneck_status": "RESOLVED — fresh real data obtained beyond 2026-11-09",
        "gate_blocker_diagnosis": p3["diag"]["finding"],
        "artifacts": {
            "data_provenance": summary["artifacts"]["data_provenance"],
            "oos_sweep": summary["artifacts"]["oos_sweep"],
            "gate_diagnostic": summary["artifacts"]["gate_diagnostic"],
            "summary": {"path": str(op_sum.relative_to(root)), "sha256": sha256_file(op_sum)},
            "registry": summary["artifacts"]["registry"],
        },
    }
    op_v = reports / f"campaign281_verdict_{ts}.json"
    op_v.write_text(json.dumps(verdict, indent=2, default=jdefault) + "\n")
    print(json.dumps({"artifact": str(op_v.relative_to(root)), "sha256": sha256_file(op_v),
                      "verdict": verdict["verdict"]}, indent=2))


if __name__ == "__main__":
    main()