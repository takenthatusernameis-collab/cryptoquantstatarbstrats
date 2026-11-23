"""Tests for C420 runner (scripts/run_c420_scoh_xsec_oos.py): pure-function
tests on synthetic arrays (including a brute-force equality test for the
vectorized SCOH spectral-coherence / Welch cross-spectrum kernel vs the
per-window explicit np.fft.rfft reference) plus schema/flag validation of
emitted real-data artifacts. No network, no fabricated market data."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import run_c420_scoh_xsec_oos as R  # noqa: E402


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
    for pb in ("coh_mean_placebo", "coh_low_placebo"):
        assert pb in R.SIGNALS
    for real in ("coh_mean_dev", "coh_low_dev"):
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


# ---------------------------------------------------------------- SCOH kernel (brute-force equality)
def test_scoh_matches_brute_force():
    """The vectorized SCOH kernel MUST equal the brute-force reference
    (per-window loop with explicit np.fft.rfft per segment). Compared with
    maxdiff < 1e-9 (FFT round-off) and matching NaN patterns."""
    rng = np.random.default_rng(20261284)
    n_assets, n_bars = 5, 4000
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    fast = R.compute_scoh_metrics(log_return, R.SCOH_W, R.SCOH_SEG_LEN,
                                  R.SCOH_N_SEG, R.SCOH_SEG_STARTS, R.SCOH_EPS)
    brute = R._scoh_bruteforce(log_return, R.SCOH_W, R.SCOH_SEG_LEN,
                               R.SCOH_N_SEG, R.SCOH_SEG_STARTS, R.SCOH_EPS)
    for key in ("coh_mean", "coh_low"):
        fv, fb = fast[key], brute[key]
        fin = np.isfinite(fv) & np.isfinite(fb)
        assert fin.sum() > 0, f"{key}: no finite overlapping points"
        assert np.array_equal(np.isnan(fv), np.isnan(fb)), f"{key}: NaN pattern mismatch"
        maxdiff = float(np.max(np.abs(fv[fin] - fb[fin]))) if fin.sum() else 0.0
        assert maxdiff < 1e-9, f"{key}: maxdiff={maxdiff} >= 1e-9"


def test_scoh_matches_brute_force_10_assets():
    """Brute-force equality with the full 10-asset panel (the real universe width)."""
    rng = np.random.default_rng(4202)
    n_assets, n_bars = 10, 1500
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    fast = R.compute_scoh_metrics(log_return, R.SCOH_W, R.SCOH_SEG_LEN,
                                  R.SCOH_N_SEG, R.SCOH_SEG_STARTS, R.SCOH_EPS)
    brute = R._scoh_bruteforce(log_return, R.SCOH_W, R.SCOH_SEG_LEN,
                               R.SCOH_N_SEG, R.SCOH_SEG_STARTS, R.SCOH_EPS)
    for key in ("coh_mean", "coh_low"):
        fv, fb = fast[key], brute[key]
        fin = np.isfinite(fv) & np.isfinite(fb)
        assert fin.sum() > 0, key
        maxdiff = float(np.max(np.abs(fv[fin] - fb[fin])))
        assert maxdiff < 1e-9, f"scoh_{key}: maxdiff={maxdiff}"


def test_scoh_matches_brute_force_with_nan():
    """Brute-force equality when the panel contains NaNs (global across assets)."""
    rng = np.random.default_rng(99)
    n_assets, n_bars = 4, 1200
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    log_return[1, 400] = np.nan
    log_return[2, 401] = np.nan
    fast = R.compute_scoh_metrics(log_return, R.SCOH_W, R.SCOH_SEG_LEN,
                                  R.SCOH_N_SEG, R.SCOH_SEG_STARTS, R.SCOH_EPS)
    brute = R._scoh_bruteforce(log_return, R.SCOH_W, R.SCOH_SEG_LEN,
                               R.SCOH_N_SEG, R.SCOH_SEG_STARTS, R.SCOH_EPS)
    for key in ("coh_mean", "coh_low"):
        fv, fb = fast[key], brute[key]
        fin = np.isfinite(fv) & np.isfinite(fb)
        assert np.array_equal(np.isnan(fv), np.isnan(fb)), f"{key}: NaN mismatch"
        maxdiff = float(np.max(np.abs(fv[fin] - fb[fin]))) if fin.sum() else 0.0
        assert maxdiff < 1e-9, f"{key}: maxdiff={maxdiff}"


def test_scoh_defined_after_window_nan_before():
    rng = np.random.default_rng(3)
    n_assets, n_bars = 3, 600
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.005
    W = R.SCOH_W
    m = R.compute_scoh_metrics(log_return, W)
    for key in ("coh_mean", "coh_low"):
        assert np.isnan(m[key][:, :W]).all(), key
        assert np.isfinite(m[key][:, W:]).any(), key


def test_scoh_non_finite_return_propagates():
    """A non-finite return in any asset at a bar -> NaN for all SCOH outputs in
    every window covering that bar (global-across-assets finiteness gate)."""
    rng = np.random.default_rng(9)
    n_assets, n_bars = 4, 600
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.005
    log_return[0, 300] = np.inf
    W = R.SCOH_W
    m = R.compute_scoh_metrics(log_return, W)
    for t in range(300, min(300 + W, n_bars)):
        for key in ("coh_mean", "coh_low"):
            assert np.isnan(m[key][:, t]).all(), f"scoh_{key} t={t} should be NaN"
    for t in range(W, 300):
        for key in ("coh_mean", "coh_low"):
            assert np.isfinite(m[key][:, t]).any(), f"scoh_{key} t={t} should be finite"


def test_scoh_params():
    assert R.SCOH_W == 256
    assert R.SCOH_SEG_LEN == 128
    assert R.SCOH_N_SEG == 3
    assert R.SCOH_SEG_STARTS == (0, 64, 128)
    assert R.SCOH_EPS == 1e-12


def test_coh_range_and_low_band_subset():
    """coh_mean and coh_low are magnitude-squared coherences in [0,1]. coh_low
    (low-frequency band, mean of j=1..8) is the mean over a subset of the bins
    averaged by coh_mean, so it is also in [0,1]."""
    rng = np.random.default_rng(11)
    n_assets, n_bars = 10, 800
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    m = R.compute_scoh_metrics(log_return, R.SCOH_W)
    for key in ("coh_mean", "coh_low"):
        arr = m[key]
        fin = np.isfinite(arr)
        assert fin.sum() > 0, key
        assert (arr[fin] >= 0.0).all() and (arr[fin] <= 1.0).all(), key


def test_reference_config_matches_pre_registered_spec():
    assert R.ATTR_REPRESENTATIVES == {
        "coh_mean_dev": "coh_mean_dev",
        "coh_low_dev": "coh_low_dev",
    }
    assert R.PLACEBO_SEED == 20261284
    assert R.STABILITY_MIN_SIGN_CONSISTENCY == 0.70
    assert R.STABILITY_MIN_SHARPE_CORR == 0.50
    assert R.DOMINANT_SHARE_MIN == 0.50
    assert R.TRAIN_M == 12 and R.TEST_M == 3 and R.ROLL_M == 3
    assert R.SCOH_W == 256
    assert R.SCOH_SEG_LEN == 128
    assert R.SCOH_SEG_STARTS == (0, 64, 128)
    assert R.SIGNALS[0] == "coh_mean_dev"


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
    assert set(series.keys()) == {"coh_mean", "coh_low"}
    for k in ("coh_mean", "coh_low"):
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
def test_scoh_kernel_not_degenerate():
    """Rewrite guard: SCOH coherence metrics are not degenerate (not allclose to
    0 where defined)."""
    rng = np.random.default_rng(55)
    n_assets, n_bars = 5, 1600
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    W = R.SCOH_W
    mm = R.compute_scoh_metrics(log_return, W)
    for name in ("coh_mean", "coh_low"):
        arr = mm[name]
        fin = np.isfinite(arr)
        assert fin.sum() > 0, f"scoh_{name}: no finite values"
        assert not np.allclose(arr[fin], 0.0, atol=1e-12), f"scoh_{name} collapses to 0"


# ---- inline prior-family reference statistics (distinctness guards)
def _domfreq_style_stat(log_return, W):
    """Inline C404 DOMFREQ-style statistic: dominant cycle length (argmax of the
    rfft power spectrum of the detrended own window) — an FFT of the own TIME
    SERIES, not a cross-spectrum/coherence."""
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


def _specfm_style_stat(log_return, W):
    """Inline C397 SPECFM-style statistic: spectral flatness (geometric/arithmetic
    mean ratio of the own-window power spectrum) — own spectrum, not coherence."""
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
            P = P[1:]  # exclude DC
            s = P.sum()
            if s <= 0:
                continue
            gm = np.exp(np.mean(np.log(P + 1e-300)))
            am = np.mean(P)
            out[i, t] = float(gm / am) if am > 0 else np.nan
    return out


def _xcorr_style_stat(log_return, W):
    """Inline C410 XCORR-style statistic: average pairwise time-domain Pearson
    correlation of the asset vs the other assets over the window — a time-domain
    co-movement, not a frequency-localized coherence."""
    X = np.asarray(log_return, dtype=float)
    n_assets, n = X.shape
    out = np.full((n_assets, n), np.nan)
    for t in range(W, n):
        span = X[:, t - W + 1:t + 1]
        if not np.isfinite(span).all():
            continue
        C = np.corrcoef(span)
        for i in range(n_assets):
            others = [C[i, j] for j in range(n_assets) if j != i]
            vals = [v for v in others if np.isfinite(v)]
            out[i, t] = float(np.mean(vals)) if vals else np.nan
    return out


def _autocf_style_stat(log_return, W):
    """Inline C418 AUTOCF-style statistic: lag-1..4 autocorrelation of the OWN
    return series (own-return autocorrelation), not a cross-spectrum/coherence."""
    X = np.asarray(log_return, dtype=float)
    n_assets, n = X.shape
    out = np.full((n_assets, n), np.nan)
    for t in range(W, n):
        span = X[:, t - W + 1:t + 1]
        if not np.isfinite(span).all():
            continue
        for i in range(n_assets):
            x = span[i] - span[i].mean()
            sd = x.std()
            if sd <= 0:
                continue
            vals = []
            for k in (1, 2, 3, 4):
                vals.append(float(np.mean(x[:-k] * x[k:]) / (sd * sd)))
            out[i, t] = float(np.mean(vals)) if vals else np.nan
    return out


def _assert_distinct(sa, ref, name):
    fin = np.isfinite(sa) & np.isfinite(ref)
    assert fin.sum() > 0, name
    assert not np.allclose(sa[fin], ref[fin], atol=1e-6), f"SCOH degenerates to {name}"


def test_scoh_kernel_distinct_from_domfreq():
    """C404 DOMFREQ (own time-series FFT dominant cycle): legitimate distinctness-guard ref."""
    rng = np.random.default_rng(214)
    n_assets, n_bars = 5, 1200
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    W = R.SCOH_W
    mm = R.compute_scoh_metrics(log_return, W)
    sa = mm["coh_mean"][0, W:]
    ref = _domfreq_style_stat(log_return, W)[0, W:]
    _assert_distinct(sa, ref, "DOMFREQ")


def test_scoh_kernel_distinct_from_specfm():
    """C397 SPECFM (own-spectrum flatness): legitimate distinctness-guard ref."""
    rng = np.random.default_rng(215)
    n_assets, n_bars = 5, 1200
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    W = R.SCOH_W
    mm = R.compute_scoh_metrics(log_return, W)
    sa = mm["coh_low"][0, W:]
    ref = _specfm_style_stat(log_return, W)[0, W:]
    _assert_distinct(sa, ref, "SPECFM")


def test_scoh_kernel_distinct_from_xcorr():
    """C410 XCORR (time-domain average pairwise correlation): legitimate
    distinctness-guard ref (coherence is frequency-localized, XCORR is broadband)."""
    rng = np.random.default_rng(216)
    n_assets, n_bars = 5, 1200
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    W = R.SCOH_W
    mm = R.compute_scoh_metrics(log_return, W)
    sa = mm["coh_mean"][0, W:]
    ref = _xcorr_style_stat(log_return, W)[0, W:]
    _assert_distinct(sa, ref, "XCORR")


def test_scoh_kernel_distinct_from_autocf():
    """C418 AUTOCF (own-return autocorrelation): legitimate distinctness-guard ref
    (SCOH is a vs-market cross-spectrum, AUTOCF is own-return autocorrelation)."""
    rng = np.random.default_rng(217)
    n_assets, n_bars = 5, 1200
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    W = R.SCOH_W
    mm = R.compute_scoh_metrics(log_return, W)
    sa = mm["coh_low"][0, W:]
    ref = _autocf_style_stat(log_return, W)[0, W:]
    _assert_distinct(sa, ref, "AUTOCF")


# ---------------------------------------------------------------- guard tests (rewrite guards)
def test_artifact_campaign_is_420():
    """Rewrite guard: every emitted artifact self-identifies campaign 420."""
    for part in ("verdict", "summary", "registry", "oos_sweep"):
        files = sorted((ROOT / "reports").glob(f"campaign420_{part}_*.json"))
        files = [f for f in files if ".full." not in f.name]
        if not files:
            continue
        obj = json.loads(files[-1].read_text())
        assert obj["campaign"] == 420, f"{part} artifact campaign != 420: {obj.get('campaign')}"


def test_mandate_contains_scoh():
    """Rewrite guard: the C420 mandate names the SCOH spectral-coherence family
    (never prior families)."""
    p = sorted((ROOT / "reports").glob("campaign420_oos_sweep_*.json"))
    p = [f for f in p if ".full." not in f.name]
    if not p:
        return
    mandate = json.loads(p[-1].read_text())["mandate"]
    assert "SCOH" in mandate, "mandate missing SCOH"
    assert "SPECTRAL COHERENCE" in mandate.upper(), "mandate missing SPECTRAL COHERENCE"
    assert "CROSS-SPECTRUM" in mandate.upper() or "WELCH" in mandate.upper(), \
        "mandate missing cross-spectrum/Welch"
    assert "coh_mean" in mandate, "mandate missing coh_mean"
    assert "coh_low" in mandate, "mandate missing coh_low"
    for bad in ("RCF", "EMPIRICAL CHARACTERISTIC", "AUTOCF", "AUTOCORRELATION",
                "DECORRELATION", "RHO", "CDOMIN", "DOMINANCE", "ARGMAX",
                "TAILDEP", "EXCEEDANCE", "TAILBETA", "TAIL BETA", "SIGNPOWER",
                "FRACTIONAL", "XCORR", "SEMCORR", "RESIDVOL", "IDIOSYNCRATIC",
                "RESIDUAL", "LEADLAG", "LEADER-FOLLOWER", "BETAASYM", "COSKEW",
                "COKURT", "ASYMCURV", "TSCALE", "HILL", "RVQUART", "QUARTICITY",
                "KTREND", "CBREAK", "SPECFM", "MAGNET", "OUHALFLIFE", "CTES",
                "VTERM", "DDRUN", "XSKEW3", "XCOEX", "MINRV", "MADR", "BANDX",
                "PRROUGH", "HALFRANGE", "LMOM", "SEMICOV", "LVAC", "DSRV",
                "RSKEK", "ACOVK", "TIRV", "XSRANK", "RANK-PERSISTENCE", "SIGNRUN",
                "RUN-LENGTH", "SIGNCO-MOTION", "SAME-SIGN", "QREG",
                "QUANTILE-REGRESSION", "QUANTILE REGRESSION", "QATM", "QSPREAD",
                "DOMFREQ", "DOMINANT SPECTRAL", "SPECTRAL CENTROID"):
        assert bad not in mandate, f"mandate must not reference {bad} (prior campaign)"


def test_placebo_seed_is_20261284():
    assert R.PLACEBO_SEED == 20261284


def test_placebo_seed_unique_not_reserved():
    """Rewrite guard: C420 placebo seed must not collide with reserved seeds
    used by prior campaigns."""
    assert not (20261224 <= R.PLACEBO_SEED <= 20261283), \
        "placebo seed must be outside 20261224-20261283"


# ---------------------------------------------------------------- real artifacts schema (if present)
def _find_latest(prefix: str):
    files = sorted((ROOT / "reports").glob(f"campaign420_{prefix}_*.json"))
    files = [f for f in files if ".full." not in f.name]
    return files[-1] if files else None


def test_artifacts_if_present_have_required_flags():
    p = _find_latest("verdict")
    if p is None:
        return
    v = json.loads(p.read_text())
    assert v["campaign"] == 420
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
    assert sw["config"]["scoh_params"]["window_W"] == 256
    assert sw["config"]["scoh_params"]["seg_len"] == 128
    assert sw["config"]["scoh_params"]["n_seg"] == 3


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
    test_scoh_matches_brute_force()
    test_scoh_matches_brute_force_10_assets()
    test_scoh_matches_brute_force_with_nan()
    test_scoh_defined_after_window_nan_before()
    test_scoh_non_finite_return_propagates()
    test_scoh_params()
    test_coh_range_and_low_band_subset()
    test_reference_config_matches_pre_registered_spec()
    test_phase_randomized_surrogate_same_marginal_deterministic()
    test_build_underlying_shapes_and_keys()
    test_build_scores_signals_lookbacks_causal()
    test_scoh_kernel_not_degenerate()
    test_scoh_kernel_distinct_from_domfreq()
    test_scoh_kernel_distinct_from_specfm()
    test_scoh_kernel_distinct_from_xcorr()
    test_scoh_kernel_distinct_from_autocf()
    test_artifact_campaign_is_420()
    test_mandate_contains_scoh()
    test_placebo_seed_is_20261284()
    test_placebo_seed_unique_not_reserved()
    test_artifacts_if_present_have_required_flags()
    print("All C420 SCOH runner tests passed")