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
class IcebergExecution:
    """Iceberg order execution model.

    Only a visible portion (``visible_qty`` / ``display_qty``) is exposed at a
    time; when that slice is filled, another is replenished until the full order
    quantity is complete.
    """

    visible_qty: float = 1.0
    display_qty: float | None = None
    min_fill: float = 0.0
    price_offset_bps: float = 0.0
    price_offset: float | None = None
    price_offset_absolute: float = 0.0
    time_in_force: str = "day"
    participation_rate: float = 0.1
    slippage_bps: float = 0.0

    def __post_init__(self) -> None:
        if self.display_qty is None:
            self.display_qty = self.visible_qty
        else:
            self.visible_qty = self.display_qty
        if self.price_offset is not None:
            try:
                self.price_offset_absolute = float(self.price_offset)
            except (TypeError, ValueError):
                pass
        try:
            v = float(self.visible_qty) if self.visible_qty is not None else 1.0
            if not np.isfinite(v) or v <= 0.0:
                self.visible_qty = 1.0
            else:
                self.visible_qty = v
        except (TypeError, ValueError):
            self.visible_qty = 1.0


@dataclass
class MarketExecution:
    participation_rate: float = 0.1
    slippage_bps: float = 0.0


@dataclass
class LimitExecution:
    participation_rate: float = 0.1
    slippage_bps: float = 0.0


@dataclass
class VWAPExecution:
    participation_rate: float = 0.1
    slippage_bps: float = 0.0


@dataclass
class TWAPExecution:
    participation_rate: float = 0.1
    slippage_bps: float = 0.0


