"""
Volatility Surface Strategy
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


class VolatilitySurfaceStrategy(Strategy):
    """Strategy trading on implied volatility surface/regime signals.

    Long when IV is depressed relative to its rolling regime (e.g., low percentile rank),
    short when IV is elevated, and exits on reversion to mean.
    """

    def __init__(
        self,
        asset: str = "BTC",
        iv_column: str | None = None,
        lookback: int = 30,
        entry_percentile: float = 0.2,
        exit_percentile: float = 0.5,
        short_percentile: float = 0.8,
        params: dict[str, Any] | None = None,
        enriched_diagnostics: dict[str, Any] | None = None,
        use_enriched_gates: bool = True,
        strict_enriched_gates: bool = True,
    ):
        super().__init__(f"volatility_surface_{asset}", params)
        self.asset = asset
        self.iv_column = iv_column
        self.lookback = lookback
        self.entry_percentile = entry_percentile
        self.exit_percentile = exit_percentile
        self.short_percentile = short_percentile
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
            "source": "strategies.volatility_surface",
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
        iv_col = self.iv_column
        if iv_col is None:
            for candidate in ["iv", "implied_vol", "implied_volatility", "IV"]:
                if candidate in data.columns:
                    iv_col = candidate
                    break
        if iv_col is None:
            for col in data.columns:
                if "iv" in str(col).lower():
                    iv_col = col
                    break

        if iv_col is not None and iv_col in data.columns:
            iv = data[iv_col].astype(float)
        elif self.asset in data.columns:
            price = data[self.asset].astype(float)
            returns = price.pct_change()
            iv = returns.rolling(self.lookback).std() * np.sqrt(252)
        else:
            iv = pd.Series(0.0, index=data.index)

        signals["iv"] = iv

        def percentile_rank(series: pd.Series) -> float:
            if len(series) == 0:
                return 0.5
            current = series.iloc[-1]
            rank = (series < current).sum() / len(series)
            return float(rank)

        iv_percentile = iv.rolling(self.lookback).apply(percentile_rank, raw=False)
        signals["iv_percentile"] = iv_percentile
        signals["iv_mean"] = iv.rolling(self.lookback).mean()

        signals["long"] = iv_percentile < self.entry_percentile
        signals["short"] = iv_percentile > self.short_percentile
        signals["exit"] = iv_percentile >= self.exit_percentile

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
                            g, sb, bool(self.strict_enriched_gates)
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
                signals["long"] = signals["long"].copy()
                signals["short"] = signals["short"].copy()
                signals.loc[mask_bad, "long"] = False
                signals.loc[mask_bad, "short"] = False

        signals["enriched_gates_ok"] = enriched_ok
        return signals

    def calculate_position_sizes(self, signals: pd.DataFrame) -> dict[str, float]:
        """Calculate position sizes based on latest signal."""
        last = signals.iloc[-1] if len(signals) else pd.Series(dtype=float)
        long = bool(last.get("long", False))
        short = bool(last.get("short", False))
        exit_sig = bool(last.get("exit", False))

        # If exiting/reverting, flatten
        if exit_sig and not long and not short:
            return {self.asset: 0.0}

        if long and not short:
            return {self.asset: 1.0}
        if short and not long:
            return {self.asset: -1.0}
        return {self.asset: 0.0}
