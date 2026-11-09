"""ML-gated cointegration pairs signals (Campaign #3).

Uses trailing-only cointegration/regime features and a classifier for
cointegration persistence. Purged walk-forward evaluation and embargo are
handled by utils.ml_gating / the runner; this strategy applies a fail-closed
ML gate to candidate pair entries.

Real-data-only workflows must supply real market data. No fabrication.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from strategies.base import PairStrategy
from utils.ml_gating import (
    extract_persistence_features,
    gate_persistence,
)


class MLGatedPairsStrategy(PairStrategy):
    """Pairs strategy with ML persistence gate (fail-closed).

    Base signal: trailing spread z-score with entry/exit thresholds.
    ML gate: when provided a fitted model, candidate entries are allowed only
    if the model predicts cointegration persistence above threshold using
    trailing features only. Exits are never blocked by the ML gate.
    """

    def __init__(
        self,
        pair: tuple[str, str],
        lookback: int = 120,
        entry_threshold: float = 2.0,
        exit_threshold: float = 0.5,
        ml_model: Any | None = None,
        ml_threshold: float = 0.5,
        min_obs: int = 60,
        params: dict[str, Any] | None = None,
    ):
        if len(pair) != 2 or pair[0] == pair[1]:
            raise ValueError("pair must contain two distinct asset names.")
        if lookback < 10:
            raise ValueError("lookback must be >= 10.")
        if entry_threshold <= 0 or exit_threshold < 0 or exit_threshold >= entry_threshold:
            raise ValueError("Thresholds must satisfy entry_threshold > exit_threshold >= 0.")
        if not (0.0 <= ml_threshold <= 1.0):
            raise ValueError("ml_threshold must be in [0,1].")
        super().__init__(f"ml_gated_pairs_{pair[0]}_{pair[1]}", pair, params)
        self.lookback = int(lookback)
        self.entry_threshold = float(entry_threshold)
        self.exit_threshold = float(exit_threshold)
        self.ml_model = ml_model
        self.ml_threshold = float(ml_threshold)
        self.min_obs = int(min_obs)
        self._gate_audit: list[dict[str, Any]] = []

    def get_gate_audit(self) -> list[dict[str, Any]]:
        return list(self._gate_audit)

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        asset1, asset2 = self.pair
        missing = [a for a in self.pair if a not in data.columns]
        if missing:
            raise ValueError(f"Pair assets missing from data: {missing}")
        p1 = data[asset1].astype(float)
        p2 = data[asset2].astype(float)
        aligned = pd.concat([p1, p2], axis=1).dropna()
        aligned.columns = [asset1, asset2]
        idx = data.index
        signals = pd.DataFrame(
            0.0, index=idx, columns=[asset1, asset2, "zscore", "ml_allow", "ml_prob"]
        )
        signals["zscore"] = np.nan
        signals["ml_prob"] = np.nan
        signals["ml_allow"] = 0.0

        # Rolling OLS hedge on trailing window (causal)
        a = aligned[asset1]
        b = aligned[asset2]
        spread = pd.Series(np.nan, index=aligned.index, dtype=float)
        hedge = pd.Series(np.nan, index=aligned.index, dtype=float)
        for i in range(self.lookback, len(aligned) + 1):
            aw = a.iloc[i - self.lookback : i]
            bw = b.iloc[i - self.lookback : i]
            if len(aw) < self.min_obs:
                continue
            # OLS: a = beta*b + eps
            try:
                x = bw.values
                y = aw.values
                vx = float(np.var(x))
                if not np.isfinite(vx) or vx < 1e-18:
                    beta = 1.0
                else:
                    beta = float(np.cov(x, y, ddof=0)[0, 1] / vx)
                if not np.isfinite(beta) or beta <= 0:
                    beta = abs(beta) if np.isfinite(beta) and abs(beta) > 1e-12 else 1.0
                beta = float(np.clip(beta, 1e-6, 1e6))
                hedge.iloc[i - 1] = beta
                spread.iloc[i - 1] = float(y[-1] - beta * x[-1])
            except Exception:
                continue

        # zscore from trailing spread
        sp = spread
        mu = sp.rolling(self.lookback, min_periods=self.min_obs).mean()
        sd = sp.rolling(self.lookback, min_periods=self.min_obs).std(ddof=0)
        z = (sp - mu) / sd.replace(0.0, np.nan)

        pos = pd.Series(0.0, index=aligned.index, dtype=float)
        self._gate_audit = []
        for i in range(len(aligned)):
            zi = z.iloc[i]
            prev = float(pos.iloc[i - 1]) if i > 0 else 0.0
            hi = hedge.iloc[i]
            if not np.isfinite(zi) or not np.isfinite(hi):
                pos.iloc[i] = 0.0
                continue
            # exit logic
            if prev > 0 and zi >= -self.exit_threshold:
                pos.iloc[i] = 0.0
                continue
            if prev < 0 and zi <= self.exit_threshold:
                pos.iloc[i] = 0.0
                continue
            if prev != 0:
                pos.iloc[i] = prev
                continue
            # candidate entries require ML gate
            want = 0.0
            if zi <= -self.entry_threshold:
                want = 1.0  # long spread: long asset1, short asset2*beta
            elif zi >= self.entry_threshold:
                want = -1.0
            if want == 0.0:
                pos.iloc[i] = 0.0
                continue
            # ML gate uses trailing data up to i (causal; no future bars).
            # features are computed from aligned.iloc[:i+1] windowed - causal trailing only)
            feats = extract_persistence_features(
                a.iloc[: i + 1], b.iloc[: i + 1], lookback=self.lookback, min_obs=self.min_obs
            )
            gr = gate_persistence(feats, self.ml_model, threshold=self.ml_threshold)
            allow = gr.allow
            prob_val = gr.prob_persistent
            signals.loc[aligned.index[i], "ml_prob"] = (
                prob_val if prob_val is not None else np.nan
            )
            signals.loc[aligned.index[i], "ml_allow"] = 1.0 if allow else 0.0
            if i % 50 == 0 or not allow:
                self._gate_audit.append(
                    {
                        "t": str(aligned.index[i]),
                        "z": float(zi),
                        "want": float(want),
                        "allow": bool(allow),
                        "prob": gr.prob_persistent,
                        "reason": gr.reason,
                    }
                )
            pos.iloc[i] = want if allow else 0.0

        signals.loc[aligned.index, "zscore"] = z.values
        # dollar-neutral-ish weights per pair (gross normalized)
        gross = 1.0 + np.abs(hedge.reindex(aligned.index).fillna(1.0))
        w1 = pos / gross
        w2 = -pos * hedge.reindex(aligned.index).fillna(1.0) / gross
        signals.loc[aligned.index, asset1] = w1.values
        signals.loc[aligned.index, asset2] = w2.values
        return signals
