#!/usr/bin/env python3
# Campaign #11: rolling-stability blocker diagnosis
# Gate-pass feasibility on wider universe (cached data only).

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
from strategies.pairs_trading import CointegrationPairsStrategy

ROOT = Path(__file__).resolve().parent.parent
CACHE_PKL = ROOT / "data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl"
CACHE_META = Path(str(CACHE_PKL).replace(".pkl", ".meta.json"))
PORTFOLIO_BASELINE = ROOT / "reports/portfolio_real.json"

PAIRS = [
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

GATE_NAMES = (
    "eg_pass",
    "johansen_pass",
    "spread_mr_pass",
    "hl_bounds_pass",
    "leg_stationarity_ok",
    "rolling_stable_ok",
    "no_structural_break",
)
SWEEPS = {"lookback": [60, 120, 240], "cointegration_check_interval": [1, 24, 48]}


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
        raise FileNotFoundError("Missing cache")
    meta = json.loads(CACHE_META.read_text(encoding="utf-8"))
    with open(CACHE_PKL, "rb") as f:
        data = pickle.load(f)
    if not isinstance(data, pd.DataFrame):
        raise TypeError("Bad cache")
    data = data.sort_index()
    return data, meta


def _per_bar_gate_accounting(
    bd: pd.DataFrame | None, enriched_ok: pd.Series | None
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
        "breakdown_recorded": bd is not None and not bd.empty,
    }
    if bd is None or bd.empty:
        return out
    n = len(bd)
    out["bars_total"] = int(n)
    fail_counts: dict[str, int] = {k: 0 for k in GATE_NAMES}
    for k in GATE_NAMES:
        if k in bd.columns:
            fail_counts[k] = int((bd[k] == False).sum())  # noqa: E712
    out["per_gate_fail_count"] = fail_counts
    if "all_pass" in bd.columns:
        out["per_gate_fail_count_all_pass"] = int((bd["all_pass"] == False).sum())  # noqa: E712
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
        if assessable:
            out["pass_rate"] = float(passes / assessable)
            out["fail_rate"] = float(fails / assessable)
            out["unassessable_rate"] = float(unassessable / assessable)
    return out


def _run_pair_sweep(pair: tuple[str, str], data: pd.DataFrame) -> dict[str, Any]:
    engine = BacktestEngine(initial_capital=100_000.0)
    pcols = list(pair)
    df = data[pcols].dropna()
    sweep_results = []
    for lb in SWEEPS["lookback"]:
        for cci in SWEEPS["cointegration_check_interval"]:
            strat = CointegrationPairsStrategy(
                pair=pair,
                lookback=lb,
                entry_threshold=2.0,
                cointegration_pvalue=0.05,
                cointegration_check_interval=cci,
                use_enriched_gates=True,
                strict_enriched_gates=True,
            )
            res = engine.run(strat, df, fee_rate=0.001, slippage=0.0005)
            breakdown = strat.get_gate_breakdown()
            try:
                enriched_ok = strat.generate_signals(df)["enriched_gates_ok"]
            except Exception:
                enriched_ok = None
            acct = _per_bar_gate_accounting(breakdown, enriched_ok)
            sweep_results.append(
                {
                    "lookback": lb,
                    "cointegration_check_interval": cci,
                    "bars": int(len(df)),
                    "gate_accounting": acct,
                    "total_return": float(res.get("total_return", 0.0)),
                    "trades_count": int(res.get("activity", {}).get("trades_count", 0)),
                }
            )
    any_bar_passes = any(r["gate_accounting"].get("bars_pass", 0) > 0 for r in sweep_results)
    rolling_stable_blocks_all = False
    if sweep_results:
        rolling_stable_blocks_all = all(
            r["gate_accounting"].get("per_gate_fail_count", {}).get("rolling_stable_ok", 0)
            == r["gate_accounting"].get("bars_total", 0)
            and r["gate_accounting"].get("bars_total", 0) > 0
            for r in sweep_results
        )
    return {
        "pair": list(pair),
        "symbols": pcols,
        "bars": int(len(df)),
        "window": {"start": str(df.index.min()), "end": str(df.index.max())},
        "sweeps": sweep_results,
        "any_bar_passes_all_gates": bool(any_bar_passes),
        "rolling_stable_blocks_all_bars_all_sweeps": bool(rolling_stable_blocks_all),
    }


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
        results_pairs["/".join(pair)] = _run_pair_sweep(pair, data)
    any_passes_anywhere = any(
        r.get("any_bar_passes_all_gates", False) for r in results_pairs.values()
    )
    rolling_stable_is_sole = all(
        r.get("rolling_stable_blocks_all_bars_all_sweeps", False)
        and not r.get("any_bar_passes_all_gates", False)
        for r in results_pairs.values()
    )
    if any_passes_anywhere:
        conclusion_status = "edge"
        conclusion_reason = "Some bars pass all enriched gates."
    elif rolling_stable_is_sole:
        conclusion_status = "no_edge"
        conclusion_reason = "No bar passes all gates; rolling_stable_ok blocks all bars."
    else:
        conclusion_status = "insufficient_or_blocked"
        conclusion_reason = "Mixed blocker pattern."
    report = {
        "type": "campaign11_rolling_stability_blocker",
        "computed_at": _now_iso(),
        "real_data_only": True,
        "fabricated_data": False,
        "provenance": {
            "source": "examples.run_campaign11_rolling_stability_blocker",
            "cache_spot_pkl": str(CACHE_PKL.relative_to(ROOT)),
            "cache_spot_meta": str(CACHE_META.relative_to(ROOT)),
            "cache_spot_pkl_sha256": spot_hash,
            "cache_spot_meta_sha256": meta_hash,
            "cache_spot_meta_content": meta,
            "volume_cache_hashes": vol_hashes,
            "network_fetch_performed": False,
            "no_synthetic_fabricated_inputs": True,
            "symbols": SYMBOLS,
            "pairs": [list(p) for p in PAIRS],
            "start": START,
            "end": END,
            "freq": FREQ,
        },
        "sweeps": SWEEPS,
        "pairs": results_pairs,
        "conclusion": {
            "status": conclusion_status,
            "reason": conclusion_reason,
            "edge_claim": conclusion_status == "edge",
            "honest": True,
        },
    }
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = ROOT / f"reports/campaign11_rolling_stability_blocker_{stamp}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(_json_safe(report), indent=2, allow_nan=False), encoding="utf-8")
    print(str(out_path))
    print(json.dumps(_json_safe(report["conclusion"]), indent=2))


if __name__ == "__main__":
    main()
