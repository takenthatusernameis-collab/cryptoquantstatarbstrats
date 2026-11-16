"""Tests for C328 runner (scripts/run_c328_variance_ratio_xsec_oos.py):
costed OOS cross-sectional intraday VARIANCE-RATIO (RANDOM-WALK-DEVIATION)
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

import run_c328_variance_ratio_xsec_oos as R  # noqa: E402


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


# ---------------------------------------------------------------- rolling variance
def test_rolling_var_min_periods_and_zero_variance():
    a = np.array([1., 2., 3., 4., 5., 6.])
    out = R._rolling_var_1d(a, 4)
    assert np.isnan(out[:3]).all()                      # < window -> NaN
    assert np.isclose(out[3], 5.0 / 3.0)               # var([1,2,3,4]) ddof=1
    assert np.isclose(out[5], 5.0 / 3.0)               # var([3,4,5,6])
    # zero window variance -> NaN (denominator<=0)
    b = np.full(5, 5.0)
    assert np.isnan(R._rolling_var_1d(b, 3)).all()
    # a non-finite observation inside a window -> NaN for that window (fail-closed)
    c = np.array([1., 2., np.nan, 4., 5.])
    assert np.isnan(R._rolling_var_1d(c, 3)).all()


def test_rolling_var_window_two_is_population_like():
    a = np.array([0., 2., 4., 8.])
    out = R._rolling_var_1d(a, 2)
    assert np.isclose(out[1], 2.0)   # var([0,2]) ddof=1 = 2
    assert np.isclose(out[2], 2.0)   # var([2,4]) = 2
    assert np.isclose(out[3], 8.0)   # var([4,8]) = 8


# ---------------------------------------------------------------- variance-ratio direction
def test_vr_ratio_trending_above_one_meanreverting_below():
    W = R.VR_WINDOW
    q = 8
    # monotonic ramp -> q-sum variance grows faster than q*1-bar variance -> VR > 1
    ramp = np.arange(W, dtype=float)
    var1 = R._rolling_var_1d(ramp, W)
    ramp_q = np.array([ramp[j:j + q].sum() for j in range(W - q + 1)])
    varq = R._rolling_var_1d(ramp_q, W - q + 1)
    vr_trend = varq[-1] / (q * var1[-1])
    assert np.isfinite(vr_trend) and vr_trend > 1.0, vr_trend
    # alternating + small noise -> q-sums nearly cancel -> VR < 1 (nonzero variance)
    rng = np.random.default_rng(5)
    alt = 1.0 * ((-1.0) ** np.arange(W)) + rng.normal(0.0, 0.05, W)
    var1a = R._rolling_var_1d(alt, W)
    alt_q = np.array([alt[j:j + q].sum() for j in range(W - q + 1)])
    varq_alt = R._rolling_var_1d(alt_q, W - q + 1)
    vr_alt = varq_alt[-1] / (q * var1a[-1])
    assert np.isfinite(vr_alt) and vr_alt < 1.0, vr_alt


# ---------------------------------------------------------------- synthetic panel
def _fill_rq(bs):
    lr = bs["log_return"]
    n_assets, n_bars = lr.shape
    cs = np.concatenate([np.zeros((n_assets, 1)), np.cumsum(lr, axis=1)], axis=1)
    for h in (4, 8, 16):
        rq = np.zeros((n_assets, n_bars), dtype=float)
        if n_bars >= h:
            rq[:, h - 1:] = cs[:, h:] - cs[:, :n_bars + 1 - h]
        bs[f"r_q{h}"] = rq


def _base_bs(n_days=12):
    n_bars = n_days * R.TOD_BARS_PER_DAY
    t = np.arange(n_bars)
    n = 3
    lr = np.zeros((n, n_bars))
    bs = {"log_return": lr, "perp_close": np.full((n, n_bars), 100.0),
          "tod_idx": (t % R.TOD_BARS_PER_DAY).astype(np.int64),
          "day_ord": (t // R.TOD_BARS_PER_DAY).astype(np.int64),
          "n_bars": n_bars, "n_days": n_days}
    _fill_rq(bs)
    return bs


def _bs_vr_regime(n_days=8, L=4):
    """Asset0 final day becomes strongly trend-like (monotonic ramp -> VR>>1, above
    baseline -> LOW score, short); asset2 final day becomes strongly mean-reverting
    (alternating + tiny noise -> VR<<1, below baseline -> HIGH score, long).
    Prior days are iid noise (VR~1) so the same-tod baseline is moderate."""
    n_bars = n_days * R.TOD_BARS_PER_DAY
    rng = np.random.default_rng(11)
    n = 3
    lr = rng.standard_normal((n, n_bars)) * 1e-3
    d0 = (n_days - 1) * R.TOD_BARS_PER_DAY
    idx = np.arange(R.TOD_BARS_PER_DAY)
    lr[0, d0:d0 + R.TOD_BARS_PER_DAY] = np.linspace(-1e-3, 1e-3, R.TOD_BARS_PER_DAY)
    lr[2, d0:d0 + R.TOD_BARS_PER_DAY] = 1e-3 * ((-1.0) ** idx) + rng.normal(0.0, 1e-5, R.TOD_BARS_PER_DAY)
    bs = {"log_return": lr, "perp_close": np.full((n, n_bars), 100.0),
          "tod_idx": (np.arange(n_bars) % R.TOD_BARS_PER_DAY).astype(np.int64),
          "day_ord": (np.arange(n_bars) // R.TOD_BARS_PER_DAY).astype(np.int64),
          "n_bars": n_bars, "n_days": n_days}
    _fill_rq(bs)
    return bs


def test_vr4_dev_high_short_low_long():
    bs = _bs_vr_regime(8, 4)
    sc = R.build_score(bs, "vr4_dev", 4)
    col = sc[:, -1]
    assert np.isfinite(col[0]) and np.isfinite(col[2])
    assert col[0] < 0.0 < col[2], col


def test_vr8_dev_high_short_low_long():
    bs = _bs_vr_regime(8, 4)
    sc = R.build_score(bs, "vr8_dev", 4)
    col = sc[:, -1]
    assert np.isfinite(col[0]) and np.isfinite(col[2])
    assert col[0] < 0.0 < col[2], col


def test_vr16_dev_high_short_low_long():
    bs = _bs_vr_regime(8, 4)
    sc = R.build_score(bs, "vr16_dev", 4)
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
    for sig in R.SIGNALS:
        sc = R.build_score(bs, sig, 10)  # L > days -> structural warmup, all NaN
        assert np.isnan(sc).all(), sig


def test_signals_nan_in_vr_window_warmup():
    """With zero returns the 1-bar variance is 0 -> VR is NaN everywhere (fail-closed
    on Var1<=0), never traded."""
    bs = _base_bs(6)
    for sig in R.SIGNALS:
        sc = R.build_score(bs, sig, 3)
        assert np.isnan(sc).all(), sig


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