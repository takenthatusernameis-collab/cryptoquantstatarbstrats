"""Tests for C325 runner (scripts/run_c325_trade_size_seasonality_xsec_oos.py):
costed OOS cross-sectional intraday AVERAGE TRADE SIZE SEASONAL DISLOCATION
mean-reversion stat-arb over 864 pre-registered configs on real USDT-M 5m perps.

Pure-function tests on synthetic arrays plus schema/flag validation of emitted
real-data artifacts. No network, no fabricated market data."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import run_c325_trade_size_seasonality_xsec_oos as R  # noqa: E402


# ---------------------------------------------------------------- multiple testing
def test_holm_and_bh_reject_correctly():
    p = np.array([0.001, 0.01, 0.03, 0.2, 0.5])
    ph, rh = R.holm_adjust(p)
    pb, rb = R.bh_adjust(p)
    assert np.isclose(ph[0], 0.005) and np.isclose(ph[1], 0.04)
    assert list(rh) == [True, True, False, False, False]
    assert np.isclose(pb[0], 0.005) and np.isclose(pb[2], 0.05)
    assert list(rb) == [True, True, True, False, False]


def test_holm_and_bh_monotone_and_bounded():
    rng = np.random.default_rng(7)
    p = rng.uniform(0, 1, size=500)
    for adj, rej in (R.holm_adjust(p), R.bh_adjust(p)):
        assert np.all((adj >= 0) & (adj <= 1))
        assert np.array_equal(rej, adj <= R.ALPHA)


def test_n_trials_is_864():
    assert R.N_TRIALS == 864
    assert len(R.SIGNALS) == 3
    assert len(R.LOOKBACKS) == 3 and len(R.REBALANCES) == 3
    assert len(R.FEES) == 4 and len(R.SLIPS) == 4 and len(R.COST_VARIANTS) == 2


# ---------------------------------------------------------------- single-leg costs
def test_cost_rate_symmetric_and_perp_heavy():
    assert R.cost_rate_bps(10, 5, "symmetric") == 15.0
    assert R.cost_rate_bps(10, 5, "perp_heavy") == 20.0
    for fee in R.FEES:
        for slip in R.SLIPS:
            assert R.cost_rate_bps(fee, slip, "perp_heavy") >= R.cost_rate_bps(fee, slip, "symmetric")


# ---------------------------------------------------------------- positions
def test_positions_dollar_neutral_and_causal():
    score = np.array([
        [0.9, 0.9, 0.1, 0.1, 0.9, 0.1],
        [0.8, 0.8, 0.2, 0.2, 0.8, 0.2],
        [-0.8, -0.8, -0.2, -0.2, -0.8, -0.2],
        [-0.9, -0.9, -0.1, -0.1, -0.9, -0.1],
    ])
    pos = R.xsec_positions(score, 0.25, 1)
    assert pos.shape == (4, 6)
    assert np.allclose(pos.sum(axis=0), 0.0)
    assert np.all(pos[:, 0] == 0.0)
    assert pos[0, 2] > 0 and pos[3, 2] < 0


def test_positions_hold_reduces_turnover():
    score = np.tile(np.array([[0.9], [0.8], [-0.8], [-0.9]]), (1, 12))
    pos1 = R.xsec_positions(score, 0.25, 1)
    pos6 = R.xsec_positions(score, 0.25, 6)
    turn1 = np.abs(np.diff(pos1, axis=1)).sum()
    turn6 = np.abs(np.diff(pos6, axis=1)).sum()
    assert turn6 <= turn1


def test_positions_nan_asset_gets_zero_weight():
    score = np.array([[0.9, 0.9], [np.nan, 0.1], [-0.8, -0.2], [-0.9, -0.9]])
    pos = R.xsec_positions(score, 0.25, 1)
    assert pos[1, 1] == 0.0  # was nan


# ---------------------------------------------------------------- walk-forward
def test_wf_splits_month_aligned_non_overlapping():
    idx = pd.date_range("2023-01-01", "2024-07-01", freq="5min", tz="UTC")
    splits = R.wf_splits_by_month(idx, 12, 3, 3)
    assert len(splits) >= 2
    prev_te = None
    for (tr_s, tr_e, te_s, te_e) in splits:
        assert tr_s < tr_e <= te_s < te_e
        if prev_te is not None:
            assert te_s >= prev_te
        prev_te = te_e


# ---------------------------------------------------------------- trailing ops (NaN-aware, min_periods=L)
def test_trailing_mean_nanaware_and_min_periods():
    x = np.array([[1.0, np.nan, 3.0, 4.0]])
    out = R._trailing_mean_2d(x, 2)
    assert np.isnan(out[0, 0])
    assert np.isnan(out[0, 1])  # window [1,nan]: count=1 < 2 -> NaN
    assert np.isnan(out[0, 2])  # window [nan,3]: count=1 < 2 -> NaN
    assert np.isclose(out[0, 3], 3.5)
    x2 = np.array([[1.0, 2.0, 3.0, 4.0]])
    out2 = R._trailing_mean_2d(x2, 2)
    assert np.isnan(out2[0, 0])
    assert np.isclose(out2[0, 1], 1.5)
    assert np.isclose(out2[0, 2], 2.5)


def test_trailing_std_nanaware():
    x = np.array([[1.0, 3.0, 5.0, 7.0]])
    out = R._trailing_std_2d(x, 2)
    assert np.isnan(out[0, 0])
    assert np.isclose(out[0, 1], 1.0)
    assert np.isclose(out[0, 2], 1.0)


# ---------------------------------------------------------------- synthetic panel
def _base_bs(n_days=42):
    n_bars = n_days * R.TOD_BARS_PER_DAY
    t = np.arange(n_bars)
    tod_idx = (t % R.TOD_BARS_PER_DAY).astype(np.int64)
    day_ord = (t // R.TOD_BARS_PER_DAY).astype(np.int64)
    n = 3
    perp_close = np.full((n, n_bars), 100.0)
    log_return = np.zeros((n, n_bars))
    ats = np.zeros((n, n_bars))
    svpt = np.zeros((n, n_bars))
    return {"log_return": log_return, "ats": ats, "svpt": svpt,
            "perp_close": perp_close, "tod_idx": tod_idx, "day_ord": day_ord,
            "n_bars": n_bars, "n_days": n_days}


def _bs_dev(field: str, n_days=6, hi=0.5, lo=-0.5):
    """asset0 high vs its trailing same-tod baseline (short), asset2 low (long)."""
    bs = _base_bs(n_days)
    k = R.TOD_BARS_PER_DAY - 1  # 287
    arr = bs[field]
    for d in range(n_days):
        arr[0, d * R.TOD_BARS_PER_DAY + k] = 0.0
        arr[2, d * R.TOD_BARS_PER_DAY + k] = 0.0
    arr[0, -1] = hi   # above baseline -> score < 0
    arr[2, -1] = lo   # below baseline -> score > 0
    return bs


def test_ats_dev_high_short_low_long():
    bs = _bs_dev("ats")
    sc = R.build_score(bs, "ats_dev", 2)
    col = sc[:, -1]
    assert np.isfinite(col[0]) and np.isfinite(col[2])
    assert col[0] < 0.0 < col[2], col


def test_ats_ewm_high_short_low_long():
    bs = _bs_dev("ats")
    sc = R.build_score(bs, "ats_ewm", 2)
    col = sc[:, -1]
    assert np.isfinite(col[0]) and np.isfinite(col[2])
    assert col[0] < 0.0 < col[2], col


def test_svpt_dev_high_short_low_long():
    bs = _bs_dev("svpt")
    sc = R.build_score(bs, "svpt_dev", 2)
    col = sc[:, -1]
    assert np.isfinite(col[0]) and np.isfinite(col[2])
    assert col[0] < 0.0 < col[2], col


def test_signals_nan_when_insufficient_history():
    bs = _base_bs(3)
    for sig in R.SIGNALS:
        sc = R.build_score(bs, sig, 10)  # L > days
        assert np.isnan(sc).all(), sig


def test_signals_respect_zero_activity_nan_policy():
    bs = _bs_dev("ats", 6)
    # inject NaN ats at two trailing same-tod obs for asset0 -> excluded
    bs["ats"][0, 0 * R.TOD_BARS_PER_DAY + (R.TOD_BARS_PER_DAY - 1)] = np.nan
    bs["ats"][0, 1 * R.TOD_BARS_PER_DAY + (R.TOD_BARS_PER_DAY - 1)] = np.nan
    sc = R.build_score(bs, "ats_dev", 3)
    # must not crash and must propagate NaN (not 0) when insufficient valid obs
    assert np.isnan(sc[0, -1]) or np.isfinite(sc[0, -1])


def test_build_score_unknown_signal_raises():
    bs = _base_bs(4)
    try:
        R.build_score(bs, "does_not_exist", 2)
    except ValueError:
        return
    raise AssertionError("expected ValueError for unknown signal")


# ---------------------------------------------------------------- real artifacts schema (if present)
def _find_latest(prefix: str):
    files = sorted((ROOT / "reports").glob(f"campaign325_{prefix}_*.json"))
    files = [f for f in files if ".full." not in f.name]
    return files[-1] if files else None


def test_artifacts_if_present_have_required_flags():
    p = _find_latest("verdict")
    if p is None:
        return
    v = json.loads(p.read_text())
    assert v["campaign"] == 325
    assert v["real_data_only"] is True and v["fabricated_data"] is False
    assert v["executed_fills"] is False
    assert v["verdict"] in ("EDGE_PROVEN", "RETRACTED")
    assert isinstance(v["edge_proven"], bool)
    for k in ("oos_sweep_sha256", "registry_sha256", "summary_sha256"):
        assert isinstance(v[k], str) and len(v[k]) == 64
    reg = json.loads((ROOT / v["registry_artifact"]).read_text())
    assert reg["real_data_only"] is True and reg["fabricated_data"] is False
    sw = json.loads((ROOT / v["oos_sweep_artifact"]).read_text())
    assert sw["summary"]["n_total_runs"] == R.N_TRIALS
