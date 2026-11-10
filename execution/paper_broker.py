"""Paper broker for Campaign #5 production bridge.

Consumes real/public market data (or recorded real candles with provenance) and
simulates fills **only as paper/simulated**. It never contacts a real exchange to
place orders and never labels fills as real exchange fills.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _finite_pos(x: Any) -> bool:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return False
    return math.isfinite(v) and v > 0.0


@dataclass
class PaperFill:
    order_id: str
    client_order_id: str
    symbol: str
    side: str
    quantity: float
    price: float
    fee: float
    timestamp_utc: str
    simulated_fill: bool = True
    paper: bool = True
    real_exchange_fill: bool = False
    execution_environment: str = "paper"
    slippage_bps: float = 0.0
    market_data_source: str = "real_public_or_cached_provenance"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "order_id": self.order_id,
            "client_order_id": self.client_order_id,
            "symbol": self.symbol,
            "side": self.side,
            "quantity": self.quantity,
            "price": self.price,
            "fee": self.fee,
            "timestamp_utc": self.timestamp_utc,
            "simulated_fill": True,
            "paper": True,
            "real_exchange_fill": False,
            "execution_environment": self.execution_environment,
            "slippage_bps": self.slippage_bps,
            "market_data_source": self.market_data_source,
            "metadata": dict(self.metadata),
        }


class PaperBroker:
    """Simple deterministic paper broker.

    - Market orders fill at provided real market price with explicit slippage/fees.
    - Limit buys fill when market <= limit; limit sells fill when market >= limit.
    - All outputs are paper/simulated only.
    - Testnet/live credentials are not required; live order submission is not
      performed. Any attempt to use live mode is fail-closed.
    """

    def __init__(
        self,
        *,
        fee_rate: float = 0.001,
        slippage_bps: float = 5.0,
        execution_environment: str = "paper_public_data",
        allow_live_submission: bool = False,
        testnet_credentials_present: bool = False,
        capability_probe: dict[str, Any] | None = None,
    ):
        if not math.isfinite(float(fee_rate)) or float(fee_rate) < 0.0:
            raise ValueError("fee_rate must be finite and >= 0")
        if not math.isfinite(float(slippage_bps)) or float(slippage_bps) < 0.0:
            raise ValueError("slippage_bps must be finite and >= 0")
        self.fee_rate = float(fee_rate)
        self.slippage_bps = float(slippage_bps)
        self.execution_environment = str(execution_environment)
        self.allow_live_submission = bool(allow_live_submission)
        self.testnet_credentials_present = bool(testnet_credentials_present)
        self.capability_probe = dict(capability_probe or {})
        self.fill_log: list[dict[str, Any]] = []
        self.blocked_routes: list[dict[str, Any]] = []
        self._record_capability_state()

    def _record_capability_state(self) -> None:
        # Fail-closed: no live submission in this campaign implementation.
        if not self.allow_live_submission:
            self.blocked_routes.append(
                {
                    "route": "live_exchange_order_submission",
                    "status": "blocked_fail_closed",
                    "reason": (
                        "live/testnet order submission disabled; "
                        "Campaign #5 uses paper simulation only"
                    ),
                    "credentials_present": self.testnet_credentials_present,
                    "capability_probe": self.capability_probe,
                }
            )
        if self.testnet_credentials_present is False:
            self.blocked_routes.append(
                {
                    "route": "exchange_testnet_authenticated_api",
                    "status": "blocked",
                    "reason": (
                        "testnet/exchange credentials not present in environment; not assumed"
                    ),
                }
            )

    def execute(
        self,
        order: dict[str, Any],
        *,
        market_price: float | None = None,
    ) -> list[dict[str, Any]]:
        if not isinstance(order, dict):
            raise ValueError("order must be a dict")
        symbol = str(order.get("symbol", "")).upper()
        side = str(order.get("side", "")).lower()
        order_type = str(order.get("order_type", "market")).lower()
        qty = order.get("quantity")
        if not symbol or side not in {"buy", "sell"}:
            raise ValueError("invalid order symbol/side")
        if order_type not in {"market", "limit"}:
            raise ValueError("unsupported order_type")
        if not _finite_pos(qty):
            raise ValueError("quantity must be > 0")
        if not _finite_pos(market_price):
            raise ValueError("market_price from real/public data is required for paper execution")
        mpx = float(market_price) if market_price is not None else 0.0
        limit_price = order.get("limit_price")
        if order_type == "limit":
            if not _finite_pos(limit_price):
                raise ValueError("limit_price required for limit orders")
            lpx = float(limit_price) if limit_price is not None else 0.0
            crosses = (side == "buy" and mpx <= lpx) or (side == "sell" and mpx >= lpx)
            if not crosses:
                return []
            ref = lpx
        else:
            ref = mpx
        slip = self.slippage_bps / 10000.0
        fill_price = ref * (1.0 + slip) if side == "buy" else ref * (1.0 - slip)
        if not _finite_pos(fill_price):
            raise ValueError("computed paper fill price invalid")
        qf = float(qty) if qty is not None else 0.0
        fee = qf * fill_price * self.fee_rate
        pf = PaperFill(
            order_id=str(order.get("order_id", "")),
            client_order_id=str(order.get("client_order_id", "")),
            symbol=symbol,
            side=side,
            quantity=qf,
            price=float(fill_price),
            fee=float(fee),
            timestamp_utc=str(order.get("timestamp") or _utc_now_iso()),
            execution_environment=self.execution_environment,
            slippage_bps=self.slippage_bps,
            metadata={
                "market_price": mpx,
                "reference_price": ref,
                "order_type": order_type,
                "simulated_execution_model": "deterministic_slippage_fee_paper",
            },
        )
        out = pf.to_dict()
        self.fill_log.append(out)
        return [out]

    def state(self) -> dict[str, Any]:
        return {
            "execution_environment": self.execution_environment,
            "simulated_fills": True,
            "real_exchange_fills": False,
            "allow_live_submission": self.allow_live_submission,
            "testnet_credentials_present": self.testnet_credentials_present,
            "fee_rate": self.fee_rate,
            "slippage_bps": self.slippage_bps,
            "fill_count": len(self.fill_log),
            "blocked_routes": list(self.blocked_routes),
        }
