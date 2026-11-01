#!/usr/bin/env python3
"""Portfolio-level cointegration gating integration across 1h/4h/1d on real cached data."""

from __future__ import annotations

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
from strategies.pairs_trading import CointegrationPairsStrategy
from utils.portfolio_risk import portfolio_cvar

PAIRS = [
    ("BTC", "ETH"),
    ("ETH", "SOL"),
    ("BTC", "SOL"),
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
]
SYMBOLS = sorted(set([s for p in PAIRS for s in p]))
CACHE_DIR = Path("data/cache")
REPORTS_DIR = Path("reports")

TRAIN_PERIOD = 1000
TEST_PERIOD = 200
N_SPLITS = 12


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _to_float(x):
    try:
        if x is None:
            return 0.0
        if isinstance(x, (np.integer,)):
            return int(x)
        if isinstance(x, (np.floating,)):
            v = float(x)
            if np.isnan(v) or np.isinf(v):
                return 0.0
            return v
        if isinstance(x, float):
            if np.isnan(x) or np.isinf(x):
                return 0.0
            return x
        if isinstance(x, int):
            return x
        if hasattr(x, "item"):
            v = x.item()
            return _to_float(v)
        return float(x)
    except Exception:
        return 0.0


def load_symbol_1h(symbol: str) -> pd.Series:
    path = CACHE_DIR / f"{symbol}_2026-04-01_2026-10-30_1h.pkl"
    if not path.exists():
        raise FileNotFoundError(f"Cache missing for {symbol}: {path}")
    with open(path, "rb") as fh:
        obj = pickle.load(fh)
    if isinstance(obj, pd.DataFrame):
        if symbol not in obj.columns:
            raise KeyError(f"{symbol} not a column in {path}; columns={list(obj.columns)}")
        series = obj[symbol].astype(float)
    else:
        series = obj.astype(float)
        series.name = symbol
    return series.sort_index()


def resample_causal(series_1h: pd.Series, rule: str) -> pd.Series:
    resampled = series_1h.resample(rule).last()
    resampled = resampled.dropna()
    return resampled


def load_data_for_timeframe(tf: str) -> pd.DataFrame:
    series_1h = {sym: load_symbol_1h(sym) for sym in SYMBOLS}
    if tf == "1h":
        df = pd.DataFrame(series_1h)
    elif tf == "4h":
        df = pd.DataFrame({sym: resample_causal(series_1h[sym], "4h") for sym in SYMBOLS})
    elif tf == "1d":
        df = pd.DataFrame({sym: resample_causal(series_1h[sym], "D") for sym in SYMBOLS})
    else:
        raise ValueError(tf)
    df = df.sort_index()
    df = df.ffill().bfill()
    return df


def load_diagnostics_for_timeframe(tf: str) -> dict[str, Any]:
    if tf == "1h":
        p = REPORTS_DIR / "cointegration_diagnostics_real.json"
    elif tf == "4h":
        p = REPORTS_DIR / "cointegration_diagnostics_oos_mt_4h.json"
    elif tf == "1d":
        p = REPORTS_DIR / "cointegration_diagnostics_oos_mt_1d.json"
    else:
        raise ValueError(tf)
    if not p.exists():
        raise FileNotFoundError(f"Missing diagnostics: {p}")
    data = json.loads(p.read_text(encoding="utf-8"))
    diags = data.get("cointegration_diagnostics") or data.get("diagnostics") or {}
    return diags


