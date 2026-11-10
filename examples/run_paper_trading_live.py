#!/usr/bin/env python3
"""Campaign #5: Production bridge bounded paper-trading session.

Uses real/public Binance market data (cached when available) with provenance.
Submits orders through fail-closed OMS + PaperBroker. Paper fills are simulated
only (``simulated_fills: true``) and are NEVER presented as real exchange fills.

If real data routes are unavailable, the script records blocked_routes/limitations
honestly and still emits artifacts (fail-closed/blocked where required).
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

# Ensure repo root importable when run as script.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.cache import load_cached  # noqa: E402
from data.loader import DataLoader  # noqa: E402
from execution.oms import OMS, AccountState, OrderIntent  # noqa: E402
from execution.paper_broker import PaperBroker  # noqa: E402
from execution.risk import RiskConfig, RiskDashboard  # noqa: E402
from strategies.mean_reversion import MeanReversionStrategy  # noqa: E402
from utils.risk_dashboard import build_risk_dashboard_artifact  # noqa: E402


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _json_safe(obj: Any) -> Any:
    try:
        if pd.isna(obj):
            return None
    except Exception:
        pass
    if isinstance(obj, (pd.Timestamp, datetime)):
        return obj.isoformat()
    if isinstance(obj, (int, float, str, bool)) or obj is None:
        return obj
    if isinstance(obj, dict):
        return {str(k): _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(v) for v in obj]
    if hasattr(obj, "item"):
        try:
            return _json_safe(obj.item())
        except Exception:
            pass
    return str(obj)


def run_bounded_paper_session(
    *,
    market_df: pd.DataFrame,
    symbol: str,
    data_source: dict[str, Any],
    max_bars: int = 120,
    initial_cash: float = 100_000.0,
    lookback: int = 20,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if market_df is None or market_df.empty or symbol not in market_df.columns:
        raise ValueError(f"market_df must contain non-empty '{symbol}' column")
    df = market_df[[symbol]].dropna().copy()
    df = df.tail(max(max_bars + lookback + 5, lookback + 10))

    # Real-data strategy path: bounded mean-reversion intents on real prices.
    # Compute a bounded signal series on real prices; no fills fabricated.
    strat = MeanReversionStrategy(
        asset=symbol, lookback=lookback, entry_threshold=1.5, exit_threshold=0.5
    )
    sig_df = strat.generate_signals(df[[symbol]])

    acct = AccountState.with_cash(initial_cash)
    oms = OMS(acct)
    broker = PaperBroker(
        fee_rate=0.001, slippage_bps=5.0, execution_environment="paper_public_data"
    )
    dashboard = RiskDashboard(
        RiskConfig(
            max_notional_per_order=15_000.0,
            max_position_notional_per_symbol=30_000.0,
            max_gross_exposure=60_000.0,
            max_net_exposure=60_000.0,
            max_symbol_concentration=0.80,
            max_turnover_notional=500_000.0,
            max_drawdown_fraction=0.25,
            stale_data_seconds=3600.0,  # still enforced for non-replay callers
            require_market_price=True,
            fail_closed_on_missing_data=True,
            allow_historical_replay=True,
            replay_timestamp_skew_seconds=3600.0 * 24,  # bar timestamp consistency
        )
    )

    bars = []
    orders_out = []
    decision_log = []
    processed = 0
    last_ts = None
    for ts, row in df.iterrows():
        if processed >= max_bars:
            break
        px = float(row[symbol])
        last_ts = ts
        ts_iso = ts.isoformat() if hasattr(ts, "isoformat") else str(ts)
        sig_row = sig_df.loc[ts] if ts in sig_df.index else {}
        target = int(float(sig_row.get(symbol, 0.0) or 0.0)) if hasattr(sig_row, "get") else 0
        pos = acct.positions.get(symbol)
        cur_qty = pos.quantity if pos else 0.0
        # Bounded paper intent sizing: convert target direction to small notional intent.
        intent = None
        target_notional = target * 5000.0  # bounded paper sizing
        desired_qty = (target_notional / px) if px > 0 else 0.0
        delta = desired_qty - cur_qty
        # deadband
        if abs(delta) * px < 250.0:
            decision_log.append(
                {"timestamp_utc": ts_iso, "price": px, "target": target, "action": "hold_deadband"}
            )
        else:
            side = "buy" if delta > 0 else "sell"
            intent = OrderIntent(
                symbol=symbol,
                side=side,
                quantity=min(abs(delta), 0.5),  # strict cap for bounded demo safety
                order_type="market",
                client_order_id=f"{symbol}-{ts_iso}-{side}",
                timestamp=ts_iso,
                metadata={
                    "strategy": "mean_reversion_real_data_path",
                    "target": target,
                    "paper_bounded": True,
                },
            )
            pstate = acct.mark_to_market({symbol: px})
            now_utc = ts.to_pydatetime() if hasattr(ts, "to_pydatetime") else None
            risk_dec = dashboard.pre_trade_check(
                intent.normalized().__dict__,
                market_price=px,
                portfolio_state=pstate,
                data_timestamp_utc=ts_iso,
                now_utc=now_utc,
            )
            rec = oms.submit(intent, broker=broker, market_price=px, risk_decision=risk_dec)
            orders_out.append(rec.to_dict())
            decision_log.append(
                {
                    "timestamp_utc": ts_iso,
                    "price": px,
                    "target": target,
                    "action": "submit",
                    "risk_allowed": risk_dec.get("allowed"),
                    "order_id": rec.order_id,
                    "status": rec.status.value,
                }
            )
        mtm = acct.mark_to_market({symbol: px})
        dashboard.update_drawdown(float(mtm["equity"]))
        bars.append(
            {"timestamp_utc": ts_iso, "price": px, "equity": mtm["equity"], "cash": mtm["cash"]}
        )
        processed += 1

    final_ts = last_ts.isoformat() if hasattr(last_ts, "isoformat") else _utc_now()
    final_state = acct.mark_to_market({symbol: float(df[symbol].iloc[-1])})
    test_fixture = bool(data_source.get("test_fixture"))
    market_data_real_only = not test_fixture and data_source.get("type") in {
        "real_cached_public_binance",
        "real_public_binance",
        "real_public_or_cached_provenance",
    }
    session = {
        "campaign": "Campaign #5 - Production bridge",
        "status": "ok",
        "generated_at_utc": _utc_now(),
        "market_data_real_only": bool(market_data_real_only),
        "real_data_only": bool(market_data_real_only),
        "fabricated_data": False,
        "simulated_fills": True,
        "real_exchange_fills_claimed": False,
        "environment": {
            "mode": "paper_bounded_session",
            "exchange_submission": "disabled_fail_closed",
            "testnet_credentials_present": False,
            "live_submission_allowed": False,
            "broker": broker.state(),
        },
        "blocked_routes": broker.state().get("blocked_routes", []),
        "data_sources": _json_safe(data_source),
        "oms_config": {
            "initial_cash": initial_cash,
            "strategy": "MeanReversionStrategy real-data path (bounded paper intents)",
            "symbol": symbol,
            "lookback": lookback,
            "max_bars": max_bars,
            "bounded_order_quantity_cap": 0.5,
            "idempotency": "client_order_id required/indexed",
        },
        "risk_config": dashboard.runtime_state().get("config"),
        "orders": _json_safe(orders_out),
        "fills": _json_safe([f for o in orders_out for f in o.get("fills", [])]),
        "positions": _json_safe(final_state.get("positions", {})),
        "pnl_summary": _json_safe(
            {
                "initial_cash": initial_cash,
                "final_equity": final_state.get("equity"),
                "final_cash": final_state.get("cash"),
                "realized_pnl": final_state.get("realized_pnl"),
                "unrealized_pnl": final_state.get("unrealized_pnl"),
                "fees_paid": final_state.get("fees_paid"),
                "gross_exposure": final_state.get("gross_exposure"),
                "net_exposure": final_state.get("net_exposure"),
                "bars_processed": processed,
                "start_timestamp_utc": df.index[0].isoformat()
                if hasattr(df.index[0], "isoformat")
                else str(df.index[0]),
                "end_timestamp_utc": final_ts,
            }
        ),
        "equity_curve": _json_safe(bars[-50:]),
        "decision_log_tail": _json_safe(decision_log[-50:]),
        "risk_events": _json_safe([e.to_dict() for e in dashboard.events]),
        "limitations": [
            (
                "Paper fills are simulated from real/public market prices with "
                "deterministic slippage/fees; not real exchange fills."
            ),
            (
                "No live/testnet authenticated exchange order submission performed; "
                "credentials not assumed."
            ),
            (
                "Bounded session for production-bridge validation; not proof of "
                "profitability or live readiness."
            ),
            (
                "Historical intrabar/L2 replay not fabricated."
                if not test_fixture
                else (
                    "Test fixture path used in tests only; "
                    "campaign artifacts must use real/public data provenance."
                )
            ),
        ],
        "notes": [
            "Fail-closed OMS/risk controls active.",
            "All simulated fills are labeled simulated_fill=true and real_exchange_fill=false.",
        ],
    }
    risk_artifact = build_risk_dashboard_artifact(
        dashboard,
        campaign="Campaign #5 - Production bridge",
        generated_at_utc=_utc_now(),
        environment=session["environment"],
        data_sources=session["data_sources"],
        portfolio_state=final_state,
        blocked_routes=session["blocked_routes"],
        limitations=session["limitations"],
        extra={
            "market_data_real_only": session["market_data_real_only"],
            "fabricated_data": False,
            "simulated_fills_context": True,
            "session_artifact_ref": "reports/paper_trading_session.json",
        },
    )
    session["risk_dashboard"] = {
        "status": risk_artifact.get("status"),
        "breach_count": len(risk_artifact.get("events", [])),
        "kill_switch": risk_artifact.get("risk_state", {}).get("kill_switch"),
    }
    return session, risk_artifact


def main() -> int:
    reports_dir = ROOT / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    session_path = reports_dir / "paper_trading_session.json"
    risk_path = reports_dir / "risk_dashboard.json"

    loader = DataLoader()
    symbol = "BTC"
    start, end, interval = "2026-04-01", "2026-05-15", "1h"
    blocked_routes: list[dict[str, Any]] = []
    limitations: list[str] = []
    data_source: dict[str, Any]
    try:
        df, prov = load_cached(loader, [symbol], start, end, interval)
        # load_cached already preserves blocked route info; include it.
        for br in prov.get("blocked_routes", []) or []:
            blocked_routes.append(
                {"route": str(br), "status": "observed_by_loader", "reason": "see provenance"}
            )
        data_source = {
            "type": "real_cached_public_binance",
            "provider": (
                "Binance public spot via data.loader.DataLoader.load_binance_data/data.cache"
            ),
            "symbol": symbol,
            "start": start,
            "end": end,
            "interval": interval,
            "provenance": _json_safe(prov),
            "test_fixture": False,
        }
    except Exception as exc:
        # Honest failure: no fabricated market data. Still emit blocked artifacts.
        lp = getattr(loader, "last_fetch_provenance", {}) or {}
        for br in lp.get("blocked_routes") or []:
            blocked_routes.append({"route": str(br), "status": "blocked", "reason": str(exc)[:200]})
        blocked_routes.append(
            {"route": "real_market_data_load", "status": "blocked", "reason": str(exc)[:300]}
        )
        limitations.append(
            "Real/public market data unavailable in this environment; "
            "no fabricated market data or fills emitted."
        )
        session = {
            "campaign": "Campaign #5 - Production bridge",
            "status": "blocked",
            "generated_at_utc": _utc_now(),
            "market_data_real_only": False,
            "real_data_only": False,
            "fabricated_data": False,
            "simulated_fills": True,
            "real_exchange_fills_claimed": False,
            "blocked_routes": blocked_routes,
            "data_sources": {
                "type": "unavailable",
                "error": str(exc)[:500],
                "loader_provenance": _json_safe(lp),
            },
            "oms_config": {},
            "risk_config": RiskConfig().__dict__,
            "orders": [],
            "fills": [],
            "positions": {},
            "pnl_summary": {},
            "limitations": limitations,
            "notes": ["Blocked honestly: required real/public market data could not be loaded."],
        }
        dashboard = RiskDashboard(RiskConfig())
        dashboard.kill_switch.trip("market_data_unavailable", {"error": str(exc)[:300]})
        risk = build_risk_dashboard_artifact(
            dashboard,
            campaign="Campaign #5 - Production bridge",
            generated_at_utc=_utc_now(),
            environment={"mode": "paper_blocked", "exchange_submission": "disabled_fail_closed"},
            data_sources=session["data_sources"],
            portfolio_state={
                "equity": 0,
                "cash": 0,
                "gross_exposure": 0,
                "net_exposure": 0,
                "positions": {},
            },
            blocked_routes=blocked_routes,
            limitations=limitations,
        )
        session["risk_dashboard"] = {
            "status": risk["status"],
            "kill_switch": risk["risk_state"]["kill_switch"],
        }
        session_path.write_text(json.dumps(_json_safe(session), indent=2) + "\n")
        risk_path.write_text(json.dumps(_json_safe(risk), indent=2) + "\n")
        print(f"Wrote blocked artifacts: {session_path}, {risk_path}")
        return 2

    session, risk = run_bounded_paper_session(
        market_df=df, symbol=symbol, data_source=data_source, max_bars=120, initial_cash=100_000.0
    )
    session["blocked_routes"] = (session.get("blocked_routes") or []) + blocked_routes
    risk["blocked_routes"] = list(
        {
            json.dumps(b, sort_keys=True): b
            for b in (risk.get("blocked_routes") or []) + blocked_routes
        }.values()
    )
    session_path.write_text(json.dumps(_json_safe(session), indent=2) + "\n")
    risk_path.write_text(json.dumps(_json_safe(risk), indent=2) + "\n")
    print(f"Wrote {session_path} and {risk_path}")
    print(
        json.dumps(
            {
                "status": session["status"],
                "market_data_real_only": session["market_data_real_only"],
                "simulated_fills": session["simulated_fills"],
                "orders": len(session["orders"]),
                "fills": len(session["fills"]),
                "final_equity": session["pnl_summary"].get("final_equity"),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
