"""Tests for C429 runner (scripts/run_c429_signet_xsec_oos.py): pure-function
tests on synthetic arrays (including a brute-force equality test for the
vectorized SIGNENTROPY kernel vs the per-window explicit order-1 Markov
transition matrix reference) plus schema/flag validation of emitted
real-data artifacts. No network, no fabricated market data."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import run_c429_signet_xsec_oos as R  # noqa: E402


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


def test_n_trials_matches_pre_registered_grid_product():
    assert R.N_TRIALS == 2592
    assert len(R.SIGNALS) == 8
    assert len(R.LOOKBACKS) == 6
    assert len(R.REBALANCES) == 3
    assert len(R.FEES) == 3 and len(R.SLIPS) == 3 and len(R.COST_VARIANTS) == 2
    assert R.N_TRIALS == (len(R.SIGNALS) * len(R.LOOKBACKS) * len(R.REBALANCES)
                          * len(R.FEES) * len(R.SLIPS) * len(R.COST_VARIANTS))
    for pb in ("signentropy_trans_entropy_placebo", "signentropy_trans_asym_placebo",
               "signentropy_p_stay_placebo", "signentropy_p_switch_placebo"):
        assert pb in R.SIGNALS
    for real in ("signentropy_trans_entropy_dev", "signentropy_trans_asym_dev",
                 "signentropy_p_stay_dev", "signentropy_p_switch_dev"):
        assert real in R.SIGNALS


# ---------------------------------------------------------------- single-leg costs
def test_cost_rate_taker_and_maker_blend():
    assert np.isclose(R.cost_rate(0.0004, 0.0001, "taker"), 0.0005)
    assert np.isclose(R.cost_rate(0.0004, 0.0001, "maker_blend"), 0.0003)
    for fee in R.FEES:
        for slip in R.SLIPS:
            assert R.cost_rate(fee, slip, "taker") >= R.cost_rate(fee, slip, "maker_blend")


# ---------------------------------------------------------------- positions
def test_positions_dollar_neutral_and_causal():
    score = np.array([
        [0.9, 0.9, 0.1, 0.1, 0.9, 0.1],
        [0.8, 0.8, 0.2, 0.2, 0.8, 0.2],
        [-0.8, -0.8, -0.2, -0.2, -0.8, -0.2],
        [-0.9, -0.9, -0.1, -0.1, -0.9, -0.1],
    ])
    pos = R.xsec_positions(score, R.FRAC, 1)
    assert pos.shape == (4, 6)
    assert np.allclose(pos.sum(axis=0), 0.0)
    assert np.all(pos[:, 0] == 0.0)
    assert pos[0, 2] > 0 and pos[3, 2] < 0


def test_positions_hold_reduces_turnover():
    score = np.tile(np.array([[0.9], [0.8], [-0.8], [-0.9]]), (1, 12))
    pos1 = R.xsec_positions(score, R.FRAC, 1)
    pos12 = R.xsec_positions(score, R.FRAC, 12)
    turn1 = np.abs(np.diff(pos1, axis=1)).sum()
    turn12 = np.abs(np.diff(pos12, axis=1)).sum()
    assert turn12 <= turn1


def test_positions_nan_asset_gets_zero_weight():
    score = np.array([[0.9, 0.9], [np.nan, 0.1], [-0.8, -0.2], [-0.9, -0.9]])
    pos = R.xsec_positions(score, R.FRAC, 1)
    assert pos[1, 1] == 0.0


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


def test_wf_splits_count_2023_2025():
    idx = pd.date_range("2023-01-01", "2026-01-01", freq="5min", tz="UTC")
    splits = R.wf_splits_by_month(idx, 12, 3, 3)
    assert len(splits) == 8


# ---------------------------------------------------------------- SIGNENTROPY kernel (brute-force equality)
def test_signentropy_matches_brute_force():
    """The vectorized SIGNENTROPY kernel MUST equal the brute-force reference
    (per-window loop with explicit order-1 Markov transition matrix computation).
    Compared with maxdiff < 1e-12 and matching NaN patterns."""
    rng = np.random.default_rng(20261293)
    n_assets, n_bars = 5, 4000
    # Generate price paths, derive signs
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    log_ret = np.zeros_like(close)
    log_ret[:, 1:] = np.log(close[:, 1:] / close[:, :-1])
    sign = np.sign(log_ret).astype(int)
    sign[:, 0] = 0

    fast = R.compute_signentropy_metrics(sign, W=R.SIGNENTROPY_W)
    brute = R._signentropy_bruteforce(sign, W=R.SIGNENTROPY_W)
    for key in ("signentropy_trans_entropy", "signentropy_trans_asym",
                "signentropy_p_stay", "signentropy_p_switch"):
        fv, fb = fast[key], brute[key]
        fin = np.isfinite(fv) & np.isfinite(fb)
        assert fin.sum() > 0, f"{key}: no finite overlapping points"
        assert np.array_equal(np.isnan(fv), np.isnan(fb)), f"{key}: NaN pattern mismatch"
        maxdiff = float(np.max(np.abs(fv[fin] - fb[fin]))) if fin.sum() else 0.0
        assert maxdiff < 1e-12, f"{key}: maxdiff={maxdiff} >= 1e-12"


def test_signentropy_matches_brute_force_10_assets():
    """Brute-force equality with the full 10-asset panel (the real universe width)."""
    rng = np.random.default_rng(4294)
    n_assets, n_bars = 10, 1500
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    log_ret = np.zeros_like(close)
    log_ret[:, 1:] = np.log(close[:, 1:] / close[:, :-1])
    sign = np.sign(log_ret).astype(int)
    sign[:, 0] = 0

    fast = R.compute_signentropy_metrics(sign, W=R.SIGNENTROPY_W)
    brute = R._signentropy_bruteforce(sign, W=R.SIGNENTROPY_W)
    for key in ("signentropy_trans_entropy", "signentropy_trans_asym",
                "signentropy_p_stay", "signentropy_p_switch"):
        fv, fb = fast[key], brute[key]
        fin = np.isfinite(fv) & np.isfinite(fb)
        assert fin.sum() > 0, key
        assert np.array_equal(np.isnan(fv), np.isnan(fb)), key
        maxdiff = float(np.max(np.abs(fv[fin] - fb[fin])))
        assert maxdiff < 1e-12, f"signentropy_{key}: maxdiff={maxdiff} (float64 noise floor)"


def test_signetropy_matches_brute_force_with_nan():
    """Brute-force equality when the panel contains NaNs (global across assets)."""
    rng = np.random.default_rng(99)
    n_assets, n_bars = 4, 1200
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    log_ret = np.zeros_like(close)
    log_ret[:, 1:] = np.log(close[:, 1:] / close[:, :-1])
    sign = np.sign(log_ret).astype(int)
    sign[:, 0] = 0
    # Inject NaN in close -> propagates to NaN in sign
    close[1, 400] = np.nan
    close[2, 401] = np.nan
    log_ret = np.zeros_like(close)
    log_ret[:, 1:] = np.log(close[:, 1:] / close[:, :-1])
    log_ret = np.where(np.isfinite(log_ret), log_ret, np.nan)
    sign = np.sign(log_ret).astype(int)
    sign[:, 0] = 0

    fast = R.compute_signentropy_metrics(sign, W=R.SIGNENTROPY_W)
    brute = R._signentropy_bruteforce(sign, W=R.SIGNENTROPY_W)
    for key in ("signentropy_trans_entropy", "signentropy_trans_asym",
                "signentropy_p_stay", "signentropy_p_switch"):
        fv, fb = fast[key], brute[key]
        assert np.array_equal(np.isnan(fv), np.isnan(fb)), f"{key}: NaN mismatch"
        fin = np.isfinite(fv) & np.isfinite(fb)
        maxdiff = float(np.max(np.abs(fv[fin] - fb[fin]))) if fin.sum() else 0.0
        assert maxdiff < 1e-12, f"{key}: maxdiff={maxdiff} (float64 noise floor)"


def test_signetropy_defined_after_window_nan_before():
    rng = np.random.default_rng(3)
    n_assets, n_bars = 3, 600
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.005, axis=1))
    log_ret = np.zeros_like(close)
    log_ret[:, 1:] = np.log(close[:, 1:] / close[:, :-1])
    sign = np.sign(log_ret).astype(int)
    sign[:, 0] = 0
    W = R.SIGNENTROPY_W
    m = R.compute_signentropy_metrics(sign, W=W)
    for key in ("signentropy_trans_entropy", "signentropy_trans_asym",
                "signentropy_p_stay", "signentropy_p_switch"):
        assert np.isnan(m[key][:, :W]).all(), key
        assert np.isfinite(m[key][:, W:]).any(), key


def test_signetropy_non_finite_close_propagates():
    """A non-finite close in any asset at a bar -> NaN for all SIGNENTROPY outputs
    in every window covering that bar (global-across-assets finiteness gate)."""
    rng = np.random.default_rng(9)
    n_assets, n_bars = 4, 600
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.005, axis=1))
    close[:, 300] = np.nan
    log_ret = np.zeros_like(close)
    log_ret[:, 1:] = np.log(close[:, 1:] / close[:, :-1])
    sign = np.sign(log_ret).astype(int)
    sign[:, 0] = 0
    W = R.SIGNENTROPY_W
    m = R.compute_signentropy_metrics(sign, W=W)
    for t in range(300, min(300 + W + 1, n_bars)):
        for key in ("signentropy_trans_entropy", "signentropy_trans_asym",
                    "signentropy_p_stay", "signentropy_p_switch"):
            assert np.isnan(m[key][:, t]).all(), f"signentropy_{key} t={t} should be NaN"
    for t in range(W, 300):
        assert np.isfinite(m["signentropy_trans_entropy"][:, t]).any(), f"signentropy_trans_entropy t={t} should be finite"


def test_signetropy_params():
    assert R.SIGNENTROPY_W == 256


def test_signetropy_trans_entropy_range():
    """Transition entropy H_trans = -Σ p_ij log p_ij: in [0, log(4)] = [0, ~1.386]."""
    rng = np.random.default_rng(2026)
    n_assets, n_bars = 2, 1000
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    log_ret = np.zeros_like(close)
    log_ret[:, 1:] = np.log(close[:, 1:] / close[:, :-1])
    sign = np.sign(log_ret).astype(int)
    sign[:, 0] = 0
    W = R.SIGNENTROPY_W
    m = R.compute_signentropy_metrics(sign, W=W)
    fin = np.isfinite(m["signentropy_trans_entropy"])
    assert (m["signentropy_trans_entropy"][fin] >= -1e-9).all(), "trans_entropy must be >= 0"
    assert (m["signentropy_trans_entropy"][fin] <= np.log(4) + 1e-9).all(), "trans_entropy must be <= log(4)"


def test_signetropy_trans_asym_range():
    """Transition asymmetry asym = p_+- - p_-+: in [-1, 1]."""
    rng = np.random.default_rng(2027)
    n_assets, n_bars = 2, 1000
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    log_ret = np.zeros_like(close)
    log_ret[:, 1:] = np.log(close[:, 1:] / close[:, :-1])
    sign = np.sign(log_ret).astype(int)
    sign[:, 0] = 0
    W = R.SIGNENTROPY_W
    m = R.compute_signentropy_metrics(sign, W=W)
    fin = np.isfinite(m["signentropy_trans_asym"])
    assert (m["signentropy_trans_asym"][fin] >= -1.0 - 1e-9).all(), "trans_asym must be >= -1"
    assert (m["signentropy_trans_asym"][fin] <= 1.0 + 1e-9).all(), "trans_asym must be <= 1"


def test_signetropy_p_stay_range():
    """Persistence p_stay = (p_++ + p_--)/2: in [0, 1]."""
    rng = np.random.default_rng(2028)
    n_assets, n_bars = 2, 1000
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    log_ret = np.zeros_like(close)
    log_ret[:, 1:] = np.log(close[:, 1:] / close[:, :-1])
    sign = np.sign(log_ret).astype(int)
    sign[:, 0] = 0
    W = R.SIGNENTROPY_W
    m = R.compute_signentropy_metrics(sign, W=W)
    fin = np.isfinite(m["signentropy_p_stay"])
    assert (m["signentropy_p_stay"][fin] >= -1e-9).all(), "p_stay must be >= 0"
    assert (m["signentropy_p_stay"][fin] <= 1.0 + 1e-9).all(), "p_stay must be <= 1"


def test_signetropy_p_switch_range():
    """Switching p_switch = (p_+- + p_-+)/2 = 1 - p_stay: in [0, 1]."""
    rng = np.random.default_rng(2029)
    n_assets, n_bars = 2, 1000
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    log_ret = np.zeros_like(close)
    log_ret[:, 1:] = np.log(close[:, 1:] / close[:, :-1])
    sign = np.sign(log_ret).astype(int)
    sign[:, 0] = 0
    W = R.SIGNENTROPY_W
    m = R.compute_signentropy_metrics(sign, W=W)
    fin = np.isfinite(m["signentropy_p_switch"])
    assert (m["signentropy_p_switch"][fin] >= -1e-9).all(), "p_switch must be >= 0"
    assert (m["signentropy_p_switch"][fin] <= 1.0 + 1e-9).all(), "p_switch must be <= 1"


def test_signetropy_p_stay_plus_p_switch_equals_one():
    """p_stay + p_switch == 1 (where both finite)."""
    rng = np.random.default_rng(2030)
    n_assets, n_bars = 3, 800
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    log_ret = np.zeros_like(close)
    log_ret[:, 1:] = np.log(close[:, 1:] / close[:, :-1])
    sign = np.sign(log_ret).astype(int)
    sign[:, 0] = 0
    W = R.SIGNENTROPY_W
    m = R.compute_signentropy_metrics(sign, W=W)
    fin = np.isfinite(m["signentropy_p_stay"]) & np.isfinite(m["signentropy_p_switch"])
    assert fin.sum() > 0
    sum_vals = m["signentropy_p_stay"][fin] + m["signentropy_p_switch"][fin]
    assert np.allclose(sum_vals, 1.0, atol=1e-12), "p_stay + p_switch must equal 1"


def test_reference_config_matches_pre_registered_spec():
    assert R.ATTR_REPRESENTATIVES == {
        "signentropy_trans_entropy_dev": "signentropy_trans_entropy_dev",
        "signentropy_trans_asym_dev": "signentropy_trans_asym_dev",
        "signentropy_p_stay_dev": "signentropy_p_stay_dev",
        "signentropy_p_switch_dev": "signentropy_p_switch_dev",
    }
    assert R.PLACEBO_SEED == 20261293
    assert R.STABILITY_MIN_SIGN_CONSISTENCY == 0.70
    assert R.STABILITY_MIN_SHARPE_CORR == 0.50
    assert R.DOMINANT_SHARE_MIN == 0.50
    assert R.TRAIN_M == 12 and R.TEST_M == 3 and R.ROLL_M == 3
    assert R.SIGNENTROPY_W == 256
    assert R.SIGNALS[0] == "signentropy_trans_entropy_dev"


# ---------------------------------------------------------------- phase-randomized surrogate
def test_phase_randomized_surrogate_same_marginal_deterministic():
    rng = np.random.default_rng(0)
    x = rng.standard_normal(500) * 3.0 + 5.0
    s1 = R._phase_randomized_surrogate(x, R.PLACEBO_SEED)
    s2 = R._phase_randomized_surrogate(x, R.PLACEBO_SEED)
    assert np.array_equal(s1, s2)
    assert np.isclose(np.sort(s1[np.isfinite(s1)]), np.sort(x[np.isfinite(x)]), equal_nan=True).all()


# ---------------------------------------------------------------- build_underlying / build_scores
def _synthetic_bs(n_assets=3, n_days=8, seed=1):
    rng = np.random.default_rng(seed)
    T = 288
    lr = rng.standard_normal((n_assets, n_days * T)) * 0.001
    c = 100.0 * np.exp(np.cumsum(lr, axis=1))
    s = np.sign(lr).astype(int)
    s[:, 0] = 0
    return {
        "perp_close": c, "log_return": lr, "sign": s,
        "bucket": np.tile(np.arange(T), n_days),
        "n_assets": n_assets, "n_days": n_days, "n_bars": n_days * T,
    }


def test_build_underlying_shapes_and_keys():
    bs = _synthetic_bs()
    series = R.build_underlying(bs)
    assert set(series.keys()) == {"signentropy_trans_entropy", "signentropy_trans_asym",
                                  "signentropy_p_stay", "signentropy_p_switch"}
    for k in ("signentropy_trans_entropy", "signentropy_trans_asym",
              "signentropy_p_stay", "signentropy_p_switch"):
        assert series[k].shape == (bs["n_assets"], bs["n_bars"])


def test_build_scores_signals_lookbacks_causal():
    bs = _synthetic_bs()
    series = R.build_underlying(bs)
    scores = R.build_scores(series, bs["bucket"])
    for sig in R.SIGNALS:
        for L in R.LOOKBACKS:
            assert (sig, L) in scores
            assert scores[(sig, L)].shape == (bs["n_assets"], bs["n_bars"])
    for key, sc in scores.items():
        assert np.isnan(sc[:, 0]).all(), key


# ---------------------------------------------------------------- kernel distinctness guards
def test_signetropy_kernel_not_degenerate():
    """Rewrite guard: SIGNENTROPY metrics are not degenerate (not allclose to 0 where defined)."""
    rng = np.random.default_rng(55)
    n_assets, n_bars = 5, 1600
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    log_ret = np.zeros_like(close)
    log_ret[:, 1:] = np.log(close[:, 1:] / close[:, :-1])
    sign = np.sign(log_ret).astype(int)
    sign[:, 0] = 0
    W = R.SIGNENTROPY_W
    mm = R.compute_signentropy_metrics(sign, W=W)
    for name in ("signentropy_trans_entropy", "signentropy_trans_asym",
                 "signentropy_p_stay", "signentropy_p_switch"):
        arr = mm[name]
        fin = np.isfinite(arr)
        assert fin.sum() > 0, f"signentropy_{name}: no finite values"
        # at least some values should be non-zero
        assert not np.allclose(arr[fin], 0.0, atol=1e-12), f"signentropy_{name} collapses to 0"


# ---- inline prior-family reference statistics (distinctness guards)
def _c329_sign_entropy_style_stat(sign, W):
    """Inline C329-style statistic: Shannon entropy of sign COUNTS over window
    (directional disorder/balance) — count/level statistics, NOT transition probabilities."""
    n_assets, n = sign.shape
    out = np.full((n_assets, n), np.nan, dtype=float)
    for t in range(W, n):
        span = sign[:, t - W:t + 1]
        if not np.isfinite(span).all():
            continue
        for i in range(n_assets):
            s = span[i]
            pos = int(np.count_nonzero(s == 1))
            neg = int(np.count_nonzero(s == -1))
            total = pos + neg
            if total == 0:
                continue
            p_pos = pos / total if pos > 0 else 0.0
            p_neg = neg / total if neg > 0 else 0.0
            H = -(p_pos * np.log(p_pos) if p_pos > 0 else 0.0) - (p_neg * np.log(p_neg) if p_neg > 0 else 0.0)
            out[i, t] = float(H)
    return out


def _c329_maxrun_style_stat(sign, W):
    """Inline C329-style maxrun: maximum same-sign run length within window."""
    n_assets, n = sign.shape
    out = np.full((n_assets, n), np.nan, dtype=float)
    for t in range(W, n):
        span = sign[:, t - W:t + 1]
        if not np.isfinite(span).all():
            continue
        for i in range(n_assets):
            s = span[i]
            s2 = s[s != 0]
            if len(s2) < 2:
                continue
            change = s2[1:] != s2[:-1]
            starts = np.concatenate([[0], np.nonzero(change)[0] + 1])
            lens = np.diff(np.concatenate([starts, [len(s2)]]))
            out[i, t] = float(lens.max())
    return out


def _c328_signstreak_style_stat(sign, W):
    """Inline C328 signstreak-style: current run length ending at t."""
    n_assets, n = sign.shape
    out = np.full((n_assets, n), np.nan, dtype=float)
    for t in range(W, n):
        span = sign[:, t - W:t + 1]
        if not np.isfinite(span).all():
            continue
        for i in range(n_assets):
            s = span[i]
            if s[-1] == 0:
                out[i, t] = 0.0
                continue
            run = 1
            for k in range(len(s) - 2, -1, -1):
                if s[k] == s[-1] and s[k] != 0:
                    run += 1
                else:
                    break
            out[i, t] = float(run)
    return out


def _c422_zcrpath_style_stat(close, W):
    """Inline C422 ZCRPATH-style: zero-crossing rate of cumulative-return path."""
    X = np.diff(np.log(close), axis=1)
    n_assets, n = X.shape
    out = np.full((n_assets, n), np.nan, dtype=float)
    for t in range(W, n):
        span = X[:, t - W + 1:t + 1]
        if not np.isfinite(span).all():
            continue
        for i in range(n_assets):
            x = span[i]
            C = np.cumsum(x)
            chg = C[:-1] * C[1:] < 0
            out[i, t] = float(chg.sum() / (W - 1))
    return out


def _c423_runlen_style_stat(close, W):
    """Inline C423 RUNLEN-style: run-length distribution entropy of consecutive same-sign returns."""
    X = np.diff(np.log(close), axis=1)
    n_assets, n = X.shape
    out = np.full((n_assets, n), np.nan, dtype=float)
    for t in range(W, n):
        span = X[:, t - W + 1:t + 1]
        if not np.isfinite(span).all():
            continue
        for i in range(n_assets):
            x = span[i]
            s = np.sign(x)
            s2 = s[s != 0.0]
            if len(s2) < 2:
                continue
            change = s2[1:] != s2[:-1]
            starts = np.concatenate([[0], np.nonzero(change)[0] + 1])
            lens = np.diff(np.concatenate([starts, [len(s2)]])).astype(float)
            total = float(lens.sum())
            p = lens / total
            out[i, t] = float(-(p * np.log(p)).sum())
    return out


def _c424_iesd_style_stat(close, W):
    """Inline C424 IESD-style: mean spacing of local-extremum gaps."""
    n_assets, n = close.shape
    out_mean = np.full((n_assets, n), np.nan, dtype=float)
    for t in range(W, n):
        span = close[:, t - W:t + 1]
        if not np.isfinite(span).all():
            continue
        for i in range(n_assets):
            C = span[i]
            is_max = (C[1:-1] > C[:-2]) & (C[1:-1] > C[2:])
            is_min = (C[1:-1] < C[:-2]) & (C[1:-1] < C[2:])
            ext_rel = np.flatnonzero(is_max | is_min)
            if len(ext_rel) < 2:
                continue
            ext_pos = ext_rel + 1
            spacings = np.diff(ext_pos).astype(float)
            out_mean[i, t] = float(spacings.mean())
    return out_mean


def _c426_wlmf_style_stat(close, W):
    """Inline C426 WLMF-style: db3 wavelet finest-detail energy over the window."""
    s10 = math.sqrt(10.0)
    s52 = math.sqrt(5.0 + 2.0 * s10)
    sqrt2 = math.sqrt(2.0)
    h = np.array([
        (1.0 + s10 + s52) / (16.0 * sqrt2),
        (5.0 + s10 + 3.0 * s52) / (16.0 * sqrt2),
        (10.0 - 2.0 * s10 + 2.0 * s52) / (16.0 * sqrt2),
        (10.0 - 2.0 * s10 - 2.0 * s52) / (16.0 * sqrt2),
        (5.0 + s10 - 3.0 * s52) / (16.0 * sqrt2),
        (1.0 + s10 - s52) / (16.0 * sqrt2),
    ])
    g = ((-1.0) ** np.arange(len(h))) * h[::-1]
    X = np.diff(np.log(close), axis=1)
    n_assets, n = X.shape
    out = np.full((n_assets, n), np.nan, dtype=float)
    Lh = len(h)
    for t in range(W, n):
        span = X[:, t - W + 1:t + 1]
        if not np.isfinite(span).all():
            continue
        for i in range(n_assets):
            a = span[i]
            nn = len(a)
            half = nn // 2
            k = np.arange(half)
            idx = (2 * k[:, None] - np.arange(Lh)[None, :]) % nn
            d = a[idx] @ g
            out[i, t] = float(np.std(d)) if half > 0 else np.nan
    return out


def _c358_mfdfa_style_stat(close, W):
    """Inline C358 MF-DFA style: fluctuation function F(s) over scales."""
    X = np.diff(np.log(close), axis=1)
    n_assets, n = X.shape
    out = np.full((n_assets, n), np.nan, dtype=float)
    scales = np.array([8, 16, 32, 64, 128], dtype=int)
    for t in range(W, n):
        span = X[:, t - W + 1:t + 1]
        if not np.isfinite(span).all():
            continue
        for i in range(n_assets):
            prof = np.cumsum(span[i] - np.mean(span[i]))
            Fs = []
            for s in scales:
                if s > len(prof):
                    continue
                segs = prof[:len(prof) // s * s].reshape(-1, s)
                Fs.append(float(np.sqrt(np.mean((segs - segs.mean(axis=1, keepdims=True)) ** 2))))
            if len(Fs) >= 3:
                out[i, t] = float(np.polyfit(np.log2(scales[:len(Fs)]), np.log2(Fs), 1)[0])
    return out


def _c349_permutation_entropy_style_stat(close, W):
    """Inline C349 permutation entropy style."""
    X = np.diff(np.log(close), axis=1)
    n_assets, n = X.shape
    out = np.full((n_assets, n), np.nan, dtype=float)
    for t in range(W, n):
        span = X[:, t - W + 1:t + 1]
        if not np.isfinite(span).all():
            continue
        for i in range(n_assets):
            x = span[i]
            if len(x) < 3:
                continue
            # simple order-3 permutation entropy
            patterns = []
            for k in range(len(x) - 2):
                trip = x[k:k+3]
                order = tuple(np.argsort(trip, kind="mergesort"))
                patterns.append(order)
            if not patterns:
                continue
            _, counts = np.unique(patterns, return_counts=True)
            p = counts / len(patterns)
            out[i, t] = float(-(p * np.log(p)).sum())
    return out


def _c355_sample_entropy_style_stat(close, W):
    """Inline C355 sample entropy style."""
    X = np.diff(np.log(close), axis=1)
    n_assets, n = X.shape
    out = np.full((n_assets, n), np.nan, dtype=float)
    for t in range(W, n):
        span = X[:, t - W + 1:t + 1]
        if not np.isfinite(span).all():
            continue
        for i in range(n_assets):
            x = span[i]
            m = 2
            r = 0.2 * np.std(x) if np.std(x) > 0 else 0.0
            if r == 0:
                continue
            N = len(x)
            if N <= m + 1:
                continue
            # sample entropy
            def _count(m_val):
                K = N - m_val + 1
                T = np.stack([x[i:i + m_val] for i in range(K)])
                total = 0
                chunk = 64
                for i0 in range(0, K, chunk):
                    block = T[i0:i0 + chunk]
                    d = np.max(np.abs(block[:, None, :] - T[None, :, :]), axis=2)
                    total += int(np.count_nonzero(d < r))
                return max(total - K, 0) // 2
            A = _count(m + 1)
            B = _count(m)
            if B > 0 and A > 0:
                out[i, t] = float(-np.log(A / B))
    return out


def _assert_distinct(sa, ref, name):
    sa = np.asarray(sa, dtype=float)
    ref = np.asarray(ref, dtype=float)
    m = min(len(sa), len(ref))
    sa, ref = sa[:m], ref[:m]
    fin = np.isfinite(sa) & np.isfinite(ref)
    assert fin.sum() > 0, name
    assert not np.allclose(sa[fin], ref[fin], atol=1e-6), f"SIGNENTROPY degenerates to {name}"


def test_signetropy_kernel_distinct_from_c329_sign_entropy():
    """C329 sign entropy (Shannon entropy of sign COUNTS): legitimate
    distinctness-guard ref (count/level statistics vs order-1 Markov transition dynamics)."""
    rng = np.random.default_rng(214)
    n_assets, n_bars = 5, 1200
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    log_ret = np.zeros_like(close)
    log_ret[:, 1:] = np.log(close[:, 1:] / close[:, :-1])
    sign = np.sign(log_ret).astype(int)
    sign[:, 0] = 0
    W = R.SIGNENTROPY_W
    mm = R.compute_signentropy_metrics(sign, W=W)
    sa = mm["signentropy_trans_entropy"][0, W:]
    ref = _c329_sign_entropy_style_stat(sign, W)[0, W:]
    _assert_distinct(sa, ref, "C329_SIGN_ENTROPY")


def test_signetropy_kernel_distinct_from_c329_maxrun():
    """C329 maxrun (max same-sign run length): legitimate distinctness-guard ref."""
    rng = np.random.default_rng(217)
    n_assets, n_bars = 5, 1200
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    log_ret = np.zeros_like(close)
    log_ret[:, 1:] = np.log(close[:, 1:] / close[:, :-1])
    sign = np.sign(log_ret).astype(int)
    sign[:, 0] = 0
    W = R.SIGNENTROPY_W
    mm = R.compute_signentropy_metrics(sign, W=W)
    sa = mm["signentropy_trans_entropy"][0, W:]
    ref = _c329_maxrun_style_stat(sign, W)[0, W:]
    _assert_distinct(sa, ref, "C329_MAXRUN")


def test_signetropy_kernel_distinct_from_c328_signstreak():
    """C328 signstreak (current run length ending at t): legitimate distinctness-guard ref."""
    rng = np.random.default_rng(219)
    n_assets, n_bars = 5, 1200
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    log_ret = np.zeros_like(close)
    log_ret[:, 1:] = np.log(close[:, 1:] / close[:, :-1])
    sign = np.sign(log_ret).astype(int)
    sign[:, 0] = 0
    W = R.SIGNENTROPY_W
    mm = R.compute_signentropy_metrics(sign, W=W)
    sa = mm["signentropy_trans_entropy"][0, W:]
    ref = _c328_signstreak_style_stat(sign, W)[0, W:]
    _assert_distinct(sa, ref, "C328_SIGNSTREAK")


def test_signetropy_kernel_distinct_from_zcrpath():
    """C422 ZCRPATH (zero-crossing rate of cumulative-return path): legitimate distinctness-guard ref."""
    rng = np.random.default_rng(219)
    n_assets, n_bars = 5, 1200
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    W = R.SIGNENTROPY_W
    sign = np.sign(np.diff(np.log(close), axis=1)).astype(int)
    sign = np.concatenate([np.zeros((n_assets, 1), dtype=int), sign], axis=1)
    mm = R.compute_signentropy_metrics(sign, W=W)
    sa = mm["signentropy_trans_entropy"][0, W:]
    ref = _c422_zcrpath_style_stat(close, W)[0, W:]
    _assert_distinct(sa, ref, "ZCRPATH")


def test_signetropy_kernel_distinct_from_runlen():
    """C423 RUNLEN (run-length distribution entropy of consecutive return signs): legitimate distinctness-guard ref."""
    rng = np.random.default_rng(220)
    n_assets, n_bars = 5, 1200
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    W = R.SIGNENTROPY_W
    sign = np.sign(np.diff(np.log(close), axis=1)).astype(int)
    sign = np.concatenate([np.zeros((n_assets, 1), dtype=int), sign], axis=1)
    mm = R.compute_signentropy_metrics(sign, W=W)
    sa = mm["signentropy_trans_entropy"][0, W:]
    ref = _c423_runlen_style_stat(close, W)[0, W:]
    _assert_distinct(sa, ref, "RUNLEN")


def test_signetropy_kernel_distinct_from_iesd():
    """C424 IESD (inter-extremum spacing distribution): legitimate distinctness-guard ref."""
    rng = np.random.default_rng(224)
    n_assets, n_bars = 5, 1200
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    W = R.SIGNENTROPY_W
    sign = np.sign(np.diff(np.log(close), axis=1)).astype(int)
    sign = np.concatenate([np.zeros((n_assets, 1), dtype=int), sign], axis=1)
    mm = R.compute_signentropy_metrics(sign, W=W)
    sa = mm["signentropy_trans_entropy"][0, W:]
    ref = _c424_iesd_style_stat(close, W)[0, W:]
    _assert_distinct(sa, ref, "IESD")


def test_signetropy_kernel_distinct_from_wlmf():
    """C426 WLMF (wavelet-leader multifractal spectrum): legitimate distinctness-guard ref."""
    rng = np.random.default_rng(236)
    n_assets, n_bars = 5, 1200
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    W = R.SIGNENTROPY_W
    sign = np.sign(np.diff(np.log(close), axis=1)).astype(int)
    sign = np.concatenate([np.zeros((n_assets, 1), dtype=int), sign], axis=1)
    mm = R.compute_signentropy_metrics(sign, W=W)
    sa = mm["signentropy_trans_entropy"][0, W:]
    ref = _c426_wlmf_style_stat(close, W)[0, W:]
    _assert_distinct(sa, ref, "WLMF")


def test_signetropy_kernel_distinct_from_mfdfa():
    """C358 MF-DFA (fluctuation-function generalized Hurst): legitimate distinctness-guard ref."""
    rng = np.random.default_rng(230)
    n_assets, n_bars = 5, 1200
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    W = R.SIGNENTROPY_W
    sign = np.sign(np.diff(np.log(close), axis=1)).astype(int)
    sign = np.concatenate([np.zeros((n_assets, 1), dtype=int), sign], axis=1)
    mm = R.compute_signentropy_metrics(sign, W=W)
    sa = mm["signentropy_trans_entropy"][0, W:]
    ref = _c358_mfdfa_style_stat(close, W)[0, W:]
    _assert_distinct(sa, ref, "MF-DFA")


def test_signetropy_kernel_distinct_from_permutation_entropy():
    """C349 permutation entropy: legitimate distinctness-guard ref."""
    rng = np.random.default_rng(240)
    n_assets, n_bars = 5, 1200
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    W = R.SIGNENTROPY_W
    sign = np.sign(np.diff(np.log(close), axis=1)).astype(int)
    sign = np.concatenate([np.zeros((n_assets, 1), dtype=int), sign], axis=1)
    mm = R.compute_signentropy_metrics(sign, W=W)
    sa = mm["signentropy_trans_entropy"][0, W:]
    ref = _c349_permutation_entropy_style_stat(close, W)[0, W:]
    _assert_distinct(sa, ref, "PERMUTATION_ENTROPY")


def test_signetropy_kernel_distinct_from_sample_entropy():
    """C355 sample entropy: legitimate distinctness-guard ref."""
    rng = np.random.default_rng(242)
    n_assets, n_bars = 5, 1200
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    W = R.SIGNENTROPY_W
    sign = np.sign(np.diff(np.log(close), axis=1)).astype(int)
    sign = np.concatenate([np.zeros((n_assets, 1), dtype=int), sign], axis=1)
    mm = R.compute_signentropy_metrics(sign, W=W)
    sa = mm["signentropy_trans_entropy"][0, W:]
    ref = _c355_sample_entropy_style_stat(close, W)[0, W:]
    _assert_distinct(sa, ref, "SAMPLE_ENTROPY")


def test_signetropy_kernel_distinct_from_ptlt():
    """C428 PTLT (path-local-time peak/trough occupation + extreme recency): legitimate distinctness-guard ref."""
    rng = np.random.default_rng(244)
    n_assets, n_bars = 5, 1200
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    W = R.SIGNENTROPY_W
    sign = np.sign(np.diff(np.log(close), axis=1)).astype(int)
    sign = np.concatenate([np.zeros((n_assets, 1), dtype=int), sign], axis=1)
    mm = R.compute_signentropy_metrics(sign, W=W)
    sa = mm["signentropy_trans_entropy"][0, W:]
    # PTLT uses price path bins, so we compute a simplified PTLT-like stat on close
    n_assets, n = close.shape
    out = np.full((n_assets, n), np.nan, dtype=float)
    B = 32
    for t in range(W, n):
        span = close[:, t - W:t + 1]
        if not np.isfinite(span).all():
            continue
        for i in range(n_assets):
            C = span[i]
            cmin = float(C.min()); cmax = float(C.max())
            if cmin == cmax:
                continue
            edges = np.linspace(cmin, cmax, B + 1)
            bins = np.searchsorted(edges, C, side="right") - 1
            bins = np.clip(bins, 0, B - 1)
            max_bin = int(bins[np.argmax(C)])
            min_bin = int(bins[np.argmin(C)])
            L_peak = float(np.count_nonzero(bins == max_bin))
            L_trough = float(np.count_nonzero(bins == min_bin))
            total = float(len(C))
            out[i, t] = L_peak / total if total > 0 else np.nan
    ref = out[0, W:]
    _assert_distinct(sa, ref, "PTLT")


# ---------------------------------------------------------------- guard tests (rewrite guards)
def test_artifact_campaign_is_429():
    """Rewrite guard: every emitted artifact self-identifies campaign 429."""
    for part in ("verdict", "summary", "registry", "oos_sweep"):
        files = sorted((ROOT / "reports").glob(f"campaign429_{part}_*.json"))
        files = [f for f in files if ".full." not in f.name]
        if not files:
            continue
        obj = json.loads(files[-1].read_text())
        assert obj["campaign"] == 429, f"{part} artifact campaign != 429: {obj.get('campaign')}"


def test_mandate_contains_signentropy():
    """Rewrite guard: the C429 mandate names the SIGNENTROPY order-1 Markov family."""
    p = sorted((ROOT / "reports").glob("campaign429_oos_sweep_*.json"))
    p = [f for f in p if ".full." not in f.name]
    if not p:
        return
    mandate = json.loads(p[-1].read_text())["mandate"]
    assert ("SIGNENTROPY" in mandate), "mandate missing SIGNENTROPY"
    assert "signentropy_trans_entropy" in mandate, "mandate missing signentropy_trans_entropy"
    assert "signentropy_trans_asym" in mandate, "mandate missing signentropy_trans_asym"
    assert "signentropy_p_stay" in mandate, "mandate missing signentropy_p_stay"
    assert "signentropy_p_switch" in mandate, "mandate missing signentropy_p_switch"
    assert "order-1 Markov" in mandate, "mandate missing order-1 Markov"


def test_placebo_seed_is_20261293():
    assert R.PLACEBO_SEED == 20261293


def test_placebo_seed_unique_not_reserved():
    """Rewrite guard: C429 placebo seed must not collide with reserved seeds
    used by prior campaigns (20261224..20261291)."""
    assert not (20261224 <= R.PLACEBO_SEED <= 20261291), \
        "placebo seed must be outside 20261224-20261291"


# ---------------------------------------------------------------- real artifacts schema (if present)
def _find_latest(prefix: str):
    files = sorted((ROOT / "reports").glob(f"campaign429_{prefix}_*.json"))
    files = [f for f in files if ".full." not in f.name]
    return files[-1] if files else None


def test_artifacts_if_present_have_required_flags():
    p = _find_latest("verdict")
    if p is None:
        return
    v = json.loads(p.read_text())
    assert v["campaign"] == 429
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
    assert sw["config"]["n_trials"] == R.N_TRIALS
    assert sw["real_data_only"] is True and sw["fabricated_data"] is False
    assert sw["config"]["placebo_seed"] == R.PLACEBO_SEED
    assert sw["config"]["signentropy_params"]["window_W"] == 256


if __name__ == "__main__":
    test_holm_and_bh_reject_correctly()
    test_holm_and_bh_monotone_and_bounded()
    test_n_trials_matches_pre_registered_grid_product()
    test_cost_rate_taker_and_maker_blend()
    test_positions_dollar_neutral_and_causal()
    test_positions_hold_reduces_turnover()
    test_positions_nan_asset_gets_zero_weight()
    test_wf_splits_month_aligned_non_overlapping()
    test_wf_splits_count_2023_2025()
    test_signetropy_matches_brute_force()
    test_signetropy_matches_brute_force_10_assets()
    test_signetropy_matches_brute_force_with_nan()
    test_signetropy_defined_after_window_nan_before()
    test_signetropy_non_finite_close_propagates()
    test_signetropy_params()
    test_signetropy_trans_entropy_range()
    test_signetropy_trans_asym_range()
    test_signetropy_p_stay_range()
    test_signetropy_p_switch_range()
    test_signetropy_p_stay_plus_p_switch_equals_one()
    test_reference_config_matches_pre_registered_spec()
    test_phase_randomized_surrogate_same_marginal_deterministic()
    test_build_underlying_shapes_and_keys()
    test_build_scores_signals_lookbacks_causal()
    test_signetropy_kernel_not_degenerate()
    test_signetropy_kernel_distinct_from_c329_sign_entropy()
    test_signetropy_kernel_distinct_from_c329_maxrun()
    test_signetropy_kernel_distinct_from_c328_signstreak()
    test_signetropy_kernel_distinct_from_zcrpath()
    test_signetropy_kernel_distinct_from_runlen()
    test_signetropy_kernel_distinct_from_iesd()
    test_signetropy_kernel_distinct_from_wlmf()
    test_signetropy_kernel_distinct_from_mfdfa()
    test_signetropy_kernel_distinct_from_permutation_entropy()
    test_signetropy_kernel_distinct_from_sample_entropy()
    test_signetropy_kernel_distinct_from_ptlt()
    test_artifact_campaign_is_429()
    test_mandate_contains_signetropy()
    test_placebo_seed_is_20261293()
    test_placebo_seed_unique_not_reserved()
    test_artifacts_if_present_have_required_flags()
    print("All C429 SIGNENTROPY runner tests passed")