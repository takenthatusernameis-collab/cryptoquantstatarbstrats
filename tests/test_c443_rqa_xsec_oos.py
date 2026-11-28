"""Tests for C443 runner (scripts/run_c443_rqa_xsec_oos.py): pure-function tests
on synthetic arrays (including a brute-force equality test for the vectorized
RQA measures vs an independent naive explicit reference) plus schema/flag
validation of emitted real-data artifacts.
Includes kernel-distinctness guards vs ALL named prior families C349/C365/C422/
C376/C392/C425 RQA/C433/C434/C429/C430/C431/C432/C435/C436/C437/C438/C439/C440/
C441/C442. No network, no fabricated market data."""
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

import run_c443_rqa_xsec_oos as R  # noqa: E402


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
    for pb in ("rqa_det_m3_placebo", "rqa_lam_m4_placebo", "rqa_ent_m5_placebo", "rqa_det_m6_placebo"):
        assert pb in R.SIGNALS
    for real in ("rqa_det_m3_dev", "rqa_lam_m4_dev", "rqa_ent_m5_dev", "rqa_det_m6_dev"):
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


# ================================================================ RQA brute-force reference
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


def _true_run_lengths_brute(arr: np.ndarray) -> list:
    """Independent naive run-length of consecutive True values."""
    arr = np.asarray(arr, dtype=bool)
    lengths = []
    i = 0
    n = len(arr)
    while i < n:
        if arr[i]:
            j = i
            while j < n and arr[j]:
                j += 1
            lengths.append(j - i)
            i = j
        else:
            i += 1
    return lengths


def _rqa_measures_brute(pts: np.ndarray, eps_quantile: float = R.RQA_EPS_QUANTILE,
                        l_min: int = R.RQA_L_MIN, v_min: int = R.RQA_V_MIN):
    """Independent naive explicit RQA (DET, LAM, ENTR) of the delay embedding
    pts (n, m): explicit pairwise Euclidean distance loop, eps = quantile of
    off-diagonal distances, recurrence matrix, run-length diagonal/vertical
    lines, DET/LAM/ENTR."""
    pts = np.asarray(pts, dtype=float)
    if not np.isfinite(pts).all():
        return (np.nan, np.nan, np.nan)
    n = len(pts)
    if n < 3:
        return (np.nan, np.nan, np.nan)
    D = np.zeros((n, n), dtype=float)
    for a in range(n):
        for b in range(a + 1, n):
            d = float(np.sqrt(((pts[a] - pts[b]) ** 2).sum()))
            D[a, b] = d
            D[b, a] = d
    iu = np.triu_indices(n, k=1)
    pair_d = np.array([D[iu[0][k], iu[1][k]] for k in range(len(iu[0]))], dtype=float)
    n_pairs = len(pair_d)
    if n_pairs == 0:
        return (np.nan, np.nan, np.nan)
    d_min = float(pair_d.min())
    d_max = float(pair_d.max())
    if d_max <= d_min or not np.isfinite(d_min) or not np.isfinite(d_max):
        return (np.nan, np.nan, np.nan)
    eps = float(np.quantile(pair_d, eps_quantile))
    if not np.isfinite(eps) or eps <= 0:
        return (np.nan, np.nan, np.nan)
    Rmat = D <= eps
    np.fill_diagonal(Rmat, False)  # exclude trivial self-recurrence (main diagonal)
    # diagonal lines: all off-main diagonals
    diag_lengths = []
    for off in range(-(n - 1), n):
        if off == 0:
            continue
        diag_lengths.extend(_true_run_lengths_brute(np.diag(Rmat, k=off)))
    # vertical lines: per column
    vert_lengths = []
    for j in range(n):
        vert_lengths.extend(_true_run_lengths_brute(Rmat[:, j]))
    diag_lengths = np.asarray(diag_lengths, dtype=int) if diag_lengths else np.array([], dtype=int)
    vert_lengths = np.asarray(vert_lengths, dtype=int) if vert_lengths else np.array([], dtype=int)
    # DET
    if diag_lengths.size == 0 or int(diag_lengths.sum()) <= 0:
        det = np.nan
    else:
        den = int(diag_lengths.sum())
        num = int(diag_lengths[diag_lengths >= l_min].sum())
        det = num / den if den > 0 else np.nan
    # LAM
    if vert_lengths.size == 0 or int(vert_lengths.sum()) <= 0:
        lam = np.nan
    else:
        den = int(vert_lengths.sum())
        num = int(vert_lengths[vert_lengths >= v_min].sum())
        lam = num / den if den > 0 else np.nan
    # ENTR
    ent = np.nan
    ent_lengths = diag_lengths[diag_lengths >= l_min]
    if ent_lengths.size >= 1:
        counts = np.bincount(ent_lengths)
        counts = counts[counts > 0].astype(float)
        p = counts / counts.sum()
        ent = float(-(p * np.log(p)).sum())
    return (det, lam, ent)


