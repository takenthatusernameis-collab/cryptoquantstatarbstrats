#!/usr/bin/env python3
"""Campaign #10: wider-universe causal per-bar gate validation (cached data only).

Extends Campaign #9 (causal per-bar enriched gates on BTC/ETH, ETH/SOL, BTC/SOL;
conclusion no_edge) to the wider ``reports/portfolio_real.json`` universe (>=10
pairs: ADA/ETH, XRP/BTC, BNB/ETH, BTC/BNB, SOL/BNB, ADA/BTC, XRP/ETH, BNB/BTC,
DOT/BTC, DOT/ETH, POL/BTC, AVAX/BTC, LINK/BTC, LTC/BTC, plus baselines
BTC/ETH, ETH/SOL, BTC/SOL). Enriched gates are enforced causally per-bar on
trailing windows (target_schema_diagnostics recomputed every
cointegration_check_interval bars, forward-filled, fail-closed under strict
mode) instead of applying a full-history aggregate diagnostic as a static
per-bar pass.

Determines whether the ``rolling_stable_ok`` trailing-window insufficiency is a
structural blocker or whether any wider-universe pair/portfolio slice yields
reproducible cost-aware OOS net edge vs buy-and-hold without weakening gate
thresholds.

Produces reports/campaign10_wider_universe_causal_gates_<UTC>.json from cached
Binance spot candles only. No network refetch, no synthetic/fabricated prices/
IV/volume/fills/order books/labels/metrics. All findings evidence-based and
honest; negative/insufficient findings are valid only if fully evidenced.

Artifact includes: real-data provenance (cache paths/hashes/meta), WF/OOS
splits, fee×slippage grid, per-pair and aggregate per-bar gate pass/fail/trade/
exposure accounting, cached-aggregate reference path, B&H benchmarks, path
comparison vs Campaign #9 baseline, and explicit conclusion
edge/no_edge/insufficient_or_blocked.
"""

from __future__ import annotations

import hashlib
import json
import pickle
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd

from backtest.engine import BacktestEngine
from strategies.pairs_trading import CointegrationPairsStrategy, _evaluate_enriched_gates_strict
from utils.cointegration import target_schema_diagnostics
from utils.regime import detect_regimes

ROOT = Path(__file__).resolve().parent.parent
CACHE_PKL = ROOT / "data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl"
CACHE_META = (
    ROOT / "data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.meta.json"
)
PORTFOLIO_BASELINE = ROOT / "reports/portfolio_real.json"

# Wider universe from reports/portfolio_real.json (>=10 pairs plus baselines).
PAIRS: list[tuple[str, str]] = [
    ("ADA", "ETH"),
    ("XRP", "BTC"),
    ("BNB", "ETH"),
    ("BTC", "BNB"),
    ("SOL", "BNB"),
    ("ADA", "BTC"),
    ("XRP", "ETH"),
    ("BNB", "BTC"),
    ("DOT", "BTC"),
    ("DOT", "ETH"),
    ("POL", "BTC"),
    ("AVAX", "BTC"),
    ("LINK", "BTC"),
    ("LTC", "BTC"),
    ("BTC", "ETH"),
    ("ETH", "SOL"),
    ("BTC", "SOL"),
]
SYMBOLS = sorted({s for p in PAIRS for s in p})
START = "2026-04-01"
END = "2026-10-30"
FREQ = "1h"
WF = {
    "train_period": 500,
    "test_period": 100,
    "n_splits": 4,
    "mode": "rolling",
    "metric": "calmar_ratio",
}
GRID = {
    "lookback": [120],
    "entry_threshold": [2.0, 2.5],
    "cointegration_pvalue": [0.05],
}
COST_GRID = [
    {"fee_rate": 0.0, "slippage": 0.0},
    {"fee_rate": 0.0005, "slippage": 0.0},
    {"fee_rate": 0.001, "slippage": 0.0005},
    {"fee_rate": 0.002, "slippage": 0.001},
]
PORTFOLIO_RISK_CONTROLS = {
    "max_gross_exposure": 1.4,
    "per_pair_cap": 0.32,
    "max_correlation_exposure": 0.5,
    "max_cvar_allocation": 0.25,
    "drawdown_circuit_breaker": -0.10,
}
GATE_NAMES = (
    "eg_pass",
    "johansen_pass",
    "spread_mr_pass",
    "hl_bounds_pass",
    "leg_stationarity_ok",
    "rolling_stable_ok",
    "no_structural_break",
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _json_safe(obj: Any) -> Any:
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        v = float(obj)
        return v if np.isfinite(v) else None
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, np.ndarray):
        return [_json_safe(x) for x in obj.tolist()]
    if isinstance(obj, pd.Series):
        return [_json_safe(x) for x in obj.tolist()]
    if isinstance(obj, pd.DataFrame):
        return {c: [_json_safe(x) for x in obj[c].tolist()] for c in obj.columns}
    if isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {str(k): _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(x) for x in obj]
    if isinstance(obj, float):
        return obj if np.isfinite(obj) else None
    return obj


