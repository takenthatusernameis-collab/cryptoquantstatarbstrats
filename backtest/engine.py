"""
Backtesting framework for statistical arbitrage strategies
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from strategies.base import Strategy
from utils.metrics import cvar, sharpe_ratio, sortino_ratio, var


class BacktestEngine:
    """Backtesting engine for trading strategies."""

    def __init__(self, initial_capital: float = 100000.0):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions: dict[str, float] = {}
        self.trades: list[dict[str, Any]] = []
        self.equity_curve: list[float] = []

    def _evaluate_weights(
        self,
        weights: pd.DataFrame,
        data: pd.DataFrame,
        fee_rate: float = 0.0,
        slippage: float = 0.0,
        risk_manager: Any = None,
        cost_model: Any = None,
        execution_simulator: Any = None,
    ) -> dict[str, Any]:
        """Core backtest computation given a (pre-computed) weights DataFrame.

        Aligns ``weights`` to ``data``, optionally applies risk management,
        subtracts transaction costs from turnover, and returns the standard
        result dictionary. This is shared by :meth:`run` and
        :meth:`run_portfolio`.
        """
        returns = data.pct_change().fillna(0.0)

        # Align weights to data: reindex to data index/columns, fill NaN with 0.
        weights = (
            weights.reindex(index=data.index, columns=data.columns, fill_value=0.0)
            .fillna(0.0)
        )

        # Apply risk management if provided
        if risk_manager is not None:
            try:
                weights = risk_manager.max_position_size(weights, self.capital)
            except Exception:
                pass

        if execution_simulator is not None:
            portfolio_returns, cost = self._simulate_execution(
                weights, data, returns, execution_simulator
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

        total_return = float(cumulative_returns.iloc[-1] - 1.0)
        sharpe = sharpe_ratio(portfolio_returns)
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
            calmar_ratio = total_return / abs(max_drawdown)
        else:
            calmar_ratio = 0.0

        # Compute advanced risk metrics
        sortino = sortino_ratio(portfolio_returns)
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
        }
        return result

    def _simulate_execution(
        self,
        weights: pd.DataFrame,
        data: pd.DataFrame,
        returns: pd.DataFrame,
        execution_simulator: Any,
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
                fill = execution_simulator.simulate_order("market", side, qty, price)
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

    def run(
        self,
        strategy: Strategy,
        data: pd.DataFrame,
        fee_rate: float = 0.0,
        slippage: float = 0.0,
        risk_manager: Any = None,
        cost_model: Any = None,
        execution_simulator: Any = None,
    ) -> dict[str, Any]:
        """Run backtest for a given strategy.

        Transaction costs are computed from per-period turnover. When
        ``cost_model`` is provided it takes precedence over ``fee_rate`` and
        ``slippage``; otherwise the legacy linear model is used.
        """
        signals = strategy.generate_signals(data)

        # Determine per-asset weights from signals.
        weights = pd.DataFrame(0.0, index=data.index, columns=data.columns)

        # Explicit per-asset weight columns (e.g. cross-exchange legs).
        weight_cols = [c for c in data.columns if c in signals.columns]
        if weight_cols:
            for asset in weight_cols:
                weights[asset] = signals[asset].reindex(data.index).fillna(0.0)

        if "long" in signals.columns and "short" in signals.columns:
            long_mask = signals["long"].fillna(False).reindex(
                data.index, fill_value=False
            )
            short_mask = signals["short"].fillna(False).reindex(
                data.index, fill_value=False
            )
            for asset in data.columns:
                weights.loc[long_mask, asset] = 1.0
                weights.loc[short_mask, asset] = -1.0

        if "exit" in signals.columns:
            exit_mask = signals["exit"].fillna(False).reindex(
                data.index, fill_value=False
            )
            weights.loc[exit_mask, :] = 0.0

        # Equal-weight across active positions to stay fully invested.
        active = weights.abs().sum(axis=1).replace(0.0, np.nan)
        weights = weights.div(active, axis=0).fillna(0.0)

        return self._evaluate_weights(
            weights,
            data,
            fee_rate=fee_rate,
            slippage=slippage,
            risk_manager=risk_manager,
            cost_model=cost_model,
            execution_simulator=execution_simulator,
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
    ) -> dict[str, Any]:
        """Run backtest and include an equal-weighted buy-and-hold benchmark."""
        result = self.run(
            strategy,
            data,
            fee_rate=fee_rate,
            slippage=slippage,
            risk_manager=risk_manager,
            cost_model=cost_model,
        )
        returns = data.pct_change().fillna(0.0)
        n = data.shape[1]
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

        Returns:
            A backtest result dictionary (same shape as :meth:`run`).
        """
        return self._evaluate_weights(
            weights,
            data,
            fee_rate=fee_rate,
            slippage=slippage,
            risk_manager=risk_manager,
            cost_model=cost_model,
            execution_simulator=execution_simulator,
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
    ) -> dict[str, Any]:
        """Perform walk-forward validation."""
        results = []
        total = len(data)
        i = 0
        while i + train_period + test_period <= total:
            train_data = data.iloc[i : i + train_period]
            test_data = data.iloc[i + train_period : i + train_period + test_period]
            # Train the strategy if it has a fit method
            if hasattr(strategy, "fit"):
                try:
                    strategy.fit(train_data)
                except Exception:
                    pass
            # Run on test data
            result = self.run(
                strategy,
                test_data,
                fee_rate=fee_rate,
                slippage=slippage,
                cost_model=cost_model,
                risk_manager=risk_manager,
                execution_simulator=execution_simulator,
            )
            results.append(result)
            i += test_period

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
        reoptimize: bool = False,
        optimizer: Any = None,
    ) -> dict[str, Any]:
        """Perform walk-forward validation using portfolio weights.

        If ``reoptimize`` is True and an ``optimizer`` is provided, weights
        are recomputed on each train window (optimizer should accept
        ``train_data`` and return a weights DataFrame/Series aligned to
        assets).
        """
        results = []
        total = len(data)
        i = 0
        w = weights.copy() if hasattr(weights, "copy") else weights
        # Align
        if isinstance(w, pd.Series):
            w = w.to_frame().T
        w = w.reindex(index=data.index, method="ffill").fillna(0.0)
        # ensure columns align
        if isinstance(data, pd.DataFrame) and hasattr(w, "columns"):
            w = w.reindex(columns=data.columns, fill_value=0.0)

        while i + train_period + test_period <= total:
            train_data = data.iloc[i : i + train_period]
            test_data = data.iloc[i + train_period : i + train_period + test_period]
            test_index = test_data.index
            w_test = w.reindex(index=test_index)
            if reoptimize and optimizer is not None:
                try:
                    w_opt = optimizer(train_data)
                    if isinstance(w_opt, pd.Series):
                        w_opt_df = w_opt.to_frame().T.reindex(index=test_index)
                    elif isinstance(w_opt, pd.DataFrame):
                        w_opt_df = w_opt.reindex(index=test_index, method="ffill").fillna(0.0)
                    else:
                        w_opt_df = w_test
                    # align columns
                    if isinstance(test_data, pd.DataFrame):
                        w_opt_df = w_opt_df.reindex(columns=test_data.columns, fill_value=0.0)
                    w_test = w_opt_df
                except Exception:
                    pass
            result = self.run_portfolio(
                w_test,
                test_data,
                fee_rate=fee_rate,
                slippage=slippage,
                cost_model=cost_model,
                risk_manager=risk_manager,
                execution_simulator=execution_simulator,
            )
            results.append(result)
            i += test_period

        if not results:
            result = self.run_portfolio(
                w,
                data,
                fee_rate=fee_rate,
                slippage=slippage,
                cost_model=cost_model,
                risk_manager=risk_manager,
                execution_simulator=execution_simulator,
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
        return agg