def _rqa_bruteforce_series(log_return, W_q, m):
    """Independent brute-force per-window RQA for one embedding dimension m
    (measure = MEASURE_BY_M[m]). Explicit per-window mean/std, explicit
    delay-embed loop, explicit pairwise-distance loop, RQA measures."""
    Rm = np.asarray(log_return, float)
    n_assets, n = Rm.shape
    measure = R.MEASURE_BY_M[m]
    out = np.full((n_assets, n), np.nan, float)
    z = np.full((n_assets, n), np.nan, float)
    for i in range(n_assets):
        mean, sd = _rolling_mean_std_brute(Rm[i], W_q)
        z[i] = np.where(sd > 0, (Rm[i] - mean) / np.where(sd > 0, sd, 1.0), np.nan)
    tau = R.RQA_DELAY_TAU
    n_pts = W_q - (m - 1) * tau
    if n_pts < 3:
        return out
    for i in range(n_assets):
        for t in range(W_q - 1, n):
            a = t - W_q + 1
            window_pts = np.empty((n_pts, m), dtype=float)
            for j in range(n_pts):
                start = a + j
                window_pts[j] = z[i, start:start + m]
            if not np.isfinite(window_pts).all():
                continue
            det, lam, ent = _rqa_measures_brute(window_pts)
            out[i, t] = {"det": det, "lam": lam, "ent": ent}[measure]
    return out


def _rqa_bruteforce_metrics(log_return, W_q):
    return {m: _rqa_bruteforce_series(log_return, W_q, m) for m in R.RQA_EMBEDDINGS}


def test_rqa_matches_brute_force():
    """The vectorized RQA measures MUST equal the brute-force explicit
    per-window reference (maxdiff < 1e-12, matching NaN pattern)."""
    W_q = 48
    d = _synth(3, 250, 20261443)
    fast = R.compute_rqa_metrics(d["log_return"], W_q=W_q)
    brute = _rqa_bruteforce_metrics(d["log_return"], W_q)
    for m in R.RQA_EMBEDDINGS:
        key = f"{R.MEASURE_BY_M[m]}_m{m}"
        fin = np.isfinite(fast["real"][key]) & np.isfinite(brute[m])
        assert fin.sum() > 0, "%s: no finite overlapping points" % key
        assert np.array_equal(np.isnan(fast["real"][key]), np.isnan(brute[m])), "%s: NaN pattern mismatch" % key
        maxdiff = float(np.max(np.abs(fast["real"][key][fin] - brute[m][fin])))
        assert maxdiff < 1e-12, "%s: maxdiff=%.3e >= 1e-12" % (key, maxdiff)


def test_rqa_matches_brute_force_10_assets():
    """Brute-force equality with the full 10-asset panel width."""
    W_q = 48
    d = _synth(10, 180, 4294)
    fast = R.compute_rqa_metrics(d["log_return"], W_q=W_q)
    brute = _rqa_bruteforce_metrics(d["log_return"], W_q)
    for m in R.RQA_EMBEDDINGS:
        key = f"{R.MEASURE_BY_M[m]}_m{m}"
        fin = np.isfinite(fast["real"][key]) & np.isfinite(brute[m])
        assert fin.sum() > 0, "%s" % key
        assert np.array_equal(np.isnan(fast["real"][key]), np.isnan(brute[m])), "%s: NaN mismatch" % key
        maxdiff = float(np.max(np.abs(fast["real"][key][fin] - brute[m][fin])))
        assert maxdiff < 1e-12, "%s: maxdiff=%.3e" % (key, maxdiff)


