"""Paper trading session reporting and artifact persistence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _to_float(val: Any) -> float:
    try:
        if val is None:
            return 0.0
        import numpy as _np

        if isinstance(val, float) and (_np.isnan(val) or _np.isinf(val)):
            return 0.0
        return float(val)
    except Exception:
        return 0.0


def build_paper_trading_report(
    session_summary: dict[str, Any] | None = None,
    fills: list[dict[str, Any]] | None = None,
    equity_curve: list[dict[str, Any]] | None = None,
    positions: dict[str, Any] | None = None,
    monitoring: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a serializable paper-trading session report."""
    session_summary = dict(session_summary or {})
    fills_list = list(fills or session_summary.get("fills") or [])
    equity_list = list(equity_curve or session_summary.get("equity_curve") or [])
    positions_dict = dict(positions or session_summary.get("positions") or {})
    monitoring_dict = dict(monitoring or session_summary.get("monitoring") or {})

    # Ensure fills are serializable
    serializable_fills = []
    for f in fills_list:
        try:
            serializable_fills.append({k: v for k, v in dict(f).items()})
        except Exception:
            continue

    # Build session summary
    summary = {}
    summary["initial_capital"] = _to_float(
        session_summary.get("initial_capital", metadata.get("initial_capital") if metadata else 0.0)
    )
    summary["realized_pnl"] = _to_float(session_summary.get("realized_pnl", 0.0))
    summary["num_fills"] = int(session_summary.get("num_fills", len(serializable_fills)))
    summary["portfolio_value"] = _to_float(
        session_summary.get("portfolio_value", summary["initial_capital"] + summary["realized_pnl"])
    )
    if metadata:
        summary["metadata"] = dict(metadata)
    if "risk_metrics" in session_summary:
        summary["risk_metrics"] = dict(session_summary["risk_metrics"])

    report: dict[str, Any] = {
        "session_summary": summary,
        "fills": serializable_fills,
        "equity_curve": equity_list,
        "positions": positions_dict,
        "monitoring": monitoring_dict,
    }
    return report


def paper_report_to_dict(report: dict[str, Any] | None) -> dict[str, Any]:
    """Return a serializable dict copy of the paper-trading report."""
    if not isinstance(report, dict):
        return {}
    out: dict[str, Any] = {}
    for k, v in report.items():
        out[k] = v
    return out


def generate_paper_trading_report_text(report: dict[str, Any] | None) -> str:
    """Generate human-readable text report for a paper-trading session."""
    report = report or {}
    session_summary = report.get("session_summary") or {}
    fills = report.get("fills") or []
    positions = report.get("positions") or {}
    monitoring = report.get("monitoring") or {}

    lines: list[str] = [
        "Paper Trading Report",
        "====================",
    ]
    lines.append(f"Initial Capital:     {session_summary.get('initial_capital', 0.0)}")
    lines.append(f"Realized PnL:        {session_summary.get('realized_pnl', 0.0)}")
    lines.append(f"Portfolio Value:     {session_summary.get('portfolio_value', 0.0)}")
    lines.append(f"Number of Fills:     {len(fills) if isinstance(fills, list) else session_summary.get('num_fills', 0)}")
    lines.append("")

    if positions:
        lines.append("Positions")
        lines.append("---------")
        for sym, pos in positions.items():
            try:
                if isinstance(pos, dict):
                    qty = pos.get("quantity", 0.0)
                    avg = pos.get("avg_cost", 0.0)
                    upnl = pos.get("unrealized_pnl", 0.0)
                else:
                    qty = getattr(pos, "quantity", 0.0)
                    avg = getattr(pos, "avg_cost", 0.0)
                    upnl = getattr(pos, "unrealized_pnl", 0.0)
                lines.append(f"{sym}: qty={qty} avg_cost={avg} unrealized_pnl={upnl}")
            except Exception:
                lines.append(f"{sym}: {pos}")
        lines.append("")

    if monitoring:
        lines.append("Monitoring")
        lines.append("----------")
        alerts = monitoring.get("alerts") or []
        lines.append(f"Total Alerts: {len(alerts) if isinstance(alerts, list) else monitoring.get('total_alerts', 0)}")
        for a in alerts[:10] if isinstance(alerts, list) else []:
            try:
                if isinstance(a, dict):
                    lines.append(f"- [{a.get('level')}] {a.get('metric')}: {a.get('message')}")
                else:
                    lines.append(f"- {a}")
            except Exception:
                pass
        lines.append("")

    if fills:
        lines.append("Fills (first 10)")
        lines.append("----------------")
        for f in (fills if isinstance(fills, list) else [])[:10]:
            try:
                if isinstance(f, dict):
                    lines.append(
                        f"{f.get('timestamp','')} {f.get('symbol','')} {f.get('side','')} "
                        f"qty={f.get('quantity','')} price={f.get('price','')} fee={f.get('fee','')}"
                    )
                else:
                    lines.append(str(f))
            except Exception:
                pass
        lines.append("")

    return "\n".join(lines)


