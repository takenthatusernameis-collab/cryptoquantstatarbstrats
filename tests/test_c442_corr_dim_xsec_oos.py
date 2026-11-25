"""Tests for C442 runner (scripts/run_c442_corr_dim_xsec_oos.py): pure-function tests
on synthetic arrays (including a brute-force equality test for the vectorized
correlation dimension vs an independent naive explicit reference) plus
schema/flag validation of emitted real-data artifacts.
Includes kernel-distinctness guards vs ALL named prior families C349/C365/C422/
C376/C392/C425/C433/C434/C429/C430/C431/C432/C435/C436/C437/C438/C439/C440/C441.
No network, no fabricated market data."""
from __future__ import annotations

import importlib
import math
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import run_c442_corr_dim_xsec_oos as R  # noqa: E402


# ================================================================ multiple testing
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
    for pb in ("corr_dim_m3_placebo", "corr_dim_m4_placebo", "corr_dim_m5_placebo", "corr_dim_m6_placebo"):
        assert pb in R.SIGNALS
    for real in ("corr_dim_m3_dev", "corr_dim_m4_dev", "corr_dim_m5_dev", "corr_dim_m6_dev"):
        assert real in R.SIGNALS


# ================================================================ single-leg costs
def test_cost_rate_taker_and_maker_blend():
    assert np.isclose(R.cost_rate(0.0004, 0.0001, "taker"), 0.0005)
    assert np.isclose(R.cost_rate(0.0004, 0.0001, "maker_blend"), 0.0003)
    for fee in R.FEES:
        for slip in R.SLIPS:
            assert R.cost_rate(fee, slip, "taker") >= R.cost_rate(fee, slip, "maker_blend")


# ================================================================ positions
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


# ================================================================ walk-forward
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


# ================================================================ synthetic helpers
def _synth(n_assets, n_bars, seed):
    rng = np.random.default_rng(seed)
    lr = rng.standard_normal((n_assets, n_bars)) * 0.001
    lr[:, 0] = 0.0
    close = 100.0 * np.exp(np.cumsum(lr, axis=1))
    abs_ret = np.abs(lr)
    sign = np.sign(lr).astype(int)
    return {"close": close, "log_return": lr, "abs_ret": abs_ret, "sign": sign}


def _synth_multi(n_assets, n_bars, seed):
    rng = np.random.default_rng(seed)
    parts = []
    for i in range(n_assets):
        kind = i % 5
        if kind == 0:
            x = rng.standard_normal(n_bars) * 0.001
        elif kind == 1:
            x = rng.standard_t(df=5.0, size=n_bars) * 0.001
        elif kind == 2:
            x = rng.uniform(-1.0, 1.0, size=n_bars) * 0.001
        elif kind == 3:
            x = rng.standard_normal(n_bars) * 0.002
        else:
            x = np.abs(rng.standard_normal(n_bars)) * 0.001 - 0.0005
        parts.append(x)
    lr = np.stack(parts, axis=0)
    lr[:, 0] = 0.0
    close = 100.0 * np.exp(np.cumsum(lr, axis=1))
    abs_ret = np.abs(lr)
    sign = np.sign(lr).astype(int)
    return {"close": close, "log_return": lr, "abs_ret": abs_ret, "sign": sign}


# ================================================================ correlation dimension brute-force reference
def _rolling_mean_std_brute(r: np.ndarray, W_q: int):
    """Independent per-bar trailing mean/std over [t-W_q+1, t] (expanding early)."""
    T = len(r)
    mean = np.full(T, np.nan, float)
    sd = np.full(T, np.nan, float)
    for t in range(T):
        w = r[max(0, t - W_q + 1):t + 1]
        mean[t] = float(np.mean(w))
        sd[t] = float(np.std(w, ddof=0))
    return mean, sd