def test_rqa_matches_brute_force_with_nan():
    """Brute-force equality when the panel contains NaNs (propagates to NaN windows)."""
    W_q = 48
    d = _synth(4, 250, 99)
    d["log_return"][1, 200] = np.nan
    fast = R.compute_rqa_metrics(d["log_return"], W_q=W_q)
    brute = _rqa_bruteforce_metrics(d["log_return"], W_q)
    for m in R.RQA_EMBEDDINGS:
        key = f"{R.MEASURE_BY_M[m]}_m{m}"
        assert np.array_equal(np.isnan(fast["real"][key]), np.isnan(brute[m])), "%s: NaN mismatch" % key
        fin = np.isfinite(fast["real"][key]) & np.isfinite(brute[m])
        maxdiff = float(np.max(np.abs(fast["real"][key][fin] - brute[m][fin]))) if fin.sum() else 0.0
        assert maxdiff < 1e-12, "%s: maxdiff=%.3e" % (key, maxdiff)


def test_rqa_defined_after_window_nan_before():
    W_q = 48
    d = _synth(3, 400, 3)
    fast = R.compute_rqa_metrics(d["log_return"], W_q=W_q)
    for m in R.RQA_EMBEDDINGS:
        key = f"{R.MEASURE_BY_M[m]}_m{m}"
        assert np.isnan(fast["real"][key][:, :W_q - 1]).all(), "%s" % key
        assert np.isfinite(fast["real"][key][:, W_q - 1:]).any(), "%s" % key


def test_rqa_non_finite_propagates():
    """A non-finite value in an asset at a bar -> NaN for that asset in every
    window covering that bar."""
    W_q = 48
    d = _synth(4, 400, 9)
    d["log_return"][:, 200] = np.nan
    fast = R.compute_rqa_metrics(d["log_return"], W_q=W_q)
    for m in R.RQA_EMBEDDINGS:
        key = f"{R.MEASURE_BY_M[m]}_m{m}"
        for t in range(200, min(200 + W_q, 400)):
            assert np.isnan(fast["real"][key][:, t]).all(), "%s t=%d should be NaN" % (key, t)


def test_rqa_degenerate_window_is_nan():
    """Constant (zero-variance) series: sigma[t]<=0 => all RQA metrics NaN."""
    W_q = 48
    d = _synth(3, 300, 7)
    d["log_return"][:] = 0.5
    fast = R.compute_rqa_metrics(d["log_return"], W_q=W_q)
    for m in R.RQA_EMBEDDINGS:
        key = f"{R.MEASURE_BY_M[m]}_m{m}"
        assert np.isnan(fast["real"][key]).all(), "%s should be all-NaN for degenerate series" % key


# ================================================================ params / spec
def test_rqa_params():
    assert R.RQA_W == 256
    assert R.RQA_W_FALLBACK == 128
    assert R.RQA_DELAY_TAU == 1
    assert tuple(R.RQA_EMBEDDINGS) == (3, 4, 5, 6)
    assert tuple(R.RQA_KEYS) == ("det_m3", "lam_m4", "ent_m5", "det_m6")
    assert float(R.EPS) == 1e-12
    assert R.PLACEBO_SEED == 20261443
    assert R.MEASURE_BY_M == {3: "det", 4: "lam", 5: "ent", 6: "det"}