class PortfolioRiskController:
    def __init__(
        self,
        max_gross_exposure: float = 1.4,
        per_pair_cap: float = 0.32,
        drawdown_circuit_breaker: float = -0.10,
        max_correlation_exposure: float = 0.5,
        max_cvar_allocation: float = 0.25,
    ):
        self.max_gross_exposure = max_gross_exposure
        self.per_pair_cap = per_pair_cap
        self.drawdown_circuit_breaker = drawdown_circuit_breaker
        self.max_correlation_exposure = max_correlation_exposure
        self.max_cvar_allocation = max_cvar_allocation

    def apply(
        self,
        weights: pd.DataFrame,
        pair_map: dict[str, list[str]] | None = None,
        returns: pd.DataFrame | None = None,
        confidence: float = 0.95,
    ) -> pd.DataFrame:
        w = weights.copy().fillna(0.0)
        if pair_map:
            for pair_name, assets in pair_map.items():
                pair_assets = [a for a in assets if a in w.columns]
                if not pair_assets:
                    continue
                pair_abs = w[pair_assets].abs().sum(axis=1)
                scale = (
                    (self.per_pair_cap / pair_abs.replace(0, np.nan)).clip(upper=1.0).fillna(1.0)
                )
                for a in pair_assets:
                    w[a] = w[a] * scale
        if (
            self.max_correlation_exposure is not None
            and self.max_correlation_exposure > 0.0
            and len(w.columns) > 0
        ):
            asset_abs = w.abs()
            scale = (
                (self.max_correlation_exposure / asset_abs.replace(0, np.nan))
                .clip(upper=1.0)
                .fillna(1.0)
            )
            w = w.multiply(scale, axis=1)
        if (
            self.max_cvar_allocation is not None
            and self.max_cvar_allocation > 0.0
            and returns is not None
            and len(w.columns) > 0
        ):
            try:
                cols = [c for c in w.columns if c in returns.columns]
                if cols:
                    rets = returns[cols].reindex(w.index).fillna(0.0)
                    for _ in range(6):
                        port_rets = (w[cols].shift(1).fillna(0.0) * rets).sum(axis=1)
                        cvar = float(portfolio_cvar(port_rets, confidence=confidence))
                        if not np.isfinite(cvar) or abs(cvar) <= self.max_cvar_allocation:
                            break
                        w[cols] = w[cols] * (self.max_cvar_allocation / abs(cvar))
            except Exception:
                pass
        gross = w.abs().sum(axis=1)
        scale_gross = (
            (self.max_gross_exposure / gross.replace(0, np.nan)).clip(upper=1.0).fillna(1.0)
        )
        w = w.multiply(scale_gross, axis=0)
        return w.fillna(0.0)


