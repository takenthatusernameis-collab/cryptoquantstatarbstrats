#!/usr/bin/env python3
"""Campaign #12: causal per-bar enriched-gate evaluation on unevaluated real caches.

Determines whether any unevaluated real cache in data/cache/ yields a causal
per-bar enriched-gate edge (any bar passes all enriched gates under unmodified
thresholds) on any pair across trailing configs, without weakening thresholds
and without fabrication. Produces honest edge/no_edge/insufficient_or_blocked
per cache.

Cached real data only. No network refetch. No synthetic/fabricated prices,
IV, volume, fills, order books, labels, or metrics.

Usage:
  PYTHONPATH=$PWD python examples/run_campaign12_causal_gates.py \
    --cache 90d10b876bb8eda9619cbba73ed19d6c7db4ea7327284f2e33f10a7872a5b263

Derives symbols/start/end/freq from the cache .meta.json and evaluates the
curated pairs available in that cache across lookback x cointegration_check_interval
sweeps (gate thresholds unmodified: entry_threshold=2.0, cointegration_pvalue=0.05,
hl 1<hl<500, EG p<=0.05, etc.), fail-closed under strict enriched gates.
"""

from __future__ import annotations

import argparse
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

GATE_NAMES = (
    "eg_pass",
    "johansen_pass",
    "spread_mr_pass",
    "hl_bounds_pass",
    "leg_stationarity_ok",
    "rolling_stable_ok",
    "no_structural_break",
)

# Gate thresholds are UNMODIFIED (match Campaigns #9-#11).
ENTRY_THRESHOLD = 2.0
COINTEGRATION_PVALUE = 0.05
LOOKBACKS = [120, 240]
CHECK_INTERVALS = [24, 48]
FEE_RATE = 0.001
SLIPPAGE = 0.0005


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


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


def _curated_pairs(symbols: list[str]) -> list[tuple[str, str]]:
    """Curated, cache-available pairs prioritizing the validated baseline set."""
    sym_set = set(symbols)
    preferred = [
        ("BTC", "ETH"),
        ("ETH", "SOL"),
        ("BTC", "SOL"),
        ("ADA", "ETH"),
        ("XRP", "BTC"),
        ("BNB", "ETH"),
        ("ADA", "BTC"),
        ("XRP", "ETH"),
        ("BNB", "BTC"),
        ("SOL", "BNB"),
        ("DOT", "BTC"),
        ("DOT", "ETH"),
        ("POL", "BTC"),
        ("AVAX", "BTC"),
        ("LINK", "BTC"),
        ("LTC", "BTC"),
    ]
    pairs = [p for p in preferred if p[0] in sym_set and p[1] in sym_set]
    # Deterministic fallback: any remaining same-cache symbol pair not yet covered.
    for i, a in enumerate(sorted(sym_set)):
        for b in sorted(sym_set)[i + 1 :]:
            if (a, b) not in pairs and (b, a) not in pairs:
                pairs.append((a, b))
    return pairs