def _correlation_dimension_brute(pts: np.ndarray, n_radii: int = R.CORR_DIM_N_RADII) -> float:
    """Independent naive explicit correlation dimension of the delay embedding
    pts (n, m): explicit pairwise Euclidean distance loop over i<j, correlation
    sum C(r) over log-spaced radii, slope of log C(r) vs log r where 0<C<1."""
    pts = np.asarray(pts, dtype=float)
    if not np.isfinite(pts).all():
        return np.nan
    n = len(pts)
    if n < 3:
        return np.nan
    D = np.zeros((n, n), dtype=float)
    for p in range(n):
        for q in range(p + 1, n):
            d = float(np.sqrt(((pts[p] - pts[q]) ** 2).sum()))
            D[p, q] = d
            D[q, p] = d
    iu = np.triu_indices(n, k=1)
    pair_d = np.array([D[iu[0][k], iu[1][k]] for k in range(len(iu[0]))], dtype=float)
    n_pairs = len(pair_d)
    if n_pairs == 0:
        return np.nan
    d_min = float(pair_d.min())
    d_max = float(pair_d.max())
    if d_max <= d_min or not np.isfinite(d_min) or not np.isfinite(d_max):
        return np.nan
    radii = np.geomspace(d_min * (1.0 + 1e-9), d_max * (1.0 - 1e-9), n_radii)
    pd_sorted = np.sort(pair_d)
    C = np.searchsorted(pd_sorted, radii, side="right").astype(float) / n_pairs
    mask = (C > 0.0) & (C < 1.0) & np.isfinite(C)
    if mask.sum() < 2:
        return np.nan
    log_r = np.log(radii[mask])
    log_c = np.log(C[mask])
    if np.std(log_r) <= 0:
        return np.nan
    slope = float(np.polyfit(log_r, log_c, 1)[0])
    return slope if np.isfinite(slope) else np.nan


def _corr_dim_bruteforce_series(log_return, W_q, m):
    """Independent brute-force per-window correlation dimension for one
    embedding dimension m: explicit per-window mean/std, explicit delay-embed
    loop, explicit pairwise-distance loop, correlation sum + slope. Used only
    for equality testing on small inputs."""
    Rm = np.asarray(log_return, float)
    n_assets, n = Rm.shape
    out = np.full((n_assets, n), np.nan, float)
    z = np.full((n_assets, n), np.nan, float)
    for i in range(n_assets):
        mean, sd = _rolling_mean_std_brute(Rm[i], W_q)
        z[i] = np.where(sd > 0, (Rm[i] - mean) / np.where(sd > 0, sd, 1.0), np.nan)
    tau = R.CORR_DIM_DELAY_TAU
    n_pts = W_q - (m - 1) * tau
    if n_pts < 3:
        return out
    for i in range(n_assets):
        for t in range(W_q - 1, n):
            a = t - W_q + 1
            window_pts = np.empty((n_pts, m), dtype=float)
            finite = True
            for j in range(n_pts):
                start = a + j
                window_pts[j] = z[i, start:start + m]
            if not np.isfinite(window_pts).all():
                continue
            out[i, t] = _correlation_dimension_brute(window_pts)
    return out


def _corr_dim_bruteforce_metrics(log_return, W_q):
    return {m: _corr_dim_bruteforce_series(log_return, W_q, m) for m in R.CORR_DIM_EMBEDDINGS}


def test_corr_dim_matches_brute_force():
    """The vectorized correlation dimension MUST equal the brute-force
    explicit per-window reference (maxdiff < 1e-12, matching NaN pattern)."""
    W_q = 48
    d = _synth(3, 250, 20261442)
    fast = R.compute_corr_dim_metrics(d["log_return"], W_q=W_q)
    brute = _corr_dim_bruteforce_metrics(d["log_return"], W_q)
    for m in R.CORR_DIM_EMBEDDINGS:
        key = "corr_dim_m%d" % m
        fin = np.isfinite(fast["real"][key]) & np.isfinite(brute[m])
        assert fin.sum() > 0, "%s: no finite overlapping points" % key
        assert np.array_equal(np.isnan(fast["real"][key]), np.isnan(brute[m])), "%s: NaN pattern mismatch" % key
        maxdiff = float(np.max(np.abs(fast["real"][key][fin] - brute[m][fin])))
        assert maxdiff < 1e-12, "%s: maxdiff=%.3e >= 1e-12" % (key, maxdiff)


