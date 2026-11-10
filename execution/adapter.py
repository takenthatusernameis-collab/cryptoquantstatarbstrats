"""Campaign #6: Exchange adapter abstraction with fail-closed capability detection.

This module provides:
- Abstract ExchangeAdapter interface (paper default; optional authenticated testnet/live adapter)
- Capability detection probes for credentials/endpoints/network/testnet availability
- Honest recording of blocked routes, limitations, and environment probes
- No secrets in artifacts; credentials never assumed

If authenticated testnet/live access is unavailable, the adapter contract and a
simulated testnet-like lifecycle harness are provided with explicit
`simulated`/`real_exchange_interaction=false` labels and honest limitations.
"""

from __future__ import annotations

import os
import socket
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _is_finite_number(value: Any) -> bool:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return False
    return v == v and v != float("inf") and v != float("-inf")


class AdapterMode(str, Enum):
    PAPER = "paper"
    TESTNET = "testnet"
    LIVE = "live"


class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"


class OrderStatus(str, Enum):
    NEW = "new"
    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELED = "canceled"
    REPLACED = "replaced"
    REJECTED = "rejected"
    EXPIRED = "expired"


class RejectReason(str, Enum):
    INVALID_INPUT = "invalid_input"
    INSUFFICIENT_BALANCE = "insufficient_balance"
    POSITION_LIMIT = "position_limit"
    PRICE_FILTER = "price_filter"
    LOT_SIZE_FILTER = "lot_size_filter"
    NOTIONAL_FILTER = "notional_filter"
    UNKNOWN_SYMBOL = "unknown_symbol"
    EXCHANGE_MAINTENANCE = "exchange_maintenance"
    RATE_LIMIT = "rate_limit"
    INTERNAL_ERROR = "internal_error"
    AUTHENTICATION_FAILED = "authentication_failed"
    IP_NOT_WHITELISTED = "ip_not_whitelisted"
    TESTNET_DISABLED = "testnet_disabled"
    NOT_FOUND = "not_found"


@dataclass
class CapabilityProbe:
    """Result of a capability probe (network, credentials, endpoint reachability)."""
    probe_name: str
    target: str
    attempted_at_utc: str
    success: bool
    latency_ms: float | None = None
    error: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "probe_name": self.probe_name,
            "target": self.target,
            "attempted_at_utc": self.attempted_at_utc,
            "success": self.success,
            "latency_ms": self.latency_ms,
            "error": self.error,
            "details": dict(self.details),
        }


@dataclass
class ExchangeCredentials:
    """Exchange credential configuration (names only, never values in artifacts)."""
    api_key_env_var: str
    api_secret_env_var: str
    passphrase_env_var: str | None = None
    testnet: bool = True

    def to_dict_safe(self) -> dict[str, Any]:
        """Safe representation for artifacts (names only, never values)."""
        return {
            "api_key_env_var": self.api_key_env_var,
            "api_secret_env_var": self.api_secret_env_var,
            "passphrase_env_var": self.passphrase_env_var,
            "testnet": self.testnet,
            "values_present": self._check_presence(),
        }

    def _check_presence(self) -> dict[str, bool]:
        return {
            "api_key": bool(os.environ.get(self.api_key_env_var)),
            "api_secret": bool(os.environ.get(self.api_secret_env_var)),
            "passphrase": bool(os.environ.get(self.passphrase_env_var)) if self.passphrase_env_var else True,
        }

    def get_credentials(self) -> dict[str, str] | None:
        """Get actual credentials if all present; else None."""
        key = os.environ.get(self.api_key_env_var)
        secret = os.environ.get(self.api_secret_env_var)
        passphrase = os.environ.get(self.passphrase_env_var) if self.passphrase_env_var else ""
        if key and secret and (self.passphrase_env_var is None or passphrase):
            return {"api_key": key, "api_secret": secret, "passphrase": passphrase or ""}
        return None