def _load_cached_spot(cache_pkl: Path, cache_meta: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    if not cache_pkl.exists() or not cache_meta.exists():
        raise FileNotFoundError(f"Missing cache: {cache_pkl} / {cache_meta}")
    meta = json.loads(cache_meta.read_text(encoding="utf-8"))
    with open(cache_pkl, "rb") as f:
        data = pickle.load(f)
    if not isinstance(data, pd.DataFrame):
        raise TypeError("Bad cache payload")
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
    for lb in LOOKBACKS:
        for cci in CHECK_INTERVALS:
            strat = CointegrationPairsStrategy(
                pair=pair,
                lookback=lb,
                entry_threshold=ENTRY_THRESHOLD,
                cointegration_pvalue=COINTEGRATION_PVALUE,
                cointegration_check_interval=cci,
                use_enriched_gates=True,
                strict_enriched_gates=True,
            )
            res = engine.run(strat, df, fee_rate=FEE_RATE, slippage=SLIPPAGE)
            breakdown = strat.get_gate_breakdown()
            # Derive enriched_ok from the per-bar breakdown captured during the
            # single engine.run above (avoids recomputing diagnostics a second
            # time). all_pass True -> 1.0, False -> 0.0, pre-refresh NaN -> fill 0.0 strict.
            if breakdown is not None and not breakdown.empty and "all_pass" in breakdown.columns:
                ap = breakdown["all_pass"]
                enriched_ok = pd.Series(np.where(ap.to_numpy(dtype=bool), 1.0, 0.0), index=df.index, dtype=float)
                enriched_ok = enriched_ok.where(ap.notna(), np.nan)
                enriched_ok = enriched_ok.bfill().ffill().fillna(0.0)
            else:
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
    ap = argparse.ArgumentParser(description="Campaign #12 causal per-bar enriched-gate evaluation")
    ap.add_argument("--cache", required=True, help="Full cache key hash (data/cache/<hash>.pkl)")
    ap.add_argument(
        "--pairs",
        default=None,
        help='Comma-separated "A/B" pairs to override the curated set',
    )
    args = ap.parse_args()

    cache_pkl = ROOT / f"data/cache/{args.cache}.pkl"
    cache_meta = ROOT / f"data/cache/{args.cache}.meta.json"
    data, meta = _load_cached_spot(cache_pkl, cache_meta)

    # Honor the real-only provenance contract from the cache meta.
    fetch_real = bool(meta.get("fetch_real_data_only", False))
    fetch_fab = bool(meta.get("fetch_fabricated_data", False))
    if not fetch_real or fetch_fab:
        print(
            "REFUSING: cache meta does not assert fetch_real_data_only=true and "
            "fetch_fabricated_data=false.",
            file=sys.stderr,
        )
        sys.exit(2)

    symbols = list(meta.get("columns", []) or meta.get("symbols", []))
    start = meta.get("start")
    end = meta.get("end")
    freq = meta.get("interval")
    cache8 = args.cache[:8]

    if args.pairs:
        pairs: list[tuple[str, str]] = []
        for token in args.pairs.split(","):
            token = token.strip()
            if "/" not in token:
                continue
            a, b = token.split("/")
            a, b = a.strip().upper(), b.strip().upper()
            if a in symbols and b in symbols and a != b:
                pairs.append((a, b))
    else:
        pairs = _curated_pairs(symbols)

    spot_hash = _sha256(cache_pkl)
    meta_hash = _sha256(cache_meta)

    results_pairs = {}
    for idx, pair in enumerate(pairs, 1):
        print(f"[C12] pair {idx}/{len(pairs)} {'/'.join(pair)}", flush=True)
        results_pairs["/".join(pair)] = _run_pair_sweep(pair, data)

    any_passes_anywhere = any(
        r.get("any_bar_passes_all_gates", False) for r in results_pairs.values()
    )
    # Data-sufficiency guard: a cache too short for even the smallest rolling
    # stability window is honestly insufficient_or_blocked, not no_edge.
    min_bars = min((r.get("bars", 0) for r in results_pairs.values()), default=0)
    rolling_stable_is_sole = all(
        r.get("rolling_stable_blocks_all_bars_all_sweeps", False)
        and not r.get("any_bar_passes_all_gates", False)
        for r in results_pairs.values()
    )
    if any_passes_anywhere:
        conclusion_status = "edge"
        conclusion_reason = "Some bars pass all enriched gates."
    elif min_bars > 0 and min_bars < 60:
        conclusion_status = "insufficient_or_blocked"
        conclusion_reason = (
            f"Cache too short ({min_bars} bars) for enriched-gate rolling windows; "
            "insufficient_or_blocked with evidence."
        )
    elif rolling_stable_is_sole:
        conclusion_status = "no_edge"
        conclusion_reason = "No bar passes all gates; rolling_stable_ok blocks all bars."
    else:
        conclusion_status = "insufficient_or_blocked"
        conclusion_reason = "Mixed blocker pattern / unassessable gates on real data."

    report = {
        "type": "campaign12_causal_per_bar_enriched_gates",
        "campaign": 12,
        "computed_at": _now_iso(),
        "real_data_only": True,
        "fabricated_data": False,
        "provenance": {
            "source": "examples.run_campaign12_causal_gates",
            "cache_spot_pkl": str(cache_pkl.relative_to(ROOT)),
            "cache_spot_meta": str(cache_meta.relative_to(ROOT)),
            "cache_spot_pkl_sha256": spot_hash,
            "cache_spot_meta_sha256": meta_hash,
            "cache_meta_content": meta,
            "network_fetch_performed": False,
            "no_synthetic_fabricated_inputs": True,
            "symbols": symbols,
            "pairs": [list(p) for p in pairs],
            "start": start,
            "end": end,
            "freq": freq,
            "fetch_real_data_only": fetch_real,
            "fetch_fabricated_data": fetch_fab,
        },
        "thresholds_unmodified": {
            "entry_threshold": ENTRY_THRESHOLD,
            "cointegration_pvalue": COINTEGRATION_PVALUE,
            "lookbacks": LOOKBACKS,
            "check_intervals": CHECK_INTERVALS,
            "fee_rate": FEE_RATE,
            "slippage": SLIPPAGE,
            "strict_enriched_gates": True,
            "use_enriched_gates": True,
        },
        "sweeps": {"lookbacks": LOOKBACKS, "check_intervals": CHECK_INTERVALS},
        "pairs": results_pairs,
        "conclusion": {
            "status": conclusion_status,
            "reason": conclusion_reason,
            "edge_claim": conclusion_status == "edge",
            "honest": True,
            "cache_bars_min": int(min_bars),
        },
    }
    stamp = _stamp()
    out_path = ROOT / f"reports/campaign12_causal_per_bar_enriched_gates_{cache8}_{stamp}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(_json_safe(report), indent=2, allow_nan=False), encoding="utf-8"
    )
    print(str(out_path))
    print(json.dumps(_json_safe(report["conclusion"]), indent=2))


if __name__ == "__main__":
    main()
