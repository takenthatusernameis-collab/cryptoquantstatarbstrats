"""Tests for C419 runner (scripts/run_c419_rcf_xsec_oos.py): pure-function
tests on synthetic arrays (including a brute-force equality test for the
vectorized RCF standardized empirical-characteristic-function kernel vs the
per-window cos/sin reference) plus schema/flag validation of emitted real-data
artifacts. No network, no fabricated market data."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import run_c419_rcf_xsec_oos as R  # noqa: E402


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
    for pb in ("rcf_mod_placebo", "rcf_imag_placebo"):
        assert pb in R.SIGNALS
    for real in ("rcf_mod_dev", "rcf_imag_dev"):
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


# ---------------------------------------------------------------- RCF kernel (brute-force equality)
def test_rcf_matches_brute_force():
    """The vectorized RCF kernel MUST equal the brute-force reference
    (per-window loop with explicit np.cos/np.sin). Compared with maxdiff < 1e-12
    and matching NaN patterns."""
    rng = np.random.default_rng(20261283)
    n_assets, n_bars = 5, 4000
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    fast = R.compute_rcf_metrics(log_return, R.RCF_W, R.RCF_U0)
    brute = R._rcf_bruteforce(log_return, R.RCF_W, R.RCF_U0)
    for key in ("rcf_mod", "rcf_imag"):
        fv, fb = fast[key], brute[key]
        fin = np.isfinite(fv) & np.isfinite(fb)
        assert fin.sum() > 0, f"{key}: no finite overlapping points"
        assert np.array_equal(np.isnan(fv), np.isnan(fb)), f"{key}: NaN pattern mismatch"
        maxdiff = float(np.max(np.abs(fv[fin] - fb[fin]))) if fin.sum() else 0.0
        assert maxdiff < 1e-12, f"{key}: maxdiff={maxdiff} >= 1e-12"


def test_rcf_matches_brute_force_10_assets():
    """Brute-force equality with the full 10-asset panel (the real universe width)."""
    rng = np.random.default_rng(4192)
    n_assets, n_bars = 10, 1500
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    fast = R.compute_rcf_metrics(log_return, R.RCF_W, R.RCF_U0)
    brute = R._rcf_bruteforce(log_return, R.RCF_W, R.RCF_U0)
    for key in ("rcf_mod", "rcf_imag"):
        fv, fb = fast[key], brute[key]
        fin = np.isfinite(fv) & np.isfinite(fb)
        assert fin.sum() > 0, key
        maxdiff = float(np.max(np.abs(fv[fin] - fb[fin])))
        assert maxdiff < 1e-12, f"rcf_{key}: maxdiff={maxdiff}"


def test_rcf_matches_brute_force_with_nan():
    """Brute-force equality when the panel contains NaNs."""
    rng = np.random.default_rng(99)
    n_assets, n_bars = 4, 1200
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    log_return[1, 400] = np.nan
    log_return[2, 401] = np.nan
    fast = R.compute_rcf_metrics(log_return, R.RCF_W, R.RCF_U0)
    brute = R._rcf_bruteforce(log_return, R.RCF_W, R.RCF_U0)
    for key in ("rcf_mod", "rcf_imag"):
        fv, fb = fast[key], brute[key]
        fin = np.isfinite(fv) & np.isfinite(fb)
        assert np.array_equal(np.isnan(fv), np.isnan(fb)), f"{key}: NaN mismatch"
        maxdiff = float(np.max(np.abs(fv[fin] - fb[fin]))) if fin.sum() else 0.0
        assert maxdiff < 1e-12, f"{key}: maxdiff={maxdiff}"


def test_rcf_defined_after_window_nan_before():
    rng = np.random.default_rng(3)
    n_assets, n_bars = 3, 600
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.005
    W = R.RCF_W
    m = R.compute_rcf_metrics(log_return, W)
    for key in ("rcf_mod", "rcf_imag"):
        assert np.isnan(m[key][:, :W]).all(), key
        assert np.isfinite(m[key][:, W:]).any(), key


def test_rcf_non_finite_return_propagates():
    """A non-finite return in any asset at a bar -> NaN for all RCF outputs in
    every window covering that bar."""
    rng = np.random.default_rng(9)
    n_assets, n_bars = 4, 600
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.005
    log_return[0, 300] = np.inf
    W = R.RCF_W
    m = R.compute_rcf_metrics(log_return, W)
    for t in range(300, min(300 + W, n_bars)):
        for key in ("rcf_mod", "rcf_imag"):
            assert np.isnan(m[key][:, t]).all(), f"rcf_{key} t={t} should be NaN"
    for t in range(W, 300):
        for key in ("rcf_mod", "rcf_imag"):
            assert np.isfinite(m[key][:, t]).any(), f"rcf_{key} t={t} should be finite"


def test_rcf_params():
    assert R.RCF_W == 256
    assert R.RCF_U0 == 1.0


def test_rcf_mod_range_and_imag_range():
    """rcf_mod (ECF modulus) in [0,1]; rcf_imag (imaginary part) in [-1,1]."""
    rng = np.random.default_rng(11)
    n_assets, n_bars = 10, 800
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    m = R.compute_rcf_metrics(log_return, R.RCF_W, R.RCF_U0)
    mod = m["rcf_mod"]
    imag = m["rcf_imag"]
    fin = np.isfinite(mod)
    assert fin.sum() > 0
    assert (mod[fin] >= 0.0).all() and (mod[fin] <= 1.0).all()
    ifin = np.isfinite(imag)
    assert ifin.sum() > 0
    assert (imag[ifin] >= -1.0).all() and (imag[ifin] <= 1.0).all()


def test_reference_config_matches_pre_registered_spec():
    assert R.ATTR_REPRESENTATIVES == {
        "rcf_mod_dev": "rcf_mod_dev",
        "rcf_imag_dev": "rcf_imag_dev",
    }
    assert R.PLACEBO_SEED == 20261283
    assert R.STABILITY_MIN_SIGN_CONSISTENCY == 0.70
    assert R.STABILITY_MIN_SHARPE_CORR == 0.50
    assert R.DOMINANT_SHARE_MIN == 0.50
    assert R.TRAIN_M == 12 and R.TEST_M == 3 and R.ROLL_M == 3
    assert R.RCF_W == 256
    assert R.RCF_U0 == 1.0
    assert R.SIGNALS[0] == "rcf_mod_dev"


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
    assert set(series.keys()) == {"rcf_mod", "rcf_imag"}
    for k in ("rcf_mod", "rcf_imag"):
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
def test_rcf_kernel_not_degenerate():
    """Rewrite guard: RCF metrics are not degenerate (not allclose to 0 where defined)."""
    rng = np.random.default_rng(55)
    n_assets, n_bars = 5, 1600
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    W = R.RCF_W
    mm = R.compute_rcf_metrics(log_return, W, R.RCF_U0)
    for name in ("rcf_mod", "rcf_imag"):
        arr = mm[name]
        fin = np.isfinite(arr)
        assert fin.sum() > 0, f"rcf_{name}: no finite values"
        assert not np.allclose(arr[fin], 0.0, atol=1e-12), f"rcf_{name} collapses to 0"


# ---- inline prior-family reference statistics (distinctness guards)
def _acovk_style_stat(log_return, W, lags=(1, 2, 4, 8)):
    """Inline C375 ACOVK unnormalized realized autocovariance gamma_k (own-lag
    covariance), not the value-distribution ECF."""
    X = np.asarray(log_return, dtype=float)
    n_assets, n = X.shape
    m = X.mean(axis=0, keepdims=True)
    Xc = X - m
    out = np.full((n_assets, n), np.nan)
    for t in range(W, n):
        span = Xc[:, t - W + 1:t + 1]
        if not np.isfinite(span).all():
            continue
        for i in range(n_assets):
            vals = []
            for k in lags:
                a = span[i, :-k] if k < W else span[i, :0]
                b = span[i, k:] if k < W else span[i, :0]
                if len(a) < 3:
                    continue
                vals.append(float(np.mean(a * b)))
            out[i, t] = float(np.mean(vals)) if vals else np.nan
    return out


def _poly_skew_stat(log_return, W):
    """Inline C361 RSKEW / C371 RSK-style statistic: rolling third standardized
    moment (unbounded polynomial moment = a derivative of phi at 0), not the ECF."""
    X = np.asarray(log_return, dtype=float)
    n_assets, n = X.shape
    out = np.full((n_assets, n), np.nan)
    for t in range(W, n):
        span = X[:, t - W + 1:t + 1]
        if not np.isfinite(span).all():
            continue
        for i in range(n_assets):
            s = span[i]
            sd = s.std()
            if sd <= 0:
                continue
            out[i, t] = float(np.mean(((s - s.mean()) / sd) ** 3))
    return out


def _domfreq_style_stat(log_return, W):
    """Inline C404 DOMFREQ-style statistic: dominant cycle length (argmax of the
    rfft power spectrum of the detrended window) — an FFT of the TIME SERIES, not
    the value distribution."""
    X = np.asarray(log_return, dtype=float)
    n_assets, n = X.shape
    out = np.full((n_assets, n), np.nan)
    for t in range(W, n):
        span = X[:, t - W + 1:t + 1]
        if not np.isfinite(span).all():
            continue
        for i in range(n_assets):
            y = span[i] - span[i].mean()
            P = np.abs(np.fft.rfft(y)) ** 2
            P[0] = 0.0
            j = int(np.argmax(P))
            out[i, t] = float(W / j) if j > 0 else float(W)
    return out


def _qatm_style_stat(log_return, W):
    """Inline C363 QATM / C376 QSPREAD-style statistic: (q90-q10) quantile spread
    of the window — an order-statistic object, not the ECF."""
    X = np.asarray(log_return, dtype=float)
    n_assets, n = X.shape
    out = np.full((n_assets, n), np.nan)
    for t in range(W, n):
        span = X[:, t - W + 1:t + 1]
        if not np.isfinite(span).all():
            continue
        for i in range(n_assets):
            q = np.percentile(span[i], [10, 90])
            out[i, t] = float(q[1] - q[0])
    return out


def _magnet_style_stat(log_return, W):
    """Inline C396 MAGNET-style statistic: Shannon entropy of magnitude bins — a
    magnitude-bin entropy object, not the ECF."""
    X = np.asarray(log_return, dtype=float)
    n_assets, n = X.shape
    out = np.full((n_assets, n), np.nan)
    for t in range(W, n):
        span = X[:, t - W + 1:t + 1]
        if not np.isfinite(span).all():
            continue
        for i in range(n_assets):
            a = np.abs(span[i])
            hist, _ = np.histogram(a, bins=8)
            p = hist[hist > 0] / hist.sum()
            out[i, t] = float(-np.sum(p * np.log(p)))
    return out


def _assert_distinct(sa, ref, name):
    fin = np.isfinite(sa) & np.isfinite(ref)
    assert fin.sum() > 0, name
    assert not np.allclose(sa[fin], ref[fin], atol=1e-6), f"RCF degenerates to {name}"


def test_rcf_kernel_distinct_from_acovk():
    """C375 ACOVK (unnormalized own-lag autocovariance): legitimate distinctness-guard ref."""
    rng = np.random.default_rng(214)
    n_assets, n_bars = 5, 1200
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    W = R.RCF_W
    mm = R.compute_rcf_metrics(log_return, W, R.RCF_U0)
    sa = mm["rcf_mod"][0, W:]
    ref = _acovk_style_stat(log_return, W)[0, W:]
    _assert_distinct(sa, ref, "ACOVK")


def test_rcf_kernel_distinct_from_poly_skew():
    """C361 RSKEW / C371 RSK (polynomial moment): legitimate distinctness-guard ref."""
    rng = np.random.default_rng(215)
    n_assets, n_bars = 5, 1200
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    W = R.RCF_W
    mm = R.compute_rcf_metrics(log_return, W, R.RCF_U0)
    sa = mm["rcf_imag"][0, W:]
    ref = _poly_skew_stat(log_return, W)[0, W:]
    _assert_distinct(sa, ref, "RSKEW")


def test_rcf_kernel_distinct_from_domfreq():
    """C404 DOMFREQ (time-series FFT dominant cycle): legitimate distinctness-guard ref."""
    rng = np.random.default_rng(216)
    n_assets, n_bars = 5, 1200
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    W = R.RCF_W
    mm = R.compute_rcf_metrics(log_return, W, R.RCF_U0)
    sa = mm["rcf_mod"][0, W:]
    ref = _domfreq_style_stat(log_return, W)[0, W:]
    _assert_distinct(sa, ref, "DOMFREQ")


def test_rcf_kernel_distinct_from_qatm():
    """C363 QATM / C376 QSPREAD (quantile spread): legitimate distinctness-guard ref."""
    rng = np.random.default_rng(217)
    n_assets, n_bars = 5, 1200
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    W = R.RCF_W
    mm = R.compute_rcf_metrics(log_return, W, R.RCF_U0)
    sa = mm["rcf_imag"][0, W:]
    ref = _qatm_style_stat(log_return, W)[0, W:]
    _assert_distinct(sa, ref, "QATM")


def test_rcf_kernel_distinct_from_magnet():
    """C396 MAGNET (magnitude-bin entropy): legitimate distinctness-guard ref."""
    rng = np.random.default_rng(218)
    n_assets, n_bars = 5, 1200
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    W = R.RCF_W
    mm = R.compute_rcf_metrics(log_return, W, R.RCF_U0)
    sa = mm["rcf_mod"][0, W:]
    ref = _magnet_style_stat(log_return, W)[0, W:]
    _assert_distinct(sa, ref, "MAGNET")


# ---------------------------------------------------------------- guard tests (rewrite guards)
def test_artifact_campaign_is_419():
    """Rewrite guard: every emitted artifact self-identifies campaign 419."""
    for part in ("verdict", "summary", "registry", "oos_sweep"):
        files = sorted((ROOT / "reports").glob(f"campaign419_{part}_*.json"))
        files = [f for f in files if ".full." not in f.name]
        if not files:
            continue
        obj = json.loads(files[-1].read_text())
        assert obj["campaign"] == 419, f"{part} artifact campaign != 419: {obj.get('campaign')}"


def test_mandate_contains_rcf():
    """Rewrite guard: the C419 mandate names the RCF standardized empirical
    characteristic function (never prior families)."""
    p = sorted((ROOT / "reports").glob("campaign419_oos_sweep_*.json"))
    p = [f for f in p if ".full." not in f.name]
    if not p:
        return
    mandate = json.loads(p[-1].read_text())["mandate"]
    assert "RCF" in mandate, "mandate missing RCF"
    assert "EMPIRICAL CHARACTERISTIC" in mandate.upper(), "mandate missing EMPIRICAL CHARACTERISTIC"
    assert "rcf_mod" in mandate, "mandate missing rcf_mod"
    assert "rcf_imag" in mandate, "mandate missing rcf_imag"
    for bad in ("AUTOCF", "AUTOCORRELATION", "DECORRELATION", "RHO",
                "CDOMIN", "DOMINANCE", "ARGMAX", "TAILDEP", "EXCEEDANCE",
                "TAILBETA", "TAIL BETA", "SIGNPOWER", "FRACTIONAL", "XCORR",
                "SEMCORR", "RESIDVOL", "IDIOSYNCRATIC", "RESIDUAL", "LEADLAG",
                "LEADER-FOLLOWER", "BETAASYM", "COSKEW", "COKURT", "ASYMCURV",
                "TSCALE", "HILL", "RVQUART", "QUARTICITY", "KTREND", "CBREAK",
                "SPECFM", "MAGNET", "OUHALFLIFE", "CTES", "VTERM", "DDRUN",
                "XSKEW3", "XCOEX", "MINRV", "MADR", "BANDX", "PRROUGH",
                "HALFRANGE", "LMOM", "SEMICOV", "LVAC", "DSRV", "RSKEK",
                "ACOVK", "TIRV", "XSRANK", "RANK-PERSISTENCE", "SIGNRUN",
                "RUN-LENGTH", "SIGNCO-MOTION", "SAME-SIGN", "QREG",
                "QUANTILE-REGRESSION", "QUANTILE REGRESSION", "QATM", "QSPREAD"):
        assert bad not in mandate, f"mandate must not reference {bad} (prior campaign)"


def test_placebo_seed_is_20261283():
    assert R.PLACEBO_SEED == 20261283


def test_placebo_seed_unique_not_reserved():
    """Rewrite guard: C419 placebo seed must not collide with reserved seeds
    used by prior campaigns."""
    assert not (20261224 <= R.PLACEBO_SEED <= 20261281), "placebo seed must be outside 20261224-20261281"


# ---------------------------------------------------------------- real artifacts schema (if present)
def _find_latest(prefix: str):
    files = sorted((ROOT / "reports").glob(f"campaign419_{prefix}_*.json"))
    files = [f for f in files if ".full." not in f.name]
    return files[-1] if files else None


def test_artifacts_if_present_have_required_flags():
    p = _find_latest("verdict")
    if p is None:
        return
    v = json.loads(p.read_text())
    assert v["campaign"] == 419
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
    assert sw["config"]["rcf_params"]["window_W"] == 256
    assert sw["config"]["rcf_params"]["u0"] == 1.0


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
    test_rcf_matches_brute_force()
    test_rcf_matches_brute_force_10_assets()
    test_rcf_matches_brute_force_with_nan()
    test_rcf_defined_after_window_nan_before()
    test_rcf_non_finite_return_propagates()
    test_rcf_params()
    test_rcf_mod_range_and_imag_range()
    test_reference_config_matches_pre_registered_spec()
    test_phase_randomized_surrogate_same_marginal_deterministic()
    test_build_underlying_shapes_and_keys()
    test_build_scores_signals_lookbacks_causal()
    test_rcf_kernel_not_degenerate()
    test_rcf_kernel_distinct_from_acovk()
    test_rcf_kernel_distinct_from_poly_skew()
    test_rcf_kernel_distinct_from_domfreq()
    test_rcf_kernel_distinct_from_qatm()
    test_rcf_kernel_distinct_from_magnet()
    test_artifact_campaign_is_419()
    test_mandate_contains_rcf()
    test_placebo_seed_is_20261283()
    test_placebo_seed_unique_not_reserved()
    test_artifacts_if_present_have_required_flags()
    print("All C419 RCF runner tests passed")