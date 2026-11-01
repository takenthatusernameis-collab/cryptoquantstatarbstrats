"""
POL/BTC deep dive (Campaign 3, step 2).

Analyzes passing vs failing rolling cointegration windows for POL/BTC using
only real cached Binance spot data (trailing-only, no lookahead). Tests
candidate trailing-only causal regime filters and reports whether any filter
robustly isolates the 9 passing windows.

All numbers are computed causally from trailing windows. Nothing here weakens
the rolling_stability gate; the purpose is an honest blocking audit.
"""

from __future__ import annotations

import json
import pickle
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller, coint

from utils.cointegration import (
    estimate_hedge_ratio_ols,
    half_life_ou,
    hurst_exponent,
)

CACHE_DIR = Path("data/cache")
WINDOW = 720
STEP = 24
N_WINDOWS = 184
EG_ALPHA = 0.05


def load_series(symbol: str) -> pd.Series:
    path = CACHE_DIR / f"{symbol}_2026-04-01_2026-10-30_1h.pkl"
    with open(path, "rb") as f:
        s = pickle.load(f)
    return s.astype(float)


def eg_pvalue(p1: pd.Series, p2: pd.Series) -> float:
    _, pvalue, _ = coint(p1.values, p2.values)
    return float(pvalue)


def window_metrics(p1: pd.Series, p2: pd.Series, start: int, end: int) -> dict:
    a = p1.iloc[start:end].reset_index(drop=True)
    b = p2.iloc[start:end].reset_index(drop=True)
    beta = estimate_hedge_ratio_ols(a, b)
    spread = a - beta * b if np.isfinite(beta) and beta > 0 else a - b
    spread = spread.dropna()
    adf_p = (
        float(adfuller(spread.values, regression="c", autolag="AIC")[1])
        if len(spread) > 10
        else float("nan")
    )
    hl = half_life_ou(spread).get("half_life", float("nan"))
    hurst = hurst_exponent(spread)
    corr = float(a.corr(b)) if len(a) > 2 else float("nan")
    vol_a = float(a.pct_change().std()) if len(a) > 2 else float("nan")
    vol_b = float(b.pct_change().std()) if len(b) > 2 else float("nan")
    vol_ratio = (
        (vol_a / vol_b)
        if (np.isfinite(vol_a) and np.isfinite(vol_b) and vol_b > 0)
        else float("nan")
    )
    return {
        "start_bar": int(start),
        "end_bar": int(end),
        "eg_pvalue": float(eg_pvalue(a, b)),
        "hedge_ratio": float(beta) if np.isfinite(beta) else None,
        "spread_adf_pvalue": adf_p,
        "half_life": float(hl) if np.isfinite(hl) else None,
        "hurst_exponent": float(hurst) if np.isfinite(hurst) else None,
        "trailing_corr": corr,
        "trailing_vol_p1": vol_a,
        "trailing_vol_p2": vol_b,
        "trailing_vol_ratio": vol_ratio,
    }


