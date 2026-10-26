"""Execution simulation utilities.

Provides an :class:`ExecutionSimulator` that models market/limit orders with
partial fills and volume participation constraints. Intended to be plugged into
the backtesting engine for more realistic fill simulation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass
class ExecutionSimulator:
    """Simulate order execution with volume participation limits.

    Attributes:
        participation_rate: Maximum fraction of bar volume a single order may
            consume (0 < rate <= 1).
        slippage_bps: Additional slippage in basis points applied to fills.
    """

    participation_rate: float = 0.1
    slippage_bps: float = 0.0
    _fills: list[dict[str, Any]] = field(default_factory=list, repr=False)

    def _valid_rate(self) -> float:
        try:
            r = float(self.participation_rate)
        except (TypeError, ValueError):
            return 0.1
        if not np.isfinite(r) or r <= 0.0:
            return 0.1
        return min(r, 1.0)

    def simulate_order(
        self,
        order_type: str,
        side: str,
        quantity: float,
        price: float,
        bar_volume: float = 0.0,
        bar_high: float | None = None,
        bar_low: float | None = None,
        limit_price: float | None = None,
    ) -> dict[str, Any]:
        """Simulate a single order.

        Returns a dict with ``filled_qty``, ``avg_price``, ``status`` and
        ``remaining_qty``.
        """
        try:
            qty = float(quantity)
            px = float(price)
        except (TypeError, ValueError):
            return {"filled_qty": 0.0, "avg_price": 0.0, "status": "rejected", "remaining_qty": 0.0}

        if not np.isfinite(qty) or not np.isfinite(px) or qty == 0.0 or px <= 0.0:
            return {"filled_qty": 0.0, "avg_price": 0.0, "status": "rejected", "remaining_qty": qty}

        side = str(side).lower()
        if side not in ("buy", "sell"):
            return {"filled_qty": 0.0, "avg_price": 0.0, "status": "rejected", "remaining_qty": qty}

        order_type = str(order_type).lower()
        if order_type not in ("market", "limit"):
            return {"filled_qty": 0.0, "avg_price": 0.0, "status": "rejected", "remaining_qty": qty}

        # Limit price eligibility
        if order_type == "limit":
            lp = limit_price if limit_price is not None else price
            try:
                lp = float(lp)
            except (TypeError, ValueError):
                return {"filled_qty": 0.0, "avg_price": 0.0,
                        "status": "rejected", "remaining_qty": qty}
            if side == "buy" and px > lp:
                # market price above limit -> no fill
                return {"filled_qty": 0.0, "avg_price": 0.0,
                        "status": "unfilled", "remaining_qty": qty}
            if side == "sell" and px < lp:
                return {"filled_qty": 0.0, "avg_price": 0.0,
                        "status": "unfilled", "remaining_qty": qty}

        # Volume participation cap
        try:
            vol = float(bar_volume) if bar_volume is not None else 0.0
        except (TypeError, ValueError):
            vol = 0.0
        if not np.isfinite(vol) or vol <= 0.0:
            max_fill = abs(qty)
        else:
            cap = self._valid_rate() * vol
            max_fill = min(abs(qty), cap) if cap > 0 else abs(qty)

        filled = min(abs(qty), max_fill) if max_fill > 0 else abs(qty)
        if filled <= 0.0:
            filled = 0.0

        # Slippage
        slip = self.slippage_bps / 10000.0
        if side == "buy":
            fill_price = px * (1.0 + slip)
        else:
            fill_price = px * (1.0 - slip)

        # Partial fill determination
        if filled < abs(qty) - 1e-12:
            status = "partial"
        else:
            status = "filled"

        signed_filled = filled if side == "buy" else -filled
        result = {
            "filled_qty": signed_filled,
            "avg_price": float(fill_price),
            "status": status,
            "remaining_qty": qty - signed_filled,
        }
        self._fills.append({"order_type": order_type, "side": side, **result})
        return result

    def fills(self) -> list[dict[str, Any]]:
        return list(self._fills)

    def reset(self) -> None:
        self._fills.clear()
