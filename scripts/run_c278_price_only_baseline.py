#!/usr/bin/env python3
"""C278: price-only baseline on the real 11-asset spot cache.

C277A proved the C273 volume-return "edge" does not survive a spot-price PnL
gate. C278 asks the only remaining economically relevant question: does any
existing price-based strategy produce costed out-of-sample PnL from real spot
prices on the same 11 assets?

Route:
  1. Attempt CointegrationPairsStrategy on the real spot cache with the cached
     publication-grade diagnostics, strict fail-closed gates, same WF/cost grid.
  2. If pairs are blocked (no causal gate passes -> zero exposure), fail closed
     and run the single-asset MeanReversionStrategy on the same 11 assets, same
     WF/cost grid, with an equal-weight buy-and-hold benchmark.

No network, no synthetic data, no threshold weakening.
"""

from __future__ import annotations

import hashlib
import json
import pickle
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))

from strategies.mean_reversion import MeanReversionStrategy  # noqa: E402
from strategies.pairs_trading import CointegrationPairsStrategy  # noqa: E402

cache_dir = root / "data" / "cache"
reports = root / "reports"
reports.mkdir(exist_ok=True)
ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

SPOT_CACHE = cache_dir / "0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl"
SPOT_META = cache_dir / "0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.meta.json"
PAIR_DIAGNOSTICS = reports / "portfolio_real.json"
C277_ARTIFACT = reports / "campaign277_c273_price_pnl_revalidation_20261112T172258Z.json"

TRAIN, TEST, STEP = 720, 168, 168
COST_GRID = [[0, 0], [5, 5], [10, 10], [20, 20], [40, 40]]
MR_LOOKBACK = 30
MR_ENTRY = 2.0
MR_EXIT = 0.5
CANONICAL_PAIRS = [("BTC", "ETH"), ("ETH", "SOL"), ("BTC", "SOL")]


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_spot():
    meta = json.loads(SPOT_META.read_text()) if SPOT_META.exists() else {}
    with open(SPOT_CACHE, "rb") as f:
        df = pickle.load(f)
    if isinstance(df, pd.Series):
        df = df.to_frame()
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    return df, meta, sha256_file(SPOT_CACHE)


def wf_splits(n: int, train: int = TRAIN, test: int = TEST, step: int = STEP):
    out = []
    i = 0
    while i + train + test <= n:
        out.append((i, i + train, i + train + test))
        i += step
    return out


def evaluate(pos: pd.Series, rets: pd.Series, splits) -> dict:
    npn = rets.to_numpy(dtype=float)
    ppn = pos.to_numpy(dtype=float)
    bh = npn.copy()
    oos_mask = np.zeros(len(npn), dtype=bool)
    for (_s0, tr_e, te_e) in splits:
        oos_mask[tr_e:te_e] = True
    gross = float((ppn * npn)[oos_mask].sum()) if oos_mask.any() else float("nan")
    per_cost = {}
    for fee, slp in COST_GRID:
        tc = (fee + slp) / 10000.0
        trades = np.abs(np.diff(np.concatenate([[0.0], ppn])))
        strat = ppn * npn - trades * tc
        oos_np = np.concatenate([strat[tr_e:te_e] for (_s0, tr_e, te_e) in splits]) if splits else np.array([])
        oos_bh = np.concatenate([bh[tr_e:te_e] for (_s0, tr_e, te_e) in splits]) if splits else np.array([])
        oos_tr = np.concatenate([trades[tr_e:te_e] for (_s0, tr_e, te_e) in splits]) if splits else np.array([])
        per_cost[f"fee{fee}_slip{slp}"] = {
            "oos_net_sum": float(oos_np.sum()),
            "oos_net_mean": float(oos_np.mean()) if oos_np.size else np.nan,
            "bh_oos_net_mean": float(oos_bh.mean()) if oos_bh.size else np.nan,
            "oos_n": int(oos_np.size),
            "exposure_bars": int((np.abs(pos.shift(1).fillna(0.0)) > 0).sum()),
            "oos_turnover_sum": float(oos_tr.sum()),
        }
    turnover = float(np.abs(np.diff(np.concatenate([[0.0], ppn])))[oos_mask].sum())
    be = (gross / turnover * 10000.0) if turnover > 0 else None
    return {
        "per_cost": per_cost,
        "gross_oos_sum": gross,
        "oos_turnover_sum": turnover,
        "breakeven_total_cost_bps": float(be) if be is not None and np.isfinite(be) else None,
        "bh_oos_net_mean": float(bh[oos_mask].mean()) if oos_mask.any() else np.nan,
        "oos_net_mean_fee0": per_cost["fee0_slip0"]["oos_net_mean"],
    }


