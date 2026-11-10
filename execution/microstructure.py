"""Campaign #6: Paper microstructure / latency realism extensions.

This module extends paper execution with configurable latency, queue/partial-fill,
slippage/impact hooks, and data-gap handling — all honest/provenance-labeled.

No fabricated fills, order books, exchange responses, or market data.
All simulations are explicitly labeled with simulated=True, real_exchange_fill=False.
"""

from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _is_finite_number(value: Any) -> bool:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return False
    return v == v and v != float("inf") and v != float("-inf")


@dataclass
class MicrostructureConfig:
    """Configuration for paper microstructure simulation."""

    # Latency simulation (ms)
    base_latency_ms: float = 10.0
    latency_jitter_ms: float = 5.0
    network_latency_distribution: str = "lognormal"  # "fixed" | "normal" | "lognormal" | "exponential"

    # Queue / partial fill simulation
    enable_queue_simulation: bool = True
    partial_fill_probability: float = 0.1
    partial_fill_min_ratio: float = 0.1
    partial_fill_max_ratio: float = 0.9
    queue_position_impact_bps: float = 0.5  # Additional slippage per queue position

    # Slippage / impact hooks
    base_slippage_bps: float = 5.0
    volatility_slippage_multiplier: float = 1.0  # Multiplier based on recent volatility
    impact_model: str = "square_root"  # "linear" | "square_root" | "none"
    impact_coefficient: float = 0.1  # Impact in bps per sqrt(notional/ADV)
    adv_usd: float = 1_000_000.0  # Average daily volume in USD (per symbol)

    # Data gap handling
    enable_data_gap_handling: bool = True
    max_gap_tolerance_bars: int = 5
    gap_fill_strategy: str = "last_known"  # "last_known" | "interpolate" | "skip"

    # Randomization
    random_seed: int | None = None

    def __post_init__(self) -> None:
        if self.random_seed is not None:
            random.seed(self.random_seed)

    def to_dict(self) -> dict[str, Any]:
        return {
            "base_latency_ms": self.base_latency_ms,
            "latency_jitter_ms": self.latency_jitter_ms,
            "network_latency_distribution": self.network_latency_distribution,
            "enable_queue_simulation": self.enable_queue_simulation,
            "partial_fill_probability": self.partial_fill_probability,
            "partial_fill_min_ratio": self.partial_fill_min_ratio,
            "partial_fill_max_ratio": self.partial_fill_max_ratio,
            "queue_position_impact_bps": self.queue_position_impact_bps,
            "base_slippage_bps": self.base_slippage_bps,
            "volatility_slippage_multiplier": self.volatility_slippage_multiplier,
            "impact_model": self.impact_model,
            "impact_coefficient": self.impact_coefficient,
            "adv_usd": self.adv_usd,
            "enable_data_gap_handling": self.enable_data_gap_handling,
            "max_gap_tolerance_bars": self.max_gap_tolerance_bars,
            "gap_fill_strategy": self.gap_fill_strategy,
            "random_seed": self.random_seed,
        }


@dataclass
class LatencySample:
    """Sampled latency breakdown."""
    base_ms: float
    jitter_ms: float
    total_ms: float
    distribution: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "base_ms": self.base_ms,
            "jitter_ms": self.jitter_ms,
            "total_ms": self.total_ms,
            "distribution": self.distribution,
        }


class LatencySimulator:
    """Simulates realistic network/order latency."""

    def __init__(self, config: MicrostructureConfig):
        self.config = config
        self._rng = random.Random(config.random_seed)

    def sample_latency(self) -> LatencySample:
        """Sample a latency value based on configured distribution."""
        base = self.config.base_latency_ms
        jitter_scale = self.config.latency_jitter_ms
        dist = self.config.network_latency_distribution

        if dist == "fixed":
            jitter = 0.0
        elif dist == "normal":
            jitter = abs(self._rng.gauss(0.0, jitter_scale))
        elif dist == "lognormal":
            # Log-normal with median at base, scale by jitter
            sigma = math.log(1.0 + jitter_scale / max(base, 1.0))
            jitter = self._rng.lognormvariate(math.log(base), sigma) - base
            jitter = max(0.0, jitter)
        elif dist == "exponential":
            jitter = self._rng.expovariate(1.0 / max(jitter_scale, 1.0))
        else:
            jitter = 0.0

        return LatencySample(
            base_ms=base,
            jitter_ms=jitter,
            total_ms=base + jitter,
            distribution=dist,
        )

    def apply_latency(self, func: Callable[[], Any]) -> tuple[Any, LatencySample]:
        """Execute function with simulated latency delay."""
        sample = self.sample_latency()
        if sample.total_ms > 0:
            time.sleep(sample.total_ms / 1000.0)
        result = func()
        return result, sample


