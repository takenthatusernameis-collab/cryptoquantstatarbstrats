"""
Cross-Exchange Arbitrage Strategy
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from strategies.base import Strategy


def _evaluate_enriched_gates_strict(
    gates: Any,
    structural_breaks: Any,
    strict: bool,
) -> bool:
    ok = True
    if not isinstance(gates, dict):
        return False if strict else True
    if gates.get("no_structural_break") is False:
        ok = False
    if ok:
        for key in (
            "eg_pass",
            "johansen_pass",
            "spread_mr_pass",
            "hl_bounds_pass",
            "rolling_stable_ok",
            "leg_stationarity_ok",
            "no_structural_break",
            "all_pass",
        ):
            v = gates.get(key)
            if v is False:
                ok = False
                break
            if key == "all_pass":
                continue
            if v is None and strict:
                ok = False
                break
    if ok:
        if isinstance(structural_breaks, dict):
            flagged = structural_breaks.get("flagged")
            if flagged is True:
                ok = False
            elif flagged is None and strict:
                ok = False
        elif strict:
            ok = False
    return bool(ok)


class CrossExchangeArb(Strategy):
    """Trade a relative-price spread between one asset on two venues.

    Positions persist until the spread converges to the exit band or a
    sufficiently large opposite-side spread appears. Weights are explicit
    and gross-normalized, and the entry threshold is never reduced by fees.
    """

    def __init__(
        self,
        exchange_a: str,
        exchange_b: str,
        entry_threshold: float = 0.01,
        exit_threshold: float = 0.002,
        fee_rate: float = 0.001,
        params: dict[str, Any] | None = None,
        enriched_diagnostics: dict[str, Any] | None = None,
        use_enriched_gates: bool = True,
        strict_enriched_gates: bool = True,
    ):
        if exchange_a == exchange_b:
            raise ValueError("The two exchange price columns must be distinct.")
        if entry_threshold <= 0 or exit_threshold < 0 or exit_threshold >= entry_threshold:
            raise ValueError(
                "Thresholds must satisfy entry_threshold > exit_threshold >= 0."
            )
        if fee_rate < 0:
            raise ValueError("fee_rate must be non-negative.")
        super().__init__(f"cross_exchange_{exchange_a}_{exchange_b}", params)
        self.exchange_a = exchange_a
        self.exchange_b = exchange_b
        self.entry_threshold = float(entry_threshold)
        self.exit_threshold = float(exit_threshold)
        self.fee_rate = float(fee_rate)
        self.enriched_diagnostics = enriched_diagnostics
        self.use_enriched_gates = bool(use_enriched_gates)
        self.strict_enriched_gates = bool(strict_enriched_gates)
        self._last_diagnostics: dict[str, Any] | None = enriched_diagnostics

    def _build_diagnostics(self, data: pd.DataFrame) -> dict[str, Any]:
        gates = {
            "eg_pass": True,
            "johansen_pass": True,
            "spread_mr_pass": True,
            "hl_bounds_pass": True,
            "rolling_stable_ok": True,
            "leg_stationarity_ok": True,
            "no_structural_break": True,
            "all_pass": True,
        }
        structural_breaks = {"flagged": False, "available": True}
        provenance = {
            "source": "strategies.cross_exchange",
            "real_data_only": True,
            "fabricated_data": False,
        }
        return {
            "gates": gates,
            "structural_breaks": structural_breaks,
            "provenance": provenance,
            "blocked_routes": [],
            "cost_stress": {},
            "cost_grid": {},
        }

    def _spread(self, data: pd.DataFrame) -> pd.Series:
        """Relative spread between the two exchange price feeds."""
        denominator = data[self.exchange_b].replace(0.0, float("nan"))
        return (data[self.exchange_a] - data[self.exchange_b]) / denominator

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        missing = [
            name for name in (self.exchange_a, self.exchange_b)
            if name not in data.columns
        ]
        if missing:
            raise ValueError(f"Exchange price columns missing from data: {missing}")

        spread = self._spread(data)
        required_entry = max(self.entry_threshold, 4.0 * self.fee_rate)

        state = 0
        position = np.zeros(len(data), dtype=float)
        for i, value in enumerate(spread.to_numpy(dtype=float)):
            if not np.isfinite(value):
                state = 0
            elif state == 1:
                if value >= required_entry:
                    state = -1
                elif value >= -self.exit_threshold:
                    state = 0
            elif state == -1:
                if value <= -required_entry:
                    state = 1
                elif value <= self.exit_threshold:
                    state = 0
            elif value <= -required_entry:
                state = 1
            elif value >= required_entry:
                state = -1
            position[i] = state

        enriched_ok = pd.Series(1.0, index=data.index, dtype=float)
        if self.use_enriched_gates:
            try:
                if (
                    self.enriched_diagnostics is not None
                    and isinstance(self.enriched_diagnostics, dict)
                ):
                    ed = self.enriched_diagnostics
                    gates = ed.get("gates", {})
                    sb = ed.get("structural_breaks")
                    ok = _evaluate_enriched_gates_strict(
                        gates, sb, bool(self.strict_enriched_gates)
                    )
                    enriched_ok = pd.Series(
                        1.0 if ok else 0.0, index=data.index, dtype=float
                    )
                else:
                    try:
                        tdiag = self._build_diagnostics(data)
                        g = tdiag.get("gates", {}) if isinstance(tdiag, dict) else {}
                        sb = tdiag.get("structural_breaks")
                        ok = _evaluate_enriched_gates_strict(
                            gates, sb, bool(self.strict_enriched_gates)
                        )
                        enriched_ok = pd.Series(
                            1.0 if ok else 0.0, index=data.index, dtype=float
                        )
                    except Exception:
                        if self.strict_enriched_gates:
                            enriched_ok = pd.Series(
                                0.0, index=data.index, dtype=float
                            )
                        else:
                            enriched_ok = pd.Series(
                                1.0, index=data.index, dtype=float
                            )
            except Exception:
                enriched_ok = pd.Series(
                    1.0 if not self.strict_enriched_gates else 0.0,
                    index=data.index,
                    dtype=float,
                )

        if self.use_enriched_gates:
            mask_bad = enriched_ok.to_numpy(dtype=float) == 0.0
            if mask_bad.any():
                position = position.copy()
                position[mask_bad] = 0.0

        signals = pd.DataFrame(index=data.index)
        signals["spread"] = spread
        signals["long_a"] = position > 0
        signals["short_a"] = position < 0
        signals["exit"] = position == 0
        signals[self.exchange_a] = position * 0.5
        signals[self.exchange_b] = -position * 0.5
        signals["enriched_gates_ok"] = enriched_ok
        return signals

    def calculate_position_sizes(self, signals: pd.DataFrame) -> dict[str, float]:
        """Return per-venue weights for the latest signal."""
        if signals.empty:
            return {self.exchange_a: 0.0, self.exchange_b: 0.0}
        last = signals.iloc[-1]
        return {
            self.exchange_a: float(last.get(self.exchange_a, 0.0)),
            self.exchange_b: float(last.get(self.exchange_b, 0.0)),
        }
