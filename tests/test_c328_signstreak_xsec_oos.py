"""Tests for C328 runner (scripts/run_c328_signstreak_xsec_oos.py):
costed OOS cross-sectional intraday RETURN SIGN-RUN / DIRECTIONAL STREAK
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

import run_c328_signstreak_xsec_oos as R  # noqa: E402


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


# ---------------------------------------------------------------- trailing sum + ewm
def test_trailing_sum_min_periods_and_nan():
    a = np.arange(1.0, 11.0)
    out = R._trailing_sum_1d(a, 4)
    assert np.isnan(out[:3]).all()            # < L obs -> NaN
    assert np.isclose(out[3], 1.0 + 2.0 + 3.0 + 4.0)  # = 10
    assert np.isclose(out[-1], 7.0 + 8.0 + 9.0 + 10.0)  # = 34
    b = np.arange(1.0, 11.0); b[5] = np.nan
    out_b = R._trailing_sum_1d(b, 4)
    assert np.isnan(out_b[5])                 # window covers index 5
    assert np.isfinite(out_b[-1])             # tail window clean


def test_ewm_mean_causal_and_finite():
    rng = np.random.default_rng(3)
    vals = rng.standard_normal(50)
    out = R._ewm_mean_1d(vals, 0.3)
    assert out.shape == (50,)
    assert np.isfinite(out).all()
    # causal: first value equals itself
    assert np.isclose(out[0], vals[0])
    # recursion: out[t] = alpha*vals[t] + (1-alpha)*out[t-1]
    alpha = 0.3
    for t in range(1, 50):
        assert np.isclose(out[t], alpha * vals[t] + (1.0 - alpha) * out[t - 1])


# ---------------------------------------------------------------- sign-streak bucket stats
def test_bucket_signstreak_stats_structure():
    n_assets, n_bars = 2, 48
    bucket_idx = np.array([0, 1] * 24)
    sign_run = np.array([[1, 2, 1, 2] * 12, [2, 1, 2, 1] * 12], dtype=float)
    sign_chg = np.array([[0, 1, 0, 1] * 12, [0, 1, 0, 1] * 12], dtype=float)
    L = 6
    alpha = 0.3
    js = R.bucket_signstreak_stats(sign_run, sign_chg, bucket_idx, L, alpha)
    assert set(js) == {"streak", "signchg", "streak_ewm"}
    for k in js:
        assert js[k].shape == (n_assets, n_bars)


def test_bucket_signstreak_signchg_trailing_count():
    n_assets, n_bars = 1, 12
    bucket_idx = np.zeros(n_bars, dtype=np.int64)
    sign_run = np.zeros((n_assets, n_bars))
    sign_chg = np.ones((n_assets, n_bars))
    L = 4
    alpha = 0.3
    js = R.bucket_signstreak_stats(sign_run, sign_chg, bucket_idx, L, alpha)
    # signchg is trailing sum of sign_chg over L same-tod bars -> == L where valid
    for j in range(L - 1, n_bars):
        assert np.isclose(js["signchg"][0, j], L)


# ---------------------------------------------------------------- synthetic panel
def _base_bs(n_days=12):
    n_bars = n_days * R.TOD_BARS_PER_DAY
    t = np.arange(n_bars)
    tod_idx = (t % R.TOD_BARS_PER_DAY).astype(np.int64)
    day_ord = (t // R.TOD_BARS_PER_DAY).astype(np.int64)
    n = 3
    log_return = np.zeros((n, n_bars))
    sign_run = np.zeros((n, n_bars))
    sign_chg = np.zeros((n, n_bars))
    return {"log_return": log_return, "sign_run": sign_run, "sign_chg": sign_chg,
            "perp_close": np.full((n, n_bars), 100.0),
            "tod_idx": tod_idx, "day_ord": day_ord,
            "n_bars": n_bars, "n_days": n_days}


def _set_last3(bs, asset, day, vals_run, vals_chg):
    """Set sign_run/sign_chg on the last 3 bars of a given day for one asset."""
    n_bpd = R.TOD_BARS_PER_DAY
    start = day * n_bpd + (n_bpd - 3)
    bs["sign_run"][asset, start:start + 3] = vals_run
    bs["sign_chg"][asset, start:start + 3] = vals_chg


def _bs_streak_regime(n_days=6, L=4):
    """Regime change only on the LAST day so the trailing-L same-tod baseline at
    the final bar straddles the change for streak-based signals.
    asset0: early days choppy (streak=1), last day persistent (streak=3) -> above
    baseline -> short. asset2: early days persistent (streak=3), last day choppy
    (streak=1) -> below baseline -> long."""
    bs = _base_bs(n_days)
    last = n_days - 1
    for dd in range(n_days):
        if dd == last:
            a0_run, a0_chg = [1, 2, 3], [0, 0, 0]   # persistent run
            a2_run, a2_chg = [1, 1, 1], [0, 1, 1]   # choppy (resets)
        else:
            a0_run, a0_chg = [1, 1, 1], [0, 1, 1]   # choppy
            a2_run, a2_chg = [1, 2, 3], [0, 0, 0]   # persistent
        _set_last3(bs, 0, dd, a0_run, a0_chg)
        _set_last3(bs, 2, dd, a2_run, a2_chg)
    return bs


def _bs_signchg_regime(n_days=8, L=4):
    """Regime change at mid point so the trailing-L signchg baseline at the final
    bar straddles the change for signchg_dev.
    asset0: early persistent (sign_chg=0), late choppy (sign_chg=1) -> high ->
    short. asset2: early choppy (sign_chg=1), late persistent (sign_chg=0) ->
    low -> long."""
    bs = _base_bs(n_days)
    mid = n_days // 2
    for dd in range(n_days):
        late = dd >= mid
        a0_chg_last = 1 if late else 0
        a2_chg_last = 0 if late else 1
        _set_last3(bs, 0, dd, [1, 1, 1], [0, 0, a0_chg_last])
        _set_last3(bs, 2, dd, [1, 1, 1], [0, 0, a2_chg_last])
    return bs


def test_streak_dev_high_short_low_long():
    bs = _bs_streak_regime(6, 4)
    sc = R.build_score(bs, "streak_dev", 4)
    col = sc[:, -1]
    assert np.isfinite(col[0]) and np.isfinite(col[2])
    assert col[0] < 0.0 < col[2], col


def test_signchg_dev_high_short_low_long():
    bs = _bs_signchg_regime(8, 4)
    sc = R.build_score(bs, "signchg_dev", 4)
    col = sc[:, -1]
    assert np.isfinite(col[0]) and np.isfinite(col[2])
    assert col[0] < 0.0 < col[2], col


def test_streak_ewm_dev_high_short_low_long():
    bs = _bs_streak_regime(6, 4)
    sc = R.build_score(bs, "streak_ewm_dev", 4)
    col = sc[:, -1]
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
    # streak_dev and signchg_dev need min_periods=L same-tod obs -> all NaN
    # when L > days. streak_ewm_dev uses EWM (no min_periods floor) -> finite.
    sc = R.build_score(bs, "streak_dev", 10)
    assert np.isnan(sc).all(), "streak_dev"
    sc = R.build_score(bs, "signchg_dev", 10)
    assert np.isnan(sc).all(), "signchg_dev"
    sc = R.build_score(bs, "streak_ewm_dev", 10)
    assert np.isfinite(sc).all(), "streak_ewm_dev"


# ---------------------------------------------------------------- real artifacts schema (if present)
def _find_latest(prefix: str):
    files = sorted((ROOT / "reports").glob(f"campaign328_{prefix}_*.json"))
    files = [f for f in files if ".full." not in f.name]
    return files[-1] if files else None


def test_artifacts_if_present_have_required_flags():
    p = _find_latest("verdict")
    if p is None:
        return
    v = json.loads(p.read_text())
    assert v["campaign"] == 328
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