class SlippageImpactModel:
    """Models slippage and market impact for paper execution."""

    def __init__(self, config: MicrostructureConfig):
        self.config = config
        self._rng = random.Random(config.random_seed + 1 if config.random_seed else None)

    def compute_slippage_bps(
        self,
        side: str,
        notional_usd: float,
        volatility: float | None = None,
        queue_position: int = 0,
    ) -> float:
        """Compute total slippage in basis points."""
        base = self.config.base_slippage_bps

        # Volatility adjustment
        if volatility is not None and self.config.volatility_slippage_multiplier > 0:
            base *= (1.0 + self.config.volatility_slippage_multiplier * volatility)

        # Market impact
        impact = 0.0
        if self.config.impact_model == "linear" and self.config.adv_usd > 0:
            impact = self.config.impact_coefficient * (notional_usd / self.config.adv_usd)
        elif self.config.impact_model == "square_root" and self.config.adv_usd > 0:
            ratio = notional_usd / self.config.adv_usd
            if ratio > 0:
                impact = self.config.impact_coefficient * math.sqrt(ratio)

        # Queue position impact
        queue_impact = queue_position * self.config.queue_position_impact_bps

        total = base + impact + queue_impact
        # Side asymmetry: buy typically gets slightly worse fills
        if side.lower() == "buy":
            total *= 1.001
        return total

    def apply_slippage(
        self,
        side: str,
        reference_price: float,
        notional_usd: float,
        volatility: float | None = None,
        queue_position: int = 0,
    ) -> float:
        """Apply slippage to reference price."""
        slippage_bps = self.compute_slippage_bps(side, notional_usd, volatility, queue_position)
        slip = slippage_bps / 10000.0
        if side.lower() == "buy":
            return reference_price * (1.0 + slip)
        return reference_price * (1.0 - slip)


class QueueSimulator:
    """Simulates order queue dynamics and partial fills."""

    def __init__(self, config: MicrostructureConfig):
        self.config = config
        self._rng = random.Random(config.random_seed + 2 if config.random_seed else None)

    def simulate_queue_fill(
        self,
        order_qty: float,
        market_price: float,
        side: str,
        queue_position: int = 0,
    ) -> tuple[float, float]:
        """Simulate fill quantity and price considering queue position.
        Returns (filled_qty, fill_price).
        """
        if not self.config.enable_queue_simulation:
            return order_qty, market_price

        # Determine if partial fill occurs
        if self._rng.random() < self.config.partial_fill_probability:
            ratio = self._rng.uniform(
                self.config.partial_fill_min_ratio,
                self.config.partial_fill_max_ratio,
            )
            filled_qty = order_qty * ratio
        else:
            filled_qty = order_qty

        # Queue position affects price (worse for deeper in queue)
        queue_slip_bps = queue_position * self.config.queue_position_impact_bps
        queue_slip = queue_slip_bps / 10000.0
        if side.lower() == "buy":
            fill_price = market_price * (1.0 + queue_slip)
        else:
            fill_price = market_price * (1.0 - queue_slip)

        return filled_qty, fill_price


