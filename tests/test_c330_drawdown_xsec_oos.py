"""Tests for C330 runner (scripts/run_c330_drawdown_xsec_oos.py):
costed OOS cross-sectional intraday RETURN-PATH DRAWDOWN / RUNUP / PATH-EFFICIENCY
SEASONAL DISLOCATION mean-reversion stat-arb over 864 pre-registered configs on
real USDT-M 5m perps.

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

import run_c330_drawdown_xsec_oos as R  # noqa: E402


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


# ---------------------------------------------------------------- trailing same-tod stats
def test_trailing_mean_2d_min_periods_requires_l_finite():
    # min_periods=L: a window with any NaN has < L finite obs -> NaN (fail-closed).
    vals = np.array([[1.0, 2.0, np.nan, 4.0, 5.0]])
    tm = R._trailing_mean_2d(vals, 2)
    assert np.isnan(tm[0, 0])              # < L obs
    assert np.isclose(tm[0, 1], 1.5)       # (1+2)/2
    assert np.isnan(tm[0, 2])              # window [2, nan] -> 1 finite < L
    assert np.isnan(tm[0, 3])              # window [nan, 4] -> 1 finite < L
    assert np.isclose(tm[0, 4], 4.5)       # (4+5)/2


def test_trailing_mean_2d_all_nan_window_is_nan():
    vals = np.array([[np.nan, np.nan, 1.0]])
    tm = R._trailing_mean_2d(vals, 2)
    assert np.isnan(tm[0, 1])              # all-NaN window
    assert np.isnan(tm[0, 2])              # only 1 finite < L


def test_bucket_trailing_stats_same_tod_structure():
    tod = np.array([0, 1, 0, 1, 0, 1], dtype=np.int64)
    vals = np.array([[10.0, 100.0, 20.0, 200.0, 30.0, 300.0]])
    tm = R.bucket_trailing_stats(vals, tod, 2)
    # bucket 0 values: 10,20,30 -> mean at idx4 = 25
    assert np.isclose(tm[0, 4], 25.0)
    # bucket 1 values: 100,200,300 -> mean at idx5 = 250
    assert np.isclose(tm[0, 5], 250.0)


# ---------------------------------------------------------------- synthetic panel
TARGET_TOD = 100
N_DAYS = 8


def _base_bs(n_days=N_DAYS):
    n_bars = n_days * R.TOD_BARS_PER_DAY
    t = np.arange(n_bars)
    tod_idx = (t % R.TOD_BARS_PER_DAY).astype(np.int64)
    day_ord = (t // R.TOD_BARS_PER_DAY).astype(np.int64)
    n = 3
    return {
        "log_return": np.zeros((n, n_bars)),
        "perp_close": np.full((n, n_bars), 100.0),
        "cumret": np.zeros((n, n_bars)),
        "drawdown": np.zeros((n, n_bars)),
        "runup": np.zeros((n, n_bars)),
        "path_eff": np.full((n, n_bars), 0.5),
        "tod_idx": tod_idx, "day_ord": day_ord,
        "n_bars": n_bars, "n_days": n_days,
    }


def _set_tod(bs, field, asset, day, val):
    bs[field][asset, day * R.TOD_BARS_PER_DAY + TARGET_TOD] = val


def _target_col(day_index=-1):
    return day_index * R.TOD_BARS_PER_DAY + TARGET_TOD


def _bs_dd_regime():
    """asset0: deep drawdown returns on the final day -> score > 0 (long).
    asset2: drawdown is shallow on the final day vs deep baseline -> score < 0."""
    bs = _base_bs()
    for d in range(4):
        _set_tod(bs, "drawdown", 0, d, -5.0)
        _set_tod(bs, "drawdown", 2, d, -1.0)
    for d in range(4, 7):
        _set_tod(bs, "drawdown", 0, d, -1.0)
        _set_tod(bs, "drawdown", 2, d, -5.0)
    _set_tod(bs, "drawdown", 0, 7, -5.0)
    _set_tod(bs, "drawdown", 2, 7, -1.0)
    return bs


def _bs_runup_regime():
    """asset0: high runup on final day -> score < 0 (short).
    asset2: low runup on final day vs high baseline -> score > 0 (long)."""
    bs = _base_bs()
    for d in range(7):
        _set_tod(bs, "runup", 0, d, 1.0)
        _set_tod(bs, "runup", 2, d, 5.0)
    _set_tod(bs, "runup", 0, 7, 5.0)
    _set_tod(bs, "runup", 2, 7, 1.0)
    return bs


def _bs_eff_regime():
    """asset0: high path efficiency on final day -> score < 0 (short).
    asset2: low path efficiency on final day vs high baseline -> score > 0 (long)."""
    bs = _base_bs()
    for d in range(7):
        _set_tod(bs, "path_eff", 0, d, 0.1)
        _set_tod(bs, "path_eff", 2, d, 0.9)
    _set_tod(bs, "path_eff", 0, 7, 0.9)
    _set_tod(bs, "path_eff", 2, 7, 0.1)
    return bs


def test_dd_dev_deep_drawdown_long_shallow_short():
    sc = R.build_score(_bs_dd_regime(), "dd_dev", 4)
    col = sc[:, _target_col()]
    assert np.isfinite(col[0]) and np.isfinite(col[2])
    assert col[0] > 0.0 > col[2], col


def test_runup_dev_high_runup_short_low_long():
    sc = R.build_score(_bs_runup_regime(), "runup_dev", 4)
    col = sc[:, _target_col()]
    assert np.isfinite(col[0]) and np.isfinite(col[2])
    assert col[0] < 0.0 < col[2], col


def test_eff_dev_high_efficiency_short_low_long():
    sc = R.build_score(_bs_eff_regime(), "eff_dev", 4)
    col = sc[:, _target_col()]
    assert np.isfinite(col[0]) and np.isfinite(col[2])
    assert col[0] < 0.0 < col[2], col


def test_build_score_unknown_signal_raises():
    bs = _base_bs(4)
    try:
        R.build_score(bs, "does_not_exist", 2)
    except ValueError:
        return
    raise AssertionError("expected ValueError for unknown signal")


def test_signals_nan_when_insufficient_history():
    bs = _base_bs(3)
    for sig in R.SIGNALS:
        sc = R.build_score(bs, sig, 10)
        assert np.isnan(sc).all(), sig


def test_path_eff_nan_propagates_fail_closed():
    bs = _base_bs()
    # inject a path_eff NaN on the final day for asset 1
    bs["path_eff"][1, _target_col()] = np.nan
    sc = R.build_score(bs, "eff_dev", 4)
    assert np.isnan(sc[1, _target_col()])


# ---------------------------------------------------------------- real artifacts schema (if present)
def _find_latest(prefix: str):
    files = sorted((ROOT / "reports").glob(f"campaign330_{prefix}_*.json"))
    files = [f for f in files if ".full." not in f.name]
    return files[-1] if files else None


def test_artifacts_if_present_have_required_flags():
    p = _find_latest("verdict")
    if p is None:
        return
    v = json.loads(p.read_text())
    assert v["campaign"] == 330
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
    assert sw["real_data_only"] is True and sw["fabricated_data"] is False


def test_cache_meta_fields_are_genuinely_distinct():
    meta = json.loads((ROOT / "data" / "cache" / "campaign330_drawdown_5m.meta.json").read_text())
    assert meta["campaign"] == 330
    assert meta["source_campaign"] == 312
    for f in ("cumret", "drawdown", "runup", "path_eff"):
        assert f in meta["fields"]
    # genuinely-distinct from C328/C329 sign fields
    assert "sign" not in meta["fields"]