def generate_paper_trading_report_html(report: dict[str, Any] | None, title: str = "Paper Trading Report") -> str:
    """Generate HTML report for a paper-trading session."""
    report = report or {}
    session_summary = report.get("session_summary") or {}
    fills = report.get("fills") or []
    positions = report.get("positions") or {}
    monitoring = report.get("monitoring") or {}

    html: list[str] = []
    html.append("<html><head><meta charset='utf-8'>")
    html.append(f"<title>{title}</title>")
    html.append(
        "<style>body{font-family:Arial, sans-serif;margin:40px;} "
        "table{border-collapse:collapse;width:100%;margin-bottom:20px;} "
        "th,td{border:1px solid #ddd;padding:8px;text-align:left;} "
        "th{background-color:#f2f2f2;} "
        "h1,h2{color:#333;}</style>"
    )
    html.append("</head><body>")
    html.append(f"<h1>{title}</h1>")
    html.append("<h2>Session Summary</h2>")
    html.append("<table><tr><th>Metric</th><th>Value</th></tr>")
    html.append(f"<tr><td>Initial Capital</td><td>{session_summary.get('initial_capital', 0.0)}</td></tr>")
    html.append(f"<tr><td>Realized PnL</td><td>{session_summary.get('realized_pnl', 0.0)}</td></tr>")
    html.append(f"<tr><td>Portfolio Value</td><td>{session_summary.get('portfolio_value', 0.0)}</td></tr>")
    html.append(f"<tr><td>Number of Fills</td><td>{len(fills) if isinstance(fills, list) else session_summary.get('num_fills', 0)}</td></tr>")
    html.append("</table>")

    if positions:
        html.append("<h2>Positions</h2>")
        html.append("<table><tr><th>Symbol</th><th>Quantity</th><th>Avg Cost</th><th>Unrealized PnL</th></tr>")
        for sym, pos in positions.items():
            try:
                if isinstance(pos, dict):
                    qty = pos.get("quantity", 0.0)
                    avg = pos.get("avg_cost", 0.0)
                    upnl = pos.get("unrealized_pnl", 0.0)
                else:
                    qty = getattr(pos, "quantity", 0.0)
                    avg = getattr(pos, "avg_cost", 0.0)
                    upnl = getattr(pos, "unrealized_pnl", 0.0)
                html.append(f"<tr><td>{sym}</td><td>{qty}</td><td>{avg}</td><td>{upnl}</td></tr>")
            except Exception:
                html.append(f"<tr><td>{sym}</td><td colspan='3'>{pos}</td></tr>")
        html.append("</table>")

    if monitoring:
        html.append("<h2>Monitoring</h2>")
        alerts = monitoring.get("alerts") or []
        html.append(f"<p>Total Alerts: {len(alerts) if isinstance(alerts, list) else monitoring.get('total_alerts', 0)}</p>")
        if isinstance(alerts, list) and alerts:
            html.append("<table><tr><th>Level</th><th>Metric</th><th>Message</th><th>Timestamp</th></tr>")
            for a in alerts:
                try:
                    if isinstance(a, dict):
                        html.append(
                            f"<tr><td>{a.get('level','')}</td><td>{a.get('metric','')}</td>"
                            f"<td>{a.get('message','')}</td><td>{a.get('timestamp','')}</td></tr>"
                        )
                    else:
                        html.append(f"<tr><td colspan='4'>{a}</td></tr>")
                except Exception:
                    pass
            html.append("</table>")

    if fills:
        html.append("<h2>Fills</h2>")
        html.append("<table><tr><th>Timestamp</th><th>Symbol</th><th>Side</th><th>Quantity</th><th>Price</th><th>Fee</th></tr>")
        for f in (fills if isinstance(fills, list) else []):
            try:
                if isinstance(f, dict):
                    html.append(
                        f"<tr><td>{f.get('timestamp','')}</td><td>{f.get('symbol','')}</td>"
                        f"<td>{f.get('side','')}</td><td>{f.get('quantity','')}</td>"
                        f"<td>{f.get('price','')}</td><td>{f.get('fee','')}</td></tr>"
                    )
                else:
                    html.append(f"<tr><td colspan='6'>{f}</td></tr>")
            except Exception:
                pass
        html.append("</table>")

    html.append("</body></html>")
    return "\n".join(html)