class DataGapHandler:
    """Handles missing/incomplete market data bars."""

    def __init__(self, config: MicrostructureConfig):
        self.config = config
        self._last_known: dict[str, float] = {}

    def handle_gap(
        self,
        symbol: str,
        expected_bar: dict[str, Any] | None,
        last_bar: dict[str, Any] | None,
    ) -> dict[str, Any] | None:
        """Handle missing data bar, return filled bar or None to skip."""
        if not self.config.enable_data_gap_handling:
            return expected_bar

        if expected_bar is not None:
            # Update last known
            if "close" in expected_bar and _is_finite_number(expected_bar["close"]):
                self._last_known[symbol] = float(expected_bar["close"])
            return expected_bar

        # Gap detected
        if last_bar is not None and "close" in last_bar:
            gap_bars = 1  # Would need bar index to compute exactly
        else:
            gap_bars = 1

        if gap_bars > self.config.max_gap_tolerance_bars:
            return None  # Skip - gap too large

        strategy = self.config.gap_fill_strategy
        if strategy == "last_known":
            if symbol in self._last_known:
                return {"close": self._last_known[symbol], "gap_filled": True, "strategy": "last_known"}
        elif strategy == "interpolate":
            # Would need next bar - not available in streaming
            pass
        elif strategy == "skip":
            pass

        return None


@dataclass
class PaperFillResult:
    """Result of a paper fill with microstructure details."""
    order_id: str
    client_order_id: str
    symbol: str
    side: str
    requested_qty: float
    filled_qty: float
    fill_price: float
    reference_price: float
    fee: float
    fee_asset: str
    slippage_bps: float
    impact_bps: float
    queue_position: int
    latency: LatencySample
    timestamp_utc: str
    simulated: bool = True
    real_exchange_fill: bool = False
    execution_environment: str = "paper_microstructure"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "order_id": self.order_id,
            "client_order_id": self.client_order_id,
            "symbol": self.symbol,
            "side": self.side,
            "requested_qty": self.requested_qty,
            "filled_qty": self.filled_qty,
            "fill_price": self.fill_price,
            "reference_price": self.reference_price,
            "fee": self.fee,
            "fee_asset": self.fee_asset,
            "slippage_bps": self.slippage_bps,
            "impact_bps": self.impact_bps,
            "queue_position": self.queue_position,
            "latency": self.latency.to_dict(),
            "timestamp_utc": self.timestamp_utc,
            "simulated": self.simulated,
            "real_exchange_fill": self.real_exchange_fill,
            "execution_environment": self.execution_environment,
            "metadata": dict(self.metadata),
        }