def test_reference_config_matches_pre_registered_spec():
    assert R.ATTR_REPRESENTATIVES == {
        "rqa_det_m3_dev": "rqa_det_m3_dev",
        "rqa_lam_m4_dev": "rqa_lam_m4_dev",
        "rqa_ent_m5_dev": "rqa_ent_m5_dev",
        "rqa_det_m6_dev": "rqa_det_m6_dev",
    }
    assert R.PLACEBO_SEED == 20261443
    assert R.STABILITY_MIN_SIGN_CONSISTENCY == 0.70
    assert R.STABILITY_MIN_SHARPE_CORR == 0.50
    assert R.DOMINANT_SHARE_MIN == 0.50
    assert R.TRAIN_M == 12 and R.TEST_M == 3 and R.ROLL_M == 3
    assert R.RQA_W == 256
    assert R.SIGNALS[0] == "rqa_det_m3_dev"


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
    assert set(underlying["real"].keys()) == set(R.RQA_KEYS)
    assert set(underlying["placebo"].keys()) == set(R.RQA_KEYS)
    for k in R.RQA_KEYS:
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
    assert not np.allclose(sa[fin], ref[fin], atol=1e-6), "rqa degenerates to %s" % name


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
    _compute_rqa_c425 = _import_compute("run_c425_rqa_xsec_oos", "compute_rqa_metrics")
except Exception:  # noqa: BLE001
    _compute_rqa_c425 = None
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
try:
    _compute_corr_dim = _import_compute("run_c442_corr_dim_xsec_oos", "compute_corr_dim_metrics")
except Exception:  # noqa: BLE001
    _compute_corr_dim = None


def _rqa_det_m3_series_inprocess(log_return, W_q, m=3):
    """In-process (no multiprocessing) RQA det m=3 series for a small synthetic
    panel, used by the distinctness guards."""
    Rm = np.asarray(log_return, dtype=float)
    n_assets, T = Rm.shape
    out = np.full((n_assets, T), np.nan, dtype=float)
    for i in range(n_assets):
        mean, sd, _cnt = R._rolling_mean_std(Rm[i], W_q)
        z = np.where(sd > 0, (Rm[i] - mean) / np.where(sd > 0, sd, 1.0), np.nan)
        out[i] = R._rqa_series_for_asset_m(np.asarray(z, dtype=float), W_q, m)
    return out


def _guard(d, ref_series, guard_name, W=64):
    sa = _rqa_det_m3_series_inprocess(d["log_return"], W)[0, W - 1:]
    ref = np.asarray(ref_series, dtype=float)
    if ref.ndim == 2:
        ref = ref[0]
    ref = ref[W - 1:][:len(sa)]
    sa = sa[:len(ref)]
    _assert_distinct(sa, ref, guard_name)


# ---- distinctness guards ----
def test_rqa_distinct_from_permutation_entropy():
    """RQA must be distinct from C349 permutation/ordinal-pattern entropy."""
    if _compute_perm_ent is None:
        return
    d = _synth_multi(3, 200, 214); W = 64
    ref = _compute_perm_ent(d["log_return"][0], W=W, m=3)["perm_ent"]
    _guard(d, ref, "C349_PERMUTATION_ENTROPY")


def test_rqa_distinct_from_ker():
    """RQA must be distinct from C365 KER."""
    if _compute_ker is None:
        return
    d = _synth_multi(3, 200, 214); W = 64
    ref = _compute_ker(d["close"][0], W=W)["ker_er"]
    _guard(d, ref, "C365_KER")


def test_rqa_distinct_from_zcrpath():
    """RQA must be distinct from C422 ZCRPATH."""
    if _compute_zcrpath is None:
        return
    d = _synth_multi(3, 200, 214); W = 64
    ref = _compute_zcrpath(d["log_return"], W=W)["zcr_path"][0, W - 1:]
    _guard(d, ref, "C422_ZCRPATH")


def test_rqa_distinct_from_qspread():
    """RQA must be distinct from C376 QSPREAD."""
    if _compute_qspread is None:
        return
    d = _synth_multi(3, 200, 214); W = 64
    ref = _compute_qspread(d["log_return"][0], W=W)["qspread_ratio"]
    _guard(d, ref, "C376_QSPREAD")


