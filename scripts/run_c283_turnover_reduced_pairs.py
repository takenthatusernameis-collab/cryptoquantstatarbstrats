#!/usr/bin/env python3
"""C283 — turnover-reduced cointegration-pairs stat-arb on the real spot cache.

Motivation: C281B found 369/663 runs gross-positive at 0 bps but EVERY one
fails by the 5-10 bps slice; turnover, not gross signal, is the binding
constraint. C281C showed the fail-closed pairs gate ``rolling_stable_ok`` is
the hard blocker (0.29% pass) and longer windows do not fix it. This campaign
keeps the exact C281B cointegration-pair construction and gates unchanged, and
sweeps ONLY trading frictions that reduce turnover: wider entry/exit bands,
position smoothing, and a minimum holding period. No gate is weakened; every
pre-registered config is reported.

Protocol: same real cache, same 720/168/168 WF, same 5-slice cost grid, same
edge rule as C281B. Strict enriched gates, no pair_diagnostics_file /
enriched_diagnostics.

Artifacts:
    campaign283_oos_sweep_<ts>.json
    campaign283_tradable_edge_registry_<ts>.json
    campaign283_summary_<ts>.json
    campaign283_verdict_<ts>.json

Smoke test (narrows grid only):
    C283_SMOKE=1 python3 scripts/run_c283_turnover_reduced_pairs.py
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
sys.path.insert(0, str(root / "scripts"))
reports = root / "reports"
cache_dir = root / "data" / "cache"
ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

import run_c281b_costed_oos as base  # noqa: E402

TRAIN, TEST, STEP = base.TRAIN, base.TEST, base.STEP
COST_GRID = base.COST_GRID

LOOKBACKS = (240, 480, 720)
ENTRIES = (2.0, 3.0)
EXITS = (0.5, 1.0)
SMOOTH = (1, 3)
HOLDS = (1, 12)


def main():
    cache_sha = base.sha256_file(base.NEW_CACHE)
    if cache_sha != base.NEW_CACHE_SHA_EXPECTED:
        raise SystemExit(f"FATAL: cache sha mismatch {cache_sha}")
    meta = json.loads(base.NEW_CACHE_META.read_text())
    if not meta.get("fetch_real_data_only") or meta.get("fetch_fabricated_data"):
        raise SystemExit("FATAL: provenance is not real-data-only")

    df = base.load_spot(base.NEW_CACHE)
    if int(df.isna().sum().sum()):
        raise SystemExit("FATAL: NaN in real cache; refusing to impute/fabricate")
    n = len(df)
    if n < 5000:
        raise SystemExit(f"FATAL: expected refreshed 5427-bar cache, got {n}")

    portfolio = json.loads(base.PORTFOLIO.read_text())
    pairs = [tuple(p) for p in portfolio.get("pairs", [])]

    smoke = os.environ.get("C283_SMOKE", "") == "1"
    lookbacks = (240,) if smoke else LOOKBACKS
    entries = (2.0,) if smoke else ENTRIES
    exits = (0.5,) if smoke else EXITS
    smooths = (1,) if smoke else SMOOTH
    holds = (1,) if smoke else HOLDS

    from backtest.engine import BacktestEngine
    from strategies.pairs_trading import CointegrationPairsStrategy

    engine = BacktestEngine(initial_capital=100000.0)
    bar_index = np.arange(n)
    results = []

    for a, b in pairs:
        pair_df = df[[a, b]].dropna()
        nn = len(pair_df)
        if nn < TRAIN + TEST + 10:
            results.append({"pair": f"{a}/{b}", "status": "insufficient_data", "bars": int(nn)})
            continue
        pret = pair_df.pct_change().fillna(0.0)
        pair_splits = base.wf_splits(nn, TRAIN, TEST, STEP)
        for lookback in lookbacks:
            for entry in entries:
                for exit_thr in exits:
                    if not (entry > exit_thr >= 0):
                        continue
                    strategy = CointegrationPairsStrategy(
                        pair=(a, b),
                        lookback=lookback,
                        entry_threshold=entry,
                        exit_threshold=exit_thr,
                        cointegration_pvalue=0.05,
                        cointegration_check_interval=lookback,
                        use_enriched_gates=True,
                        strict_enriched_gates=True,
                    )
                    signals = strategy.generate_signals(pair_df)
                    weights = engine._signals_to_weights(signals, pair_df)
                    raw_pos = weights.shift(1).fillna(0.0)
                    for smooth in smooths:
                        if smooth > 1:
                            sm_pos = raw_pos.rolling(smooth, min_periods=1).mean()
                        else:
                            sm_pos = raw_pos
                        for hold in holds:
                            if hold > 1:
                                rebalance = pd.Series(bar_index % hold == 0, index=pair_df.index)
                                pos = sm_pos.where(rebalance).ffill().fillna(0.0)
                            else:
                                pos = sm_pos
                            slices, exposure, all_sum_pos, all_mean_beats = base.costed_oos(
                                pos, pret, pair_splits, COST_GRID, base.bh_oos(pret, pair_splits)[1]
                            )
                            edge = bool(exposure > 0 and all_sum_pos and all_mean_beats)
                            results.append({
                                "pair": f"{a}/{b}",
                                "lookback": int(lookback),
                                "entry_threshold": float(entry),
                                "exit_threshold": float(exit_thr),
                                "smooth": int(smooth),
                                "hold_bars": int(hold),
                                "cointegration_pvalue": 0.05,
                                "cointegration_check_interval": int(lookback),
                                "use_enriched_gates": True,
                                "strict_enriched_gates": True,
                                "pair_diagnostics_file": None,
                                "enriched_diagnostics": None,
                                "bars": int(nn),
                                "n_splits": len(pair_splits),
                                "oos_exposure_bars_total": int(exposure),
                                "cost_slices": slices,
                                "all_cost_slices_oos_net_positive": bool(all_sum_pos),
                                "beats_bh_all_slices": bool(all_mean_beats),
                                "bh_oos_mean": base.bh_oos(pret, pair_splits)[1],
                                "price_only_edge_proven": edge,
                                "block_reason": None if edge else "no_costed_oos_edge",
                            })

    edge_runs = [r for r in results if isinstance(r, dict) and r.get("price_only_edge_proven")]
    n_total = sum(1 for r in results if isinstance(r, dict) and "price_only_edge_proven" in r)
    n_exp = sum(1 for r in results if isinstance(r, dict) and r.get("oos_exposure_bars_total", 0) > 0)
    verdict = "EDGE_PROVEN" if edge_runs else "NOT_TRADABLE"

    sweep = {
        "generated_at_utc": ts,
        "campaign": 283,
        "part": "turnover_reduced_pairs",
        "analysis": "turnover_reduced_cointegration_pairs_costed_oos",
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "real_data_only": True,
        "fabricated_data": False,
        "fail_closed": True,
        "mandate": (
            "C283 — keep C281B cointegration-pair construction and fail-closed gates unchanged; "
            "sweep only turnover-reducing trading frictions (entry/exit bands, position smoothing, "
            "minimum holding). Motivated by C281B: 369/663 runs gross-positive at 0 bps but all "
            "fail by 5-10 bps. No gate weakening."
        ),
        "preflight": {
            "cache_path": str(base.NEW_CACHE.relative_to(root)),
            "cache_sha256": cache_sha,
            "bars": n,
            "nan_count": int(df.isna().sum().sum()),
            "real_data_only": True,
            "fabricated_data": False,
        },
        "universe": {"n_pairs": len(pairs), "pairs": [list(p) for p in pairs], "smoke": smoke},
        "config": {
            "walk_forward": {"train": TRAIN, "test": TEST, "step": STEP},
            "cost_grid_bps": COST_GRID,
            "lookbacks": list(lookbacks),
            "entries": list(entries),
            "exits": list(exits),
            "smooth": list(smooths),
            "hold_bars": list(holds),
        },
        "provenance": {
            "real_data_only": True,
            "fabricated_data": False,
            "no_gate_weakening": True,
            "no_threshold_weakening": True,
            "no_cherry_picked_windows_or_costs": True,
            "all_pre_registered_configs_reported": True,
        },
        "results": results,
        "summary": {
            "n_total_runs": n_total,
            "n_with_exposure": n_exp,
            "n_edge_proven": len(edge_runs),
        },
    }

    op = reports / f"campaign283_oos_sweep_{ts}.json"
    op.write_text(json.dumps(sweep, indent=2, default=base.jdefault) + "\n")
    sweep_sha = base.sha256_file(op)

    registry = {
        "generated_at_utc": ts,
        "campaign": 283,
        "part": "registry",
        "n_tradable": len(edge_runs),
        "tradable_configs": edge_runs,
        "oos_sweep_artifact": str(op.relative_to(root)),
        "oos_sweep_sha256": sweep_sha,
        "verdict": verdict,
    }
    op_reg = reports / f"campaign283_tradable_edge_registry_{ts}.json"
    op_reg.write_text(json.dumps(registry, indent=2, default=base.jdefault) + "\n")
    reg_sha = base.sha256_file(op_reg)

    summary = {
        "generated_at_utc": ts,
        "campaign": 283,
        "part": "summary",
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "summary": sweep["summary"],
        "artifacts": {
            "oos_sweep": {"path": str(op.relative_to(root)), "sha256": sweep_sha},
            "registry": {"path": str(op_reg.relative_to(root)), "sha256": reg_sha},
        },
        "fake_oos_claimed": False,
    }
    op_sum = reports / f"campaign283_summary_{ts}.json"
    op_sum.write_text(json.dumps(summary, indent=2, default=base.jdefault) + "\n")
    sum_sha = base.sha256_file(op_sum)

    verdict_obj = {
        "generated_at_utc": ts,
        "campaign": 283,
        "part": "verdict",
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "finding": (
            f"No costed OOS edge proven for turnover-reduced pairs ({n_total} configs, "
            f"{len(edge_runs)} edge)." if not edge_runs else
            f"Costed OOS edge proven in {len(edge_runs)} config(s)."
        ),
        "basis": "cointegration_pairs_turnover_reduced_costed_oos",
        "dataset": {
            "path": str(base.NEW_CACHE.relative_to(root)),
            "sha256": cache_sha,
            "window": "2026-04-01->2026-11-13T02:00Z",
            "bars": n,
        },
        "oos_sweep_artifact": str(op.relative_to(root)),
        "oos_sweep_sha256": sweep_sha,
        "registry_artifact": str(op_reg.relative_to(root)),
        "registry_sha256": reg_sha,
        "summary_artifact": str(op_sum.relative_to(root)),
        "summary_sha256": sum_sha,
        "hard_bans_honored": [
            "No synthetic/fabricated data",
            "No gate/threshold weakening",
            "No edge claims unless costed OOS test passes",
        ],
    }
    op_ver = reports / f"campaign283_verdict_{ts}.json"
    op_ver.write_text(json.dumps(verdict_obj, indent=2, default=base.jdefault) + "\n")
    ver_sha = base.sha256_file(op_ver)

    print(json.dumps({
        "campaign": 283,
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "n_total_runs": n_total,
        "n_with_exposure": n_exp,
        "n_edge_proven": len(edge_runs),
        "artifacts": {
            "oos_sweep": str(op.relative_to(root)),
            "registry": str(op_reg.relative_to(root)),
            "summary": str(op_sum.relative_to(root)),
            "verdict": str(op_ver.relative_to(root)),
        },
        "sha256": {"oos_sweep": sweep_sha, "registry": reg_sha, "summary": sum_sha, "verdict": ver_sha},
    }, indent=2))


if __name__ == "__main__":
    main()