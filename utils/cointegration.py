"""
Publication-grade cointegration and stationarity diagnostics.

All functions work on real data only. No fabrication.
"""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.tsa.stattools import adfuller, coint, kpss
from statsmodels.tsa.vector_ar.vecm import coint_johansen


def _to_clean_pair(price1: pd.Series, price2: pd.Series) -> tuple[pd.Series, pd.Series]:
    aligned = pd.concat([price1, price2], axis=1).dropna()
    if len(aligned) < 3:
        raise ValueError("At least three aligned observations are required.")
    return aligned.iloc[:, 0].astype(float), aligned.iloc[:, 1].astype(float)


def adf_test(series: pd.Series, regression: str = "c") -> dict[str, Any]:
    """Augmented Dickey-Fuller test on a series."""
    s = series.dropna().astype(float)
    if len(s) < 10:
        return {"statistic": float("nan"), "pvalue": float("nan"), "used_lag": None, "nobs": int(len(s)), "critical_values": {}}
    try:
        stat, pval, usedlag, nobs, crit_vals, _ = adfuller(s.values, regression=regression, autolag="AIC")
        return {
            "statistic": float(stat),
            "pvalue": float(pval),
            "used_lag": int(usedlag),
            "nobs": int(nobs),
            "critical_values": {k: float(v) for k, v in crit_vals.items()},
        }
    except Exception as e:
        return {"statistic": float("nan"), "pvalue": float("nan"), "error": str(e)[:80], "nobs": int(len(s))}


def kpss_test(series: pd.Series, regression: str = "c", nlags: str = "auto") -> dict[str, Any]:
    """KPSS stationarity test (null: stationary)."""
    s = series.dropna().astype(float)
    if len(s) < 10:
        return {"statistic": float("nan"), "pvalue": float("nan"), "nobs": int(len(s)), "critical_values": {}}
    try:
        stat, pval, lags, crit_vals = kpss(s.values, regression=regression, nlags=nlags)
        return {
            "statistic": float(stat),
            "pvalue": float(pval),
            "lags": int(lags),
            "nobs": int(len(s)),
            "critical_values": {k: float(v) for k, v in crit_vals.items()},
        }
    except Exception as e:
        return {"statistic": float("nan"), "pvalue": float("nan"), "error": str(e)[:80], "nobs": int(len(s))}


def engle_granger_test(price1: pd.Series, price2: pd.Series) -> dict[str, Any]:
    """Engle-Granger cointegration test."""
    try:
        p1, p2 = _to_clean_pair(price1, price2)
        score, pvalue, crit_vals = coint(p1.values, p2.values)
        return {
            "score": float(score),
            "pvalue": float(pvalue),
            "critical_values": {f"cv{int(k*100)}": float(v) for k, v in zip([0.01, 0.05, 0.10], crit_vals)},
        }
    except Exception as e:
        return {"score": float("nan"), "pvalue": float("nan"), "error": str(e)[:80]}


def estimate_hedge_ratio_ols(price1: pd.Series, price2: pd.Series) -> float:
    """Estimate hedge ratio beta = cov(p1,p2)/var(p2) or OLS p1 ~ alpha + beta*p2."""
    try:
        p1, p2 = _to_clean_pair(price1, price2)
        if p2.var() == 0:
            return float("nan")
        beta = np.cov(p1.values, p2.values)[0, 1] / np.var(p2.values)
        if not np.isfinite(beta) or beta <= 0:
            # try OLS
            X = np.column_stack([np.ones(len(p2)), p2.values])
            coeffs = np.linalg.lstsq(X, p1.values, rcond=None)[0]
            beta = float(coeffs[1])
        if not np.isfinite(beta):
            return float("nan")
        return float(beta)
    except Exception:
        return float("nan")


def calculate_spread(price1: pd.Series, price2: pd.Series, beta: float | None = None) -> pd.Series:
    if beta is None:
        beta = estimate_hedge_ratio_ols(price1, price2)
    if not np.isfinite(beta):
        beta = 1.0
    aligned = pd.concat([price1, price2], axis=1).dropna()
    return aligned.iloc[:, 0] - beta * aligned.iloc[:, 1]


