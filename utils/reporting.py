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
    equity_curve = (result or {}).get("equity_curve")
    if equity_curve is not None:
        try:
            equity = (
                equity_curve
                if isinstance(equity_curve, pd.Series)
                else pd.Series(equity_curve)
            )
            if len(equity) > 0:
                running_max = equity.cummax()
                drawdown = equity / running_max - 1.0

                def _normalize(values, height=120.0):
                    vmin = float(values.min())
                    vmax = float(values.max())
                    span = vmax - vmin if vmax != vmin else 1.0
                    return [height - (float(v) - vmin) / span * height for v in values]

                width = 600.0
                n = len(equity)
                xs = [i * width / max(n - 1, 1) for i in range(n)]
                ey = _normalize(equity.values)
                dy = _normalize(drawdown.values)

                equity_points = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ey))
                dd_points = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, dy))

                html.append("<h2>Equity Curve &amp; Drawdown</h2>")
                html.append(
                    f'<svg width="{int(width)}" height="260" '
                    'style="border:1px solid #ddd;background:#fafafa;">'
                )
                html.append(
                    f'<polyline points="{equity_points}" fill="none" '
                    'stroke="#1f77b4" stroke-width="2" />'
                )
                html.append(
                    f'<polyline points="{dd_points}" fill="none" '
                    'stroke="#d62728" stroke-width="1.5" />'
                )
                html.append("</svg>")
        except Exception:
            pass

    # Trade list (if available)
    trades = None
    if result:
        if "trades" in result and result.get("trades") is not None:
            trades = result.get("trades")
        elif "trade_list" in result and result.get("trade_list") is not None:
            trades = result.get("trade_list")
    if trades is not None:
        try:
            import pandas as _pd

            if isinstance(trades, _pd.DataFrame) and len(trades) > 0:
                html.append("<h2>Trade List</h2>")
                html.append("<table>")
                html.append(
                    "<tr>"
                    + "".join(f"<th>{col}</th>" for col in trades.columns)
                    + "</tr>"
                )
                for _, row in trades.head(200).iterrows():
                    html.append(
                        "<tr>"
                        + "".join(f"<td>{row[c]}</td>" for c in trades.columns)
                        + "</tr>"
                    )
                html.append("</table>")
                if len(trades) > 200:
                    html.append(f"<p><em>Showing first 200 of {len(trades)} trades.</em></p>")
        except Exception:
            pass

    # Weights (if available)
    weights = (result or {}).get("weights")
    if weights is not None:
        try:
            import pandas as _pd

            if isinstance(weights, _pd.DataFrame):
                if len(weights) == 0:
                    pass
                else:
                    html.append("<h2>Portfolio Weights</h2>")
                    html.append("<table>")
                    html.append(
                        "<tr>"
                        + "".join(f"<th>{col}</th>" for col in weights.columns)
                        + "</tr>"
                    )
                    # Show last row
                    last = weights.tail(1).iloc[0]
                    html.append(
                        "<tr>"
                        + "".join(f"<td>{last[c]}</td>" for c in weights.columns)
                        + "</tr>"
                    )
                    html.append("</table>")
        except Exception:
            pass

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
            # Page 1: Metrics
            fig = plt.figure(figsize=(11, 8.5))
            plt.rcParams.update({"font.size": 9})
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
                0.08,
                0.92,
                "\n".join(text),
                va="top",
                family="monospace",
                fontsize=9,
            )
            pdf.savefig(fig, bbox_inches="tight", pad_inches=0.5)
            plt.close(fig)

            # Page 2: Equity curve and drawdown
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
                        axes[0].plot(equity.index, equity.values, label="Equity", linewidth=1.2)
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
                        fig.suptitle("Equity Curve & Drawdown")
                        fig.tight_layout(pad=2.0)
                        pdf.savefig(fig, bbox_inches="tight", pad_inches=0.5)
                        plt.close(fig)
                except Exception:
                    pass

            # Page 3: Weights (if available)
            weights = (result or {}).get("weights")
            if weights is not None:
                try:
                    import pandas as _pd

                    if isinstance(weights, _pd.DataFrame) and len(weights) > 0:
                        fig = plt.figure(figsize=(11, 8.5))
                        plt.rcParams.update({"font.size": 9})
                        plt.axis("off")
                        wtext = ["Portfolio Weights (Last)"]
                        wtext.append("=" * len(wtext[0]))
                        wtext.append("")
                        last = weights.tail(1).iloc[0]
                        for c in weights.columns:
                            try:
                                wtext.append(f"  {c}: {float(last[c]):.4f}")
                            except Exception:
                                wtext.append(f"  {c}: {last[c]}")
                        plt.text(
                            0.08,
                            0.92,
                            "\n".join(wtext),
                            va="top",
                            family="monospace",
                            fontsize=8,
                        )
                        pdf.savefig(fig, bbox_inches="tight", pad_inches=0.5)
                        plt.close(fig)
                except Exception:
                    pass

            # Page 4: Trades (if available)
            trades = None
            if result:
                if result.get("trades") is not None:
                    trades = result.get("trades")
                elif result.get("trade_list") is not None:
                    trades = result.get("trade_list")
            if trades is not None:
                try:
                    import pandas as _pd

                    if isinstance(trades, _pd.DataFrame) and len(trades) > 0:
                        fig = plt.figure(figsize=(11, 8.5))
                        plt.rcParams.update({"font.size": 7})
                        plt.axis("off")
                        ttext = ["Trade List (first 50)"]
                        ttext.append("=" * len(ttext[0]))
                        ttext.append("")
                        for _, row in trades.head(50).iterrows():
                            parts = []
                            for c in trades.columns[:6]:
                                parts.append(f"{c}={row[c]}")
                            ttext.append("  " + ", ".join(str(p) for p in parts))
                        plt.text(
                            0.05,
                            0.95,
                            "\n".join(ttext),
                            va="top",
                            family="monospace",
                            fontsize=6.5,
                        )
                        pdf.savefig(fig, bbox_inches="tight", pad_inches=0.5)
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
