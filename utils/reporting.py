from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import pandas as pd


def _get_attribution(result: dict) -> tuple[Any, Any]:
    result = result or {}
    brinson = result.get("brinson") or result.get("brinson_attribution")
    factor = result.get("factor") or result.get("factor_attribution")
    return brinson, factor


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
    # Attribution section (Brinson / factor) when available.
    brinson, factor = _get_attribution(result)
    if brinson is not None or factor is not None:
        lines.append("")
        lines.append("Attribution")
        lines.append("===========")
        if isinstance(brinson, dict):
            lines.extend(brinson_text_lines(brinson))
        if isinstance(factor, dict):
            lines.extend(factor_text_lines(factor))
    return "\n".join(lines)


def report_to_dict(result: dict) -> dict:
    """Return a serializable dict of key metrics (float/int/str only)."""
    result = result or {}
    data: dict[str, Any] = {
        "total_return": float(result.get("total_return", 0.0)),
        "sharpe_ratio": float(result.get("sharpe_ratio", 0.0)),
        "sortino_ratio": float(result.get("sortino_ratio", 0.0)),
        "var": float(result.get("var", result.get("VaR", 0.0))),
        "cvar": float(result.get("cvar", result.get("CVaR", 0.0))),
        "max_drawdown": float(result.get("max_drawdown", result.get("maxDD", 0.0))),
        "max_drawdown_duration": int(result.get("max_drawdown_duration", 0)),
        "calmar_ratio": float(result.get("calmar_ratio", 0.0)),
    }
    data.update(attribution_to_dict(result))
    return data


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


def _fmt_pct(x: float) -> str:
    try:
        return f"{float(x):.4%}"
    except Exception:
        return str(x)


def _fmt_num(x: float) -> str:
    try:
        return f"{float(x):.4f}"
    except Exception:
        return str(x)


def _series_sum(s: Any) -> float:
    try:
        if s is None:
            return 0.0
        if isinstance(s, pd.Series):
            return float(pd.Series(s).dropna().sum())
        return float(s)
    except Exception:
        return 0.0