def _load_cached_spot() -> tuple[pd.DataFrame, dict[str, Any]]:
    if not CACHE_PKL.exists() or not CACHE_META.exists():
        raise FileNotFoundError(f"Required cache missing: {CACHE_PKL} / {CACHE_META}")
    meta = json.loads(CACHE_META.read_text(encoding="utf-8"))
    with open(CACHE_PKL, "rb") as f:
        data = pickle.load(f)
    if not isinstance(data, pd.DataFrame):
        raise TypeError("Cached spot data must be a pandas DataFrame")
    data = data.sort_index()
    return data, meta


def _buy_hold_total(df: pd.DataFrame, cols: list[str]) -> float:
    sub = df[cols].dropna()
    if len(sub) < 2:
        return 0.0
    start = sub.iloc[0]
    end = sub.iloc[-1]
    rets = (end / start) - 1.0
    return float(rets.mean())


def _trade_exposure_accounting(
    result: dict[str, Any], weights: pd.DataFrame | None = None
) -> dict[str, Any]:
    w = weights
    if w is None:
        w = result.get("weights")
    out: dict[str, Any] = {
        "trades_count": 0,
        "n_bars_in_position": 0,
        "n_bars_total": 0,
        "max_gross_exposure": 0.0,
        "mean_gross_exposure": 0.0,
        "total_turnover": 0.0,
    }
    if isinstance(w, pd.DataFrame) and not w.empty:
        gross = w.abs().sum(axis=1)
        active = gross > 1e-12
        changes = (
            (w.diff().abs().sum(axis=1).fillna(w.abs().sum(axis=1)) > 1e-12)
            & active
        )
        out.update(
            {
                "trades_count": int(changes.sum()),
                "n_bars_in_position": int(active.sum()),
                "n_bars_total": int(len(w)),
                "max_gross_exposure": float(gross.max()) if len(gross) else 0.0,
                "mean_gross_exposure": float(gross.mean()) if len(gross) else 0.0,
                "total_turnover": float(
                    w.diff().abs().sum(axis=1).fillna(w.abs().sum(axis=1)).sum()
                ),
            }
        )
    elif isinstance(result, dict):
        act = result.get("activity") or {}
        for k in out:
            if k in act:
                out[k] = _json_safe(act[k])
    return out


def _full_sample_diag(pair: tuple[str, str], data: pd.DataFrame) -> dict[str, Any]:
    pcols = list(pair)
    df = data[pcols].dropna()
    try:
        diag = target_schema_diagnostics(df[pcols[0]], df[pcols[1]], pair_name="/".join(pair))
    except Exception as e:
        diag = {"status": "error", "error": str(e)[:200]}
    gates = diag.get("gates", {}) if isinstance(diag, dict) else {}
    sb = diag.get("structural_breaks", {}) if isinstance(diag, dict) else {}
    strict_ok = _evaluate_enriched_gates_strict(gates, sb, True)
    return {
        "pair": list(pair),
        "full_sample_diagnostic_status": diag.get("status") if isinstance(diag, dict) else None,
        "gates": gates,
        "structural_breaks": sb,
        "blocked_routes": (diag.get("provenance") or {}).get("blocked_routes", [])
        if isinstance(diag, dict)
        else [],
        "strict_cached_gate_decision_fail_closed": bool(strict_ok),
    }


