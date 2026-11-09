"""ML-augmented signal filtering for cointegration persistence.

Real-data-only, leakage-controlled, fail-closed gating utilities.
Features are computed from trailing windows only. Purged walk-forward CV
uses an embargo gap equal to the feature/lookback horizon to prevent
overlap leakage between train and test folds.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

try:
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler

    _SKLEARN_OK = True
except Exception:  # pragma: no cover - exercised by fail-closed path
    SimpleImputer = None
    LogisticRegression = None
    Pipeline = None
    StandardScaler = None
    _SKLEARN_OK = False

from utils.cointegration import (
    calculate_spread,
    engle_granger_test,
    estimate_hedge_ratio_ols,
    half_life_ou,
    hurst_exponent,
    johansen_test,
)

FEATURE_NAMES = [
    "eg_pvalue",
    "eg_stat",
    "johansen_trace0",
    "johansen_trace1",
    "half_life",
    "hurst",
    "spread_vol",
    "spread_z_abs",
    "hedge_ratio",
    "ret_corr",
    "price_ratio_z",
    "regime_vol",
    "regime_trend",
]


def _finite_or_nan(x: Any) -> float:
    try:
        v = float(x)
        return v if np.isfinite(v) else float("nan")
    except Exception:
        return float("nan")


def _regime_proxy(series: pd.Series, window: int) -> tuple[float, float]:
    """Simple causal regime proxies (no future leakage)."""
    s = series.dropna().astype(float)
    if len(s) < max(5, window // 2):
        return float("nan"), float("nan")
    ret = s.pct_change().dropna()
    if len(ret) < 5:
        return float("nan"), float("nan")
    vol = float(ret.tail(min(len(ret), window)).std(ddof=0))
    # trend proxy: sign of trailing mean return
    trend = float(np.sign(ret.tail(min(len(ret), window)).mean()))
    return vol, trend


def extract_persistence_features(
    price1: pd.Series,
    price2: pd.Series,
    *,
    lookback: int = 120,
    min_obs: int = 60,
) -> dict[str, float]:
    """Extract trailing-only cointegration persistence features.

    Fail-closed by returning NaNs when insufficient data or computation fails.
    Never uses future information.
    """
    out = {k: float("nan") for k in FEATURE_NAMES}
    try:
        a, b = price1.align(price2, join="inner")
        a = a.dropna().astype(float)
        b = b.reindex(a.index).dropna().astype(float)
        idx = a.index.intersection(b.index)
        a = a.loc[idx]
        b = b.loc[idx]
        if len(a) < min_obs or len(b) < min_obs:
            return out
        # Use only trailing window
        a_w = a.iloc[-lookback:] if len(a) >= lookback else a
        b_w = b.iloc[-lookback:] if len(b) >= lookback else b
        if len(a_w) < min_obs:
            return out

        eg = engle_granger_test(a_w, b_w)
        out["eg_pvalue"] = _finite_or_nan(eg.get("pvalue"))
        stat = eg.get("test_statistic")
        if stat is None:
            stat = eg.get("statistic")
        if stat is None:
            stat = eg.get("score")
        out["eg_stat"] = _finite_or_nan(stat)
        joh = johansen_test(a_w, b_w)
        tr = joh.get("trace_stat")
        if isinstance(tr, (list, tuple)) and len(tr) >= 2:
            out["johansen_trace0"] = _finite_or_nan(tr[0])
            out["johansen_trace1"] = _finite_or_nan(tr[1])

        beta = estimate_hedge_ratio_ols(a_w, b_w)
        out["hedge_ratio"] = _finite_or_nan(beta)
        spread = calculate_spread(a_w, b_w, beta if np.isfinite(beta) else None)
        hl = half_life_ou(spread)
        out["half_life"] = _finite_or_nan(hl.get("half_life"))
        out["hurst"] = _finite_or_nan(hurst_exponent(spread))

        s = spread.dropna()
        if len(s) >= 5:
            mu = float(s.mean())
            sd = float(s.std(ddof=0))
            out["spread_vol"] = sd if np.isfinite(sd) else float("nan")
            if np.isfinite(sd) and sd > 1e-12 and np.isfinite(mu):
                out["spread_z_abs"] = abs(float((s.iloc[-1] - mu) / sd))
        ra = a_w.pct_change().dropna()
        rb = b_w.pct_change().dropna()
        rc_idx = ra.index.intersection(rb.index)
        if len(rc_idx) >= 10:
            c = float(np.corrcoef(ra.loc[rc_idx].values, rb.loc[rc_idx].values)[0, 1])
            out["ret_corr"] = c if np.isfinite(c) else float("nan")
        ratio = (a_w / b_w.replace(0.0, np.nan)).dropna()
        if len(ratio) >= 10:
            rz = (ratio.iloc[-1] - ratio.mean()) / (ratio.std(ddof=0) + 1e-12)
            out["price_ratio_z"] = _finite_or_nan(rz)
        rv, rt = _regime_proxy(a_w / b_w.replace(0.0, np.nan), lookback)
        out["regime_vol"] = rv
        out["regime_trend"] = rt
    except Exception:
        return {k: float("nan") for k in FEATURE_NAMES}
    return out


@dataclass
class GateResult:
    allow: bool
    prob_persistent: float | None
    reason: str
    features: dict[str, float]


def _build_model(random_state: int = 42) -> Any:
    if not _SKLEARN_OK:
        raise RuntimeError("sklearn unavailable")
    return Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            (
                "clf",
                LogisticRegression(
                    max_iter=500,
                    class_weight="balanced",
                    random_state=random_state,
                    solver="lbfgs",
                ),
            ),
        ]
    )


def purged_walk_forward_indices(
    n: int, *, train_size: int, test_size: int, step: int, embargo: int
) -> list[tuple[np.ndarray, np.ndarray]]:
    """Purged walk-forward splits with embargo gap.

    Train uses [start, train_end), test uses [test_start, test_end) where
    test_start >= train_end + embargo. No overlap leakage.
    """
    splits: list[tuple[np.ndarray, np.ndarray]] = []
    if n <= 0 or train_size <= 0 or test_size <= 0 or step <= 0:
        return splits
    start = 0
    while True:
        train_end = start + train_size
        test_start = train_end + max(0, embargo)
        test_end = test_start + test_size
        if test_end > n:
            break
        tr = np.arange(start, train_end, dtype=int)
        te = np.arange(test_start, test_end, dtype=int)
        if len(tr) and len(te):
            splits.append((tr, te))
        start += step
    return splits


def train_persistence_classifier(
    X: pd.DataFrame,
    y: pd.Series,
    *,
    train_size: int,
    test_size: int,
    step: int,
    embargo: int,
    threshold: float = 0.5,
    random_state: int = 42,
) -> dict[str, Any]:
    """Train/evaluate with purged walk-forward CV; fail-closed on insufficient data."""
    result: dict[str, Any] = {
        "ok": False,
        "reason": "not_run",
        "splits": 0,
        "oos_predictions": [],
        "oos_actuals": [],
        "metrics": {},
        "feature_names": list(X.columns),
    }
    if not _SKLEARN_OK:
        result["reason"] = "sklearn_unavailable"
        return result
    df = X.copy()
    df["_y"] = y.values
    df = df.replace([np.inf, -np.inf], np.nan)
    # keep rows with label; imputer handles feature NaNs, but drop rows where all features NaN
    feat_cols = [c for c in df.columns if c != "_y"]
    df = df.dropna(subset=["_y"])
    if feat_cols:
        df = df[df[feat_cols].notna().any(axis=1)]
    if len(df) < max(30, train_size + test_size + embargo):
        result["reason"] = "insufficient_rows_after_dropna"
        result["rows_after_dropna"] = int(len(df))
        return result
    y_clean = df.pop("_y").astype(int)
    if y_clean.nunique() < 2:
        result["reason"] = "single_class_label"
        return result
    splits = purged_walk_forward_indices(
        len(df), train_size=train_size, test_size=test_size, step=step, embargo=embargo
    )
    if not splits:
        result["reason"] = "no_purged_splits"
        result["rows_after_dropna"] = int(len(df))
        return result
    preds: list[int] = []
    probs: list[float] = []
    actuals: list[int] = []
    split_meta: list[dict[str, Any]] = []
    Xv = df.values
    yv = y_clean.values
    for tr, te in splits:
        if len(np.unique(yv[tr])) < 2:
            split_meta.append(
                {"train_n": int(len(tr)), "test_n": int(len(te)), "skipped": "single_class_train"}
            )
            continue
        model = _build_model(random_state=random_state)
        try:
            model.fit(Xv[tr], yv[tr])
            p = model.predict_proba(Xv[te])[:, 1]
            pred = (p >= threshold).astype(int)
        except Exception as exc:
            split_meta.append(
                {"train_n": int(len(tr)), "test_n": int(len(te)), "skipped": str(exc)[:120]}
            )
            continue
        preds.extend(pred.tolist())
        probs.extend([float(x) for x in p])
        actuals.extend(yv[te].astype(int).tolist())
        split_meta.append(
            {
                "train_n": int(len(tr)),
                "test_n": int(len(te)),
                "train_end": int(tr[-1]),
                "test_start": int(te[0]),
                "embargo": int(embargo),
            }
        )
    if not actuals:
        result["reason"] = "no_valid_oos_predictions"
        result["split_meta"] = split_meta
        result["splits"] = len(splits)
        return result
    actual_arr = np.asarray(actuals)
    pred_arr = np.asarray(preds)
    acc = float((actual_arr == pred_arr).mean())
    # Precision/recall for positive class with zero guards
    tp = int(((pred_arr == 1) & (actual_arr == 1)).sum())
    fp = int(((pred_arr == 1) & (actual_arr == 0)).sum())
    fn = int(((pred_arr == 0) & (actual_arr == 1)).sum())
    precision = float(tp / (tp + fp)) if (tp + fp) else 0.0
    recall = float(tp / (tp + fn)) if (tp + fn) else 0.0
    f1 = float(2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    result.update(
        {
            "ok": True,
            "reason": "ok",
            "splits": len(splits),
            "evaluated_splits": int(sum(1 for m in split_meta if not m.get("skipped"))),
            "split_meta": split_meta,
            "oos_n": int(len(actuals)),
            "metrics": {
                "accuracy": acc,
                "precision_pos": precision,
                "recall_pos": recall,
                "f1_pos": f1,
                "positive_rate_actual": float(actual_arr.mean()),
                "positive_rate_pred": float(pred_arr.mean()),
                "threshold": float(threshold),
            },
        }
    )
    # keep payload bounded
    result["oos_preview"] = {
        "probs_head": probs[:20],
        "preds_head": preds[:20],
        "actuals_head": actuals[:20],
    }
    return result


def gate_persistence(
    features: dict[str, float],
    model: Any | None,
    *,
    threshold: float = 0.5,
) -> GateResult:
    """Fail-closed ML gate. Blocks if model unavailable or prediction fails."""
    row = pd.DataFrame([{k: features.get(k, np.nan) for k in FEATURE_NAMES}])
    row = row.replace([np.inf, -np.inf], np.nan)
    if model is None or not _SKLEARN_OK:
        return GateResult(False, None, "model_unavailable_fail_closed", features)
    try:
        prob = float(model.predict_proba(row.values)[:, 1][0])
        if not np.isfinite(prob):
            return GateResult(False, None, "nonfinite_prob_fail_closed", features)
        allow = bool(prob >= threshold)
        reason = "ok" if allow else "below_threshold"
        if row.isna().any(axis=1).iloc[0]:
            reason = reason + "_with_imputed_features"
        return GateResult(allow, prob, reason, features)
    except Exception as exc:
        return GateResult(False, None, f"predict_error_fail_closed:{str(exc)[:80]}", features)


def fit_final_model(
    X: pd.DataFrame, y: pd.Series, random_state: int = 42
) -> tuple[Any | None, dict[str, Any]]:
    """Fit a final model on cleaned data for artifact metadata; fail-closed."""
    meta: dict[str, Any] = {"ok": False, "reason": "not_run"}
    if not _SKLEARN_OK:
        meta["reason"] = "sklearn_unavailable"
        return None, meta
    df = X.copy()
    df["_y"] = y.values
    df = df.replace([np.inf, -np.inf], np.nan)
    # keep rows with label; imputer handles feature NaNs, but drop rows where all features NaN
    feat_cols = [c for c in df.columns if c != "_y"]
    df = df.dropna(subset=["_y"])
    if feat_cols:
        df = df[df[feat_cols].notna().any(axis=1)]
    if len(df) < 30:
        meta.update({"reason": "insufficient_rows", "rows": int(len(df))})
        return None, meta
    y_clean = df.pop("_y").astype(int)
    if y_clean.nunique() < 2:
        meta.update({"reason": "single_class", "rows": int(len(df))})
        return None, meta
    model = _build_model(random_state=random_state)
    try:
        model.fit(df.values, y_clean.values)
        meta.update({"ok": True, "reason": "ok", "rows": int(len(df))})
        return model, meta
    except Exception as exc:
        meta.update({"reason": f"fit_error:{str(exc)[:120]}", "rows": int(len(df))})
        return None, meta


def sha256_json_obj(obj: Any) -> str:
    b = json.dumps(obj, sort_keys=True, default=str, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(b).hexdigest()