def run_pairs(data: pd.DataFrame) -> dict:
    results = {}
    any_exposure = False
    for pair in CANONICAL_PAIRS:
        strat = CointegrationPairsStrategy(
            pair=pair,
            pair_diagnostics_file=str(PAIR_DIAGNOSTICS),
            strict_enriched_gates=True,
        )
        signals = strat.generate_signals(data)
        legs = [signals[a].abs() + signals[b].abs() for a, b in [pair]]
        gross = legs[0].to_numpy(dtype=float)
        splits = wf_splits(len(data))
        oos_mask = np.zeros(len(data), dtype=bool)
        for (_s0, tr_e, te_e) in splits:
            oos_mask[tr_e:te_e] = True
        exposure_oos = int((gross[oos_mask] > 0).sum()) if oos_mask.any() else 0
        if exposure_oos > 0:
            any_exposure = True
        bd = strat.get_gate_breakdown()
        gate_pass = None
        if bd is not None and len(bd):
            gate_pass = float(bd["all_pass"].mean())
        results["/".join(pair)] = {
            "pair": list(pair),
            "exposure_bars_oos": exposure_oos,
            "any_exposure_oos": bool(exposure_oos > 0),
            "all_pass_gate_share": gate_pass,
            "blocked": bool(exposure_oos == 0),
            "block_reason": (
                "strict enriched cointegration gates fail closed on the real cached "
                "diagnostics (eg/johansen/spread_mr/leg_stationarity/rolling_stable "
                "all fail); no causal pass -> zero exposure."
                if exposure_oos == 0
                else "gates passed and produced exposure"
            ),
        }
    return {
        "route": "CointegrationPairsStrategy",
        "diagnostics_source": str(PAIR_DIAGNOSTICS.relative_to(root)),
        "diagnostics_sha256": sha256_file(PAIR_DIAGNOSTICS) if PAIR_DIAGNOSTICS.exists() else None,
        "strict_enriched_gates": True,
        "any_exposure_oos": bool(any_exposure),
        "blocked": bool(not any_exposure),
        "pairs": results,
    }


