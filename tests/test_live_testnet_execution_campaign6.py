"""Campaign #6: Live/testnet execution validation tests.

Tests cover:
- Adapter capability detection (fail-closed)
- Testnet adapter contract and simulated harness
- Order lifecycle state machine validation
- Microstructure simulation (latency, queue, partial fills, slippage, impact)
- Labeling/provenance (never claim real exchange evidence when simulated)
- Smoke integration
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

# Ensure repo root importable
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from execution.adapter import (  # noqa: E402
    AdapterMode,
    ExchangeCredentials,
    OrderAck,
    OrderIntent,
    OrderSide,
    OrderType,
    PaperExchangeAdapter,
    SimulatedTestnetAdapter,
    create_adapter_from_env,
)
from execution.lifecycle import (  # noqa: E402
    VALID_TRANSITIONS,
    LifecycleEvent,
    LifecycleHarness,
    LifecycleState,
    LifecycleValidator,
    OrderLifecycle,
    create_test_lifecycle_scenarios,
)
from execution.microstructure import (  # noqa: E402
    DataGapHandler,
    LatencySimulator,
    MicrostructureConfig,
    MicrostructurePaperBroker,
    PaperFillResult,
    QueueSimulator,
    SlippageImpactModel,
    create_microstructure_broker_from_env,
)
from execution.oms import OMS, AccountState  # noqa: E402
from execution.oms import OrderIntent as OMSOrderIntent  # noqa: E402
from execution.paper_broker import PaperBroker  # noqa: E402
from execution.risk import RiskConfig, RiskDashboard  # noqa: E402


class TestAdapterCapabilityDetection:
    """Test fail-closed capability detection."""

    def test_paper_adapter_blocks_live_routes(self):
        adapter = PaperExchangeAdapter()
        summary = adapter.get_capability_summary()
        assert summary["mode"] == "paper"
        blocked = summary["blocked_routes"]
        assert any(b["route"] == "live_exchange_order_submission" for b in blocked)
        assert any(b["route"] == "exchange_authenticated_api" for b in blocked)

    def test_simulated_testnet_adapter_labels_simulated(self):
        creds = ExchangeCredentials(
            api_key_env_var="BINANCE_TESTNET_API_KEY",
            api_secret_env_var="BINANCE_TESTNET_API_SECRET",
            testnet=True,
        )
        adapter = SimulatedTestnetAdapter(credentials=creds)
        summary = adapter.get_capability_summary()
        assert summary["mode"] == "testnet"
        blocked = summary["blocked_routes"]
        assert any(b["route"] == "authenticated_testnet_api" for b in blocked)
        assert any(b["status"] == "simulated" for b in blocked)

    def test_credentials_presence_probe(self):
        creds = ExchangeCredentials(
            api_key_env_var="NONEXISTENT_KEY",
            api_secret_env_var="NONEXISTENT_SECRET",
            testnet=True,
        )
        adapter = PaperExchangeAdapter(credentials=creds)
        probes = adapter.run_capability_probes()
        cred_probe = next((p for p in probes if p.probe_name == "credentials_presence"), None)
        assert cred_probe is not None
        assert cred_probe.success is False
        assert "presence" in cred_probe.details

    def test_capability_probe_dns_tcp_http(self):
        adapter = PaperExchangeAdapter()
        probes = adapter.run_capability_probes()
        probe_names = {p.probe_name for p in probes}
        assert any(n.startswith("dns_") for n in probe_names)
        assert any(n.startswith("tcp_") for n in probe_names)
        assert any(n.startswith("http_") for n in probe_names)

    def test_capability_probe_records_latency(self):
        adapter = PaperExchangeAdapter()
        probes = adapter.run_capability_probes()
        for p in probes:
            if p.success and p.latency_ms is not None:
                assert p.latency_ms >= 0

    def test_create_adapter_from_env_defaults_to_paper(self):
        # Ensure no ADAPTER_MODE set
        if "ADAPTER_MODE" in os.environ:
            del os.environ["ADAPTER_MODE"]
        adapter = create_adapter_from_env()
        assert isinstance(adapter, PaperExchangeAdapter)
        assert adapter.mode == AdapterMode.PAPER


class TestAdapterContract:
    """Test exchange adapter interface contract."""

    def test_paper_adapter_submit_ack_fill_lifecycle(self):
        adapter = PaperExchangeAdapter(fee_rate=0.0, slippage_bps=0.0)
        intent = OrderIntent(
            symbol="BTCUSDT",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=0.01,
            client_order_id="test-1",
        )
        ack = adapter.submit_order(intent)
        assert isinstance(ack, OrderAck)
        assert ack.status.value == "acknowledged"
        assert ack.simulated is True
        assert ack.real_exchange_interaction is False

        # Query order
        order_update = adapter.query_order(ack.exchange_order_id, "BTCUSDT")
        assert order_update.status.value == "acknowledged"

        # Simulate fill
        fills = adapter.simulate_fill(ack.exchange_order_id, market_price=50000.0)
        assert len(fills) == 1
        fill = fills[0]
        assert fill.simulated is True
        assert fill.real_exchange_fill is False
        assert fill.execution_environment == "paper"

    def test_paper_adapter_limit_order_no_cross(self):
        adapter = PaperExchangeAdapter(fee_rate=0.0, slippage_bps=0.0)
        intent = OrderIntent(
            symbol="BTCUSDT",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=0.01,
            limit_price=49000.0,  # Below market
            client_order_id="test-limit-1",
        )
        ack = adapter.submit_order(intent)
        assert ack.status.value == "acknowledged"
        # No fill without crossing
        adapter.simulate_fill(ack.exchange_order_id, market_price=50000.0)
        # In paper adapter, limit orders don't auto-fill on simulate_fill unless crossed
        # The simulate_fill method will fill if market crosses
        order = adapter.query_order(ack.exchange_order_id, "BTCUSDT")
        assert order.filled_quantity == 0.0

    def test_paper_adapter_cancel_replace(self):
        adapter = PaperExchangeAdapter(fee_rate=0.0, slippage_bps=0.0)
        intent = OrderIntent(
            symbol="BTCUSDT",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=0.01,
            client_order_id="test-replace-1",
        )
        ack = adapter.submit_order(intent)
        # Cancel
        cancel_result = adapter.cancel_order(ack.exchange_order_id, "BTCUSDT")
        assert cancel_result.status.value == "canceled"

        # Replace
        intent2 = OrderIntent(
            symbol="BTCUSDT",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=0.02,
            client_order_id="test-replace-2",
        )
        # Submit then replace
        ack2 = adapter.submit_order(intent)
        replace_result = adapter.replace_order(ack2.exchange_order_id, "BTCUSDT", intent2)
        assert replace_result.status.value in {"acknowledged", "filled", "partially_filled"}

    def test_paper_adapter_get_open_orders(self):
        adapter = PaperExchangeAdapter(fee_rate=0.0, slippage_bps=0.0)
        intent = OrderIntent(
            symbol="BTCUSDT",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=0.01,
            client_order_id="test-open-1",
        )
        ack = adapter.submit_order(intent)
        open_orders = adapter.get_open_orders("BTCUSDT")
        assert len(open_orders) >= 1
        assert any(o.exchange_order_id == ack.exchange_order_id for o in open_orders)

    def test_paper_adapter_account_balances_exchange_info(self):
        adapter = PaperExchangeAdapter()
        balances = adapter.get_account_balances()
        assert balances["simulated"] is True
        assert balances["real_exchange_interaction"] is False
        exchange_info = adapter.get_exchange_info()
        assert exchange_info["simulated"] is True
        assert exchange_info["real_exchange_interaction"] is False


class TestOrderLifecycleStateMachine:
    """Test formal order lifecycle state machine."""

    def test_valid_transitions(self):
        for (from_state, event), to_state in VALID_TRANSITIONS.items():
            lifecycle = OrderLifecycle(
                client_order_id="test",
                symbol="BTCUSDT",
                side="buy",
                order_type="market",
                quantity=1.0,
            )
            lifecycle.state = from_state
            new_state = lifecycle.transition(event)
            assert new_state == to_state

    def test_invalid_transition_raises(self):
        lifecycle = OrderLifecycle(
            client_order_id="test",
            symbol="BTCUSDT",
            side="buy",
            order_type="market",
            quantity=1.0,
        )
        # Cannot fill from CREATED
        with pytest.raises(ValueError, match="Invalid transition"):
            lifecycle.transition(LifecycleEvent.FILL)

    def test_market_fill_scenario(self):
        lifecycle = OrderLifecycle(
            client_order_id="test-market",
            symbol="BTCUSDT",
            side="buy",
            order_type="market",
            quantity=1.0,
        )
        lifecycle.submit()
        lifecycle.acknowledge()
        lifecycle.fill(1.0, 50000.0)
        assert lifecycle.state == LifecycleState.FILLED
        assert lifecycle.filled_quantity == 1.0
        assert lifecycle.is_terminal()

    def test_partial_then_full_fill(self):
        lifecycle = OrderLifecycle(
            client_order_id="test-partial",
            symbol="BTCUSDT",
            side="buy",
            order_type="market",
            quantity=1.0,
        )
        lifecycle.submit()
        lifecycle.acknowledge()
        lifecycle.partial_fill(0.3, 50000.0)
        assert lifecycle.state == LifecycleState.PARTIALLY_FILLED
        assert lifecycle.filled_quantity == 0.3
        lifecycle.fill(0.7, 50100.0)
        assert lifecycle.state == LifecycleState.FILLED
        assert lifecycle.filled_quantity == 1.0

    def test_cancel_before_fill(self):
        lifecycle = OrderLifecycle(
            client_order_id="test-cancel",
            symbol="BTCUSDT",
            side="buy",
            order_type="market",
            quantity=1.0,
        )
        lifecycle.submit()
        lifecycle.acknowledge()
        lifecycle.request_cancel()
        lifecycle.acknowledge_cancel()
        assert lifecycle.state == LifecycleState.CANCELED
        assert lifecycle.is_terminal()

    def test_cancel_after_partial_fill(self):
        lifecycle = OrderLifecycle(
            client_order_id="test-cancel-partial",
            symbol="BTCUSDT",
            side="buy",
            order_type="market",
            quantity=1.0,
        )
        lifecycle.submit()
        lifecycle.acknowledge()
        lifecycle.partial_fill(0.3, 50000.0)
        lifecycle.request_cancel()
        lifecycle.acknowledge_cancel()
        assert lifecycle.state == LifecycleState.CANCELED
        assert lifecycle.filled_quantity == 0.3

    def test_replace_order(self):
        lifecycle = OrderLifecycle(
            client_order_id="test-replace",
            symbol="BTCUSDT",
            side="buy",
            order_type="market",
            quantity=1.0,
        )
        lifecycle.submit()
        lifecycle.acknowledge()
        lifecycle.request_replace("new-coid")
        lifecycle.acknowledge_replace()
        assert lifecycle.state == LifecycleState.REPLACED
        assert lifecycle.is_terminal()

    def test_reject(self):
        lifecycle = OrderLifecycle(
            client_order_id="test-reject",
            symbol="BTCUSDT",
            side="buy",
            order_type="market",
            quantity=1.0,
        )
        lifecycle.submit()
        lifecycle.reject("insufficient_balance", "Not enough funds")
        assert lifecycle.state == LifecycleState.REJECTED
        assert lifecycle.reject_reason == "insufficient_balance"
        assert lifecycle.is_terminal()

    def test_timeout_retry(self):
        lifecycle = OrderLifecycle(
            client_order_id="test-timeout",
            symbol="BTCUSDT",
            side="buy",
            order_type="market",
            quantity=1.0,
        )
        lifecycle.submit()
        lifecycle.timeout()
        assert lifecycle.state == LifecycleState.TIMEOUT
        lifecycle.retry()
        assert lifecycle.state == LifecycleState.SUBMITTED

    def test_lifecycle_validator(self):
        validator = LifecycleValidator(strict=True)
        scenarios = create_test_lifecycle_scenarios()
        for name, transitions in scenarios.items():
            is_valid, errors = validator.validate_sequence(transitions)
            assert is_valid, f"Scenario {name} failed: {errors}"

    def test_lifecycle_harness_helpers(self):
        harness = LifecycleHarness()
        harness.create_order("test-1", "BTCUSDT", "buy", "market", 0.01)
        lifecycle = harness.run_full_lifecycle_market("test-1", 50000.0)
        assert lifecycle.state == LifecycleState.FILLED

        harness.create_order("test-2", "BTCUSDT", "buy", "limit", 0.01)
        lifecycle2 = harness.run_full_lifecycle_limit("test-2", 50000.0, crosses=True)
        assert lifecycle2.state == LifecycleState.FILLED

        harness.create_order("test-3", "BTCUSDT", "buy", "limit", 0.01)
        lifecycle3 = harness.run_full_lifecycle_limit("test-3", 50000.0, crosses=False)
        assert lifecycle3.state == LifecycleState.EXPIRED

        harness.create_order("test-4", "BTCUSDT", "buy", "market", 0.01)
        lifecycle4 = harness.run_partial_fill_then_complete("test-4", 0.005, 50000.0, 50100.0)
        assert lifecycle4.state == LifecycleState.FILLED

        harness.create_order("test-5", "BTCUSDT", "buy", "market", 0.01)
        lifecycle5 = harness.run_cancel_before_fill("test-5")
        assert lifecycle5.state == LifecycleState.CANCELED

        harness.create_order("test-6", "BTCUSDT", "buy", "market", 0.01)
        lifecycle6 = harness.run_cancel_after_partial("test-6", 0.005, 50000.0)
        assert lifecycle6.state == LifecycleState.CANCELED
        assert lifecycle6.filled_quantity == 0.005

        harness.create_order("test-7", "BTCUSDT", "buy", "market", 0.01)
        lifecycle7 = harness.run_replace("test-7", "test-7-replaced")
        assert lifecycle7.state == LifecycleState.REPLACED

        harness.create_order("test-8", "BTCUSDT", "buy", "market", 0.01)
        lifecycle8 = harness.run_reject("test-8", "insufficient_balance")
        assert lifecycle8.state == LifecycleState.REJECTED

        harness.create_order("test-9", "BTCUSDT", "buy", "market", 0.01)
        lifecycle9 = harness.run_timeout_retry("test-9")
        assert lifecycle9.state == LifecycleState.ACKNOWLEDGED


class TestMicrostructureSimulation:
    """Test paper microstructure realism."""

    def test_latency_simulator_distributions(self):
        config = MicrostructureConfig(
            base_latency_ms=10.0,
            latency_jitter_ms=5.0,
            network_latency_distribution="fixed",
            random_seed=42,
        )
        sim = LatencySimulator(config)
        sample = sim.sample_latency()
        assert sample.total_ms == 10.0
        assert sample.distribution == "fixed"

        config.network_latency_distribution = "normal"
        sim = LatencySimulator(config)
        sample = sim.sample_latency()
        assert sample.total_ms >= 10.0

        config.network_latency_distribution = "lognormal"
        sim = LatencySimulator(config)
        sample = sim.sample_latency()
        assert sample.total_ms >= 10.0

    def test_slippage_impact_model(self):
        config = MicrostructureConfig(
            base_slippage_bps=5.0,
            volatility_slippage_multiplier=1.0,
            impact_model="square_root",
            impact_coefficient=0.1,
            adv_usd=1_000_000.0,
        )
        model = SlippageImpactModel(config)

        # Base slippage
        slip = model.compute_slippage_bps("buy", 10000.0)
        assert slip >= 5.0

        # With volatility
        slip_vol = model.compute_slippage_bps("buy", 10000.0, volatility=0.02)
        assert slip_vol > slip

        # With notional (impact)
        slip_large = model.compute_slippage_bps("buy", 100_000.0)
        assert slip_large > slip

        # Apply to price
        price = model.apply_slippage("buy", 50000.0, 10000.0)
        assert price > 50000.0
        price_sell = model.apply_slippage("sell", 50000.0, 10000.0)
        assert price_sell < 50000.0

    def test_queue_simulator_partial_fills(self):
        config = MicrostructureConfig(
            enable_queue_simulation=True,
            partial_fill_probability=1.0,  # Always partial
            partial_fill_min_ratio=0.3,
            partial_fill_max_ratio=0.7,
            queue_position_impact_bps=0.5,
            random_seed=42,
        )
        queue = QueueSimulator(config)
        filled_qty, fill_price = queue.simulate_queue_fill(1.0, 50000.0, "buy", queue_position=1)
        assert 0.3 <= filled_qty <= 0.7
        assert fill_price > 50000.0  # Buy gets worse price with queue position

    def test_data_gap_handler(self):
        config = MicrostructureConfig(
            enable_data_gap_handling=True,
            max_gap_tolerance_bars=5,
            gap_fill_strategy="last_known",
        )
        handler = DataGapHandler(config)

        # First bar - no last known
        result = handler.handle_gap("BTCUSDT", None, None)
        assert result is None

        # Provide a bar
        handler.handle_gap("BTCUSDT", {"close": 50000.0}, None)
        # Gap - should fill with last known
        result = handler.handle_gap("BTCUSDT", None, {"close": 50000.0})
        assert result is not None
        assert result["close"] == 50000.0
        assert result["gap_filled"] is True

    def test_microstructure_paper_broker_full_flow(self):
        config = MicrostructureConfig(
            base_latency_ms=1.0,
            latency_jitter_ms=0.5,
            network_latency_distribution="fixed",
            base_slippage_bps=5.0,
            partial_fill_probability=0.0,
            random_seed=42,
        )
        broker = MicrostructurePaperBroker(config=config, fee_rate=0.001)

        order = {
            "order_id": "micro-1",
            "client_order_id": "micro-coid-1",
            "symbol": "BTCUSDT",
            "side": "buy",
            "quantity": 0.01,
            "order_type": "market",
        }
        fills = broker.execute(order, market_price=50000.0, volatility=0.02)
        assert len(fills) == 1
        fill = fills[0]
        assert isinstance(fill, PaperFillResult)
        assert fill.simulated is True
        assert fill.real_exchange_fill is False
        assert fill.execution_environment == "paper_microstructure"
        assert fill.filled_qty == 0.01
        assert fill.fill_price > 50000.0  # Slippage applied
        assert fill.latency.total_ms > 0
        assert fill.slippage_bps > 0
        assert fill.queue_position >= 0

    def test_microstructure_partial_fill_probability(self):
        config = MicrostructureConfig(
            partial_fill_probability=1.0,
            partial_fill_min_ratio=0.5,
            partial_fill_max_ratio=0.5,
            random_seed=42,
        )
        broker = MicrostructurePaperBroker(config=config, fee_rate=0.0)

        order = {
            "order_id": "micro-2",
            "client_order_id": "micro-coid-2",
            "symbol": "BTCUSDT",
            "side": "buy",
            "quantity": 1.0,
            "order_type": "market",
        }
        fills = broker.execute(order, market_price=50000.0)
        assert len(fills) == 1
        # With probability 1.0 and ratio 0.5, should get partial
        assert fills[0].filled_qty == 0.5

    def test_microstructure_limit_order(self):
        config = MicrostructureConfig(random_seed=42)
        broker = MicrostructurePaperBroker(config=config, fee_rate=0.0)

        # Limit buy below market - should not fill
        order = {
            "order_id": "micro-3",
            "client_order_id": "micro-coid-3",
            "symbol": "BTCUSDT",
            "side": "buy",
            "quantity": 0.01,
            "order_type": "limit",
            "limit_price": 49000.0,
        }
        fills = broker.execute(order, market_price=50000.0)
        assert fills == []

        # Limit buy above market - should fill
        order["limit_price"] = 51000.0
        order["client_order_id"] = "micro-coid-4"
        fills = broker.execute(order, market_price=50000.0)
        assert len(fills) == 1


class TestProvenanceLabeling:
    """Test that all simulated outputs are properly labeled."""

    def test_paper_adapter_ack_labeled_simulated(self):
        adapter = PaperExchangeAdapter()
        intent = OrderIntent(
            symbol="BTCUSDT",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=0.01,
        )
        ack = adapter.submit_order(intent)
        assert ack.simulated is True
        assert ack.real_exchange_interaction is False

    def test_paper_adapter_fill_labeled_simulated(self):
        adapter = PaperExchangeAdapter(fee_rate=0.0, slippage_bps=0.0)
        intent = OrderIntent(
            symbol="BTCUSDT",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=0.01,
        )
        ack = adapter.submit_order(intent)
        fills = adapter.simulate_fill(ack.exchange_order_id, market_price=50000.0)
        assert len(fills) == 1
        assert fills[0].simulated is True
        assert fills[0].real_exchange_fill is False

    def test_lifecycle_harness_labeled_simulated(self):
        harness = LifecycleHarness()
        harness.create_order("test", "BTCUSDT", "buy", "market", 0.01)
        lifecycle = harness.run_full_lifecycle_market("test", 50000.0)
        assert lifecycle.simulated is True
        assert lifecycle.real_exchange_interaction is False

    def test_microstructure_fills_labeled_simulated(self):
        broker = create_microstructure_broker_from_env()
        order = {
            "order_id": "test",
            "client_order_id": "test-coid",
            "symbol": "BTCUSDT",
            "side": "buy",
            "quantity": 0.01,
            "order_type": "market",
        }
        fills = broker.execute(order, market_price=50000.0)
        for fill in fills:
            assert fill.simulated is True
            assert fill.real_exchange_fill is False

    def test_oms_rejects_unlabeled_fills(self):
        acct = AccountState.with_cash(100000)
        oms = OMS(acct)
        broker = PaperBroker(fee_rate=0.0, slippage_bps=0.0)
        intent = OMSOrderIntent(symbol="BTC", side="buy", quantity=0.01, client_order_id="x")
        rec = oms.submit(intent, broker=broker, market_price=50000.0)

        # Try to apply fill without simulated_fill label
        with pytest.raises(ValueError, match="simulated_fill|paper"):
            oms.apply_fill(rec.order_id, {"quantity": 0.01, "price": 50000, "fee": 0})


class TestSmokeIntegration:
    """Smoke integration test for Campaign #6 components."""

    def test_adapter_lifecycle_microstructure_integration(self):
        """Run a complete flow: adapter -> lifecycle -> microstructure."""
        # 1. Adapter submits order
        adapter = PaperExchangeAdapter(fee_rate=0.001, slippage_bps=5.0)
        intent = OrderIntent(
            symbol="BTCUSDT",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=0.01,
            client_order_id="integration-1",
        )
        ack = adapter.submit_order(intent)
        assert ack.status.value == "acknowledged"

        # 2. Track lifecycle
        lifecycle = OrderLifecycle(
            client_order_id=ack.client_order_id,
            symbol=ack.symbol,
            side=ack.side.value,
            order_type=ack.order_type.value,
            quantity=ack.quantity,
            limit_price=ack.limit_price,
            exchange_order_id=ack.exchange_order_id,
        )
        lifecycle.submit(ack.exchange_order_id)
        lifecycle.acknowledge()

        # 3. Microstructure fill (deterministic full-fill broker; no partial fill noise)
        micro_broker = create_microstructure_broker_from_env()
        micro_broker.config.partial_fill_probability = 0.0
        order_dict = {
            "order_id": ack.exchange_order_id,
            "client_order_id": ack.client_order_id,
            "symbol": ack.symbol,
            "side": ack.side.value,
            "quantity": ack.quantity,
            "order_type": ack.order_type.value,
        }
        fills = micro_broker.execute(order_dict, market_price=50000.0, volatility=0.02)
        assert len(fills) == 1
        fill = fills[0]

        # 4. Complete lifecycle
        lifecycle.fill(fill.filled_qty, fill.fill_price, fill.fee)
        assert lifecycle.state == LifecycleState.FILLED
        assert lifecycle.is_terminal()

        # 5. Validate lifecycle
        validator = LifecycleValidator()
        is_valid, errors = validator.validate_lifecycle(lifecycle)
        assert is_valid, f"Integration lifecycle invalid: {errors}"

    def test_runner_smoke(self):
        """Smoke test the Campaign #6 runner (dry run)."""
        from examples.run_live_testnet_readiness import run_live_testnet_readiness
        readiness, lifecycle, microstructure = run_live_testnet_readiness()

        assert readiness["campaign"] == "Campaign #6 - Live/testnet execution validation"
        assert readiness["status"] == "ok"
        assert "capability_probes" in readiness
        assert "blocked_routes" in readiness
        assert "preflight_checklist" in readiness

        assert lifecycle["campaign"] == "Campaign #6 - Live/testnet execution validation"
        assert lifecycle["status"] == "ok"
        assert lifecycle["scenarios_passed"] == lifecycle["scenarios_tested"]

        assert microstructure["campaign"] == "Campaign #6 - Live/testnet execution validation"
        assert microstructure["status"] == "ok"
        assert microstructure["fill_count"] > 0