@dataclass
class ExecutionSimulator:
    """Simulate order execution with volume participation limits."""

    participation_rate: float = 0.1
    slippage_bps: float = 0.0
    order_type: str = "market"
    iceberg_visible_qty: float = 1.0
    iceberg_min_fill: float = 0.0
    iceberg_price_offset_bps: float = 0.0
    iceberg_price_offset_absolute: float = 0.0
    iceberg_time_in_force: str = "day"
    _fills: list[dict[str, Any]] = field(default_factory=list, repr=False)
    _iceberg: IcebergExecution | None = field(default=None, repr=False)

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
        if order_type not in ("market", "limit", "vwap", "twap", "iceberg"):
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
                return {"filled_qty": 0.0, "avg_price": 0.0,
                        "status": "unfilled", "remaining_qty": qty}
            if side == "sell" and px < lp:
                return {"filled_qty": 0.0, "avg_price": 0.0,
                        "status": "unfilled", "remaining_qty": qty}

        if order_type == "iceberg":
            return self._simulate_iceberg(
                side, qty, px, bar_volume, bar_high, bar_low
            )

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

        # Base fill price depends on order type
        if order_type == "vwap":
            try:
                hi = float(bar_high) if bar_high is not None else px
                lo = float(bar_low) if bar_low is not None else px
            except (TypeError, ValueError):
                hi, lo = px, px
            base_price = (hi + lo + px) / 3.0
        elif order_type == "twap":
            try:
                hi = float(bar_high) if bar_high is not None else px
                lo = float(bar_low) if bar_low is not None else px
            except (TypeError, ValueError):
                hi, lo = px, px
            base_price = (hi + lo) / 2.0
        else:
            base_price = px

        # Slippage
        slip = self.slippage_bps / 10000.0
        if side == "buy":
            fill_price = base_price * (1.0 + slip)
        else:
            fill_price = base_price * (1.0 - slip)

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

    def _simulate_iceberg(
        self,
        side: str,
        qty: float,
        price: float,
        bar_volume: float = 0.0,
        bar_high: float | None = None,
        bar_low: float | None = None,
    ) -> dict[str, Any]:
        try:
            q = float(qty)
        except (TypeError, ValueError):
            q = 0.0
        if not np.isfinite(q) or abs(q) == 0.0:
            return {"filled_qty": 0.0, "avg_price": 0.0, "status": "rejected", "remaining_qty": qty}

        iceberg = self._iceberg
        visible_qty = float(
            getattr(iceberg, "visible_qty", None)
            or getattr(iceberg, "display_qty", None)
            or self.iceberg_visible_qty
            or 1.0
        )
        try:
            if not np.isfinite(visible_qty) or visible_qty <= 0.0:
                visible_qty = 1.0
        except Exception:
            visible_qty = 1.0

        min_fill = float(getattr(iceberg, "min_fill", self.iceberg_min_fill) or 0.0)
        try:
            if not np.isfinite(min_fill) or min_fill < 0.0:
                min_fill = 0.0
        except Exception:
            min_fill = 0.0

        price_offset_bps = float(
            getattr(iceberg, "price_offset_bps", self.iceberg_price_offset_bps)
            or 0.0
        )
        price_offset_abs = float(
            getattr(
                iceberg,
                "price_offset_absolute",
                getattr(iceberg, "price_offset", self.iceberg_price_offset_absolute),
            )
            or 0.0
        )
        try:
            if not np.isfinite(price_offset_bps):
                price_offset_bps = 0.0
            if not np.isfinite(price_offset_abs):
                price_offset_abs = 0.0
        except Exception:
            price_offset_bps = 0.0
            price_offset_abs = 0.0

        try:
            vol = float(bar_volume) if bar_volume is not None else 0.0
        except (TypeError, ValueError):
            vol = 0.0
        if not np.isfinite(vol) or vol <= 0.0:
            max_fill_total = abs(q)
        else:
            cap = self._valid_rate() * vol
            max_fill_total = min(abs(q), cap) if cap > 0 else abs(q)

        fillable = min(abs(q), max_fill_total)
        if fillable <= 0.0:
            fillable = 0.0

        if fillable < abs(q) - 1e-12:
            if min_fill > 0.0 and fillable < min_fill - 1e-12:
                return {
                    "filled_qty": 0.0,
                    "avg_price": 0.0,
                    "status": "unfilled",
                    "remaining_qty": q,
                }
        elif fillable >= abs(q) - 1e-12:
            fillable = abs(q)
        else:
            if min_fill > 0.0 and fillable < min_fill - 1e-12 and fillable < abs(q) - 1e-12:
                return {
                    "filled_qty": 0.0,
                    "avg_price": 0.0,
                    "status": "unfilled",
                    "remaining_qty": q,
                }

        if fillable <= 0.0:
            return {"filled_qty": 0.0, "avg_price": 0.0, "status": "unfilled", "remaining_qty": q}

        if self.order_type == "vwap":
            try:
                hi = float(bar_high) if bar_high is not None else price
                lo = float(bar_low) if bar_low is not None else price
            except (TypeError, ValueError):
                hi, lo = price, price
            base_price = (hi + lo + price) / 3.0
        elif self.order_type == "twap":
            try:
                hi = float(bar_high) if bar_high is not None else price
                lo = float(bar_low) if bar_low is not None else price
            except (TypeError, ValueError):
                hi, lo = price, price
            base_price = (hi + lo) / 2.0
        else:
            base_price = price

        base_price = base_price + price_offset_abs
        if price_offset_bps != 0.0:
            base_price = base_price * (1.0 + price_offset_bps / 10000.0)

        slip = self.slippage_bps / 10000.0
        if side == "buy":
            fill_price = base_price * (1.0 + slip)
        else:
            fill_price = base_price * (1.0 - slip)

        if fillable < abs(q) - 1e-12:
            status = "partial"
        else:
            status = "filled"

        signed_filled = fillable if side == "buy" else -fillable
        result = {
            "filled_qty": signed_filled,
            "avg_price": float(fill_price),
            "status": status,
            "remaining_qty": q - signed_filled,
        }
        self._fills.append({"order_type": "iceberg", "side": side, **result})
        return result

    def fills(self) -> list[dict[str, Any]]:
        return list(self._fills)

    def reset(self) -> None:
        self._fills.clear()
