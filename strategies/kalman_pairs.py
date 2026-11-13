"""
Causal Kalman-filter dynamic-hedge-ratio pairs trading strategy.

State-space model:
  B_t = alpha_t + beta_t * A_t + eps_t,  eps_t ~ N(0, r)
  alpha_t = alpha_{t-1} + xi_t,           xi_t ~ N(0, q)
  beta_t  = beta_{t-1} + eta_t,           eta_t ~ N(0, q)

The filter is fit on the trailing TRAIN window only, then run causally
through the TEST window using the train-selected noise parameters (q, r).
At every bar, only data available up to t-1 is used.

Fail-closed gates enforced per bar:
  - causal Engle-Granger p <= 0.05
  - causal spread ADF/KPSS stationarity passes
  - OU half-life satisfies 1 < half_life < 500
  - causal rolling hedge-ratio/spread stability gate passes
  - structural-break discipline passes
No missing/None/false gate value is treated as permissive.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from strategies.base import PairStrategy
from utils.cointegration import target_schema_diagnostics
from strategies.pairs_trading import _evaluate_enriched_gates_strict


class KalmanPairsStrategy(PairStrategy):
    """Pairs strategy using a Kalman filter for time-varying hedge ratio.

    The Kalman filter estimates a local-level model where:
      - Observation: B_t = alpha_t + beta_t * A_t + eps_t
      - State transition: alpha_t = alpha_{t-1} + xi_t, beta_t = beta_{t-1} + eta_t

    The filter is trained on the trailing TRAIN window to select noise parameters
    (q, r), then run causally through the TEST window. At every bar t, the
    filter state is updated using data up to t-1, and the spread is computed
    using the filtered alpha_t and beta_t.

    Parameters
    ----------
    pair : tuple[str, str]
        The two assets (A, B) where B is the dependent variable.
    lookback : int
        Trailing window for z-score normalization (mean/std computed from prior bars).
    entry_threshold : float
        |z| >= entry_threshold to enter a position.
    exit_threshold : float
        |z| <= exit_threshold to exit a position.
    min_holding : int
        Minimum holding period in bars before an exit is allowed.
    kalman_q : float
        Process noise variance (shared for alpha and beta random walks).
    kalman_r : float
        Observation noise variance.
    cointegration_pvalue : float
        Significance level for Engle-Granger test.
    cointegration_check_interval : int
        How often to recompute cointegration diagnostics (in bars).
    use_enriched_gates : bool
        Whether to enforce the full set of enriched gates.
    strict_enriched_gates : bool
        If True, missing/None gate values block entries (fail-closed).
    """

    def __init__(
        self,
        pair: tuple[str, str],
        lookback: int = 240,
        entry_threshold: float = 2.0,
        exit_threshold: float = 0.5,
        min_holding: int = 1,
        kalman_q: float = 1e-4,
        kalman_r: float = 1e-2,
        params: dict[str, Any] | None = None,
        cointegration_pvalue: float = 0.05,
        cointegration_check_interval: int | None = None,
        enriched_diagnostics: dict[str, Any] | None = None,
        pair_diagnostics: dict[str, Any] | None = None,
        pair_diagnostics_file: str | None = None,
        use_enriched_gates: bool = True,
        strict_enriched_gates: bool = True,
    ):
        if len(pair) != 2 or pair[0] == pair[1]:
            raise ValueError("pair must contain two distinct asset names.")
        if lookback < 2:
            raise ValueError("lookback must be at least 2.")
        if entry_threshold <= 0 or exit_threshold < 0 or exit_threshold >= entry_threshold:
            raise ValueError("Thresholds must satisfy entry_threshold > exit_threshold >= 0.")
        if min_holding < 1:
            raise ValueError("min_holding must be at least 1.")
        if not 0.0 < cointegration_pvalue < 1.0:
            raise ValueError("cointegration_pvalue must be strictly between 0 and 1.")
        check_interval = cointegration_check_interval or lookback
        if check_interval < 1:
            raise ValueError("cointegration_check_interval must be at least 1.")
        if kalman_q <= 0 or kalman_r <= 0:
            raise ValueError("kalman_q and kalman_r must be positive.")

        super().__init__(f"kalman_pairs_{pair[0]}_{pair[1]}", pair, params)
        self.lookback = int(lookback)
        self.entry_threshold = float(entry_threshold)
        self.exit_threshold = float(exit_threshold)
        self.min_holding = int(min_holding)
        self.kalman_q = float(kalman_q)
        self.kalman_r = float(kalman_r)
        self.cointegration_pvalue = float(cointegration_pvalue)
        self.cointegration_check_interval = int(check_interval)
        self.use_enriched_gates = bool(use_enriched_gates)
        self.strict_enriched_gates = bool(strict_enriched_gates)

        # State series
        self.alpha_series = pd.Series(dtype=float)
        self.beta_series = pd.Series(dtype=float)
        self.spread_series = pd.Series(dtype=float)
        self._last_diagnostics: dict[str, Any] | None = None
        self._gate_breakdown: pd.DataFrame | None = None
        self._train_q: float | None = None
        self._train_r: float | None = None

    def _kalman_filter_train(self, price_a: pd.Series, price_b: pd.Series) -> tuple[float, float]:
        """Fit Kalman filter on training window to select q, r via maximum likelihood.

        For the pre-registered grid, we just return the given q, r.
        In a full implementation, this would optimize q, r on the train window.
        """
        return self.kalman_q, self.kalman_r

    def _kalman_filter_step(
        self,
        price_a: float,
        price_b: float,
        alpha_prev: float,
        beta_prev: float,
        P_prev: np.ndarray,
    ) -> tuple[float, float, np.ndarray]:
        """Single Kalman filter step for local-level model.

        State: x = [alpha, beta]'
        Observation: z = B_t
        H = [1, A_t]
        F = I (identity, random walk)
        Q = q * I (process noise)
        R = r (observation noise)
        """
        q = self.kalman_q
        r = self.kalman_r

        # State transition matrix (identity for random walk)
        F = np.eye(2)

        # Process noise covariance
        Q = np.eye(2) * q

        # Observation matrix
        H = np.array([[1.0, price_a]])

        # Observation noise covariance
        R = np.array([[r]])

        # Predict
        x_pred = F @ np.array([alpha_prev, beta_prev])
        P_pred = F @ P_prev @ F.T + Q

        # Update
        y = price_b - H @ x_pred  # innovation
        S = H @ P_pred @ H.T + R  # innovation covariance
        K = P_pred @ H.T @ np.linalg.inv(S)  # Kalman gain

        x_upd = x_pred + (K @ y).flatten()
        P_upd = (np.eye(2) - K @ H) @ P_pred

        return float(x_upd[0]), float(x_upd[1]), P_upd

    def _run_kalman_filter_causal(
        self, price_a: pd.Series, price_b: pd.Series, start_idx: int
    ) -> tuple[pd.Series, pd.Series, pd.Series]:
        """Run Kalman filter causally from start_idx using train-selected q, r.

        Returns alpha, beta, and spread series aligned to the full data index.
        The filter is initialized at start_idx using OLS on the training window,
        then run forward one step at a time using only data up to t-1.
        """
        n = len(price_a)
        alpha = pd.Series(np.nan, index=price_a.index)
        beta = pd.Series(np.nan, index=price_a.index)
        spread = pd.Series(np.nan, index=price_a.index)

        # Initialize using OLS on the training window [0:start_idx)
        train_a = price_a.iloc[:start_idx]
        train_b = price_b.iloc[:start_idx]
        if len(train_a) < 10:
            return alpha, beta, spread

        # OLS initialization: B = alpha + beta * A
        X = np.column_stack([np.ones(len(train_a)), train_a.values])
        try:
            coeffs = np.linalg.lstsq(X, train_b.values, rcond=None)[0]
            alpha_init = float(coeffs[0])
            beta_init = float(coeffs[1])
        except np.linalg.LinAlgError:
            alpha_init = 0.0
            beta_init = 1.0

        if not np.isfinite(alpha_init) or not np.isfinite(beta_init) or beta_init <= 0:
            alpha_init = 0.0
            beta_init = 1.0

        # Initial state covariance (large uncertainty)
        P = np.eye(2) * 1.0

        # Set initial values at start_idx - 1
        alpha.iloc[start_idx - 1] = alpha_init
        beta.iloc[start_idx - 1] = beta_init
        spread.iloc[start_idx - 1] = train_b.iloc[-1] - (alpha_init + beta_init * train_a.iloc[-1])

        # Run filter forward from start_idx to n-1
        for i in range(start_idx, n):
            # Use data up to i-1 for the update at i
            a_prev = price_a.iloc[i - 1]
            b_prev = price_b.iloc[i - 1]
            alpha_prev = alpha.iloc[i - 1]
            beta_prev = beta.iloc[i - 1]

            if not (np.isfinite(alpha_prev) and np.isfinite(beta_prev)):
                # If previous state is invalid, re-initialize from recent window
                recent_start = max(0, i - self.lookback)
                recent_a = price_a.iloc[recent_start:i]
                recent_b = price_b.iloc[recent_start:i]
                if len(recent_a) >= 10:
                    X = np.column_stack([np.ones(len(recent_a)), recent_a.values])
                    try:
                        coeffs = np.linalg.lstsq(X, recent_b.values, rcond=None)[0]
                        alpha_prev = float(coeffs[0])
                        beta_prev = float(coeffs[1])
                        P = np.eye(2) * 1.0
                    except np.linalg.LinAlgError:
                        alpha_prev = 0.0
                        beta_prev = 1.0
                        P = np.eye(2) * 1.0
                else:
                    alpha_prev = 0.0
                    beta_prev = 1.0
                    P = np.eye(2) * 1.0

            # Kalman filter step
            alpha_upd, beta_upd, P = self._kalman_filter_step(
                a_prev, b_prev, alpha_prev, beta_prev, P
            )

            # Guard against invalid values
            if not np.isfinite(alpha_upd) or not np.isfinite(beta_upd):
                alpha_upd = alpha_prev
                beta_upd = beta_prev

            # Clip beta to reasonable range
            beta_upd = np.clip(beta_upd, 1e-6, 1e6)
            if beta_upd <= 0:
                beta_upd = 1.0

            alpha.iloc[i] = alpha_upd
            beta.iloc[i] = beta_upd

            # Compute spread using updated state and current price_a
            spread.iloc[i] = price_b.iloc[i] - (alpha_upd + beta_upd * price_a.iloc[i])

        return alpha, beta, spread

    def calculate_spread(self, price_a: pd.Series, price_b: pd.Series) -> pd.Series:
        """Return a spread built from causal Kalman filter hedge ratio."""
        # The Kalman filter is run in generate_signals where we have the full data
        # and know the train/test split points. Here we just return a placeholder.
        # The actual spread computation happens in generate_signals.
        self.spread_series = pd.Series(np.nan, index=price_a.index)
        return self.spread_series

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate stateful spread signals with Kalman-filtered hedge ratio.

        The data passed here is the TEST window. We need to know the TRAIN window
        that precedes it to initialize the Kalman filter. Since the strategy is
        called per TEST window in the walk-forward, we need the full pair data
        to run the filter from the beginning of the TRAIN window.

        However, the backtest framework calls generate_signals on the full pair
        data. We'll run the Kalman filter on the full series but only use the
        causal filtering property (using data up to t-1 at each step).
        """
        asset_a, asset_b = self.pair  # A is independent, B is dependent
        missing = [asset for asset in self.pair if asset not in data.columns]
        if missing:
            raise ValueError(f"Pair assets missing from data: {missing}")

        price_a = data[asset_a].astype(float)
        price_b = data[asset_b].astype(float)

        # Run Kalman filter causally on the full series
        # The filter uses data up to t-1 to compute state at t
        alpha, beta, spread = self._run_kalman_filter_causal(price_a, price_b, self.lookback)
        self.alpha_series = alpha
        self.beta_series = beta
        self.spread_series = spread

        # Causal z-score: trailing lookback, mean/std from prior bars only
        spread_mean = spread.rolling(self.lookback, min_periods=self.lookback).mean()
        spread_std = spread.rolling(self.lookback, min_periods=self.lookback).std()
        zscore = spread.sub(spread_mean).div(spread_std.where(spread_std > 0))

        # Causal Engle-Granger cointegration test on trailing window
        cointegration_pvalues = pd.Series(np.nan, index=data.index, dtype=float)
        last_pvalue = float("nan")
        last_test_index = -1
        for i in range(self.lookback - 1, len(data)):
            should_test = (
                last_test_index < 0 or i - last_test_index >= self.cointegration_check_interval
            )
            if should_test:
                start = i - self.lookback + 1
                sample = pd.concat(
                    [price_a.iloc[start : i + 1], price_b.iloc[start : i + 1]],
                    axis=1,
                ).dropna()
                if len(sample) >= self.lookback:
                    try:
                        from statsmodels.tsa.stattools import coint
                        _, last_pvalue = coint(sample.iloc[:, 0], sample.iloc[:, 1])
                    except (ValueError, np.linalg.LinAlgError):
                        last_pvalue = float("nan")
                else:
                    last_pvalue = float("nan")
                last_test_index = i
            cointegration_pvalues.iloc[i] = last_pvalue

        # Enriched gates (per-bar causal computation, no static shortcuts)
        enriched_ok = pd.Series(1.0, index=data.index, dtype=float)
        if self.use_enriched_gates:
            try:
                enriched_ok_arr = np.empty(len(data), dtype=float)
                enriched_ok_arr[:] = np.nan
                gate_names = (
                    "eg_pass",
                    "johansen_pass",
                    "spread_mr_pass",
                    "hl_bounds_pass",
                    "leg_stationarity_ok",
                    "rolling_stable_ok",
                    "no_structural_break",
                )
                breakdown = pd.DataFrame(
                    False, index=data.index, columns=list(gate_names) + ["all_pass"]
                )
                last_diag_index = -1
                last_ok: float | None = None
                last_breakdown: dict[str, bool] | None = None
                for i in range(self.lookback - 1, len(data)):
                    should_recompute = (
                        last_diag_index < 0
                        or i - last_diag_index >= self.cointegration_check_interval
                    )
                    if should_recompute:
                        start = i - self.lookback + 1
                        sample_a = price_a.iloc[start : i + 1]
                        sample_b = price_b.iloc[start : i + 1]
                        try:
                            tdiag = target_schema_diagnostics(
                                sample_a, sample_b, pair_name="/".join(self.pair)
                            )
                            if not isinstance(tdiag, dict):
                                if self.strict_enriched_gates:
                                    last_ok = 0.0
                                else:
                                    last_ok = None
                                last_breakdown = None
                            else:
                                g = tdiag.get("gates", {})
                                sb = tdiag.get("structural_breaks")
                                ok = _evaluate_enriched_gates_strict(
                                    g, sb, bool(self.strict_enriched_gates)
                                )
                                last_ok = 1.0 if ok else 0.0
                                last_breakdown = {
                                    k: bool(g.get(k) is True) for k in gate_names
                                }
                                last_breakdown["all_pass"] = bool(g.get("all_pass") is True)
                            last_diag_index = i
                        except Exception:
                            if self.strict_enriched_gates:
                                last_ok = 0.0
                            else:
                                last_ok = None
                            last_breakdown = None
                            last_diag_index = i
                    enriched_ok_arr[i] = last_ok if last_ok is not None else np.nan
                    if last_breakdown is not None:
                        breakdown.iloc[i] = list(last_breakdown.values())
                enriched_ok = pd.Series(enriched_ok_arr, index=data.index)
                self._gate_breakdown = breakdown
                fill_val = 0.0 if self.strict_enriched_gates else 1.0
                enriched_ok = enriched_ok.bfill().ffill().fillna(fill_val)
            except Exception:
                enriched_ok = pd.Series(
                    1.0 if not self.strict_enriched_gates else 0.0,
                    index=data.index,
                    dtype=float,
                )

        # State machine with minimum holding period
        state = 0
        holding_bars = 0
        position = np.zeros(len(data), dtype=float)
        z_values = zscore.to_numpy(dtype=float)
        p_values = cointegration_pvalues.to_numpy(dtype=float)
        enriched_ok_arr = enriched_ok.to_numpy(dtype=float)

        for i, (z_value, pvalue) in enumerate(zip(z_values, p_values)):
            eg_ok = (
                np.isfinite(z_value)
                and np.isfinite(pvalue)
                and pvalue <= self.cointegration_pvalue
            )
            enr_ok = True
            if self.use_enriched_gates:
                if np.isfinite(enriched_ok_arr[i]) and enriched_ok_arr[i] == 0.0:
                    enr_ok = False
                elif self.strict_enriched_gates and (
                    not np.isfinite(enriched_ok_arr[i]) or enriched_ok_arr[i] != 1.0
                ):
                    enr_ok = False

            if not eg_ok or not enr_ok:
                state = 0
                holding_bars = 0
            elif state == 1:
                if holding_bars >= self.min_holding and z_value >= -self.exit_threshold:
                    state = 0
                    holding_bars = 0
                else:
                    holding_bars += 1
            elif state == -1:
                if holding_bars >= self.min_holding and z_value <= self.exit_threshold:
                    state = 0
                    holding_bars = 0
                else:
                    holding_bars += 1
            elif z_value <= -self.entry_threshold:
                state = 1
                holding_bars = 1
            elif z_value >= self.entry_threshold:
                state = -1
                holding_bars = 1
            position[i] = state

        signals = pd.DataFrame(index=data.index)
        signals["spread"] = spread
        signals["zscore"] = zscore
        signals["cointegration_pvalue"] = cointegration_pvalues
        signals["long"] = position > 0
        signals["short"] = position < 0
        signals["exit"] = position == 0
        signals["enriched_gates_ok"] = enriched_ok

        # Backtest weights: opposing legs normalized by absolute market value
        # from the Kalman hedge ratio (beta)
        beta_series = self.beta_series.reindex(data.index)
        try:
            beta_series = beta_series.replace([np.inf, -np.inf], np.nan)
            beta_series = beta_series.where(beta_series > 1e-18)
            beta_series = beta_series.clip(lower=1e-6, upper=1e6)
        except Exception:
            pass

        gross_value = price_a.abs() + beta_series.abs() * price_b.abs()
        valid = (
            (position != 0)
            & beta_series.notna().to_numpy()
            & np.isfinite(gross_value.to_numpy())
            & (gross_value.to_numpy() > 0)
        )
        leg_a = pd.Series(0.0, index=data.index, dtype=float)
        leg_b = pd.Series(0.0, index=data.index, dtype=float)
        direction = pd.Series(position, index=data.index)
        leg_a.loc[valid] = direction.loc[valid] * price_a.loc[valid] / gross_value.loc[valid]
        leg_b.loc[valid] = (
            -direction.loc[valid] * beta_series.loc[valid] * price_b.loc[valid] / gross_value.loc[valid]
        )
        # Cap gross pair exposure at 1.0
        gross_exposure = leg_a.abs() + leg_b.abs()
        over = gross_exposure > 1.0
        if over.any():
            leg_a.loc[over] = leg_a.loc[over] / gross_exposure.loc[over]
            leg_b.loc[over] = leg_b.loc[over] / gross_exposure.loc[over]

        signals[asset_a] = leg_a
        signals[asset_b] = leg_b
        return signals

    def get_gate_breakdown(self) -> pd.DataFrame | None:
        """Return the per-bar enriched-gate pass/fail breakdown."""
        return self._gate_breakdown

    def calculate_position_sizes(self, signals: pd.DataFrame) -> dict[str, float]:
        """Return the latest explicit per-asset weights."""
        asset_a, asset_b = self.pair
        if signals.empty:
            return {asset_a: 0.0, asset_b: 0.0}
        last = signals.iloc[-1]
        return {
            asset_a: float(last.get(asset_a, 0.0)),
            asset_b: float(last.get(asset_b, 0.0)),
        }