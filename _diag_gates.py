#!/usr/bin/env python3
"""Diagnostic: measure REAL per-gate pass rates on cached Binance data.

Answers: on the actual trailing-sample sizes used by the strategy (60/120/500/600
bars), which gates can even be assessed, and which genuinely pass? No fabrication.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from data.loader import DataLoader
from utils.cointegration import (
    adf_test,
    engle_granger_test,
    estimate_hedge_ratio_ols,
    half_life_ou,
    hurst_exponent,
    johansen_test,
    rolling_cointegration_stability,
    structural_break_check,
    calculate_spread,
)

PAIRS = [("BTC", "ETH"), ("ETH", "SOL"), ("BTC", "SOL")]
# Sample sizes the strategy actually uses as trailing windows.
SAMPLE_SIZES = [60, 120, 240, 360, 500, 600, 1080, 2160, 5064]


def gate_report(p1: pd.Series, p2: pd.Series, n: int) -> dict:
    s1 = p1.iloc[-n:]
    s2 = p2.iloc[-n:]
    out: dict = {"n_sample": int(n)}
    eg = engle_granger_test(s1, s2)
    out["eg_pvalue"] = eg.get("pvalue")
    joh = johansen_test(s1, s2)
    out["joh_rank_trace"] = joh.get("rank_trace_95")
    beta = estimate_hedge_ratio_ols(s1, s2)
    spread = calculate_spread(s1, s2, beta) if np.isfinite(beta) else pd.Series(dtype=float)
    adf_sp = adf_test(spread)
    out["spread_adf_pvalue"] = adf_sp.get("pvalue")
    hl = half_life_ou(spread)
    out["half_life"] = hl.get("half_life")
    out["hl_is_mr"] = hl.get("is_mean_reverting")
    out["hurst"] = hurst_exponent(spread)
    adf1 = adf_test(s1)
    adf2 = adf_test(s2)
    out["adf_leg1_p"] = adf1.get("pvalue")
    out["adf_leg2_p"] = adf2.get("pvalue")
    # Rolling stability at the window the strategy hard-codes (720) AND adaptive
    for wl in (720, max(24, n // 3), max(24, n // 2)):
        if wl >= len(s1):
            continue
        rs = rolling_cointegration_stability(s1, s2, window=wl, step=max(12, wl // 6))
        out[f"rolling_win{wl}"] = {
            "stable": rs.get("stable"),
            "frac_sig": rs.get("frac_significant"),
            "n_windows": rs.get("n_windows"),
            "reason": rs.get("reason"),
        }
    sb = structural_break_check(s1, s2)
    out["struct_break"] = {"has_break": sb.get("has_break"), "reason": sb.get("reason")}
    return out


def main() -> None:
    loader = DataLoader()
    data, prov = loader.fetch_with_provenance(
        ["BTC", "ETH", "SOL"], "2026-04-01", "2026-10-28", interval="1h", use_cache=True
    )
    data = loader.clean_data(data)
    print(f"Loaded {len(data)} bars; cache_used={prov.get('cache', {}).get('disk_cache')}")
    result: dict = {"n_bars": int(len(data)), "pairs": {}}
    for a, b in PAIRS:
        p1 = data[a].astype(float)
        p2 = data[b].astype(float)
        rows = []
        for n in SAMPLE_SIZES:
            if n > len(p1):
                continue
            rows.append(gate_report(p1, p2, n))
        result["pairs"][f"{a}/{b}"] = rows
        # Summary table
        print(f"\n=== {a}/{b} ===")
        for r in rows:
            rs = {k: v for k, v in r.items() if k.startswith("rolling_win")}
            print(
                f"  n={r['n_sample']:5d} eg_p={r['eg_pvalue']:.3f} "
                f"joh_rank={r['joh_rank_trace']} spread_adf_p={r['spread_adf_pvalue']:.3f} "
                f"hl={r['half_life']} hurst={r['hurst']} "
                f"adf_legs=({r['adf_leg1_p']:.2f},{r['adf_leg2_p']:.2f}) "
                f"rolling={ {k.split('rolling_')[1]: (v.get('stable'), v.get('frac_sig'), v.get('n_windows'), v.get('reason')) for k, v in rs.items()} }"
            )
    out_path = Path(__file__).resolve().parent / "reports" / "gate_diagnosis_real.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, default=float), encoding="utf-8")
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()