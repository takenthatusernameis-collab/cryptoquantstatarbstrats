"""Campaign #5 production bridge tests (OMS, paper broker, risk, provenance).

These tests validate fail-closed behavior and honest labeling. Any synthetic data
used here is a test fixture only and must never be presented as real evidence.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import pytest

from execution.oms import OMS, AccountState, OrderIntent, OrderStatus
from execution.paper_broker import PaperBroker
from execution.risk import KillSwitch, RiskConfig, RiskDashboard, StaleDataGuard


def test_order_intent_validation_fail_closed():
    with pytest.raises(ValueError):
        OrderIntent(symbol="", side="buy", quantity=1).validate()
    with pytest.raises(ValueError):
        OrderIntent(symbol="BTC", side="hold", quantity=1).validate()
    with pytest.raises(ValueError):
        OrderIntent(symbol="BTC", side="buy", quantity=0).validate()
    with pytest.raises(ValueError):
        OrderIntent(symbol="BTC", side="buy", quantity=-1).validate()
    with pytest.raises(ValueError):
        OrderIntent(symbol="BTC", side="buy", quantity=float("nan")).validate()
    with pytest.raises(ValueError):
        OrderIntent(symbol="BTC", side="buy", quantity=1, order_type="limit").validate()
    OrderIntent(
        symbol="BTC", side="buy", quantity=1, order_type="limit", limit_price=100
    ).validate()


def test_oms_idempotency_client_order_id():
    oms = OMS(AccountState.with_cash(100000))
    broker = PaperBroker(fee_rate=0.0, slippage_bps=0.0)
    intent = OrderIntent(symbol="BTC", side="buy", quantity=0.1, client_order_id="same-id")
    r1 = oms.submit(intent, broker=broker, market_price=50000)
    r2 = oms.submit(intent, broker=broker, market_price=50000)
    assert r1.order_id == r2.order_id
    assert r1.client_order_id == "same-id"
    assert oms.by_client_order_id("same-id").order_id == r1.order_id
    assert len([o for o in oms.orders.values()]) == 1


def test_oms_accounting_and_paper_fill_labeling():
    acct = AccountState.with_cash(100000)
    oms = OMS(acct)
    broker = PaperBroker(fee_rate=0.001, slippage_bps=0.0)
    intent = OrderIntent(symbol="ETH", side="buy", quantity=1.0, client_order_id="buy-eth")
    rec = oms.submit(intent, broker=broker, market_price=2000.0)
    assert rec.status in {OrderStatus.FILLED, OrderStatus.PARTIALLY_FILLED}
    assert rec.filled_quantity == pytest.approx(1.0)
    assert rec.cumulative_fee == pytest.approx(2.0)
    assert acct.cash == pytest.approx(100000 - 2000 - 2.0)
    assert acct.positions["ETH"].quantity == pytest.approx(1.0)
    assert len(rec.fills) == 1
    fill = rec.fills[0]
    assert fill["simulated_fill"] is True
    assert fill["paper"] is True
    assert fill["real_exchange_fill"] is False
    snap = acct.mark_to_market({"ETH": 2100.0})
    assert snap["positions"]["ETH"]["unrealized_pnl"] == pytest.approx(100.0)
    assert snap["gross_exposure"] == pytest.approx(2100.0)


def test_oms_rejects_unlabeled_fill():
    acct = AccountState.with_cash(100000)
    oms = OMS(acct)
    rec = oms.submit(
        OrderIntent(symbol="BTC", side="buy", quantity=0.01, client_order_id="x"),
        broker=None,
        market_price=50000,
    )
    # accepted without broker
    with pytest.raises(ValueError, match="simulated_fill|paper"):
        oms.apply_fill(rec.order_id, {"quantity": 0.01, "price": 50000, "fee": 0})


def test_paper_broker_never_claims_real_exchange_fills_and_blocks_live():
    broker = PaperBroker(fee_rate=0.0, slippage_bps=10.0, allow_live_submission=False)
    state = broker.state()
    assert state["simulated_fills"] is True
    assert state["real_exchange_fills"] is False
    assert state["allow_live_submission"] is False
    assert any(r.get("route") == "live_exchange_order_submission" for r in state["blocked_routes"])
    fills = broker.execute(
        {
            "order_id": "o1",
            "client_order_id": "c1",
            "symbol": "BTC",
            "side": "buy",
            "quantity": 1,
            "order_type": "market",
        },
        market_price=100.0,
    )
    assert len(fills) == 1
    assert fills[0]["real_exchange_fill"] is False
    assert fills[0]["simulated_fill"] is True
    assert fills[0]["price"] == pytest.approx(100.1)


def test_paper_broker_limit_crossing():
    broker = PaperBroker(fee_rate=0.0, slippage_bps=0.0)
    nofill = broker.execute(
        {
            "order_id": "o1",
            "client_order_id": "c1",
            "symbol": "BTC",
            "side": "buy",
            "quantity": 1,
            "order_type": "limit",
            "limit_price": 99.0,
        },
        market_price=100.0,
    )
    assert nofill == []
    fill = broker.execute(
        {
            "order_id": "o2",
            "client_order_id": "c2",
            "symbol": "BTC",
            "side": "buy",
            "quantity": 1,
            "order_type": "limit",
            "limit_price": 101.0,
        },
        market_price=100.0,
    )
    assert len(fill) == 1 and fill[0]["simulated_fill"] is True


def test_risk_kill_switch_fail_closed():
    ks = KillSwitch()
    dash = RiskDashboard(RiskConfig(max_notional_per_order=10), kill_switch=ks)
    ks.trip("manual")
    dec = dash.pre_trade_check(
        {"symbol": "BTC", "side": "buy", "quantity": 1},
        market_price=5.0,
        portfolio_state={
            "gross_exposure": 0,
            "net_exposure": 0,
            "equity": 1000,
            "cash": 1000,
            "positions": {},
        },
        data_timestamp_utc=datetime.now(timezone.utc).isoformat(),
    )
    assert dec["allowed"] is False
    assert dec["breaches"][0]["code"] == "kill_switch_active"


def test_risk_stale_data_fail_closed():
    dash = RiskDashboard(RiskConfig(stale_data_seconds=60))
    old = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
    dec = dash.pre_trade_check(
        {"symbol": "BTC", "side": "buy", "quantity": 0.001},
        market_price=50000.0,
        portfolio_state={
            "gross_exposure": 0,
            "net_exposure": 0,
            "equity": 100000,
            "cash": 100000,
            "positions": {},
        },
        data_timestamp_utc=old,
    )
    assert dec["allowed"] is False
    assert dec["breaches"][0]["code"] == "stale_or_missing_data"
    missing = dash.pre_trade_check(
        {"symbol": "BTC", "side": "buy", "quantity": 0.001},
        market_price=50000.0,
        portfolio_state={
            "gross_exposure": 0,
            "net_exposure": 0,
            "equity": 100000,
            "cash": 100000,
            "positions": {},
        },
        data_timestamp_utc=None,
    )
    assert missing["allowed"] is False


def test_risk_limits():
    dash = RiskDashboard(
        RiskConfig(
            max_notional_per_order=1000,
            max_gross_exposure=5000,
            max_symbol_concentration=0.4,
        )
    )
    now = datetime.now(timezone.utc).isoformat()
    base_port = {
        "gross_exposure": 0,
        "net_exposure": 0,
        "equity": 100000,
        "cash": 100000,
        "positions": {},
    }
    too_big = dash.pre_trade_check(
        {"symbol": "BTC", "side": "buy", "quantity": 1},
        market_price=2000.0,
        portfolio_state=base_port,
        data_timestamp_utc=now,
    )
    assert too_big["allowed"] is False
    codes = {b["code"] for b in too_big["breaches"]}
    assert "max_notional_per_order" in codes


def test_stale_guard_invalid_timestamp():
    g = StaleDataGuard(60)
    stale, reason = g.is_stale("not-a-time")
    assert stale is True and reason and "invalid" in reason


def test_runner_smoke_integration_real_cached_data_if_available():
    """Smoke test: run paper session logic on real cached data if present.

    Uses only cached real public Binance data when available (provenance-preserving).
    If cache is unavailable, uses a tiny clearly-labeled test fixture DataFrame
    and does NOT write campaign artifacts as real evidence.
    """
    root = Path(__file__).resolve().parent.parent
    import sys

    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from data.cache import load_cached
    from data.loader import DataLoader
    from examples.run_paper_trading_live import run_bounded_paper_session

    loader = DataLoader()
    used_fixture = False
    try:
        df, prov = load_cached(loader, ["BTC"], "2026-04-01", "2026-04-02", "1h")
        data_source = {
            "type": "real_cached_public_binance",
            "provenance": prov,
            "test_fixture": False,
        }
    except Exception:
        # test-only fixture fallback; never presented as real evidence
        idx = pd.date_range("2026-04-01", periods=24, freq="1h", tz="UTC")
        df = pd.DataFrame({"BTC": [50000.0 + i for i in range(len(idx))]}, index=idx)
        prov = {"blocked_routes": [], "cache_hit": False, "note": "test_fixture_only"}
        data_source = {
            "type": "test_fixture_synthetic_prices",
            "provenance": prov,
            "test_fixture": True,
        }
        used_fixture = True

    report, risk = run_bounded_paper_session(
        market_df=df,
        symbol="BTC",
        data_source=data_source,
        max_bars=5,
        initial_cash=100000.0,
    )
    assert report["simulated_fills"] is True
    assert report["fabricated_data"] is False
    assert report["real_exchange_fills_claimed"] is False
    assert isinstance(report["orders"], list)
    assert "risk_dashboard" in risk or "risk_state" in risk
    # paper fills, if any, must be labeled
    for f in report.get("fills", []):
        assert f.get("simulated_fill") is True
        assert f.get("real_exchange_fill") is False
    if used_fixture:
        assert report["market_data_real_only"] is False
        assert report["data_sources"]["test_fixture"] is True
    else:
        assert report["market_data_real_only"] is True
