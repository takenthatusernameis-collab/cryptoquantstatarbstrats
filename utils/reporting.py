from __future__ import annotations

from pathlib import Path

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


def generate_html_report(result: dict, title: str = "Backtest Report") -> str:
    """Generate a simple HTML report from a backtest result."""
    result = result or {}
    metrics = report_to_dict(result) if result else {}
    risk = risk_report_to_dict(result) if result else {}

    def fmt_pct(x: float) -> str:
        try:
            return f"{float(x):.4%}"
        except Exception:
            return str(x)

    def fmt_num(x: float) -> str:
        try:
            return f"{float(x):.4f}"
        except Exception:
            return str(x)

    html = []
    html.append("<!DOCTYPE html>")
    html.append("<html><head><meta charset='utf-8'>")
    html.append(f"<title>{title}</title>")
    html.append(
        "<style>"
        "body{font-family:Arial,sans-serif;margin:40px;}"
        "h1{color:#333;}"
        "table{border-collapse:collapse;width:100%;}"
        "th,td{border:1px solid #ddd;padding:8px;text-align:left;}"
        "th{background-color:#f2f2f2;}"
        "</style>"
    )
    html.append("</head><body>")
    html.append(f"<h1>{title}</h1>")
    html.append("<h2>Performance Metrics</h2>")
    html.append("<table>")
    html.append(
        "<tr><th>Metric</th><th>Value</th></tr>"
        f"<tr><td>Total Return</td><td>{fmt_pct(metrics.get('total_return', 0.0))}</td></tr>"
        f"<tr><td>Sharpe Ratio</td><td>{fmt_num(metrics.get('sharpe_ratio', 0.0))}</td></tr>"
        f"<tr><td>Sortino Ratio</td><td>{fmt_num(metrics.get('sortino_ratio', 0.0))}</td></tr>"
        f"<tr><td>Calmar Ratio</td><td>{fmt_num(metrics.get('calmar_ratio', 0.0))}</td></tr>"
        "</table>"
    )
    html.append("<h2>Risk Metrics</h2>")
    html.append("<table>")
    html.append("<tr><th>Metric</th><th>Value</th></tr>")
    html.append(f"<tr><td>VaR (95%)</td><td>{fmt_pct(risk.get('var', 0.0))}</td></tr>")
    html.append(f"<tr><td>CVaR (95%)</td><td>{fmt_pct(risk.get('cvar', 0.0))}</td></tr>")
    html.append(
        f"<tr><td>Max Drawdown</td><td>{fmt_pct(risk.get('max_drawdown', 0.0))}</td></tr>"
    )
    html.append(
        "<tr><td>Max DD Duration</td>"
        f"<td>{int(risk.get('max_drawdown_duration', 0))} periods</td></tr>"
    )
    html.append("</table>")
    html.append("</body></html>")
    return "\n".join(html)


def generate_pdf_report(result: dict, output_path: str, title: str = "Backtest Report") -> str:
    """Generate a PDF report from a backtest result.

    Attempts to use matplotlib/pdf backends if available; falls back to
    writing HTML if PDF generation is not possible.
    """
    html = generate_html_report(result, title=title)
    try:
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_pdf import PdfPages
    except Exception:
        # Fallback: write HTML alongside if requested as .html, else write HTML content
        try:
            html_path = output_path
            if html_path.lower().endswith(".pdf"):
                html_path = output_path.rsplit(".", 1)[0] + ".html"
            Path(html_path).write_text(html)
            return html_path
        except Exception:
            return html

    try:
        metrics = report_to_dict(result) if result else {}
        risk = risk_report_to_dict(result) if result else {}

        def fmt_pct(x: float) -> str:
            try:
                return f"{float(x):.4%}"
            except Exception:
                return str(x)

        def fmt_num(x: float) -> str:
            try:
                return f"{float(x):.4f}"
            except Exception:
                return str(x)

        with PdfPages(output_path) as pdf:
            fig = plt.figure(figsize=(11, 8.5))
            plt.axis("off")
            text = []
            text.append(title)
            text.append("=" * len(title))
            text.append("")
            text.append("Performance Metrics:")
            text.append(f"  Total Return:        {fmt_pct(metrics.get('total_return', 0.0))}")
            text.append(f"  Sharpe Ratio:        {fmt_num(metrics.get('sharpe_ratio', 0.0))}")
            text.append(f"  Sortino Ratio:       {fmt_num(metrics.get('sortino_ratio', 0.0))}")
            text.append(f"  Calmar Ratio:        {fmt_num(metrics.get('calmar_ratio', 0.0))}")
            text.append("")
            text.append("Risk Metrics:")
            text.append(f"  VaR (95%):           {fmt_pct(risk.get('var', 0.0))}")
            text.append(f"  CVaR (95%):          {fmt_pct(risk.get('cvar', 0.0))}")
            text.append(
                f"  Max Drawdown:        {fmt_pct(risk.get('max_drawdown', 0.0))}"
            )
            text.append(
                f"  Max DD Duration:     {int(risk.get('max_drawdown_duration', 0))} periods"
            )
            plt.text(
                0.1,
                0.9,
                "\n".join(text),
                va="top",
                family="monospace",
                fontsize=10,
            )
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)

            equity_curve = (result or {}).get("equity_curve")
            if equity_curve is not None:
                try:
                    import pandas as _pd

                    equity = (
                        equity_curve
                        if isinstance(equity_curve, _pd.Series)
                        else _pd.Series(equity_curve)
                    )
                    if len(equity) > 0:
                        fig, axes = plt.subplots(2, 1, figsize=(11, 8.5), sharex=True)
                    axes[0].plot(equity.index, equity.values, label="Equity")
                    axes[0].set_ylabel("Equity")
                    axes[0].legend()
                    running_max = equity.cummax()
                    drawdown = equity / running_max - 1.0
                    axes[1].fill_between(
                        drawdown.index,
                        drawdown.values,
                        color="red",
                        alpha=0.3,
                        label="Drawdown",
                    )
                    axes[1].set_ylabel("Drawdown")
                    axes[1].set_xlabel("Time")
                    axes[1].legend()
                    fig.tight_layout()
                    pdf.savefig(fig, bbox_inches="tight")
                    plt.close(fig)
                except Exception:
                    pass
        return output_path
    except Exception:
        try:
            html_path = output_path
            if html_path.lower().endswith(".pdf"):
                html_path = output_path.rsplit(".", 1)[0] + ".html"
            Path(html_path).write_text(html)
            return html_path
        except Exception:
            return html