def save_paper_trading_artifacts(
    report: dict[str, Any],
    artifact_dir: str | Path,
    prefix: str = "paper_trading",
) -> dict[str, str]:
    """Save paper-trading artifacts (report, fills, equity curve, alerts) to artifact_dir."""
    artifact_dir = Path(artifact_dir)
    artifact_dir.mkdir(parents=True, exist_ok=True)

    saved: dict[str, str] = {}
    report_path = artifact_dir / f"{prefix}_report.json"
    report_data = paper_report_to_dict(report)
    report_path.write_text(json.dumps(report_data, indent=2, default=float))
    saved["report"] = str(report_path)

    fills_path = artifact_dir / f"{prefix}_fills.json"
    fills_path.write_text(json.dumps(report_data.get("fills", []), indent=2, default=float))
    saved["fills"] = str(fills_path)

    equity_path = artifact_dir / f"{prefix}_equity_curve.json"
    equity_path.write_text(json.dumps(report_data.get("equity_curve", []), indent=2, default=float))
    saved["equity_curve"] = str(equity_path)

    alerts_path = artifact_dir / f"{prefix}_alerts.json"
    alerts_path.write_text(json.dumps((report_data.get("monitoring") or {}).get("alerts", []), indent=2, default=float))
    saved["alerts"] = str(alerts_path)

    return saved


def load_paper_trading_artifacts(artifact_dir: str | Path, prefix: str = "paper_trading") -> dict[str, Any]:
    """Load paper-trading artifacts from artifact_dir."""
    artifact_dir = Path(artifact_dir)
    report_path = artifact_dir / f"{prefix}_report.json"
    if report_path.exists():
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    # Try to build from individual files for backward compat
    report: dict[str, Any] = {}
    fills_path = artifact_dir / f"{prefix}_fills.json"
    if fills_path.exists():
        try:
            with open(fills_path, "r", encoding="utf-8") as f:
                report["fills"] = json.load(f)
        except Exception:
            report["fills"] = []
    else:
        report["fills"] = []

    equity_path = artifact_dir / f"{prefix}_equity_curve.json"
    if equity_path.exists():
        try:
            with open(equity_path, "r", encoding="utf-8") as f:
                report["equity_curve"] = json.load(f)
        except Exception:
            report["equity_curve"] = []
    else:
        report["equity_curve"] = []

    alerts_path = artifact_dir / f"{prefix}_alerts.json"
    alerts = []
    if alerts_path.exists():
        try:
            with open(alerts_path, "r", encoding="utf-8") as f:
                alerts = json.load(f)
        except Exception:
            alerts = []
    report["monitoring"] = {"alerts": alerts}
    report["session_summary"] = report.get("session_summary") or {}
    report["positions"] = report.get("positions") or {}
    return report