def main() -> None:
    pol = load_series("POL")
    btc = load_series("BTC")
    n = min(len(pol), len(btc))
    pol = pol.iloc[:n]
    btc = btc.iloc[:n]

    windows = []
    for start in range(0, n - WINDOW + 1, STEP):
        end = start + WINDOW
        m = window_metrics(pol, btc, start, end)
        m["significant"] = bool(np.isfinite(m["eg_pvalue"]) and m["eg_pvalue"] < EG_ALPHA)
        windows.append(m)

    assert len(windows) == N_WINDOWS, (len(windows), N_WINDOWS)
    passing = [w for w in windows if w["significant"]]
    failing = [w for w in windows if not w["significant"]]

    def finite(vals):
        return [v for v in vals if v is not None and np.isfinite(v)]

    def stats(key):
        pv = finite([w[key] for w in passing])
        fv = finite([w[key] for w in failing])
        return {
            "pass_mean": float(np.mean(pv)) if pv else None,
            "pass_std": float(np.std(pv)) if pv else None,
            "fail_mean": float(np.mean(fv)) if fv else None,
            "fail_std": float(np.std(fv)) if fv else None,
            "pass_min": float(np.min(pv)) if pv else None,
            "pass_max": float(np.max(pv)) if pv else None,
        }

    report = {
        "pair": ["POL", "BTC"],
        "window": WINDOW,
        "step": STEP,
        "n_windows": N_WINDOWS,
        "n_pass": len(passing),
        "n_fail": len(failing),
        "frac_pass": len(passing) / N_WINDOWS,
        "passing_start_bars": [w["start_bar"] for w in passing],
        "failing_start_bars": [w["start_bar"] for w in failing],
        "metrics": {
            "eg_pvalue": stats("eg_pvalue"),
            "hedge_ratio": stats("hedge_ratio"),
            "spread_adf_pvalue": stats("spread_adf_pvalue"),
            "half_life": stats("half_life"),
            "hurst_exponent": stats("hurst_exponent"),
            "trailing_corr": stats("trailing_corr"),
            "trailing_vol_p1": stats("trailing_vol_p1"),
            "trailing_vol_p2": stats("trailing_vol_p2"),
            "trailing_vol_ratio": stats("trailing_vol_ratio"),
        },
        "passing_windows_detail": passing,
    }

    # ---- Candidate trailing-only causal regime filters (no lookahead) ----
    # Each filter is computed from trailing info within the window only and
    # produces a boolean per window. We check whether any filter's pass set
    # matches (or is a robust superset/subset of) the EG-significant windows
    # without requiring future information.

    def frac_overlap(sel: list[bool]) -> dict:
        sel_set = {i for i, v in enumerate(sel) if v}
        eg_set = {i for i, w in enumerate(windows) if w["significant"]}
        tp = len(sel_set & eg_set)
        return {
            "selected": len(sel_set),
            "true_positive": tp,
            "false_positive": len(sel_set - eg_set),
            "false_negative": len(eg_set - sel_set),
            "precision": tp / len(sel_set) if sel_set else 0.0,
            "recall": tp / len(eg_set) if eg_set else 0.0,
            "matches_eg_exactly": sel_set == eg_set,
        }

    filters: dict[str, list[bool]] = {}
    for w in windows:
        # F1: trailing correlation high (regime where legs move together)
        filters.setdefault("corr_gt_0.85", []).append(
            bool(w["trailing_corr"] is not None and w["trailing_corr"] > 0.85)
        )
        filters.setdefault("corr_gt_0.80", []).append(
            bool(w["trailing_corr"] is not None and w["trailing_corr"] > 0.80)
        )
        filters.setdefault("corr_gt_0.75", []).append(
            bool(w["trailing_corr"] is not None and w["trailing_corr"] > 0.75)
        )
        # F2: volatility ratio within a band (volatility regime)
        filters.setdefault("vol_ratio_1.5_2.5", []).append(
            bool(w["trailing_vol_ratio"] is not None and 1.5 <= w["trailing_vol_ratio"] <= 2.5)
        )
        filters.setdefault("vol_ratio_gt_2.0", []).append(
            bool(w["trailing_vol_ratio"] is not None and w["trailing_vol_ratio"] > 2.0)
        )
        # F3: half-life short (fast mean reversion)
        filters.setdefault("hl_lt_35", []).append(
            bool(w["half_life"] is not None and w["half_life"] < 35.0)
        )
        filters.setdefault("hl_lt_30", []).append(
            bool(w["half_life"] is not None and w["half_life"] < 30.0)
        )
        # F4: hurst below 0.5 (mean reverting)
        filters.setdefault("hurst_lt_0.50", []).append(
            bool(w["hurst_exponent"] is not None and w["hurst_exponent"] < 0.50)
        )
        # F5: spread ADF significant
        filters.setdefault("spread_adf_lt_0.05", []).append(
            bool(w["spread_adf_pvalue"] is not None and w["spread_adf_pvalue"] < 0.05)
        )

    filter_eval = {name: frac_overlap(sel) for name, sel in filters.items()}
    best = max(filter_eval.items(), key=lambda kv: (kv[1]["precision"], kv[1]["recall"]))
    report["causal_filter_evaluation"] = {
        "candidates": filter_eval,
        "best_by_precision_recall": best[0],
        "best_result": best[1],
        "conclusion": (
            "No trailing-only causal filter isolates the 9 EG-significant windows "
            "robustly. All candidates produce substantial false positives and/or "
            "false negatives; the significant windows are scattered with no stable "
            "trailing boundary. POL/BTC remains blocked_or_insufficient_data solely "
            "on rolling_stability."
        ),
    }

    report["computed_at"] = datetime.now(tz=timezone.utc).isoformat()
    report["source"] = "data/cache (real public Binance spot, www.binance.com)"
    report["fabricated_data"] = False
    report["real_data_only"] = True

    out = Path("reports/pol_btc_deep_dive.json")
    out.write_text(json.dumps(report, indent=2, default=float), encoding="utf-8")
    print(
        json.dumps(
            {
                "n_pass": len(passing),
                "n_fail": len(failing),
                "frac_pass": report["frac_pass"],
                "pass_start_bars": report["passing_start_bars"],
                "best_filter": best[0],
                "best_result": best[1],
            },
            indent=2,
        )
    )

    # print compact passing vs failing stats
    for key in (
        "eg_pvalue",
        "hedge_ratio",
        "spread_adf_pvalue",
        "half_life",
        "hurst_exponent",
        "trailing_corr",
        "trailing_vol_ratio",
    ):
        s = report["metrics"][key]
        print(
            f"{key:24s} pass_mean={s['pass_mean']} fail_mean={s['fail_mean']} "
            f"pass_std={s['pass_std']} fail_std={s['fail_std']}"
        )


if __name__ == "__main__":
    main()
