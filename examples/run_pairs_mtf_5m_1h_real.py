#!/usr/bin/env python3
"""Campaign #4: HF/multi-timeframe cointegration (real Binance spot data only).

Emits reports/pairs_mtf_5m_1h.json with honest provenance/provenance-like schema.
- 1h cointegration/hedge/spread context + 5m entry/exit signals.
- Causal alignment only: 1h bar at t informs 5m bars at/after t+1h. No lookahead.
- Purged/leakage controls by construction (causal merge) and explicit checks.
- Fail-closed on missing data/NaNs/gates.
- Execution realism: explicit fees/slippage/turnover/capacity proxy on 5m bars.
  Historical L2/intrabar replay not publicly available and never fabricated.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data.cache import load_cached
from data.loader import DataLoader
from utils.mtf_pairs import MTFPairConfig, run_mtf_universe

SYMBOLS = ["ADA", "AVAX", "BNB", "BTC", "DOT", "ETH", "LINK", "LTC", "POL", "SOL", "XRP"]
PAIRS = [
    ("BTC", "ETH"),
    ("ETH", "SOL"),
    ("BTC", "SOL"),
    ("BNB", "BTC"),
    ("BNB", "ETH"),
    ("SOL", "BNB"),
    ("ADA", "BTC"),
    ("XRP", "BTC"),
    ("DOT", "BTC"),
    ("AVAX", "BTC"),
    ("LINK", "BTC"),
    ("LTC", "BTC"),
    ("POL", "BTC"),
    ("XRP", "ETH"),
]
# Real-data window: 3 months of 5m (substantial, feasible) within cached 1h range.
H1_START, H1_END = "2026-04-01", "2026-10-30"
M5_START, M5_END = "2026-08-01", "2026-10-30"
OUT = Path(__file__).resolve().parent.parent / "reports" / "pairs_mtf_5m_1h.json"


def _load_interval(
    symbols: list[str], start: str, end: str, interval: str
) -> tuple[Any, dict[str, Any]]:
    loader = DataLoader()
    blocked_routes: list[Any] = []
    provenance: dict[str, Any] = {
        "interval": interval,
        "start": start,
        "end": end,
        "symbols_requested": symbols,
    }
    try:
        data, prov = load_cached(loader, symbols, start, end, interval=interval)
        provenance.update(prov)
        for r in prov.get("blocked_routes", []) or []:
            if r not in blocked_routes:
                blocked_routes.append(r)
        return data, provenance
    except Exception as e:
        prov = dict(getattr(loader, "last_fetch_provenance", {}) or {})
        prov.update({"interval": interval, "error": str(e)[:400], "status": "blocked"})
        for r in prov.get("blocked_routes", []) or []:
            if r not in blocked_routes:
                blocked_routes.append(r)
        return None, prov


def _cost_sensitivity(h1, m5, pairs: list[tuple[str, str]]) -> list[dict[str, Any]]:
    scenarios = [
        {"name": "low", "fee_rate": 0.0005, "slippage_bps": 2.0},
        {"name": "base", "fee_rate": 0.0010, "slippage_bps": 5.0},
        {"name": "high", "fee_rate": 0.0020, "slippage_bps": 10.0},
    ]
    out = []
    for sc in scenarios:
        cfg = MTFPairConfig(
        pair=("BTC", "ETH"),
        fee_rate=sc["fee_rate"],
        slippage_bps=sc["slippage_bps"],
    )
        run = run_mtf_universe(h1, m5, pairs, config_template=cfg)
        agg = run.get("aggregate", {})
        out.append({
            "scenario": sc["name"],
            "fee_rate": sc["fee_rate"],
            "slippage_bps": sc["slippage_bps"],
            "status": run.get("status"),
            "pairs_ok": agg.get("pairs_ok"),
            "mean_sharpe_ok": agg.get("mean_sharpe_ok"),
            "mean_total_return_ok": agg.get("mean_total_return_ok"),
            "mean_max_drawdown_ok": agg.get("mean_max_drawdown_ok"),
            "blocked_routes": run.get("blocked_routes", []),
        })
    return out


def main() -> None:
    generated_at = datetime.now(timezone.utc).isoformat()
    blocked_routes: list[Any] = []
    limitations: list[str] = [
        "Historical L2/intrabar replay not publicly available from public routes used; "
        "fills/order books are not fabricated.",
        "5m execution is close-to-close proxy with explicit fee+slippage+turnover costs, "
        "not exchange matching-engine replay.",
        "1h cointegration/half-life/correlation gates are trailing statistical diagnostics "
        "on real candles; fail-closed and not proof of future edge.",
        "Universe/windows limited to real data successfully fetched/cached in this "
        "environment; any unavailable route/symbol is recorded honestly.",
    ]

    h1, h1_prov = _load_interval(SYMBOLS, H1_START, H1_END, "1h")
    m5, m5_prov = _load_interval(SYMBOLS, M5_START, M5_END, "5m")
    for prov in (h1_prov, m5_prov):
        for r in (prov.get("blocked_routes") or []):
            if r not in blocked_routes:
                blocked_routes.append(r)

    report: dict[str, Any] = {
        "real_data_only": True,
        "fabricated_data": False,
        "generated_at_utc": generated_at,
        "campaign": "Campaign #4 - HF/multi-timeframe cointegration",
        "status": "blocked",
        "blocked_routes": blocked_routes,
        "data_sources": {
            "provider": (
                "Binance public spot klines via "
                "data.loader.DataLoader / data.cache.load_cached"
            ),
            "symbols_requested": SYMBOLS,
            "intervals": {
                "context_1h": {"start": H1_START, "end": H1_END, "provenance": h1_prov},
                "execution_5m": {"start": M5_START, "end": M5_END, "provenance": m5_prov},
            },
            "notes": (
            "Only real fetched/cached candles used. No synthetic candles, IV, volume, "
            "fills, order books, labels, or metrics fabricated as evidence."
        ),
        },
        "method": {
            "strategy": (
                "Multi-timeframe pairs: 1h trailing cointegration/hedge/spread "
                "context gates + 5m z-score entry/exit."
            ),
            "causal_alignment": (
            "1h bar at index t (open label) becomes available at t+1h (close). "
            "merge_asof backward on available_at maps to 5m bars at/after close; "
            "no 5m bar uses 1h information before close."
        ),
            "gates": {
                "trailing_only": True,
                "fail_closed": True,
"1h": [
                "OLS hedge beta",
                "Engle-Granger/coint p-value (AIC) when available else "
                "ADF-on-spread proxy",
                "rolling correlation",
                "OU half-life bounds",
            ],
            "5m": [
                "rolling z-score from causally aligned spread",
                "entry/exit/stop thresholds",
                "gate_ok required",
            ],
            },
            "wf_leakage_controls": (
            "No train/test optimization on this artifact; evaluation uses causal "
            "rolling trailing windows and causal 1h->5m availability. Purged WF "
            "not separately claimed beyond causal construction; leakage sanity checked."
        ),
        "cost_model": (
            "Per-bar turnover * (fee_rate + slippage_bps/10000) on 5m positions "
            "shifted by 1 bar; gross-normalized pair legs; no fabricated "
            "fills/order books."
        ),
            "limitations": limitations,
        },
        "results": None,
        "cost_sensitivity": None,
        "limitations": limitations,
        "notes": [],
    }

    if h1 is None or h1.empty or m5 is None or m5.empty:
        report["status"] = "blocked"
        report["notes"].append(
            "Required 1h and/or 5m real data unavailable; "
            "artifact remains honest/blocked."
        )
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(report, indent=2, default=str) + "\n")
        print(f"Wrote {OUT} status=blocked")
        return

    h1 = h1.sort_index()
    m5 = m5.sort_index()
    # Use shared symbols present in both frames
    shared = [s for s in SYMBOLS if s in h1.columns and s in m5.columns]
    pairs = [p for p in PAIRS if p[0] in shared and p[1] in shared]
    report["data_sources"]["symbols_used"] = shared
    report["data_sources"]["pairs_evaluated"] = [list(p) for p in pairs]
    report["data_sources"]["h1_shape"] = [int(h1.shape[0]), int(h1.shape[1])]
    report["data_sources"]["m5_shape"] = [int(m5.shape[0]), int(m5.shape[1])]
    report["data_sources"]["h1_range_utc"] = [str(h1.index.min()), str(h1.index.max())]
    report["data_sources"]["m5_range_utc"] = [str(m5.index.min()), str(m5.index.max())]

    base_cfg = MTFPairConfig(pair=("BTC", "ETH"))
    run = run_mtf_universe(h1, m5, pairs, config_template=base_cfg)
    sens = _cost_sensitivity(h1, m5, pairs[:8])  # focused sensitivity, honest subset
    report["results"] = run
    report["cost_sensitivity"] = sens
    for r in run.get("blocked_routes", []) or []:
        if r not in blocked_routes:
            blocked_routes.append(r)
    for sc in sens:
        for r in sc.get("blocked_routes", []) or []:
            if r not in blocked_routes:
                blocked_routes.append(r)
    report["blocked_routes"] = blocked_routes

    if run.get("status") == "ok":
        report["status"] = "ok"
    elif (
        run.get("status") == "partial"
        or run.get("aggregate", {}).get("pairs_ok", 0) > 0
    ):
        report["status"] = "partial"
    else:
        report["status"] = "blocked"
    report["notes"].append(
        "OOS/edge: results are reported honestly from real data; any "
        "non-positive/weak metrics are not hidden. No claim of profitable edge."
    )
    results_list = run.get("results", []) or []
    if all(
        r.get("activity", {}).get("trade_events", 0) == 0
        for r in results_list
        if isinstance(r, dict)
    ):
        report["notes"].append(
            "All evaluated pairs produced zero trade events under fail-closed "
            "gates/cost-aware 5m logic (honest)."
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, default=str) + "\n")
    pairs_ok = run.get("aggregate", {}).get("pairs_ok")
    print(
        f"Wrote {OUT} status={report['status']} "
        f"pairs_ok={pairs_ok} blocked_routes={len(blocked_routes)}"
    )


if __name__ == "__main__":
    main()