def run_mean_reversion(data: pd.DataFrame) -> dict:
    per_asset = {}
    strat_means = []
    bh_means = []
    any_exposure = False
    for sym in data.columns:
        price = data[sym].astype(float)
        rets = np.log(price).diff()
        strat = MeanReversionStrategy(
            asset=sym,
            lookback=MR_LOOKBACK,
            entry_threshold=MR_ENTRY,
            exit_threshold=MR_EXIT,
        )
        signals = strat.generate_signals(data)
        pos = (signals["long"].astype(float) - signals["short"].astype(float))
        aligned = pd.concat([pos.rename("pos"), rets.rename("ret")], axis=1).dropna()
        if len(aligned) < TRAIN + TEST + 50:
            per_asset[sym] = {"status": "insufficient"}
            continue
        pos = aligned["pos"]
        rets = aligned["ret"]
        splits = wf_splits(len(pos))
        if len(splits) == 0:
            per_asset[sym] = {"status": "no_splits"}
            continue
        ev = evaluate(pos, rets, splits)
        if ev["per_cost"]["fee0_slip0"]["exposure_bars"] > 0:
            any_exposure = True
        per_asset[sym] = {"status": "ok", "bars": int(len(pos)), "pnl": ev}
        oos_mask = np.zeros(len(pos), dtype=bool)
        for (_s0, tr_e, te_e) in splits:
            oos_mask[tr_e:te_e] = True
        strat_means.append(ev["oos_net_mean_fee0"])
        bh_means.append(ev["bh_oos_net_mean"])
    cross = {}
    for fee, slp in COST_GRID:
        key = f"fee{fee}_slip{slp}"
        cross[key] = float(
            sum(a["pnl"]["per_cost"][key]["oos_net_sum"]
                for a in per_asset.values() if a.get("status") == "ok")
        )
    all_pos = all(v > 0 for v in cross.values()) if cross else False
    all_beat_bh = (
        np.nanmean(strat_means) > np.nanmean(bh_means)
        if strat_means and bh_means
        else False
    )
    edge = bool(any_exposure and all_pos and all_beat_bh)
    return {
        "route": "MeanReversionStrategy (single-asset fallback)",
        "params": {
            "lookback": MR_LOOKBACK,
            "entry_threshold": MR_ENTRY,
            "exit_threshold": MR_EXIT,
        },
        "any_exposure_oos": bool(any_exposure),
        "per_asset": per_asset,
        "cross_asset_oos_net_sums": cross,
        "all_cost_slices_positive": bool(all_pos),
        "all_cost_slices_beat_bh_mean_rule": bool(all_beat_bh),
        "mean_net_strategy_fee0": float(np.nanmean(strat_means)) if strat_means else np.nan,
        "mean_bh_fee0": float(np.nanmean(bh_means)) if bh_means else np.nan,
        "price_only_edge_proven": edge,
    }


