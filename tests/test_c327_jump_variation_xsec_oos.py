"""Tests for C327 runner (scripts/run_c327_jump_variation_xsec_oos.py):
costed OOS cross-sectional intraday SIGNED JUMP-VARIATION (DISCONTINUITY)
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

import run_c327_jump_variation_xsec_oos as R  # noqa: E402


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


# ---------------------------------------------------------------- trailing sum + jump stats
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


def test_bucket_jump_stats_rv_bv_structure():
    n_assets, n_bars = 2, 48
    bucket_idx = np.array([0, 1] * 24)
    rng = np.random.default_rng(3)
    r = rng.standard_normal((n_assets, n_bars))
    r2 = r * r
    signed_r2 = r * np.abs(r)
    bip = np.zeros_like(r)
    bip[1:] = np.abs(r[1:]) * np.abs(r[:-1])
    L = 6
    js = R.bucket_jump_stats(r2, signed_r2, bip, bucket_idx, L)
    assert set(js) == {"rv", "bv", "jv", "rv_bv", "jv_ratio", "sjv"}
    for k in js:
        assert js[k].shape == (n_assets, n_bars)
    # RV == sum r^2; BV == pi/2 * sum bipower; JV == max(RV-BV,0)
    for b in (0, 1):
        pos = np.where(bucket_idx == b)[0]
        for i in range(n_assets):
            sub_r2 = r2[i, pos]
            sub_bip = bip[i, pos]
            for j in range(L - 1, len(pos)):
                win_r2 = sub_r2[j - L + 1:j + 1]
                win_bip = sub_bip[j - L + 1:j + 1]
                assert np.isclose(js["rv"][i, pos[j]], win_r2.sum())
                assert np.isclose(js["bv"][i, pos[j]], R.PI_OVER_2 * win_bip.sum())
                assert np.isclose(js["jv"][i, pos[j]], max(win_r2.sum() - R.PI_OVER_2 * win_bip.sum(), 0.0))


def test_bucket_jump_stats_denominator_nan():
    n_assets, n_bars = 1, 12
    bucket_idx = np.zeros(n_bars, dtype=np.int64)
    r = np.zeros((n_assets, n_bars))
    r2 = np.zeros((n_assets, n_bars))
    signed_r2 = np.zeros((n_assets, n_bars))
    bip = np.zeros((n_assets, n_bars))
    js = R.bucket_jump_stats(r2, signed_r2, bip, bucket_idx, 4)
    # all zero -> RV=0, BV=0 -> jv_ratio/rv_bv/sjv NaN (denominator<=0)
    assert np.isnan(js["jv_ratio"]).all()
    assert np.isnan(js["rv_bv"]).all()
    assert np.isnan(js["sjv"]).all()


# ---------------------------------------------------------------- synthetic panel
def _base_bs(n_days=12):
    n_bars = n_days * R.TOD_BARS_PER_DAY
    t = np.arange(n_bars)
    tod_idx = (t % R.TOD_BARS_PER_DAY).astype(np.int64)
    day_ord = (t // R.TOD_BARS_PER_DAY).astype(np.int64)
    n = 3
    log_return = np.zeros((n, n_bars))
    r2 = np.zeros((n, n_bars))
    abs_r = np.zeros((n, n_bars))
    signed_r2 = np.zeros((n, n_bars))
    bipower = np.zeros((n, n_bars))
    return {"log_return": log_return, "r2": r2, "abs_r": abs_r,
            "signed_r2": signed_r2, "bipower": bipower,
            "perp_close": np.full((n, n_bars), 100.0),
            "tod_idx": tod_idx, "day_ord": day_ord,
            "n_bars": n_bars, "n_days": n_days}


def _fill_jump_inputs(bs):
    bs["r2"] = bs["log_return"] * bs["log_return"]
    bs["abs_r"] = np.abs(bs["log_return"])
    bs["signed_r2"] = bs["log_return"] * bs["abs_r"]
    bs["bipower"][:, 1:] = bs["abs_r"][:, 1:] * bs["abs_r"][:, :-1]


def _bs_jump_regime(n_days=12, L=4):
    """Binary jumpiness trend across the late regime (last L days), so the final
    same-tod observation deviates from its trailing baseline for all three signals.
    asset0: late regime becomes MORE jumpy -> above baseline -> short (score<0).
    asset2: late regime becomes LESS jumpy -> below baseline -> long (score>0).
    Burst at 3 consecutive bars (k-2,k-1,k) per day so bipower > 0 everywhere."""
    bs = _base_bs(n_days)
    k = R.TOD_BARS_PER_DAY - 1
    JUMPY = np.array([0.02, 0.001, 0.02])   # high jump-ness (RV >> BV)
    SMOOTH = np.array([0.01, 0.01, 0.01])  # low jump-ness (RV <= BV => JV=0)
    for dd in range(n_days):
        base_idx = dd * R.TOD_BARS_PER_DAY + (k - 2)
        if dd < n_days - L:
            bs["log_return"][0, base_idx:base_idx + 3] = SMOOTH
            bs["log_return"][2, base_idx:base_idx + 3] = JUMPY
        else:
            # late regime: asset0 smooth->jumpy (rising), asset2 jumpy->smooth (falling)
            if dd < n_days - L + 2:
                a0, a2 = SMOOTH, JUMPY
            else:
                a0, a2 = JUMPY, SMOOTH
            bs["log_return"][0, base_idx:base_idx + 3] = a0
            bs["log_return"][2, base_idx:base_idx + 3] = a2
    _fill_jump_inputs(bs)
    return bs


def test_sjv_dev_high_short_low_long():
    bs = _bs_jump_regime(12, 4)
    sc = R.build_score(bs, "sjv_dev", 4)
    col = sc[:, -1]
    assert np.isfinite(col[0]) and np.isfinite(col[2])
    assert col[0] < 0.0 < col[2], col


def test_jv_ratio_dev_high_short_low_long():
    bs = _bs_jump_regime(12, 4)
    sc = R.build_score(bs, "jv_ratio_dev", 4)
    col = sc[:, -1]
    assert np.isfinite(col[0]) and np.isfinite(col[2])
    assert col[0] < 0.0 < col[2], col


def test_rv_bv_dev_high_short_low_long():
    bs = _bs_jump_regime(12, 4)
    sc = R.build_score(bs, "rv_bv_dev", 4)
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


# ---------------------------------------------------------------- real artifacts schema (if present)
def _find_latest(prefix: str):
    files = sorted((ROOT / "reports").glob(f"campaign327_{prefix}_*.json"))
    files = [f for f in files if ".full." not in f.name]
    return files[-1] if files else None


def test_artifacts_if_present_have_required_flags():
    p = _find_latest("verdict")
    if p is None:
        return
    v = json.loads(p.read_text())
    assert v["campaign"] == 327
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