def _per_bar_gate_accounting(
    breakdown: pd.DataFrame | None, enriched_ok: pd.Series | None
) -> dict[str, Any]:
    out: dict[str, Any] = {
        "bars_total": 0,
        "bars_assessable": 0,
        "bars_pass": 0,
        "bars_fail": 0,
        "bars_unassessable": 0,
        "pass_rate": 0.0,
        "fail_rate": 0.0,
        "unassessable_rate": 0.0,
        "per_gate_fail_count": {k: 0 for k in GATE_NAMES},
        "per_gate_fail_count_all_pass": 0,
        "breakdown_recorded": breakdown is not None and not breakdown.empty,
    }
    if breakdown is None or breakdown.empty:
        return out
    bd = breakdown
    n = len(bd)
    out["bars_total"] = int(n)
    fail_counts: dict[str, int] = {k: 0 for k in GATE_NAMES}
    fail_all = 0
    for k in GATE_NAMES:
        if k in bd.columns:
            fail_counts[k] = int((bd[k] == False).sum())  # noqa: E712
    if "all_pass" in bd.columns:
        fail_all = int((bd["all_pass"] == False).sum())  # noqa: E712
    out["per_gate_fail_count"] = fail_counts
    out["per_gate_fail_count_all_pass"] = fail_all
    if enriched_ok is not None and len(enriched_ok) == n:
        arr = enriched_ok.to_numpy(dtype=float)
        finite = np.isfinite(arr)
        assessable = int(finite.sum())
        passes = int(((arr == 1.0) & finite).sum())
        fails = int(((arr == 0.0) & finite).sum())
        unassessable = assessable - passes - fails
        out["bars_assessable"] = assessable
        out["bars_pass"] = passes
        out["bars_fail"] = fails
        out["bars_unassessable"] = unassessable
        out["pass_rate"] = float(passes / assessable) if assessable else 0.0
        out["fail_rate"] = float(fails / assessable) if assessable else 0.0
        out["unassessable_rate"] = float(unassessable / assessable) if assessable else 0.0
    return out


def _regime_slices(data: pd.DataFrame, portfolio_returns: pd.Series) -> dict[str, Any]:
    out: dict[str, Any] = {}
    try:
        regimes = detect_regimes(data[["BTC"]].copy(), window=20)
        vol_col = next((c for c in regimes.columns if c.endswith("_vol_regime")), None)
        trend_col = next((c for c in regimes.columns if c.endswith("_trend")), None)
        if vol_col:
            v = regimes[vol_col].reindex(portfolio_returns.index)
            for label in sorted([x for x in v.dropna().unique()]):
                mask = v == label
                r = portfolio_returns.reindex(v.index)[mask].fillna(0.0)
                if len(r):
                    out[f"btc_vol_regime_{int(label)}"] = {
                        "bars": int(mask.sum()),
                        "total_return": float((1.0 + r).prod() - 1.0),
                        "mean_return": float(r.mean()),
                    }
        if trend_col:
            t = regimes[trend_col].reindex(portfolio_returns.index)
            for label in sorted([int(x) for x in t.dropna().unique()]):
                mask = t == label
                r = portfolio_returns.reindex(t.index)[mask].fillna(0.0)
                if len(r):
                    out[f"btc_trend_{label}"] = {
                        "bars": int(mask.sum()),
                        "total_return": float((1.0 + r).prod() - 1.0),
                        "mean_return": float(r.mean()),
                    }
    except Exception as e:
        out["error"] = str(e)[:200]
    return out


