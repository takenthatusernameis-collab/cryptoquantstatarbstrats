"""Tests for C326 runner (scripts/run_c326_autocorr_seasonality_xsec_oos.py):
costed OOS cross-sectional intraday RETURN AUTOCORRELATION SEASONAL DISLOCATION
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

import run_c326_autocorr_seasonality_xsec_oos as R  # noqa: E402


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


# ---------------------------------------------------------------- autocorr ops
def test_rolling_autocorr_monotone_and_alternating():
    up = np.arange(1.0, 13.0)
    out_up = R._rolling_autocorr_1d(up, 6, 1)
    assert np.isnan(out_up[0]) and np.isnan(out_up[4])   # warmup (<L obs)
    assert np.isclose(out_up[-1], 1.0)                    # monotone -> +1
    alt = np.array([1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1], dtype=float)
    out_alt = R._rolling_autocorr_1d(alt, 6, 1)
    assert np.isclose(out_alt[-1], -1.0)                  # alternating -> -1


def test_rolling_autocorr_zero_variance_and_short_nan():
    const = np.ones(12)
    assert np.isnan(R._rolling_autocorr_1d(const, 6, 1)[-1])   # denom<=0 -> NaN
    short = np.arange(4.0)
    assert np.isnan(R._rolling_autocorr_1d(short, 6, 1)).all()  # n<L -> all NaN


def test_rolling_autocorr_ignores_nonfinite_windows():
    a = np.arange(1.0, 13.0)
    a[2] = np.nan  # contaminates windows covering index 2
    out = R._rolling_autocorr_1d(a, 6, 1)
    # window [0..5],[1..6],...,[2..7] contain idx2 -> NaN; later windows clean
    assert np.isnan(out[5]) and np.isnan(out[7])
    assert np.isfinite(out[11])


def test_bucket_autocorr_matches_direct_per_bucket():
    n_assets = 2
    n_bars = 24
    bucket_idx = np.array([0, 1] * 12)  # two interleaved buckets
    rng = np.random.default_rng(3)
    r = rng.standard_normal((n_assets, n_bars))
    L, lag = 5, 1
    out = R.bucket_autocorr(r, bucket_idx, L, lag)
    assert out.shape == (n_assets, n_bars)
    for b in (0, 1):
        pos = np.where(bucket_idx == b)[0]
        for i in range(n_assets):
            direct = R._rolling_autocorr_1d(r[i, pos], L, lag)
            assert np.allclose(out[i, pos], direct, equal_nan=True)


# ---------------------------------------------------------------- synthetic panel
def _base_bs(n_days=12):
    n_bars = n_days * R.TOD_BARS_PER_DAY
    t = np.arange(n_bars)
    tod_idx = (t % R.TOD_BARS_PER_DAY).astype(np.int64)
    day_ord = (t // R.TOD_BARS_PER_DAY).astype(np.int64)
    n = 3
    log_return = np.zeros((n, n_bars))
    abs_log_return = np.zeros((n, n_bars))
    return {"log_return": log_return, "abs_log_return": abs_log_return,
            "perp_close": np.full((n, n_bars), 100.0),
            "tod_idx": tod_idx, "day_ord": day_ord,
            "n_bars": n_bars, "n_days": n_days}


def _bs_regime(field: str, n_days=12, L=4):
    """asset0 autocorr rises above baseline (short); asset2 falls below (long)."""
    bs = _base_bs(n_days)
    k = R.TOD_BARS_PER_DAY - 1
    arr = bs[field]
    for dd in range(n_days):
        if dd < n_days - L:
            arr[0, dd * R.TOD_BARS_PER_DAY + k] = 0.01 if (dd % 2 == 0) else -0.01
        else:
            arr[0, dd * R.TOD_BARS_PER_DAY + k] = 0.001 * (dd - (n_days - L) + 1)
        if dd < n_days - L:
            arr[2, dd * R.TOD_BARS_PER_DAY + k] = 0.001 * (dd + 1)
        else:
            arr[2, dd * R.TOD_BARS_PER_DAY + k] = 0.01 if ((dd - (n_days - L)) % 2 == 0) else -0.01
    bs["abs_log_return"] = np.abs(bs["log_return"])
    return bs


def test_ac1_dev_high_short_low_long():
    bs = _bs_regime("log_return", 12, 4)
    sc = R.build_score(bs, "ac1_dev", 4)
    col = sc[:, -1]
    assert np.isfinite(col[0]) and np.isfinite(col[2])
    assert col[0] < 0.0 < col[2], col


def test_ac2_dev_high_short_low_long():
    # lag-2 regime shift: asset0 baseline lag2=-1 (period-4) -> last lag2=+1 (rising);
    # asset2 baseline lag2=+1 (increasing) -> last lag2=-1 (period-4).
    n_days, L = 24, 8
    bs = _base_bs(n_days)
    k = R.TOD_BARS_PER_DAY - 1

    def p4(dd):
        return [0.02, 0.01, -0.02, -0.01][dd % 4]

    def inc(dd):
        return 0.001 * (dd + 1)

    for dd in range(n_days):
        if dd < n_days - L:
            bs["log_return"][0, dd * R.TOD_BARS_PER_DAY + k] = p4(dd)
            bs["log_return"][2, dd * R.TOD_BARS_PER_DAY + k] = inc(dd)
        else:
            bs["log_return"][0, dd * R.TOD_BARS_PER_DAY + k] = inc(dd - (n_days - L))
            bs["log_return"][2, dd * R.TOD_BARS_PER_DAY + k] = p4(dd - (n_days - L))
    bs["abs_log_return"] = np.abs(bs["log_return"])
    sc = R.build_score(bs, "ac2_dev", L)
    col = sc[:, -1]
    assert np.isfinite(col[0]) and np.isfinite(col[2])
    assert col[0] < 0.0 < col[2], col


def test_absac1_dev_uses_abs_log_return():
    bs = _base_bs(12)
    k = R.TOD_BARS_PER_DAY - 1
    L = 4
    # build |log_return| with a regime shift: asset0 clustering rises, asset2 falls
    for dd in range(12):
        if dd < 12 - L:
            bs["abs_log_return"][0, dd * R.TOD_BARS_PER_DAY + k] = 0.01 if (dd % 2 == 0) else -0.01
            bs["abs_log_return"][2, dd * R.TOD_BARS_PER_DAY + k] = 0.001 * (dd + 1)
        else:
            bs["abs_log_return"][0, dd * R.TOD_BARS_PER_DAY + k] = 0.001 * (dd - (12 - L) + 1)
            bs["abs_log_return"][2, dd * R.TOD_BARS_PER_DAY + k] = 0.01 if ((dd - (12 - L)) % 2 == 0) else -0.01
    sc = R.build_score(bs, "absac1_dev", L)
    col = sc[:, -1]
    assert np.isfinite(col[0]) and np.isfinite(col[2])
    assert col[0] < 0.0 < col[2], col


def test_signals_nan_when_insufficient_history():
    bs = _base_bs(3)
    for sig in R.SIGNALS:
        sc = R.build_score(bs, sig, 10)  # L > days -> structural warmup, all NaN
        assert np.isnan(sc).all(), sig


def test_build_score_unknown_signal_raises():
    bs = _base_bs(4)
    try:
        R.build_score(bs, "does_not_exist", 2)
    except ValueError:
        return
    raise AssertionError("expected ValueError for unknown signal")


# ---------------------------------------------------------------- real artifacts schema (if present)
def _find_latest(prefix: str):
    files = sorted((ROOT / "reports").glob(f"campaign326_{prefix}_*.json"))
    files = [f for f in files if ".full." not in f.name]
    return files[-1] if files else None


def test_artifacts_if_present_have_required_flags():
    p = _find_latest("verdict")
    if p is None:
        return
    v = json.loads(p.read_text())
    assert v["campaign"] == 326
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