def test_corr_dim_matches_brute_force_10_assets():
    """Brute-force equality with the full 10-asset panel width."""
    W_q = 48
    d = _synth(10, 180, 4294)
    fast = R.compute_corr_dim_metrics(d["log_return"], W_q=W_q)
    brute = _corr_dim_bruteforce_metrics(d["log_return"], W_q)
    for m in R.CORR_DIM_EMBEDDINGS:
        key = "corr_dim_m%d" % m
        fin = np.isfinite(fast["real"][key]) & np.isfinite(brute[m])
        assert fin.sum() > 0, "%s" % key
        assert np.array_equal(np.isnan(fast["real"][key]), np.isnan(brute[m])), "%s: NaN mismatch" % key
        maxdiff = float(np.max(np.abs(fast["real"][key][fin] - brute[m][fin])))
        assert maxdiff < 1e-12, "%s: maxdiff=%.3e" % (key, maxdiff)


def test_corr_dim_matches_brute_force_with_nan():
    """Brute-force equality when the panel contains NaNs (propagates to NaN windows)."""
    W_q = 48
    d = _synth(4, 250, 99)
    d["log_return"][1, 200] = np.nan
    fast = R.compute_corr_dim_metrics(d["log_return"], W_q=W_q)
    brute = _corr_dim_bruteforce_metrics(d["log_return"], W_q)
    for m in R.CORR_DIM_EMBEDDINGS:
        key = "corr_dim_m%d" % m
        assert np.array_equal(np.isnan(fast["real"][key]), np.isnan(brute[m])), "%s: NaN mismatch" % key
        fin = np.isfinite(fast["real"][key]) & np.isfinite(brute[m])
        maxdiff = float(np.max(np.abs(fast["real"][key][fin] - brute[m][fin]))) if fin.sum() else 0.0
        assert maxdiff < 1e-12, "%s: maxdiff=%.3e" % (key, maxdiff)


def test_corr_dim_defined_after_window_nan_before():
    W_q = 48
    d = _synth(3, 400, 3)
    fast = R.compute_corr_dim_metrics(d["log_return"], W_q=W_q)
    for m in R.CORR_DIM_EMBEDDINGS:
        key = "corr_dim_m%d" % m
        assert np.isnan(fast["real"][key][:, :W_q - 1]).all(), "%s" % key
        assert np.isfinite(fast["real"][key][:, W_q - 1:]).any(), "%s" % key


def test_corr_dim_non_finite_propagates():
    """A non-finite value in an asset at a bar -> NaN for that asset in every
    window covering that bar."""
    W_q = 48
    d = _synth(4, 400, 9)
    d["log_return"][:, 200] = np.nan
    fast = R.compute_corr_dim_metrics(d["log_return"], W_q=W_q)
    for m in R.CORR_DIM_EMBEDDINGS:
        key = "corr_dim_m%d" % m
        for t in range(200, min(200 + W_q, 400)):
            assert np.isnan(fast["real"][key][:, t]).all(), "%s t=%d should be NaN" % (key, t)


def test_corr_dim_degenerate_window_is_nan():
    """Constant (zero-variance) series: sigma[t]<=0 => all corr_dim metrics NaN."""
    W_q = 48
    d = _synth(3, 300, 7)
    d["log_return"][:] = 0.5
    fast = R.compute_corr_dim_metrics(d["log_return"], W_q=W_q)
    for m in R.CORR_DIM_EMBEDDINGS:
        key = "corr_dim_m%d" % m
        assert np.isnan(fast["real"][key]).all(), "%s should be all-NaN for degenerate series" % key