class TestFailClosedBehavior:
    """Test fail-closed behavior across Campaign #6 components."""

    def test_adapter_blocks_without_credentials(self):
        adapter = PaperExchangeAdapter()
        # No credentials configured - live submission blocked
        summary = adapter.get_capability_summary()
        blocked = summary["blocked_routes"]
        assert any(b["status"] == "blocked_fail_closed" for b in blocked)

    def test_risk_dashboard_fail_closed_stale_data(self):
        dashboard = RiskDashboard(RiskConfig(stale_data_seconds=60))
        old_ts = datetime(2020, 1, 1, tzinfo=timezone.utc).isoformat()
        decision = dashboard.pre_trade_check(
            {"symbol": "BTC", "side": "buy", "quantity": 0.001},
            market_price=50000.0,
            portfolio_state={
                "gross_exposure": 0,
                "net_exposure": 0,
                "equity": 100000,
                "cash": 100000,
                "positions": {},
            },
            data_timestamp_utc=old_ts,
        )
        assert decision["allowed"] is False
        assert decision["breaches"][0]["code"] == "stale_or_missing_data"

    def test_oms_rejects_invalid_intent(self):
        oms = OMS(AccountState.with_cash(100000))
        intent = OMSOrderIntent(symbol="", side="buy", quantity=1)
        rec = oms.submit(intent, broker=None, market_price=50000)
        assert rec.status.value == "rejected"

    def test_microstructure_requires_market_price(self):
        broker = create_microstructure_broker_from_env()
        order = {
            "order_id": "test",
            "client_order_id": "test",
            "symbol": "BTCUSDT",
            "side": "buy",
            "quantity": 0.01,
            "order_type": "market",
        }
        with pytest.raises(ValueError, match="market_price"):
            broker.execute(order, market_price=None)

    def test_no_fabricated_exchange_evidence(self):
        """Ensure no component claims real exchange interaction when simulated."""
        adapter = PaperExchangeAdapter()
        ack = adapter.submit_order(OrderIntent(
            symbol="BTCUSDT", side=OrderSide.BUY, order_type=OrderType.MARKET, quantity=0.01))
        assert ack.real_exchange_interaction is False

        broker = create_microstructure_broker_from_env()
        fills = broker.execute({"order_id": "x", "client_order_id": "x", "symbol": "BTCUSDT",
                                "side": "buy", "quantity": 0.01, "order_type": "market"},
                               market_price=50000.0)
        for fill in fills:
            assert fill.real_exchange_fill is False

        harness = LifecycleHarness()
        harness.create_order("x", "BTCUSDT", "buy", "market", 0.01)
        lifecycle = harness.run_full_lifecycle_market("x", 50000.0)
        assert lifecycle.real_exchange_interaction is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
