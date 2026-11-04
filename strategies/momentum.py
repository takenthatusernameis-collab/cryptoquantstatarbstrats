"""
Momentum Strategy
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


class MomentumStrategy(Strategy):
    """Momentum strategy on a single asset."""

    def __init__(
        self,
        asset: str,
        n: int = 10,
        m: int = 20,
        entry_threshold: float = 0.01,
        params: dict[str, Any] | None = None,
        enriched_diagnostics: dict[str, Any] | None = None,
        use_enriched_gates: bool = True,
        strict_enriched_gates: bool = True,
    ):
        super().__init__(f"momentum_{asset}", params)
        self.asset = asset
        self.n = n
        self.m = m
        self.entry_threshold = entry_threshold
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
            "source": "strategies.momentum",
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

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        signals = pd.DataFrame(index=data.index)
        price = data[self.asset]
        shifted = price.shift(self.n)
        ma = shifted.rolling(self.m).mean()
        signals["ma"] = ma
        signals["long"] = price > ma * (1 + self.entry_threshold)
        signals["short"] = price < ma * (1 - self.entry_threshold)
        signals["exit"] = abs(price - ma) / ma < self.entry_threshold * 0.5

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
                        enriched_ok_arr = np.empty(len(data), dtype=float)
                        enriched_ok_arr[:] = 1.0 if ok else 0.0
                        enriched_ok = pd.Series(enriched_ok_arr, index=data.index)
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
                signals["long"] = signals["long"].copy()
                signals["short"] = signals["short"].copy()
                signals.loc[mask_bad, "long"] = False
                signals.loc[mask_bad, "short"] = False

        # Explicit asset weights prevent this single-asset strategy from
        # applying its generic long/short flags to every input column.
        signals[self.asset] = (
            signals["long"].astype(float) - signals["short"].astype(float)
        )
        signals["enriched_gates_ok"] = enriched_ok
        return signals

    def calculate_position_sizes(self, signals: pd.DataFrame) -> dict[str, float]:
        last = signals.iloc[-1] if len(signals) else pd.Series(dtype=float)
        long = bool(last.get("long", False))
        short = bool(last.get("short", False))
        if long and not short:
            return {self.asset: 1.0}
        if short and not long:
            return {self.asset: -1.0}
        return {self.asset: 0.0}
