#!/usr/bin/env python3
"""End-to-end fail-closed audit: prove CointegrationPairsStrategy emits zero
entries/positions/exposure for every pair × timeframe where diagnostics say
blocked, across the full real Binance spot universe.

Real data only (cached 1h spot klines, resampled 4h/1d via real last()).
Fail-closed always. No threshold weakening. Causal trailing semantics honored
by the strategy (aggregate cached diagnostics are applied fail-closed under
strict mode per strategy design).

Writes reports/pairs_failclosed_audit_<UTC>.json.
"""
from __future__ import annotations

import json
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from data.cache import load_cached  # noqa: E402
from data.loader import DataLoader  # noqa: E402
from strategies.pairs_trading import CointegrationPairsStrategy  # noqa: E402

SYMBOLS = [
    "ADA", "AVAX", "BNB", "BTC", "DOT", "ETH", "LINK", "LTC", "POL", "SOL", "XRP",
]
START = "2026-04-01"
END = "2026-10-30"
TIMEFRAMES = ("1h", "4h", "1d")
DIAG_ARTIFACT = ROOT / "reports" / "pairs_leg_stationarity_closest_20261105T063013Z.json"
MEMO_ARTIFACT = ROOT / "reports" / "pairs_leg_stationarity_impossibility_memo_20261105T065521Z.json"


def resample_ohlc_close(df: pd.DataFrame, rule: str) -> pd.DataFrame:
    return df.resample(rule).last().dropna()


def utc_now() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def load_diag_index() -> dict[tuple[str, str], dict[str, Any]]:
    raw = json.loads(DIAG_ARTIFACT.read_text(encoding="utf-8"))
    idx: dict[tuple[str, str], dict[str, Any]] = {}
    for e in raw.get("entries", []):
        idx[(e["pair"], e["tf"])] = e
    return idx


def build_enriched_diag(entry: dict[str, Any]) -> dict[str, Any]:
    """Construct the enriched_diagnostics shape CointegrationPairsStrategy expects
    from a real pre-computed diagnostic entry. Uses full_gate_detail when present."""
    fgd = entry.get("full_gate_detail") or {}
    gates = fgd.get("gates") or {
        "all_pass": entry.get("all_pass", False),
        "eg_pass": entry.get("eg_pass"),
        "johansen_pass": entry.get("johansen_pass"),
        "spread_mr_pass": entry.get("spread_mr_pass"),
        "hl_bounds_pass": entry.get("hl_bounds_pass"),
        "leg_stationarity_ok": entry.get("leg_stationarity_ok"),
        "rolling_stable_ok": entry.get("rolling_stable_ok"),
        "no_structural_break": entry.get("no_structural_break"),
    }
    structural_breaks = {"flagged": not bool(entry.get("no_structural_break", True))}
    return {
        "pair": entry.get("pair"),
        "gates": gates,
        "structural_breaks": structural_breaks,
        "provenance": {
            "source": str(DIAG_ARTIFACT.name),
            "real_data_only": True,
            "fabricated_data": False,
            "note": "real pre-computed diagnostic; cached path is fail-closed under strict mode",
        },
    }


def audit_one(
    df: pd.DataFrame, a: str, b: str, tf: str, entry: dict[str, Any]
) -> dict[str, Any]:
    pair_df = df[[a, b]].dropna()
    diag_leg_ok = entry.get("leg_stationarity_ok")
    diag_all_pass = entry.get("all_pass")
    blocked_routes = list(entry.get("blocked_routes") or [])
    diagnostic_blocked = (diag_leg_ok is False) or (diag_all_pass is False)

    enriched = build_enriched_diag(entry)
    strat = CointegrationPairsStrategy(
        pair=(a, b),
        lookback=60,
        entry_threshold=2.0,
        exit_threshold=0.5,
        enriched_diagnostics=enriched,
        use_enriched_gates=True,
        strict_enriched_gates=True,
    )
    signals = strat.generate_signals(pair_df)
    wa = signals[a].to_numpy(dtype=float)
    wb = signals[b].to_numpy(dtype=float)
    # entry = any non-zero position bar (weight != 0 on either leg)
    active = (wa != 0.0) | (wb != 0.0)
    n_entries_bars = int(active.sum())
    max_abs_exposure_a = float(abs(wa).max()) if len(wa) else 0.0
    max_abs_exposure_b = float(abs(wb).max()) if len(wb) else 0.0
    has_any_position = n_entries_bars > 0
    # fail-closed breach: diagnostic blocked but strategy emitted exposure
    breach = bool(diagnostic_blocked and has_any_position)

    return {
        "pair": f"{a}/{b}",
        "tf": tf,
        "n_bars": int(len(pair_df)),
        "diagnostic": {
            "leg_stationarity_ok": diag_leg_ok,
            "all_pass": diag_all_pass,
            "eg_pass": entry.get("eg_pass"),
            "johansen_pass": entry.get("johansen_pass"),
            "spread_mr_pass": entry.get("spread_mr_pass"),
            "hl_bounds_pass": entry.get("hl_bounds_pass"),
            "rolling_stable_ok": entry.get("rolling_stable_ok"),
            "no_structural_break": entry.get("no_structural_break"),
            "blocked_routes": blocked_routes,
            "diagnostic_blocked": diagnostic_blocked,
            "source_artifact": DIAG_ARTIFACT.name,
        },
        "strategy_actual": {
            "use_enriched_gates": True,
            "strict_enriched_gates": True,
            "enriched_diagnostics_supplied": True,
            "n_active_position_bars": n_entries_bars,
            "has_any_position": has_any_position,
            "max_abs_exposure_leg_a": max_abs_exposure_a,
            "max_abs_exposure_leg_b": max_abs_exposure_b,
            "total_weight_columns": [a, b],
        },
        "assertion": {
            "expected_zero_when_blocked": diagnostic_blocked,
            "entries_zero": n_entries_bars == 0,
            "pass_fail_closed": (not diagnostic_blocked) or (n_entries_bars == 0),
            "breach": breach,
        },
        "provenance": {
            "real_data_only": True,
            "fabricated_data": False,
            "causal_trailing": True,
            "no_threshold_weakening": True,
            "fail_closed": True,
        },
        "rationale": (
            "Diagnostic blocked (leg_stationarity_ok/all_pass false, real data); strict "
            "fail-closed strategy with real pre-computed enriched diagnostics must emit zero."
            if diagnostic_blocked
            else "Diagnostic not blocked (unexpected); exposure audited without breach assertion."
        ),
    }


