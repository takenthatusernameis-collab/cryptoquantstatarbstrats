"""
Performance attribution and factor decomposition utilities.

Provides:

* :func:`brinson_attribution` -- Brinson-Fachler style decomposition of active
  return into allocation, selection and interaction effects.
* :func:`factor_attribution` -- OLS regression-based (CAPM / multi-factor)
  attribution decomposing returns into alpha, factor exposures (beta) and
  residual idiosyncratic return.

All functions align inputs by date index, handle missing data defensively and
return plain dicts/pandas objects that are JSON-serializable friendly.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def _to_frame(x: Any, columns: list[str] | None = None) -> pd.DataFrame:
    """Coerce ``x`` into a DataFrame, filling missing values with 0."""
    if x is None:
        return pd.DataFrame(dtype=float)
    if isinstance(x, pd.DataFrame):
        df = x.copy()
    elif isinstance(x, pd.Series):
        df = x.to_frame()
    else:
        df = pd.DataFrame(np.asarray(x, dtype=float))
    if columns is not None:
        df = df.reindex(columns=columns, fill_value=0.0)
    return df.fillna(0.0)


def _align_inputs(
    weights: pd.DataFrame,
    benchmark_weights: pd.DataFrame,
    returns: pd.DataFrame,
    asset_returns: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Align all inputs on a common inner-join index and union of columns."""
    frames = [weights, benchmark_weights, returns, asset_returns]
    common_index = frames[0].index
    for f in frames[1:]:
        common_index = common_index.intersection(f.index)
    if len(common_index) == 0:
        common_index = frames[0].index[:0]

    columns = list(weights.columns)
    for f in frames[1:]:
        for c in f.columns:
            if c not in columns:
                columns.append(c)

    aligned = []
    for f in frames:
        f = f.reindex(index=common_index)
        f = f.reindex(columns=columns, fill_value=0.0)
        aligned.append(f.fillna(0.0))
    return tuple(aligned)