def half_life_ou(series: pd.Series) -> dict[str, Any]:
    """Estimate half-life of mean reversion for OU process via AR(1)."""
    s = series.dropna().astype(float)
    if len(s) < 5:
        return {"half_life": float("nan"), "beta": float("nan"), "is_mean_reverting": False}
    s_lag = s.shift(1).dropna()
    s_diff = s.diff().dropna()
    # align
    idx = s_lag.index.intersection(s_diff.index)
    if len(idx) < 4:
        return {"half_life": float("nan"), "beta": float("nan"), "is_mean_reverting": False}
    x = s_lag.loc[idx].values
    y = s_diff.loc[idx].values
    if np.std(x) == 0:
        return {"half_life": float("nan"), "beta": float("nan"), "is_mean_reverting": False}
    try:
        beta = np.polyfit(x, y, 1)[0]
        is_mr = bool(beta < 0)
        if not is_mr:
            return {"half_life": float("inf"), "beta": float(beta), "is_mean_reverting": False}
        hl = -np.log(2.0) / beta
        if not np.isfinite(hl) or hl < 0:
            return {"half_life": float("inf"), "beta": float(beta), "is_mean_reverting": False}
        return {"half_life": float(hl), "beta": float(beta), "is_mean_reverting": True}
    except Exception as e:
        return {"half_life": float("nan"), "beta": float("nan"), "is_mean_reverting": False, "error": str(e)[:80]}


def hurst_exponent(ts: pd.Series, max_lag: int = 20) -> float:
    """Rough Hurst exponent estimate (R/S style). H < 0.5 suggests mean reversion."""
    s = ts.dropna().astype(float).values
    if len(s) < max_lag * 2:
        return float("nan")
    try:
        lags = range(2, max_lag + 1)
        tau = []
        for lag in lags:
            pp = s[lag:] - s[:-lag]
            tau.append(np.sqrt(np.std(pp)))
        # Fit power law
        poly = np.polyfit(np.log(lags), np.log(tau), 1)
        hurst = poly[0] * 2.0
        if not np.isfinite(hurst):
            return float("nan")
        return float(hurst)
    except Exception:
        return float("nan")


def johansen_test(price1: pd.Series, price2: pd.Series, det_order: int = 0, k_ar_diff: int = 1) -> dict[str, Any]:
    """Johansen cointegration test for bivariate case."""
    try:
        p1, p2 = _to_clean_pair(price1, price2)
        df = pd.concat([p1, p2], axis=1)
        # coint_johansen expects data in columns
        result = coint_johansen(df.values, det_order=det_order, k_ar_diff=k_ar_diff)
        trace_stat = result.lr1  # trace
        max_eig_stat = result.lr2
        cvt = result.cvt  # critical values for trace (90%, 95%, 99%)
        cve = result.cvm  # for max eigen
        r_0_trace = int(trace_stat[0] > cvt[0, 1])  # 95%
        r_0_max = int(max_eig_stat[0] > cve[0, 1])
        return {
            "trace_stat": [float(x) for x in trace_stat],
            "max_eig_stat": [float(x) for x in max_eig_stat],
            "critical_values_trace_95": [float(x) for x in cvt[:, 1]],
            "critical_values_max_95": [float(x) for x in cve[:, 1]],
            "rank_trace_95": r_0_trace + (int(trace_stat[1] > cvt[1, 1]) if len(trace_stat) > 1 else 0),
            "rank_maxeig_95": r_0_max + (int(max_eig_stat[1] > cve[1, 1]) if len(max_eig_stat) > 1 else 0),
            "eigenvalues": [float(x) for x in result.eig],
        }
    except Exception as e:
        return {"error": str(e)[:120], "rank_trace_95": 0, "rank_maxeig_95": 0}


def rolling_cointegration_stability(price1: pd.Series, price2: pd.Series, window: int = 720, step: int = 24) -> dict[str, Any]:
    """Test rolling cointegration stability over time windows."""
    try:
        p1, p2 = _to_clean_pair(price1, price2)
        if len(p1) < window * 1.5:
            return {"stable": False, "reason": "insufficient_data", "pvalues": [], "frac_significant": 0.0}
        pvalues = []
        for start in range(0, len(p1) - window + 1, step):
            end = start + window
            try:
                res = engle_granger_test(p1.iloc[start:end], p2.iloc[start:end])
                pv = res.get("pvalue", float("nan"))
                if np.isfinite(pv):
                    pvalues.append(float(pv))
            except Exception:
                continue
        if not pvalues:
            return {"stable": False, "pvalues": [], "frac_significant": 0.0}
        frac_sig = float(np.mean([pv < 0.05 for pv in pvalues]))
        stable = frac_sig >= 0.6  # majority of windows cointegrated
        return {
            "stable": bool(stable),
            "pvalues": pvalues,
            "frac_significant_0_05": frac_sig,
            "n_windows": len(pvalues),
            "window": int(window),
            "step": int(step),
        }
    except Exception as e:
        return {"stable": False, "error": str(e)[:80], "pvalues": [], "frac_significant_0_05": 0.0}