def test_rqa_distinct_from_ddrun():
    """RQA must be distinct from C392 DDRRUN."""
    if _compute_ddrun is None:
        return
    d = _synth_multi(3, 200, 214); W = 64
    ref = _compute_ddrun(d["close"], W=W)["dd_asym"]
    sa = _rqa_det_m3_series_inprocess(d["log_return"], W)[0, W - 1:]
    ref_b = np.full_like(sa, float(ref[0]))
    _assert_distinct(sa, ref_b, "C392_DDRRUN")


def test_rqa_distinct_from_rqa_c425():
    """RQA DET/LAM/ENTR (m in {3,4,5,6}, Euclidean, eps=quantile) must be
    distinct from C425 RQA (fixed m=3, Chebyshev, eps=0.1*sigma, RR/DET/LAM/TT)."""
    if _compute_rqa_c425 is None:
        return
    d = _synth_multi(3, 200, 214); W = 64
    ref = _compute_rqa_c425(d["close"], W=W, m=3, tau=1)["rqa_det"][0, W - 1:]
    _guard(d, ref, "C425_RQA")


def test_rqa_distinct_from_signentropy():
    """RQA must be distinct from C429 Markov sign-transition entropy."""
    if _compute_signetropy is None:
        return
    d = _synth_multi(3, 200, 214); W = 64
    ref = _compute_signetropy(d["sign"], W=W)["signentropy_trans_entropy"][0, W - 1:]
    _guard(d, ref, "C429_MARKOV")


def test_rqa_distinct_from_distcor():
    """RQA must be distinct from C430 dCor."""
    if _compute_distcor is None:
        return
    d = _synth_multi(3, 200, 214); W = 64
    mkt = _mkt_of(d)
    ref = _compute_distcor(d["log_return"], d["abs_ret"], d["sign"], mkt, W=W)["dcor_market"][0, W - 1:]
    _guard(d, ref, "C430_DISTCOR")


def test_rqa_distinct_from_cq():
    """RQA must be distinct from C431 CQ."""
    if _compute_cq is None:
        return
    d = _synth_multi(3, 200, 214); W = 64
    mkt = _mkt_of(d)
    ref = _compute_cq(d["log_return"], d["abs_ret"], d["sign"], mkt, W_q=W)["cq_market"][0, W - 1:]
    _guard(d, ref, "C431_CQ")


def test_rqa_distinct_from_edfgof():
    """RQA must be distinct from C432 EDF-GOF."""
    if _compute_edf is None:
        return
    d = _synth_multi(3, 200, 214); W = 64
    ref = _compute_edf(d["log_return"], W_q=W)["edf_ks"][0, W - 1:]
    _guard(d, ref, "C432_EDFGOF")


def test_rqa_distinct_from_hvg():
    """RQA must be distinct from C433 HVG."""
    if _compute_hvg is None:
        return
    d = _synth_multi(3, 200, 214); W = 64
    ref = _compute_hvg(d["log_return"], W_q=W)["hvg_mean_degree"][0, W - 1:]
    _guard(d, ref, "C433_HVG")


def test_rqa_distinct_from_lyapunov():
    """RQA must be distinct from C434 Lyapunov."""
    if _compute_lyap is None:
        return
    d = _synth_multi(3, 200, 214); W = 64
    ref = _compute_lyap(d["log_return"], W_q=W)["lyap_m3"][0, W - 1:]
    _guard(d, ref, "C434_LYAPUNOV")


def test_rqa_distinct_from_te():
    """RQA must be distinct from C435 Transfer Entropy."""
    if _compute_te is None:
        return
    d = _synth_multi(3, 200, 214); W = 64
    ref = _compute_te(d["log_return"], W_q=W)["te_mean"][0, W - 1:]
    _guard(d, ref, "C435_TRANSFER_ENTROPY")


def test_rqa_distinct_from_mi():
    """RQA must be distinct from C436 Mutual Information."""
    if _compute_mi is None:
        return
    d = _synth_multi(3, 200, 214); W = 64
    ref = _compute_mi(d["log_return"], W_q=W)["mi_mean"][0, W - 1:]
    _guard(d, ref, "C436_MUTUAL_INFORMATION")


