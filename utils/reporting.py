from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, cast

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


def _pdf_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _write_minimal_pdf(output_path: str, title: str, lines: list[str]) -> str:
    """Write a minimal valid PDF-1.4 document at output_path (no external deps)."""
    buf = bytearray()
    offsets: dict[int, int] = {}

    def obj(num: int, content: bytes) -> None:
        nonlocal buf
        offsets[num] = len(buf)
        buf += f"{num} 0 obj\n".encode("ascii")
        buf += content
        buf += b"\nendobj\n"

    buf += b"%PDF-1.4\n%\xE2\xE3\xCF\xD3\n"

    stream_parts = [
        b"BT",
        b"/F1 12 Tf",
        b"50 740 Td",
        f"({_pdf_escape(title)}) Tj".encode("latin-1", errors="replace"),
    ]
    for line in lines:
        stream_parts.append(b"0 -16 Td")
        stream_parts.append(f"({_pdf_escape(line)}) Tj".encode("latin-1", errors="replace"))
    stream_parts.append(b"ET")
    stream = b"\n".join(stream_parts) + b"\n"

    obj(1, b"<< /Type /Catalog /Pages 2 0 R >>")
    obj(2, b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    obj(3, b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]"
           b" /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>")
    obj(4, b"<< /Length "
           + str(len(stream)).encode("ascii")
           + b" >>\nstream\n"
           + stream
           + b"\nendstream")
    obj(5, b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    xref_offset = len(buf)
    buf += b"xref\n"
    count = len(offsets) + 1
    buf += f"0 {count}\n".encode("ascii")
    buf += b"0000000000 65535 f\r\n"
    for num in sorted(offsets):
        buf += f"{offsets[num]:010d} 00000 n\r\n".encode("ascii")
    buf += b"trailer\n<< /Size " + str(count).encode("ascii") + b" /Root 1 0 R >>\n"
    buf += b"startxref\n"
    buf += f"{xref_offset}\n".encode("ascii")
    buf += b"%%EOF\n"
    Path(output_path).write_bytes(buf)
    return output_path


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
        lines = [title]
        if isinstance(result, dict):
            total_return = result.get("total_return")
            if total_return is not None:
                try:
                    lines.append(f"Total Return: {float(total_return):.4%}")
                except Exception:
                    pass
        try:
            return _write_minimal_pdf(output_path, title, lines)
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


def bootstrap_walk_forward_intervals(
    wf_result: dict,
    n_iterations: int = 1000,
    seed: int = 42,
    confidence: float = 0.95,
) -> dict[str, tuple[float, float]]:
    """Bootstrap confidence intervals for walk-forward aggregates.

    Resamples the per-window out-of-sample returns with replacement,
    recomputes the walk-forward aggregates for each resample, and returns
    ``(low, high)`` percentile intervals for ``mean_return``,
    ``oos_mean_return`` and ``oos_is_ratio``.
    """
    wf_result = wf_result or {}
    results = wf_result.get("results", []) or []
    oos_returns = [
        float(r.get("oos_total_return", r.get("total_return", 0.0)))
        for r in results
    ]
    is_returns = [
        float(r.get("is_total_return", 0.0))
        for r in results
        if "is_total_return" in r
    ]
    if not oos_returns:
        return {}

    try:
        import numpy as _np
    except Exception:
        return {}

    rng = _np.random.default_rng(seed)
    n = len(oos_returns)
    oos_arr = _np.array(oos_returns, dtype=float)
    is_arr = _np.array(is_returns, dtype=float) if len(is_returns) == n else None

    def _percentiles(values: list[float]) -> tuple[float, float]:
        arr = _np.array(values, dtype=float)
        tail = 100.0 * ((1.0 - float(confidence)) / 2.0)
        low = float(_np.percentile(arr, tail))
        high = float(_np.percentile(arr, 100.0 - tail))
        return (low, high)

    mean_bs: list[float] = []
    ratio_bs: list[float] = []
    for _ in range(max(1, int(n_iterations))):
        idx = rng.integers(0, n, size=n)
        sample = oos_arr[idx]
        m = float(_np.mean(sample))
        mean_bs.append(m)
        if is_arr is not None:
            is_sample = is_arr[idx]
            im = float(_np.mean(is_sample))
            ratio_bs.append(m / im if im != 0 else 0.0)

    intervals: dict[str, tuple[float, float]] = {}
    if mean_bs:
        intervals["mean_return"] = _percentiles(mean_bs)
        intervals["oos_mean_return"] = _percentiles(mean_bs)
    if ratio_bs:
        intervals["oos_is_ratio"] = _percentiles(ratio_bs)
    return intervals


def sweep_cost_sensitivity(
    walk_forward_fn: Callable[..., dict[str, Any]],
    cost_grid: list[tuple[float, float]],
    **wf_kwargs: Any,
) -> list[dict[str, Any]]:
    """Run walk-forward across a grid of (fee_rate, slippage) cost assumptions.

    For each ``(fee_rate, slippage)`` pair in ``cost_grid``, calls
    ``walk_forward_fn`` with the supplied keyword arguments (overriding
    ``fee_rate`` and ``slippage`` per config) and records the resulting
    walk-forward aggregates.

    ``walk_forward_fn`` should be a callable (e.g. a lambda wrapping
    ``engine.walk_forward`` or ``engine.walk_forward_portfolio``) that accepts
    ``fee_rate`` and ``slippage`` keyword arguments and returns the
    walk-forward result dict (the same shape returned by
    :meth:`backtest.engine.BacktestEngine.walk_forward`).

    Returns a list of dicts, one per config (in grid order), with keys:
    ``fee_rate``, ``slippage``, ``mean_return``, ``oos_mean_return``,
    ``oos_is_ratio``, ``max_drawdown`` (mean per-window drawdown), plus the
    original ``walk_forward`` result under ``"result"`` when available.
    """
    results: list[dict[str, Any]] = []
    for fee_rate, slippage in cost_grid:
        try:
            wf = walk_forward_fn(fee_rate=float(fee_rate), slippage=float(slippage), **wf_kwargs)
        except Exception:
            continue
        if not isinstance(wf, dict):
            continue
        row: dict[str, Any] = {
            "fee_rate": float(fee_rate),
            "slippage": float(slippage),
            "mean_return": _safe_float(wf.get("mean_return", 0.0)),
            "oos_mean_return": _safe_float(wf.get("oos_mean_return", 0.0)),
            "oos_is_ratio": _safe_float(wf.get("oos_is_ratio", 0.0)),
        }
        # Aggregate max drawdown across per-window results (mean of window DDs).
        per_window = wf.get("results", []) or []
        try:
            import numpy as _np

            dds = [
                _safe_float((r or {}).get("max_drawdown", 0.0))
                for r in per_window
            ]
            row["max_drawdown"] = float(_np.mean(dds)) if dds else 0.0
        except Exception:
            row["max_drawdown"] = 0.0
        row["result"] = wf
        results.append(row)
    return results


def load_live_results_csv(path: str) -> list[dict[str, Any]]:
    """Load live/paper trading results from a CSV.

    Expected columns: ``scheme``, ``live_mean_return``, ``live_max_drawdown``
    (plus optional ``live_total_return`` and ``live_sharpe_ratio``). Values are
    decimals (e.g. ``0.05`` for 5%). Returns one dict per scheme.
    """
    import csv

    schemes: list[dict[str, Any]] = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            scheme = (row.get("scheme") or "").strip()
            if not scheme:
                continue
            schemes.append(
                {
                    "scheme": scheme,
                    "live_mean_return": _safe_float(row.get("live_mean_return")),
                    "live_max_drawdown": _safe_float(row.get("live_max_drawdown")),
                    "live_total_return": _safe_float(row.get("live_total_return", 0.0)),
                    "live_sharpe_ratio": _safe_float(row.get("live_sharpe_ratio", 0.0)),
                }
            )
    return schemes


def load_benchmarks_csv(path: str) -> list[dict[str, Any]]:
    """Load benchmark strategy registry from a CSV.

    Expected columns: ``name`` (benchmark name), ``mean_return``, ``max_drawdown``
    (plus optional ``total_return`` and ``sharpe_ratio``). Values are decimals.
    Returns one dict per benchmark.
    """
    import csv

    benchmarks: list[dict[str, Any]] = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = (row.get("name") or row.get("benchmark") or "").strip()
            if not name:
                continue
            benchmarks.append(
                {
                    "name": name,
                    "mean_return": _safe_float(row.get("mean_return")),
                    "max_drawdown": _safe_float(row.get("max_drawdown")),
                    "total_return": _safe_float(row.get("total_return", 0.0)),
                    "sharpe_ratio": _safe_float(row.get("sharpe_ratio", 0.0)),
                }
            )
    return benchmarks


def _benchmarks_section(benchmarks: Any, wf_result: dict) -> dict[str, Any]:
    """Build the ``benchmarks`` report section from a benchmark registry.

    Compares each benchmark's metrics against the walk-forward out-of-sample
    baseline (mean return / max drawdown).
    """
    benchmarks_in: list[dict[str, Any]] = []
    if isinstance(benchmarks, dict):
        candidate = benchmarks.get("benchmarks")
        if isinstance(candidate, list):
            benchmarks_in = [b for b in candidate if isinstance(b, dict)]
        elif "name" in benchmarks:
            benchmarks_in = [benchmarks]
    elif isinstance(benchmarks, list):
        benchmarks_in = [b for b in benchmarks if isinstance(b, dict)]

    results = wf_result.get("results", []) or []
    oos_returns: list[float] = []
    oos_drawdowns: list[float] = []
    for res in results:
        res = res or {}
        if "oos_total_return" in res:
            oos_returns.append(_safe_float(res.get("oos_total_return")))
        elif "total_return" in res:
            oos_returns.append(_safe_float(res.get("total_return")))
        oos_drawdowns.append(_safe_float(res.get("max_drawdown", 0.0)))

    def _mean(vals: list[float]) -> float:
        return sum(vals) / len(vals) if vals else 0.0

    wf_oos_mean_return = _mean(oos_returns)
    wf_oos_max_drawdown = _mean(oos_drawdowns)

    items: list[dict[str, Any]] = []
    for b in benchmarks_in:
        name = str(b.get("name", "") or "")
        items.append(
            {
                "name": name,
                "wf_oos_mean_return": wf_oos_mean_return,
                "wf_oos_max_drawdown": wf_oos_max_drawdown,
                "benchmark_mean_return": _safe_float(b.get("mean_return")),
                "benchmark_max_drawdown": _safe_float(b.get("max_drawdown")),
                "benchmark_total_return": _safe_float(b.get("total_return", 0.0)),
                "benchmark_sharpe_ratio": _safe_float(b.get("sharpe_ratio", 0.0)),
            }
        )

    return {
        "benchmarks": items,
        "wf_oos_mean_return": wf_oos_mean_return,
        "wf_oos_max_drawdown": wf_oos_max_drawdown,
        "benchmark_count": len(items),
    }


def _live_trading_section(live_results: Any, wf_result: dict) -> dict[str, Any]:
    """Build the ``live_trading`` report section from live/paper results.

    Compares each live scheme's realized metrics against the walk-forward
    out-of-sample baseline (expected performance).
    """
    schemes_in: list[dict[str, Any]] = []
    if isinstance(live_results, dict):
        candidate = live_results.get("schemes")
        if isinstance(candidate, list):
            schemes_in = [r for r in candidate if isinstance(r, dict)]
        elif "scheme" in live_results:
            schemes_in = [live_results]
    elif isinstance(live_results, list):
        schemes_in = [r for r in live_results if isinstance(r, dict)]

    results = wf_result.get("results", []) or []
    oos_returns: list[float] = []
    oos_drawdowns: list[float] = []
    for res in results:
        res = res or {}
        if "oos_total_return" in res:
            oos_returns.append(_safe_float(res.get("oos_total_return")))
        elif "total_return" in res:
            oos_returns.append(_safe_float(res.get("total_return")))
        oos_drawdowns.append(_safe_float(res.get("max_drawdown", 0.0)))

    def _mean(vals: list[float]) -> float:
        return sum(vals) / len(vals) if vals else 0.0

    wf_oos_mean_return = _mean(oos_returns)
    wf_oos_max_drawdown = _mean(oos_drawdowns)

    schemes_out: list[dict[str, Any]] = []
    for s in schemes_in:
        scheme = str(s.get("scheme", "") or "")
        live_mean_return = _safe_float(s.get("live_mean_return"))
        live_max_drawdown = _safe_float(s.get("live_max_drawdown"))
        schemes_out.append(
            {
                "scheme": scheme,
                "oos_mean_return": wf_oos_mean_return,
                "live_mean_return": live_mean_return,
                "oos_max_drawdown": wf_oos_max_drawdown,
                "live_max_drawdown": live_max_drawdown,
                "live_total_return": _safe_float(s.get("live_total_return", 0.0)),
                "live_sharpe_ratio": _safe_float(s.get("live_sharpe_ratio", 0.0)),
            }
        )

    live_means = [s["live_mean_return"] for s in schemes_out]
    live_drawdowns = [s["live_max_drawdown"] for s in schemes_out]

    return {
        "schemes": schemes_out,
        "oos_mean_return": wf_oos_mean_return,
        "oos_max_drawdown": wf_oos_max_drawdown,
        "live_mean_return": _mean(live_means),
        "live_max_drawdown": _mean(live_drawdowns),
        "scheme_count": len(schemes_out),
    }


def generate_walk_forward_report(
    wf_result: dict, multi_horizon: Any = None, live_results: Any = None,
    benchmarks: Any = None,
) -> dict:
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

    try:
        import numpy as _np
    except Exception:
        _np = None  # type: ignore[assignment]

    rows: list[dict[str, Any]] = []
    equity_segments: list[pd.Series] = []
    cumulative_before = 1.0

    for i, res in enumerate(results):
        res = res or {}
        total_return = float(res.get("total_return", 0.0))
        row: dict[str, Any] = {
            "window": i,
            "total_return": total_return,
            "sharpe_ratio": float(res.get("sharpe_ratio", 0.0)),
            "sortino_ratio": float(res.get("sortino_ratio", 0.0)),
            "max_drawdown": float(res.get("max_drawdown", 0.0)),
            "calmar_ratio": float(res.get("calmar_ratio", 0.0)),
            "start_equity": float(cumulative_before),
            "end_equity": float(cumulative_before * (1.0 + total_return)),
        }
        # In-sample vs out-of-sample metrics (when the engine attached them).
        if "is_total_return" in res:
            row["is_total_return"] = float(res.get("is_total_return", 0.0))
            row["is_sharpe_ratio"] = float(res.get("is_sharpe_ratio", 0.0))
            row["is_max_drawdown"] = float(res.get("is_max_drawdown", 0.0))
        if "oos_total_return" in res:
            row["oos_total_return"] = float(res.get("oos_total_return", total_return))
        rows.append(row)

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

    # Aggregate in-sample vs out-of-sample performance across windows when the
    # engine attached IS metrics to each window result.
    is_returns = [float(r.get("is_total_return", 0.0)) for r in rows if "is_total_return" in r]
    oos_returns = [
        float(r.get("oos_total_return", r.get("total_return", 0.0)))
        for r in rows
        if "is_total_return" in r
    ]
    if is_returns and _np is not None:
        try:
            is_arr = _np.array(is_returns, dtype=float)
            oos_arr = _np.array(oos_returns, dtype=float)
            is_mean = float(_np.mean(is_arr))
            oos_mean = float(_np.mean(oos_arr))
            report["is_vs_oos"] = {
                "is_mean_return": is_mean,
                "oos_mean_return": oos_mean,
                "oos_is_ratio": (oos_mean / is_mean) if is_mean != 0 else 0.0,
                "is_mean_sharpe": float(
                    _np.mean(_np.array(
                        [float(r.get("is_sharpe_ratio", 0.0))
                        for r in rows
                        if "is_total_return" in r],
                        dtype=float,
                    ))
                ),
                "oos_mean_sharpe": float(
                    _np.mean(_np.array(
                        [float(r.get("sharpe_ratio", 0.0))
                        for r in rows
                        if "is_total_return" in r],
                        dtype=float,
                    ))
                ),
                "is_mean_max_drawdown": float(
                    _np.mean(_np.array(
                        [float(r.get("is_max_drawdown", 0.0))
                        for r in rows
                        if "is_total_return" in r],
                        dtype=float,
                    ))
                ),
                "oos_mean_max_drawdown": float(
                    _np.mean(_np.array(
                        [float(r.get("max_drawdown", 0.0))
                        for r in rows
                        if "is_total_return" in r],
                        dtype=float,
                    ))
                ),
            }
        except Exception:
            pass

    # Bootstrap confidence intervals for walk-forward aggregates when
    # per-window returns are available.
    returns_list = wf_result.get("returns", []) or []
    if returns_list:
        try:
            report["confidence_intervals"] = bootstrap_walk_forward_intervals(
                wf_result,
            )
        except Exception:
            pass

    # Cost-model sensitivity sweep results (when the caller attached a
    # precomputed sweep via the ``cost_sensitivity`` key on the wf_result).
    cost_sensitivity = wf_result.get("cost_sensitivity")
    if isinstance(cost_sensitivity, list) and cost_sensitivity:
        try:
            report["cost_sensitivity"] = [
                {k: v for k, v in row.items() if k != "result"} for row in cost_sensitivity
            ]
        except Exception:
            pass

    # Multi-horizon walk-forward results (expanding vs rolling windows).
    multi_horizon_data = (
        multi_horizon if multi_horizon is not None else wf_result.get("multi_horizon")
    )
    if isinstance(multi_horizon_data, dict) and multi_horizon_data:
        try:
            # If values are wf_result dicts, compute aggregates
            processed = []
            for mode_name, mh_res in multi_horizon_data.items():
                if isinstance(mh_res, dict):
                    agg = {}
                    agg["mode"] = mode_name
                    # Try to extract from existing aggregates
                    if "mean_return" in mh_res:
                        agg["mean_return"] = mh_res["mean_return"]
                    if "oos_mean_return" in mh_res:
                        agg["oos_mean_return"] = mh_res["oos_mean_return"]
                    elif "mean_return" in mh_res:
                        agg["oos_mean_return"] = mh_res.get(
                            "oos_mean_return", mh_res["mean_return"]
                        )
                    # compute from results if needed
                    results_mh = mh_res.get("results") or []
                    if "oos_mean_return" not in agg and results_mh:
                        try:
                            import numpy as _np2

                            oos_rets = []
                            for r in results_mh:
                                r2 = r or {}
                                if "oos_total_return" in r2:
                                    oos_rets.append(float(r2["oos_total_return"]))
                                elif "total_return" in r2:
                                    oos_rets.append(float(r2["total_return"]))
                            if oos_rets:
                                agg["oos_mean_return"] = float(_np2.mean(oos_rets))
                        except Exception:
                            pass
                    if "mean_return" not in agg and "returns" in mh_res:
                        try:
                            import numpy as _np2

                            rets_arr = _np2.array(mh_res["returns"], dtype=float)
                            if rets_arr.size > 0:
                                agg["mean_return"] = float(_np2.mean(rets_arr))
                        except Exception:
                            pass
                    # oos_is_ratio
                    if "oos_is_ratio" in mh_res:
                        agg["oos_is_ratio"] = mh_res["oos_is_ratio"]
                    else:
                        is_m = (
                            agg.get("mean_return")
                            if "is_mean_return" in mh_res or "is_mean_return" in agg
                            else mh_res.get("is_mean_return")
                        )
                        # look for is_mean_return
                        if is_m is None and results_mh:
                            try:
                                is_list = [
                                    float((r or {}).get("is_total_return", 0.0))
                                    for r in results_mh
                                    if "is_total_return" in (r or {})
                                ]
                                if is_list:
                                    import numpy as _np2

                                    is_m = float(_np2.mean(is_list))
                            except Exception:
                                pass
                        oos_m = agg.get("oos_mean_return")
                        if is_m is not None and oos_m is not None and is_m != 0:
                            agg["oos_is_ratio"] = float(oos_m / is_m)
                    # max drawdown
                    if "max_drawdown" in mh_res:
                        agg["max_drawdown"] = mh_res["max_drawdown"]
                    else:
                        if results_mh:
                            try:
                                import numpy as _np2

                                dds = [
                                    float((r or {}).get("max_drawdown", 0.0))
                                    for r in results_mh
                                ]
                                if dds:
                                    agg["max_drawdown"] = float(_np2.mean(dds))
                            except Exception:
                                pass
                    # copy if they came from aggregate keys
                    if (
                        "is_mean_return" in mh_res
                        and "oos_mean_return" not in agg
                        and "is_vs_oos" not in agg
                    ):
                        pass
                    processed.append(agg)
                else:
                    processed.append(mh_res)
            report["multi_horizon"] = processed if processed else multi_horizon_data
        except Exception:
            pass
    elif isinstance(multi_horizon_data, list) and multi_horizon_data:
        try:
            report["multi_horizon"] = multi_horizon_data
        except Exception:
            pass

    # Live/paper trading results attached for comparison against walk-forward
    # out-of-sample (expected) performance.
    live_results_param = (
        live_results if live_results is not None else wf_result.get("live_results")
    )
    if live_results_param is not None:
        try:
            report["live_trading"] = _live_trading_section(live_results_param, wf_result)
        except Exception:
            pass

    benchmarks_param = (
        benchmarks if benchmarks is not None else wf_result.get("benchmarks")
    )
    if benchmarks_param is not None:
        try:
            report["benchmarks"] = _benchmarks_section(benchmarks_param, wf_result)
        except Exception:
            pass

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
    is_vs_oos = wf_report.get("is_vs_oos")
    if isinstance(is_vs_oos, dict):
        try:
            out["is_vs_oos"] = dict(is_vs_oos)
        except Exception:
            pass
    confidence_intervals = wf_report.get("confidence_intervals")
    if isinstance(confidence_intervals, dict) and confidence_intervals:
        try:
            out["confidence_intervals"] = {
                str(k): [float(v[0]), float(v[1])]
                for k, v in confidence_intervals.items()
                if isinstance(v, (list, tuple)) and len(v) == 2
            }
        except Exception:
            pass
    cost_sensitivity = wf_report.get("cost_sensitivity")
    if isinstance(cost_sensitivity, list) and cost_sensitivity:
        try:
            out["cost_sensitivity"] = [
                {str(k): v for k, v in row.items() if k != "result"}
                for row in cost_sensitivity
            ]
        except Exception:
            pass
    multi_horizon = wf_report.get("multi_horizon")
    if multi_horizon is not None:
        try:
            out["multi_horizon"] = multi_horizon
        except Exception:
            pass
    live_trading = wf_report.get("live_trading")
    if isinstance(live_trading, dict) and live_trading:
        try:
            out["live_trading"] = {
                "schemes": [
                    {str(k): v for k, v in s.items() if k != "result"}
                    for s in live_trading.get("schemes", [])
                    if isinstance(s, dict)
                ],
                "oos_mean_return": float(live_trading.get("oos_mean_return", 0.0)),
                "oos_max_drawdown": float(live_trading.get("oos_max_drawdown", 0.0)),
                "live_mean_return": float(live_trading.get("live_mean_return", 0.0)),
                "live_max_drawdown": float(live_trading.get("live_max_drawdown", 0.0)),
                "scheme_count": int(live_trading.get("scheme_count", 0)),
            }
        except Exception:
            pass
    benchmarks = wf_report.get("benchmarks")
    if isinstance(benchmarks, dict) and benchmarks:
        try:
            out["benchmarks"] = {
                "benchmarks": [
                    {str(k): v for k, v in b.items() if k != "result"}
                    for b in benchmarks.get("benchmarks", [])
                    if isinstance(b, dict)
                ],
                "wf_oos_mean_return": float(benchmarks.get("wf_oos_mean_return", 0.0)),
                "wf_oos_max_drawdown": float(benchmarks.get("wf_oos_max_drawdown", 0.0)),
                "benchmark_count": int(benchmarks.get("benchmark_count", 0)),
            }
        except Exception:
            pass
    brinson = wf_report.get("brinson")
    factor = wf_report.get("factor")
    if isinstance(brinson, dict) or isinstance(factor, dict):
        out.update(attribution_to_dict({"brinson": brinson, "factor": factor}))
    return out


def generate_walk_forward_text_report(wf_report: dict) -> str:
    """Build a human-readable text summary of a walk-forward report."""
    wf_report = wf_report or {}
    summary = wf_report.get("summary")
    if not isinstance(summary, pd.DataFrame):
        try:
            summary = pd.DataFrame(summary) if summary is not None else pd.DataFrame()
        except Exception:
            summary = pd.DataFrame()

    lines: list[str] = [
        "Walk-Forward Report",
        "====================",
    ]
    for key in ("mean_return", "std_return", "positive_periods", "total_periods"):
        if key in wf_report:
            lines.append(f"{key}: {wf_report[key]}")
    lines.append("")

    if len(summary) > 0:
        lines.append("Per-window summary:")
        lines.append(summary.to_string(index=False))
    else:
        lines.append("No walk-forward windows.")

    # In-Sample vs Out-of-Sample comparison (when IS metrics are present).
    is_vs_oos = wf_report.get("is_vs_oos")
    if isinstance(is_vs_oos, dict):
        lines.append("")
        lines.append("In-Sample vs Out-of-Sample")
        lines.append("============================")
        lines.append(
            f"  Mean IS Return:        {_fmt_pct(is_vs_oos.get('is_mean_return', 0.0))}"
        )
        lines.append(
            f"  Mean OOS Return:       {_fmt_pct(is_vs_oos.get('oos_mean_return', 0.0))}"
        )
        lines.append(
            f"  OOS/IS Ratio:          {_fmt_num(is_vs_oos.get('oos_is_ratio', 0.0))}"
        )
        lines.append(
            f"  Mean IS Sharpe:        {_fmt_num(is_vs_oos.get('is_mean_sharpe', 0.0))}"
        )
        lines.append(
            f"  Mean OOS Sharpe:       {_fmt_num(is_vs_oos.get('oos_mean_sharpe', 0.0))}"
        )
        lines.append(
            f"  Mean IS Max Drawdown:  {_fmt_pct(is_vs_oos.get('is_mean_max_drawdown', 0.0))}"
        )
        lines.append(
            f"  Mean OOS Max Drawdown: {_fmt_pct(is_vs_oos.get('oos_mean_max_drawdown', 0.0))}"
        )

    # Confidence intervals (bootstrap) when present.
    confidence_intervals = wf_report.get("confidence_intervals")
    if isinstance(confidence_intervals, dict) and confidence_intervals:
        lines.append("")
        lines.append("Confidence Intervals (bootstrap)")
        lines.append("================================")
        for key in ("mean_return", "oos_mean_return", "oos_is_ratio"):
            ci = confidence_intervals.get(key)
            if isinstance(ci, (list, tuple)) and len(ci) == 2:
                low, high = float(ci[0]), float(ci[1])
                label = key.replace("_", " ").title()
                fmt = _fmt_pct if "return" in key else _fmt_num
                lines.append(f"  {label}: [{fmt(low)}, {fmt(high)}]")

    # Cost-model sensitivity sweep when present.
    cost_sensitivity = wf_report.get("cost_sensitivity")
    if isinstance(cost_sensitivity, list) and cost_sensitivity:
        lines.append("")
        lines.append("Cost-Model Sensitivity")
        lines.append("=======================")
        header = (
            "  "
            + "  ".join(
                f"{c:>12}"
                for c in [
                    "fee_rate",
                    "slippage",
                    "mean_return",
                    "oos_mean_return",
                    "oos_is_ratio",
                    "max_drawdown",
                ]
            )
        )
        lines.append(header)
        for row in cost_sensitivity:
            lines.append(
                "  "
                + "  ".join(
                    [
                        f"{_fmt_pct(row.get('fee_rate', 0.0)):>12}",
                        f"{_fmt_pct(row.get('slippage', 0.0)):>12}",
                        f"{_fmt_pct(row.get('mean_return', 0.0)):>12}",
                        f"{_fmt_pct(row.get('oos_mean_return', 0.0)):>12}",
                        f"{_fmt_num(row.get('oos_is_ratio', 0.0)):>12}",
                        f"{_fmt_pct(row.get('max_drawdown', 0.0)):>12}",
                    ]
                )
            )
        # Identify best/worst cost configs by OOS mean return.
        try:
            valid = [r for r in cost_sensitivity if isinstance(r, dict)]
            if valid:
                best = max(valid, key=lambda r: _safe_float(r.get("oos_mean_return", 0.0)))
                worst = min(valid, key=lambda r: _safe_float(r.get("oos_mean_return", 0.0)))
                lines.append("")
                lines.append(
                    f"  Best OOS return: fee={_fmt_pct(best.get('fee_rate', 0.0))}, "
                    f"slippage={_fmt_pct(best.get('slippage', 0.0))} "
                    f"-> OOS={_fmt_pct(best.get('oos_mean_return', 0.0))}"
                )
                lines.append(
                    f"  Worst OOS return: fee={_fmt_pct(worst.get('fee_rate', 0.0))}, "
                    f"slippage={_fmt_pct(worst.get('slippage', 0.0))} "
                    f"-> OOS={_fmt_pct(worst.get('oos_mean_return', 0.0))}"
                )
        except Exception:
            pass

    # Multi-Horizon Walk-Forward (expanding vs rolling)
    multi_horizon = wf_report.get("multi_horizon")
    if multi_horizon is not None:
        lines.append("")
        lines.append("Multi-Horizon Walk-Forward")
        lines.append("===========================")
        if isinstance(multi_horizon, dict):
            for key, val in multi_horizon.items():
                lines.append(f"  {key}: {val}")
        elif isinstance(multi_horizon, list):
            header = (
                "  "
                + "  ".join(
                    f"{c:>18}"
                    for c in [
                        "mode",
                        "mean_return",
                        "oos_mean_return",
                        "oos_is_ratio",
                        "max_drawdown",
                    ]
                )
            )
            lines.append(header)
            for row in multi_horizon:
                if not isinstance(row, dict):
                    continue
                lines.append(
                    "  "
                    + "  ".join(
                        [
                            f"{str(row.get('mode', '')):>18}",
                            f"{_fmt_pct(row.get('mean_return', 0.0)):>18}",
                            f"{_fmt_pct(row.get('oos_mean_return', 0.0)):>18}",
                            f"{_fmt_num(row.get('oos_is_ratio', 0.0)):>18}",
                            f"{_fmt_pct(row.get('max_drawdown', 0.0)):>18}",
                        ]
                    )
                )

    # Live vs Walk-Forward comparison (when live/paper results are present).
    live_trading = wf_report.get("live_trading")
    if isinstance(live_trading, dict) and live_trading.get("schemes"):
        lines.append("")
        lines.append("Live vs Walk-Forward")
        lines.append("====================")
        header = (
            "  "
            + "  ".join(
                f"{c:>16}"
                for c in [
                    "scheme",
                    "oos_mean_return",
                    "live_mean_return",
                    "oos_max_drawdown",
                    "live_max_drawdown",
                ]
            )
        )
        lines.append(header)
        for row in live_trading["schemes"]:
            lines.append(
                "  "
                + "  ".join(
                    [
                        f"{str(row.get('scheme', '')):>16}",
                        f"{_fmt_pct(row.get('oos_mean_return', 0.0)):>16}",
                        f"{_fmt_pct(row.get('live_mean_return', 0.0)):>16}",
                        f"{_fmt_pct(row.get('oos_max_drawdown', 0.0)):>16}",
                        f"{_fmt_pct(row.get('live_max_drawdown', 0.0)):>16}",
                    ]
                )
            )
        lines.append("")
        lines.append(
            "  Aggregate: OOS Mean Return="
            f"{_fmt_pct(live_trading.get('oos_mean_return', 0.0))}, "
            f"Live Mean Return={_fmt_pct(live_trading.get('live_mean_return', 0.0))}, "
            f"OOS Max Drawdown={_fmt_pct(live_trading.get('oos_max_drawdown', 0.0))}, "
            f"Live Max Drawdown={_fmt_pct(live_trading.get('live_max_drawdown', 0.0))}"
        )

    # Strategy Benchmarks (when benchmark registry is present).
    benchmarks = wf_report.get("benchmarks")
    if isinstance(benchmarks, dict) and benchmarks.get("benchmarks"):
        lines.append("")
        lines.append("Strategy Benchmarks")
        lines.append("===================")
        header = (
            "  "
            + "  ".join(
                f"{c:>20}"
                for c in [
                    "benchmark",
                    "wf_oos_mean_return",
                    "bench_mean_return",
                    "wf_oos_max_drawdown",
                    "bench_max_drawdown",
                ]
            )
        )
        lines.append(header)
        for row in benchmarks["benchmarks"]:
            lines.append(
                "  "
                + "  ".join(
                    [
                        f"{str(row.get('name', '')):>20}",
                        f"{_fmt_pct(row.get('wf_oos_mean_return', 0.0)):>20}",
                        f"{_fmt_pct(row.get('benchmark_mean_return', 0.0)):>20}",
                        f"{_fmt_pct(row.get('wf_oos_max_drawdown', 0.0)):>20}",
                        f"{_fmt_pct(row.get('benchmark_max_drawdown', 0.0)):>20}",
                    ]
                )
            )

    # Attribution (if available)
    brinson, factor = _get_attribution(wf_report)
    if brinson is not None or factor is not None:
        lines.append("")
        lines.append("Attribution")
        lines.append("===========")
        if isinstance(brinson, dict):
            lines.extend(brinson_text_lines(brinson))
        if isinstance(factor, dict):
            lines.extend(factor_text_lines(factor))
    return "\n".join(lines)


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

    # In-Sample vs Out-of-Sample comparison (when IS metrics are present).
    is_vs_oos = wf_report.get("is_vs_oos")
    if isinstance(is_vs_oos, dict):
        html.append("<h2>In-Sample vs Out-of-Sample</h2>")
        html.append("<table>")
        html.append("<tr><th>Metric</th><th>In-Sample</th><th>Out-of-Sample</th></tr>")
        html.append(
            f"<tr><td>Mean Return</td><td>{_fmt_pct(is_vs_oos.get('is_mean_return', 0.0))}</td>"
            f"<td>{_fmt_pct(is_vs_oos.get('oos_mean_return', 0.0))}</td></tr>"
        )
        html.append(
            f"<tr><td>Mean Sharpe</td><td>{_fmt_num(is_vs_oos.get('is_mean_sharpe', 0.0))}</td>"
            f"<td>{_fmt_num(is_vs_oos.get('oos_mean_sharpe', 0.0))}</td></tr>"
        )
        html.append(
            f"<tr><td>Mean Max Drawdown</td>"
            f"<td>{_fmt_pct(is_vs_oos.get('is_mean_max_drawdown', 0.0))}</td>"
            f"<td>{_fmt_pct(is_vs_oos.get('oos_mean_max_drawdown', 0.0))}</td></tr>"
        )
        html.append(
            f"<tr><td>OOS/IS Ratio</td>"
            f"<td colspan=2>{_fmt_num(is_vs_oos.get('oos_is_ratio', 0.0))}</td></tr>"
        )
        html.append("</table>")

    # Confidence intervals (bootstrap) when present.
    confidence_intervals = wf_report.get("confidence_intervals")
    if isinstance(confidence_intervals, dict) and confidence_intervals:
        html.append("<h2>Confidence Intervals (bootstrap)</h2>")
        html.append("<table>")
        html.append("<tr><th>Metric</th><th>Lower</th><th>Upper</th></tr>")
        for key in ("mean_return", "oos_mean_return", "oos_is_ratio"):
            ci = confidence_intervals.get(key)
            if isinstance(ci, (list, tuple)) and len(ci) == 2:
                low, high = float(ci[0]), float(ci[1])
                label = key.replace("_", " ").title()
                fmt = _fmt_pct if "return" in key else _fmt_num
                html.append(
                    f"<tr><td>{label}</td><td>{fmt(low)}</td><td>{fmt(high)}</td></tr>"
                )
        html.append("</table>")

    # Cost-model sensitivity sweep when present.
    cost_sensitivity = wf_report.get("cost_sensitivity")
    if isinstance(cost_sensitivity, list) and cost_sensitivity:
        html.append("<h2>Cost-Model Sensitivity</h2>")
        html.append("<table>")
        html.append(
            "<tr><th>Fee Rate</th><th>Slippage</th><th>Mean Return</th>"
            "<th>OOS Mean Return</th><th>OOS/IS Ratio</th><th>Max Drawdown</th></tr>"
        )
        for row in cost_sensitivity:
            html.append(
                "<tr>"
                f"<td>{_fmt_pct(row.get('fee_rate', 0.0))}</td>"
                f"<td>{_fmt_pct(row.get('slippage', 0.0))}</td>"
                f"<td>{_fmt_pct(row.get('mean_return', 0.0))}</td>"
                f"<td>{_fmt_pct(row.get('oos_mean_return', 0.0))}</td>"
                f"<td>{_fmt_num(row.get('oos_is_ratio', 0.0))}</td>"
                f"<td>{_fmt_pct(row.get('max_drawdown', 0.0))}</td>"
                "</tr>"
            )
        html.append("</table>")
        try:
            valid = [r for r in cost_sensitivity if isinstance(r, dict)]
            if valid:
                best = max(valid, key=lambda r: _safe_float(r.get("oos_mean_return", 0.0)))
                worst = min(valid, key=lambda r: _safe_float(r.get("oos_mean_return", 0.0)))
                html.append("<p><em>")
                html.append(
                    f"Best OOS return: fee={_fmt_pct(best.get('fee_rate', 0.0))}, "
                    f"slippage={_fmt_pct(best.get('slippage', 0.0))} "
                    f"-> OOS={_fmt_pct(best.get('oos_mean_return', 0.0))}. "
                )
                html.append(
                    f"Worst OOS return: fee={_fmt_pct(worst.get('fee_rate', 0.0))}, "
                    f"slippage={_fmt_pct(worst.get('slippage', 0.0))} "
                    f"-> OOS={_fmt_pct(worst.get('oos_mean_return', 0.0))}."
                )
                html.append("</em></p>")
        except Exception:
            pass

    # Multi-Horizon Walk-Forward
    multi_horizon = wf_report.get("multi_horizon")
    if multi_horizon is not None:
        html.append("<h2>Multi-Horizon Walk-Forward</h2>")
        if isinstance(multi_horizon, dict):
            html.append("<table>")
            html.append("<tr><th>Parameter</th><th>Value</th></tr>")
            import html as _html_mod

            for key, val in multi_horizon.items():
                html.append(
                    f"<tr><td>{_html_mod.escape(str(key))}</td><td>{_html_mod.escape(str(val))}</td></tr>"
                )
            html.append("</table>")
        elif isinstance(multi_horizon, list):
            html.append("<table>")
            html.append(
                "<tr><th>Mode</th><th>Mean Return</th>"
                "<th>OOS Mean Return</th><th>OOS/IS Ratio</th>"
                "<th>Max Drawdown</th></tr>"
            )
            import html as _html_mod

            for row in multi_horizon:
                if not isinstance(row, dict):
                    continue
                html.append(
                    "<tr>"
                    f"<td>{_html_mod.escape(str(row.get('mode', '')))}</td>"
                    f"<td>{_fmt_pct(row.get('mean_return', 0.0))}</td>"
                    f"<td>{_fmt_pct(row.get('oos_mean_return', 0.0))}</td>"
                    f"<td>{_fmt_num(row.get('oos_is_ratio', 0.0))}</td>"
                    f"<td>{_fmt_pct(row.get('max_drawdown', 0.0))}</td>"
                    "</tr>"
                )
            html.append("</table>")

    # Strategy Benchmarks when present.
    benchmarks = wf_report.get("benchmarks")
    if isinstance(benchmarks, dict) and benchmarks.get("benchmarks"):
        html.append("<h2>Strategy Benchmarks</h2>")
        html.append(
            "<table>"
            "<tr><th>Benchmark</th><th>WF OOS Mean Return</th>"
            "<th>Bench Mean Return</th><th>WF OOS Max Drawdown</th>"
            "<th>Bench Max Drawdown</th></tr>"
        )
        import html as _html_mod

        for row in benchmarks["benchmarks"]:
            html.append(
                "<tr>"
                f"<td>{_html_mod.escape(str(row.get('name', '')))}</td>"
                f"<td>{_fmt_pct(row.get('wf_oos_mean_return', 0.0))}</td>"
                f"<td>{_fmt_pct(row.get('benchmark_mean_return', 0.0))}</td>"
                f"<td>{_fmt_pct(row.get('wf_oos_max_drawdown', 0.0))}</td>"
                f"<td>{_fmt_pct(row.get('benchmark_max_drawdown', 0.0))}</td>"
                "</tr>"
            )
        html.append("</table>")
        html.append("<p><em>")
        html.append(
            "Aggregate: WF OOS Mean Return="
            f"{_fmt_pct(benchmarks.get('wf_oos_mean_return', 0.0))}, "
            f"WF OOS Max Drawdown={_fmt_pct(benchmarks.get('wf_oos_max_drawdown', 0.0))}. "
        )
        html.append(
            f"Benchmark count={int(benchmarks.get('benchmark_count', 0))}."
        )
        html.append("</em></p>")

    # Live vs Walk-Forward comparison when present.
    live_trading = wf_report.get("live_trading")
    if isinstance(live_trading, dict) and live_trading.get("schemes"):
        html.append("<h2>Live vs Walk-Forward</h2>")
        html.append("<table>")
        html.append(
            "<tr><th>Scheme</th><th>OOS Mean Return</th>"
            "<th>Live Mean Return</th><th>OOS Max Drawdown</th>"
            "<th>Live Max Drawdown</th></tr>"
        )
        import html as _html_mod

        for row in live_trading["schemes"]:
            html.append(
                "<tr>"
                f"<td>{_html_mod.escape(str(row.get('scheme', '')))}</td>"
                f"<td>{_fmt_pct(row.get('oos_mean_return', 0.0))}</td>"
                f"<td>{_fmt_pct(row.get('live_mean_return', 0.0))}</td>"
                f"<td>{_fmt_pct(row.get('oos_max_drawdown', 0.0))}</td>"
                f"<td>{_fmt_pct(row.get('live_max_drawdown', 0.0))}</td>"
                "</tr>"
            )
        html.append("</table>")
        html.append("<p><em>")
        html.append(
            "Aggregate: OOS Mean Return="
            f"{_fmt_pct(live_trading.get('oos_mean_return', 0.0))}, "
            f"Live Mean Return={_fmt_pct(live_trading.get('live_mean_return', 0.0))}. "
        )
        html.append(
            f"OOS Max Drawdown={_fmt_pct(live_trading.get('oos_max_drawdown', 0.0))}, "
            f"Live Max Drawdown={_fmt_pct(live_trading.get('live_max_drawdown', 0.0))}."
        )
        html.append("</em></p>")

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
        lines = [title]
        if isinstance(wf_report, dict):
            summary = wf_report.get("summary")
            if summary is not None:
                try:
                    lines.extend(str(c) for c in summary.columns)
                except Exception:
                    pass
        try:
            return _write_minimal_pdf(output_path, title, lines)
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

            # Page 3: In-Sample vs Out-of-Sample comparison (when present).
            is_vs_oos = wf_report.get("is_vs_oos")
            if isinstance(is_vs_oos, dict):
                try:
                    fig, ax = plt.subplots(figsize=(11, 4.5))
                    ax.axis("off")
                    ax.set_title("In-Sample vs Out-of-Sample", fontsize=12, pad=20)
                    rows_is = [
                        ["Metric", "In-Sample", "Out-of-Sample"],
                        ["Mean Return",
                         _fmt_pct(is_vs_oos.get("is_mean_return", 0.0)),
                         _fmt_pct(is_vs_oos.get("oos_mean_return", 0.0))],
                        ["Mean Sharpe",
                         _fmt_num(is_vs_oos.get("is_mean_sharpe", 0.0)),
                         _fmt_num(is_vs_oos.get("oos_mean_sharpe", 0.0))],
                        ["Mean Max Drawdown",
                         _fmt_pct(is_vs_oos.get("is_mean_max_drawdown", 0.0)),
                         _fmt_pct(is_vs_oos.get("oos_mean_max_drawdown", 0.0))],
                        ["OOS/IS Ratio", _fmt_num(is_vs_oos.get("oos_is_ratio", 0.0)), ""],
                    ]
                    table = ax.table(
                        cellText=rows_is[1:],
                        colLabels=rows_is[0],
                        loc="center",
                        cellLoc="center",
                        bbox=cast(Any, (0.05, 0.35, 0.9, 0.45)),
                    )
                    table.auto_set_font_size(False)
                    table.set_fontsize(9)
                    table.scale(1.0, 1.2)
                    pdf.savefig(fig, bbox_inches="tight", pad_inches=0.5)
                    plt.close(fig)
                except Exception:
                    pass

            # Page 4: Confidence intervals (bootstrap) when present.
            confidence_intervals = wf_report.get("confidence_intervals")
            if isinstance(confidence_intervals, dict) and confidence_intervals:
                try:
                    fig, ax = plt.subplots(figsize=(11, 4.5))
                    ax.axis("off")
                    ax.set_title("Confidence Intervals (bootstrap)", fontsize=12, pad=20)
                    rows_ci = [["Metric", "Lower", "Upper"]]
                    for key in ("mean_return", "oos_mean_return", "oos_is_ratio"):
                        ci = confidence_intervals.get(key)
                        if isinstance(ci, (list, tuple)) and len(ci) == 2:
                            low, high = float(ci[0]), float(ci[1])
                            label = key.replace("_", " ").title()
                            fmt = _fmt_pct if "return" in key else _fmt_num
                            rows_ci.append([label, fmt(low), fmt(high)])
                    if len(rows_ci) > 1:
                        table = ax.table(
                            cellText=rows_ci[1:],
                            colLabels=rows_ci[0],
                            loc="center",
                            cellLoc="center",
                            bbox=cast(Any, (0.05, 0.35, 0.9, 0.45)),
                        )
                        table.auto_set_font_size(False)
                        table.set_fontsize(9)
                        table.scale(1.0, 1.2)
                        pdf.savefig(fig, bbox_inches="tight", pad_inches=0.5)
                    plt.close(fig)
                except Exception:
                    pass

            # Page 5: Cost-model sensitivity sweep when present.
            cost_sensitivity = wf_report.get("cost_sensitivity")
            if isinstance(cost_sensitivity, list) and cost_sensitivity:
                try:
                    fig, ax = plt.subplots(figsize=(11, 4.5))
                    ax.axis("off")
                    ax.set_title("Cost-Model Sensitivity", fontsize=12, pad=20)
                    rows_cs = [
                        [
                            "Fee Rate",
                            "Slippage",
                            "Mean Return",
                            "OOS Mean Return",
                            "OOS/IS Ratio",
                            "Max Drawdown",
                        ]
                    ]
                    for row in cost_sensitivity:
                        rows_cs.append([
                            _fmt_pct(row.get("fee_rate", 0.0)),
                            _fmt_pct(row.get("slippage", 0.0)),
                            _fmt_pct(row.get("mean_return", 0.0)),
                            _fmt_pct(row.get("oos_mean_return", 0.0)),
                            _fmt_num(row.get("oos_is_ratio", 0.0)),
                            _fmt_pct(row.get("max_drawdown", 0.0)),
                        ])
                    if len(rows_cs) > 1:
                        table = ax.table(
                            cellText=rows_cs[1:],
                            colLabels=rows_cs[0],
                            loc="center",
                            cellLoc="center",
                            bbox=cast(Any, (0.02, 0.35, 0.96, 0.45)),
                        )
                        table.auto_set_font_size(False)
                        table.set_fontsize(8)
                        table.scale(1.0, 1.2)
                        pdf.savefig(fig, bbox_inches="tight", pad_inches=0.5)
                    plt.close(fig)
                except Exception:
                    pass

            # Page 6: Multi-Horizon Walk-Forward when present.
            multi_horizon = wf_report.get("multi_horizon")
            if multi_horizon is not None:
                try:
                    fig, ax = plt.subplots(figsize=(11, 4.5))
                    ax.axis("off")
                    ax.set_title("Multi-Horizon Walk-Forward", fontsize=12, pad=20)
                    if isinstance(multi_horizon, dict):
                        rows_mh = [["Parameter", "Value"]]
                        for key, val in multi_horizon.items():
                            rows_mh.append([str(key), str(val)])
                        table = ax.table(
                            cellText=rows_mh[1:],
                            colLabels=rows_mh[0],
                            loc="center",
                            cellLoc="center",
                            bbox=cast(Any, (0.1, 0.25, 0.8, 0.5)),
                        )
                    elif isinstance(multi_horizon, list):
                        rows_mh = [
                            [
                                "Mode",
                                "Mean Return",
                                "OOS Mean Return",
                                "OOS/IS Ratio",
                                "Max Drawdown",
                            ]
                        ]
                        for row in multi_horizon:
                            if not isinstance(row, dict):
                                continue
                            rows_mh.append([
                                str(row.get("mode", "")),
                                _fmt_pct(row.get("mean_return", 0.0)),
                                _fmt_pct(row.get("oos_mean_return", 0.0)),
                                _fmt_num(row.get("oos_is_ratio", 0.0)),
                                _fmt_pct(row.get("max_drawdown", 0.0)),
                            ])
                        table = ax.table(
                            cellText=rows_mh[1:],
                            colLabels=rows_mh[0],
                            loc="center",
                            cellLoc="center",
                            bbox=cast(Any, (0.05, 0.35, 0.9, 0.45)),
                        )
                    else:
                        table = cast(Any, None)
                    if "table" in locals() and table is not None:
                        table.auto_set_font_size(False)
                        table.set_fontsize(9)
                        table.scale(1.0, 1.2)
                        pdf.savefig(fig, bbox_inches="tight", pad_inches=0.5)
                    plt.close(fig)
                except Exception:
                    pass

            # Page: Strategy Benchmarks when present.
            benchmarks = wf_report.get("benchmarks")
            if isinstance(benchmarks, dict) and benchmarks.get("benchmarks"):
                try:
                    fig, ax = plt.subplots(figsize=(11, 4.5))
                    ax.axis("off")
                    ax.set_title("Strategy Benchmarks", fontsize=12, pad=20)
                    rows_bm = [
                        [
                            "Benchmark",
                            "WF OOS Mean Return",
                            "Bench Mean Return",
                            "WF OOS Max Drawdown",
                            "Bench Max Drawdown",
                        ]
                    ]
                    for row in benchmarks["benchmarks"]:
                        rows_bm.append([
                            str(row.get("name", "")),
                            _fmt_pct(row.get("wf_oos_mean_return", 0.0)),
                            _fmt_pct(row.get("benchmark_mean_return", 0.0)),
                            _fmt_pct(row.get("wf_oos_max_drawdown", 0.0)),
                            _fmt_pct(row.get("benchmark_max_drawdown", 0.0)),
                        ])
                    table = ax.table(
                        cellText=rows_bm[1:],
                        colLabels=rows_bm[0],
                        loc="center",
                        cellLoc="center",
                        bbox=cast(Any, (0.05, 0.35, 0.9, 0.45)),
                    )
                    table.auto_set_font_size(False)
                    table.set_fontsize(9)
                    table.scale(1.0, 1.2)
                    pdf.savefig(fig, bbox_inches="tight", pad_inches=0.5)
                    plt.close(fig)
                except Exception:
                    pass

            # Page: Live vs Walk-Forward when present.
            live_trading = wf_report.get("live_trading")
            if isinstance(live_trading, dict) and live_trading.get("schemes"):
                try:
                    fig, ax = plt.subplots(figsize=(11, 4.5))
                    ax.axis("off")
                    ax.set_title("Live vs Walk-Forward", fontsize=12, pad=20)
                    rows_lt = [
                        [
                            "Scheme",
                            "OOS Mean Return",
                            "Live Mean Return",
                            "OOS Max Drawdown",
                            "Live Max Drawdown",
                        ]
                    ]
                    for row in live_trading["schemes"]:
                        rows_lt.append([
                            str(row.get("scheme", "")),
                            _fmt_pct(row.get("oos_mean_return", 0.0)),
                            _fmt_pct(row.get("live_mean_return", 0.0)),
                            _fmt_pct(row.get("oos_max_drawdown", 0.0)),
                            _fmt_pct(row.get("live_max_drawdown", 0.0)),
                        ])
                    table = ax.table(
                        cellText=rows_lt[1:],
                        colLabels=rows_lt[0],
                        loc="center",
                        cellLoc="center",
                        bbox=cast(Any, (0.05, 0.35, 0.9, 0.45)),
                    )
                    table.auto_set_font_size(False)
                    table.set_fontsize(9)
                    table.scale(1.0, 1.2)
                    pdf.savefig(fig, bbox_inches="tight", pad_inches=0.5)
                    plt.close(fig)
                except Exception:
                    pass

            # Attribution (if available)
            brinson, factor = _get_attribution(wf_report or {})
            if brinson is not None or factor is not None:
                try:
                    fig, ax = plt.subplots(figsize=(11, 4.5))
                    ax.axis("off")
                    ax.set_title("Attribution", fontsize=12, pad=20)
                    y = 0.85
                    if isinstance(brinson, dict):
                        ax.text(
                            0.05,
                            y,
                            "Brinson Attribution (aggregated)",
                            fontsize=10,
                            transform=ax.transAxes,
                        )
                        y -= 0.08
                        rows_b = [
                            ["Allocation", _fmt_pct(_series_sum(brinson.get("allocation_total")))],
                            ["Selection", _fmt_pct(
                                _series_sum(brinson.get("selection_total"))
                            )],
                            ["Interaction", _fmt_pct(
                                _series_sum(brinson.get("interaction_total"))
                            )],
                        ]
                        try:
                            table = ax.table(
                                cellText=rows_b,
                                colLabels=["Effect", "Total"],
                                loc="center",
                                cellLoc="center",
                                bbox=cast(Any, (0.05, y - 0.25, 0.9, 0.2)),
                            )
                            table.auto_set_font_size(False)
                            table.set_fontsize(8)
                            table.scale(1.0, 1.2)
                            y -= 0.35
                        except Exception:
                            pass
                    if isinstance(factor, dict):
                        ax.text(
                            0.05,
                            y,
                            "Factor Attribution (aggregated)",
                            fontsize=10,
                            transform=ax.transAxes,
                        )
                        y -= 0.08
                        rows_f = [
                            ["Alpha (period)", _fmt_num(_safe_float(factor.get("alpha")))],
                            ["Alpha (annualized)", _fmt_num(
                                _safe_float(factor.get("alpha_annualized"))
                            )],
                            ["R-squared", _fmt_num(_safe_float(factor.get("r_squared")))],
                        ]
                        try:
                            table = ax.table(
                                cellText=rows_f,
                                colLabels=["Metric", "Value"],
                                loc="center",
                                cellLoc="center",
                                bbox=cast(Any, (0.05, y - 0.25, 0.9, 0.2)),
                            )
                            table.auto_set_font_size(False)
                            table.set_fontsize(8)
                            table.scale(1.0, 1.2)
                        except Exception:
                            pass
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


def compare_walk_forward_reports(reports: list[dict]) -> dict:
    """Compare multiple walk-forward reports and return a comparison structure."""
    reports = reports or []
    comparison: dict[str, Any] = {
        "reports": [],
        "benchmarks": [],
    }
    for idx, rep in enumerate(reports):
        rep = rep or {}
        summary = rep.get("summary")
        total_windows = 0
        if isinstance(summary, pd.DataFrame):
            total_windows = len(summary)
        elif summary is not None:
            try:
                total_windows = len(summary)
            except Exception:
                total_windows = 0

        oos_mean_return = rep.get("oos_mean_return")
        mean_return = rep.get("mean_return")
        if oos_mean_return is None and mean_return is not None:
            oos_mean_return = mean_return

        max_drawdown = None
        try:
            if (
                isinstance(summary, pd.DataFrame)
                and len(summary) > 0
                and "max_drawdown" in summary.columns
            ):
                max_drawdown = float(summary["max_drawdown"].mean())
            elif isinstance(summary, list) and summary:
                dds = [
                    _safe_float(r.get("max_drawdown", 0.0))
                    for r in summary
                    if isinstance(r, dict)
                ]
                if dds:
                    max_drawdown = float(sum(dds) / len(dds))
        except Exception:
            pass

        sharpe_ratio = None
        try:
            if (
                isinstance(summary, pd.DataFrame)
                and len(summary) > 0
                and "sharpe_ratio" in summary.columns
            ):
                sharpe_ratio = float(summary["sharpe_ratio"].mean())
            elif isinstance(summary, list) and summary:
                srs = [
                    _safe_float(r.get("sharpe_ratio", 0.0))
                    for r in summary
                    if isinstance(r, dict)
                ]
                if srs:
                    sharpe_ratio = float(sum(srs) / len(srs))
        except Exception:
            pass

        is_vs_oos = rep.get("is_vs_oos") or {}
        oos_is_ratio = is_vs_oos.get("oos_is_ratio") if isinstance(is_vs_oos, dict) else None

        entry = {
            "index": idx,
            "name": rep.get("name") or f"Report {idx + 1}",
            "total_windows": total_windows,
            "mean_return": mean_return,
            "oos_mean_return": oos_mean_return,
            "max_drawdown": max_drawdown,
            "sharpe_ratio": sharpe_ratio,
            "oos_is_ratio": oos_is_ratio,
        }
        comparison["reports"].append(entry)

        benchmarks = rep.get("benchmarks") or {}
        if isinstance(benchmarks, dict):
            bm_list = benchmarks.get("benchmarks") or []
            if isinstance(bm_list, list):
                for b in bm_list:
                    if not isinstance(b, dict):
                        continue
                    comparison["benchmarks"].append(
                        {
                            "report_index": idx,
                            "report_name": entry["name"],
                            "benchmark_name": b.get("name", ""),
                            "wf_oos_mean_return": b.get("wf_oos_mean_return"),
                            "benchmark_mean_return": b.get("benchmark_mean_return"),
                            "wf_oos_max_drawdown": b.get("wf_oos_max_drawdown"),
                            "benchmark_max_drawdown": b.get("benchmark_max_drawdown"),
                            "delta_mean_return": (
                                _safe_float(b.get("wf_oos_mean_return"))
                                - _safe_float(b.get("benchmark_mean_return"))
                            ),
                            "delta_max_drawdown": (
                                _safe_float(b.get("wf_oos_max_drawdown"))
                                - _safe_float(b.get("benchmark_max_drawdown"))
                            ),
                        }
                    )

    return comparison


def generate_walk_forward_comparison_html(
    comparison: dict, title: str = "Walk-Forward Comparison Dashboard"
) -> str:
    """Generate HTML for walk-forward comparison dashboard."""
    comparison = comparison or {}
    reports = comparison.get("reports") or []
    benchmarks = comparison.get("benchmarks") or []

    def _html_escape(s: str) -> str:
        try:
            import html as _html_mod

            return _html_mod.escape(s)
        except Exception:
            return s

    html = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8" />',
        f"<title>{title}</title>",
        "<style>",
        "body{font-family:Arial,Helvetica,sans-serif;margin:40px;background:#fff;color:#222}",
        "h1{font-size:22px;margin-bottom:10px}",
        "table{border-collapse:collapse;width:100%;max-width:1000px;margin-bottom:20px}",
        "th,td{border:1px solid #ddd;padding:6px 8px;font-size:12px;text-align:right}",
        "th{background:#f5f5f5;text-align:right}",
        "td:first-child,th:first-child{text-align:left}",
        "</style>",
        "</head>",
        "<body>",
        f"<h1>{title}</h1>",
    ]

    if reports:
        html.append("<h2>Reports Comparison</h2>")
        html.append("<table>")
        html.append(
            "<tr><th>Report</th><th>Windows</th><th>OOS Mean Return</th>"
            "<th>Mean Return</th><th>Sharpe Ratio</th>"
            "<th>Max Drawdown</th><th>OOS/IS Ratio</th></tr>"
        )
        for r in reports:
            html.append(
                "<tr>"
                f"<td>{_html_escape(str(r.get('name', '')))}</td>"
                f"<td>{r.get('total_windows', 0)}</td>"
                f"<td>{_fmt_pct(r.get('oos_mean_return', 0.0))}</td>"
                f"<td>{_fmt_pct(r.get('mean_return', 0.0))}</td>"
                f"<td>{_fmt_num(r.get('sharpe_ratio', 0.0))}</td>"
                f"<td>{_fmt_pct(r.get('max_drawdown', 0.0))}</td>"
                f"<td>{_fmt_num(r.get('oos_is_ratio', 0.0))}</td>"
                "</tr>"
            )
        html.append("</table>")
    else:
        html.append("<p>No reports provided.</p>")

    if benchmarks:
        html.append("<h2>Benchmark vs Walk-Forward Deltas</h2>")
        html.append("<table>")
        html.append(
            "<tr><th>Report</th><th>Benchmark</th><th>WF OOS Mean Return</th>"
            "<th>Bench Mean Return</th><th>Delta Mean Return</th><th>WF OOS Max DD</th>"
            "<th>Bench Max DD</th><th>Delta Max DD</th></tr>"
        )
        for b in benchmarks:
            html.append(
                "<tr>"
                f"<td>{_html_escape(str(b.get('report_name', '')))}</td>"
                f"<td>{_html_escape(str(b.get('benchmark_name', '')))}</td>"
                f"<td>{_fmt_pct(b.get('wf_oos_mean_return', 0.0))}</td>"
                f"<td>{_fmt_pct(b.get('benchmark_mean_return', 0.0))}</td>"
                f"<td>{_fmt_pct(b.get('delta_mean_return', 0.0))}</td>"
                f"<td>{_fmt_pct(b.get('wf_oos_max_drawdown', 0.0))}</td>"
                f"<td>{_fmt_pct(b.get('benchmark_max_drawdown', 0.0))}</td>"
                f"<td>{_fmt_pct(b.get('delta_max_drawdown', 0.0))}</td>"
                "</tr>"
            )
        html.append("</table>")

    html.extend(["</body>", "</html>"])
    return "\n".join(html)