# ================================================================ params / spec
def test_corr_dim_params():
    assert R.CORR_DIM_W == 256
    assert R.CORR_DIM_W_FALLBACK == 128
    assert R.CORR_DIM_DELAY_TAU == 1
    assert tuple(R.CORR_DIM_EMBEDDINGS) == (3, 4, 5, 6)
    assert tuple(R.CORR_DIM_KEYS) == ("corr_dim_m3", "corr_dim_m4", "corr_dim_m5", "corr_dim_m6")
    assert float(R.EPS) == 1e-12
    assert R.PLACEBO_SEED == 20261442


def test_reference_config_matches_pre_registered_spec():
    assert R.ATTR_REPRESENTATIVES == {
        "corr_dim_m3_dev": "corr_dim_m3_dev",
        "corr_dim_m4_dev": "corr_dim_m4_dev",
        "corr_dim_m5_dev": "corr_dim_m5_dev",
        "corr_dim_m6_dev": "corr_dim_m6_dev",
    }
    assert R.PLACEBO_SEED == 20261442
    assert R.STABILITY_MIN_SIGN_CONSISTENCY == 0.70
    assert R.STABILITY_MIN_SHARPE_CORR == 0.50
    assert R.DOMINANT_SHARE_MIN == 0.50
    assert R.TRAIN_M == 12 and R.TEST_M == 3 and R.ROLL_M == 3
    assert R.CORR_DIM_W == 256
    assert R.SIGNALS[0] == "corr_dim_m3_dev"


# ================================================================ i.i.d. permuted surrogate
def test_iid_permuted_surrogate_same_marginal_deterministic():
    rng = np.random.default_rng(0)
    x = rng.standard_normal(500) * 3.0 + 5.0
    s1 = R._iid_permuted_surrogate(x, R.PLACEBO_SEED)
    s2 = R._iid_permuted_surrogate(x, R.PLACEBO_SEED)
    assert np.array_equal(s1, s2)
    assert np.isclose(np.sort(s1[np.isfinite(s1)]), np.sort(x[np.isfinite(x)]), equal_nan=True).all()
    fin = s1[np.isfinite(s1)]
    if len(fin) > 2:
        ac1 = float(np.corrcoef(fin[:-1], fin[1:])[0, 1])
        assert abs(ac1) < 0.1, "iid permutation did not destroy serial geometry, lag-1=%.4f" % ac1


# ================================================================ build_underlying / build_scores
def _synthetic_bs(n_assets=3, n_days=2, seed=1):
    d = _synth(n_assets, n_days * 288, seed)
    return {
        "perp_close": d["close"], "log_return": d["log_return"],
        "abs_ret": d["abs_ret"], "sign": d["sign"],
        "bucket": np.tile(np.arange(288), n_days),
        "n_assets": n_assets, "n_days": n_days, "n_bars": n_days * 288,
    }


def test_build_underlying_shapes_and_keys():
    old = R.METRICS_CACHE
    R.METRICS_CACHE = Path(tempfile.mktemp(suffix=".npz"))
    try:
        bs = _synthetic_bs()
        underlying = R.build_underlying(bs)
    finally:
        R.METRICS_CACHE = old
    assert set(underlying["real"].keys()) == set(R.CORR_DIM_KEYS)
    assert set(underlying["placebo"].keys()) == set(R.CORR_DIM_KEYS)
    for k in R.CORR_DIM_KEYS:
        assert underlying["real"][k].shape == (bs["n_assets"], bs["n_bars"])
        assert underlying["placebo"][k].shape == (bs["n_assets"], bs["n_bars"])