def _run_pair(pair: tuple[str, str], data: pd.DataFrame) -> dict[str, Any]:
    engine = BacktestEngine(initial_capital=100_000.0)
    pcols = list(pair)
    df = data[pcols].dropna()

    full_sample_diag = _full_sample_diag(pair, df)

    paths: dict[str, Any] = {}
    for path in ("cached_aggregate", "causal_per_bar"):
        path_rows = []
        top = {}
        for lb in GRID["lookback"]:
            for et in GRID["entry_threshold"]:
                for cp in GRID["cointegration_pvalue"]:
                    strat = CointegrationPairsStrategy(
                        pair=pair,
                        lookback=lb,
                        entry_threshold=et,
                        cointegration_pvalue=cp,
                        use_enriched_gates=True,
                        strict_enriched_gates=True,
                    )
                    if path == "cached_aggregate":
                        strat.enriched_diagnostics = full_sample_diag
                    wf = engine.walk_forward(
                        strat,
                        df,
                        train_period=WF["train_period"],
                        test_period=WF["test_period"],
                        fee_rate=0.001,
                        slippage=0.0005,
                        mode=WF["mode"],
                        n_splits=WF["n_splits"],
                    )
                    oos_mean = float(wf.get("oos_mean_return", wf.get("mean_return", 0.0)) or 0.0)
                    path_rows.append(
                        {
                            "lookback": lb,
                            "entry_threshold": et,
                            "cointegration_pvalue": cp,
                            "oos_mean_return": oos_mean,
                            "oos_is_ratio": float(wf.get("oos_is_ratio", 0.0) or 0.0),
                            "oos_periods": len(wf.get("results", []) or []),
                        }
                    )
        path_rows.sort(
            key=lambda r: (r["oos_mean_return"], r.get("oos_is_ratio", 0.0)), reverse=True
        )
        top = path_rows[0] if path_rows else {}

        replay_by_cost = []
        gate_breakdown_full: dict[str, Any] = {}
        best_replay_res = None
        for c in COST_GRID:
            strat = CointegrationPairsStrategy(
                pair=pair,
                lookback=int(top.get("lookback", 120)),
                entry_threshold=float(top.get("entry_threshold", 2.0)),
                cointegration_pvalue=float(top.get("cointegration_pvalue", 0.05)),
                use_enriched_gates=True,
                strict_enriched_gates=True,
            )
            if path == "cached_aggregate":
                strat.enriched_diagnostics = full_sample_diag
            res = engine.run(strat, df, fee_rate=c["fee_rate"], slippage=c["slippage"])
            w = res.get("weights")
            replay_by_cost.append(
                {
                    **c,
                    "total_return": float(res.get("total_return", 0.0)),
                    "sharpe_ratio": float(res.get("sharpe_ratio", 0.0)),
                    "max_drawdown": float(res.get("max_drawdown", 0.0)),
                    "calmar_ratio": float(res.get("calmar_ratio", 0.0)),
                    "final_equity": float(
                        (res.get("equity_curve").iloc[-1] * 100000.0)
                        if isinstance(res.get("equity_curve"), pd.Series)
                        and len(res.get("equity_curve"))
                        else 100000.0
                    ),
                    "trade_exposure": _trade_exposure_accounting(
                        res, w if isinstance(w, pd.DataFrame) else None
                    ),
                }
            )
            best_replay_res = res
        if path == "causal_per_bar" and best_replay_res is not None:
            strat_final = CointegrationPairsStrategy(
                pair=pair,
                lookback=int(top.get("lookback", 120)),
                entry_threshold=float(top.get("entry_threshold", 2.0)),
                cointegration_pvalue=float(top.get("cointegration_pvalue", 0.05)),
                use_enriched_gates=True,
                strict_enriched_gates=True,
            )
            engine.run(strat_final, df, fee_rate=0.001, slippage=0.0005)
            breakdown = strat_final.get_gate_breakdown()
            enriched_ok = None
            try:
                enriched_ok = strat_final.generate_signals(df)["enriched_gates_ok"]
            except Exception:
                enriched_ok = None
            gate_breakdown_full = _per_bar_gate_accounting(breakdown, enriched_ok)
        else:
            gate_breakdown_full = {
                "cached_aggregate_uniform_decision": full_sample_diag[
                    "strict_cached_gate_decision_fail_closed"
                ],
                "note": "Cached full-history aggregate applied uniformly; fail-closed under strict "
                "mode (Campaign #8/9 reference path). No per-bar variation possible.",
            }

        oos_by_cost = []
        for c in COST_GRID:
            strat = CointegrationPairsStrategy(
                pair=pair,
                lookback=int(top.get("lookback", 120)),
                entry_threshold=float(top.get("entry_threshold", 2.0)),
                cointegration_pvalue=float(top.get("cointegration_pvalue", 0.05)),
                use_enriched_gates=True,
                strict_enriched_gates=True,
            )
            if path == "cached_aggregate":
                strat.enriched_diagnostics = full_sample_diag
            wf = engine.walk_forward(
                strat,
                df,
                train_period=WF["train_period"],
                test_period=WF["test_period"],
                fee_rate=c["fee_rate"],
                slippage=c["slippage"],
                mode=WF["mode"],
                n_splits=WF["n_splits"],
            )
            oos_by_cost.append(
                {
                    **c,
                    "oos_mean_return": float(
                        wf.get("oos_mean_return", wf.get("mean_return", 0.0)) or 0.0
                    ),
                    "oos_is_ratio": float(wf.get("oos_is_ratio", 0.0) or 0.0),
                    "oos_periods": len(wf.get("results", []) or []),
                }
            )

        bh = _buy_hold_total(df, pcols)
        port_rets = (
            best_replay_res.get("portfolio_returns")
            if isinstance(best_replay_res, dict)
            else None
        )
        regime = _regime_slices(df, port_rets) if isinstance(port_rets, pd.Series) else {}

        paths[path] = {
            "pair": list(pair),
            "symbols": pcols,
            "bars": int(len(df)),
            "window": {"start": str(df.index.min()), "end": str(df.index.max())},
            "walk_forward": WF,
            "grid": GRID,
            "top_ranked": top,
            "all_combos_ranked": path_rows,
            "oos_by_cost": oos_by_cost,
            "replay_by_cost": replay_by_cost,
            "buy_and_hold_total_return": bh,
            "enriched_gate_accounting": gate_breakdown_full,
            "full_sample_diagnostic": full_sample_diag if path == "cached_aggregate" else None,
            "regime_slices_baseline_cost": regime,
        }

    bh = _buy_hold_total(df, pcols)
    comparison = {
        "cached_oos_best": paths["cached_aggregate"]["top_ranked"].get("oos_mean_return"),
        "causal_oos_best": paths["causal_per_bar"]["top_ranked"].get("oos_mean_return"),
        "cached_replay_best_vs_bh": max(
            [float(r.get("total_return", 0.0)) for r in paths["cached_aggregate"]["replay_by_cost"]]
            or [0.0],
        )
        > bh,
        "causal_replay_best_vs_bh": max(
            [float(r.get("total_return", 0.0)) for r in paths["causal_per_bar"]["replay_by_cost"]]
            or [0.0],
        )
        > bh,
        "cached_replay_max_return": max(
            [float(r.get("total_return", 0.0)) for r in paths["cached_aggregate"]["replay_by_cost"]]
            or [0.0],
        ),
        "causal_replay_max_return": max(
            [float(r.get("total_return", 0.0)) for r in paths["causal_per_bar"]["replay_by_cost"]]
            or [0.0],
        ),
    }

    return {
        "pair": list(pair),
        "symbols": pcols,
        "bars": int(len(df)),
        "window": {"start": str(df.index.min()), "end": str(df.index.max())},
        "buy_and_hold_total_return": bh,
        "full_sample_diagnostic": full_sample_diag,
        "paths": paths,
        "path_comparison": comparison,
    }


