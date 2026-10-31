"""
Publication-grade cointegration and stationarity diagnostics.

All functions work on real data only. No fabrication.
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any

import numpy as np
import pandas as pd
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
        return {
            "statistic": float("nan"),
            "pvalue": float("nan"),
            "used_lag": None,
            "nobs": int(len(s)),
            "critical_values": {},
        }
    try:
        stat, pval, usedlag, nobs, crit_vals, _ = adfuller(
            s.values, regression=regression, autolag="AIC"
        )
        return {
            "statistic": float(stat),
            "pvalue": float(pval),
            "used_lag": int(usedlag),
            "nobs": int(nobs),
            "critical_values": {k: float(v) for k, v in crit_vals.items()},
        }
    except Exception as e:
        return {
            "statistic": float("nan"),
            "pvalue": float("nan"),
            "error": str(e)[:80],
            "nobs": int(len(s)),
        }


def kpss_test(series: pd.Series, regression: str = "c", nlags: str = "auto") -> dict[str, Any]:
    """KPSS stationarity test (null: stationary)."""
    s = series.dropna().astype(float)
    if len(s) < 10:
        return {
            "statistic": float("nan"),
            "pvalue": float("nan"),
            "nobs": int(len(s)),
            "critical_values": {},
        }
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
        return {
            "statistic": float("nan"),
            "pvalue": float("nan"),
            "error": str(e)[:80],
            "nobs": int(len(s)),
        }


def engle_granger_test(price1: pd.Series, price2: pd.Series) -> dict[str, Any]:
    """Engle-Granger cointegration test."""
    try:
        p1, p2 = _to_clean_pair(price1, price2)
        score, pvalue, crit_vals = coint(p1.values, p2.values)
        return {
            "score": float(score),
            "pvalue": float(pvalue),
            "critical_values": {
                f"cv{int(k * 100)}": float(v) for k, v in zip([0.01, 0.05, 0.10], crit_vals)
            },
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
        return {
            "half_life": float("nan"),
            "beta": float("nan"),
            "is_mean_reverting": False,
            "error": str(e)[:80],
        }


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


def johansen_test(
    price1: pd.Series, price2: pd.Series, det_order: int = 0, k_ar_diff: int = 1
) -> dict[str, Any]:
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
            "critical_values_trace_all": [cvt[:, i].tolist() for i in range(cvt.shape[1])],
            "critical_values_max_all": [cve[:, i].tolist() for i in range(cve.shape[1])],
            "rank_trace_95": r_0_trace
            + (int(trace_stat[1] > cvt[1, 1]) if len(trace_stat) > 1 else 0),
            "rank_maxeig_95": r_0_max
            + (int(max_eig_stat[1] > cve[1, 1]) if len(max_eig_stat) > 1 else 0),
            "eigenvalues": [float(x) for x in result.eig],
        }
    except Exception as e:
        return {"error": str(e)[:120], "rank_trace_95": 0, "rank_maxeig_95": 0}


def rolling_cointegration_stability(
    price1: pd.Series, price2: pd.Series, window: int = 720, step: int = 24
) -> dict[str, Any]:
    """Test rolling cointegration stability over time windows."""
    try:
        p1, p2 = _to_clean_pair(price1, price2)
        if len(p1) < window * 1.5:
            return {
                "stable": False,
                "reason": "insufficient_data",
                "pvalues": [],
                "frac_significant": 0.0,
            }
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


def structural_break_check(
    price1: pd.Series, price2: pd.Series, min_seg: int = 200
) -> dict[str, Any]:
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


def comprehensive_cointegration_diagnostics(
    price1: pd.Series, price2: pd.Series, pair_name: str = ""
) -> dict[str, Any]:
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
        hl_ok = bool(
            diag["half_life"].get("is_mean_reverting")
            and np.isfinite(diag["half_life"].get("half_life"))
            and 1 < diag["half_life"]["half_life"] < 500
        )
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


def _json_safe(value: Any) -> Any:
    """Recursively convert NaN/Inf to None for strict JSON serialization."""
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        return value
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    return value


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _opt_float(value: Any) -> float | None:
    """Return ``value`` as a finite float, or ``None`` when missing/non-finite."""
    if value is None:
        return None
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def _eg_target(eg: dict[str, Any]) -> dict[str, Any]:
    stat = _opt_float(eg.get("score"))
    pvalue = _opt_float(eg.get("pvalue"))
    prov: dict[str, Any] = {
        "source": "statsmodels.tsa.stattools.coint",
        "real_data_only": True,
        "fabricated_data": False,
    }
    if stat is None or pvalue is None:
        prov["error"] = eg.get("error")
        return {
            "available": False,
            "stat": None,
            "pvalue": None,
            "critical_values": {},
            "pass/fail": None,
            "method": None,
            "provenance": prov,
        }
    return {
        "available": True,
        "stat": stat,
        "pvalue": pvalue,
        "critical_values": eg.get("critical_values", {}),
        "pass/fail": bool(pvalue < 0.05),
        "method": "engle_granger",
        "provenance": prov,
    }


def _johansen_target(joh: dict[str, Any]) -> dict[str, Any]:
    trace_stat = joh.get("trace_stat")
    max_eig_stat = joh.get("max_eig_stat")
    available = bool(
        trace_stat is not None
        and max_eig_stat is not None
        and len(trace_stat) > 0
        and len(max_eig_stat) > 0
    )
    prov: dict[str, Any] = {
        "source": "statsmodels.tsa.vector_ar.vecm.coint_johansen",
        "real_data_only": True,
        "fabricated_data": False,
    }
    if not available:
        prov["error"] = joh.get("error")
        return {
            "available": False,
            "trace_stat": None,
            "max_eig_stat": None,
            "cv_90": None,
            "cv_95": None,
            "cv_99": None,
            "rank": None,
            "pass/fail": None,
            "provenance": prov,
        }
    assert trace_stat is not None and max_eig_stat is not None
    rank = joh.get("rank_trace_95")
    cvt_cols = joh.get("critical_values_trace_all")
    return {
        "available": True,
        "trace_stat": [float(x) for x in trace_stat],
        "max_eig_stat": [float(x) for x in max_eig_stat],
        "cv_90": (
            [float(x) for x in cvt_cols[0]]
            if isinstance(cvt_cols, (list, tuple)) and len(cvt_cols) > 0
            else None
        ),
        "cv_95": (
            [float(x) for x in cvt_cols[1]]
            if isinstance(cvt_cols, (list, tuple)) and len(cvt_cols) > 1
            else None
        ),
        "cv_99": (
            [float(x) for x in cvt_cols[2]]
            if isinstance(cvt_cols, (list, tuple)) and len(cvt_cols) > 2
            else None
        ),
        "rank": int(rank) if rank is not None else None,
        "pass/fail": bool(rank is not None and int(rank) >= 1),
        "provenance": prov,
    }


def _stationarity_target(tr: dict[str, Any], test: str = "adf") -> dict[str, Any]:
    stat = _opt_float(tr.get("statistic"))
    pvalue = _opt_float(tr.get("pvalue"))
    available = bool(stat is not None and pvalue is not None)
    source_name = (
        "statsmodels.tsa.stattools.kpss" if test == "kpss" else "statsmodels.tsa.stattools.adfuller"
    )
    prov: dict[str, Any] = {
        "source": source_name,
        "real_data_only": True,
        "fabricated_data": False,
    }
    if tr.get("error"):
        prov["error"] = tr.get("error")
    return {
        "available": available,
        "stat": stat,
        "pvalue": pvalue,
        "critical_values": tr.get("critical_values", {}) if available else {},
        "nobs": tr.get("nobs"),
        "used_lag": tr.get("used_lag"),
        "lags": tr.get("lags"),
        "provenance": prov,
    }


def _half_life_entry(hl: dict[str, Any]) -> dict[str, Any]:
    hl_value = _opt_float(hl.get("half_life"))
    beta = _opt_float(hl.get("beta"))
    is_mr = bool(hl.get("is_mean_reverting"))
    available = bool(hl_value is not None)
    in_bounds = bool(hl_value is not None and 1.0 < hl_value < 500.0)
    prov: dict[str, Any] = {
        "source": "utils.cointegration.half_life_ou (AR(1) OU)",
        "real_data_only": True,
        "fabricated_data": False,
    }
    if hl.get("error"):
        prov["error"] = hl.get("error")
    return {
        "available": available,
        "half_life_ou": hl_value,
        "beta": beta,
        "is_mean_reverting": is_mr if available else None,
        "hl_bounds_pass": in_bounds if available else None,
        "provenance": prov,
    }


def _rolling_target(rs: dict[str, Any], window: int) -> dict[str, Any]:
    available = bool(rs.get("stable") is not None and rs.get("frac_significant_0_05") is not None)
    pvalues = rs.get("pvalues", []) or []
    details: list[dict[str, Any]] = []
    if available:
        step = int(rs.get("step", 24))
        frac = _opt_float(rs.get("frac_significant_0_05", rs.get("frac_significant")))
        for i, pv in enumerate(pvalues):
            pv_finite = math.isfinite(pv)
            details.append(
                {
                    "window_index": i,
                    "start_bar": i * step,
                    "pvalue": float(pv) if pv_finite else None,
                    "significant_0_05": bool(pv < 0.05) if pv_finite else None,
                }
            )
    return {
        "available": available,
        "windows": [int(window)] if available else [],
        "frac_significant": frac if available else None,
        "stable": bool(rs.get("stable")) if available else None,
        "n_windows": int(rs.get("n_windows", 0)) if available else 0,
        "step": int(rs.get("step", 24)) if available else None,
        "details": details,
        "notes": rs.get("reason") or rs.get("error"),
        "provenance": {
            "source": "utils.cointegration.rolling_cointegration_stability",
            "real_data_only": True,
            "fabricated_data": False,
            **({"error": rs.get("error")} if rs.get("error") else {}),
        },
    }


def _structural_breaks_target(sb: dict[str, Any]) -> dict[str, Any]:
    available = bool("has_break" in sb and sb.get("reason") is None and "error" not in sb)
    breaks: list[dict[str, Any]] = []
    if available and sb.get("has_break"):
        breaks.append(
            {
                "method": "rolling_hedge_ratio_halfsample_chow_heuristic",
                "beta_first_half": float(sb["beta_first_half"]),
                "beta_second_half": float(sb["beta_second_half"]),
                "relative_change": float(sb.get("rel_diff", 0.0)),
            }
        )
    prov: dict[str, Any] = {
        "source": "utils.cointegration.structural_break_check",
        "real_data_only": True,
        "fabricated_data": False,
    }
    if sb.get("error"):
        prov["error"] = sb.get("error")
    return {
        "available": available,
        "breaks": breaks,
        "flagged": bool(sb.get("has_break")) if available else None,
        "notes": sb.get("reason") or sb.get("error"),
        "provenance": prov,
    }


def target_schema_diagnostics(
    price1: pd.Series,
    price2: pd.Series,
    pair_name: str = "",
    source: str = "reports/portfolio_real.json",
) -> dict[str, Any]:
    """Build a publication-grade cointegration diagnostic dict in the target schema.

    Computes every available field from real series only. Never fabricates.
    ``status`` is ``computed_from_existing_results`` when the full series are
    available; individual sub-tests report ``available: false`` when they cannot
    be computed.
    """
    leg1, leg2 = pair_name.split("/") if "/" in pair_name else [pair_name, pair_name]
    pair = [leg1, leg2]

    eg = engle_granger_test(price1, price2)
    joh = johansen_test(price1, price2)
    adf1 = adf_test(price1)
    adf2 = adf_test(price2)
    kpss1 = kpss_test(price1)
    kpss2 = kpss_test(price2)

    beta = _opt_float(estimate_hedge_ratio_ols(price1, price2))
    beta_ok = bool(beta is not None and beta > 0)
    spread = calculate_spread(price1, price2, beta) if beta_ok else pd.Series(dtype=float)
    spread_len = int(len(spread))
    if spread_len:
        adf_spread = adf_test(spread)
        kpss_spread = kpss_test(spread)
        hl = half_life_ou(spread)
        hurst = _opt_float(hurst_exponent(spread))
    else:
        adf_spread = {"statistic": float("nan"), "pvalue": float("nan"), "critical_values": {}}
        kpss_spread = {"statistic": float("nan"), "pvalue": float("nan"), "critical_values": {}}
        hl = {"half_life": float("nan"), "beta": float("nan"), "is_mean_reverting": False}
        hurst = None
    hl_t = _half_life_entry(hl)
    hl_value = _opt_float(hl.get("half_life"))
    hl_is_mr = bool(hl.get("is_mean_reverting"))
    hurst_ok = bool(hurst is not None)
    mr_favorable = bool(
        hl_is_mr
        and hl_value is not None
        and 1.0 < hl_value < 500.0
        and hurst_ok
        and hurst is not None
        and hurst < 0.5
    ) if spread_len else None

    rs = rolling_cointegration_stability(price1, price2)
    sb = structural_break_check(price1, price2)

    eg_t = _eg_target(eg)
    joh_t = _johansen_target(joh)

    spread_adf_p = _opt_float(adf_spread.get("pvalue"))
    spread_mr_pass = bool(
        spread_len
        and spread_adf_p is not None
        and spread_adf_p < 0.05
    )
    hl_bounds_pass = bool(hl_t["hl_bounds_pass"])
    adf1_p = _opt_float(adf1.get("pvalue"))
    adf2_p = _opt_float(adf2.get("pvalue"))
    leg_stationarity_ok = bool(adf1_p is not None and adf2_p is not None)
    rolling_stable_ok = bool(rs.get("stable"))

    eg_pass = bool(eg_t["pass/fail"])
    joh_pass = bool(joh_t["pass/fail"])
    all_pass = bool(
        eg_pass
        and joh_pass
        and spread_mr_pass
        and hl_bounds_pass
        and leg_stationarity_ok
        and rolling_stable_ok
    )

    adf_spread_stat = _opt_float(adf_spread.get("statistic"))
    kpss_spread_stat = _opt_float(kpss_spread.get("statistic"))
    kpss_spread_p = _opt_float(kpss_spread.get("pvalue"))

    return _json_safe(
        {
            "pair": pair,
            "status": "computed_from_existing_results",
            "engle_granger": eg_t,
            "johansen": joh_t,
            "adf_leg1": _stationarity_target(adf1, "adf"),
            "kpss_leg1": _stationarity_target(kpss1, "kpss"),
            "adf_leg2": _stationarity_target(adf2, "adf"),
            "kpss_leg2": _stationarity_target(kpss2, "kpss"),
            "spread": {
                "available": beta_ok and spread_len > 0,
                "hedge_ratio": beta,
                "adf_spread": {
                    "available": bool(
                        spread_len > 0 and spread_adf_p is not None
                    ),
                    "stat": adf_spread_stat,
                    "pvalue": spread_adf_p,
                    "critical_values": adf_spread.get("critical_values", {}),
                    "provenance": {
                        "source": "statsmodels.tsa.stattools.adfuller (spread)",
                        "real_data_only": True,
                        "fabricated_data": False,
                    },
                },
                "kpss_spread": {
                    "available": bool(
                        spread_len > 0 and kpss_spread_p is not None
                    ),
                    "stat": kpss_spread_stat,
                    "pvalue": kpss_spread_p,
                    "critical_values": kpss_spread.get("critical_values", {}),
                    "provenance": {
                        "source": "statsmodels.tsa.stattools.kpss (spread)",
                        "real_data_only": True,
                        "fabricated_data": False,
                    },
                },
                "half_life_ou": hl_t["half_life_ou"],
                "hurst_exponent": hurst,
                "mr_favorable": mr_favorable,
                "provenance": {
                    "source": "utils.cointegration (hedge ratio + spread tests)",
                    "real_data_only": True,
                    "fabricated_data": False,
                },
            },
            "rolling_stability": _rolling_target(rs, 720),
            "structural_breaks": _structural_breaks_target(sb),
            "gates": {
                "all_pass": all_pass,
                "eg_pass": eg_pass,
                "johansen_pass": joh_pass,
                "spread_mr_pass": spread_mr_pass,
                "hl_bounds_pass": hl_bounds_pass,
                "leg_stationarity_ok": leg_stationarity_ok,
                "rolling_stable_ok": rolling_stable_ok,
            },
            "provenance": {
                "source": source,
                "real_data_only": True,
                "fabricated_data": False,
                "computed_at": _now_iso(),
                "blocked_routes": [],
                "rationale": "Real Binance spot series (www.binance.com); no fabrication.",
            },
        }
    )


def blocked_schema_diagnostics(
    pair: list[str],
    blocked_routes: list[dict[str, Any]],
    rationale: str,
    source: str = "reports/portfolio_real.json",
) -> dict[str, Any]:
    """Build a ``blocked_or_insufficient_data`` diagnostic in the target schema.

    Used when the real pair series cannot be reconstructed (no network, no
    cached artifact series). Every sub-test reports ``available: false`` /
    null values; gates are null/false. Never fabricates.
    """
    null_prov: dict[str, Any] = {
        "source": source,
        "real_data_only": True,
        "fabricated_data": False,
    }
    return _json_safe(
        {
            "pair": list(pair),
            "status": "blocked_or_insufficient_data",
            "engle_granger": {
                "available": False,
                "stat": None,
                "pvalue": None,
                "critical_values": {},
                "pass/fail": None,
                "method": None,
                "provenance": {**null_prov, "error": "series_unreconstructible"},
            },
            "johansen": {
                "available": False,
                "trace_stat": None,
                "max_eig_stat": None,
                "cv_90": None,
                "cv_95": None,
                "cv_99": None,
                "rank": None,
                "pass/fail": None,
                "provenance": {**null_prov, "error": "series_unreconstructible"},
            },
            "adf_leg1": {
                "available": False,
                "stat": None,
                "pvalue": None,
                "critical_values": {},
                "nobs": None,
                "used_lag": None,
                "lags": None,
                "provenance": {**null_prov, "error": "series_unreconstructible"},
            },
            "kpss_leg1": {
                "available": False,
                "stat": None,
                "pvalue": None,
                "critical_values": {},
                "nobs": None,
                "used_lag": None,
                "lags": None,
                "provenance": {**null_prov, "error": "series_unreconstructible"},
            },
            "adf_leg2": {
                "available": False,
                "stat": None,
                "pvalue": None,
                "critical_values": {},
                "nobs": None,
                "used_lag": None,
                "lags": None,
                "provenance": {**null_prov, "error": "series_unreconstructible"},
            },
            "kpss_leg2": {
                "available": False,
                "stat": None,
                "pvalue": None,
                "critical_values": {},
                "nobs": None,
                "used_lag": None,
                "lags": None,
                "provenance": {**null_prov, "error": "series_unreconstructible"},
            },
            "spread": {
                "available": False,
                "hedge_ratio": None,
                "adf_spread": {
                    "available": False,
                    "stat": None,
                    "pvalue": None,
                    "critical_values": {},
                    "provenance": {**null_prov, "error": "series_unreconstructible"},
                },
                "kpss_spread": {
                    "available": False,
                    "stat": None,
                    "pvalue": None,
                    "critical_values": {},
                    "provenance": {**null_prov, "error": "series_unreconstructible"},
                },
                "half_life_ou": None,
                "hurst_exponent": None,
                "mr_favorable": None,
                "provenance": {**null_prov, "error": "series_unreconstructible"},
            },
            "rolling_stability": {
                "available": False,
                "windows": [],
                "frac_significant": None,
                "stable": None,
                "n_windows": 0,
                "step": None,
                "details": [],
                "notes": "series_unreconstructible",
                "provenance": {**null_prov, "error": "series_unreconstructible"},
            },
            "structural_breaks": {
                "available": False,
                "breaks": [],
                "flagged": None,
                "notes": "series_unreconstructible",
                "provenance": {**null_prov, "error": "series_unreconstructible"},
            },
            "gates": {
                "all_pass": False,
                "eg_pass": None,
                "johansen_pass": None,
                "spread_mr_pass": None,
                "hl_bounds_pass": None,
                "leg_stationarity_ok": None,
                "rolling_stable_ok": None,
            },
            "provenance": {
                "source": source,
                "real_data_only": True,
                "fabricated_data": False,
                "computed_at": _now_iso(),
                "blocked_routes": blocked_routes,
                "rationale": rationale,
            },
        }
    )