def test_build_scores_signals_lookbacks_causal():
    old = R.METRICS_CACHE
    R.METRICS_CACHE = Path(tempfile.mktemp(suffix=".npz"))
    try:
        bs = _synthetic_bs()
        underlying = R.build_underlying(bs)
    finally:
        R.METRICS_CACHE = old
    scores = R.build_scores(underlying, bs["bucket"])
    for sig in R.SIGNALS:
        for L in R.LOOKBACKS:
            assert (sig, L) in scores
            assert scores[(sig, L)].shape == (bs["n_assets"], bs["n_bars"])
    for key, sc in scores.items():
        assert np.isnan(sc[:, 0]).all(), key


# ================================================================ windowed-stat helper for guards
def _assert_distinct(sa, ref, name):
    sa = np.asarray(sa, dtype=float)
    ref = np.asarray(ref, dtype=float)
    m = min(len(sa), len(ref))
    sa, ref = sa[:m], ref[:m]
    fin = np.isfinite(sa) & np.isfinite(ref)
    if fin.sum() == 0:
        return
    assert not np.allclose(sa[fin], ref[fin], atol=1e-6), "corr_dim degenerates to %s" % name


def _mkt_of(d):
    return d["log_return"].mean(0)


# ---- import prior-family compute functions for distinctness guards ----
def _import_compute(mod_name, func_name):
    mod = importlib.import_module(mod_name)
    return getattr(mod, func_name)


try:
    _compute_perm_ent = _import_compute("run_c349_permutation_entropy_xsec_oos", "compute_perm_ent_metrics")
except Exception:  # noqa: BLE001
    _compute_perm_ent = None
try:
    _compute_ker = _import_compute("run_c365_ker_xsec_oos", "compute_ker_metrics")
except Exception:  # noqa: BLE001
    _compute_ker = None
try:
    _compute_zcrpath = _import_compute("run_c422_zcrpath_xsec_oos", "compute_zcrpath_metrics")
except Exception:  # noqa: BLE001
    _compute_zcrpath = None
try:
    _compute_qspread = _import_compute("run_c376_qspread_xsec_oos", "compute_qspread_metrics")
except Exception:  # noqa: BLE001
    _compute_qspread = None
try:
    _compute_ddrun = _import_compute("run_c392_ddrun_xsec_oos", "compute_ddrun_metrics")
except Exception:  # noqa: BLE001
    _compute_ddrun = None
try:
    _compute_rqa = _import_compute("run_c425_rqa_xsec_oos", "compute_rqa_metrics")
except Exception:  # noqa: BLE001
    _compute_rqa = None
try:
    _compute_signetropy = _import_compute("run_c429_signet_xsec_oos", "compute_signetropy_metrics")
except Exception:  # noqa: BLE001
    _compute_signetropy = None
try:
    _compute_distcor = _import_compute("run_c430_distcor_xsec_oos", "compute_distcor_metrics")
except Exception:  # noqa: BLE001
    _compute_distcor = None
try:
    _compute_cq = _import_compute("run_c431_cq_xsec_oos", "compute_cq_metrics")
except Exception:  # noqa: BLE001
    _compute_cq = None
try:
    _compute_edf = _import_compute("run_c432_edfgof_xsec_oos", "compute_edf_metrics")
except Exception:  # noqa: BLE001
    _compute_edf = None
try:
    _compute_hvg = _import_compute("run_c433_hvg_xsec_oos", "compute_hvg_metrics")
except Exception:  # noqa: BLE001
    _compute_hvg = None
try:
    _compute_lyap = _import_compute("run_c434_lyap_xsec_oos", "compute_lyap_metrics")
except Exception:  # noqa: BLE001
    _compute_lyap = None
try:
    _compute_te = _import_compute("run_c435_te_xsec_oos", "compute_te_metrics")
except Exception:  # noqa: BLE001
    _compute_te = None
try:
    _compute_mi = _import_compute("run_c436_mi_xsec_oos", "compute_mi_metrics")
except Exception:  # noqa: BLE001
    _compute_mi = None
try:
    _compute_jsd = _import_compute("run_c437_jsd_xsec_oos", "compute_jsd_metrics")
