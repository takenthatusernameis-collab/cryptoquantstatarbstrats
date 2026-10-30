"""
Backtesting framework for statistical arbitrage strategies
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from strategies.base import Strategy
from utils.attribution import brinson_attribution, factor_attribution
from utils.metrics import cvar, sharpe_ratio, sortino_ratio, var
from utils.rebalance import create_rebalanced_weights
from utils.regime import detect_regimes, volatility_regime


def _infer_periods_per_year(index: pd.Index) -> int:
    """Infer annualization from timestamp spacing; default to daily market data."""
    if not isinstance(index, pd.DatetimeIndex) or len(index) < 3:
        return 252
    seconds = index.to_series().diff().dt.total_seconds().dropna()
    seconds = seconds[seconds > 0]
    if seconds.empty:
        return 252
    median_seconds = float(seconds.median())
    if not np.isfinite(median_seconds) or median_seconds <= 0:
        return 252
    seconds_per_year = 365.25 * 24.0 * 60.0 * 60.0
    return int(max(1, min(round(seconds_per_year / median_seconds), 525600)))


def _resolve_anchor_index(anchor: Any, data: pd.DataFrame) -> int:
    """Resolve ``anchor`` to the starting row index for walk-forward windows.

    ``anchor`` may be ``None`` (start of the data), an integer row offset, or a
    timestamp string / ``pandas.Timestamp`` located via ``index.searchsorted``.
    Booleans, non-integral floats, and unparseable timestamp strings are
    rejected outright instead of being silently coeried to the origin.
    """
    if anchor is None:
        return 0
    if isinstance(anchor, bool):
        raise ValueError(
            "anchor must be None, an integer row offset, or a timestamp string; got bool"
        )
    if isinstance(anchor, (int, np.integer)):
        i = int(anchor)
    elif isinstance(anchor, float):
        if not anchor.is_integer():
            raise ValueError("anchor must be an integer row offset or a timestamp string")
        i = int(anchor)
    elif isinstance(anchor, str):
        # Try to parse as integer first (for CLI numeric strings like "0", "40")
        s = anchor.strip()
        # Check if it's all digits possibly with sign
        try:
            # Try int conversion
            # Avoid treating timestamps like "2024-01-01" as ints
            if s.lstrip('-+').isdigit():
                i = int(s)
            else:
                try:
                    ts = pd.Timestamp(anchor)
                    i = int(data.index.searchsorted(ts))
                except Exception as exc:
                    raise ValueError(
                        f"anchor could not be parsed as a timestamp: {anchor!r}"
                    ) from exc
        except ValueError:
            try:
                ts = pd.Timestamp(anchor)
                i = int(data.index.searchsorted(ts))
            except Exception as exc:
                raise ValueError(
                    f"anchor could not be parsed as a timestamp: {anchor!r}"
                ) from exc
    else:
        try:
            ts = pd.Timestamp(anchor)
            i = int(data.index.searchsorted(ts))
        except Exception as exc:
            raise ValueError(
                f"anchor could not be parsed as a timestamp: {anchor!r}"
            ) from exc
    if i < 0:
        return 0
    return i



class BacktestEngine:
    """Backtesting engine for trading strategies."""

    def __init__(self, initial_capital: float = 100000.0):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions: dict[str, float] = {}
        self.trades: list[dict[str, Any]] = []
        self.equity_curve: list[float] = []

    def _apply_regime_gating(
        self,
        weights: pd.DataFrame,
        data: pd.DataFrame,
        regime_signal: Any = None,
        regime_mode: str | None = None,
        regime_lookback: int | None = None,
        regime_vol_mode: str | None = None,
    ) -> pd.DataFrame:
        if regime_signal is None and regime_mode is None and regime_vol_mode is None:
            return weights

        w = weights.copy()
        mask = None

        if regime_signal is not None:
            if isinstance(regime_signal, (pd.Series, pd.DataFrame)):
                rs = regime_signal
                if isinstance(rs, pd.DataFrame):
                    # If multiple columns, OR/any True where any allows? Or just take first aligned
                    # Or check if all True means allowed; alternatively treat as boolean per period
                    rs = rs.reindex(index=w.index).fillna(True)
                    if rs.shape[1] == 1:
                        rs_series = rs.iloc[:, 0]
                    else:
                        # If any column is True, treat as allowed (permissive).
                        rs_series = rs.any(axis=1)
                else:
                    rs_series = rs.reindex(index=w.index)
                # Normalize to boolean: True means allowed to trade
                try:
                    mask = rs_series.astype(bool)
                except Exception:
                    mask = pd.Series(True, index=w.index)
            else:
                # Assume scalar True/False
                try:
                    allowed = bool(regime_signal)
                except Exception:
                    allowed = True
                if not allowed:
                    mask = pd.Series(False, index=w.index)
                else:
                    mask = None

        if mask is None and regime_mode is not None:
            lb = int(regime_lookback) if regime_lookback is not None and regime_lookback > 0 else 20
            try:
                regimes = detect_regimes(data, window=lb)
            except Exception:
                regimes = None
            if regimes is not None and not regimes.empty:
                trend_cols = [c for c in regimes.columns if c.endswith("_trend")]
                if trend_cols:
                    trend_mask = regimes[trend_cols].abs().sum(axis=1) > 0
                    mask = trend_mask
                else:
                    vol_cols = [c for c in regimes.columns if c.endswith("_vol_regime")]
                    if vol_cols:
                        mask = pd.Series(True, index=w.index)
            else:
                mask = None

        if regime_vol_mode is not None:
            lb = int(regime_lookback) if regime_lookback is not None and regime_lookback > 0 else 20
            # gate to low-volatility regimes using volatility_regime
            try:
                vol_mask = pd.Series(True, index=w.index)
                for col in data.columns:
                    vr = volatility_regime(data[col], window=lb)
                    try:
                        is_low = vr == vr.min() if hasattr(vr, "min") else vr == 0
                    except Exception:
                        is_low = vr == 0
                    vol_mask = vol_mask & is_low.reindex(index=w.index).fillna(True).astype(bool)
                if mask is None:
                    mask = vol_mask
                else:
                    mask = mask & vol_mask
            except Exception:
                pass

        if mask is not None:
            mask = mask.reindex(index=w.index).fillna(True)
            # Gate: zero weights when not allowed
            w = w.where(mask, 0.0)
        return w.fillna(0.0)

    def _evaluate_weights(
        self,
        weights: pd.DataFrame,
        data: pd.DataFrame,
        fee_rate: float = 0.0,
        slippage: float = 0.0,
        risk_manager: Any = None,
        cost_model: Any = None,
        execution_simulator: Any = None,
        volume: pd.DataFrame | None = None,
        high: pd.DataFrame | None = None,
        low: pd.DataFrame | None = None,
        regime_signal: Any = None,
        regime_mode: str | None = None,
        regime_lookback: int | None = None,
        regime_vol_mode: str | None = None,
        benchmark_weights: pd.DataFrame | None = None,
        factor_returns: pd.DataFrame | None = None,
        weights_are_targets: bool = True,
        circuit_breaker: Any = None,
    ) -> dict[str, Any]:
        """Core backtest computation given a (pre-computed) weights DataFrame.

        Aligns ``weights`` to ``data``, optionally applies risk management,
        subtracts transaction costs from turnover, and returns the standard
        result dictionary. This is shared by :meth:`run` and
        :meth:`run_portfolio`.

        When ``benchmark_weights`` is provided, Brinson-style allocation /
        selection / interaction attribution is computed against the benchmark.
        When ``factor_returns`` is provided, an OLS factor attribution
        (alpha / beta / residual) is computed on the portfolio returns.

        When a ``circuit_breaker`` is supplied it is evaluated per bar against
        the running equity curve computed so far, so it can force full
        de-risking (zero weights) once the trailing drawdown breaches the
        configured threshold.
        """
        returns = data.pct_change().fillna(0.0)

        # Align weights to data: reindex to data index/columns, fill NaN with 0.
        weights = (
            weights.reindex(index=data.index, columns=data.columns, fill_value=0.0)
            .fillna(0.0)
        )

        # Apply regime gating if provided
        weights = self._apply_regime_gating(
            weights,
            data,
            regime_signal=regime_signal,
            regime_mode=regime_mode,
            regime_lookback=regime_lookback,
            regime_vol_mode=regime_vol_mode,
        )

        # Apply risk management if provided
        if risk_manager is not None:
            try:
                weights = risk_manager.max_position_size(weights, self.capital)
            except Exception:
                pass

        # Signals/target weights calculated from bar t close cannot earn the
        # return that ended at bar t. Execute them from the next bar instead.
        if weights_are_targets:
            weights = weights.shift(1).fillna(0.0)

        if execution_simulator is not None:
            portfolio_returns, cost = self._simulate_execution(
                weights, data, returns, execution_simulator, volume=volume, high=high, low=low
            )
        else:
            portfolio_returns = (weights * returns).sum(axis=1)

            # Apply transaction costs: fees and slippage on turnover
            turnover = weights.diff().abs().sum(axis=1).fillna(0.0)
            # Initial turnover (first row has no diff).
            if len(turnover) > 0:
                turnover.iloc[0] = float(weights.iloc[0].abs().sum())
            if cost_model is not None:
                cost = cost_model.compute_cost_series(turnover, self.capital)
            else:
                cost = turnover * (fee_rate + slippage)
        portfolio_returns = portfolio_returns - cost

        cumulative_returns = (1.0 + portfolio_returns).cumprod()

        # Per-bar dynamic drawdown circuit breaker. We recompute weights and
        # costs bar-by-bar so the breaker can react to the equity path as it
        # is being built. When the breaker trips, all subsequent weights are
        # forced to zero (full de-risking) and the breaker stays tripped.
        if circuit_breaker is not None:
            try:
                cb_weights = weights.copy()
                cb_turnover = turnover.copy() if 'turnover' in locals() else None
                cb_cost = cost.copy() if 'cost' in locals() else None
                cb_returns = portfolio_returns.copy()
                cb_equity = pd.Series(1.0, index=weights.index, dtype=float)
                running_peak = 1.0
                tripped = False
                for i in range(len(weights)):
                    if tripped:
                        cb_weights.iloc[i] = 0.0
                        if cb_turnover is not None:
                            cb_turnover.iloc[i] = float(cb_weights.iloc[i].abs().sum())
                    else:
                        # Evaluate breaker against equity up to previous bar.
                        prev_equity = cb_equity.iloc[i - 1] if i > 0 else 1.0
                        running_peak = max(running_peak, prev_equity)
                        if prev_equity > 0:
                            dd = prev_equity / running_peak - 1.0
                        else:
                            dd = 0.0
                        if circuit_breaker.breached(dd):
                            tripped = True
                            cb_weights.iloc[i] = 0.0
                            if cb_turnover is not None:
                                cb_turnover.iloc[i] = float(cb_weights.iloc[i].abs().sum())
                    # Recompute this bar's return with possibly zeroed weights.
                    if cb_turnover is not None and cb_cost is not None:
                        if cost_model is not None:
                            cb_cost.iloc[i] = float(cost_model.compute_cost_series(
                                cb_turnover.iloc[[i]], self.capital
                            ))
                        else:
                            cb_cost.iloc[i] = float(cb_turnover.iloc[i] * (fee_rate + slippage))
                        cb_returns.iloc[i] = float((cb_weights.iloc[i] * returns.iloc[i]).sum()) - float(cb_cost.iloc[i])
                    else:
                        cb_returns.iloc[i] = float((cb_weights.iloc[i] * returns.iloc[i]).sum())
                    cb_equity.iloc[i] = float(cb_equity.iloc[i - 1] * (1.0 + cb_returns.iloc[i])) if i > 0 else float(1.0 + cb_returns.iloc[i])
                portfolio_returns = cb_returns
                cumulative_returns = cb_equity
                weights = cb_weights
            except Exception:
                pass

        total_return = float(cumulative_returns.iloc[-1] - 1.0)
        periods_per_year = _infer_periods_per_year(data.index)
        sharpe = sharpe_ratio(portfolio_returns, periods_per_year=periods_per_year)
        running_max = cumulative_returns.cummax()
        drawdown = cumulative_returns / running_max - 1.0
        max_drawdown = float(drawdown.min())

        # Compute max drawdown duration
        max_dd_duration = 0
        if len(drawdown) > 0:
            in_drawdown = False
            dd_start = 0
            for i in range(len(drawdown)):
                if drawdown.iloc[i] < 0:
                    if not in_drawdown:
                        in_drawdown = True
                        dd_start = i
                else:
                    if in_drawdown:
                        dd_duration = i - dd_start
                        if dd_duration > max_dd_duration:
                            max_dd_duration = dd_duration
                        in_drawdown = False
            if in_drawdown:
                dd_duration = len(drawdown) - dd_start
                if dd_duration > max_dd_duration:
                    max_dd_duration = dd_duration

        # Compute Calmar ratio
        if max_drawdown < 0:
            observed_periods = max(len(portfolio_returns) - 1, 1)
            if total_return > -1.0:
                annualized_return = (1.0 + total_return) ** (
                    periods_per_year / observed_periods
                ) - 1.0
            else:
                annualized_return = total_return
            calmar_ratio = annualized_return / abs(max_drawdown)
        else:
            calmar_ratio = 0.0

        # Compute advanced risk metrics
        sortino = sortino_ratio(
            portfolio_returns, periods_per_year=periods_per_year
        )
        var_95 = var(portfolio_returns, confidence=0.95)
        cvar_95 = cvar(portfolio_returns, confidence=0.95)

        self.equity_curve = [float(x) for x in cumulative_returns]
        self.positions = weights.iloc[-1].to_dict() if len(weights) else {}

        result = {
            "total_return": total_return,
            "sharpe_ratio": sharpe,
            "max_drawdown": max_drawdown,
            "max_drawdown_duration": int(max_dd_duration),
            "calmar_ratio": float(calmar_ratio),
            "sortino_ratio": float(sortino),
            "var": float(var_95),
            "cvar": float(cvar_95),
            "equity_curve": cumulative_returns,
            "weights": weights,
            "portfolio_returns": portfolio_returns,
            "returns": portfolio_returns,
        }

        # Optional Brinson attribution vs a benchmark.
        if benchmark_weights is not None:
            try:
                result["brinson"] = brinson_attribution(
                    returns,
                    weights,
                    benchmark_weights,
                    returns,
                )
            except Exception:
                pass

        # Optional OLS factor attribution on portfolio returns.
        if factor_returns is not None:
            try:
                result["factor"] = factor_attribution(
                    portfolio_returns, factor_returns
                )
            except Exception:
                pass

        return result

    def _simulate_execution(
        self,
        weights: pd.DataFrame,
        data: pd.DataFrame,
        returns: pd.DataFrame,
        execution_simulator: Any,
        volume: pd.DataFrame | None = None,
        high: pd.DataFrame | None = None,
        low: pd.DataFrame | None = None,
    ) -> tuple[pd.Series, pd.Series]:
        """Simulate order execution per period using ``execution_simulator``.

        Converts each period's target weight change into dollar orders, simulates
        each fill (applying slippage and volume participation constraints), and
        tracks the actually executed positions. The portfolio return for a period
        is earned by the executed position held through that period, and slippage
        costs are returned as a per-period cost series (fraction of capital).

        When the simulator fills only part of an order, the unfilled portion is
        not carried into the position, so the executed weight drifts from the
        target. This path only runs when an ``execution_simulator`` is supplied;
        the legacy cost model is used otherwise, keeping the default behavior
        unchanged.
        """
        capital = self.capital
        portfolio_returns = pd.Series(0.0, index=weights.index, dtype=float)
        cost = pd.Series(0.0, index=weights.index, dtype=float)
        prev_executed = pd.Series(0.0, index=weights.columns, dtype=float)

        for i in range(len(weights)):
            target_dollars = weights.iloc[i] * capital
            prices = data.iloc[i]
            period_rets = returns.iloc[i]
            new_executed = prev_executed.copy()
            period_cost = 0.0

            for asset in weights.columns:
                try:
                    target_d = float(target_dollars.get(asset, 0.0))
                    prev_d = float(prev_executed.get(asset, 0.0))
                except (TypeError, ValueError):
                    continue
                if not np.isfinite(target_d) or not np.isfinite(prev_d):
                    continue
                trade_dollars = target_d - prev_d
                if trade_dollars == 0.0:
                    continue
                try:
                    price = float(prices.get(asset, 0.0))
                except (TypeError, ValueError):
                    continue
                if not np.isfinite(price) or price <= 0.0:
                    continue

                side = "buy" if trade_dollars > 0.0 else "sell"
                qty = abs(trade_dollars) / price
                bar_volume = 0.0
                if volume is not None:
                    try:
                        bar_volume = float(volume.iloc[i].get(asset, 0.0))
                    except (TypeError, ValueError, AttributeError):
                        bar_volume = 0.0
                bar_high = None
                bar_low = None
                if high is not None:
                    try:
                        bar_high = float(high.iloc[i].get(asset, np.nan))
                        if not np.isfinite(bar_high):
                            bar_high = None
                    except (TypeError, ValueError, AttributeError):
                        bar_high = None
                if low is not None:
                    try:
                        bar_low = float(low.iloc[i].get(asset, np.nan))
                        if not np.isfinite(bar_low):
                            bar_low = None
                    except (TypeError, ValueError, AttributeError):
                        bar_low = None
                order_type = getattr(execution_simulator, "order_type", "market")
                fill = execution_simulator.simulate_order(
                    order_type,
                    side,
                    qty,
                    price,
                    bar_volume=bar_volume,
                    bar_high=bar_high,
                    bar_low=bar_low,
                )
                try:
                    filled_qty = float(fill["filled_qty"])
                    avg_price = float(fill["avg_price"])
                except (TypeError, ValueError, KeyError):
                    continue
                if not np.isfinite(filled_qty) or not np.isfinite(avg_price) or avg_price <= 0.0:
                    continue

                filled_dollars = filled_qty * avg_price
                new_executed[asset] = prev_d + filled_dollars
                period_cost += abs(filled_qty) * abs(avg_price - price)

            portfolio_returns.iloc[i] = float((new_executed * period_rets).sum()) / capital
            cost.iloc[i] = period_cost / capital
            prev_executed = new_executed

        return portfolio_returns, cost

    @staticmethod
    def _align_optimizer_result(
        w_opt: Any, train_data: pd.DataFrame, train_index: pd.Index
    ) -> pd.DataFrame:
        """Align an optimizer result (Series or DataFrame) to a target window.

        Used both for the out-of-sample test window and the in-sample train
        window in :meth:`walk_forward_portfolio`. A Series result is a single
        target estimated from the training window and applied (forward-filled)
        throughout the target window.
        """
        if isinstance(w_opt, pd.Series):
            aligned = w_opt.reindex(train_data.columns).fillna(0.0)
            return pd.DataFrame(
                [aligned.to_numpy(dtype=float)],
                columns=train_data.columns,
                index=[train_index[0]],
            )
        if isinstance(w_opt, pd.DataFrame):
            if w_opt.empty:
                raise ValueError("Optimizer returned an empty weights DataFrame.")
            w_df = w_opt.reindex(columns=train_data.columns, fill_value=0.0)
            return w_df.reindex(index=train_index, method="ffill").fillna(0.0)
        raise TypeError(
            "Optimizer must return a pandas Series or DataFrame of weights."
        )

    def _evaluate_in_sample(
        self,
        strategy: Strategy | None,
        weights: pd.DataFrame | None,
        train_data: pd.DataFrame,
        volume: pd.DataFrame | None,
        high: pd.DataFrame | None,
        low: pd.DataFrame | None,
        reoptimize: bool,
        optimizer: Any,
        fee_rate: float,
        slippage: float,
        cost_model: Any,
        risk_manager: Any,
        execution_simulator: Any,
        regime_signal: Any,
        regime_mode: str | None,
        regime_lookback: int | None,
        regime_vol_mode: str | None,
        benchmark_weights: pd.DataFrame | None,
        factor_returns: pd.DataFrame | None,
    ) -> dict[str, float]:
        """Evaluate in-sample (train-window) performance, returning IS metrics.

        Returns a dict with ``is_total_return``, ``is_sharpe_ratio`` and
        ``is_max_drawdown``. Falls back to zeros if evaluation fails so that
        out-of-sample reporting is never broken by an IS computation.
        """
        out = {
            "is_total_return": 0.0,
            "is_sharpe_ratio": 0.0,
            "is_max_drawdown": 0.0,
        }
        try:
            train_index = train_data.index
            train_volume = volume.loc[train_index] if volume is not None else None
            train_high = high.loc[train_index] if high is not None else None
            train_low = low.loc[train_index] if low is not None else None

            if strategy is not None:
                # Strategy-based walk-forward: run the (already fit) strategy on
                # the train window to measure in-sample fit.
                is_result = self.run(
                    strategy,
                    train_data,
                    fee_rate=fee_rate,
                    slippage=slippage,
                    cost_model=cost_model,
                    risk_manager=risk_manager,
                    execution_simulator=execution_simulator,
                    volume=train_volume,
                    high=train_high,
                    low=train_low,
                    regime_signal=regime_signal,
                    regime_mode=regime_mode,
                    regime_lookback=regime_lookback,
                    regime_vol_mode=regime_vol_mode,
                    benchmark_weights=benchmark_weights,
                    factor_returns=factor_returns,
                )
            else:
                # Portfolio walk-forward: use the optimizer result on the train
                # window (when reoptimizing) or the supplied weights sliced to
                # the train window. Weights are treated as held positions, not
                # fresh targets, mirroring the out-of-sample run.
                if reoptimize and optimizer is not None:
                    w_opt = optimizer(train_data)
                    is_weights = self._align_optimizer_result(
                        w_opt, train_data, train_index
                    )
                else:
                    is_weights = (
                        weights.reindex(index=train_index).fillna(0.0)
                        if weights is not None
                        else pd.DataFrame(0.0, index=train_index, columns=train_data.columns)
                    )
                is_result = self.run_portfolio(
                    is_weights,
                    train_data,
                    fee_rate=fee_rate,
                    slippage=slippage,
                    cost_model=cost_model,
                    risk_manager=risk_manager,
                    execution_simulator=execution_simulator,
                    volume=train_volume,
                    high=train_high,
                    low=train_low,
                    regime_signal=regime_signal,
                    regime_mode=regime_mode,
                    regime_lookback=regime_lookback,
                    regime_vol_mode=regime_vol_mode,
                    benchmark_weights=benchmark_weights,
                    factor_returns=factor_returns,
                    weights_are_targets=False,
                )
            out["is_total_return"] = float(is_result.get("total_return", 0.0))
            out["is_sharpe_ratio"] = float(is_result.get("sharpe_ratio", 0.0))
            out["is_max_drawdown"] = float(is_result.get("max_drawdown", 0.0))
        except Exception:
            pass
        return out

    def _signals_to_weights(
        self, signals: pd.DataFrame, data: pd.DataFrame
    ) -> pd.DataFrame:
        """Convert strategy signals to target weights without overriding explicit legs."""
        weights = pd.DataFrame(0.0, index=data.index, columns=data.columns)

        # Explicit per-asset weights take precedence over generic long/short flags.
        weight_cols = [c for c in data.columns if c in signals.columns]
        if weight_cols:
            for asset in weight_cols:
                weights[asset] = signals[asset].reindex(data.index).fillna(0.0)
        elif "long" in signals.columns and "short" in signals.columns:
            long_mask = signals["long"].fillna(False).reindex(
                data.index, fill_value=False
            ).astype(bool)
            short_mask = signals["short"].fillna(False).reindex(
                data.index, fill_value=False
            ).astype(bool)
            for asset in data.columns:
                weights.loc[long_mask, asset] = 1.0
                weights.loc[short_mask, asset] = -1.0

        if "exit" in signals.columns:
            exit_mask = signals["exit"].fillna(False).reindex(
                data.index, fill_value=False
            ).astype(bool)
            weights.loc[exit_mask, :] = 0.0

        active = weights.abs().sum(axis=1).replace(0.0, np.nan)
        return weights.div(active, axis=0).fillna(0.0)

    def run(
        self,
        strategy: Strategy,
        data: pd.DataFrame,
        fee_rate: float = 0.0,
        slippage: float = 0.0,
        risk_manager: Any = None,
        cost_model: Any = None,
        execution_simulator: Any = None,
        volume: pd.DataFrame | None = None,
        high: pd.DataFrame | None = None,
        low: pd.DataFrame | None = None,
        rebalance_frequency: str | None = None,
        rebalance_offset: Any = None,
        regime_signal: Any = None,
        regime_mode: str | None = None,
        regime_lookback: int | None = None,
        regime_vol_mode: str | None = None,
        benchmark_weights: pd.DataFrame | None = None,
        factor_returns: pd.DataFrame | None = None,
    ) -> dict[str, Any]:
        """Run backtest for a given strategy.

        Transaction costs are computed from per-period turnover. When
        ``cost_model`` is provided it takes precedence over ``fee_rate`` and
        ``slippage``; otherwise the legacy linear model is used.
        """
        signals = strategy.generate_signals(data)

        weights = self._signals_to_weights(signals, data)

        if rebalance_frequency is not None:
            weights = create_rebalanced_weights(
                weights, data, freq=rebalance_frequency, offset=rebalance_offset
            )

        return self._evaluate_weights(
            weights,
            data,
            fee_rate=fee_rate,
            slippage=slippage,
            risk_manager=risk_manager,
            cost_model=cost_model,
            execution_simulator=execution_simulator,
            volume=volume,
            high=high,
            low=low,
            regime_signal=regime_signal,
            regime_mode=regime_mode,
            regime_lookback=regime_lookback,
            regime_vol_mode=regime_vol_mode,
            benchmark_weights=benchmark_weights,
            factor_returns=factor_returns,
        )

    def run_with_benchmark(
        self,
        strategy: Strategy,
        data: pd.DataFrame,
        fee_rate: float = 0.0,
        slippage: float = 0.0,
        risk_manager: Any = None,
        cost_model: Any = None,
        execution_simulator: Any = None,
        regime_signal: Any = None,
        regime_mode: str | None = None,
        regime_lookback: int | None = None,
        regime_vol_mode: str | None = None,
        benchmark_weights: pd.DataFrame | None = None,
        factor_returns: pd.DataFrame | None = None,
    ) -> dict[str, Any]:
        """Run backtest and include an equal-weighted buy-and-hold benchmark."""
        result = self.run(
            strategy,
            data,
            fee_rate=fee_rate,
            slippage=slippage,
            risk_manager=risk_manager,
            cost_model=cost_model,
            execution_simulator=execution_simulator,
            regime_signal=regime_signal,
            regime_mode=regime_mode,
            regime_lookback=regime_lookback,
            regime_vol_mode=regime_vol_mode,
            benchmark_weights=benchmark_weights,
            factor_returns=factor_returns,
        )
        pair_cols = list(getattr(strategy, "pair", None) or data.columns)
        pair_cols = [c for c in pair_cols if c in data.columns] or list(data.columns)
        pair_data = data[pair_cols]
        returns = pair_data.pct_change().fillna(0.0)
        n = pair_data.shape[1]
        if n == 0:
            bench_returns = pd.Series(0.0, index=data.index)
        else:
            bench_weights = pd.DataFrame(
                1.0 / n, index=data.index, columns=data.columns
            )
            bench_returns = (bench_weights * returns).sum(axis=1)
            turnover = bench_weights.diff().abs().sum(axis=1).fillna(0.0)
            # Initial entry turnover
            turnover.iloc[0] = float(bench_weights.iloc[0].abs().sum())
            if cost_model is not None:
                cost = cost_model.compute_cost_series(turnover, self.capital)
            else:
                cost = turnover * (fee_rate + slippage)
            bench_returns = bench_returns - cost

        bench_equity = (1.0 + bench_returns).cumprod()
        bench_total_return = float(bench_equity.iloc[-1] - 1.0) if len(bench_equity) else 0.0

        result["benchmark_total_return"] = bench_total_return
        result["benchmark_equity_curve"] = bench_equity
        return result

    def run_portfolio(
        self,
        weights: pd.DataFrame,
        data: pd.DataFrame,
        fee_rate: float = 0.0,
        slippage: float = 0.0,
        risk_manager: Any = None,
        cost_model: Any = None,
        execution_simulator: Any = None,
        volume: pd.DataFrame | None = None,
        high: pd.DataFrame | None = None,
        low: pd.DataFrame | None = None,
        rebalance_frequency: str | None = None,
        rebalance_offset: Any = None,
        regime_signal: Any = None,
        regime_mode: str | None = None,
        regime_lookback: int | None = None,
        regime_vol_mode: str | None = None,
        benchmark_weights: pd.DataFrame | None = None,
        factor_returns: pd.DataFrame | None = None,
        weights_are_targets: bool = False,
        circuit_breaker: Any = None,
    ) -> dict[str, Any]:
        """Run a backtest using pre-computed portfolio weights.

        Unlike :meth:`run`, this does not generate signals from a strategy;
        it uses the supplied ``weights`` DataFrame directly (aligned to
        ``data``). This makes it straightforward to combine with the portfolio
        optimization utilities in :mod:`utils.optimization`.

        Args:
            weights: Target portfolio weights indexed like ``data``, with one
                column per asset. Non-finite or missing entries are treated as
                zero.
            data: Price data DataFrame (assets as columns).
            fee_rate: Legacy linear fee rate (ignored when ``cost_model`` is
                set).
            slippage: Legacy slippage rate (ignored when ``cost_model`` is
                set).
            risk_manager: Optional risk manager to apply to the weights.
            cost_model: Optional transaction cost model.
            volume: Optional per-asset bar volume (indexed like ``data``)
                used by the execution simulator for volume participation
                constraints. Ignored when no ``execution_simulator`` is set.

        Returns:
            A backtest result dictionary (same shape as :meth:`run`).
        """
        if rebalance_frequency is not None:
            weights = create_rebalanced_weights(
                weights, data, freq=rebalance_frequency, offset=rebalance_offset
            )
        return self._evaluate_weights(
            weights,
            data,
            fee_rate=fee_rate,
            slippage=slippage,
            risk_manager=risk_manager,
            cost_model=cost_model,
            execution_simulator=execution_simulator,
            volume=volume,
            high=high,
            low=low,
            regime_signal=regime_signal,
            regime_mode=regime_mode,
            regime_lookback=regime_lookback,
            regime_vol_mode=regime_vol_mode,
            benchmark_weights=benchmark_weights,
            factor_returns=factor_returns,
            weights_are_targets=weights_are_targets,
            circuit_breaker=circuit_breaker,
        )

    def walk_forward(
        self,
        strategy: Strategy,
        data: pd.DataFrame,
        train_period: int = 252,
        test_period: int = 63,
        fee_rate: float = 0.0,
        slippage: float = 0.0,
        cost_model: Any = None,
        risk_manager: Any = None,
        execution_simulator: Any = None,
        volume: pd.DataFrame | None = None,
        high: pd.DataFrame | None = None,
        low: pd.DataFrame | None = None,
        regime_signal: Any = None,
        regime_mode: str | None = None,
        regime_lookback: int | None = None,
        regime_vol_mode: str | None = None,
        benchmark_weights: pd.DataFrame | None = None,
        factor_returns: pd.DataFrame | None = None,
        mode: str = "rolling",
        anchor: Any = None,
        n_splits: int | None = None,
    ) -> dict[str, Any]:
        """Perform walk-forward validation.

        ``mode`` selects the window scheme: ``"rolling"`` (fixed-size train
        window sliding forward, default) or ``"expanding"`` (train window grows
        from ``train_period`` as the origin slides forward).

        ``anchor`` optionally sets the origin index for the first window: an
        integer row offset, a timestamp string/pandas Timestamp, or None for
        the start of the data. ``n_splits`` optionally caps the number of
        forward-test windows evaluated.
        """
        if train_period < 1 or test_period < 1:
            raise ValueError("train_period and test_period must be positive.")
        if mode not in ("rolling", "expanding"):
            raise ValueError(
                f"Invalid mode: {mode!r}; allowed: ('rolling', 'expanding')"
            )
        if n_splits is not None:
            try:
                n_splits = int(n_splits)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"n_splits must be an integer > 0: {exc}") from exc
            if n_splits <= 0:
                raise ValueError(f"n_splits must be > 0, got {n_splits}")

        results = []
        total = len(data)
        i = _resolve_anchor_index(anchor, data)
        while i + train_period + test_period <= total:
            if mode == "expanding":
                train_start = 0
                train_end = i + train_period
                train_data = data.iloc[train_start:train_end]
            else:
                train_data = data.iloc[i : i + train_period]
            test_data = data.iloc[i + train_period : i + train_period + test_period]
            # Train the strategy if it has a fit method
            if hasattr(strategy, "fit"):
                try:
                    strategy.fit(train_data)
                except Exception:
                    pass
            # Generate signals with both the training history and test bars
            # available. The strategy must still use causal rolling features.
            if mode == "expanding":
                full_window = data.iloc[0 : i + train_period + test_period]
            else:
                full_window = data.iloc[i : i + train_period + test_period]
            signals = strategy.generate_signals(full_window)
            target_weights = self._signals_to_weights(signals, full_window)
            executed_weights = target_weights.shift(1).fillna(0.0)
            weights_test = executed_weights.reindex(test_data.index).fillna(0.0)
            test_volume = volume.loc[test_data.index] if (volume is not None) else None
            test_high = high.loc[test_data.index] if (high is not None) else None
            test_low = low.loc[test_data.index] if (low is not None) else None
            result = self.run_portfolio(
                weights_test,
                test_data,
                fee_rate=fee_rate,
                slippage=slippage,
                cost_model=cost_model,
                risk_manager=risk_manager,
                execution_simulator=execution_simulator,
                volume=test_volume,
                high=test_high,
                low=test_low,
                regime_signal=regime_signal,
                regime_mode=regime_mode,
                regime_lookback=regime_lookback,
                regime_vol_mode=regime_vol_mode,
                benchmark_weights=benchmark_weights,
                factor_returns=factor_returns,
                weights_are_targets=False,
            )
            # In-sample (train-window) performance for IS/OOS comparison.
            is_metrics = self._evaluate_in_sample(
                strategy=strategy,
                weights=None,
                train_data=train_data,
                volume=volume,
                high=high,
                low=low,
                reoptimize=False,
                optimizer=None,
                fee_rate=fee_rate,
                slippage=slippage,
                cost_model=cost_model,
                risk_manager=risk_manager,
                execution_simulator=execution_simulator,
                regime_signal=regime_signal,
                regime_mode=regime_mode,
                regime_lookback=regime_lookback,
                regime_vol_mode=regime_vol_mode,
                benchmark_weights=benchmark_weights,
                factor_returns=factor_returns,
            )
            result["is_total_return"] = is_metrics["is_total_return"]
            result["is_sharpe_ratio"] = is_metrics["is_sharpe_ratio"]
            result["is_max_drawdown"] = is_metrics["is_max_drawdown"]
            result["oos_total_return"] = result["total_return"]
            results.append(result)
            i += test_period
            if n_splits is not None and len(results) >= n_splits:
                break

        if not results:
            # If not enough data for walk-forward, run on all data
            result = self.run(
                strategy,
                data,
                fee_rate=fee_rate,
                slippage=slippage,
                cost_model=cost_model,
                risk_manager=risk_manager,
                execution_simulator=execution_simulator,
                volume=volume,
                high=high,
                low=low,
                regime_signal=regime_signal,
                regime_mode=regime_mode,
                regime_lookback=regime_lookback,
                regime_vol_mode=regime_vol_mode,
                benchmark_weights=benchmark_weights,
                factor_returns=factor_returns,
            )
            return {
                "returns": [result["total_return"]],
                "results": [result],
            }

        returns_list = [r["total_return"] for r in results]
        agg: dict[str, Any] = {
            "returns": returns_list,
            "results": results,
        }
        try:
            import numpy as _np

            arr = _np.array(returns_list, dtype=float)
            if arr.size > 0:
                agg["mean_return"] = float(_np.mean(arr))
                agg["std_return"] = float(_np.std(arr, ddof=1)) if arr.size > 1 else 0.0
                agg["positive_periods"] = int(_np.sum(arr > 0))
                agg["total_periods"] = int(arr.size)
        except Exception:
            pass
        # Aggregate in-sample vs out-of-sample performance across windows.
        is_returns = [
            float((r or {}).get("is_total_return", 0.0)) for r in results
        ]
        if is_returns:
            try:
                is_arr = _np.array(is_returns, dtype=float)
                oos_arr = _np.array(returns_list, dtype=float)
                agg["is_mean_return"] = float(_np.mean(is_arr))
                agg["oos_mean_return"] = float(_np.mean(oos_arr))
                if _np.mean(is_arr) != 0:
                    agg["oos_is_ratio"] = float(_np.mean(oos_arr) / _np.mean(is_arr))
                else:
                    agg["oos_is_ratio"] = 0.0
            except Exception:
                pass
        return agg

    def walk_forward_portfolio(
        self,
        weights: pd.DataFrame,
        data: pd.DataFrame,
        train_period: int = 252,
        test_period: int = 63,
        fee_rate: float = 0.0,
        slippage: float = 0.0,
        cost_model: Any = None,
        risk_manager: Any = None,
        execution_simulator: Any = None,
        volume: pd.DataFrame | None = None,
        high: pd.DataFrame | None = None,
        low: pd.DataFrame | None = None,
        reoptimize: bool = False,
        optimizer: Any = None,
        regime_signal: Any = None,
        regime_mode: str | None = None,
        regime_lookback: int | None = None,
        regime_vol_mode: str | None = None,
        benchmark_weights: pd.DataFrame | None = None,
        factor_returns: pd.DataFrame | None = None,
        mode: str = "rolling",
        anchor: Any = None,
        n_splits: int | None = None,
    ) -> dict[str, Any]:
        """Perform walk-forward validation using portfolio weights.

        If ``reoptimize`` is True and an ``optimizer`` is provided, weights
        are recomputed on each train window (optimizer should accept
        ``train_data`` and return a weights DataFrame/Series aligned to
        assets).

        ``anchor`` optionally sets the origin index for the first window: an
        integer row offset, a timestamp string/pandas Timestamp, or None for
        the start of the data. ``n_splits`` optionally caps the number of
        forward-test windows evaluated.
        """
        if train_period < 1 or test_period < 1:
            raise ValueError("train_period and test_period must be positive.")
        if reoptimize and optimizer is None:
            raise ValueError("optimizer is required when reoptimize=True.")
        if mode not in ("rolling", "expanding"):
            raise ValueError(
                f"Invalid mode: {mode!r}; allowed: ('rolling', 'expanding')"
            )
        if n_splits is not None:
            try:
                n_splits = int(n_splits)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"n_splits must be an integer > 0: {exc}") from exc
            if n_splits <= 0:
                raise ValueError(f"n_splits must be > 0, got {n_splits}")

        results = []
        total = len(data)
        i = _resolve_anchor_index(anchor, data)
        w = weights.copy() if hasattr(weights, "copy") else weights
        # Align
        if isinstance(w, pd.Series):
            w = w.to_frame().T
        w = w.reindex(index=data.index, method="ffill").fillna(0.0)
        # ensure columns align
        if isinstance(data, pd.DataFrame) and hasattr(w, "columns"):
            w = w.reindex(columns=data.columns, fill_value=0.0)

        while i + train_period + test_period <= total:
            if mode == "expanding":
                train_data = data.iloc[0 : i + train_period]
            else:
                train_data = data.iloc[i : i + train_period]
            test_data = data.iloc[i + train_period : i + train_period + test_period]
            test_index = test_data.index
            w_test = w.reindex(index=test_index)
            if reoptimize and optimizer is not None:
                # Reoptimization failures must be explicit: silently reverting
                # to stale weights would make the reported run misleading.
                w_opt = optimizer(train_data)
                w_test = self._align_optimizer_result(w_opt, test_data, test_index)
            test_volume = volume.loc[test_data.index] if (volume is not None) else None
            test_high = high.loc[test_data.index] if (high is not None) else None
            test_low = low.loc[test_data.index] if (low is not None) else None
            result = self.run_portfolio(
                w_test,
                test_data,
                fee_rate=fee_rate,
                slippage=slippage,
                cost_model=cost_model,
                risk_manager=risk_manager,
                execution_simulator=execution_simulator,
                volume=test_volume,
                high=test_high,
                low=test_low,
                regime_signal=regime_signal,
                regime_mode=regime_mode,
                regime_lookback=regime_lookback,
                regime_vol_mode=regime_vol_mode,
                benchmark_weights=benchmark_weights,
                factor_returns=factor_returns,
                weights_are_targets=not (reoptimize and optimizer is not None),
            )
            # In-sample (train-window) performance for IS/OOS comparison.
            is_metrics = self._evaluate_in_sample(
                strategy=None,
                weights=w,
                train_data=train_data,
                volume=volume,
                high=high,
                low=low,
                reoptimize=reoptimize,
                optimizer=optimizer,
                fee_rate=fee_rate,
                slippage=slippage,
                cost_model=cost_model,
                risk_manager=risk_manager,
                execution_simulator=execution_simulator,
                regime_signal=regime_signal,
                regime_mode=regime_mode,
                regime_lookback=regime_lookback,
                regime_vol_mode=regime_vol_mode,
                benchmark_weights=benchmark_weights,
                factor_returns=factor_returns,
            )
            result["is_total_return"] = is_metrics["is_total_return"]
            result["is_sharpe_ratio"] = is_metrics["is_sharpe_ratio"]
            result["is_max_drawdown"] = is_metrics["is_max_drawdown"]
            result["oos_total_return"] = result["total_return"]
            results.append(result)
            i += test_period
            if n_splits is not None and len(results) >= n_splits:
                break

        if not results:
            result = self.run_portfolio(
                w,
                data,
                fee_rate=fee_rate,
                slippage=slippage,
                cost_model=cost_model,
                risk_manager=risk_manager,
                execution_simulator=execution_simulator,
                volume=volume,
                high=high,
                low=low,
                regime_signal=regime_signal,
                regime_mode=regime_mode,
                regime_lookback=regime_lookback,
                regime_vol_mode=regime_vol_mode,
                benchmark_weights=benchmark_weights,
                factor_returns=factor_returns,
            )
            return {"returns": [result["total_return"]], "results": [result]}

        returns_list = [r["total_return"] for r in results]
        agg: dict[str, Any] = {"returns": returns_list, "results": results}
        try:
            import numpy as _np

            arr = _np.array(returns_list, dtype=float)
            if arr.size > 0:
                agg["mean_return"] = float(_np.mean(arr))
                agg["std_return"] = float(_np.std(arr, ddof=1)) if arr.size > 1 else 0.0
                agg["positive_periods"] = int(_np.sum(arr > 0))
                agg["total_periods"] = int(arr.size)
        except Exception:
            pass
        # Aggregate in-sample vs out-of-sample performance across windows.
        is_returns = [
            float((r or {}).get("is_total_return", 0.0)) for r in results
        ]
        if is_returns:
            try:
                is_arr = _np.array(is_returns, dtype=float)
                oos_arr = _np.array(returns_list, dtype=float)
                agg["is_mean_return"] = float(_np.mean(is_arr))
                agg["oos_mean_return"] = float(_np.mean(oos_arr))
                if _np.mean(is_arr) != 0:
                    agg["oos_is_ratio"] = float(_np.mean(oos_arr) / _np.mean(is_arr))
                else:
                    agg["oos_is_ratio"] = 0.0
            except Exception:
                pass
        return agg