def brinson_attribution(
    returns: pd.DataFrame,
    weights: pd.DataFrame,
    benchmark_weights: pd.DataFrame,
    asset_returns: pd.DataFrame,
) -> dict[str, Any]:
    """Brinson-Fachler attribution of active return.

    Decomposes the portfolio's active return (portfolio vs benchmark) for each
    period and asset into:

    * ``allocation`` -- (w_p - w_b) * (r_b,i - r_b): value added by over/under
      weighting assets relative to the benchmark.
    * ``selection`` -- w_b * (r_p,i - r_b,i): value added by the portfolio
      earning a different return on an asset than the benchmark.
    * ``interaction`` -- (w_p - w_b) * (r_p,i - r_b,i): cross term.

    Args:
        returns: Per-asset returns earned by the portfolio (dates x assets).
        weights: Portfolio weights (dates x assets). Must sum to ~1 per row.
        benchmark_weights: Benchmark weights (dates x assets).
        asset_returns: Benchmark / reference per-asset returns (dates x assets).

    Returns:
        Dict with per-asset ``allocation``/``selection``/``interaction``
        DataFrames, per-period totals (``allocation_total``, ``selection_total``,
        ``interaction_total``, ``total_active_return``), ``portfolio_return``,
        ``benchmark_return`` and a per-asset ``summary`` DataFrame.
    """
    returns = _to_frame(returns)
    weights = _to_frame(weights)
    benchmark_weights = _to_frame(benchmark_weights)
    asset_returns = _to_frame(asset_returns)

    if returns.empty or weights.empty:
        empty_df = pd.DataFrame(dtype=float)
        empty_series = pd.Series(dtype=float)
        return {
            "allocation": empty_df,
            "selection": empty_df,
            "interaction": empty_df,
            "allocation_total": empty_series,
            "selection_total": empty_series,
            "interaction_total": empty_series,
            "total_active_return": empty_series,
            "portfolio_return": empty_series,
            "benchmark_return": empty_series,
            "summary": empty_df,
        }

    weights, benchmark_weights, returns, asset_returns = _align_inputs(
        weights, benchmark_weights, returns, asset_returns
    )

    # Normalize weights to sum to 1 per row where possible.
    w_p = weights.copy()
    w_b = benchmark_weights.copy()
    w_p_sum = w_p.sum(axis=1).replace(0.0, np.nan)
    w_p = w_p.div(w_p_sum, axis=0).fillna(0.0)
    w_b_sum = w_b.sum(axis=1).replace(0.0, np.nan)
    w_b = w_b.div(w_b_sum, axis=0).fillna(0.0)

    r_p = returns.astype(float)
    r_b = asset_returns.astype(float)

    # Benchmark total return per period.
    benchmark_return = (w_b * r_b).sum(axis=1)

    # Per-asset active return vs benchmark constituent return.
    active_asset_return = r_p.sub(r_b, axis=0)

    allocation = (w_p - w_b).multiply(r_b.sub(benchmark_return, axis=0), axis=0)
    selection = w_b.multiply(active_asset_return, axis=0)
    interaction = (w_p - w_b).multiply(active_asset_return, axis=0)

    allocation_total = allocation.sum(axis=1)
    selection_total = selection.sum(axis=1)
    interaction_total = interaction.sum(axis=1)

    portfolio_return = (w_p * r_p).sum(axis=1)
    total_active_return = portfolio_return - benchmark_return

    summary_rows: list[dict[str, Any]] = []
    all_columns = list(dict.fromkeys(list(r_p.columns) + list(r_b.columns)))
    for col in all_columns:
        summary_rows.append(
            {
                "asset": col,
                "allocation": float(allocation[col].sum()) if col in allocation.columns else 0.0,
                "selection": float(selection[col].sum()) if col in selection.columns else 0.0,
                "interaction": float(interaction[col].sum()) if col in interaction.columns else 0.0,
                "total": float(
                    (allocation[col] + selection[col] + interaction[col]).sum()
                )
                if col in allocation.columns
                else 0.0,
            }
        )
    summary = pd.DataFrame(summary_rows)

    return {
        "allocation": allocation,
        "selection": selection,
        "interaction": interaction,
        "allocation_total": allocation_total,
        "selection_total": selection_total,
        "interaction_total": interaction_total,
        "total_active_return": total_active_return,
        "portfolio_return": portfolio_return,
        "benchmark_return": benchmark_return,
        "summary": summary,
    }