@dataclass
class OrderIntent:
    """Normalized order intent for adapter submission."""
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    limit_price: float | None = None
    client_order_id: str | None = None
    timestamp: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def normalized(self) -> "OrderIntent":
        symbol = str(self.symbol).strip().upper()
        if isinstance(self.side, OrderSide):
            side = self.side
        else:
            side = OrderSide(str(self.side).strip().lower())
        if isinstance(self.order_type, OrderType):
            order_type = self.order_type
        else:
            order_type = OrderType(str(self.order_type).strip().lower())
        coid = self.client_order_id
        if coid is None or str(coid).strip() == "":
            coid = f"coid-{uuid.uuid4().hex}"
        ts = self.timestamp or _utc_now_iso()
        limit_price = float(self.limit_price) if self.limit_price is not None else None
        return OrderIntent(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=float(self.quantity),
            limit_price=limit_price,
            client_order_id=str(coid),
            timestamp=ts,
            metadata=dict(self.metadata or {}),
        )

    def validate(self) -> None:
        intent = self.normalized()
        if not intent.symbol:
            raise ValueError("symbol is required")
        if not _is_finite_number(intent.quantity) or intent.quantity <= 0.0:
            raise ValueError("quantity must be a finite number > 0")
        if intent.order_type == OrderType.LIMIT:
            if intent.limit_price is None or not _is_finite_number(intent.limit_price) or float(intent.limit_price) <= 0.0:
                raise ValueError("limit_price must be a finite number > 0 for limit orders")
        else:
            if intent.limit_price is not None:
                lp = intent.limit_price
                if not _is_finite_number(lp) or float(lp) <= 0.0:
                    raise ValueError("limit_price, if provided for market orders, must be > 0")


@dataclass
class OrderAck:
    """Exchange acknowledgment of order submission."""
    exchange_order_id: str
    client_order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    limit_price: float | None
    status: OrderStatus
    timestamp_utc: str
    simulated: bool = True
    real_exchange_interaction: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "exchange_order_id": self.exchange_order_id,
            "client_order_id": self.client_order_id,
            "symbol": self.symbol,
            "side": self.side.value,
            "order_type": self.order_type.value,
            "quantity": self.quantity,
            "limit_price": self.limit_price,
            "status": self.status.value,
            "timestamp_utc": self.timestamp_utc,
            "simulated": self.simulated,
            "real_exchange_interaction": self.real_exchange_interaction,
            "metadata": dict(self.metadata),
        }


@dataclass
class Fill:
    """Order fill from exchange."""
    exchange_order_id: str
    client_order_id: str
    symbol: str
    side: OrderSide
    quantity: float
    price: float
    fee: float
    fee_asset: str
    timestamp_utc: str
    trade_id: str | None = None
    simulated: bool = True
    real_exchange_fill: bool = False
    execution_environment: str = "paper"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "exchange_order_id": self.exchange_order_id,
            "client_order_id": self.client_order_id,
            "symbol": self.symbol,
            "side": self.side.value,
            "quantity": self.quantity,
            "price": self.price,
            "fee": self.fee,
            "fee_asset": self.fee_asset,
            "timestamp_utc": self.timestamp_utc,
            "trade_id": self.trade_id,
            "simulated": self.simulated,
            "real_exchange_fill": self.real_exchange_fill,
            "execution_environment": self.execution_environment,
            "metadata": dict(self.metadata),
        }