def aggregate_benchmark_registry(benchmarks: Any) -> dict[str, Any]:
    benchmarks_in: list[dict[str, Any]] = []
    if isinstance(benchmarks, dict):
        candidate = benchmarks.get("benchmarks")
        if isinstance(candidate, list):
            benchmarks_in = [b for b in candidate if isinstance(b, dict)]
        elif "name" in benchmarks:
            benchmarks_in = [benchmarks]
    elif isinstance(benchmarks, list):
        benchmarks_in = [b for b in benchmarks if isinstance(b, dict)]

    items: list[dict[str, Any]] = []
    returns: list[float] = []
    drawdowns: list[float] = []
    for b in benchmarks_in:
        mr = _safe_float(b.get("mean_return", 0.0))
        md = _safe_float(b.get("max_drawdown", 0.0))
        tr = _safe_float(b.get("total_return", 0.0))
        sr = _safe_float(b.get("sharpe_ratio", 0.0))
        name = str(b.get("name") or b.get("benchmark") or "")
        items.append(
            {
                "name": name,
                "mean_return": mr,
                "max_drawdown": md,
                "total_return": tr,
                "sharpe_ratio": sr,
            }
        )
        returns.append(mr)
        drawdowns.append(md)

    count = len(items)
    mean_return = (sum(returns) / count) if count else 0.0
    mean_drawdown = (sum(drawdowns) / count) if count else 0.0
    return {
        "benchmarks": items,
        "count": count,
        "mean_return": mean_return,
        "mean_drawdown": mean_drawdown,
    }