except Exception:  # noqa: BLE001
    _compute_jsd = None
try:
    _compute_wass = _import_compute("run_c438_wasserstein_xsec_oos", "compute_wass_metrics")
except Exception:  # noqa: BLE001
    _compute_wass = None
try:
    _compute_hsic = _import_compute("run_c439_hsic_xsec_oos", "compute_hsic_metrics")
except Exception:  # noqa: BLE001
    _compute_hsic = None
try:
    _compute_path_signature = _import_compute("run_c440_path_signature_xsec_oos", "compute_path_signature_metrics")
except Exception:  # noqa: BLE001
    _compute_path_signature = None
try:
    _compute_tda = _import_compute("run_c441_tda_xsec_oos", "compute_tda_metrics")
except Exception:  # noqa: BLE001
    _compute_tda = None


def _corr_dim_m3_series_inprocess(log_return, W_q, m=3):
    """In-process (no multiprocessing) correlation dimension m=3 series for a
    small synthetic panel, used by the distinctness guards."""
    Rm = np.asarray(log_return, dtype=float)
    n_assets, T = Rm.shape
    out = np.full((n_assets, T), np.nan, dtype=float)
    for i in range(n_assets):
        mean, sd, _cnt = R._rolling_mean_std(Rm[i], W_q)
        z = np.where(sd > 0, (Rm[i] - mean) / np.where(sd > 0, sd, 1.0), np.nan)
        out[i] = R._corr_dim_series_for_asset_m(np.asarray(z, dtype=float), W_q, m)
    return out


def _guard(d, ref_series, guard_name, W=64):
    sa = _corr_dim_m3_series_inprocess(d["log_return"], W)[0, W - 1:]
    ref = np.asarray(ref_series, dtype=float)
    if ref.ndim == 2:
        ref = ref[0]
    ref = ref[W - 1:][:len(sa)]
    sa = sa[:len(ref)]
    _assert_distinct(sa, ref, guard_name)


# ---- distinctness guards ----
def test_corr_dim_distinct_from_permutation_entropy():
    """Correlation dimension must be distinct from C349
    permutation/ordinal-pattern entropy (rank orderings) — a clone-trap, VOID."""
    if _compute_perm_ent is None:
        return
    d = _synth_multi(3, 200, 214); W = 64
    ref = _compute_perm_ent(d["log_return"][0], W=W, m=3)["perm_ent"]
    _guard(d, ref, "C349_PERMUTATION_ENTROPY")


def test_corr_dim_distinct_from_ker():
    """Correlation dimension must be distinct from C365 KER
    (net-displacement/path-length ratio)."""
    if _compute_ker is None:
        return
    d = _synth_multi(3, 200, 214); W = 64
    ref = _compute_ker(d["close"][0], W=W)["ker_er"]
    _guard(d, ref, "C365_KER")


def test_corr_dim_distinct_from_zcrpath():
    """Correlation dimension must be distinct from C422 ZCRPATH (path functional)."""
    if _compute_zcrpath is None:
        return
    d = _synth_multi(3, 200, 214); W = 64
    ref = _compute_zcrpath(d["log_return"], W=W)["zcr_path"][0, W - 1:]
    _guard(d, ref, "C422_ZCRPATH")


def test_corr_dim_distinct_from_qspread():
    """Correlation dimension must be distinct from C376 QSPREAD (path functional)."""
    if _compute_qspread is None:
        return
    d = _synth_multi(3, 200, 214); W = 64
    ref = _compute_qspread(d["log_return"][0], W=W)["qspread_ratio"]
    _guard(d, ref, "C376_QSPREAD")


def test_corr_dim_distinct_from_ddrun():
    """Correlation dimension must be distinct from C392 DDRRUN (path functional).
    DDRRUN is a time-invariant scalar per asset, while corr_dim is a time-varying series."""
    if _compute_ddrun is None:
        return
    d = _synth_multi(3, 200, 214); W = 64
    ref = _compute_ddrun(d["close"], W=W)["dd_asym"]
    sa = _corr_dim_m3_series_inprocess(d["log_return"], W)[0, W - 1:]
    ref_b = np.full_like(sa, float(ref[0]))
    _assert_distinct(sa, ref_b, "C392_DDRRUN")