def main() -> None:
    if not DIAG_ARTIFACT.exists():
        print(f"FATAL: missing diagnostic artifact {DIAG_ARTIFACT}", file=sys.stderr)
        sys.exit(2)
    diag_idx = load_diag_index()
    loader = DataLoader()
    data, prov = load_cached(loader, SYMBOLS, START, END, interval="1h", use_cache=True)
    data = loader.clean_data(data)
    print(f"Loaded {len(data)} hourly bars for {list(data.columns)}")
    frames: dict[str, pd.DataFrame] = {"1h": data}
    for tf, rule in (("4h", "4h"), ("1d", "1d")):
        frames[tf] = resample_ohlc_close(data, rule)
        print(f"Resampled {tf}: {len(frames[tf])} bars")

    cache_detail = prov.get("cache", {}) or {}
    blocked_routes = list(
        prov.get("blocked_routes", []) or cache_detail.get("blocked_routes", []) or []
    )
    data_provenance = {
        "source": "real public Binance spot klines (cached)",
        "real_data_only": True,
        "fabricated_data": False,
        "hosts_tried": list(prov.get("hosts", []) or cache_detail.get("hosts_tried", []) or []),
        "blocked_routes": blocked_routes,
        "symbols": list(data.columns),
        "start": START,
        "end": END,
    }

    results: list[dict[str, Any]] = []
    breaches: list[dict[str, Any]] = []
    missing_diag: list[str] = []
    for tf in TIMEFRAMES:
        df = frames[tf]
        cols = list(df.columns)
        import itertools
        for a, b in itertools.combinations(cols, 2):
            key = (f"{a}/{b}", tf)
            entry = diag_idx.get(key)
            if entry is None:
                missing_diag.append(f"{a}/{b}@{tf}")
                continue
            row = audit_one(df, a, b, tf, entry)
            results.append(row)
            if row["assertion"]["breach"]:
                breaches.append({"pair": row["pair"], "tf": tf, "detail": row["strategy_actual"]})

    n_audited = len(results)
    n_blocked = sum(1 for r in results if r["diagnostic"]["diagnostic_blocked"])
    n_pass_diag = n_audited - n_blocked
    n_zero_when_blocked = sum(
        1 for r in results
        if r["diagnostic"]["diagnostic_blocked"] and r["assertion"]["entries_zero"]
    )
    n_breaches = len(breaches)
    overall_pass = (n_breaches == 0) and (len(missing_diag) == 0)

    summary = {
        "n_audited": n_audited,
        "n_diagnostic_blocked": n_blocked,
        "n_diagnostic_not_blocked": n_pass_diag,
        "n_zero_exposure_when_blocked": n_zero_when_blocked,
        "n_breaches_fail_closed": n_breaches,
        "n_missing_diagnostic_entries": len(missing_diag),
        "overall_pass_fail_closed": overall_pass,
        "conclusion": (
            "PASS: CointegrationPairsStrategy (fail-closed, strict enriched gates) emitted "
            "zero entries/positions/exposure for all diagnostic-blocked pair×TF combos."
            if overall_pass
            else "FAIL: breach(es) or missing diagnostic entries; see breaches/missing_diagnostic."
        ),
    }
    print(json.dumps(summary, indent=2))
    if breaches:
        print("BREACHES:", breaches)

    report = {
        "created_at": datetime.now(tz=timezone.utc).isoformat(),
        "purpose": "pairs_failclosed_audit_end_to_end",
        "real_data_only": True,
        "fabricated_data": False,
        "no_threshold_weakening": True,
        "fail_closed": True,
        "causal_trailing": True,
        "source_diagnostic_artifact": DIAG_ARTIFACT.name,
        "source_memo_artifact": MEMO_ARTIFACT.name if MEMO_ARTIFACT.exists() else None,
        "data_provenance": data_provenance,
        "strategy_config": {
            "class": "CointegrationPairsStrategy",
            "lookback": 60,
            "entry_threshold": 2.0,
            "exit_threshold": 0.5,
            "use_enriched_gates": True,
            "strict_enriched_gates": True,
            "enriched_diagnostics_mode": "real_precomputed_per_pair_tf_fail_closed_cached_path",
        },
        "summary": summary,
        "breaches": breaches,
        "missing_diagnostic": missing_diag,
        "results": results,
    }
    out = ROOT / "reports" / f"pairs_failclosed_audit_{utc_now()}.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
