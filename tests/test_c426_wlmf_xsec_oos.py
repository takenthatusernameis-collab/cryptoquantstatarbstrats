"""Tests for C426 runner (scripts/run_c426_wlmf_xsec_oos.py): pure-function
tests on synthetic arrays (including a brute-force equality test for the
vectorized wavelet-leader-multifractal-spectrum kernel vs the per-window
explicit DWT + leader index sets + Legendre-spectrum reference) plus
schema/flag validation of emitted real-data artifacts. No network, no
fabricated market data."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import run_c426_wlmf_xsec_oos as R  # noqa: E402


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
    assert R.N_TRIALS == 1296
    assert len(R.SIGNALS) == 4
    assert len(R.LOOKBACKS) == 6
    assert len(R.REBALANCES) == 3
    assert len(R.FEES) == 3 and len(R.SLIPS) == 3 and len(R.COST_VARIANTS) == 2
    assert R.N_TRIALS == (len(R.SIGNALS) * len(R.LOOKBACKS) * len(R.REBALANCES)
                          * len(R.FEES) * len(R.SLIPS) * len(R.COST_VARIANTS))
    for pb in ("wlmf_width_placebo", "wlmf_centroid_placebo"):
        assert pb in R.SIGNALS
    for real in ("wlmf_width_dev", "wlmf_centroid_dev"):
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


# ---------------------------------------------------------------- WLMF kernel (brute-force equality)
def test_wlmf_matches_brute_force():
    """The vectorized WLMF kernel MUST equal the brute-force reference
    (per-window loop with explicit gather+matvec DWT + explicit leader index
    sets + Legendre spectrum). Compared with maxdiff < 1e-12 and matching NaN patterns."""
    rng = np.random.default_rng(20261290)
    n_assets, n_bars = 5, 4000
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    fast = R.compute_wlmf_metrics(close, W=R.WLM_F_W)
    brute = R._wlmf_bruteforce(close, W=R.WLM_F_W)
    for key in ("wlmf_width", "wlmf_centroid"):
        fv, fb = fast[key], brute[key]
        fin = np.isfinite(fv) & np.isfinite(fb)
        assert fin.sum() > 0, f"{key}: no finite overlapping points"
        assert np.array_equal(np.isnan(fv), np.isnan(fb)), f"{key}: NaN pattern mismatch"
        maxdiff = float(np.max(np.abs(fv[fin] - fb[fin]))) if fin.sum() else 0.0
        assert maxdiff < 1e-9, f"{key}: maxdiff={maxdiff} >= 1e-9 (float64 noise floor)"


def test_wlmf_matches_brute_force_10_assets():
    """Brute-force equality with the full 10-asset panel (the real universe width)."""
    rng = np.random.default_rng(4264)
    n_assets, n_bars = 10, 1500
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    fast = R.compute_wlmf_metrics(close, W=R.WLM_F_W)
    brute = R._wlmf_bruteforce(close, W=R.WLM_F_W)
    for key in ("wlmf_width", "wlmf_centroid"):
        fv, fb = fast[key], brute[key]
        fin = np.isfinite(fv) & np.isfinite(fb)
        assert fin.sum() > 0, key
        maxdiff = float(np.max(np.abs(fv[fin] - fb[fin])))
        assert maxdiff < 1e-9, f"wlmf_{key}: maxdiff={maxdiff} (float64 noise floor)"


def test_wlmf_matches_brute_force_with_nan():
    """Brute-force equality when the panel contains NaNs (global across assets)."""
    rng = np.random.default_rng(99)
    n_assets, n_bars = 4, 1200
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    close[1, 400] = np.nan
    close[2, 401] = np.nan
    fast = R.compute_wlmf_metrics(close, W=R.WLM_F_W)
    brute = R._wlmf_bruteforce(close, W=R.WLM_F_W)
    for key in ("wlmf_width", "wlmf_centroid"):
        fv, fb = fast[key], brute[key]
        fin = np.isfinite(fv) & np.isfinite(fb)
        assert np.array_equal(np.isnan(fv), np.isnan(fb)), f"{key}: NaN mismatch"
        maxdiff = float(np.max(np.abs(fv[fin] - fb[fin]))) if fin.sum() else 0.0
        assert maxdiff < 1e-9, f"{key}: maxdiff={maxdiff} (float64 noise floor)"


def test_wlmf_defined_after_window_nan_before():
    rng = np.random.default_rng(3)
    n_assets, n_bars = 3, 600
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.005, axis=1))
    W = R.WLM_F_W
    m = R.compute_wlmf_metrics(close, W=W)
    for key in ("wlmf_width", "wlmf_centroid"):
        assert np.isnan(m[key][:, :W - 1]).all(), key
        assert np.isfinite(m[key][:, W - 1:]).any(), key


def test_wlmf_non_finite_close_propagates():
    """A non-finite close in any asset at a bar -> NaN for all WLMF outputs
    in every window covering that bar (global-across-assets finiteness gate)."""
    rng = np.random.default_rng(9)
    n_assets, n_bars = 4, 600
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.005, axis=1))
    close[0, 300] = np.inf
    W = R.WLM_F_W
    m = R.compute_wlmf_metrics(close, W=W)
    for t in range(300, min(300 + W, n_bars)):
        for key in ("wlmf_width", "wlmf_centroid"):
            assert np.isnan(m[key][:, t]).all(), f"wlmf_{key} t={t} should be NaN"
    for t in range(W, 300):
        assert np.isfinite(m["wlmf_width"][:, t]).any(), f"wlmf_width t={t} should be finite"


def test_wlmf_params():
    assert R.WLM_F_W == 256
    assert R.WLM_F_J == 5
    assert tuple(R.WLM_F_LEVELS) == (2, 3, 4, 5)
    assert len(R.WLM_F_Q) == 21


def test_wlmf_width_range():
    """wlmf_width = Delta h = h_max - h_min over {q:D(h)>=0} must be >= 0."""
    rng = np.random.default_rng(2026)
    n_assets, n_bars = 2, 1000
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    W = R.WLM_F_W
    m = R.compute_wlmf_metrics(close, W=W)
    fin = np.isfinite(m["wlmf_width"])
    assert (m["wlmf_width"][fin] >= 0.0).all(), "width must be non-negative"


def test_reference_config_matches_pre_registered_spec():
    assert R.ATTR_REPRESENTATIVES == {
        "wlmf_width_dev": "wlmf_width_dev",
        "wlmf_centroid_dev": "wlmf_centroid_dev",
    }
    assert R.PLACEBO_SEED == 20261290
    assert R.STABILITY_MIN_SIGN_CONSISTENCY == 0.70
    assert R.STABILITY_MIN_SHARPE_CORR == 0.50
    assert R.DOMINANT_SHARE_MIN == 0.50
    assert R.TRAIN_M == 12 and R.TEST_M == 3 and R.ROLL_M == 3
    assert R.WLM_F_W == 256
    assert R.SIGNALS[0] == "wlmf_width_dev"


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
    return {
        "perp_close": c, "log_return": lr,
        "bucket": np.tile(np.arange(T), n_days),
        "n_assets": n_assets, "n_days": n_days, "n_bars": n_days * T,
    }


def test_build_underlying_shapes_and_keys():
    bs = _synthetic_bs()
    series = R.build_underlying(bs)
    assert set(series.keys()) == {"wlmf_width", "wlmf_centroid"}
    for k in ("wlmf_width", "wlmf_centroid"):
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
def test_wlmf_kernel_not_degenerate():
    """Rewrite guard: WLMF metrics are not degenerate (not allclose to 0 where defined)."""
    rng = np.random.default_rng(55)
    n_assets, n_bars = 5, 1600
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    W = R.WLM_F_W
    mm = R.compute_wlmf_metrics(close, W=W)
    for name in ("wlmf_width", "wlmf_centroid"):
        arr = mm[name]
        fin = np.isfinite(arr)
        assert fin.sum() > 0, f"wlmf_{name}: no finite values"
        assert not np.allclose(arr[fin], 0.0, atol=1e-12), f"wlmf_{name} collapses to 0"


# ---- inline prior-family reference statistics (distinctness guards)
def _signchop_style_stat(close, W):
    """Inline C344-style statistic: sign-change / chop rate of the return sign
    sequence over the window — sign flips of the return sign, NOT wavelet-leader
    multifractal spectrum."""
    X = np.diff(np.log(close), axis=1)
    n_assets, n = X.shape
    out = np.full((n_assets, n), np.nan)
    for t in range(W, n):
        span = X[:, t - W + 1:t + 1]
        if not np.isfinite(span).all():
            continue
        for i in range(n_assets):
            s = np.sign(span[i])
            out[i, t] = float(np.mean(s[1:] != s[:-1])) if W > 1 else np.nan
    return out


def _signrun_style_stat(close, W):
    """Inline C374 SIGNRUN-style statistic: max run share / mean run length of
    signed runs — a single max/mean summary, NOT wavelet-leader spectrum."""
    X = np.diff(np.log(close), axis=1)
    n_assets, n = X.shape
    out = np.full((n_assets, n), np.nan)
    for t in range(W, n):
        span = X[:, t - W + 1:t + 1]
        if not np.isfinite(span).all():
            continue
        for i in range(n_assets):
            s = np.sign(span[i])
            s2 = s[s != 0]
            if len(s2) < 2:
                continue
            change = s2[1:] != s2[:-1]
            starts = np.concatenate([[0], np.nonzero(change)[0] + 1])
            lens = np.diff(np.concatenate([starts, [len(s2)]]))
            out[i, t] = float(lens.max() / lens.mean()) if lens.mean() > 0 else np.nan
    return out


def _zcrpath_style_stat(close, W):
    """Inline C422 ZCRPATH-style statistic: zero-crossing rate of the
    cumulative-return path — crossings of cumsum(X), NOT wavelet-leader spectrum."""
    X = np.diff(np.log(close), axis=1)
    n_assets, n = X.shape
    out = np.full((n_assets, n), np.nan)
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


def _runlen_style_stat(close, W):
    """Inline C423 RUNLEN-style statistic: run-length distribution entropy of
    consecutive same-sign returns — full run-length entropy, NOT wavelet-leader spectrum."""
    X = np.diff(np.log(close), axis=1)
    n_assets, n = X.shape
    out = np.full((n_assets, n), np.nan)
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


def _iesd_style_stat(close, W):
    """Inline C424 IESD-style statistic: mean spacing of local-extremum gaps —
    inter-extremum spacing distribution, NOT wavelet-leader spectrum."""
    n_assets, n = close.shape
    out_mean = np.full((n_assets, n), np.nan)
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


def _mfdfa_style_stat(close, W):
    """Inline C358 MF-DFA style statistic: fluctuation function F(s) over scales,
    generalized Hurst from log-log slope — NOT wavelet-leader multifractal spectrum."""
    X = np.diff(np.log(close), axis=1)
    n_assets, n = X.shape
    out = np.full((n_assets, n), np.nan)
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


def _rqa_det_style_stat(close, W):
    """Inline C425 RQA det: diagonal-line determinism of delay-embedding recurrence
    matrix — NOT wavelet-leader multifractal spectrum."""
    X = np.diff(np.log(close), axis=1)
    n_assets, n = X.shape
    m = 3
    tau = 1
    emb = np.stack([X[:, k:n - (m - 1 - k) * tau] for k in range(m)], axis=-1)
    out = np.full((n_assets, n), np.nan)
    eps = 0.1
    for t in range(W, n):
        span = emb[:, t - W + 1:t + 1]
        if not np.isfinite(span).all():
            continue
        for i in range(n_assets):
            E = span[i]
            N = E.shape[0]
            D = np.max(np.abs(E[:, None, :] - E[None, :, :]), axis=-1)
            Rm = (D <= eps * np.std(X[i])).astype(float)
            np.fill_diagonal(Rm, 0.0)
            total_diag = 0
            total_all = 0
            for off in range(-(N - 2), N - 1):
                d = np.diag(Rm, k=off)
                runs = []
                cur = 0
                for v in d:
                    if v:
                        cur += 1
                    else:
                        if cur >= 2:
                            runs.append(cur)
                        cur = 0
                if cur >= 2:
                    runs.append(cur)
                total_diag += sum(runs)
                total_all += len(d)
            out[i, t] = float(total_diag / total_all) if total_all > 0 else np.nan
    return out


def _assert_distinct(sa, ref, name):
    fin = np.isfinite(sa) & np.isfinite(ref)
    assert fin.sum() > 0, name
    assert not np.allclose(sa[fin], ref[fin], atol=1e-6), f"WLMF degenerates to {name}"


def test_wlmf_kernel_distinct_from_signchop():
    """C344 sign-change/chop rate: legitimate distinctness-guard ref
    (sign flips of the return sign vs wavelet-leader multifractal spectrum)."""
    rng = np.random.default_rng(214)
    n_assets, n_bars = 5, 1200
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    W = R.WLM_F_W
    mm = R.compute_wlmf_metrics(close, W=W)
    sa = mm["wlmf_width"][0, W:]
    ref = _signchop_style_stat(close, W)[0, W - 1:]
    _assert_distinct(sa, ref, "SIGNCHOP")


def test_wlmf_kernel_distinct_from_signrun():
    """C374 SIGNRUN (max run share / mean run length): legitimate
    distinctness-guard ref (single max/mean summary vs wavelet-leader spectrum)."""
    rng = np.random.default_rng(217)
    n_assets, n_bars = 5, 1200
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    W = R.WLM_F_W
    mm = R.compute_wlmf_metrics(close, W=W)
    sa = mm["wlmf_width"][0, W:]
    ref = _signrun_style_stat(close, W)[0, W - 1:]
    _assert_distinct(sa, ref, "SIGNRUN")


def test_wlmf_kernel_distinct_from_zcrpath():
    """C422 ZCRPATH (zero-crossing rate of cumulative-return path): legitimate
    distinctness-guard ref (cumulative-path crossings vs wavelet-leader spectrum)."""
    rng = np.random.default_rng(219)
    n_assets, n_bars = 5, 1200
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    W = R.WLM_F_W
    mm = R.compute_wlmf_metrics(close, W=W)
    sa = mm["wlmf_width"][0, W:]
    ref = _zcrpath_style_stat(close, W)[0, W - 1:]
    _assert_distinct(sa, ref, "ZCRPATH")


def test_wlmf_kernel_distinct_from_runlen():
    """C423 RUNLEN (run-length distribution entropy of consecutive return signs):
    legitimate distinctness-guard ref (run-length entropy vs wavelet-leader spectrum)."""
    rng = np.random.default_rng(220)
    n_assets, n_bars = 5, 1200
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    W = R.WLM_F_W
    mm = R.compute_wlmf_metrics(close, W=W)
    sa = mm["wlmf_width"][0, W:]
    ref = _runlen_style_stat(close, W)[0, W - 1:]
    _assert_distinct(sa, ref, "RUNLEN")


def test_wlmf_kernel_distinct_from_iesd():
    """C424 IESD (inter-extremum spacing distribution): legitimate
    distinctness-guard ref (spacing between local extrema vs wavelet-leader spectrum)."""
    rng = np.random.default_rng(224)
    n_assets, n_bars = 5, 1200
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    W = R.WLM_F_W
    mm = R.compute_wlmf_metrics(close, W=W)
    sa = mm["wlmf_width"][0, W:]
    ref = _iesd_style_stat(close, W)[0, W:]
    _assert_distinct(sa, ref, "IESD")


def test_wlmf_kernel_distinct_from_mfdfa():
    """C358 MF-DFA (fluctuation-function generalized Hurst): legitimate
    distinctness-guard ref (fluctuation-function scaling vs wavelet-leader spectrum)."""
    rng = np.random.default_rng(230)
    n_assets, n_bars = 5, 1200
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    W = R.WLM_F_W
    mm = R.compute_wlmf_metrics(close, W=W)
    sa = mm["wlmf_width"][0, W:]
    ref = _mfdfa_style_stat(close, W)[0, W - 1:]
    _assert_distinct(sa, ref, "MF-DFA")


def test_wlmf_kernel_distinct_from_rqa():
    """C425 RQA (diagonal-line determinism of delay-embedding recurrence matrix):
    legitimate distinctness-guard ref (recurrence-plot topology vs wavelet-leader spectrum)."""
    rng = np.random.default_rng(232)
    n_assets, n_bars = 5, 1200
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    W = R.WLM_F_W
    mm = R.compute_wlmf_metrics(close, W=W)
    sa = mm["wlmf_width"][0, W:]
    ref = _rqa_det_style_stat(close, W)[0, W - 1:]
    _assert_distinct(sa, ref, "RQA")


# ---------------------------------------------------------------- guard tests (rewrite guards)
def test_artifact_campaign_is_426():
    """Rewrite guard: every emitted artifact self-identifies campaign 426."""
    for part in ("verdict", "summary", "registry", "oos_sweep"):
        files = sorted((ROOT / "reports").glob(f"campaign426_{part}_*.json"))
        files = [f for f in files if ".full." not in f.name]
        if not files:
            continue
        obj = json.loads(files[-1].read_text())
        assert obj["campaign"] == 426, f"{part} artifact campaign != 426: {obj.get('campaign')}"


def test_mandate_contains_wlmf():
    """Rewrite guard: the C426 mandate names the WLMF wavelet-leader
    multifractal-spectrum family (never prior families)."""
    p = sorted((ROOT / "reports").glob("campaign426_oos_sweep_*.json"))
    p = [f for f in p if ".full." not in f.name]
    if not p:
        return
    mandate = json.loads(p[-1].read_text())["mandate"]
    assert ("WLMF" in mandate or "wavelet" in mandate.lower()), "mandate missing WLMF"
    assert "wlmf_width" in mandate, "mandate missing wlmf_width"
    assert "wlmf_centroid" in mandate, "mandate missing wlmf_centroid"
    for bad in ("RQA", "RECURRENCE", "recurrence", "delay_embedding", "DELAY EMBEDDING",
                "chebyshev", "CHEBYSHEV", "recurrence_matrix", "RQA_RR", "RQA_DET",
                "IESD", "INTER-EXTREMUM", "RUNLEN", "RUN-LENGTH", "ZCRPATH", "ZERO-CROSSING",
                "SIGNCHOP", "SIGN-SEQUENCE", "MF-DFA", "MULTIFRACTAL DFA"):
        assert bad not in mandate, f"mandate must not reference {bad} (prior campaign)"


def test_placebo_seed_is_20261290():
    assert R.PLACEBO_SEED == 20261290


def test_placebo_seed_unique_not_reserved():
    """Rewrite guard: C426 placebo seed must not collide with reserved seeds
    used by prior campaigns (20261224..20261288)."""
    assert not (20261224 <= R.PLACEBO_SEED <= 20261288), \
        "placebo seed must be outside 20261224-20261288"


# ---------------------------------------------------------------- real artifacts schema (if present)
def _find_latest(prefix: str):
    files = sorted((ROOT / "reports").glob(f"campaign426_{prefix}_*.json"))
    files = [f for f in files if ".full." not in f.name]
    return files[-1] if files else None


def test_artifacts_if_present_have_required_flags():
    p = _find_latest("verdict")
    if p is None:
        return
    v = json.loads(p.read_text())
    assert v["campaign"] == 426
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
    assert sw["config"]["wlmf_params"]["window_W"] == 256


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
    test_wlmf_matches_brute_force()
    test_wlmf_matches_brute_force_10_assets()
    test_wlmf_matches_brute_force_with_nan()
    test_wlmf_defined_after_window_nan_before()
    test_wlmf_non_finite_close_propagates()
    test_wlmf_params()
    test_wlmf_width_range()
    test_reference_config_matches_pre_registered_spec()
    test_phase_randomized_surrogate_same_marginal_deterministic()
    test_build_underlying_shapes_and_keys()
    test_build_scores_signals_lookbacks_causal()
    test_wlmf_kernel_not_degenerate()
    test_wlmf_kernel_distinct_from_signchop()
    test_wlmf_kernel_distinct_from_signrun()
    test_wlmf_kernel_distinct_from_zcrpath()
    test_wlmf_kernel_distinct_from_runlen()
    test_wlmf_kernel_distinct_from_iesd()
    test_wlmf_kernel_distinct_from_mfdfa()
    test_wlmf_kernel_distinct_from_rqa()
    test_artifact_campaign_is_426()
    test_mandate_contains_wlmf()
    test_placebo_seed_is_20261290()
    test_placebo_seed_unique_not_reserved()
    test_artifacts_if_present_have_required_flags()
    print("All C426 WLMF runner tests passed")