def structural_break_check(price1: pd.Series, price2: pd.Series, min_seg: int = 200) -> dict[str, Any]:
    """Simple structural break check via rolling hedge ratio instability (Chow-like heuristic)."""
    try:
        p1, p2 = _to_clean_pair(price1, price2)
        if len(p1) < min_seg * 2:
            return {"has_break": False, "reason": "insufficient_data"}
        # split into halves
        mid = len(p1) // 2
        beta1 = estimate_hedge_ratio_ols(p1.iloc[:mid], p2.iloc[:mid])
        beta2 = estimate_hedge_ratio_ols(p1.iloc[mid:], p2.iloc[mid:])
        if not (np.isfinite(beta1) and np.isfinite(beta2)):
            return {"has_break": False, "reason": "beta_nan"}
        rel_diff = abs(beta1 - beta2) / (abs(beta1) + abs(beta2) + 1e-18)
        has_break = bool(rel_diff > 0.25)  # 25% change suggests instability
        return {
            "has_break": bool(has_break),
            "beta_first_half": float(beta1),
            "beta_second_half": float(beta2),
            "rel_diff": float(rel_diff),
        }
    except Exception as e:
        return {"has_break": False, "error": str(e)[:80]}


def comprehensive_cointegration_diagnostics(price1: pd.Series, price2: pd.Series, pair_name: str = "") -> dict[str, Any]:
    """Full cointegration diagnostics for publication-grade rigor."""
    diag: dict[str, Any] = {"pair": pair_name}
    try:
        # Unit roots on legs
        diag["adf_leg1"] = adf_test(price1)
        diag["adf_leg2"] = adf_test(price2)
        diag["kpss_leg1"] = kpss_test(price1)
        diag["kpss_leg2"] = kpss_test(price2)

        # Engle-Granger
        eg = engle_granger_test(price1, price2)
        diag["engle_granger"] = eg

        # Johansen
        joh = johansen_test(price1, price2)
        diag["johansen"] = joh

        # Spread quality
        beta = estimate_hedge_ratio_ols(price1, price2)
        diag["hedge_ratio_ols"] = float(beta) if np.isfinite(beta) else float("nan")
        spread = calculate_spread(price1, price2, beta)
        diag["adf_spread"] = adf_test(spread)
        diag["kpss_spread"] = kpss_test(spread)
        diag["half_life"] = half_life_ou(spread)
        diag["hurst_spread"] = hurst_exponent(spread)

        # Stability
        diag["rolling_stability"] = rolling_cointegration_stability(price1, price2)
        diag["structural_break"] = structural_break_check(price1, price2)

        # Gates
        eg_ok = bool(np.isfinite(eg.get("pvalue")) and eg["pvalue"] < 0.05)
        joh_ok = bool(joh.get("rank_trace_95", 0) >= 1 or joh.get("rank_maxeig_95", 0) >= 1)
        hl_ok = bool(diag["half_life"].get("is_mean_reverting") and np.isfinite(diag["half_life"].get("half_life")) and 1 < diag["half_life"]["half_life"] < 500)
        stable_ok = bool(diag["rolling_stability"].get("stable", False))
        break_ok = not bool(diag["structural_break"].get("has_break", False))
        diag["gates"] = {
            "engle_granger_pass": eg_ok,
            "johansen_pass": joh_ok,
            "half_life_pass": hl_ok,
            "rolling_stability_pass": stable_ok,
            "no_structural_break": break_ok,
            "all_pass": bool(eg_ok and joh_ok and hl_ok and stable_ok and break_ok),
        }
        return diag
    except Exception as e:
        diag["error"] = str(e)[:200]
        diag["gates"] = {"all_pass": False}
        return diag