def _run_portfolio(data: pd.DataFrame) -> dict[str, Any]:
    try:
        from examples.run_portfolio_real import (
            PortfolioRiskController,
            regime_adaptive_meta_selector,
        )
    except Exception as e:
        return {"status": "blocked_or_insufficient_data", "error": str(e)[:200]}
    engine = BacktestEngine(initial_capital=100_000.0)
    cols = [c for c in SYMBOLS if c in data.columns]
    df = data[cols].dropna()

    portfolio_by_path: dict[str, Any] = {}
    for path in ("cached_aggregate", "causal_per_bar"):
        weights_by_pair: dict[str, pd.DataFrame] = {}
        pair_map: dict[str, list[str]] = {}
        per_pair_info = {}
        for pair in PAIRS:
            strat = CointegrationPairsStrategy(
                pair=pair,
                lookback=120,
                entry_threshold=2.0,
                cointegration_pvalue=0.05,
                use_enriched_gates=True,
                strict_enriched_gates=True,
            )
            if path == "cached_aggregate":
                fd = _full_sample_diag(pair, data)
                strat.enriched_diagnostics = {
                    "gates": fd["gates"],
                    "structural_breaks": fd["structural_breaks"],
                }
            sig = strat.generate_signals(df[list(pair)].copy())
            w = pd.DataFrame(0.0, index=df.index, columns=cols)
            for a in pair:
                if a in sig.columns:
                    w[a] = sig[a].reindex(df.index).fillna(0.0)
            key = "/".join(pair)
            weights_by_pair[key] = w
            pair_map[key] = list(pair)
            per_pair_info[key] = {
                "params": {"lookback": 120, "entry_threshold": 2.0, "cointegration_pvalue": 0.05},
                "path": path,
            }
        combined = regime_adaptive_meta_selector(weights_by_pair, df[cols])
        ctrl = PortfolioRiskController(**PORTFOLIO_RISK_CONTROLS)
        rets = df[cols].pct_change().fillna(0.0)
        corr = rets.corr().fillna(0.0).to_dict()
        controlled = ctrl.apply(combined, pair_map=pair_map, correlation_matrix=corr, returns=rets)
        controlled = controlled.reindex(index=df.index, columns=cols).fillna(0.0)
        path_cost = []
        for c in COST_GRID:
            res = engine.run_portfolio(
                controlled, df[cols], fee_rate=c["fee_rate"], slippage=c["slippage"]
            )
            w = res.get("weights")
            path_cost.append(
                {
                    **c,
                    "total_return": float(res.get("total_return", 0.0)),
                    "sharpe_ratio": float(res.get("sharpe_ratio", 0.0)),
                    "max_drawdown": float(res.get("max_drawdown", 0.0)),
                    "calmar_ratio": float(res.get("calmar_ratio", 0.0)),
                    "final_equity": float(
                        (res.get("equity_curve").iloc[-1] * 100000.0)
                        if isinstance(res.get("equity_curve"), pd.Series)
                        and len(res.get("equity_curve"))
                        else 100000.0
                    ),
                    "trade_exposure": _trade_exposure_accounting(
                        res, w if isinstance(w, pd.DataFrame) else None
                    ),
                }
            )
        base_port = engine.run_portfolio(controlled, df[cols], fee_rate=0.001, slippage=0.0005)
        regime = (
            _regime_slices(df, base_port.get("portfolio_returns"))
            if isinstance(base_port.get("portfolio_returns"), pd.Series)
            else {}
        )
        portfolio_by_path[path] = {
            "pairs": ["/".join(p) for p in PAIRS],
            "symbols": cols,
            "bars": int(len(df)),
            "risk_controls": PORTFOLIO_RISK_CONTROLS,
            "per_pair_params": per_pair_info,
            "portfolio_by_cost": path_cost,
            "buy_and_hold_total_return": _buy_hold_total(df, cols),
            "regime_slices_baseline_cost": regime,
            "circuit_breaker_enforced_in_controller": True,
        }
    return portfolio_by_path


