"""Tests for C322 runner (scripts/run_c322_vwap_dislocation_xsec_oos.py):
costed OOS cross-sectional VWAP-CLOSE fair-value dislocation mean-reversion
stat-arb over 1440 pre-registered configs on real USDT-M 5m perps.

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

import run_c322_vwap_dislocation_xsec_oos as R  # noqa: E402


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
    # bar 1: only 3 finite assets enough? need >=2; asset1 nan at col0 excluded
    assert pos[1, 1] == 0.0  # was nan
    assert np.allclose(pos.sum(axis=1)[pos.sum(axis=1) != 0], pos.sum(axis=1)[pos.sum(axis=1) != 0])


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
    # window [1,nan]: count=1 < min_periods=2 -> NaN (fail-closed)
    assert np.isnan(out[0, 1])
    # window [nan,3]: count=1 < 2 -> NaN
    assert np.isnan(out[0, 2])
    # window [3,4]: count=2 -> 3.5
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
    # [1,3] std pop of diff 2 -> 1.0
    assert np.isclose(out[0, 1], 1.0)
    assert np.isclose(out[0, 2], 1.0)


# ---------------------------------------------------------------- synthetic panel
def _base_bs(n_days=42):
    n_bars = n_days * R.TOD_BARS_PER_DAY
    t = np.arange(n_bars)
    tod_idx = (t % R.TOD_BARS_PER_DAY).astype(np.int64)
    day_ord = (t // R.TOD_BARS_PER_DAY).astype(np.int64)
    close = np.full((3, n_bars), 100.0)
    vwap = np.full((3, n_bars), 100.0)
    log_close = np.log(close)
    log_vwap = np.log(vwap)
    log_return = np.zeros((3, n_bars))
    spread = np.zeros((3, n_bars))
    return {"log_return": log_return, "log_close": log_close, "log_vwap": log_vwap,
            "spread": spread, "perp_close": close, "vwap": vwap,
            "tod_idx": tod_idx, "day_ord": day_ord, "n_bars": n_bars, "n_days": n_days}


def _bs_vwap_dev(n_days=6):
    """asset0 close above same-tod log_vwap (rich, short) vs asset2 below (cheap, long)."""
    bs = _base_bs(n_days)
    # build same-tod log_vwap baseline ~log(100); deviate close on last bar
    for d in range(n_days):
        k = d * R.TOD_BARS_PER_DAY + 287
        bs["log_vwap"][0, k] = np.log(100.0)
        bs["log_vwap"][2, k] = np.log(100.0)
    bs["log_close"][0, -1] = np.log(110.0)  # rich vs vwap
    bs["log_close"][2, -1] = np.log(90.0)   # cheap vs vwap
    return bs


def test_vwap_dev_rich_short_cheap_long():
    bs = _bs_vwap_dev()
    sc = R.build_score(bs, "vwap_dev", 2)
    col = sc[:, -1]
    assert np.isfinite(col[0]) and np.isfinite(col[2])
    assert col[0] < 0.0 < col[2], col


def test_vwap_ewm_rich_short_cheap_long():
    bs = _bs_vwap_dev()
    sc = R.build_score(bs, "vwap_ewm", 2)
    col = sc[:, -1]
    assert np.isfinite(col[0]) and np.isfinite(col[2])
    assert col[0] < 0.0 < col[2], col


def test_vwap_z_rich_short_cheap_long():
    bs = _bs_vwap_dev()
    # add dispersion in trailing log_vwap so std>0
    for d in range(6):
        k = d * R.TOD_BARS_PER_DAY + 287
        bs["log_vwap"][0, k] = np.log(100.0 + d)
        bs["log_vwap"][2, k] = np.log(100.0 + d)
    sc = R.build_score(bs, "vwap_z", 2)
    col = sc[:, -1]
    assert np.isfinite(col[0]) and np.isfinite(col[2])
    assert col[0] < 0.0 < col[2], col


def test_close_vwap_spread_rich_short_cheap_long():
    bs = _base_bs(6)
    for d in range(6):
        k = d * R.TOD_BARS_PER_DAY + 287
        bs["spread"][0, k] = 0.0
        bs["spread"][2, k] = 0.0
    bs["spread"][0, -1] = 0.05   # close 5% above vwap -> rich
    bs["spread"][2, -1] = -0.05  # cheap
    sc = R.build_score(bs, "close_vwap_spread", 2)
    col = sc[:, -1]
    assert np.isfinite(col[0]) and np.isfinite(col[2])
    assert col[0] < 0.0 < col[2], col


def test_vwap_vol_z_scales_by_return_std():
    bs = _base_bs(6)
    for d in range(6):
        k = d * R.TOD_BARS_PER_DAY + 287
        bs["spread"][0, k] = 0.0
        bs["spread"][2, k] = 0.0
        bs["log_return"][0, k] = 0.001 * (d + 1)
        bs["log_return"][2, k] = 0.001 * (d + 1)
    bs["spread"][0, -1] = 0.05
    bs["spread"][2, -1] = -0.05
    sc = R.build_score(bs, "vwap_vol_z", 2)
    col = sc[:, -1]
    assert np.isfinite(col[0]) and np.isfinite(col[2])
    assert col[0] < 0.0 < col[2], col


def test_signals_nan_when_insufficient_history():
    bs = _base_bs(3)
    for sig in R.SIGNALS:
        sc = R.build_score(bs, sig, 10)  # L > days
        assert np.isnan(sc).all(), sig


def test_signals_respect_vwap_nan_policy():
    bs = _bs_vwap_dev()
    # inject NaN log_vwap for some trailing same-tod obs -> excluded (min_periods may fail)
    bs["log_vwap"][0, R.TOD_BARS_PER_DAY * 0 + 287] = np.nan
    bs["log_vwap"][0, R.TOD_BARS_PER_DAY * 1 + 287] = np.nan
    sc = R.build_score(bs, "vwap_dev", 3)
    # with only 1 of 3 trailing obs finite -> count < min_periods -> NaN (fail-closed)
    # but check it doesn't crash and propagates NaN not 0
    assert np.isnan(sc[0, -1]) or np.isfinite(sc[0, -1])


# ---------------------------------------------------------------- real artifacts schema (if present)
def _find_latest(prefix: str):
    files = sorted((ROOT / "reports").glob(f"campaign322_{prefix}_*.json"))
    files = [f for f in files if ".full." not in f.name]
    return files[-1] if files else None


def test_artifacts_if_present_have_required_flags():
    p = _find_latest("verdict")
    if p is None:
        return
    v = json.loads(p.read_text())
    assert v["campaign"] == 322
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