class MicrostructurePaperBroker:
    """Paper broker with full microstructure simulation.

    Extends basic paper execution with:
    - Configurable latency simulation
    - Queue position and partial fill modeling
    - Slippage and market impact models
    - Data gap handling
    - Full provenance labeling
    """

    def __init__(
        self,
        *,
        config: MicrostructureConfig | None = None,
        fee_rate: float = 0.001,
        execution_environment: str = "paper_microstructure",
    ):
        self.config = config or MicrostructureConfig()
        if not _is_finite_number(fee_rate) or fee_rate < 0:
            raise ValueError("fee_rate must be finite and >= 0")
        self.fee_rate = float(fee_rate)
        self.execution_environment = execution_environment

        self.latency_sim = LatencySimulator(self.config)
        self.slippage_model = SlippageImpactModel(self.config)
        self.queue_sim = QueueSimulator(self.config)
        self.gap_handler = DataGapHandler(self.config)

        self.fill_log: list[PaperFillResult] = []
        self._order_counter = 0
        self._queue_positions: dict[str, int] = {}

    def _next_order_id(self) -> str:
        self._order_counter += 1
        return f"micro-ord-{self._order_counter}"

    def execute(
        self,
        order: dict[str, Any],
        *,
        market_price: float | None = None,
        market_data: dict[str, Any] | None = None,
        volatility: float | None = None,
    ) -> list[PaperFillResult]:
        """Execute order with full microstructure simulation."""
        if not isinstance(order, dict):
            raise ValueError("order must be a dict")

        symbol = str(order.get("symbol", "")).upper()
        side = str(order.get("side", "")).lower()
        order_type = str(order.get("order_type", "market")).lower()
        qty = order.get("quantity")
        client_order_id = str(order.get("client_order_id", f"coid-{self._next_order_id()}"))

        if not symbol or side not in {"buy", "sell"}:
            raise ValueError("invalid order symbol/side")
        if order_type not in {"market", "limit"}:
            raise ValueError("unsupported order_type")
        if not _is_finite_number(qty) or float(qty) <= 0:  # type: ignore[arg-type]
            raise ValueError("quantity must be finite and > 0")
        if not _is_finite_number(market_price) or float(market_price) <= 0:  # type: ignore[arg-type]
            raise ValueError("market_price from real/public data is required")

        mpx = float(market_price)  # type: ignore[arg-type]
        order_id = self._next_order_id()
        requested_qty = float(qty)  # type: ignore[arg-type]
        notional_usd = requested_qty * mpx

        # Get queue position (simulated)
        queue_key = f"{symbol}:{side}"
        queue_position = self._queue_positions.get(queue_key, 0)
        self._queue_positions[queue_key] = queue_position + 1

        # Simulate latency
        latency = self.latency_sim.sample_latency()

        # Handle limit orders
        if order_type == "limit":
            limit_price = order.get("limit_price")
            if not _is_finite_number(limit_price):
                raise ValueError("limit_price required for limit orders")
            lpx = float(limit_price)  # type: ignore[arg-type]
            crosses = (side == "buy" and mpx <= lpx) or (side == "sell" and mpx >= lpx)
            if not crosses:
                return []

            # For limit orders that cross, use limit price as reference
            reference_price = lpx
        else:
            reference_price = mpx

        # Apply slippage and impact
        fill_price = self.slippage_model.apply_slippage(
            side, reference_price, notional_usd, volatility, queue_position
        )

        # Compute slippage and impact components
        slip_bps = self.slippage_model.compute_slippage_bps(side, notional_usd, volatility, queue_position)
        base_slip_bps = self.config.base_slippage_bps
        impact_bps = max(0.0, slip_bps - base_slip_bps)

        # Simulate queue/partial fill
        filled_qty, fill_price = self.queue_sim.simulate_queue_fill(
            requested_qty, fill_price, side, queue_position
        )

        # Compute fee
        fee = filled_qty * fill_price * self.fee_rate

        result = PaperFillResult(
            order_id=order_id,
            client_order_id=client_order_id,
            symbol=symbol,
            side=side,
            requested_qty=requested_qty,
            filled_qty=filled_qty,
            fill_price=fill_price,
            reference_price=reference_price,
            fee=fee,
            fee_asset="USDT",
            slippage_bps=slip_bps,
            impact_bps=impact_bps,
            queue_position=queue_position,
            latency=latency,
            timestamp_utc=_utc_now_iso(),
            metadata={
                "order_type": order_type,
                "market_price": mpx,
                "simulated_execution_model": "paper_microstructure_full",
                "volatility": volatility,
            },
        )
        self.fill_log.append(result)
        return [result]

    def state(self) -> dict[str, Any]:
        return {
            "execution_environment": self.execution_environment,
            "simulated_fills": True,
            "real_exchange_fills": False,
            "fee_rate": self.fee_rate,
            "config": self.config.to_dict(),
            "fill_count": len(self.fill_log),
            "queue_positions": dict(self._queue_positions),
        }

    def get_fills(self) -> list[dict[str, Any]]:
        return [f.to_dict() for f in self.fill_log]


def create_microstructure_broker_from_env() -> MicrostructurePaperBroker:
    """Create microstructure broker from environment variables (all optional)."""
    import os
    return MicrostructurePaperBroker(
        config=MicrostructureConfig(
            base_latency_ms=float(os.environ.get("MICRO_LATENCY_BASE_MS", "10")),
            latency_jitter_ms=float(os.environ.get("MICRO_LATENCY_JITTER_MS", "5")),
            network_latency_distribution=os.environ.get("MICRO_LATENCY_DIST", "lognormal"),
            partial_fill_probability=float(os.environ.get("MICRO_PARTIAL_FILL_PROB", "0.1")),
            base_slippage_bps=float(os.environ.get("MICRO_BASE_SLIPPAGE_BPS", "5")),
            volatility_slippage_multiplier=float(os.environ.get("MICRO_VOL_MULT", "1.0")),
            impact_model=os.environ.get("MICRO_IMPACT_MODEL", "square_root"),
            impact_coefficient=float(os.environ.get("MICRO_IMPACT_COEFF", "0.1")),
            adv_usd=float(os.environ.get("MICRO_ADV_USD", "1000000")),
            random_seed=int(os.environ["MICRO_RANDOM_SEED"]) if os.environ.get("MICRO_RANDOM_SEED") else None,
        ),
        fee_rate=float(os.environ.get("MICRO_FEE_RATE", "0.001")),
    )