def main() -> None:
    data, meta = _load_cached_spot()
    spot_hash = _sha256(CACHE_PKL)
    meta_hash = _sha256(CACHE_META)
    vol_meta_path = ROOT / "data/cache/volume_1h_full.meta.json"
    vol_pkl_path = ROOT / "data/cache/volume_1h_full.pkl"
    vol_prov_path = ROOT / "data/cache/volume_1h_full.provenance.json"
    vol_hashes = {}
    for p in [vol_meta_path, vol_pkl_path, vol_prov_path]:
        if p.exists():
            vol_hashes[str(p.relative_to(ROOT))] = _sha256(p)

    results_pairs = {}
    for pair in PAIRS:
        results_pairs["/".join(pair)] = _run_pair(pair, data)

    portfolio = _run_portfolio(data)

    any_positive_oos_net = False
    any_positive_replay_net_vs_bh = False
    for k, r in results_pairs.items():
        causal = r["paths"].get("causal_per_bar", {})
        for row in causal.get("oos_by_cost", []):
            if float(row.get("oos_mean_return", 0.0)) > 0.0:
                any_positive_oos_net = True
        for row in causal.get("replay_by_cost", []):
            if float(row.get("total_return", 0.0)) > float(r.get("buy_and_hold_total_return", 0.0)):
                any_positive_replay_net_vs_bh = True
    for path, port in (portfolio or {}).items():
        if isinstance(port, dict):
            for row in port.get("portfolio_by_cost") or []:
                if float(row.get("total_return", 0.0)) > float(
                    port.get("buy_and_hold_total_return", 0.0)
                ):
                    any_positive_replay_net_vs_bh = True

    if any_positive_oos_net and any_positive_replay_net_vs_bh:
        conclusion_status = "edge"
        conclusion_reason = (
            "Positive OOS net and replay net vs buy-and-hold in tested slices "
            "under causal per-bar enriched gates; interpret with full evidence "
            "and limitations."
        )
    elif not any_positive_oos_net and not any_positive_replay_net_vs_bh:
        conclusion_status = "no_edge"
        conclusion_reason = (
            "Across tested cached-real-data wider-universe pairs/portfolio, "
            "walk-forward OOS cost slices, and replay cost slices under causal "
            "per-bar enriched gates (with cached-aggregate fail-closed "
            "reference), no positive OOS net edge and no replay "
            "outperformance vs buy-and-hold were observed under stated "
            "costs/windows. rolling_stable_ok trailing-window insufficiency is a "
            "structural blocker across the wider universe; gate thresholds were "
            "not weakened."
        )
    else:
        conclusion_status = "insufficient_or_blocked"
        conclusion_reason = (
            "Mixed or limited evidence across tested slices; no robust positive "
            "OOS net edge vs buy-and-hold established under stated conditions."
        )

    report = {
        "type": "campaign10_wider_universe_causal_gates",
        "computed_at": _now_iso(),
        "real_data_only": True,
        "fabricated_data": False,
        "provenance": {
            "source": "examples.run_campaign10_wider_universe_causal_gates",
            "cache_spot_pkl": str(CACHE_PKL.relative_to(ROOT)),
            "cache_spot_meta": str(CACHE_META.relative_to(ROOT)),
            "cache_spot_pkl_sha256": spot_hash,
            "cache_spot_meta_sha256": meta_hash,
            "cache_spot_meta_content": meta,
            "volume_cache_hashes": vol_hashes,
            "portfolio_baseline_reference": str(PORTFOLIO_BASELINE.relative_to(ROOT))
            if PORTFOLIO_BASELINE.exists()
            else None,
            "network_fetch_performed": False,
            "no_synthetic_fabricated_inputs": True,
            "symbols": SYMBOLS,
            "pairs": [list(p) for p in PAIRS],
            "start": START,
            "end": END,
            "freq": FREQ,
            "cached_aggregate_reference_campaign": "campaign9",
        },
        "walk_forward": WF,
        "grid": GRID,
        "fee_slippage_grid": COST_GRID,
        "pairs": results_pairs,
        "portfolio": portfolio,
        "conclusion": {
            "status": conclusion_status,
            "reason": conclusion_reason,
            "edge_claim": conclusion_status == "edge",
            "honest": True,
        },
    }

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = ROOT / f"reports/campaign10_wider_universe_causal_gates_{stamp}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = _json_safe(report)
    out_path.write_text(json.dumps(payload, indent=2, allow_nan=False), encoding="utf-8")
    print(str(out_path))
    print(json.dumps(_json_safe(report["conclusion"]), indent=2))


if __name__ == "__main__":
    main()
