#!/usr/bin/env python3
"""C281B — costed out-of-sample edge test on the refreshed real spot cache.

This is the mandatory floor of C281. It reuses the C280 Path A protocol
verbatim (same walk-forward split, same cost grid, same fail-closed enriched
gates, same edge rule) but points at the newest provable real cache
``26736ab8...`` (5427 x 11 Binance spot 1h bars, 2026-04-01 -> 2026-11-13T02:00Z,
``fetch_real_data_only=true``, ``fetch_fabricated_data=false``, 0 NaN), which is
the C281A dataset. It sweeps the full 17-pair universe from
``reports/portfolio_real.json`` plus all 11 single assets.

Edge rule (unchanged from C280):
    oos_edge_proven=true IFF OOS exposure > 0 AND for EVERY cost slice the OOS
    net sum > 0 AND mean OOS net > mean buy-and-hold OOS net on the same WF
    windows.

No edge is ever fabricated: an honest ``NOT_TRADABLE`` is a valid outcome.
Every emitted artifact records its SHA256-from-bytes.

Smoke testing (does not change the protocol, only narrows the universe):
    C281B_LIMIT_PAIRS=1 C281B_LIMIT_ASSETS=1 python3 scripts/run_c281b_costed_oos.py
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

# C281A dataset: verified provable real Binance spot cache.
NEW_CACHE = cache_dir / "26736ab8fbb16974dd59f123855ab7e4810026d12712a05a363eabacd814ade2.pkl"
NEW_CACHE_META = NEW_CACHE.with_suffix(".meta.json")
NEW_CACHE_SHA_EXPECTED = "9355aed62b00a56b46ebba70eec4f9855620e8fea1b6eeae417ec6d7dea349df"
NEW_CACHE_META_SHA_EXPECTED = "95baf25daae1656a8c6f074acdcd909250565ddda8e86920b00d85163646afd1"
C281A_PROVENANCE = "reports/campaign281_data_provenance_20261113T024731Z.json"
PORTFOLIO = root / "reports" / "portfolio_real.json"

# Protocol constants — identical to C280 Path A.
TRAIN, TEST, STEP = 720, 168, 168
COST_GRID = [[0, 0], [5, 5], [10, 10], [20, 20], [40, 40]]
PAIR_LOOKBACKS = (240, 480, 720)
PAIR_ENTRIES = (2.0, 2.5)
PAIR_EXITS = (0.5,)
MR_LOOKBACKS = (24, 48, 96, 120)
MR_ENTRIES = (1.5, 2.0, 2.5)
MR_EXITS = (0.25, 0.5)
MOM_N = (10, 20, 40)
MOM_M = (20, 40, 80)
MOM_ENTRIES = (0.005, 0.01, 0.02)


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


def main():
    preflight = {}

    if not NEW_CACHE.exists():
        raise SystemExit(f"FATAL: C281A cache missing: {NEW_CACHE}")
    if not NEW_CACHE_META.exists():
        raise SystemExit(f"FATAL: C281A meta missing: {NEW_CACHE_META}")

    cache_sha = sha256_file(NEW_CACHE)
    meta_sha = sha256_file(NEW_CACHE_META)
    if cache_sha != NEW_CACHE_SHA_EXPECTED:
        raise SystemExit(
            f"FATAL: cache sha256 mismatch: {cache_sha} != {NEW_CACHE_SHA_EXPECTED}"
        )
    if meta_sha != NEW_CACHE_META_SHA_EXPECTED:
        raise SystemExit(
            f"FATAL: meta sha256 mismatch: {meta_sha} != {NEW_CACHE_META_SHA_EXPECTED}"
        )

    meta = json.loads(NEW_CACHE_META.read_text())
    df = load_spot(NEW_CACHE)
    n = len(df)
    nan_count = int(df.isna().sum().sum())

    preflight = {
        "cache_path": str(NEW_CACHE.relative_to(root)),
        "cache_sha256": cache_sha,
        "meta_sha256": meta_sha,
        "meta": meta,
        "bars": n,
        "nan_count": nan_count,
        "index_duplicate_count": int(df.index.duplicated().sum()),
        "start": str(df.index.min()),
        "end": str(df.index.max()),
        "real_data_only": bool(meta.get("fetch_real_data_only")),
        "fabricated_data": bool(meta.get("fetch_fabricated_data")),
        "assertions": {
            "fetch_real_data_only_is_true": bool(meta.get("fetch_real_data_only")) is True,
            "fetch_fabricated_data_is_false": bool(meta.get("fetch_fabricated_data")) is False,
            "no_nan": nan_count == 0,
            "no_duplicate_index": int(df.index.duplicated().sum()) == 0,
            "sha256_from_bytes_verified": True,
        },
    }
    if not all(preflight["assertions"].values()):
        raise SystemExit(f"FATAL: C281A dataset preflight failed: {json.dumps(preflight, indent=2)}")
    if nan_count:
        raise SystemExit("FATAL: NaN present in real cache; refusing to impute/fabricate.")

    portfolio = json.loads(PORTFOLIO.read_text())
    all_pairs = [tuple(p) for p in portfolio.get("pairs", [])]
    all_assets = list(portfolio.get("symbols", []))

    limit_pairs = int(os.environ.get("C281B_LIMIT_PAIRS", "0") or 0)
    limit_assets = int(os.environ.get("C281B_LIMIT_ASSETS", "0") or 0)
    pairs = all_pairs[:limit_pairs] if limit_pairs > 0 else all_pairs
    assets = all_assets[:limit_assets] if limit_assets > 0 else all_assets

    universe = {
        "n_pairs_total": len(all_pairs),
        "n_pairs_run": len(pairs),
        "pairs_run": [list(p) for p in pairs],
        "n_assets_total": len(all_assets),
        "n_assets_run": len(assets),
        "assets_run": assets,
        "limited_smoke": bool(limit_pairs or limit_assets),
        "limit_pairs": limit_pairs,
        "limit_assets": limit_assets,
    }

    returns_full = df.pct_change().fillna(0.0)
    splits = wf_splits(n, TRAIN, TEST, STEP)
    bh_sum, bh_mean = bh_oos(returns_full, splits)

    results = []

    from backtest.engine import BacktestEngine
    from strategies.mean_reversion import MeanReversionStrategy
    from strategies.momentum import MomentumStrategy
    from strategies.pairs_trading import CointegrationPairsStrategy

    engine = BacktestEngine(initial_capital=100000.0)

    # ---- pairs: cointegration, fail-closed enriched gates, no diagnostics file ----
    for a, b in pairs:
        pair_df = df[[a, b]].dropna()
        nn = len(pair_df)
        if nn < TRAIN + TEST + 10:
            results.append({"pair": f"{a}/{b}", "status": "insufficient_data", "bars": int(nn)})
            continue
        pret = pair_df.pct_change().fillna(0.0)
        pair_splits = wf_splits(nn, TRAIN, TEST, STEP)
        for lookback in PAIR_LOOKBACKS:
            for entry in PAIR_ENTRIES:
                for exit_thr in PAIR_EXITS:
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
                    pos = weights.shift(1).fillna(0.0)
                    slices, exposure, all_sum_pos, all_mean_beats = costed_oos(
                        pos, pret, pair_splits, COST_GRID, bh_mean
                    )
                    edge = bool(exposure > 0 and all_sum_pos and all_mean_beats)
                    results.append({
                        "pair": f"{a}/{b}",
                        "lookback": int(lookback),
                        "entry_threshold": float(entry),
                        "exit_threshold": float(exit_thr),
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
                        "bh_oos_mean": bh_mean,
                        "price_only_edge_proven": edge,
                        "block_reason": None if edge else "no_costed_oos_edge",
                    })

    # ---- single-asset MeanReversion + Momentum ----
    for asset in assets:
        sdf = df[[asset]].dropna()
        nn = len(sdf)
        if nn < TRAIN + TEST + 10:
            continue
        aret = sdf.pct_change().fillna(0.0)
        asset_splits = wf_splits(nn, TRAIN, TEST, STEP)
        _, bh_a_mean = bh_oos(aret, asset_splits)
        for lb in MR_LOOKBACKS:
            for ent in MR_ENTRIES:
                for ex in MR_EXITS:
                    strategy = MeanReversionStrategy(
                        asset=asset,
                        lookback=lb,
                        entry_threshold=ent,
                        exit_threshold=ex,
                        use_enriched_gates=True,
                        strict_enriched_gates=True,
                    )
                    signals = strategy.generate_signals(sdf)
                    weights = pd.DataFrame(0.0, index=sdf.index, columns=[asset])
                    if asset in signals.columns:
                        weights[asset] = signals[asset].reindex(sdf.index).fillna(0.0)
                    pos = weights.shift(1).fillna(0.0)
                    slices, exposure, all_sum_pos, all_mean_beats = costed_oos(
                        pos, aret, asset_splits, COST_GRID, bh_a_mean
                    )
                    edge = bool(exposure > 0 and all_sum_pos and all_mean_beats)
                    results.append({
                        "asset": asset,
                        "strategy": "MeanReversionStrategy",
                        "params": {
                            "lookback": int(lb),
                            "entry_threshold": float(ent),
                            "exit_threshold": float(ex),
                        },
                        "bars": int(nn),
                        "n_splits": len(asset_splits),
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
                        asset=asset,
                        n=int(nn_),
                        m=int(mm),
                        entry_threshold=float(ent),
                        use_enriched_gates=True,
                        strict_enriched_gates=True,
                    )
                    signals = strategy.generate_signals(sdf)
                    weights = pd.DataFrame(0.0, index=sdf.index, columns=[asset])
                    if asset in signals.columns:
                        weights[asset] = signals[asset].reindex(sdf.index).fillna(0.0)
                    pos = weights.shift(1).fillna(0.0)
                    slices, exposure, all_sum_pos, all_mean_beats = costed_oos(
                        pos, aret, asset_splits, COST_GRID, bh_a_mean
                    )
                    edge = bool(exposure > 0 and all_sum_pos and all_mean_beats)
                    results.append({
                        "asset": asset,
                        "strategy": "MomentumStrategy",
                        "params": {
                            "n": int(nn_),
                            "m": int(mm),
                            "entry_threshold": float(ent),
                        },
                        "bars": int(nn),
                        "n_splits": len(asset_splits),
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
    n_total = sum(1 for r in results if isinstance(r, dict) and "price_only_edge_proven" in r)
    verdict = "EDGE_PROVEN" if edge_runs else "NOT_TRADABLE"

    sweep = {
        "generated_at_utc": ts,
        "campaign": 281,
        "part": "B_costed_oos",
        "analysis": "costed_oos_sweep_on_refreshed_real_spot_data",
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "real_data_only": True,
        "fabricated_data": False,
        "fail_closed": True,
        "mandate": (
            "C281B — pre-registered costed OOS sweep on the C281A refreshed real cache; "
            "full 17-pair universe + all 11 single assets; fail-closed enriched gates; "
            "no pair_diagnostics_file/enriched_diagnostics; edge rule: OOS exposure>0 AND "
            "all cost slices net sum>0 AND mean OOS net > mean B&H OOS net."
        ),
        "preflight": preflight,
        "data_source": {
            "spot_cache": str(NEW_CACHE.relative_to(root)),
            "spot_cache_sha256": cache_sha,
            "meta_sha256": meta_sha,
            "c281a_provenance": C281A_PROVENANCE,
            "bars": int(n),
            "interval": "1h",
            "assets": sorted(df.columns.tolist()),
            "window": {"start": str(df.index.min()), "end": str(df.index.max())},
            "note": (
                "Refreshed 2026-04-01->2026-11-13T02:00Z real spot cache; extends C279's "
                "exhausted 2026-04-01->2026-10-30 window by 14 days and provides 28 WF splits "
                "(vs 1 on the C280 data)."
            ),
        },
        "universe": universe,
        "config": {
            "walk_forward": {"train": TRAIN, "test": TEST, "step": STEP},
            "n_splits": len(splits),
            "cost_grid_bps": COST_GRID,
            "pairs": [list(p) for p in pairs],
            "pair_grid": {
                "lookbacks": list(PAIR_LOOKBACKS),
                "entries": list(PAIR_ENTRIES),
                "exits": list(PAIR_EXITS),
            },
            "assets": assets,
            "mean_reversion": {
                "lookbacks": list(MR_LOOKBACKS),
                "entries": list(MR_ENTRIES),
                "exits": list(MR_EXITS),
            },
            "momentum": {
                "n": list(MOM_N),
                "m": list(MOM_M),
                "entries": list(MOM_ENTRIES),
            },
        },
        "provenance": {
            "real_data_only": True,
            "fabricated_data": False,
            "no_pair_diagnostics_file": True,
            "no_enriched_diagnostics": True,
            "no_threshold_weakening": True,
            "no_cherry_picked_windows_or_costs": True,
        },
        "results": results,
        "summary": {
            "n_total_runs": n_total,
            "n_with_exposure": n_exp,
            "n_edge_proven": len(edge_runs),
            "bh_oos_mean_full_universe": bh_mean,
        },
    }

    op = reports / f"campaign281_oos_sweep_{ts}.json"
    op.write_text(json.dumps(sweep, indent=2, default=jdefault) + "\n")
    sweep_sha = sha256_file(op)

    registry = {
        "generated_at_utc": ts,
        "campaign": 281,
        "part": "B_registry",
        "analysis": "tradable_edge_registry",
        "n_tradable": len(edge_runs),
        "tradable_configs": edge_runs,
        "oos_sweep_artifact": str(op.relative_to(root)),
        "oos_sweep_sha256": sweep_sha,
        "verdict": verdict,
        "real_data_only": True,
        "fabricated_data": False,
    }
    op_reg = reports / f"campaign281_tradable_edge_registry_{ts}.json"
    op_reg.write_text(json.dumps(registry, indent=2, default=jdefault) + "\n")
    reg_sha = sha256_file(op_reg)

    summary = {
        "generated_at_utc": ts,
        "campaign": 281,
        "part": "B_summary",
        "analysis": "execution_summary",
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "real_data_only": True,
        "fabricated_data": False,
        "universe": universe,
        "artifacts": {
            "oos_sweep": {"path": str(op.relative_to(root)), "sha256": sweep_sha},
            "registry": {"path": str(op_reg.relative_to(root)), "sha256": reg_sha},
        },
        "summary": sweep["summary"],
        "fake_oos_claimed": False,
        "next_action": (
            "If NOT_TRADABLE: run C281C gate diagnostics on the same data (diagnosis only, "
            "never an edge claim); then define C282. If EDGE_PROVEN: promote per registry rules."
        ),
    }
    op_sum = reports / f"campaign281_summary_{ts}.json"
    op_sum.write_text(json.dumps(summary, indent=2, default=jdefault) + "\n")
    sum_sha = sha256_file(op_sum)

    verdict_obj = {
        "generated_at_utc": ts,
        "campaign": 281,
        "part": "B_verdict",
        "analysis": "final_verdict",
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "finding": (
            f"No costed OOS edge proven on refreshed real spot data ({n_total} runs, "
            f"{len(edge_runs)} edge)."
            if not edge_runs
            else f"Costed OOS edge proven in {len(edge_runs)} config(s) on refreshed real spot data."
        ),
        "basis": "spot_price_only_costed_oos",
        "dataset": {
            "path": str(NEW_CACHE.relative_to(root)),
            "sha256": cache_sha,
            "window": "2026-04-01->2026-11-13T02:00Z",
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
            "No edge claims unless costed OOS test passes",
        ],
    }
    op_ver = reports / f"campaign281_verdict_{ts}.json"
    op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")
    ver_sha = sha256_file(op_ver)

    print(json.dumps({
        "campaign": 281,
        "part": "B",
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "n_total_runs": n_total,
        "n_with_exposure": n_exp,
        "n_edge_proven": len(edge_runs),
        "n_splits": len(splits),
        "bars": n,
        "window": {"start": str(df.index.min()), "end": str(df.index.max())},
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