"""
Reporting and visualization utilities for backtest results.
"""

from __future__ import annotations

import pandas as pd


def generate_report(result: dict) -> str:
    """Build a human-readable text summary of a backtest result."""
    result = result or {}
    total_return = result.get("total_return", 0.0)
    sharpe_ratio = result.get("sharpe_ratio", 0.0)
    sortino_ratio = result.get("sortino_ratio", 0.0)
    var_95 = result.get("var", result.get("VaR", 0.0))
    cvar_95 = result.get("cvar", result.get("CVaR", 0.0))
    max_drawdown = result.get("max_drawdown", result.get("maxDD", 0.0))
    max_dd_duration = result.get("max_drawdown_duration", result.get("max_drawdown_duration", 0))
    calmar_ratio = result.get("calmar_ratio", 0.0)

    lines: list[str] = [
        "Backtest Report",
        "===============",
        f"Total Return:        {total_return:.4%}",
        f"Sharpe Ratio:        {sharpe_ratio:.4f}",
        f"Sortino Ratio:       {sortino_ratio:.4f}",
        f"VaR (95%):           {var_95:.4%}",
        f"CVaR (95%):          {cvar_95:.4%}",
        f"Max Drawdown:        {max_drawdown:.4%}",
        f"Max DD Duration:     {int(max_dd_duration)} periods",
        f"Calmar Ratio:        {calmar_ratio:.4f}",
    ]
    return "\n".join(lines)


def report_to_dict(result: dict) -> dict:
    """Return a serializable dict of key metrics (float/int/str only)."""
    result = result or {}
    return {
        "total_return": float(result.get("total_return", 0.0)),
        "sharpe_ratio": float(result.get("sharpe_ratio", 0.0)),
        "sortino_ratio": float(result.get("sortino_ratio", 0.0)),
        "var": float(result.get("var", result.get("VaR", 0.0))),
        "cvar": float(result.get("cvar", result.get("CVaR", 0.0))),
        "max_drawdown": float(result.get("max_drawdown", result.get("maxDD", 0.0))),
        "max_drawdown_duration": int(result.get("max_drawdown_duration", 0)),
        "calmar_ratio": float(result.get("calmar_ratio", 0.0)),
    }


def plot_equity_curve(result: dict, save_path: str | None = None) -> None:
    """Plot equity curve and drawdown from a backtest result."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return

    equity_curve = result.get("equity_curve")
    if equity_curve is None:
        return

    equity = equity_curve if isinstance(equity_curve, pd.Series) else pd.Series(equity_curve)
    if len(equity) == 0:
        return

    running_max = equity.cummax()
    drawdown = equity / running_max - 1.0

    fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    axes[0].plot(equity.index, equity.values, label="Equity")
    axes[0].set_ylabel("Equity")
    axes[0].legend()
    axes[1].fill_between(
        drawdown.index, drawdown.values, color="red", alpha=0.3, label="Drawdown"
    )
    axes[1].set_ylabel("Drawdown")
    axes[1].set_xlabel("Time")
    axes[1].legend()
    fig.tight_layout()

    if save_path:
        fig.savefig(save_path)
        plt.close(fig)
    else:
        plt.show()


def generate_risk_report(result: dict) -> str:
    """Build a human-readable risk summary of a backtest result."""
    result = result or {}
    var = result.get("var", result.get("VaR", 0.0))
    cvar = result.get("cvar", result.get("CVaR", 0.0))
    max_drawdown = result.get("max_drawdown", result.get("maxDD", 0.0))
    max_dd_duration = result.get("max_drawdown_duration", 0)
    calmar_ratio = result.get("calmar_ratio", 0.0)

    lines: list[str] = [
        "Risk Report",
        "===========",
        f"VaR (95%):              {var:.4%}",
        f"CVaR (95%):             {cvar:.4%}",
        f"Max Drawdown:           {max_drawdown:.4%}",
        f"Max DD Duration:        {int(max_dd_duration)} periods",
        f"Calmar Ratio:           {calmar_ratio:.4f}",
    ]
    return "\n".join(lines)


def risk_report_to_dict(result: dict) -> dict:
    """Return a serializable dict of risk metrics (float/int/str only)."""
    result = result or {}
    return {
        "var": float(result.get("var", result.get("VaR", 0.0))),
        "cvar": float(result.get("cvar", result.get("CVaR", 0.0))),
        "max_drawdown": float(result.get("max_drawdown", result.get("maxDD", 0.0))),
        "max_drawdown_duration": int(result.get("max_drawdown_duration", 0)),
        "calmar_ratio": float(result.get("calmar_ratio", 0.0)),
    }