def generate_benchmark_dashboard_html(benchmarks: Any) -> str:
    agg = aggregate_benchmark_registry(benchmarks)
    items = agg["benchmarks"]

    def _html_escape(s: str) -> str:
        try:
            import html as _html_mod

            return _html_mod.escape(s)
        except Exception:
            return s

    html = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8" />',
        "<title>Benchmark Registry Dashboard</title>",
        "<style>",
        "body{font-family:Arial,Helvetica,sans-serif;margin:40px;background:#fff;color:#222}",
        "table{border-collapse:collapse;width:100%;max-width:1000px;margin-bottom:20px}",
        "th,td{border:1px solid #ddd;padding:6px 8px;font-size:12px;text-align:right}",
        "th{background:#f5f5f5;text-align:right}",
        "td:first-child,th:first-child{text-align:left}",
        "</style>",
        "</head>",
        "<body>",
        "<h1>Benchmark Registry Dashboard</h1>",
        f"<p>Count: {agg['count']} | Mean Return: {_fmt_pct(agg['mean_return'])} | "
        f"Mean Drawdown: {_fmt_pct(agg['mean_drawdown'])}</p>",
        "<table>",
        "<tr><th>Benchmark</th><th>Mean Return</th><th>Max Drawdown</th>"
        "<th>Total Return</th><th>Sharpe Ratio</th></tr>",
    ]
    for b in items:
        html.append(
            "<tr>"
            f"<td>{_html_escape(str(b.get('name', '')))}</td>"
            f"<td>{_fmt_pct(b.get('mean_return', 0.0))}</td>"
            f"<td>{_fmt_pct(b.get('max_drawdown', 0.0))}</td>"
            f"<td>{_fmt_pct(b.get('total_return', 0.0))}</td>"
            f"<td>{_fmt_num(b.get('sharpe_ratio', 0.0))}</td>"
            "</tr>"
        )
    html.append("</table>")
    html.extend(["</body>", "</html>"])
    return "\n".join(html)