@dataclass
class OrderUpdate:
    """Generic order state update from exchange."""
    exchange_order_id: str
    client_order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    limit_price: float | None
    status: OrderStatus
    filled_quantity: float
    avg_fill_price: float
    cumulative_fee: float
    timestamp_utc: str
    reject_reason: RejectReason | None = None
    reject_message: str | None = None
    simulated: bool = True
    real_exchange_interaction: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d = {
            "exchange_order_id": self.exchange_order_id,
            "client_order_id": self.client_order_id,
            "symbol": self.symbol,
            "side": self.side.value,
            "order_type": self.order_type.value,
            "quantity": self.quantity,
            "limit_price": self.limit_price,
            "status": self.status.value,
            "filled_quantity": self.filled_quantity,
            "avg_fill_price": self.avg_fill_price,
            "cumulative_fee": self.cumulative_fee,
            "timestamp_utc": self.timestamp_utc,
            "simulated": self.simulated,
            "real_exchange_interaction": self.real_exchange_interaction,
            "metadata": dict(self.metadata),
        }
        if self.reject_reason:
            d["reject_reason"] = self.reject_reason.value
        if self.reject_message:
            d["reject_message"] = self.reject_message
        return d


class ExchangeAdapter(ABC):
    """Abstract exchange adapter interface.

    Implementations must:
    - Never fabricate exchange responses when real_exchange_interaction=True
    - Label all paper/simulated responses with simulated=True, real_exchange_interaction=False
    - Record capability probes and blocked routes honestly
    """

    def __init__(
        self,
        *,
        mode: AdapterMode = AdapterMode.PAPER,
        credentials: ExchangeCredentials | None = None,
        base_url: str | None = None,
        testnet_base_url: str | None = None,
        live_base_url: str | None = None,
        request_timeout_s: float = 10.0,
        enable_rate_limit_handling: bool = True,
    ):
        self.mode = mode
        self.credentials = credentials
        self.base_url = base_url
        self.testnet_base_url = testnet_base_url or "https://testnet.binance.vision"
        self.live_base_url = live_base_url or "https://api.binance.com"
        self.request_timeout_s = request_timeout_s
        self.enable_rate_limit_handling = enable_rate_limit_handling
        self.capability_probes: list[CapabilityProbe] = []
        self.blocked_routes: list[dict[str, Any]] = []
        self._record_initial_state()

    def _record_initial_state(self) -> None:
        if self.mode == AdapterMode.PAPER:
            self.blocked_routes.append({
                "route": "live_exchange_order_submission",
                "status": "blocked_fail_closed",
                "reason": "Adapter mode is PAPER; live/testnet order submission disabled",
                "credentials_present": self.credentials.to_dict_safe()["values_present"] if self.credentials else {},
            })
            self.blocked_routes.append({
                "route": "exchange_authenticated_api",
                "status": "blocked",
                "reason": "Paper mode does not contact real exchange APIs",
            })

    @abstractmethod
    def submit_order(self, intent: OrderIntent) -> OrderAck:
        """Submit order to exchange (or paper simulation)."""
        ...

    @abstractmethod
    def cancel_order(self, exchange_order_id: str, symbol: str) -> OrderUpdate:
        """Cancel order on exchange."""
        ...

    @abstractmethod
    def replace_order(
        self,
        exchange_order_id: str,
        symbol: str,
        new_intent: OrderIntent,
    ) -> OrderUpdate:
        """Replace (cancel + new) order on exchange."""
        ...

    @abstractmethod
    def query_order(self, exchange_order_id: str, symbol: str) -> OrderUpdate:
        """Query order status from exchange."""
        ...

    @abstractmethod
    def get_open_orders(self, symbol: str | None = None) -> list[OrderUpdate]:
        """Get all open orders."""
        ...

    @abstractmethod
    def get_account_balances(self) -> dict[str, Any]:
        """Get account balances."""
        ...

    @abstractmethod
    def get_exchange_info(self) -> dict[str, Any]:
        """Get exchange trading rules / symbol info."""
        ...

    def run_capability_probes(self) -> list[CapabilityProbe]:
        """Run capability detection probes and record results."""
        self.capability_probes.clear()

        # Probe 1: DNS resolution for base URLs
        for url_name, url in [
            ("testnet_base_url", self.testnet_base_url),
            ("live_base_url", self.live_base_url),
        ]:
            if url:
                self.capability_probes.append(self._probe_dns(url_name, url))

        # Probe 2: TCP connectivity to endpoints
        for url_name, url in [
            ("testnet_base_url", self.testnet_base_url),
            ("live_base_url", self.live_base_url),
        ]:
            if url:
                self.capability_probes.append(self._probe_tcp_connect(url_name, url))

        # Probe 3: HTTP GET to public endpoint (no auth required)
        for url_name, url in [
            ("testnet_ping", f"{self.testnet_base_url}/api/v3/ping"),
            ("live_ping", f"{self.live_base_url}/api/v3/ping"),
            ("testnet_exchange_info", f"{self.testnet_base_url}/api/v3/exchangeInfo"),
            ("live_exchange_info", f"{self.live_base_url}/api/v3/exchangeInfo"),
        ]:
            if url:
                self.capability_probes.append(self._probe_http_get(url_name, url))

        # Probe 4: Credential presence check
        if self.credentials:
            self.capability_probes.append(self._probe_credentials())

        # Probe 5: Authenticated endpoint test (only if credentials present and mode allows)
        if self.credentials and self.mode in (AdapterMode.TESTNET, AdapterMode.LIVE):
            creds = self.credentials.get_credentials()
            if creds:
                base = self.testnet_base_url if self.mode == AdapterMode.TESTNET else self.live_base_url
                self.capability_probes.append(self._probe_authenticated(base, creds))

        return list(self.capability_probes)

    def _probe_dns(self, name: str, url: str) -> CapabilityProbe:
        from urllib.parse import urlparse
        start = time.perf_counter()
        try:
            host = urlparse(url).hostname or ""
            if not host:
                raise ValueError("no hostname")
            socket.getaddrinfo(host, 443, socket.AF_INET, socket.SOCK_STREAM)
            elapsed = (time.perf_counter() - start) * 1000
            return CapabilityProbe(
                probe_name=f"dns_{name}",
                target=url,
                attempted_at_utc=_utc_now_iso(),
                success=True,
                latency_ms=elapsed,
                details={"hostname": host},
            )
        except Exception as exc:
            elapsed = (time.perf_counter() - start) * 1000
            return CapabilityProbe(
                probe_name=f"dns_{name}",
                target=url,
                attempted_at_utc=_utc_now_iso(),
                success=False,
                latency_ms=elapsed,
                error=str(exc),
                details={"hostname": urlparse(url).hostname if urlparse(url).hostname else "unknown"},
            )

    def _probe_tcp_connect(self, name: str, url: str) -> CapabilityProbe:
        from urllib.parse import urlparse
        start = time.perf_counter()
        try:
            host = urlparse(url).hostname or ""
            port = urlparse(url).port or 443
            sock = socket.create_connection((host, port), timeout=self.request_timeout_s)
            sock.close()
            elapsed = (time.perf_counter() - start) * 1000
            return CapabilityProbe(
                probe_name=f"tcp_{name}",
                target=url,
                attempted_at_utc=_utc_now_iso(),
                success=True,
                latency_ms=elapsed,
                details={"host": host, "port": port},
            )
        except Exception as exc:
            elapsed = (time.perf_counter() - start) * 1000
            return CapabilityProbe(
                probe_name=f"tcp_{name}",
                target=url,
                attempted_at_utc=_utc_now_iso(),
                success=False,
                latency_ms=elapsed,
                error=str(exc),
                details={"host": urlparse(url).hostname if urlparse(url).hostname else "unknown"},
            )

    def _probe_http_get(self, name: str, url: str) -> CapabilityProbe:
        import urllib.request
        start = time.perf_counter()
        try:
            req = urllib.request.Request(url, method="GET")
            req.add_header("User-Agent", "cryptoquantstatarbstrats-capability-probe/1.0")
            with urllib.request.urlopen(req, timeout=self.request_timeout_s) as resp:
                _ = resp.read()
                elapsed = (time.perf_counter() - start) * 1000
                return CapabilityProbe(
                    probe_name=f"http_{name}",
                    target=url,
                    attempted_at_utc=_utc_now_iso(),
                    success=True,
                    latency_ms=elapsed,
                    details={"status_code": resp.status},
                )
        except Exception as exc:
            elapsed = (time.perf_counter() - start) * 1000
            return CapabilityProbe(
                probe_name=f"http_{name}",
                target=url,
                attempted_at_utc=_utc_now_iso(),
                success=False,
                latency_ms=elapsed,
                error=str(exc),
            )

    def _probe_credentials(self) -> CapabilityProbe:
        assert self.credentials is not None
        presence = self.credentials._check_presence()
        all_present = all(presence.values())
        return CapabilityProbe(
            probe_name="credentials_presence",
            target=f"env_vars:{self.credentials.api_key_env_var},{self.credentials.api_secret_env_var},{self.credentials.passphrase_env_var or 'none'}",
            attempted_at_utc=_utc_now_iso(),
            success=all_present,
            details={"presence": presence, "testnet": self.credentials.testnet},
        )

    def _probe_authenticated(self, base_url: str, creds: dict[str, str]) -> CapabilityProbe:
        import hashlib
        import hmac
        import urllib.parse
        import urllib.request
        start = time.perf_counter()
        try:
            endpoint = "/api/v3/account"
            timestamp = str(int(time.time() * 1000))
            params = f"timestamp={timestamp}"
            query_string = params
            signature = hmac.new(
                creds["api_secret"].encode(),
                query_string.encode(),
                hashlib.sha256,
            ).hexdigest()
            url = f"{base_url}{endpoint}?{params}&signature={signature}"
            req = urllib.request.Request(url, method="GET")
            req.add_header("X-MBX-APIKEY", creds["api_key"])
            req.add_header("User-Agent", "cryptoquantstatarbstrats-capability-probe/1.0")
            with urllib.request.urlopen(req, timeout=self.request_timeout_s) as resp:
                _ = resp.read()
                elapsed = (time.perf_counter() - start) * 1000
                return CapabilityProbe(
                    probe_name="authenticated_account",
                    target=f"{base_url}{endpoint}",
                    attempted_at_utc=_utc_now_iso(),
                    success=True,
                    latency_ms=elapsed,
                    details={"status_code": resp.status},
                )
        except Exception as exc:
            elapsed = (time.perf_counter() - start) * 1000
            return CapabilityProbe(
                probe_name="authenticated_account",
                target=f"{base_url}/api/v3/account",
                attempted_at_utc=_utc_now_iso(),
                success=False,
                latency_ms=elapsed,
                error=str(exc),
            )

    def get_capability_summary(self) -> dict[str, Any]:
        """Get summary of capability probes for artifact emission."""
        probes = [p.to_dict() for p in self.capability_probes]
        blocked = list(self.blocked_routes)
        return {
            "mode": self.mode.value,
            "probes": probes,
            "blocked_routes": blocked,
            "credentials_config": self.credentials.to_dict_safe() if self.credentials else None,
            "environment": {
                "testnet_base_url": self.testnet_base_url,
                "live_base_url": self.live_base_url,
                "request_timeout_s": self.request_timeout_s,
            },
        }


