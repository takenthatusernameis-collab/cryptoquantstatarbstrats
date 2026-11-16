"""Tests for C329 runner (scripts/run_c329_signentropy_xsec_oos.py):
costed OOS cross-sectional intraday RETURN SIGN ENTROPY / DIRECTIONAL DISORDER
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

import run_c329_signentropy_xsec_oos as R  # noqa: E402


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


# ---------------------------------------------------------------- trailing sign counts + entropy
def test_trailing_sign_counts_min_periods():
    signs = np.array([1.0, 1.0, -1.0, 1.0, -1.0, -1.0, 1.0, 1.0, 1.0, -1.0])
    pc, nc = R._trailing_sign_counts(signs, 4)
    assert np.isnan(pc[:3]).all()
    assert np.isclose(pc[3], 3.0)   # + + - + -> 3 plus
    assert np.isclose(nc[3], 1.0)   # 1 minus
    # signs[6:10] = [1,1,1,-1] -> 3 plus, 1 minus
    assert np.isclose(pc[-1], 3.0)
    assert np.isclose(nc[-1], 1.0)


def test_entropy_from_counts_balanced_and_skewed():
    # All plus: entropy = 0
    e = R._entropy_from_counts(np.array([4.0]), np.array([0.0]))
    assert np.isclose(e[0], 0.0)
    # Balanced 2+/2-: entropy = log(2)
    e = R._entropy_from_counts(np.array([2.0]), np.array([2.0]))
    assert np.isclose(e[0], np.log(2.0))
    # 3+/1-: entropy = -0.75*log(0.75) - 0.25*log(0.25)
    e = R._entropy_from_counts(np.array([3.0]), np.array([1.0]))
    expected = -0.75 * np.log(0.75) - 0.25 * np.log(0.25)
    assert np.isclose(e[0], expected)
    # No nonzero signs: entropy = NaN
    e = R._entropy_from_counts(np.array([0.0]), np.array([0.0]))
    assert np.isnan(e[0])


def test_ewm_mean_causal_and_finite():
    rng = np.random.default_rng(3)
    vals = rng.standard_normal(50)
    out = R._ewm_mean_1d(vals, 0.3)
    assert out.shape == (50,)
    assert np.isfinite(out).all()
    assert np.isclose(out[0], vals[0])
    alpha = 0.3
    for t in range(1, 50):
        assert np.isclose(out[t], alpha * vals[t] + (1.0 - alpha) * out[t - 1])


# ---------------------------------------------------------------- sign-entropy bucket stats
def test_bucket_signentropy_stats_structure():
    n_assets, n_bars = 2, 48
    bucket_idx = np.array([0, 1] * 24)
    sign = np.array([[1, -1, 1, -1] * 12, [1, 1, -1, -1] * 12], dtype=float)
    L = 6
    alpha = 0.3
    js = R.bucket_signentropy_stats(sign, bucket_idx, L, alpha)
    assert set(js) == {"entropy", "maxrun", "entropy_ewm"}
    for k in js:
        assert js[k].shape == (n_assets, n_bars)


def test_bucket_entropy_balanced_is_log2():
    n_assets, n_bars = 1, 12
    bucket_idx = np.zeros(n_bars, dtype=np.int64)
    # perfectly balanced signs: + - + - + - ...
    sign = np.array([[1, -1] * 6], dtype=float)
    L = 4
    alpha = 0.3
    js = R.bucket_signentropy_stats(sign, bucket_idx, L, alpha)
    # entropy over balanced window = log(2)
    for j in range(L - 1, n_bars):
        assert np.isclose(js["entropy"][0, j], np.log(2.0))


def test_bucket_entropy_one_sign_is_zero():
    n_assets, n_bars = 1, 12
    bucket_idx = np.zeros(n_bars, dtype=np.int64)
    # all plus signs: entropy = 0
    sign = np.ones((n_assets, n_bars), dtype=float)
    L = 4
    alpha = 0.3
    js = R.bucket_signentropy_stats(sign, bucket_idx, L, alpha)
    for j in range(L - 1, n_bars):
        assert np.isclose(js["entropy"][0, j], 0.0)


def test_bucket_maxrun_structure():
    n_assets, n_bars = 1, 12
    bucket_idx = np.zeros(n_bars, dtype=np.int64)
    sign = np.array([[1, 1, 1, -1, -1, 1, 1, 1, 1, -1, -1, -1]], dtype=float)
    L = 4
    alpha = 0.3
    js = R.bucket_signentropy_stats(sign, bucket_idx, L, alpha)
    # At j=5 (window idx 2..5 = [1,-1,-1,1]), max run = 2
    assert np.isclose(js["maxrun"][0, 5], 2.0)


# ---------------------------------------------------------------- synthetic panel
TARGET_TOD = 100  # a fixed bar-of-day position used to control cross-day signs


def _base_bs(n_days=8):
    n_bars = n_days * R.TOD_BARS_PER_DAY
    t = np.arange(n_bars)
    tod_idx = (t % R.TOD_BARS_PER_DAY).astype(np.int64)
    day_ord = (t // R.TOD_BARS_PER_DAY).astype(np.int64)
    n = 3
    log_return = np.zeros((n, n_bars))
    sign = np.zeros((n, n_bars))
    return {"log_return": log_return, "sign": sign,
            "perp_close": np.full((n, n_bars), 100.0),
            "tod_idx": tod_idx, "day_ord": day_ord,
            "n_bars": n_bars, "n_days": n_days}


def _set_tod(bs, asset, day, val):
    """Set sign at TARGET_TOD of a given day for one asset; all other bars stay 0."""
    bs["sign"][asset, day * R.TOD_BARS_PER_DAY + TARGET_TOD] = val


def _bs_entropy_regime(n_days=8, L=4):
    """Regime change in the trailing-L window at the final bar for entropy_dev.
    asset0: early days biased (+), trailing window balanced -> entropy above
    baseline -> short. asset2: early days balanced, trailing window biased ->
    entropy below baseline -> long.
    Signs at TARGET_TOD across days:
      asset0: [+,+,+,+, +,-,+,-]  (days 0-3 +, days 4-7 balanced)
      asset2: [+,-,+,-, +,+,+,+]  (days 0-3 balanced, days 4-7 +)"""
    bs = _base_bs(n_days)
    for dd in range(4):
        _set_tod(bs, 0, dd, 1.0)
    for k, dd in enumerate(range(4, n_days)):
        _set_tod(bs, 0, dd, 1.0 if k % 2 == 0 else -1.0)
    for k, dd in enumerate(range(4)):
        _set_tod(bs, 2, dd, 1.0 if k % 2 == 0 else -1.0)
    for dd in range(4, n_days):
        _set_tod(bs, 2, dd, 1.0)
    return bs


def _bs_maxrun_regime(n_days=8, L=4):
    """Regime change in the trailing-L window at the final bar for maxrun_dev.
    asset0: early days choppy (maxrun=1), trailing window persistent (maxrun=4) ->
    above baseline -> short. asset2: early days persistent (maxrun=4), trailing
    window choppy (maxrun=1) -> below baseline -> long.
    Signs at TARGET_TOD across days:
      asset0: [+,-,+,-, +,+,+,+]  (days 0-3 choppy, days 4-7 +)
      asset2: [+,+,+,+, +,-,+,-]  (days 0-3 +, days 4-7 choppy)"""
    bs = _base_bs(n_days)
    for k, dd in enumerate(range(4)):
        _set_tod(bs, 0, dd, 1.0 if k % 2 == 0 else -1.0)
    for dd in range(4, n_days):
        _set_tod(bs, 0, dd, 1.0)
    for dd in range(4):
        _set_tod(bs, 2, dd, 1.0)
    for k, dd in enumerate(range(4, n_days)):
        _set_tod(bs, 2, dd, 1.0 if k % 2 == 0 else -1.0)
    return bs


def _target_col(bs, day_index=-1):
    """Column index of TARGET_TOD on the given day (default: final day)."""
    return day_index * R.TOD_BARS_PER_DAY + TARGET_TOD


def test_entropy_dev_high_short_low_long():
    bs = _bs_entropy_regime(8, 4)
    sc = R.build_score(bs, "entropy_dev", 4)
    col = sc[:, _target_col(bs)]
    assert np.isfinite(col[0]) and np.isfinite(col[2])
    # asset0: trailing-window entropy above baseline -> short (score < 0)
    # asset2: trailing-window entropy below baseline -> long (score > 0)
    assert col[0] < 0.0 < col[2], col


def test_maxrun_dev_high_short_low_long():
    bs = _bs_maxrun_regime(8, 4)
    sc = R.build_score(bs, "maxrun_dev", 4)
    col = sc[:, _target_col(bs)]
    assert np.isfinite(col[0]) and np.isfinite(col[2])
    # asset0: trailing-window maxrun above baseline -> short (score < 0)
    # asset2: trailing-window maxrun below baseline -> long (score > 0)
    assert col[0] < 0.0 < col[2], col


def test_entropy_ewm_dev_high_short_low_long():
    bs = _bs_entropy_regime(8, 4)
    sc = R.build_score(bs, "entropy_ewm_dev", 4)
    col = sc[:, _target_col(bs)]
    assert np.isfinite(col[0]) and np.isfinite(col[2])
    assert col[0] < 0.0 < col[2], col


def test_signals_are_zero_at_target_tod_warmup():
    # On the first day the same-tod bucket has < L observations, so every
    # seasonal-dislocation signal must be NaN there (fail-closed min_periods).
    bs = _bs_entropy_regime(8, 4)
    for sig in ("entropy_dev", "entropy_ewm_dev", "maxrun_dev"):
        sc = R.build_score(bs, sig, 4)
        assert np.isnan(sc[:, _target_col(bs, 0)]).all(), sig


def test_build_score_unknown_signal_raises():
    bs = _base_bs(4)
    try:
        R.build_score(bs, "does_not_exist", 2)
    except ValueError:
        return
    raise AssertionError("expected ValueError for unknown signal")


def test_signals_nan_when_insufficient_history():
    bs = _base_bs(3)
    # With all-zero signs and L=10 > 3 days, every trailing window has
    # insufficient observations (and no nonzero signs), so all stats are NaN.
    sc = R.build_score(bs, "entropy_dev", 10)
    assert np.isnan(sc).all(), "entropy_dev"
    sc = R.build_score(bs, "maxrun_dev", 10)
    assert np.isnan(sc).all(), "maxrun_dev"
    sc = R.build_score(bs, "entropy_ewm_dev", 10)
    assert np.isnan(sc).all(), "entropy_ewm_dev"


# ---------------------------------------------------------------- real artifacts schema (if present)
def _find_latest(prefix: str):
    files = sorted((ROOT / "reports").glob(f"campaign329_{prefix}_*.json"))
    files = [f for f in files if ".full." not in f.name]
    return files[-1] if files else None


def test_artifacts_if_present_have_required_flags():
    p = _find_latest("verdict")
    if p is None:
        return
    v = json.loads(p.read_text())
    assert v["campaign"] == 329
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