def factor_attribution(
    returns: pd.Series,
    factor_returns: pd.DataFrame,
    risk_free_rate: float = 0.0,
    periods_per_year: int = 252,
) -> dict[str, Any]:
    """OLS regression-based factor attribution (CAPM / multi-factor).

    Regresses portfolio returns on the provided factor returns::

        r_t = alpha + beta_1 * f_1,t + ... + beta_k * f_k,t + residual_t

    The fitted decomposition is::

        returns = alpha + sum(beta_k * factor_k) + residual

    Args:
        returns: Portfolio return series (dates).
        factor_returns: Factor return DataFrame (dates x factors).
        risk_free_rate: Annualized risk-free rate used to annualize alpha.
        periods_per_year: Number of periods per year for annualization.

    Returns:
        Dict with ``alpha`` (per-period), ``alpha_annualized``, ``beta``
        (factor exposures as a Series), ``r_squared``, ``residuals``,
        ``fitted_values``, ``factor_contribution`` (beta * factor returns),
        ``std_err`` (beta standard errors), ``t_stats`` and ``n_obs``.
    """
    r = _to_series(returns).astype(float)
    f = _to_frame(factor_returns).astype(float)

    if f.empty:
        f = pd.DataFrame(index=r.index)

    # Align on common index and drop rows with any missing values.
    common_index = r.index.intersection(f.index)
    r_aligned = r.reindex(common_index).dropna()
    f_aligned = f.reindex(common_index)
    valid = r_aligned.notna() & f_aligned.notna().all(axis=1)
    r_aligned = r_aligned[valid]
    f_aligned = f_aligned[valid]

    n_obs = int(len(r_aligned))
    empty_result = _empty_factor_result(periods_per_year, risk_free_rate)
    if n_obs == 0:
        return empty_result

    factor_names = list(f_aligned.columns)
    n_factors = len(factor_names)

    if n_factors == 0:
        # No factors: alpha = mean excess return, no beta.
        excess = r_aligned - risk_free_rate / periods_per_year
        alpha = float(np.mean(excess)) if len(excess) else 0.0
        return {
            **empty_result,
            "alpha": alpha,
            "alpha_annualized": alpha * periods_per_year,
            "r_squared": 0.0,
            "n_obs": n_obs,
            "residuals": r_aligned.copy(),
            "fitted_values": pd.Series(
                np.full(n_obs, alpha), index=r_aligned.index, dtype=float
            ),
        }

    y = r_aligned.to_numpy(dtype=float)
    X = np.column_stack([np.ones(n_obs), f_aligned.to_numpy(dtype=float)])

    try:
        coeffs, _, rank, _ = np.linalg.lstsq(X, y, rcond=None)
    except np.linalg.LinAlgError:
        return empty_result

    alpha = float(coeffs[0])
    betas = coeffs[1:]
    if rank < X.shape[1]:
        # Rank deficient: zero out coefficients beyond the rank.
        betas = np.where(np.arange(len(betas)) < rank - 1, betas, 0.0)

    fitted = X @ coeffs
    residuals = y - fitted
    ss_res = float(np.sum(residuals**2))
    ss_tot = float(np.sum((y - np.mean(y))**2))
    r_squared = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0

    df_resid = n_obs - (n_factors + 1)
    sigma_sq = ss_res / df_resid if df_resid > 0 else 0.0
    try:
        cov = sigma_sq * np.linalg.inv(X.T @ X)
        std_err = np.sqrt(np.maximum(np.diag(cov), 0.0))
    except np.linalg.LinAlgError:
        std_err = np.full(n_factors + 1, np.nan)

    beta_std_err = std_err[1:] if len(std_err) > 1 else np.array([np.nan] * n_factors)
    t_stats = betas / beta_std_err if np.all(beta_std_err > 0) else np.full(
        n_factors, np.nan
    )

    beta_series = pd.Series(betas, index=factor_names, dtype=float)
    std_err_series = pd.Series(beta_std_err, index=factor_names, dtype=float)
    t_stats_series = pd.Series(t_stats, index=factor_names, dtype=float)

    factor_contribution = f_aligned.multiply(beta_series, axis=1)

    return {
        "alpha": alpha,
        "alpha_annualized": alpha * periods_per_year,
        "beta": beta_series,
        "r_squared": float(r_squared),
        "residuals": pd.Series(residuals, index=r_aligned.index, dtype=float),
        "fitted_values": pd.Series(fitted, index=r_aligned.index, dtype=float),
        "factor_contribution": factor_contribution,
        "std_err": std_err_series,
        "t_stats": t_stats_series,
        "n_obs": n_obs,
        "risk_free_rate": float(risk_free_rate),
        "periods_per_year": int(periods_per_year),
    }


def _to_series(x: Any) -> pd.Series:
    if isinstance(x, pd.Series):
        return x.copy()
    if isinstance(x, pd.DataFrame):
        if x.shape[1] == 1:
            return x.iloc[:, 0].copy()
        for name in ("returns", "portfolio_returns", "value"):
            if name in x.columns:
                return x[name].copy()
        return x.iloc[:, 0].copy()
    return pd.Series(np.asarray(x, dtype=float))


def _empty_factor_result(periods_per_year: int, risk_free_rate: float) -> dict[str, Any]:
    return {
        "alpha": 0.0,
        "alpha_annualized": 0.0,
        "beta": pd.Series(dtype=float),
        "r_squared": 0.0,
        "residuals": pd.Series(dtype=float),
        "fitted_values": pd.Series(dtype=float),
        "factor_contribution": pd.DataFrame(dtype=float),
        "std_err": pd.Series(dtype=float),
        "t_stats": pd.Series(dtype=float),
        "n_obs": 0,
        "risk_free_rate": float(risk_free_rate),
        "periods_per_year": int(periods_per_year),
    }