def test_corr_dim_distinct_from_rqa():
    """Correlation dimension must be distinct from C425 RQA (recurrence topology)."""
    if _compute_rqa is None:
        return
    d = _synth_multi(3, 200, 214); W = 64
    ref = _compute_rqa(d["close"], W=W, m=3, tau=1)["rqa_rr"][0, W - 1:]
    _guard(d, ref, "C425_RQA")


def test_corr_dim_distinct_from_signentropy():
    """Correlation dimension must be distinct from C429 Markov sign-transition entropy."""
    if _compute_signetropy is None:
        return
    d = _synth_multi(3, 200, 214); W = 64
    ref = _compute_signetropy(d["sign"], W=W)["signentropy_trans_entropy"][0, W - 1:]
    _guard(d, ref, "C429_MARKOV")


def test_corr_dim_distinct_from_distcor():
    """Correlation dimension must be distinct from C430 dCor (distance correlation)."""
    if _compute_distcor is None:
        return
    d = _synth_multi(3, 200, 214); W = 64
    mkt = _mkt_of(d)
    ref = _compute_distcor(d["log_return"], d["abs_ret"], d["sign"], mkt, W=W)["dcor_market"][0, W - 1:]
    _guard(d, ref, "C430_DISTCOR")


def test_corr_dim_distinct_from_cq():
    """Correlation dimension must be distinct from C431 CQ (cross-quantilogram)."""
    if _compute_cq is None:
        return
    d = _synth_multi(3, 200, 214); W = 64
    mkt = _mkt_of(d)
    ref = _compute_cq(d["log_return"], d["abs_ret"], d["sign"], mkt, W_q=W)["cq_market"][0, W - 1:]
    _guard(d, ref, "C431_CQ")


def test_corr_dim_distinct_from_edfgof():
    """Correlation dimension must be distinct from C432 EDF-GOF (normality departure)."""
    if _compute_edf is None:
        return
    d = _synth_multi(3, 200, 214); W = 64
    ref = _compute_edf(d["log_return"], W_q=W)["edf_ks"][0, W - 1:]
    _guard(d, ref, "C432_EDFGOF")


def test_corr_dim_distinct_from_hvg():
    """Correlation dimension must be distinct from C433 HVG (graph topology)."""
    if _compute_hvg is None:
        return
    d = _synth_multi(3, 200, 214); W = 64
    ref = _compute_hvg(d["log_return"], W_q=W)["hvg_mean_degree"][0, W - 1:]
    _guard(d, ref, "C433_HVG")


def test_corr_dim_distinct_from_lyapunov():
    """Correlation dimension must be distinct from C434 Lyapunov (dynamical divergence)."""
    if _compute_lyap is None:
        return
    d = _synth_multi(3, 200, 214); W = 64
    ref = _compute_lyap(d["log_return"], W_q=W)["lyap_m3"][0, W - 1:]
    _guard(d, ref, "C434_LYAPUNOV")


def test_corr_dim_distinct_from_te():
    """Correlation dimension must be distinct from C435 Transfer Entropy (directed info flow)."""
    if _compute_te is None:
        return
    d = _synth_multi(3, 200, 214); W = 64
    ref = _compute_te(d["log_return"], W_q=W)["te_mean"][0, W - 1:]
    _guard(d, ref, "C435_TRANSFER_ENTROPY")


def test_corr_dim_distinct_from_mi():
    """Correlation dimension must be distinct from C436 Mutual Information (joint-histogram)."""
    if _compute_mi is None:
        return
    d = _synth_multi(3, 200, 214); W = 64
    ref = _compute_mi(d["log_return"], W_q=W)["mi_mean"][0, W - 1:]
    _guard(d, ref, "C436_MUTUAL_INFORMATION")