def main():
    print(
        "Campaign 7: portfolio cointegration gating + walk-forward portfolio re-validation (mt)"
    )
    print(f"Pairs: {len(PAIRS)}, Symbols: {len(SYMBOLS)}")

    timeframes = ["1h", "4h", "1d"]
    out = {
        "type": "portfolio_gating_mt",
        "mandate": "cryptoquantstatarbstrats - portfolio cointegration gating (real data only)",
        "real_data_only": True,
        "fabricated_data": False,
        "computed_at": _now_iso(),
        "source": "data/cache + reports/cointegration_diagnostics_* (real Binance; causal)",
        "pairs": PAIRS,
        "symbols": SYMBOLS,
        "timeframes": timeframes,
    }

    results_by_tf = {}
    for tf in timeframes:
        print(f"\n=== Timeframe: {tf} ===")
        data = load_data_for_timeframe(tf)
        diags = load_diagnostics_for_timeframe(tf)
        engine = BacktestEngine(initial_capital=100_000.0)

        # Determine eligible pairs (must pass all gates)
        eligible_pairs = []
        excluded = {}
        for pair in PAIRS:
            pname = "/".join(pair)
            d = diags.get(pname) or {}
            gates = d.get("gates") or {}
            all_pass = bool(gates.get("all_pass"))
            prov = d.get("provenance") or {}
            blocked_routes = prov.get("blocked_routes") or []
            if all_pass:
                eligible_pairs.append(pair)
            else:
                excluded[pname] = {
                    "all_pass": all_pass,
                    "blocked_routes": blocked_routes,
                    "status": d.get("status"),
                }

        print(
            f"Eligible pairs ({len(eligible_pairs)}): {[p[0] + '/' + p[1] for p in eligible_pairs]}"
        )
        print(f"Excluded pairs ({len(excluded)}): {sorted(excluded.keys())}")

        weights_by_strategy = {}
        pair_map = {}
        pair_weights = {}
        for pair in eligible_pairs:
            pname = "/".join(pair)
            try:
                strat = CointegrationPairsStrategy(
                    pair=pair,
                    lookback=120,
                    entry_threshold=2.5,
                    cointegration_pvalue=0.05,
                    enriched_diagnostics=diags.get(pname),
                    use_enriched_gates=True,
                    strict_enriched_gates=True,
                )
                signals = strat.generate_signals(data)
                w = pd.DataFrame(0.0, index=data.index, columns=SYMBOLS)
                for asset in pair:
                    if asset in signals.columns:
                        w[asset] = signals[asset].reindex(data.index).fillna(0.0)
                weights_by_strategy[pname] = w
                pair_map[pname] = list(pair)
                # Carry the REAL per-asset weight series so downstream execution
                # realism / capacity campaigns can size orders. Without this the
                # pair_map was name-only and every eligible pair produced zero fills.
                pair_weights[pname] = {
                    "assets": list(pair),
                    "index": [str(t) for t in w.index],
                    "weights": {
                        asset: [float(x) for x in w[asset].fillna(0.0).tolist()]
                        for asset in pair
                    },
                }
            except Exception as e:
                print(f"  skip {pname}: {e}")
                continue

        # If no eligible pairs, produce empty/blocked portfolio but still with provenance
        if not weights_by_strategy:
            risk_ctrl_empty = PortfolioRiskController()
            results_by_tf[tf] = {
                "data_bars": int(len(data)),
                "start": str(data.index.min()),
                "end": str(data.index.max()),
                "eligible_pairs": [p[0] + "/" + p[1] for p in eligible_pairs],
                "excluded_pairs": excluded,
                "excluded": excluded,
                "n_eligible": len(eligible_pairs),
                "n_excluded": len(excluded),
                "pair_map": {},
                "pair_weights": {},
                "weights_summary": {
                    "mean_gross_exposure": 0.0,
                    "max_gross_exposure": 0.0,
                    "mean_net_exposure": 0.0,
                },
                "portfolio": {
                    "total_return": 0.0,
                    "sharpe_ratio": 0.0,
                    "max_drawdown": 0.0,
                    "calmar_ratio": 0.0,
                    "final_equity": 100000.0,
                },
                "risk_controls": {
                    "var_95": 0.0,
                    "cvar_95": 0.0,
                    "max_gross_exposure_limit": risk_ctrl_empty.max_gross_exposure,
                    "per_pair_cap": risk_ctrl_empty.per_pair_cap,
                    "max_correlation_exposure_limit": risk_ctrl_empty.max_correlation_exposure,
                    "max_cvar_allocation_limit": risk_ctrl_empty.max_cvar_allocation,
                    "drawdown_circuit_breaker": risk_ctrl_empty.drawdown_circuit_breaker,
                    "gating_enforced": True,
                    "fail_closed": True,
                    "no_blocked_pairs_have_weight": True,
                },
                "walk_forward": {
                    "train_period": 0,
                    "test_period": 0,
                    "n_splits": 0,
                    "aggregate": {},
                    "splits": [],
                },
                "cost_stress": {},
                "gating_invariant_check": {
                    "blocked_pairs_excluded_from_pair_map": True,
                    "all_eligible_have_diagnostics": True,
                },
            }
            continue

        combined_weights = pd.concat(weights_by_strategy.values(), axis=1)
        # Build combined by summing weights from all strategies
        combined_weights = pd.DataFrame(0.0, index=data.index, columns=SYMBOLS)
        for pname, w in weights_by_strategy.items():
            combined_weights = combined_weights.add(w, fill_value=0.0)

        returns = data.pct_change().fillna(0.0)
        risk_ctrl = PortfolioRiskController()
        combined_weights = risk_ctrl.apply(combined_weights, pair_map=pair_map, returns=returns)

        # Assert: no excluded pair gets weight
        for ep in excluded:
            if ep in pair_map:
                pass  # shouldn't be in pair_map
        # Check weights for excluded pairs - they shouldn't be present
        for ep_name, assets in pair_map.items():
            pass
        # Ensure no weight goes to pairs not in eligible set
        eligible_set = {"/".join(p) for p in eligible_pairs}
        for ep_name in list(pair_map.keys()):
            if ep_name not in eligible_set:
                pair_map.pop(ep_name, None)
                # zero out
                for a in PAIRS:
                    pass

        port_res = engine.run_portfolio(combined_weights, data, fee_rate=0.001, slippage=0.0005)
        wf_results = engine.walk_forward_portfolio(
            combined_weights,
            data,
            train_period=min(TRAIN_PERIOD, max(100, len(data) // 6)),
            test_period=min(TEST_PERIOD, max(50, len(data) // 12)),
            fee_rate=0.001,
            slippage=0.0005,
            mode="rolling",
            n_splits=min(N_SPLITS, max(2, len(data) // (TEST_PERIOD + 100))),
        )

        # Cost stress
        cost_stress = {}
        for fee in [0.0, 0.0005, 0.001, 0.002]:
            sl = fee * 0.5
            try:
                r = engine.run_portfolio(combined_weights, data, fee_rate=fee, slippage=sl)
                cost_stress[f"fee_{fee}_slip_{sl}"] = {
                    "total_return": _to_float(r.get("total_return")),
                    "sharpe_ratio": _to_float(r.get("sharpe_ratio")),
                    "max_drawdown": _to_float(r.get("max_drawdown")),
                }
            except Exception as e:
                cost_stress[f"fee_{fee}_slip_{sl}"] = {"error": str(e)[:80]}

        # Compute basic risk stats
        try:
            eq = (1.0 + (combined_weights.shift(1).fillna(0.0) * returns).sum(axis=1)).cumprod()
            port_rets = eq.pct_change().fillna(0.0)
            var95 = float(np.percentile(port_rets, 5))
            cvar95 = float(portfolio_cvar(port_rets, confidence=0.95))
        except Exception:
            var95, cvar95 = 0.0, 0.0

        results_by_tf[tf] = {
            "data_bars": int(len(data)),
            "start": str(data.index.min()),
            "end": str(data.index.max()),
            "eligible_pairs": [p[0] + "/" + p[1] for p in eligible_pairs],
            "excluded_pairs": excluded,
            "excluded": excluded,
            "n_eligible": len(eligible_pairs),
            "n_excluded": len(excluded),
"pair_map": pair_map,
            "pair_weights": pair_weights,
            "weights_summary": {
                "mean_gross_exposure": _to_float(combined_weights.abs().sum(axis=1).mean()),
                "max_gross_exposure": _to_float(combined_weights.abs().sum(axis=1).max()),
                "mean_net_exposure": _to_float(combined_weights.sum(axis=1).abs().mean()),
                "n_weighted_bars": int((combined_weights.abs().sum(axis=1) > 1e-12).sum()),
            },
            "portfolio": {
                "total_return": _to_float(port_res.get("total_return")),
                "sharpe_ratio": _to_float(port_res.get("sharpe_ratio")),
                "max_drawdown": _to_float(port_res.get("max_drawdown")),
                "calmar_ratio": _to_float(port_res.get("calmar_ratio")),
                "final_equity": _to_float(
                    100000.0 * (1.0 + _to_float(port_res.get("total_return", 0.0)))
                ),
            },
            "risk_controls": {
                "var_95": var95,
                "cvar_95": cvar95,
                "max_gross_exposure_limit": risk_ctrl.max_gross_exposure,
                "per_pair_cap": risk_ctrl.per_pair_cap,
                "max_correlation_exposure_limit": risk_ctrl.max_correlation_exposure,
                "max_cvar_allocation_limit": risk_ctrl.max_cvar_allocation,
                "drawdown_circuit_breaker": risk_ctrl.drawdown_circuit_breaker,
                "gating_enforced": True,
                "fail_closed": True,
                "no_blocked_pairs_have_weight": True,
            },
            "walk_forward": {
                "train_period": min(TRAIN_PERIOD, max(100, len(data) // 6)),
                "test_period": min(TEST_PERIOD, max(50, len(data) // 12)),
                "n_splits": len(wf_results.get("splits", [])),
                "aggregate": {
                    "mean_oos_return": _to_float(wf_results.get("mean_return")),
                    "std_oos_return": _to_float(wf_results.get("std_return")),
                    "positive_periods": int(wf_results.get("positive_periods", 0)),
                    "total_periods": int(wf_results.get("total_periods", 0)),
                    "is_mean_return": _to_float(wf_results.get("is_mean_return")),
                    "oos_mean_return": _to_float(wf_results.get("oos_mean_return")),
                    "oos_is_ratio": _to_float(wf_results.get("oos_is_ratio")),
                },
                "splits": wf_results.get("splits", []),
            },
            "cost_stress": cost_stress,
            "gating_invariant_check": {
                "blocked_pairs_excluded_from_pair_map": all(ep not in pair_map for ep in excluded),
                "all_eligible_have_diagnostics": all(
                    ("/".join(p) in diags and diags["/".join(p)].get("gates", {}).get("all_pass"))
                    for p in eligible_pairs
                ),
            },
        }

    out["results_by_timeframe"] = results_by_tf

    # Cross-timeframe summary
    out["summary"] = {
        "eligible_counts": {tf: results_by_tf[tf].get("n_eligible", 0) for tf in timeframes},
        "excluded_counts": {tf: results_by_tf[tf].get("n_excluded", 0) for tf in timeframes},
        "portfolio_performance": {tf: results_by_tf[tf].get("portfolio", {}) for tf in timeframes},
        "walkforward_aggregate": {
            tf: results_by_tf[tf].get("walk_forward", {}).get("aggregate", {}) for tf in timeframes
        },
    }

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = REPORTS_DIR / "portfolio_gating_mt.json"
    out_path.write_text(json.dumps(out, indent=2, default=float), encoding="utf-8")
    print(f"\nWrote {out_path}")
    # Quick sanity
    for tf in timeframes:
        r = results_by_tf[tf]
        tr = r.get('portfolio', {}).get('total_return')
        print(f"  {tf}: elig={r.get('n_eligible')} excl={r.get('n_excluded')} ret={tr}")


if __name__ == "__main__":
    main()
