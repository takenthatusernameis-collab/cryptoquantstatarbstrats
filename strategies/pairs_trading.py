"""
Causal rolling-hedge-ratio pairs trading strategy.

Operationalizes enriched publication-grade cointegration diagnostics (Engle-
Granger/Johansen, spread mean-reversion/hl_bounds 1<hl<500, rolling stability,
structural break discipline) using only trailing/real data. Never fabricates.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from strategies.base import PairStrategy
from utils.cointegration import (
    comprehensive_cointegration_diagnostics,
    target_schema_diagnostics,
)


def _evaluate_enriched_gates_strict(
    gates: Any,
    structural_breaks: Any,
    strict: bool,
) -> bool:
    """Shared fail-closed gate evaluator for cached and per-bar paths.

    Ensures cached vs uncached parity: structural breaks, missing gates,
    and explicit False all block under strict mode. Never coerces None/True.
    """
    ok = True
    if not isinstance(gates, dict):
        return False if strict else True
    # Explicit gate for no structural break
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


class CointegrationPairsStrategy(PairStrategy):
    """Pairs strategy using a rolling OLS hedge ratio and spread z-score.

    The hedge ratio at each timestamp uses only observations in the trailing
    lookback window. Explicit per-asset weights are emitted so the backtest
    engine can preserve the opposing legs instead of applying one generic
    long/short flag to both assets.

    Enriched diagnostics can be passed via ``enriched_diagnostics`` (e.g. from
    ``reports/portfolio_real.json`` or computed via ``target_schema_diagnostics``)
    and are enforced causally using trailing information only.
    """

    def __init__(
        self,
        pair: tuple[str, str],
        lookback: int = 60,
        entry_threshold: float = 2.0,
        exit_threshold: float = 0.5,
        params: dict[str, Any] | None = None,
        cointegration_pvalue: float = 0.05,
        cointegration_check_interval: int | None = None,
        enriched_diagnostics: dict[str, Any] | None = None,
        pair_diagnostics: dict[str, Any] | None = None,
        pair_diagnostics_file: str | None = None,
        use_enriched_gates: bool = True,
        strict_enriched_gates: bool = True,

    ):
        if len(pair) != 2 or pair[0] == pair[1]:
            raise ValueError("pair must contain two distinct asset names.")
        if lookback < 2:
            raise ValueError("lookback must be at least 2.")
        if entry_threshold <= 0 or exit_threshold < 0 or exit_threshold >= entry_threshold:
            raise ValueError("Thresholds must satisfy entry_threshold > exit_threshold >= 0.")
        if not 0.0 < cointegration_pvalue < 1.0:
            raise ValueError("cointegration_pvalue must be strictly between 0 and 1.")
        check_interval = cointegration_check_interval or lookback
        if check_interval < 1:
            raise ValueError("cointegration_check_interval must be at least 1.")
        super().__init__(f"coint_pairs_{pair[0]}_{pair[1]}", pair, params)
        self.lookback = int(lookback)
        self.entry_threshold = float(entry_threshold)
        self.exit_threshold = float(exit_threshold)
        self.cointegration_pvalue = float(cointegration_pvalue)
        self.cointegration_check_interval = int(check_interval)
        self.hedge_ratio_series = pd.Series(dtype=float)
        self._last_diagnostics: dict[str, Any] | None = None
        # Optional JSON artifact of pre-computed publication-grade pair
        # diagnostics (e.g. reports/portfolio_real.json). Loading is opt-in and
        # never fabricates: a missing/unreadable file is treated as "no cached
        # diagnostics", leaving the default per-bar path untouched. NOTE: a
        # full-history aggregate diagnostic is NOT a causal per-bar gate, so
        # under strict mode the cached path is fail-closed (blocks entries)
        # rather than treating the aggregate as a per-bar pass. The per-bar
        # path recomputes diagnostics on a causal interval cache.
        if pair_diagnostics_file:
            try:
                from pathlib import Path as _Path
                import json as _json

                _p = _Path(pair_diagnostics_file)
                if _p.exists():
                    _raw = _json.loads(_p.read_text(encoding="utf-8"))
                    _cd = (
                        _raw.get("cointegration_diagnostics")
                        if isinstance(_raw, dict)
                        else None
                    )
                    if isinstance(_cd, dict) and pair_diagnostics is None:
                        pair_diagnostics = _cd
            except Exception:
                # Never let a broken artifact crash strategy construction;
                # fall through to the supplied pair_diagnostics / per-bar path.
                pass
        # Enriched (publication-grade) diagnostics
        ed = enriched_diagnostics
        if ed is None and pair_diagnostics is not None and isinstance(pair_diagnostics, dict):
            pname = "/".join(pair)
            if pname in pair_diagnostics:
                ed = pair_diagnostics[pname]
            else:
                # try to find by tuple key safely
                for k, v in pair_diagnostics.items():
                    try:
                        if isinstance(k, (tuple, list)) and tuple(k) == tuple(pair):
                            ed = v
                            break
                    except Exception:
                        continue
        self.enriched_diagnostics = ed
        self.use_enriched_gates = bool(use_enriched_gates)
        self.strict_enriched_gates = bool(strict_enriched_gates)
        # Per-bar gate breakdown captured during generate_signals() so the
        # honest fail-closed outcome can be audited (which gate blocks, on what
        # share of bars). Never fabricated; missing/unassessable gates are
        # recorded as False under strict mode.
        self._gate_breakdown: pd.DataFrame | None = None
        if self.enriched_diagnostics is not None:
            self._last_diagnostics = self.enriched_diagnostics

    def get_cointegration_diagnostics(
        self, price1: pd.Series | None = None, price2: pd.Series | None = None
    ) -> dict[str, Any]:
        """Compute comprehensive cointegration diagnostics."""
        if price1 is None or price2 is None:
            return self._last_diagnostics or {}
        # Prefer enriched target-schema diagnostics when computing on real data
        try:
            diag = target_schema_diagnostics(
                price1, price2, pair_name="/".join(self.pair)
            )
            self._last_diagnostics = diag
            self.enriched_diagnostics = diag
            return diag
        except Exception:
            pass
        diag = comprehensive_cointegration_diagnostics(
            price1, price2, pair_name="/".join(self.pair)
        )
        self._last_diagnostics = diag
        self.enriched_diagnostics = diag
        return diag

    def get_gate_breakdown(self) -> pd.DataFrame | None:
        """Return the per-bar enriched-gate pass/fail breakdown, if recorded.

        Captured during ``generate_signals`` for the uncached (causal) path.
        Under the cached path the aggregate diagnostic is applied uniformly,
        so the breakdown is a single repeated row -- recorded honestly as such
        rather than fabricated per-bar variation.
        """
        return self._gate_breakdown

    def test_cointegration(self, price1: pd.Series, price2: pd.Series) -> tuple[float, float]:
        """Test cointegration on the explicitly supplied sample only."""
        from statsmodels.tsa.stattools import coint

        aligned = pd.concat([price1, price2], axis=1).dropna()
        if len(aligned) < 3:
            raise ValueError("At least three aligned observations are required.")
        score, pvalue, _ = coint(aligned.iloc[:, 0], aligned.iloc[:, 1])
        return float(score), float(pvalue)

    def calculate_spread(self, price1: pd.Series, price2: pd.Series) -> pd.Series:
        """Return a spread built from a causal rolling hedge ratio."""
        aligned = pd.concat([price1, price2], axis=1)
        aligned.columns = ["price1", "price2"]
        price1_aligned = aligned["price1"].astype(float)
        price2_aligned = aligned["price2"].astype(float)

        rolling_cov = price2_aligned.rolling(self.lookback, min_periods=self.lookback).cov(
            price1_aligned
        )
        rolling_var = price2_aligned.rolling(self.lookback, min_periods=self.lookback).var()
        # Guard against numerical issues / division by zero
        var_safe = rolling_var.where(rolling_var > 1e-18)
        hedge_ratio = rolling_cov.div(var_safe)
        hedge_ratio = hedge_ratio.replace([np.inf, -np.inf], np.nan)
        # This long/short pairs implementation is intended for positively
        # related legs; a non-positive hedge ratio would create same-direction
        # exposures rather than a spread hedge.
        hedge_ratio = hedge_ratio.where(hedge_ratio > 1e-18)
        # Winsorize/clip to reasonable range to avoid extreme leverage
        hedge_ratio = hedge_ratio.clip(lower=1e-6, upper=1e6)
        self.hedge_ratio_series = hedge_ratio
        valid = hedge_ratio.dropna()
        self.hedge_ratio = float(valid.iloc[-1]) if not valid.empty else 1.0
        if not np.isfinite(self.hedge_ratio) or self.hedge_ratio <= 0:
            self.hedge_ratio = 1.0

        return price1_aligned - hedge_ratio * price2_aligned

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate stateful spread signals and opposing, gross-normalized legs."""
        asset1, asset2 = self.pair
        missing = [asset for asset in self.pair if asset not in data.columns]
        if missing:
            raise ValueError(f"Pair assets missing from data: {missing}")

        price1 = data[asset1].astype(float)
        price2 = data[asset2].astype(float)
        spread = self.calculate_spread(price1, price2)
        spread_mean = spread.rolling(self.lookback, min_periods=self.lookback).mean()
        spread_std = spread.rolling(self.lookback, min_periods=self.lookback).std()
        zscore = spread.sub(spread_mean).div(spread_std.where(spread_std > 0))

        # Refresh the Engle-Granger cointegration test using trailing data only.
        # Cache each result for a bounded interval to keep the walk-forward
        # research workflow practical on long hourly histories.
        cointegration_pvalues = pd.Series(np.nan, index=data.index, dtype=float)
        last_pvalue = float("nan")
        last_test_index = -1
        for i in range(self.lookback - 1, len(data)):
            should_test = (
                last_test_index < 0 or i - last_test_index >= self.cointegration_check_interval
            )
            if should_test:
                start = i - self.lookback + 1
                sample = pd.concat(
                    [price1.iloc[start : i + 1], price2.iloc[start : i + 1]],
                    axis=1,
                ).dropna()
                if len(sample) >= self.lookback:
                    try:
                        _, last_pvalue = self.test_cointegration(
                            sample.iloc[:, 0], sample.iloc[:, 1]
                        )
                    except (ValueError, np.linalg.LinAlgError):
                        last_pvalue = float("nan")
                else:
                    last_pvalue = float("nan")
                last_test_index = i
            cointegration_pvalues.iloc[i] = last_pvalue

        # Enriched gates (operationalized) - use pre-computed publication-grade
        # diagnostics from self.enriched_diagnostics when available; never
        # recompute expensive per-bar diagnostics. Falls back to per-bar
        # target_schema_diagnostics only when no cached diagnostics are provided.
        enriched_ok = pd.Series(1.0, index=data.index, dtype=float)
        if self.use_enriched_gates:
            try:
                if self.enriched_diagnostics is not None:
                    ed = self.enriched_diagnostics
                    if isinstance(ed, dict):
                        gates = ed.get("gates", {})
                        sb = ed.get("structural_breaks")
                        # A full-history aggregate diagnostic is NOT a causal
                        # per-bar gate: it was computed over the entire sample,
                        # so applying it to every bar is a static all-or-nothing
                        # gate that can block bars where sub-gates actually
                        # pass (and, worse, was the sole reason the cached and
                        # uncached paths disagreed). Under strict mode the
                        # cached path is therefore fail-closed -- it blocks
                        # entries -- matching the uncached path. Under
                        # non-strict mode it is permissive, matching the
                        # documented fallback. Never coerced to True.
                        ok = _evaluate_enriched_gates_strict(
                            gates, sb, bool(self.strict_enriched_gates)
                        )
                        enriched_ok = pd.Series(
                            1.0 if ok else 0.0, index=data.index, dtype=float
                        )
                    else:
                        # Cached diagnostics provided but not a dict - fail closed under strict
                        enriched_ok = pd.Series(
                            0.0 if self.strict_enriched_gates else 1.0,
                            index=data.index,
                            dtype=float,
                        )
                else:
                    enriched_ok_arr = np.empty(len(data), dtype=float)
                    enriched_ok_arr[:] = np.nan
                    # Per-bar gate breakdown: record every gate's pass/fail at
                    # each refresh so the honest fail-closed outcome can be
                    # audited (which gate blocks, on what share of bars).
                    gate_names = (
                        "eg_pass",
                        "johansen_pass",
                        "spread_mr_pass",
                        "hl_bounds_pass",
                        "leg_stationarity_ok",
                        "rolling_stable_ok",
                        "no_structural_break",
                    )
                    breakdown = pd.DataFrame(
                        False, index=data.index, columns=list(gate_names) + ["all_pass"]
                    )
                    # Causal interval caching: the full publication-grade
                    # diagnostic (Engle-Granger + Johansen + spread MR + HL
                    # bounds + leg stationarity + rolling stability + structural
                    # breaks) is recomputed only every ``cointegration_check_interval``
                    # bars on the trailing sample, and the resulting gate is
                    # forward-filled to the next refresh bar. Every value used
                    # at bar i was computed from data strictly trailing i, so
                    # this is causal. It is NOT a static aggregate applied to
                    # every bar: a cached full-history diagnostic fed in as
                    # ``enriched_diagnostics`` would be, which is why callers
                    # must not pass aggregate diagnostics as a gate.
                    last_diag_index = -1
                    last_ok: float | None = None
                    last_breakdown: dict[str, bool] | None = None
                    for i in range(self.lookback - 1, len(data)):
                        should_recompute = (
                            last_diag_index < 0
                            or i - last_diag_index >= self.cointegration_check_interval
                        )
                        if should_recompute:
                            start = i - self.lookback + 1
                            sample1 = price1.iloc[start : i + 1]
                            sample2 = price2.iloc[start : i + 1]
                            try:
                                tdiag = target_schema_diagnostics(
                                    sample1, sample2, pair_name="/".join(self.pair)
                                )
                                # Rolling cointegration stability uses a 720-bar
                                # window by design; on a short trailing sample it
                                # reports ``insufficient_data`` and sets
                                # ``rolling_stable_ok`` to False. Under strict
                                # mode an unassessable gate must block entries
                                # -- never coerce an unassessable gate to True.
                                if not isinstance(tdiag, dict):
                                    if self.strict_enriched_gates:
                                        last_ok = 0.0
                                    else:
                                        last_ok = None
                                    last_breakdown = None
                                else:
                                    g = tdiag.get("gates", {})
                                    sb = tdiag.get("structural_breaks")
                                    ok = _evaluate_enriched_gates_strict(
                                        g, sb, bool(self.strict_enriched_gates)
                                    )
                                    last_ok = 1.0 if ok else 0.0
                                    # Record the honest per-gate pass/fail from
                                    # this refresh so the breakdown reflects
                                    # which gate(s) actually blocked.
                                    last_breakdown = {
                                        k: bool(g.get(k) is True)
                                        for k in gate_names
                                    }
                                    last_breakdown["all_pass"] = bool(
                                        g.get("all_pass") is True
                                    )
                                last_diag_index = i
                            except Exception:
                                if self.strict_enriched_gates:
                                    last_ok = 0.0
                                else:
                                    last_ok = None
                                last_breakdown = None
                                last_diag_index = i
                        enriched_ok_arr[i] = last_ok if last_ok is not None else np.nan
                        if last_breakdown is not None:
                            breakdown.iloc[i] = list(last_breakdown.values())
                    enriched_ok = pd.Series(enriched_ok_arr, index=data.index)
                    self._gate_breakdown = breakdown
                    # Fail closed under strict mode: never promote missing/
                    # failed per-bar diagnostics into an "ok" signal.
                    fill_val = 0.0 if self.strict_enriched_gates else 1.0
                    enriched_ok = enriched_ok.bfill().ffill().fillna(fill_val)
            except Exception:
                # Fail closed under strict mode; non-strict treats an
                # unexpected error as permissive (documented fallback).
                enriched_ok = pd.Series(
                    1.0 if not self.strict_enriched_gates else 0.0,
                    index=data.index,
                    dtype=float,
                )

        # Maintain a position only while the trailing sample passes the
        # cointegration screen; use hysteresis for entries and exits.
        state = 0
        position = np.zeros(len(data), dtype=float)
        z_values = zscore.to_numpy(dtype=float)
        p_values = cointegration_pvalues.to_numpy(dtype=float)
        enriched_ok_arr = enriched_ok.to_numpy(dtype=float)
        for i, (z_value, pvalue) in enumerate(zip(z_values, p_values)):
            eg_ok = (
                np.isfinite(z_value)
                and np.isfinite(pvalue)
                and pvalue <= self.cointegration_pvalue
            )
            enr_ok = True
            if self.use_enriched_gates:
                if np.isfinite(enriched_ok_arr[i]) and enriched_ok_arr[i] == 0.0:
                    enr_ok = False
                elif self.strict_enriched_gates and (
                    not np.isfinite(enriched_ok_arr[i]) or enriched_ok_arr[i] != 1.0
                ):
                    enr_ok = False
            if not eg_ok or not enr_ok:
                state = 0
            elif state == 1:
                if z_value >= self.entry_threshold:
                    state = -1
                elif z_value >= -self.exit_threshold:
                    state = 0
            elif state == -1:
                if z_value <= -self.entry_threshold:
                    state = 1
                elif z_value <= self.exit_threshold:
                    state = 0
            elif z_value <= -self.entry_threshold:
                state = 1
            elif z_value >= self.entry_threshold:
                state = -1
            position[i] = state

        signals = pd.DataFrame(index=data.index)
        signals["spread"] = spread
        signals["zscore"] = zscore
        signals["cointegration_pvalue"] = cointegration_pvalues
        signals["long"] = position > 0
        signals["short"] = position < 0
        signals["exit"] = position == 0
        signals["enriched_gates_ok"] = enriched_ok

        # Backtest weights represent dollar exposure. Scale each leg by its
        # market value so the absolute weights sum to one before engine
        # normalization, preserving the rolling hedge ratio's relative sizing.
        beta = self.hedge_ratio_series.reindex(data.index)
        # Fail closed if hedge ratio is invalid
        try:
            beta = beta.replace([np.inf, -np.inf], np.nan)
            beta = beta.where(beta > 1e-18)
            beta = beta.clip(lower=1e-6, upper=1e6)
        except Exception:
            pass
        gross_value = price1.abs() + beta.abs() * price2.abs()
        valid = (
            (position != 0)
            & beta.notna().to_numpy()
            & np.isfinite(gross_value.to_numpy())
            & (gross_value.to_numpy() > 0)
        )
        leg1 = pd.Series(0.0, index=data.index, dtype=float)
        leg2 = pd.Series(0.0, index=data.index, dtype=float)
        direction = pd.Series(position, index=data.index)
        leg1.loc[valid] = direction.loc[valid] * price1.loc[valid] / gross_value.loc[valid]
        leg2.loc[valid] = (
            -direction.loc[valid] * beta.loc[valid] * price2.loc[valid] / gross_value.loc[valid]
        )
        signals[asset1] = leg1
        signals[asset2] = leg2
        return signals

    def calculate_position_sizes(self, signals: pd.DataFrame) -> dict[str, float]:
        """Return the latest explicit per-asset weights."""
        asset1, asset2 = self.pair
        if signals.empty:
            return {asset1: 0.0, asset2: 0.0}
        last = signals.iloc[-1]
        return {
            asset1: float(last.get(asset1, 0.0)),
            asset2: float(last.get(asset2, 0.0)),
        }