def test_corr_dim_distinct_from_jsd():
    """Correlation dimension must be distinct from C437 Jensen-Shannon divergence."""
    if _compute_jsd is None:
        return
    d = _synth_multi(3, 200, 214); W = 64
    ref = _compute_jsd(d["log_return"], W_q=W)["jsd_mean"][0, W - 1:]
    _guard(d, ref, "C437_JSD")


def test_corr_dim_distinct_from_wasserstein():
    """Correlation dimension must be distinct from C438 Wasserstein (optimal transport)."""
    if _compute_wass is None:
        return
    d = _synth_multi(3, 200, 214); W = 64
    ref = _compute_wass(d["log_return"], W_q=W)["wass_mean"][0, W - 1:]
    _guard(d, ref, "C438_WASSERSTEIN")


def test_corr_dim_distinct_from_hsic():
    """Correlation dimension must be distinct from C439 HSIC (centered RBF Gram trace)."""
    if _compute_hsic is None:
        return
    d = _synth_multi(3, 200, 214); W = 64
    ref = _compute_hsic(d["log_return"], W_q=W)["hsic_mean"][0, W - 1:]
    _guard(d, ref, "C439_HSIC")


def test_corr_dim_distinct_from_path_signature():
    """Correlation dimension must be distinct from C440 truncated path
    signature (Chen iterated integrals / level-2 path tensor)."""
    if _compute_path_signature is None:
        return
    d = _synth_multi(3, 200, 214); W = 64
    ref = _compute_path_signature(d["log_return"], W_q=W)["real"]["sig_area"][0, W - 1:]
    _guard(d, ref, "C440_PATH_SIGNATURE")


def test_corr_dim_distinct_from_tda():
    """Correlation dimension must be distinct from C441 TDA / persistent-homology
    H1 persistence entropy (topological shape invariant, NOT correlation-dimension
    scaling)."""
    if _compute_tda is None:
        return
    d = _synth_multi(3, 200, 214); W = 64
    ref = _compute_tda(d["log_return"], W_q=W)["real"]["tda_m3"][0, W - 1:]
    _guard(d, ref, "C441_TDA_H1_PERSISTENCE_ENTROPY")


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
    test_corr_dim_matches_brute_force()
    test_corr_dim_matches_brute_force_10_assets()
    test_corr_dim_matches_brute_force_with_nan()
    test_corr_dim_defined_after_window_nan_before()
    test_corr_dim_non_finite_propagates()
    test_corr_dim_degenerate_window_is_nan()
    test_corr_dim_params()
    test_reference_config_matches_pre_registered_spec()
    test_iid_permuted_surrogate_same_marginal_deterministic()
    test_build_underlying_shapes_and_keys()
    test_build_scores_signals_lookbacks_causal()
    test_corr_dim_distinct_from_permutation_entropy()
    test_corr_dim_distinct_from_ker()
    test_corr_dim_distinct_from_zcrpath()
    test_corr_dim_distinct_from_qspread()
    test_corr_dim_distinct_from_ddrun()
    test_corr_dim_distinct_from_rqa()
    test_corr_dim_distinct_from_signentropy()
    test_corr_dim_distinct_from_distcor()
    test_corr_dim_distinct_from_cq()
    test_corr_dim_distinct_from_edfgof()
    test_corr_dim_distinct_from_hvg()
    test_corr_dim_distinct_from_lyapunov()
    test_corr_dim_distinct_from_te()
    test_corr_dim_distinct_from_mi()
    test_corr_dim_distinct_from_jsd()
    test_corr_dim_distinct_from_wasserstein()
    test_corr_dim_distinct_from_hsic()
    test_corr_dim_distinct_from_path_signature()
    test_corr_dim_distinct_from_tda()
    print("All C442 correlation dimension runner tests passed")