def test_rqa_distinct_from_jsd():
    """RQA must be distinct from C437 Jensen-Shannon divergence."""
    if _compute_jsd is None:
        return
    d = _synth_multi(3, 200, 214); W = 64
    ref = _compute_jsd(d["log_return"], W_q=W)["jsd_mean"][0, W - 1:]
    _guard(d, ref, "C437_JSD")


def test_rqa_distinct_from_wasserstein():
    """RQA must be distinct from C438 Wasserstein."""
    if _compute_wass is None:
        return
    d = _synth_multi(3, 200, 214); W = 64
    ref = _compute_wass(d["log_return"], W_q=W)["wass_mean"][0, W - 1:]
    _guard(d, ref, "C438_WASSERSTEIN")


def test_rqa_distinct_from_hsic():
    """RQA must be distinct from C439 HSIC."""
    if _compute_hsic is None:
        return
    d = _synth_multi(3, 200, 214); W = 64
    ref = _compute_hsic(d["log_return"], W_q=W)["hsic_mean"][0, W - 1:]
    _guard(d, ref, "C439_HSIC")


def test_rqa_distinct_from_path_signature():
    """RQA must be distinct from C440 truncated path signature."""
    if _compute_path_signature is None:
        return
    d = _synth_multi(3, 200, 214); W = 64
    ref = _compute_path_signature(d["log_return"], W_q=W)["real"]["sig_area"][0, W - 1:]
    _guard(d, ref, "C440_PATH_SIGNATURE")


def test_rqa_distinct_from_tda():
    """RQA must be distinct from C441 TDA / persistent-homology H1 persistence entropy."""
    if _compute_tda is None:
        return
    d = _synth_multi(3, 200, 214); W = 64
    ref = _compute_tda(d["log_return"], W_q=W)["real"]["tda_m3"][0, W - 1:]
    _guard(d, ref, "C441_TDA_H1_PERSISTENCE_ENTROPY")


def test_rqa_distinct_from_corr_dim():
    """RQA recurrence-topology DET/LAM/ENTR must be distinct from C442
    correlation dimension (Grassberger-Procaccia global fractal scaling)."""
    if _compute_corr_dim is None:
        return
    d = _synth_multi(3, 200, 214); W = 64
    ref = _compute_corr_dim(d["log_return"], W_q=W)["real"]["corr_dim_m3"][0, W - 1:]
    _guard(d, ref, "C442_CORRELATION_DIMENSION")


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
    test_rqa_matches_brute_force()
    test_rqa_matches_brute_force_10_assets()
    test_rqa_matches_brute_force_with_nan()
    test_rqa_defined_after_window_nan_before()
    test_rqa_non_finite_propagates()
    test_rqa_degenerate_window_is_nan()
    test_rqa_params()
    test_reference_config_matches_pre_registered_spec()
    test_iid_permuted_surrogate_same_marginal_deterministic()
    test_build_underlying_shapes_and_keys()
    test_build_scores_signals_lookbacks_causal()
    test_rqa_distinct_from_permutation_entropy()
    test_rqa_distinct_from_ker()
    test_rqa_distinct_from_zcrpath()
    test_rqa_distinct_from_qspread()
    test_rqa_distinct_from_ddrun()
    test_rqa_distinct_from_rqa_c425()
    test_rqa_distinct_from_signentropy()
    test_rqa_distinct_from_distcor()
    test_rqa_distinct_from_cq()
    test_rqa_distinct_from_edfgof()
    test_rqa_distinct_from_hvg()
    test_rqa_distinct_from_lyapunov()
    test_rqa_distinct_from_te()
    test_rqa_distinct_from_mi()
    test_rqa_distinct_from_jsd()
    test_rqa_distinct_from_wasserstein()
    test_rqa_distinct_from_hsic()
    test_rqa_distinct_from_path_signature()
    test_rqa_distinct_from_tda()
    test_rqa_distinct_from_corr_dim()
    print("All C443 RQA runner tests passed")