class PaperExchangeAdapter(ExchangeAdapter):
    """Paper/simulated exchange adapter (default mode).

    Simulates order lifecycle with deterministic behavior.
    All responses are labeled simulated=True, real_exchange_interaction=False.
    """

    def __init__(
        self,
        *,
        fee_rate: float = 0.001,
        slippage_bps: float = 5.0,
        fill_latency_ms: float = 10.0,
        partial_fill_prob: float = 0.0,
        reject_prob: float = 0.0,
        **kwargs: Any,
    ):
        kwargs.setdefault("mode", AdapterMode.PAPER)
        super().__init__(**kwargs)
        if not _is_finite_number(fee_rate) or fee_rate < 0:
            raise ValueError("fee_rate must be finite and >= 0")
        if not _is_finite_number(slippage_bps) or slippage_bps < 0:
            raise ValueError("slippage_bps must be finite and >= 0")
        self.fee_rate = float(fee_rate)
        self.slippage_bps = float(slippage_bps)
        self.fill_latency_ms = float(fill_latency_ms)
        self.partial_fill_prob = float(partial_fill_prob)
        self.reject_prob = float(reject_prob)
        self._orders: dict[str, OrderUpdate] = {}
        self._fills: list[Fill] = []
        self._seq = 0

    def _next_exchange_order_id(self) -> str:
        self._seq += 1
        return f"paper-ord-{self._seq}"

    def _next_trade_id(self) -> str:
        return f"paper-trade-{uuid.uuid4().hex[:12]}"

    def submit_order(self, intent: OrderIntent) -> OrderAck:
        norm = intent.normalized()
        norm.validate()

        # Simulate rejection probability
        import random
        if random.random() < self.reject_prob:
            ack = OrderAck(
                exchange_order_id=self._next_exchange_order_id(),
                client_order_id=norm.client_order_id or "",
                symbol=norm.symbol,
                side=norm.side,
                order_type=norm.order_type,
                quantity=norm.quantity,
                limit_price=norm.limit_price,
                status=OrderStatus.REJECTED,
                timestamp_utc=_utc_now_iso(),
                simulated=True,
                real_exchange_interaction=False,
                metadata={
                    "reject_reason": "simulated_rejection",
                    "simulated_execution_model": "paper_probabilistic_reject",
                },
            )
            self._orders[ack.exchange_order_id] = OrderUpdate(
                exchange_order_id=ack.exchange_order_id,
                client_order_id=ack.client_order_id,
                symbol=ack.symbol,
                side=ack.side,
                order_type=ack.order_type,
                quantity=ack.quantity,
                limit_price=ack.limit_price,
                status=ack.status,
                filled_quantity=0.0,
                avg_fill_price=0.0,
                cumulative_fee=0.0,
                timestamp_utc=ack.timestamp_utc,
                reject_reason=RejectReason.INTERNAL_ERROR,
                reject_message="Simulated rejection",
                simulated=True,
                real_exchange_interaction=False,
            )
            return ack

        ack = OrderAck(
            exchange_order_id=self._next_exchange_order_id(),
            client_order_id=norm.client_order_id or "",
            symbol=norm.symbol,
            side=norm.side,
            order_type=norm.order_type,
            quantity=norm.quantity,
            limit_price=norm.limit_price,
            status=OrderStatus.ACKNOWLEDGED,
            timestamp_utc=_utc_now_iso(),
            simulated=True,
            real_exchange_interaction=False,
            metadata={
                "simulated_execution_model": "paper_deterministic",
                "fee_rate": self.fee_rate,
                "slippage_bps": self.slippage_bps,
            },
        )
        self._orders[ack.exchange_order_id] = OrderUpdate(
            exchange_order_id=ack.exchange_order_id,
            client_order_id=ack.client_order_id,
            symbol=ack.symbol,
            side=ack.side,
            order_type=ack.order_type,
            quantity=ack.quantity,
            limit_price=ack.limit_price,
            status=ack.status,
            filled_quantity=0.0,
            avg_fill_price=0.0,
            cumulative_fee=0.0,
            timestamp_utc=ack.timestamp_utc,
            simulated=True,
            real_exchange_interaction=False,
        )
        return ack

    def cancel_order(self, exchange_order_id: str, symbol: str) -> OrderUpdate:
        order = self._orders.get(exchange_order_id)
        if order is None:
            return OrderUpdate(
                exchange_order_id=exchange_order_id,
                client_order_id="",
                symbol=symbol,
                side=OrderSide.BUY,
                order_type=OrderType.MARKET,
                quantity=0.0,
                limit_price=None,
                status=OrderStatus.REJECTED,
                filled_quantity=0.0,
                avg_fill_price=0.0,
                cumulative_fee=0.0,
                timestamp_utc=_utc_now_iso(),
                reject_reason=RejectReason.NOT_FOUND,
                reject_message="Order not found",
                simulated=True,
                real_exchange_interaction=False,
            )
        if order.status in {OrderStatus.FILLED, OrderStatus.CANCELED, OrderStatus.REJECTED, OrderStatus.EXPIRED}:
            return OrderUpdate(
                **order.__dict__,
                status=OrderStatus.REJECTED,
                reject_reason=RejectReason.INVALID_INPUT,
                reject_message=f"Cannot cancel order in status {order.status.value}",
                simulated=True,
                real_exchange_interaction=False,
            )
        order.status = OrderStatus.CANCELED
        order.timestamp_utc = _utc_now_iso()
        order.metadata["cancel_reason"] = "user_requested"
        return order

    def replace_order(
        self,
        exchange_order_id: str,
        symbol: str,
        new_intent: OrderIntent,
    ) -> OrderUpdate:
        canceled = self.cancel_order(exchange_order_id, symbol)
        if canceled.status == OrderStatus.CANCELED:
            new_ack = self.submit_order(new_intent)
            new_ack.metadata["replaces_order_id"] = exchange_order_id
            return self._orders[new_ack.exchange_order_id]
        return canceled

    def query_order(self, exchange_order_id: str, symbol: str) -> OrderUpdate:
        order = self._orders.get(exchange_order_id)
        if order is None:
            return OrderUpdate(
                exchange_order_id=exchange_order_id,
                client_order_id="",
                symbol=symbol,
                side=OrderSide.BUY,
                order_type=OrderType.MARKET,
                quantity=0.0,
                limit_price=None,
                status=OrderStatus.REJECTED,
                filled_quantity=0.0,
                avg_fill_price=0.0,
                cumulative_fee=0.0,
                timestamp_utc=_utc_now_iso(),
                reject_reason=RejectReason.NOT_FOUND,
                reject_message="Order not found",
                simulated=True,
                real_exchange_interaction=False,
            )
        return order

    def get_open_orders(self, symbol: str | None = None) -> list[OrderUpdate]:
        open_statuses = {OrderStatus.NEW, OrderStatus.SUBMITTED, OrderStatus.ACKNOWLEDGED, OrderStatus.PARTIALLY_FILLED}
        result = [
            o for o in self._orders.values()
            if o.status in open_statuses and (symbol is None or o.symbol == symbol)
        ]
        return result

    def get_account_balances(self) -> dict[str, Any]:
        return {
            "simulated": True,
            "real_exchange_interaction": False,
            "balances": {},
            "timestamp_utc": _utc_now_iso(),
        }

    def get_exchange_info(self) -> dict[str, Any]:
        return {
            "simulated": True,
            "real_exchange_interaction": False,
            "symbols": [],
            "timestamp_utc": _utc_now_iso(),
        }

    def simulate_fill(
        self,
        exchange_order_id: str,
        market_price: float,
        *,
        force_full: bool = False,
    ) -> list[Fill]:
        """Simulate fill for a paper order (for testing/lifecycle validation)."""
        import random
        order = self._orders.get(exchange_order_id)
        if order is None or order.status not in {OrderStatus.ACKNOWLEDGED, OrderStatus.PARTIALLY_FILLED}:
            return []

        # For limit orders, check if market crosses limit price
        if order.order_type == OrderType.LIMIT and order.limit_price is not None:
            limit_price = float(order.limit_price)
            if order.side == OrderSide.BUY and market_price > limit_price:
                return []  # Buy limit not crossed (market above limit)
            if order.side == OrderSide.SELL and market_price < limit_price:
                return []  # Sell limit not crossed (market below limit)

        remaining = order.quantity - order.filled_quantity
        if remaining <= 1e-12:
            return []

        if force_full or random.random() >= self.partial_fill_prob:
            fill_qty = remaining
        else:
            fill_qty = remaining * random.uniform(0.1, 0.9)

        slip = self.slippage_bps / 10000.0
        fill_price = market_price * (1.0 + slip) if order.side == OrderSide.BUY else market_price * (1.0 - slip)
        fee = fill_qty * fill_price * self.fee_rate

        fill = Fill(
            exchange_order_id=exchange_order_id,
            client_order_id=order.client_order_id,
            symbol=order.symbol,
            side=order.side,
            quantity=fill_qty,
            price=fill_price,
            fee=fee,
            fee_asset="USDT",
            timestamp_utc=_utc_now_iso(),
            trade_id=self._next_trade_id(),
            simulated=True,
            real_exchange_fill=False,
            execution_environment="paper",
            metadata={
                "market_price": market_price,
                "slippage_bps": self.slippage_bps,
                "simulated_execution_model": "paper_deterministic_slippage_fee",
            },
        )
        self._fills.append(fill)

        order.filled_quantity += fill_qty
        prev_notional = order.avg_fill_price * (order.filled_quantity - fill_qty)
        order.avg_fill_price = (prev_notional + fill_qty * fill_price) / order.filled_quantity
        order.cumulative_fee += fee
        order.timestamp_utc = _utc_now_iso()

        if order.filled_quantity >= order.quantity - 1e-9:
            order.status = OrderStatus.FILLED
        else:
            order.status = OrderStatus.PARTIALLY_FILLED

        return [fill]


