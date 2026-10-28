"""Execution simulation utilities.

Provides an :class:`ExecutionSimulator` that models market/limit orders with
partial fills and volume participation constraints. Intended to be plugged into
the backtesting engine for more realistic fill simulation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, cast

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
class LimitOrderBookExecution:
    """Limit order book (LOB) execution model.

    Walks ``depth_levels`` price levels away from the mid price, consuming
    quantity at each level and applying ``market_impact_bps`` per level walked.
    A buy order walks the ask side (prices rise); a sell order walks the bid
    side (prices fall). Partial fills occur when volume participation caps the
    fillable quantity before the order is complete.
    """

    depth_levels: int = 3
    market_impact_bps: float = 5.0
    slippage_bps: float = 0.0
    participation_rate: float = 0.1
    level_liquidity: list[float] | None = None
    queue_position: float = 0.0

    def __post_init__(self) -> None:
        try:
            d = int(self.depth_levels)
            self.depth_levels = d if d > 0 else 1
        except (TypeError, ValueError):
            self.depth_levels = 1
        try:
            m = float(self.market_impact_bps)
            self.market_impact_bps = m if np.isfinite(m) and m >= 0.0 else 0.0
        except (TypeError, ValueError):
            self.market_impact_bps = 0.0
        try:
            s = float(self.slippage_bps)
            self.slippage_bps = s if np.isfinite(s) else 0.0
        except (TypeError, ValueError):
            self.slippage_bps = 0.0
        try:
            p = float(self.participation_rate)
            self.participation_rate = p if np.isfinite(p) and p > 0.0 else 0.1
        except (TypeError, ValueError):
            self.participation_rate = 0.1
        try:
            qp = float(self.queue_position)
            if np.isfinite(qp):
                self.queue_position = min(max(qp, 0.0), 1.0)
            else:
                self.queue_position = 0.0
        except (TypeError, ValueError):
            self.queue_position = 0.0


@dataclass
class Order:
    """Represents an order in the order management system."""

    order_id: Any
    symbol: str
    side: str  # 'buy' or 'sell'
    quantity: float
    order_type: str = "market"
    limit_price: float | None = None
    timestamp: Any = None
    status: str = "open"  # open, filled, partial, cancelled, rejected
    filled_qty: float = 0.0
    avg_fill_price: float = 0.0
    fee_rate: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Position:
    """Represents a position in a symbol."""

    symbol: str
    quantity: float = 0.0  # positive = long, negative = short
    avg_cost: float = 0.0
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    last_price: float = 0.0

    def market_value(self) -> float:
        return self.quantity * self.last_price

    def update_price(self, price: float) -> None:
        self.last_price = float(price)
        if self.quantity != 0.0 and self.avg_cost != 0.0:
            self.unrealized_pnl = self.quantity * (self.last_price - self.avg_cost)
        else:
            self.unrealized_pnl = 0.0


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
    lob_depth_levels: int = 3
    lob_market_impact_bps: float = 5.0
    lob_slippage_bps: float = 0.0
    lob_level_liquidity: list[float] | None = None
    lob_queue_position: float = 0.0
    _fills: list[dict[str, Any]] = field(default_factory=list, repr=False)
    _iceberg: IcebergExecution | None = field(default=None, repr=False)
    _lob: LimitOrderBookExecution | None = field(default=None, repr=False)
    _orders: dict[Any, Order] = field(default_factory=dict, repr=False)
    _positions: dict[str, Position] = field(default_factory=dict, repr=False)
    _order_counter: int = field(default=0, repr=False)

    def __post_init__(self) -> None:
        try:
            d = int(self.lob_depth_levels)
            self.lob_depth_levels = d if d > 0 else 1
        except (TypeError, ValueError):
            self.lob_depth_levels = 1
        try:
            m = float(self.lob_market_impact_bps)
            self.lob_market_impact_bps = m if np.isfinite(m) and m >= 0.0 else 0.0
        except (TypeError, ValueError):
            self.lob_market_impact_bps = 0.0
        try:
            s = float(self.lob_slippage_bps)
            self.lob_slippage_bps = s if np.isfinite(s) else 0.0
        except (TypeError, ValueError):
            self.lob_slippage_bps = 0.0
        # Keep limit order book object in sync if parameters change
        self._lob = LimitOrderBookExecution(
            depth_levels=self.lob_depth_levels,
            market_impact_bps=self.lob_market_impact_bps,
            slippage_bps=self.lob_slippage_bps,
            participation_rate=self.participation_rate,
            level_liquidity=self.lob_level_liquidity,
            queue_position=self.lob_queue_position,
        )

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
        order_id: Any = None,
        symbol: Any = None,
        timestamp: Any = None,
        fee_rate: float = 0.0,
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
        if order_type not in ("market", "limit", "vwap", "twap", "iceberg", "lob"):
            return {"filled_qty": 0.0, "avg_price": 0.0, "status": "rejected", "remaining_qty": qty}

        # Limit price eligibility
        if order_type == "limit":
            lp = limit_price if limit_price is not None else price
            try:
                lp = float(lp)
            except (TypeError, ValueError):
                return {
                    "filled_qty": 0.0,
                    "avg_price": 0.0,
                    "status": "rejected",
                    "remaining_qty": qty,
                }
            if side == "buy" and px > lp:
                return {
                    "filled_qty": 0.0,
                    "avg_price": 0.0,
                    "status": "unfilled",
                    "remaining_qty": qty,
                }
            if side == "sell" and px < lp:
                return {
                    "filled_qty": 0.0,
                    "avg_price": 0.0,
                    "status": "unfilled",
                    "remaining_qty": qty,
                }

        if order_type == "iceberg":
            return self._simulate_iceberg(
                side,
                qty,
                px,
                bar_volume,
                bar_high,
                bar_low,
                order_id=order_id,
                symbol=symbol,
                timestamp=timestamp,
                fee_rate=fee_rate,
            )

        if order_type == "lob":
            return self._simulate_lob(
                side,
                qty,
                px,
                bar_volume,
                bar_high,
                bar_low,
                order_id=order_id,
                symbol=symbol,
                timestamp=timestamp,
                fee_rate=fee_rate,
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
        self._fills.append(
            {
                "order_id": order_id,
                "symbol": symbol,
                "timestamp": timestamp,
                "fee_rate": fee_rate,
                "order_type": order_type,
                "side": side,
                **result,
                "fee": abs(cast(float, result["filled_qty"]))
                * float(price)
                * float(fee_rate or 0.0),
            }
        )
        return result

    def _simulate_iceberg(
        self,
        side: str,
        qty: float,
        price: float,
        bar_volume: float = 0.0,
        bar_high: float | None = None,
        bar_low: float | None = None,
        order_id: Any = None,
        symbol: Any = None,
        timestamp: Any = None,
        fee_rate: float = 0.0,
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
            getattr(iceberg, "price_offset_bps", self.iceberg_price_offset_bps) or 0.0
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
        self._fills.append(
            {
                "order_id": order_id,
                "symbol": symbol,
                "timestamp": timestamp,
                "fee_rate": fee_rate,
                "order_type": "iceberg",
                "side": side,
                **result,
                "fee": abs(cast(float, result["filled_qty"]))
                * float(price)
                * float(fee_rate or 0.0),
            }
        )
        return result

    def _simulate_lob(
        self,
        side: str,
        qty: float,
        price: float,
        bar_volume: float = 0.0,
        bar_high: float | None = None,
        bar_low: float | None = None,
        order_id: Any = None,
        symbol: Any = None,
        timestamp: Any = None,
        fee_rate: float = 0.0,
    ) -> dict[str, Any]:
        try:
            q = float(qty)
            px = float(price)
        except (TypeError, ValueError):
            return {"filled_qty": 0.0, "avg_price": 0.0, "status": "rejected", "remaining_qty": qty}

        if not np.isfinite(q) or not np.isfinite(px) or abs(q) == 0.0 or px <= 0.0:
            return {"filled_qty": 0.0, "avg_price": 0.0, "status": "rejected", "remaining_qty": qty}

        side = str(side).lower()
        if side not in ("buy", "sell"):
            return {"filled_qty": 0.0, "avg_price": 0.0, "status": "rejected", "remaining_qty": qty}

        lob = self._lob
        depth_levels = int(getattr(lob, "depth_levels", None) or self.lob_depth_levels or 1)
        if depth_levels < 1:
            depth_levels = 1
        market_impact_bps = float(
            getattr(lob, "market_impact_bps", None) or self.lob_market_impact_bps or 0.0
        )
        slippage_bps = float(getattr(lob, "slippage_bps", None) or self.lob_slippage_bps or 0.0)
        participation_rate = float(
            getattr(lob, "participation_rate", None) or self.participation_rate or 0.1
        )

        try:
            if not np.isfinite(market_impact_bps) or market_impact_bps < 0.0:
                market_impact_bps = 0.0
            if not np.isfinite(slippage_bps):
                slippage_bps = 0.0
            if not np.isfinite(participation_rate) or participation_rate <= 0.0:
                participation_rate = 0.1
            else:
                participation_rate = min(participation_rate, 1.0)
        except Exception:
            market_impact_bps = 0.0
            slippage_bps = 0.0
            participation_rate = 0.1

        # Per-level liquidity (enhanced LOB model). Falls back to the
        # volume-proxy logic below when level_liquidity is not provided.
        level_liquidity = getattr(lob, "level_liquidity", None)
        queue_position = float(getattr(lob, "queue_position", 0.0) or 0.0)
        try:
            if not np.isfinite(queue_position) or queue_position < 0.0:
                queue_position = 0.0
            queue_position = min(queue_position, 1.0)
        except Exception:
            queue_position = 0.0

        impact_per_level = market_impact_bps / 10000.0
        abs_q = abs(q)

        if level_liquidity is not None:
            # Enhanced: consume liquidity level-by-level, applying market
            # impact per level walked. Queue position reduces the fillable
            # portion at the first level.
            try:
                liq = [float(x) for x in level_liquidity]
            except (TypeError, ValueError):
                liq = []
            remaining = abs_q
            total_filled = 0.0
            levels_walked = 0
            for level in range(depth_levels):
                if remaining <= 0.0:
                    break
                levels_walked += 1
                level_liq = liq[level] if level < len(liq) else 0.0
                if not np.isfinite(level_liq) or level_liq < 0.0:
                    level_liq = 0.0
                # Queue position penalty: only the portion behind the queue
                # at the first level is fillable.
                if level == 0 and queue_position > 0.0:
                    fillable_at_level = level_liq * (1.0 - queue_position)
                else:
                    fillable_at_level = level_liq
                consume = min(fillable_at_level, remaining)
                if consume > 0.0:
                    total_filled += consume
                    remaining -= consume
            filled = total_filled
        else:
            # Backward-compatible volume-proxy logic.
            try:
                vol = float(bar_volume) if bar_volume is not None else 0.0
            except (TypeError, ValueError):
                vol = 0.0
            if not np.isfinite(vol) or vol <= 0.0:
                max_fill_by_vol = abs_q
            else:
                cap = participation_rate * vol
                max_fill_by_vol = min(abs_q, cap) if cap > 0 else abs_q

            if not np.isfinite(vol) or vol <= 0.0:
                book_total = abs_q * 10.0
            else:
                book_total = participation_rate * vol * depth_levels * 2.0
            max_fill_by_depth = book_total
            if max_fill_by_depth > abs_q * 1000:
                max_fill_by_depth = abs_q

            filled = min(abs_q, max_fill_by_vol)
            if filled > max_fill_by_depth:
                filled = max_fill_by_depth
            if filled <= 0.0:
                filled = 0.0

            if filled < abs_q - 1e-12:
                levels_walked = depth_levels
            else:
                ratio = (filled / abs_q) * depth_levels
                levels_walked = min(depth_levels, max(1, int(np.ceil(ratio))))

        total_impact = impact_per_level * levels_walked

        base_price = px
        if side == "buy":
            # Buy walks ask side - prices rise
            fill_price = base_price * (1.0 + total_impact + slippage_bps / 10000.0)
        else:
            # Sell walks bid side - prices fall
            fill_price = base_price * (1.0 - total_impact - slippage_bps / 10000.0)

        if filled < abs(q) - 1e-12:
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
        self._fills.append(
            {
                "order_id": order_id,
                "symbol": symbol,
                "timestamp": timestamp,
                "fee_rate": fee_rate,
                "order_type": "lob",
                "side": side,
                **result,
                "fee": abs(cast(float, result["filled_qty"]))
                * float(price)
                * float(fee_rate or 0.0),
            }
        )
        return result

    def fills(self) -> list[dict[str, Any]]:
        return list(self._fills)

    def reset(self) -> None:
        self._fills.clear()

    # Order management methods
    def create_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str = "market",
        limit_price: float | None = None,
        timestamp: Any = None,
        fee_rate: float = 0.0,
        order_id: Any = None,
    ) -> Order:
        """Create a new order and add it to the order book."""
        if order_id is None:
            self._order_counter += 1
            order_id = self._order_counter
        side = str(side).lower()
        if side not in ("buy", "sell"):
            raise ValueError("side must be 'buy' or 'sell'")
        order_type = str(order_type).lower()
        order = Order(
            order_id=order_id,
            symbol=str(symbol),
            side=side,
            quantity=float(quantity),
            order_type=order_type,
            limit_price=limit_price,
            timestamp=timestamp,
            status="open",
            fee_rate=float(fee_rate or 0.0),
        )
        self._orders[order_id] = order
        return order

    def submit_order(self, order: Order, **kwargs: Any) -> dict[str, Any]:
        """Submit an order for execution."""
        if order.order_id not in self._orders:
            self._orders[order.order_id] = order
        res = self.simulate_order(
            order.order_type,
            order.side,
            order.quantity,
            kwargs.get("price", order.limit_price or 0.0),
            bar_volume=kwargs.get("bar_volume", 0.0),
            bar_high=kwargs.get("bar_high"),
            bar_low=kwargs.get("bar_low"),
            limit_price=order.limit_price,
            order_id=order.order_id,
            symbol=order.symbol,
            timestamp=order.timestamp,
            fee_rate=order.fee_rate,
        )
        filled_qty = res.get("filled_qty", 0.0)
        # Update order status
        try:
            if res.get("status") == "filled":
                order.status = "filled"
                order.filled_qty = float(filled_qty)
                order.avg_fill_price = float(res.get("avg_price", 0.0))
            elif res.get("status") == "partial":
                order.status = "partial"
                order.filled_qty = float(filled_qty)
                order.avg_fill_price = float(res.get("avg_price", 0.0))
            elif res.get("status") == "rejected":
                order.status = "rejected"
            else:
                order.status = res.get("status", "open")
        except Exception:
            pass
        self._update_position_from_fill(order.symbol, filled_qty, res.get("avg_price", 0.0))
        return res

    def cancel_order(self, order_id: Any) -> bool:
        """Cancel an open order."""
        if order_id in self._orders:
            order = self._orders[order_id]
            if order.status in ("open", "partial"):
                order.status = "cancelled"
                return True
        return False

    def get_order(self, order_id: Any) -> Order | None:
        """Get an order by ID."""
        return self._orders.get(order_id)

    def get_open_orders(self, symbol: str | None = None) -> list[Order]:
        """Get all open orders, optionally filtered by symbol."""
        result = []
        for order in self._orders.values():
            if order.status in ("open", "partial"):
                if symbol is None or order.symbol == symbol:
                    result.append(order)
        return result

    def get_all_orders(self) -> list[Order]:
        """Get all orders."""
        return list(self._orders.values())

    def clear_orders(self) -> None:
        """Clear all orders."""
        self._orders.clear()

    def _update_position_from_fill(self, symbol: str, filled_qty: float, price: float) -> None:
        """Update position based on a fill."""
        if symbol not in self._positions:
            self._positions[symbol] = Position(symbol=symbol)
        pos = self._positions[symbol]
        try:
            fq = float(filled_qty)
            px = float(price)
        except Exception:
            return
        if fq == 0.0:
            return
        # Simple position tracking
        if pos.quantity == 0.0:
            pos.quantity = fq
            pos.avg_cost = px
        else:
            # Update average cost
            new_qty = pos.quantity + fq
            if (pos.quantity > 0 and fq > 0) or (pos.quantity < 0 and fq < 0):
                # Same direction
                total_cost = pos.quantity * pos.avg_cost + fq * px
                pos.avg_cost = total_cost / new_qty if new_qty != 0 else px
            else:
                # Closing or flipping
                if abs(fq) >= abs(pos.quantity):
                    # Flip or close completely
                    pos.avg_cost = px
                else:
                    # Partial close - avg cost remains the same
                    pass
            pos.quantity = new_qty
        pos.last_price = px
        pos.update_price(px)

    def get_position(self, symbol: str) -> Position | None:
        """Get position for a symbol."""
        return self._positions.get(symbol)

    def get_positions(self) -> dict[str, Position]:
        """Get all positions."""
        return dict(self._positions)

    def get_portfolio_value(self, initial_capital: float = 0.0) -> float:
        """Calculate total portfolio value."""
        total = float(initial_capital)
        for pos in self._positions.values():
            total += pos.quantity * pos.last_price
        return total

    def get_realized_pnl(self) -> float:
        """Calculate total realized PnL from fills."""
        total = 0.0
        for fill in self._fills:
            fee = fill.get("fee", 0.0)
            try:
                total -= float(fee)
            except Exception:
                pass
        return total

    def get_unrealized_pnl(self) -> float:
        """Calculate total unrealized PnL."""
        total = 0.0
        for pos in self._positions.values():
            total += float(pos.unrealized_pnl)
        return total

    def get_risk_metrics(self) -> dict[str, Any]:
        """Get portfolio risk metrics."""
        positions = list(self._positions.values())
        long_exposure = sum(p.quantity * p.last_price for p in positions if p.quantity > 0)
        short_exposure = sum(abs(p.quantity) * p.last_price for p in positions if p.quantity < 0)
        net_exposure = long_exposure - short_exposure
        gross_exposure = long_exposure + short_exposure
        return {
            "num_positions": len([p for p in positions if abs(p.quantity) > 1e-9]),
            "long_exposure": long_exposure,
            "short_exposure": short_exposure,
            "net_exposure": net_exposure,
            "gross_exposure": gross_exposure,
            "realized_pnl": self.get_realized_pnl(),
            "unrealized_pnl": self.get_unrealized_pnl(),
        }
