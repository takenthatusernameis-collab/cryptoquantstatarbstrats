from __future__ import annotations

import numpy as np
import pandas as pd

from utils.mtf_pairs import (
    MTFPairConfig,
    align_h1_to_m5_causal,
    backtest_mtf_pair,
    compute_h1_context,
    generate_mtf_signals,
)


def _m5_index(start="2026-10-01T00:00:00Z", periods=800):
    return pd.date_range(start=start, periods=periods, freq="5min", tz="UTC")


def _h1_from_m5(m5_index: pd.DatetimeIndex):
    # label 1h bars at their open times (floor to hour) for available_at = +1h
    h1 = pd.DatetimeIndex(sorted(set(m5_index.floor("1h"))))
    return h1


def test_align_h1_to_m5_causal_no_lookahead():
    m5 = _m5_index(periods=36)  # 3 hours
    h1_idx = pd.date_range("2026-10-01T00:00:00Z", periods=3, freq="1h", tz="UTC")
    h1 = pd.DataFrame({"x": [10.0, 20.0, 30.0]}, index=h1_idx)
    aligned = align_h1_to_m5_causal(h1, m5)
    # 00:00 1h bar closes at 01:00 -> available for 5m bars >= 01:00
    assert pd.isna(aligned.loc[pd.Timestamp("2026-10-01T00:55:00Z", tz="UTC"), "x"])
    assert aligned.loc[pd.Timestamp("2026-10-01T01:00:00Z", tz="UTC"), "x"] == 10.0
    assert aligned.loc[pd.Timestamp("2026-10-01T01:55:00Z", tz="UTC"), "x"] == 10.0
    assert aligned.loc[pd.Timestamp("2026-10-01T02:00:00Z", tz="UTC"), "x"] == 20.0


def test_generate_mtf_signals_fail_closed_on_missing_or_bad_gate():
    m5 = _m5_index(periods=400)
    p1 = pd.Series(100 * np.exp(np.cumsum(np.random.default_rng(0).normal(0, 0.001, len(m5)))), index=m5)
    p2 = pd.Series(50 * np.exp(np.cumsum(np.random.default_rng(1).normal(0, 0.001, len(m5)))), index=m5)
    ctx = pd.DataFrame({"beta": np.nan, "gate_ok": False}, index=m5)
    cfg = MTFPairConfig(pair=("A", "B"), min_shared_m5=100)
    sig = generate_mtf_signals(p1, p2, ctx, cfg)
    assert (sig["pos"] == 0).all()
    assert (sig["w1"] == 0).all()
    assert (sig["w2"] == 0).all()


def test_generate_mtf_signals_flat_when_insufficient_overlap():
    m5 = _m5_index(periods=50)
    p1 = pd.Series(np.linspace(100, 101, len(m5)), index=m5)
    p2 = pd.Series(np.linspace(50, 51, len(m5)), index=m5)
    ctx = pd.DataFrame({"beta": 1.0, "gate_ok": True}, index=m5)
    cfg = MTFPairConfig(pair=("A", "B"), min_shared_m5=600)
    sig = generate_mtf_signals(p1, p2, ctx, cfg)
    assert sig.empty


def test_compute_h1_context_fail_closed_with_insufficient_data():
    idx = pd.date_range("2026-10-01T00:00:00Z", periods=20, freq="1h", tz="UTC")
    p1 = pd.Series(np.linspace(100, 101, len(idx)), index=idx)
    p2 = pd.Series(np.linspace(50, 51, len(idx)), index=idx)
    cfg = MTFPairConfig(pair=("A", "B"), h1_lookback=168, min_shared_h1=240)
    ctx = compute_h1_context(p1, p2, cfg)
    assert "gate_ok" in ctx.columns
    assert (ctx["gate_ok"].fillna(False) == False).all()  # noqa: E712


def test_backtest_mtf_pair_reports_honest_status_on_short_data():
    m5 = _m5_index(periods=120)
    h1 = pd.date_range("2026-10-01T00:00:00Z", periods=24, freq="1h", tz="UTC")
    rng = np.random.default_rng(2)
    p1m = pd.Series(100 + np.cumsum(rng.normal(0, 0.1, len(m5))), index=m5)
    p2m = pd.Series(50 + np.cumsum(rng.normal(0, 0.05, len(m5))), index=m5)
    p1h = pd.Series(100 + np.cumsum(rng.normal(0, 0.2, len(h1))), index=h1)
    p2h = pd.Series(50 + np.cumsum(rng.normal(0, 0.1, len(h1))), index=h1)
    cfg = MTFPairConfig(pair=("A", "B"), min_shared_h1=240, min_shared_m5=600)
    res = backtest_mtf_pair(p1m, p2m, p1h, p2h, cfg)
    assert res["status"] == "blocked"
    assert "limitations" in res or "reason" in res
    assert res.get("blocked_routes") == [] or isinstance(res.get("blocked_routes"), list)
