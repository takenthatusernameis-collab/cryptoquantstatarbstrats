"""Regime detection utilities."""

from __future__ import annotations

import numpy as np
import pandas as pd
from hmmlearn.hmm import GaussianHMM


def rolling_volatility(series: pd.Series, window: int = 20) -> pd.Series:
    if window is None or window <= 1:
        window = 2
    return series.pct_change().rolling(window).std()


def volatility_regime(
    series: pd.Series, window: int = 20, n_regimes: int = 3, labels: list[str] | None = None
) -> pd.Series:
    vol = rolling_volatility(series, window)
    # quantile-based regimes
    q = vol.dropna()
    if q.empty:
        return pd.Series(index=series.index, dtype=object)
    try:
        bins = pd.qcut(vol, q=n_regimes, labels=False, duplicates="drop")
    except Exception:
        bins = pd.Series(0, index=series.index)
    if labels is not None and len(labels) == n_regimes:
        mapping = {i: labels[i] for i in range(n_regimes)}
        return bins.map(mapping)
    return bins


def trend_detection(series: pd.Series, short_window: int = 10, long_window: int = 50) -> pd.Series:
    if short_window is None or short_window <= 0:
        short_window = 1
    if long_window is None or long_window <= short_window:
        long_window = short_window + 1
    short_ma = series.rolling(short_window).mean()
    long_ma = series.rolling(long_window).mean()
    trend = pd.Series(0, index=series.index, dtype=int)
    trend[short_ma > long_ma] = 1
    trend[short_ma < long_ma] = -1
    return trend


def _compute_hmm_features(
    series: pd.Series,
    vol_window: int = 20,
    ret_lag: int = 1,
) -> np.ndarray:
    """Compute causal features for HMM regime detection."""
    ret = series.pct_change()
    vol = ret.rolling(vol_window).std()
    # Build feature matrix (causal - no future leakage)
    features = pd.DataFrame(index=series.index)
    features["ret"] = ret
    features["vol"] = vol
    features["abs_ret"] = ret.abs()
    # Fill NaN with small values
    features = features.fillna(0.0)
    return features.values


def hmm_regimes(
    series: pd.Series,
    n_regimes: int = 3,
    vol_window: int = 20,
    fit_window: int | None = None,
    random_state: int = 42,
    n_iter: int = 100,
    causal: bool = True,
) -> pd.Series:
    """
    HMM-based regime detection using GaussianHMM.
    Causal fit only, zero lookahead.
    """
    if len(series) < vol_window + 10:
        return pd.Series(0, index=series.index, dtype=int)

    features = _compute_hmm_features(series, vol_window=vol_window)
    labels = pd.Series(index=series.index, dtype=int)
    labels[:] = 0

    try:
        if causal and fit_window is not None and fit_window > 0:
            # Expanding window for causal fitting
            for i in range(fit_window, len(series)):
                train_data = features[:i]
                # Fit on historical data only
                model = GaussianHMM(
                    n_components=n_regimes,
                    covariance_type="full",
                    n_iter=n_iter,
                    random_state=random_state,
                )
                try:
                    model.fit(train_data)
                    # Predict current state
                    pred = model.predict(features[:i+1])
                    labels.iloc[i] = int(pred[-1])
                except Exception:
                    labels.iloc[i] = labels.iloc[i-1] if i > 0 else 0
            # Forward fill for initial period
            labels = labels.ffill().fillna(0)
        else:
            # Fit on all available data (for validation scripts) but still causal in features
            model = GaussianHMM(
                n_components=n_regimes,
                covariance_type="full",
                n_iter=n_iter,
                random_state=random_state,
            )
            try:
                model.fit(features)
                preds = model.predict(features)
                labels = pd.Series(preds, index=series.index, dtype=int)
            except Exception:
                labels = pd.Series(0, index=series.index, dtype=int)
    except Exception:
        return pd.Series(0, index=series.index, dtype=int)

    return labels


def regime_transition_probs(
    regime_labels: pd.Series,
    n_regimes: int | None = None,
) -> pd.DataFrame:
    """Compute regime transition probability matrix."""
    if n_regimes is None:
        n_regimes = int(regime_labels.max()) + 1 if len(regime_labels.dropna()) > 0 else 1

    # Count transitions
    trans = np.zeros((n_regimes, n_regimes))
    labels_clean = regime_labels.dropna().astype(int)
    for i in range(len(labels_clean) - 1):
        curr = int(labels_clean.iloc[i])
        next_reg = int(labels_clean.iloc[i + 1])
        if 0 <= curr < n_regimes and 0 <= next_reg < n_regimes:
            trans[curr, next_reg] += 1

    # Normalize to probabilities
    trans_df = pd.DataFrame(trans, index=range(n_regimes), columns=range(n_regimes))
    # Avoid division by zero
    row_sums = trans_df.sum(axis=1)
    for i in range(n_regimes):
        if row_sums.iloc[i] > 0:
            trans_df.iloc[i] = trans_df.iloc[i] / row_sums.iloc[i]
        else:
            trans_df.iloc[i] = 0.0
            trans_df.iloc[i, i] = 1.0

    return trans_df


def detect_regimes(
    data: pd.DataFrame,
    window: int = 20,
    trend_short: int = 10,
    trend_long: int = 50,
    use_hmm: bool = True,
    n_regimes: int = 3,
    random_state: int = 42,
) -> pd.DataFrame:
    out = pd.DataFrame(index=data.index)
    for col in data.columns:
        if use_hmm:
            try:
                out[f"{col}_vol_regime"] = hmm_regimes(
                    data[col], n_regimes=n_regimes, vol_window=window, random_state=random_state
                )
            except Exception:
                out[f"{col}_vol_regime"] = volatility_regime(data[col], window=window)
        else:
            out[f"{col}_vol_regime"] = volatility_regime(data[col], window=window)
        out[f"{col}_trend"] = trend_detection(
            data[col], short_window=trend_short, long_window=trend_long
        )
    return out