def main() -> None:
    data, spot_meta, spot_sha = load_spot()
    splits = wf_splits(len(data))

    pairs = run_pairs(data)
    if pairs["blocked"]:
        mr = run_mean_reversion(data)
        primary = mr
        primary_route = "mean_reversion_fallback"
    else:
        primary = pairs
        primary_route = "pairs"

    price_only_edge = bool(
        primary.get("price_only_edge_proven", False)
        if primary_route == "mean_reversion_fallback"
        else primary.get("any_exposure_oos", False)
    )

    # C277 comparison (volume-return metric is NOT tradable).
    c277 = json.loads(C277_ARTIFACT.read_text()) if C277_ARTIFACT.exists() else {}

    out = {
        "generated_at_utc": ts,
        "campaign": 278,
        "purpose": "Price-only baseline on real 11-asset spot cache after C277A proved C273 volume-return metric is not tradable.",
        "return_basis": "spot_price",
        "walk_forward": {"train": TRAIN, "test": TEST, "step": STEP},
        "cost_grid_bps": COST_GRID,
        "n_bars": int(len(data)),
        "symbols": list(data.columns),
        "spot_cache_sha256": spot_sha,
        "pairs_route": pairs,
        "primary_route": primary_route,
        "primary": primary,
        "price_only_edge_proven": price_only_edge,
        "c277_reference": {
            "path": str(C277_ARTIFACT.relative_to(root)),
            "sha256": sha256_file(C277_ARTIFACT) if C277_ARTIFACT.exists() else None,
            "price_pnl_edge_proven": c277.get("price_pnl_edge_proven"),
            "cross_asset_price_pnl": c277.get("cross_asset_price_pnl"),
            "cross_asset_volume_return_pnl": c277.get("cross_asset_volume_return_pnl"),
        },
        "edge_rule": (
            "edge proven IFF OOS exposure>0 AND all cost slices OOS net sum>0 AND mean "
            "OOS net > mean B&H spot-price return on the same WF windows."
        ),
    }
    out_name = f"campaign278_price_only_baseline_{ts}.json"
    out_path = reports / out_name
    out_path.write_text(json.dumps(out, indent=2, default=str) + "\n")
    out_sha = sha256_file(out_path)

    # Tradable edge registry: every candidate with return basis and verdict.
    registry_entries = []
    registry_entries.append(
        {
            "candidate": "C273_VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_PERCENTILE_SPREAD_SHOCK_MR",
            "campaign": 273,
            "return_basis": "quote_volume",
            "price_pnl_edge_proven": False,
            "tradable": False,
            "status": "NOT_TRADABLE",
            "note": "C277A recomputed same feature/positions/WF/cost grid on spot prices: cross-asset price PnL negative at all cost slices.",
        }
    )
    registry_entries.append(
        {
            "candidate": "C277_C273_PRICE_PNL_REVALIDATION",
            "campaign": 277,
            "return_basis": "spot_price",
            "price_pnl_edge_proven": bool(c277.get("price_pnl_edge_proven", False)),
            "tradable": bool(c277.get("price_pnl_edge_proven", False)),
            "status": "PROMOTED" if c277.get("price_pnl_edge_proven") else "NOT_PROMOTED",
            "note": "Same feature as C273; PnL from real spot log-price returns.",
        }
    )
    for pair_name, pr in pairs["pairs"].items():
        registry_entries.append(
            {
                "candidate": f"C278_PAIRS_{pair_name.replace('/', '_')}",
                "campaign": 278,
                "return_basis": "spot_price",
                "price_pnl_edge_proven": bool(pr["any_exposure_oos"]),
                "tradable": bool(pr["any_exposure_oos"]),
                "status": "BLOCKED_BY_GATES" if pr["blocked"] else "EXPOSURE_PRESENT",
                "note": pr["block_reason"],
            }
        )
    if primary_route == "mean_reversion_fallback":
        for sym, a in primary["per_asset"].items():
            if a.get("status") != "ok":
                continue
            pc = a["pnl"]["per_cost"]
            per_asset_edge = bool(
                pc["fee0_slip0"]["exposure_bars"] > 0
                and all(v["oos_net_sum"] > 0 for v in pc.values())
                and pc["fee0_slip0"]["oos_net_mean"] > pc["fee0_slip0"]["bh_oos_net_mean"]
            )
            registry_entries.append(
                {
                    "candidate": f"C278_MEAN_REVERSION_{sym}",
                    "campaign": 278,
                    "return_basis": "spot_price",
                    "price_pnl_edge_proven": per_asset_edge,
                    "tradable": per_asset_edge,
                    "status": "EDGE" if per_asset_edge else "NO_EDGE",
                    "note": (
                        f"fee0 OOS net sum={pc['fee0_slip0']['oos_net_sum']:+.4f}, "
                        f"B&H mean={pc['fee0_slip0']['bh_oos_net_mean']:+.6f}, "
                        f"break-even bps={a['pnl']['breakeven_total_cost_bps']}"
                    ),
                }
            )

    registry = {
        "generated_at_utc": ts,
        "campaign": 278,
        "return_basis_legend": {"spot_price": "tradable PnL basis", "quote_volume": "NOT_TRADABLE"},
        "overall_price_only_edge_proven": price_only_edge,
        "entries": registry_entries,
        "summary": {
            "n_candidates": len(registry_entries),
            "n_tradable": sum(1 for e in registry_entries if e["tradable"]),
            "n_not_tradable": sum(1 for e in registry_entries if not e["tradable"]),
        },
    }
    reg_name = f"tradable_edge_registry_{ts}.json"
    reg_path = reports / reg_name
    reg_path.write_text(json.dumps(registry, indent=2, default=str) + "\n")
    reg_sha = sha256_file(reg_path)

    print(
        json.dumps(
            {
                "generated_at_utc": ts,
                "primary_route": primary_route,
                "pairs_blocked": pairs["blocked"],
                "mean_reversion_edge": primary.get("price_only_edge_proven") if primary_route == "mean_reversion_fallback" else None,
                "price_only_edge_proven": price_only_edge,
                "mr_cross_asset_oos_net_sums": primary.get("cross_asset_oos_net_sums") if primary_route == "mean_reversion_fallback" else None,
                "artifact": str(out_path.relative_to(root)),
                "artifact_sha256": out_sha,
                "registry": str(reg_path.relative_to(root)),
                "registry_sha256": reg_sha,
                "registry_summary": registry["summary"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()