def _safe_float(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
        if v != v:  # NaN
            return default
        return v
    except (TypeError, ValueError):
        return default


def brinson_text_lines(brinson: dict[str, Any]) -> list[str]:
    """Text lines summarizing Brinson attribution results."""
    lines: list[str] = []
    if not isinstance(brinson, dict):
        return lines
    alloc_total = _series_sum(brinson.get("allocation_total"))
    selection_total = _series_sum(brinson.get("selection_total"))
    interaction_total = _series_sum(brinson.get("interaction_total"))
    lines.append("Brinson Attribution (allocation / selection / interaction):")
    lines.append(f"  Allocation effect:  {_fmt_pct(alloc_total)}")
    lines.append(f"  Selection effect:   {_fmt_pct(selection_total)}")
    lines.append(f"  Interaction effect: {_fmt_pct(interaction_total)}")
    summary = brinson.get("summary")
    if isinstance(summary, pd.DataFrame) and len(summary) > 0:
        lines.append("")
        lines.append("Per-asset attribution (top by |total|):")
        header = "  " + "  ".join(
            f"{c:>10}" for c in ["asset", "allocation", "selection", "interaction", "total"]
        )
        lines.append(header)
        summ = summary.copy()
        summ["__abs__"] = summ["total"].abs()
        summ = summ.sort_values("__abs__", ascending=False).head(10)
        for _, row in summ.iterrows():
            lines.append(
                "  "
                + "  ".join(
                    [
                        f"{str(row['asset']):>10}",
                        f"{_fmt_pct(_safe_float(row['allocation'])):>10}",
                        f"{_fmt_pct(_safe_float(row['selection'])):>10}",
                        f"{_fmt_pct(_safe_float(row['interaction'])):>10}",
                        f"{_fmt_pct(_safe_float(row['total'])):>10}",
                    ]
                )
            )
    return lines


def factor_text_lines(factor: dict[str, Any]) -> list[str]:
    """Text lines summarizing factor attribution results."""
    lines: list[str] = []
    if not isinstance(factor, dict):
        return lines
    lines.append("Factor Attribution (OLS regression):")
    lines.append(f"  Alpha (per period): {_fmt_num(_safe_float(factor.get('alpha')))}")
    lines.append(f"  Alpha (annualized): {_fmt_num(_safe_float(factor.get('alpha_annualized')))}")
    lines.append(f"  R-squared:          {_fmt_num(_safe_float(factor.get('r_squared')))}")
    lines.append(f"  Observations:       {int(_safe_float(factor.get('n_obs')))}")
    beta = factor.get("beta")
    if isinstance(beta, pd.Series) and len(beta) > 0:
        lines.append("  Factor exposures (beta):")
        for name, val in beta.items():
            lines.append(f"    {name}: {_fmt_num(_safe_float(val))}")
    return lines


def attribution_to_dict(result: dict) -> dict:
    """Return a serializable dict of attribution metrics."""
    result = result or {}
    out: dict[str, Any] = {}
    brinson, factor = _get_attribution(result)
    if isinstance(brinson, dict):
        summary = brinson.get("summary")
        summary_records: list[dict[str, Any]] = []
        if isinstance(summary, pd.DataFrame) and len(summary) > 0:
            for _, row in summary.iterrows():
                summary_records.append(
                    {
                        "asset": str(row["asset"]),
                        "allocation": _safe_float(row.get("allocation")),
                        "selection": _safe_float(row.get("selection")),
                        "interaction": _safe_float(row.get("interaction")),
                        "total": _safe_float(row.get("total")),
                    }
                )
        out["brinson"] = {
            "allocation_total": _series_sum(brinson.get("allocation_total")),
            "selection_total": _series_sum(brinson.get("selection_total")),
            "interaction_total": _series_sum(brinson.get("interaction_total")),
            "portfolio_return": _series_sum(brinson.get("portfolio_return")),
            "benchmark_return": _series_sum(brinson.get("benchmark_return")),
            "summary": summary_records,
        }
    if isinstance(factor, dict):
        beta = factor.get("beta")
        beta_dict: dict[str, float] = {}
        if isinstance(beta, pd.Series):
            for name, val in beta.items():
                beta_dict[str(name)] = _safe_float(val)
        out["factor"] = {
            "alpha": _safe_float(factor.get("alpha")),
            "alpha_annualized": _safe_float(factor.get("alpha_annualized")),
            "r_squared": _safe_float(factor.get("r_squared")),
            "n_obs": int(_safe_float(factor.get("n_obs"))),
            "beta": beta_dict,
        }
    return out


def generate_attribution_report(result: dict) -> str:
    """Build a human-readable attribution report from a backtest result."""
    result = result or {}
    lines: list[str] = ["Attribution Report", "=================="]
    brinson, factor = _get_attribution(result)
    if isinstance(brinson, dict):
        lines.append("")
        lines.extend(brinson_text_lines(brinson))
    if isinstance(factor, dict):
        lines.append("")
        lines.extend(factor_text_lines(factor))
    if brinson is None and factor is None:
        lines.append("No attribution results available.")
    return "\n".join(lines)


def attribution_report_to_dict(result: dict) -> dict:
    """Return a serializable dict of attribution metrics."""
    return attribution_to_dict(result or {})



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
                # Equal-weighted buy-and-hold benchmark line (if available).
                bench_equity = (result or {}).get("benchmark_equity_curve")
                if bench_equity is not None:
                    try:
                        import pandas as _pd

                        bench = (
                            bench_equity
                            if isinstance(bench_equity, _pd.Series)
                            else _pd.Series(bench_equity)
                        )
                        if len(bench) == n:
                            bench_norm = bench / float(bench.iloc[0])
                            bey = _normalize(bench_norm.values)
                            bpts = " ".join(
                                f"{x:.1f},{y:.1f}" for x, y in zip(xs, bey)
                            )
                            html.append(
                                f'<polyline points="{bpts}" fill="none" '
                                'stroke="#2ca02c" stroke-width="1.5" '
                                'stroke-dasharray="4,4" />'
                            )
                    except Exception:
                        pass
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

    # Attribution (if available)
    brinson, factor = _get_attribution(result)
    if brinson is not None or factor is not None:
        try:
            html.append("<h2>Attribution</h2>")
            if isinstance(brinson, dict):
                html.append("<h3>Brinson Attribution</h3>")
                html.append("<table><tr><th>Effect</th><th>Total</th></tr>")
                html.append(
                    f"<tr><td>Allocation</td><td>{_fmt_pct(_series_sum(brinson.get('allocation_total')))}</td></tr>"
                )
                html.append(
                    f"<tr><td>Selection</td><td>{_fmt_pct(_series_sum(brinson.get('selection_total')))}</td></tr>"
                )
                html.append(
                    f"<tr><td>Interaction</td><td>{_fmt_pct(_series_sum(brinson.get('interaction_total')))}</td></tr>"
                )
                html.append("</table>")
                summary = brinson.get("summary")
                if isinstance(summary, pd.DataFrame) and len(summary) > 0:
                    html.append("<h4>Per-Asset Attribution</h4>")
                    html.append(
                        "<table><tr><th>Asset</th><th>Allocation</th><th>Selection</th><th>Interaction</th><th>Total</th></tr>"
                    )
                    summ = summary.copy()
                    summ["__abs__"] = summ["total"].abs()
                    summ = summ.sort_values("__abs__", ascending=False).head(10)
                    for _, row in summ.iterrows():
                        html.append(
                            "<tr>"
                            f"<td>{row['asset']}</td>"
                            f"<td>{_fmt_pct(_safe_float(row.get('allocation')))}</td>"
                            f"<td>{_fmt_pct(_safe_float(row.get('selection')))}</td>"
                            f"<td>{_fmt_pct(_safe_float(row.get('interaction')))}</td>"
                            f"<td>{_fmt_pct(_safe_float(row.get('total')))}</td>"
                            "</tr>"
                        )
                    html.append("</table>")
            if isinstance(factor, dict):
                html.append("<h3>Factor Attribution</h3>")
                html.append("<table><tr><th>Metric</th><th>Value</th></tr>")
                html.append(
                    f"<tr><td>Alpha (period)</td>"
                    f"<td>{_fmt_num(_safe_float(factor.get('alpha')))}</td></tr>"
                )
                html.append(
                    f"<tr><td>Alpha (annualized)</td>"
                    f"<td>{_fmt_num(_safe_float(factor.get('alpha_annualized')))}</td></tr>"
                )
                html.append(
                    f"<tr><td>R-squared</td><td>{_fmt_num(_safe_float(factor.get('r_squared')))}</td></tr>"
                )
                html.append(
                    f"<tr><td>Observations</td><td>{int(_safe_float(factor.get('n_obs')))}</td></tr>"
                )
                beta = factor.get("beta")
                if isinstance(beta, pd.Series) and len(beta) > 0:
                    html.append("<tr><td colspan=2>Factor exposures (beta):</td></tr>")
                    for name, val in beta.items():
                        html.append(
                            f"<tr><td>{name}</td><td>{_fmt_num(_safe_float(val))}</td></tr>"
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
            # Page 1: Metrics (tighter spacing, sans-serif font)
            fig = plt.figure(figsize=(11, 8.5))
            plt.rcParams.update({"font.size": 9, "font.family": "sans-serif"})
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
            # Attribution summary (Brinson / factor) when available.
            brinson, factor = _get_attribution(result)
            if brinson is not None or factor is not None:
                text.append("")
                text.append("Attribution:")
                if isinstance(brinson, dict):
                    text.append(
                        "  Brinson allocation:  "
                        f"{fmt_pct(_series_sum(brinson.get('allocation_total')))}"
                    )
                    text.append(
                        "  Brinson selection:   "
                        f"{fmt_pct(_series_sum(brinson.get('selection_total')))}"
                    )
                    text.append(
                        "  Brinson interaction: "
                        f"{fmt_pct(_series_sum(brinson.get('interaction_total')))}"
                    )
                if isinstance(factor, dict):
                    text.append(
                        f"  Factor alpha:        {fmt_num(_safe_float(factor.get('alpha')))}"
                    )
                    text.append(
                        "  Factor alpha (ann):  "
                        f"{fmt_num(_safe_float(factor.get('alpha_annualized')))}"
                    )
                    text.append(
                        f"  Factor R-squared:    {fmt_num(_safe_float(factor.get('r_squared')))}"
                    )
            plt.text(
                0.08,
                0.94,
                "\n".join(text),
                va="top",
                family="sans-serif",
                fontsize=9,
                linespacing=1.15,
            )
            pdf.savefig(fig, bbox_inches="tight", pad_inches=0.4)
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
                        axes[0].set_ylabel("Equity", fontsize=8)
                        axes[0].legend(fontsize=7, loc="best")
                        axes[0].tick_params(labelsize=7)
                        # Equal-weighted buy-and-hold benchmark line (if available).
                        bench_equity = (result or {}).get("benchmark_equity_curve")
                        if bench_equity is not None:
                            try:
                                import pandas as _pd

                                bench = (
                                    bench_equity
                                    if isinstance(bench_equity, _pd.Series)
                                    else _pd.Series(bench_equity)
                                )
                                bench = bench.reindex(equity.index).ffill()
                                if len(bench) > 0 and bench.iloc[0] != 0:
                                    bench_norm = bench / float(bench.iloc[0]) * float(
                                        equity.iloc[0]
                                    )
                                    axes[0].plot(
                                        equity.index,
                                        bench_norm.values,
                                        label="Benchmark",
                                        linewidth=1.0,
                                        linestyle="--",
                                        color="#2ca02c",
                                    )
                                    axes[0].legend(fontsize=7, loc="best")
                            except Exception:
                                pass
                        running_max = equity.cummax()
                        drawdown = equity / running_max - 1.0
                        axes[1].fill_between(
                            drawdown.index,
                            drawdown.values,
                            color="red",
                            alpha=0.3,
                            label="Drawdown",
                        )
                        axes[1].set_ylabel("Drawdown", fontsize=8)
                        axes[1].set_xlabel("Time", fontsize=8)
                        axes[1].legend(fontsize=7, loc="best")
                        axes[1].tick_params(labelsize=7)
                        fig.suptitle("Equity Curve & Drawdown", fontsize=10)
                        fig.tight_layout(pad=1.2)
                        pdf.savefig(fig, bbox_inches="tight", pad_inches=0.4)
                        plt.close(fig)
                except Exception:
                    pass

            # Page 3: Weights (bar chart, tighter layout)
            weights = (result or {}).get("weights")
            if weights is not None:
                try:
                    import pandas as _pd

                    if isinstance(weights, _pd.DataFrame) and len(weights) > 0:
                        fig, ax = plt.subplots(figsize=(11, 8.5))
                        last = weights.tail(1).iloc[0]
                        labels = [str(c) for c in weights.columns]
                        values = [float(last[c]) for c in weights.columns]
                        colors = ["#1f77b4" if v >= 0 else "#d62728" for v in values]
                        ax.bar(labels, values, color=colors)
                        ax.axhline(0, color="black", linewidth=0.8)
                        ax.set_ylabel("Weight", fontsize=9)
                        ax.set_title("Portfolio Weights (Last)", fontsize=10)
                        ax.tick_params(labelsize=8)
                        for i, v in enumerate(values):
                            ax.text(
                                i,
                                v,
                                f"{v:.3f}",
                                ha="center",
                                va="bottom" if v >= 0 else "top",
                                fontsize=7,
                            )
                        fig.tight_layout(pad=1.0)
                        pdf.savefig(fig, bbox_inches="tight", pad_inches=0.4)
                        plt.close(fig)
                except Exception:
                    pass

            # Page 4: Trades (rendered as a table, multi-page if long)
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
                        # Render in chunks of 50 rows per page
                        chunk_size = 50
                        for start in range(0, len(trades), chunk_size):
                            chunk = trades.iloc[start : start + chunk_size]
                            fig, ax = plt.subplots(figsize=(11, 8.5))
                            ax.axis("off")
                            end_row = min(start + chunk_size, len(trades))
                            ax.set_title(
                                f"Trade List (rows {start + 1}-{end_row} of {len(trades)})",
                                fontsize=10,
                            )
                            table = ax.table(
                                cellText=chunk.values.astype(str),
                                colLabels=[str(c) for c in chunk.columns],
                                cellLoc="center",
                                loc="center",
                                colColours=["#f2f2f2"] * len(chunk.columns),
                            )
                            table.auto_set_font_size(False)
                            table.set_fontsize(7)
                            table.scale(1.0, 1.1)
                        fig.tight_layout(pad=1.0)
                        pdf.savefig(fig, bbox_inches="tight", pad_inches=0.4)
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


def generate_walk_forward_report(wf_result: dict) -> dict:
    """Aggregate walk-forward per-window results into a summary table + equity curve.

    ``wf_result`` is the dict returned by
    :meth:`backtest.engine.BacktestEngine.walk_forward` or
    :meth:`backtest.engine.BacktestEngine.walk_forward_portfolio`, i.e.
    ``{"returns": [...], "results": [result_dict, ...], ...}``.

    Returns a dict with:

    * ``summary``: :class:`pandas.DataFrame` with one row per window
      (total_return, sharpe_ratio, sortino_ratio, max_drawdown, calmar_ratio,
      start_equity, end_equity).
    * ``equity_curve``: :class:`pandas.Series` chaining the per-window equity
      curves into a single continuous curve.
    * ``mean_return``, ``std_return``, ``positive_periods``,
      ``total_periods``: aggregates copied from ``wf_result`` when present.
    """
    wf_result = wf_result or {}
    results = wf_result.get("results", []) or []

    rows: list[dict[str, Any]] = []
    equity_segments: list[pd.Series] = []
    cumulative_before = 1.0

    for i, res in enumerate(results):
        res = res or {}
        total_return = float(res.get("total_return", 0.0))
        rows.append(
            {
                "window": i,
                "total_return": total_return,
                "sharpe_ratio": float(res.get("sharpe_ratio", 0.0)),
                "sortino_ratio": float(res.get("sortino_ratio", 0.0)),
                "max_drawdown": float(res.get("max_drawdown", 0.0)),
                "calmar_ratio": float(res.get("calmar_ratio", 0.0)),
                "start_equity": float(cumulative_before),
                "end_equity": float(cumulative_before * (1.0 + total_return)),
            }
        )

        ec = res.get("equity_curve")
        if ec is not None:
            try:
                s = ec if isinstance(ec, pd.Series) else pd.Series(ec)
                s = s.astype(float)
                if len(s) > 0:
                    first = float(s.iloc[0])
                    if first != 0 and first == first:  # non-zero and not NaN
                        equity_segments.append((s / first) * cumulative_before)
            except Exception:
                pass

        cumulative_before = cumulative_before * (1.0 + total_return)

    summary = pd.DataFrame(rows)
    if equity_segments:
        equity_curve = pd.concat(equity_segments)
    else:
        equity_curve = pd.Series(dtype=float)

    report: dict[str, Any] = {
        "summary": summary,
        "equity_curve": equity_curve,
    }
    for key in ("mean_return", "std_return", "positive_periods", "total_periods"):
        if key in wf_result:
            report[key] = wf_result[key]

    # Aggregate attribution across windows when present.
    brinsons_raw = [(r or {}).get("brinson") for r in results]
    brinsons: list[dict[str, Any]] = [
        cast(dict[str, Any], b) for b in brinsons_raw if isinstance(b, dict)
    ]
    if brinsons:
        alloc = sum(_series_sum(b.get("allocation_total")) for b in brinsons)
        sel = sum(_series_sum(b.get("selection_total")) for b in brinsons)
        inter = sum(_series_sum(b.get("interaction_total")) for b in brinsons)
        port_ret = sum(_series_sum(b.get("portfolio_return")) for b in brinsons)
        bench_ret = sum(_series_sum(b.get("benchmark_return")) for b in brinsons)
        frames = []
        for b in brinsons:
            s = b.get("summary")
            if isinstance(s, pd.DataFrame) and len(s) > 0:
                frames.append(s)
        agg_summary = None
        if frames:
            combined = pd.concat(frames, ignore_index=True)
            if "asset" in combined.columns:
                for col in ("allocation", "selection", "interaction", "total"):
                    if col in combined.columns:
                        combined[col] = pd.to_numeric(combined[col], errors="coerce").fillna(0.0)
                base_cols = ("allocation", "selection", "interaction", "total")
                cols = [c for c in base_cols if c in combined.columns]
                agg_dict = {c: "sum" for c in cols}
                agg_summary = combined.groupby("asset", as_index=False).agg(agg_dict)
        report["brinson"] = {
            "allocation_total": alloc,
            "selection_total": sel,
            "interaction_total": inter,
            "portfolio_return": port_ret,
            "benchmark_return": bench_ret,
            "summary": agg_summary if agg_summary is not None else pd.DataFrame(),
        }

    factors_raw = [(r or {}).get("factor") for r in results]
    factors: list[dict[str, Any]] = [
        cast(dict[str, Any], f) for f in factors_raw if isinstance(f, dict)
    ]
    if factors:
        n = len(factors)
        alpha = sum(_safe_float(f.get("alpha")) for f in factors) / n
        alpha_ann = sum(_safe_float(f.get("alpha_annualized")) for f in factors) / n
        r2 = sum(_safe_float(f.get("r_squared")) for f in factors) / n
        n_obs = sum(int(_safe_float(f.get("n_obs"))) for f in factors)
        beta_names: set[str] = set()
        for f in factors:
            beta_obj = f.get("beta")
            if isinstance(beta_obj, pd.Series):
                beta_names.update(str(x) for x in beta_obj.index)
            elif isinstance(beta_obj, dict):
                beta_names.update(beta_obj.keys())
        beta_agg: dict[str, float] = {}
        for name in beta_names:
            vals = []
            for f in factors:
                beta_obj2 = f.get("beta")
                v = None
                if isinstance(beta_obj2, pd.Series) and name in beta_obj2.index:
                    v = beta_obj2[name]
                elif isinstance(beta_obj2, dict) and name in beta_obj2:
                    v = beta_obj2[name]
                if v is not None:
                    vals.append(_safe_float(v))
            if vals:
                beta_agg[name] = float(sum(vals) / len(vals))
        report["factor"] = {
            "alpha": alpha,
            "alpha_annualized": alpha_ann,
            "r_squared": r2,
            "n_obs": n_obs,
            "beta": pd.Series(beta_agg) if beta_agg else pd.Series(dtype=float),
        }

    return report


def walk_forward_report_to_dict(wf_report: dict) -> dict:
    """Return a serializable dict of a walk-forward report including attribution."""
    wf_report = wf_report or {}
    out: dict[str, Any] = {}
    summary = wf_report.get("summary")
    if isinstance(summary, pd.DataFrame):
        out["summary"] = summary.to_dict(orient="records")
    else:
        try:
            out["summary"] = list(summary) if summary is not None else []
        except Exception:
            out["summary"] = []
    for key in ("mean_return", "std_return", "positive_periods", "total_periods"):
        if key in wf_report:
            try:
                out[key] = wf_report[key]
            except Exception:
                pass
    brinson = wf_report.get("brinson")
    factor = wf_report.get("factor")
    if isinstance(brinson, dict) or isinstance(factor, dict):
        out.update(attribution_to_dict({"brinson": brinson, "factor": factor}))
    return out


def generate_walk_forward_html_report(wf_report: dict, title: str = "Walk-Forward Report") -> str:
    """Render a walk-forward report as HTML with summary table and equity chart."""
    wf_report = wf_report or {}
    summary = wf_report.get("summary")
    if not isinstance(summary, pd.DataFrame):
        try:
            if summary is not None:
                summary = pd.DataFrame(summary)
            else:
                summary = pd.DataFrame()
        except Exception:
            summary = pd.DataFrame()
    equity_curve = wf_report.get("equity_curve")
    if equity_curve is not None and not isinstance(equity_curve, pd.Series):
        try:
            import pandas as _pd

            equity_curve = _pd.Series(equity_curve)
        except Exception:
            equity_curve = None

    html = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8" />',
        f"<title>{title}</title>",
        "<style>",
        "body{font-family:Arial,Helvetica,sans-serif;margin:40px;background:#fff;color:#222}",
        "h1{font-size:22px;margin-bottom:10px}",
        "table{border-collapse:collapse;width:100%;max-width:900px}",
        "th,td{border:1px solid #ddd;padding:6px 8px;font-size:12px;text-align:right}",
        "th{background:#f5f5f5;text-align:right}",
        "td:first-child,th:first-child{text-align:left}",
        ".chart{margin-top:24px}",
        "</style>",
        "</head>",
        "<body>",
        f"<h1>{title}</h1>",
    ]

    if len(summary) > 0:
        html.append("<h2>Summary Table</h2>")
        html.append(summary.to_html(index=False, border=0))
    else:
        html.append("<h2>Summary Table</h2>")
        html.append("<p>No walk-forward windows.</p>")

    if equity_curve is not None and len(equity_curve) > 0:
        html.append('<div class="chart">')
        html.append("<h2>Equity Curve</h2>")
        try:
            values = equity_curve.astype(float).values
            n = len(values)
            if n > 0:
                mn = float(min(values))
                mx = float(max(values))
                span = mx - mn if (mx - mn) != 0 else 1.0
                width = 600
                height = 200
                xs = [20 + (width - 40) * i / (n - 1) if n > 1 else 310 for i in range(n)]
                ys = [height - 40 - (height - 80) * (v - mn) / span for v in values]
                points = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
                html.append(
                    '<svg width="640" height="240" xmlns="http://www.w3.org/2000/svg">'
                )
                html.append(
                    f'<polyline points="{points}" fill="none" stroke="#1f77b4" stroke-width="2" />'
                )
                html.append("</svg>")
        except Exception:
            pass
        html.append("</div>")
    else:
        html.append("<h2>Equity Curve</h2>")

    # Attribution (if available)
    brinson, factor = _get_attribution(wf_report or {})
    if brinson is not None or factor is not None:
        html.append("<h2>Attribution</h2>")
        if isinstance(brinson, dict):
            html.append("<h3>Brinson Attribution (aggregated)</h3>")
            html.append("<table><tr><th>Effect</th><th>Total</th></tr>")
            html.append(f"<tr><td>Allocation</td><td>{_fmt_pct(_series_sum(brinson.get('allocation_total')))}</td></tr>")
            html.append(f"<tr><td>Selection</td><td>{_fmt_pct(_series_sum(brinson.get('selection_total')))}</td></tr>")
            html.append(f"<tr><td>Interaction</td><td>{_fmt_pct(_series_sum(brinson.get('interaction_total')))}</td></tr>")
            html.append("</table>")
        if isinstance(factor, dict):
            html.append("<h3>Factor Attribution (aggregated)</h3>")
            html.append("<table><tr><th>Metric</th><th>Value</th></tr>")
            alpha_val = _fmt_num(_safe_float(factor.get("alpha")))
            html.append(f"<tr><td>Alpha (period)</td><td>{alpha_val}</td></tr>")
            alpha_ann_val = _fmt_num(_safe_float(factor.get("alpha_annualized")))
            html.append(f"<tr><td>Alpha (annualized)</td><td>{alpha_ann_val}</td></tr>")
            html.append(f"<tr><td>R-squared</td><td>{_fmt_num(_safe_float(factor.get('r_squared')))}</td></tr>")
            html.append("</table>")

    html.extend(["</body>", "</html>"])
    return "\n".join(html)


def generate_walk_forward_pdf_report(
    wf_report: dict, output_path: str, title: str = "Walk-Forward Report"
) -> str:
    """Render a walk-forward report as PDF with summary table and equity chart."""
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_pdf import PdfPages
    except Exception:
        html = generate_walk_forward_html_report(wf_report, title=title)
        html_path = output_path.replace(".pdf", ".html")
        try:
            Path(html_path).write_text(html)
            return html_path
        except Exception:
            return html

    wf_report = wf_report or {}
    summary = wf_report.get("summary")
    if not isinstance(summary, pd.DataFrame):
        try:
            if summary is not None:
                summary = pd.DataFrame(summary)
            else:
                summary = pd.DataFrame()
        except Exception:
            summary = pd.DataFrame()
    equity_curve = wf_report.get("equity_curve")
    if equity_curve is not None and not isinstance(equity_curve, pd.Series):
        try:
            import pandas as _pd

            equity_curve = _pd.Series(equity_curve)
        except Exception:
            equity_curve = None

    try:
        with PdfPages(output_path) as pdf:
            # Page 1: Summary table
            fig, ax = plt.subplots(figsize=(11, 8.5))
            ax.axis("off")
            ax.set_title(title, fontsize=14, pad=20)
            if len(summary) > 0:
                try:
                    table_data = [list(summary.columns)] + summary.values.tolist()
                    table = ax.table(cellText=table_data, loc="center", cellLoc="center")
                    table.auto_set_font_size(False)
                    table.set_fontsize(7)
                    table.scale(1.0, 1.2)
                except Exception:
                    pass
            else:
                ax.text(0.5, 0.5, "No walk-forward windows.", ha="center", va="center")
            pdf.savefig(fig, bbox_inches="tight", pad_inches=0.5)
            plt.close(fig)

            # Page 2: Equity curve chart
            if equity_curve is not None and len(equity_curve) > 0:
                try:
                    fig, ax = plt.subplots(figsize=(11, 4.5))
                    eq = equity_curve.astype(float)
                    ax.plot(eq.index, eq.values, linewidth=1.5)
                    ax.set_title("Equity Curve")
                    ax.set_ylabel("Equity")
                    ax.grid(True, alpha=0.3)
                    fig.tight_layout()
                    pdf.savefig(fig, bbox_inches="tight", pad_inches=0.5)
                    plt.close(fig)
                except Exception:
                    pass
            else:
                try:
                    fig, ax = plt.subplots(figsize=(11, 4.5))
                    ax.axis("off")
                    ax.set_title("Equity Curve")
                    ax.text(0.5, 0.5, "No equity curve data.", ha="center", va="center")
                    pdf.savefig(fig, bbox_inches="tight", pad_inches=0.5)
                    plt.close(fig)
                except Exception:
                    pass
        return output_path
    except Exception:
        try:
            html = generate_walk_forward_html_report(wf_report, title=title)
            html_path = output_path.replace(".pdf", ".html")
            Path(html_path).write_text(html)
            return html_path
        except Exception:
            return output_path