class SimulatedTestnetAdapter(PaperExchangeAdapter):
    """Simulated testnet adapter for when real testnet credentials are unavailable.

    Provides the same interface as a real testnet adapter but with explicit
    simulated=True labels and honest capability probe recordings showing
    that authenticated testnet access was not available.
    """

    def __init__(self, *, credentials: ExchangeCredentials | None = None, **kwargs: Any):
        kwargs.setdefault("mode", AdapterMode.TESTNET)
        kwargs.setdefault("fill_latency_ms", 50.0)  # Simulate higher testnet latency
        super().__init__(credentials=credentials, **kwargs)
        # Record that this is a simulated testnet adapter
        self.blocked_routes.append({
            "route": "authenticated_testnet_api",
            "status": "simulated",
            "reason": "Testnet credentials not available or not capability-verified; using simulated testnet adapter",
            "credentials_present": credentials.to_dict_safe()["values_present"] if credentials else {},
        })


def create_adapter_from_env() -> ExchangeAdapter:
    """Factory to create appropriate adapter based on environment variables.

    Environment variables (all optional, never assumed):
    - BINANCE_TESTNET_API_KEY, BINANCE_TESTNET_API_SECRET
    - BINANCE_LIVE_API_KEY, BINANCE_LIVE_API_SECRET
    - ADAPTER_MODE: "paper" | "testnet" | "live" (default: "paper")
    """
    import os
    mode_str = os.environ.get("ADAPTER_MODE", "paper").lower()
    try:
        mode = AdapterMode(mode_str)
    except ValueError:
        mode = AdapterMode.PAPER

    if mode == AdapterMode.TESTNET:
        creds = ExchangeCredentials(
            api_key_env_var="BINANCE_TESTNET_API_KEY",
            api_secret_env_var="BINANCE_TESTNET_API_SECRET",
            testnet=True,
        )
        if creds.get_credentials():
            # Real testnet credentials present - would use real adapter if implemented
            # For now, fall back to simulated with credential acknowledgment
            return SimulatedTestnetAdapter(credentials=creds)
        return SimulatedTestnetAdapter(credentials=creds)

    if mode == AdapterMode.LIVE:
        creds = ExchangeCredentials(
            api_key_env_var="BINANCE_LIVE_API_KEY",
            api_secret_env_var="BINANCE_LIVE_API_SECRET",
            testnet=False,
        )
        # Live mode without real credentials = blocked
        return PaperExchangeAdapter(mode=AdapterMode.PAPER)

    return PaperExchangeAdapter()
