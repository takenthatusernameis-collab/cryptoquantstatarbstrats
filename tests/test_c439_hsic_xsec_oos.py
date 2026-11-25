"""Tests for C439 runner (scripts/run_c439_hsic_xsec_oos.py): pure-function
tests on synthetic arrays (including a brute-force equality test for the
vectorized HSIC kernel vs an independent naive per-window explicit double-loop
reference) plus schema/flag validation of emitted real-data artifacts.
Includes kernel-distinctness guards vs ALL named prior families C281B-C438.
No network, no fabricated market data."""
from __future__ import annotations

import json
import math
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import run_c439_hsic_xsec_oos as R  # noqa: E402


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
    for pb in ("hsic_mean_placebo", "hsic_max_placebo", "hsic_conc_placebo", "hsic_disp_placebo"):
        assert pb in R.SIGNALS
    for real in ("hsic_mean_dev", "hsic_max_dev", "hsic_conc_dev", "hsic_disp_dev"):
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
    """Multi-distribution panel: different assets drawn from different
    distribution families so cross-asset HSIC is genuinely non-zero after
    per-window standardization."""
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


# ================================================================ HSIC brute-force reference
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


def _hsic_bruteforce_window(x: np.ndarray, y: np.ndarray, gamma: float = R.HSIC_GAMMA) -> float:
    """Naive normalized biased HSIC for one window: RBF kernels
    k(a,b)=exp(-gamma*(a-b)^2), H=I-11^T/W_q, HSIC=(1/(W_q-1)^2)*sum(Kc*Lc)."""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    Wq = len(x)
    if Wq < 2:
        return np.nan
    if not (np.isfinite(x).all() and np.isfinite(y).all()):
        return np.nan
    K = np.exp(-gamma * (x[:, None] - x[None, :]) ** 2)
    L = np.exp(-gamma * (y[:, None] - y[None, :]) ** 2)
    H = np.eye(Wq) - np.ones((Wq, Wq)) / Wq
    Kc = H @ K @ H
    Lc = H @ L @ H
    return float(np.sum(Kc * Lc) / (Wq - 1) ** 2)


def _hsic_bruteforce_series(log_return, W_q, gamma: float = R.HSIC_GAMMA):
    """Independent brute-force per-window HSIC reference: standardize per asset,
    center RBF Grams per window, compute HSIC per unordered pair as centered
    Gram trace, derive per-bar hsic_mean/hsic_max/hsic_conc/hsic_disp. Used only
    for equality testing on small inputs."""
    Rm = np.asarray(log_return, float)
    n_assets, n = Rm.shape
    out = {k: np.full((n_assets, n), np.nan, float) for k in R.HSIC_KEYS}

    # Standardize each asset (brute-force rolling mean/std)
    z = np.full((n_assets, n), np.nan, float)
    for i in range(n_assets):
        mean, sd = _rolling_mean_std_brute(Rm[i], W_q)
        z[i] = np.where(sd > 0, (Rm[i] - mean) / np.where(sd > 0, sd, 1.0), np.nan)

    pairs = [(i, j) for i in range(n_assets) for j in range(i + 1, n_assets)]
    n_pairs = len(pairs)

    for t in range(W_q - 1, n):
        window_all = z[:, t - W_q + 1:t + 1]   # (n_assets, W_q)
        if not np.isfinite(window_all).all():
            continue
        h_vals = np.zeros(n_pairs, float)
        for p, (i, j) in enumerate(pairs):
            h_vals[p] = _hsic_bruteforce_window(window_all[i], window_all[j], gamma=gamma)
        hsic_mean = float(np.mean(h_vals))
        hsic_max = float(np.max(h_vals))
        row_sum = float(np.sum(h_vals))
        norm = np.where(row_sum > 0, h_vals / max(row_sum, 1e-300), 0.0)
        hsic_conc = float(np.sum(norm * norm))
        hsic_disp = float(np.std(h_vals))

        for i in range(n_assets):
            out["hsic_mean"][i, t] = hsic_mean
            out["hsic_max"][i, t] = hsic_max
            out["hsic_conc"][i, t] = hsic_conc
            out["hsic_disp"][i, t] = hsic_disp

    return out


def test_hsic_matches_brute_force():
    """The vectorized HSIC kernel MUST equal the brute-force per-window HSIC
    reference (maxdiff < 1e-12, matching NaN)."""
    W_q = 48
    d = _synth(3, 300, 20261303)
    fast = R.compute_hsic_metrics(d["log_return"], W_q=W_q)
    brute = _hsic_bruteforce_series(d["log_return"], W_q)
    for k in R.HSIC_KEYS:
        fin = np.isfinite(fast[k]) & np.isfinite(brute[k])
        assert fin.sum() > 0, f"{k}: no finite overlapping points"
        assert np.array_equal(np.isnan(fast[k]), np.isnan(brute[k])), f"{k}: NaN pattern mismatch"
        maxdiff = float(np.max(np.abs(fast[k][fin] - brute[k][fin]))) if fin.sum() else 0.0
        assert maxdiff < 1e-12, f"{k}: maxdiff={maxdiff} >= 1e-12"


def test_hsic_matches_brute_force_10_assets():
    """Brute-force equality with the full 10-asset panel (the real universe width)."""
    W_q = 48
    d = _synth(10, 250, 4294)
    fast = R.compute_hsic_metrics(d["log_return"], W_q=W_q)
    brute = _hsic_bruteforce_series(d["log_return"], W_q)
    for k in R.HSIC_KEYS:
        fin = np.isfinite(fast[k]) & np.isfinite(brute[k])
        assert fin.sum() > 0, f"{k}"
        assert np.array_equal(np.isnan(fast[k]), np.isnan(brute[k])), f"{k}: NaN mismatch"
        maxdiff = float(np.max(np.abs(fast[k][fin] - brute[k][fin])))
        assert maxdiff < 1e-12, f"{k}: maxdiff={maxdiff} (float64 noise floor)"


def test_hsic_matches_brute_force_with_nan():
    """Brute-force equality when the panel contains NaNs (propagates to NaN windows)."""
    W_q = 48
    d = _synth(4, 300, 99)
    d["log_return"][1, 200] = np.nan
    fast = R.compute_hsic_metrics(d["log_return"], W_q=W_q)
    brute = _hsic_bruteforce_series(d["log_return"], W_q)
    for k in R.HSIC_KEYS:
        assert np.array_equal(np.isnan(fast[k]), np.isnan(brute[k])), f"{k}: NaN mismatch"
        fin = np.isfinite(fast[k]) & np.isfinite(brute[k])
        maxdiff = float(np.max(np.abs(fast[k][fin] - brute[k][fin]))) if fin.sum() else 0.0
        assert maxdiff < 1e-12, f"{k}: maxdiff={maxdiff}"


def test_hsic_defined_after_window_nan_before():
    W_q = 48
    d = _synth(3, 400, 3)
    fast = R.compute_hsic_metrics(d["log_return"], W_q=W_q)
    for k in R.HSIC_KEYS:
        assert np.isnan(fast[k][:, :W_q - 1]).all(), f"{k}"
        assert np.isfinite(fast[k][:, W_q - 1:]).any(), f"{k}"


def test_hsic_non_finite_propagates():
    """A non-finite value in any asset at a bar -> NaN for every HSIC scalar
    in every window covering that bar (global finite gate)."""
    W_q = 48
    d = _synth(4, 400, 9)
    d["log_return"][:, 200] = np.nan
    fast = R.compute_hsic_metrics(d["log_return"], W_q=W_q)
    for k in R.HSIC_KEYS:
        for t in range(200, min(200 + W_q, 400)):
            assert np.isnan(fast[k][:, t]).all(), f"{k} t={t} should be NaN"


def test_hsic_degenerate_window_is_nan():
    """Constant (zero-variance) series: sigma[t]<=0 => HSIC stats NaN."""
    W_q = 48
    d = _synth(3, 300, 7)
    d["log_return"][:] = 0.5
    fast = R.compute_hsic_metrics(d["log_return"], W_q=W_q)
    for k in R.HSIC_KEYS:
        assert np.isnan(fast[k]).all(), f"{k} should be all-NaN for degenerate series"


def test_hsic_params():
    assert R.HSIC_W == 256
    assert R.HSIC_W_FALLBACK == 128
    assert float(R.HSIC_GAMMA) == 0.5
    assert tuple(R.HSIC_KEYS) == ("hsic_mean", "hsic_max", "hsic_conc", "hsic_disp")


# ================================================================ reference-config spec
def test_reference_config_matches_pre_registered_spec():
    assert R.ATTR_REPRESENTATIVES == {
        "hsic_mean_dev": "hsic_mean_dev",
        "hsic_max_dev": "hsic_max_dev",
        "hsic_conc_dev": "hsic_conc_dev",
        "hsic_disp_dev": "hsic_disp_dev",
    }
    assert R.PLACEBO_SEED == 20261303
    assert R.STABILITY_MIN_SIGN_CONSISTENCY == 0.70
    assert R.STABILITY_MIN_SHARPE_CORR == 0.50
    assert R.DOMINANT_SHARE_MIN == 0.50
    assert R.TRAIN_M == 12 and R.TEST_M == 3 and R.ROLL_M == 3
    assert R.HSIC_W == 256
    assert R.SIGNALS[0] == "hsic_mean_dev"


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
        assert abs(ac1) < 0.1, f"iid permutation did not destroy serial geometry, lag-1={ac1}"


# ================================================================ build_underlying / build_scores
def _synthetic_bs(n_assets=3, n_days=8, seed=1):
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
    assert set(underlying["real"].keys()) == set(R.HSIC_KEYS)
    assert set(underlying["placebo"].keys()) == set(R.HSIC_KEYS)
    for k in R.HSIC_KEYS:
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
    assert fin.sum() > 0, name
    assert not np.allclose(sa[fin], ref[fin], atol=1e-6), f"HSIC degenerates to {name}"


def _windowed_stat(series, W, fn):
    """Apply fn(window)->scalar over trailing windows; NaN before W."""
    series = np.asarray(series, float)
    n = len(series)
    out = np.full(n, np.nan, float)
    for t in range(W - 1, n):
        w = series[t - W + 1:t + 1]
        if not np.isfinite(w).all():
            continue
        out[t] = fn(w)
    return out


def _mkt_of(d):
    return d["log_return"].mean(0)


# ---- inline prior-family reference statistics (distinctness guards) ----
def _ref_edfgof(x, W):
    """EDF-GOF Cramer-von Mises (C432) per trailing window vs N(0,1)."""
    from scipy import stats as _st
    def fn(w):
        wd = np.sort(w)
        n = len(wd)
        p = _st.norm.cdf(wd)
        if (p == 0.0).any() or (p == 1.0).any():
            return np.nan
        i = np.arange(1, n + 1, dtype=float)
        theo = (2 * i - 1) / (2 * n)
        cvm = 1.0 / (12 * n) + float(np.sum((p - theo) ** 2))
        return float(cvm)
    return _windowed_stat(x, W, fn)


def _ref_cross_quantilogram(x, y, W):
    """Cross-quantilogram (C431) hit-based correlation per trailing window."""
    n = len(x)
    out = np.full(n, np.nan, float)
    taus = (0.10, 0.25, 0.75, 0.90); lags = (1, 2, 4)
    for t in range(W - 1, n):
        xw = x[t - W + 1:t + 1]
        yw = y[t - W + 1:t + 1]
        vals = []
        for tau in taus:
            qx = float(np.quantile(xw, tau)); qy = float(np.quantile(yw, tau))
            hx = (xw <= qx).astype(float); hy = (yw <= qy).astype(float)
            for k in lags:
                if t - k < W - 1:
                    continue
                vals.append(float(np.mean((hx[k:] - tau) * (hy[:-k] - tau)) / (tau * (1 - tau))))
        if vals:
            out[t] = float(np.mean(vals))
    return out


def _ref_distance_correlation(x, y, W):
    """Distance correlation dCor (C430) per trailing window between x and y."""
    n = len(x)
    out = np.full(n, np.nan, float)
    for t in range(W - 1, n):
        xw = x[t - W + 1:t + 1]
        yw = y[t - W + 1:t + 1]
        if not (np.isfinite(xw).all() and np.isfinite(yw).all()):
            continue
        a = np.abs(xw[:, None] - xw[None, :])
        b = np.abs(yw[:, None] - yw[None, :])
        A = a - a.mean(1, keepdims=True) - a.mean(0, keepdims=True) + a.mean()
        Bm = b - b.mean(1, keepdims=True) - b.mean(0, keepdims=True) + b.mean()
        dcov = (A * Bm).mean()
        vx = (A * A).mean(); vy = (Bm * Bm).mean()
        if not (np.isfinite(dcov) and np.isfinite(vx) and np.isfinite(vy)) or vx <= 0 or vy <= 0:
            continue
        out[t] = float(np.sqrt(np.clip(dcov / math.sqrt(vx * vy), 0.0, 1.0)))
    return out


def _ref_markov_sign_transition(x, W):
    """C429 order-1 Markov sign transition entropy."""
    def fn(w):
        s = np.sign(w)
        curr, nxt = s[:-1], s[1:]
        mask = curr != 0
        curr, nxt = curr[mask], nxt[mask]
        if len(curr) == 0:
            return np.nan
        pp = np.count_nonzero((curr == 1) & (nxt == 1))
        pm = np.count_nonzero((curr == 1) & (nxt == -1))
        mp = np.count_nonzero((curr == -1) & (nxt == 1))
        mm = np.count_nonzero((curr == -1) & (nxt == -1))
        dp, dn = pp + pm, mp + mm
        if dp == 0 or dn == 0:
            return np.nan
        H = 0.0
        for num, den in ((pp, dp), (pm, dp), (mp, dn), (mm, dn)):
            p = num / den
            if p > 0:
                H -= p * np.log(p)
        return float(H)
    return _windowed_stat(x, W, fn)


def _ref_sign_autocorr(x, W):
    """Sign-sequence autocorrelation of own returns."""
    def fn(w):
        s = np.sign(w)
        s = s[s != 0]
        if len(s) < 4:
            return np.nan
        sd = s - s.mean()
        var = np.dot(sd, sd)
        if var <= 0:
            return np.nan
        return float(np.dot(sd[:-1], sd[1:]) / var)
    return _windowed_stat(x, W, fn)


def _ref_sign_count_entropy(x, W):
    """C329 sign-COUNT Shannon entropy."""
    def fn(w):
        pos = np.count_nonzero(w > 0)
        neg = np.count_nonzero(w < 0)
        tot = pos + neg
        if tot == 0:
            return np.nan
        H = 0.0
        for c in (pos, neg):
            p = c / tot
            if p > 0:
                H -= p * np.log(p)
        return float(H)
    return _windowed_stat(x, W, fn)


def _ref_multi_lag_autocov(x, W):
    """Multi-lag realized autocovariance / Pearson autocorrelation."""
    def fn(w):
        wd = w - w.mean()
        var = np.dot(wd, wd)
        if var <= 0:
            return np.nan
        s = 0.0
        for k in (1, 2, 4):
            s += np.dot(wd[:-k], wd[k:]) / var
        return s / 3.0
    return _windowed_stat(x, W, fn)


def _ref_avg_pairwise_corr(x_all, W):
    """Average pairwise cross-correlation profile (C410 XCORR)."""
    n_assets, n = x_all.shape
    out = np.full(n, np.nan, float)
    for t in range(W - 1, n):
        win = x_all[:, t - W + 1:t + 1]
        if not np.isfinite(win).all():
            continue
        wd = win - win.mean(axis=1, keepdims=True)
        var = np.dot(wd, wd.T)
        if np.any(np.diag(var) <= 0):
            continue
        with np.errstate(divide="ignore", invalid="ignore"):
            corr = var / np.sqrt(np.outer(np.diag(var), np.diag(var)))
        iu = np.triu_indices(n_assets, k=1)
        out[t] = float(np.nanmean(corr[iu]))
    return out


def _ref_leadlag(x, mkt, W):
    """Leader-follower regression-coefficient asymmetry vs market."""
    n = len(x)
    out = np.full(n, np.nan, float)
    for t in range(W - 1, n):
        xr = x[t - W + 1:t + 1]
        mr = mkt[t - W + 1:t + 1]
        if not (np.isfinite(xr).all() and np.isfinite(mr).all()):
            continue
        if np.std(mr) <= 0 or np.std(xr) <= 0:
            continue
        b_fwd = np.polyfit(mr[:-1], xr[1:], 1)[0]
        b_bwd = np.polyfit(mr[1:], xr[:-1], 1)[0]
        out[t] = float(b_fwd - b_bwd)
    return out


def _ref_cdom(x_all, W):
    """Cross-sectional extreme-dominance frequency."""
    n_assets, n = x_all.shape
    out = np.full(n, np.nan, float)
    for t in range(W - 1, n):
        win = x_all[:, t - W + 1:t + 1]
        if not np.isfinite(win).all():
            continue
        colmax = np.max(win, axis=0); colmin = np.min(win, axis=0)
        dom = (win == colmax[None, :]) | (win == colmin[None, :])
        out[t] = float(np.mean(dom.any(axis=0)))
    return out


def _ref_xskew3(x, W):
    """Cross third-moment irreversibility."""
    def fn(w):
        d = np.diff(w)
        if len(d) < 3:
            return np.nan
        return float(np.mean(d ** 3))
    return _windowed_stat(x, W, fn)


def _ref_domfreq(x, W):
    """Dominant spectral frequency/centroid."""
    def fn(w):
        wd = w - w.mean()
        if np.std(wd) <= 0:
            return np.nan
        F = np.abs(np.fft.rfft(wd))
        if len(F) <= 1 or F.sum() <= 0:
            return np.nan
        freqs = np.fft.rfftfreq(len(wd), d=1.0)
        return float((freqs * F).sum() / F.sum())
    return _windowed_stat(x, W, fn)


def _ref_specfm(x, W):
    """Spectral flatness/entropy."""
    def fn(w):
        wd = w - w.mean()
        if np.std(wd) <= 0:
            return np.nan
        P = np.abs(np.fft.rfft(wd)) ** 2
        P = P[P > 0]
        if len(P) == 0:
            return np.nan
        gm = np.exp(np.mean(np.log(P)))
        am = np.mean(P)
        return float(gm / am) if am > 0 else np.nan
    return _windowed_stat(x, W, fn)


def _ref_qspread(x, W):
    """Quantile spread: IQR-like quantile dispersion."""
    def fn(w):
        if np.std(w) <= 0:
            return np.nan
        return float(np.quantile(w, 0.75) - np.quantile(w, 0.25))
    return _windowed_stat(x, W, fn)


def _ref_lmom(x, W):
    """L-moment skewness."""
    def fn(w):
        if len(w) < 4 or np.std(w) <= 0:
            return np.nan
        s = np.sort(w)
        n = len(s)
        wts = np.arange(n, dtype=float) / (n - 1)
        l2 = float(np.sum(wts * s) / n - np.mean(s))
        l3 = float(np.sum(((wts ** 2) * s)) / n - 2 * np.mean(s) * np.mean(wts * s) + np.mean(s) ** 2)
        if abs(l2) < 1e-12:
            return np.nan
        return float(l3 / l2)
    return _windowed_stat(x, W, fn)


def _ref_rqa(x, W):
    """Recurrence quantification analysis: recurrence rate."""
    def fn(w):
        if np.std(w) <= 0:
            return np.nan
        yn = (w - w.mean()) / np.std(w)
        emb = np.stack([yn[:-1], yn[1:]], 1)
        r = 0.2
        d = np.sqrt(((emb[:, None, :] - emb[None, :, :]) ** 2).sum(2))
        return float(np.mean(d < r))
    return _windowed_stat(x, W, fn)


def _ref_hvg_mean_degree(x, W):
    """Horizontal Visibility Graph mean degree per trailing window."""
    def fn(w):
        Wn = len(w)
        if Wn < 2:
            return np.nan
        degree = np.zeros(Wn, dtype=np.int64)
        edges = []
        stack = []
        for j in range(Wn):
            zj = w[j]
            while stack and w[stack[-1]] < zj:
                i = stack.pop()
                edges.append((i, j))
            if stack:
                edges.append((stack[-1], j))
            stack.append(j)
        for (a, b) in edges:
            degree[a] += 1; degree[b] += 1
        E = len(edges)
        deg_sum = int(degree.sum())
        return float(deg_sum) / float(Wn)
    return _windowed_stat(x, W, fn)


# C438 Wasserstein reference (sorted-quantile L1 optimal transport) - HSIC must be distinct
def _ref_wasserstein_panel(x_all, W):
    """Cross-asset 1-Wasserstein wass_mean (C438): per trailing window, for each
    unordered pair (i,j), i<j, W1_{i<->j} = mean_k | sort(x_i_window)[k] - sort(x_j_window)[k] |
    (equal-weight empirical samples, sorted-quantile L1 optimal-transport cost),
    return mean W1. Distinct formulation from HSIC (centered RBF Gram trace vs
    sorted-quantile L1 marginal optimal-transport cost)."""
    n_assets, n = x_all.shape
    out = np.full(n, np.nan, float)
    for t in range(W - 1, n):
        win = x_all[:, t - W + 1:t + 1]
        if not np.isfinite(win).all():
            continue
        sorted_win = np.sort(win, axis=1)   # (n_assets, W)
        w1_vals = []
        for i in range(n_assets):
            for j in range(i + 1, n_assets):
                w1_vals.append(float(np.mean(np.abs(sorted_win[i] - sorted_win[j]))))
        out[t] = float(np.mean(w1_vals)) if w1_vals else np.nan
    return out


# C437 Jensen-Shannon reference (symmetric information divergence) - HSIC must be distinct
def _ref_jsd_panel(x_all, W):
    """Cross-asset Jensen-Shannon divergence jsd_mean (C437): per trailing window,
    bin each series into B equal-frequency bins, compute JSD_{i<->j} over unordered
    pairs (i,j), i<j, return mean JSD. Distinct formulation from HSIC (centered RBF
    Gram trace vs marginal-histogram KL divergence)."""
    n_assets, n = x_all.shape
    out = np.full(n, np.nan, float)
    B = 8
    for t in range(W - 1, n):
        win = x_all[:, t - W + 1:t + 1]
        if not np.isfinite(win).all():
            continue
        bins = np.zeros((n_assets, W), dtype=int)
        for a in range(n_assets):
            ranks = np.argsort(np.argsort(win[a], kind="mergesort"), kind="mergesort")
            bins[a] = (ranks * B) // W
        n_float = float(W)
        jsd_vals = []
        for i in range(n_assets):
            for j in range(i + 1, n_assets):
                xb = bins[i]; yb = bins[j]
                x_counts = np.bincount(xb, minlength=B).astype(float)
                y_counts = np.bincount(yb, minlength=B).astype(float)
                p_i = x_counts / n_float
                p_j = y_counts / n_float
                m = 0.5 * (p_i + p_j)
                kl_i = 0.0; kl_j = 0.0
                for b in range(B):
                    if p_i[b] > 0 and m[b] > 0:
                        kl_i += p_i[b] * math.log(p_i[b] / m[b])
                    if p_j[b] > 0 and m[b] > 0:
                        kl_j += p_j[b] * math.log(p_j[b] / m[b])
                jsd_vals.append(0.5 * (kl_i + kl_j))
        out[t] = float(np.mean(jsd_vals)) if jsd_vals else np.nan
    return out


# C436 Mutual Information reference (symmetric joint-histogram dependence) - HSIC must be distinct
def _ref_mi_panel(x_all, W):
    """Cross-asset Mutual Information mi_mean (C436): per trailing window,
    bin each series into B equal-frequency bins, compute MI_{i<->j} over unordered
    pairs (i,j), i<j, return mean MI. Distinct formulation from HSIC (centered RBF
    Gram trace vs joint-histogram mutual information)."""
    n_assets, n = x_all.shape
    out = np.full(n, np.nan, float)
    B = 8
    for t in range(W - 1, n):
        win = x_all[:, t - W + 1:t + 1]
        if not np.isfinite(win).all():
            continue
        bins = np.zeros((n_assets, W), dtype=int)
        for a in range(n_assets):
            ranks = np.argsort(np.argsort(win[a], kind="mergesort"), kind="mergesort")
            bins[a] = (ranks * B) // W
        n_float = float(W)
        mi_vals = []
        for i in range(n_assets):
            for j in range(i + 1, n_assets):
                xb = bins[i]; yb = bins[j]
                joint_idx = xb * B + yb
                joint_counts = np.bincount(joint_idx, minlength=B * B).reshape(B, B).astype(float)
                x_counts = np.bincount(xb, minlength=B).astype(float)
                y_counts = np.bincount(yb, minlength=B).astype(float)
                mi = 0.0
                for x in range(B):
                    for y in range(B):
                        jj = joint_counts[x, y]
                        if jj <= 0:
                            continue
                        xc = x_counts[x]; yc = y_counts[y]
                        if xc <= 0 or yc <= 0:
                            continue
                        mi += (jj / n_float) * math.log2(jj * n_float / (xc * yc))
                mi_vals.append(mi)
        out[t] = float(np.mean(mi_vals)) if mi_vals else np.nan
    return out


# C435 Transfer Entropy reference (directed, ordered pairs) - HSIC must be distinct
def _ref_transfer_entropy_panel(x_all, W):
    """Directed cross-asset Transfer Entropy te_mean (C435): per trailing window,
    bin each series into B equal-frequency bins, compute TE_{i->j} over ordered
    pairs (i,j), i!=j, return mean directed TE. Distinct formulation from HSIC
    (symmetric centered RBF Gram trace vs directed 3D histogram TE)."""
    n_assets, n = x_all.shape
    out = np.full(n, np.nan, float)
    B = 8
    for t in range(W - 1, n):
        win = x_all[:, t - W + 1:t + 1]
        if not np.isfinite(win).all():
            continue
        bins = np.zeros((n_assets, W), dtype=int)
        for a in range(n_assets):
            ranks = np.argsort(np.argsort(win[a], kind="mergesort"), kind="mergesort")
            bins[a] = (ranks * B) // W
        Wm1 = W - 1
        B2 = B * B
        B3 = B * B * B
        y_future = bins[:, 1:]
        te_vals = []
        for i in range(n_assets):
            for j in range(n_assets):
                if i == j:
                    continue
                joint_idx = y_future[j] * B2 + bins[j, :-1] * B + bins[i, :-1]
                joint_counts = np.bincount(joint_idx, minlength=B3).reshape(B, B, B).astype(float)
                yx_idx = bins[j, :-1] * B + bins[i, :-1]
                yx_counts = np.bincount(yx_idx, minlength=B2).reshape(B, B).astype(float)
                yy_idx = y_future[j] * B + bins[j, :-1]
                yy_counts = np.bincount(yy_idx, minlength=B2).reshape(B, B).astype(float)
                y_counts = np.bincount(bins[j, :-1], minlength=B).astype(float)
                n_float = float(Wm1)
                te = 0.0
                for yf in range(B):
                    for yp in range(B):
                        for xp in range(B):
                            jj = joint_counts[yf, yp, xp]
                            if jj <= 0:
                                continue
                            yx = yx_counts[yp, xp]
                            yy = yy_counts[yf, yp]
                            yc = y_counts[yp]
                            if yx <= 0 or yy <= 0 or yc <= 0:
                                continue
                            te += (jj / n_float) * math.log2(jj * yc / (yx * yy))
                te_vals.append(te)
        out[t] = float(np.mean(te_vals)) if te_vals else np.nan
    return out


def _hsic_series_for_guard(d):
    """Compute the 4 HSIC concept series for the first asset (guards compare
    concept[0])."""
    W = 128
    series = R.compute_hsic_metrics(d["log_return"], W_q=W)
    return series, W


def _guard_base():
    return _synth_multi(5, 500, 214)


def _guarded_assert(d, ref_series, concept, guard_name):
    series, W = _hsic_series_for_guard(d)
    sa = series[concept][0, W - 1:]  # first asset's concept series (1-D)
    ref = ref_series[W - 1:]
    _assert_distinct(sa, ref, guard_name)


# ---- distinctness guards ----
def test_hsic_kernel_distinct_from_mutual_information():
    """HSIC (centered RBF Gram trace) must be distinct from C436 Mutual
    Information (symmetric joint-histogram dependence)."""
    d = _guard_base(); W = 128
    ref = _ref_mi_panel(d["log_return"], W)
    sa = R.compute_hsic_metrics(d["log_return"], W_q=W)["hsic_mean"][0, W - 1:]
    _assert_distinct(sa, ref, "C436_MUTUAL_INFORMATION")


def test_hsic_kernel_distinct_from_transfer_entropy():
    """HSIC (symmetric, unordered pairs, centered RBF Gram trace) must be
    distinct from C435 Transfer Entropy (directed, ordered pairs, 3D histogram)."""
    d = _guard_base(); W = 128
    ref = _ref_transfer_entropy_panel(d["log_return"], W)
    sa = R.compute_hsic_metrics(d["log_return"], W_q=W)["hsic_mean"][0, W - 1:]
    _assert_distinct(sa, ref, "C435_TRANSFER_ENTROPY")


def test_hsic_kernel_distinct_from_jsd():
    """HSIC (centered RBF Gram trace) must be distinct from C437 Jensen-Shannon
    information divergence (marginal-histogram KL)."""
    d = _guard_base(); W = 128
    ref = _ref_jsd_panel(d["log_return"], W)
    sa = R.compute_hsic_metrics(d["log_return"], W_q=W)["hsic_mean"][0, W - 1:]
    _assert_distinct(sa, ref, "C437_JSD")


def test_hsic_kernel_distinct_from_wasserstein():
    """HSIC (centered RBF Gram trace kernel dependence) must be distinct from
    C438 Wasserstein (sorted-quantile-L1 optimal-transport marginal distance)."""
    d = _guard_base(); W = 128
    ref = _ref_wasserstein_panel(d["log_return"], W)
    sa = R.compute_hsic_metrics(d["log_return"], W_q=W)["hsic_mean"][0, W - 1:]
    _assert_distinct(sa, ref, "C438_WASSERSTEIN")


def test_hsic_kernel_distinct_from_lyapunov():
    d = _guard_base(); W = 128
    from scripts.run_c434_lyap_xsec_oos import compute_lyap_metrics as _lyap
    series = _lyap(d["log_return"], W_q=W)
    ref = series["lyap_m3"][0, W - 1:]
    sa = R.compute_hsic_metrics(d["log_return"], W_q=W)["hsic_mean"][0, W - 1:]
    _assert_distinct(sa, ref, "C434_LYAPUNOV")


def test_hsic_kernel_distinct_from_edfgof():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_edfgof(d["log_return"][0], W), "hsic_mean", "C432_EDFGOF")


def test_hsic_kernel_distinct_from_cross_quantilogram():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_cross_quantilogram(d["log_return"][0], _mkt_of(d), W),
                    "hsic_mean", "C431_CROSS_QUANTILOGRAM")


def test_hsic_kernel_distinct_from_distance_correlation():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_distance_correlation(d["log_return"][0], _mkt_of(d), W),
                    "hsic_mean", "C430_DISTCOR")


def test_hsic_kernel_distinct_from_hvg():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_hvg_mean_degree(d["log_return"][0], W),
                    "hsic_mean", "C433_HVG")


def test_hsic_kernel_distinct_from_markov_sign_transition():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_markov_sign_transition(d["log_return"][0], W),
                    "hsic_mean", "C429_MARKOV")


def test_hsic_kernel_distinct_from_sign_autocorr():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_sign_autocorr(d["log_return"][0], W),
                    "hsic_mean", "C421_SIGN_AUTOCORR")


def test_hsic_kernel_distinct_from_sign_count_entropy():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_sign_count_entropy(d["log_return"][0], W),
                    "hsic_mean", "C329_SIGN_COUNT_ENTROPY")


def test_hsic_kernel_distinct_from_multi_lag_autocov():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_multi_lag_autocov(d["log_return"][0], W),
                    "hsic_mean", "C375_ACOVK")


def test_hsic_kernel_distinct_from_avg_pairwise_corr():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_avg_pairwise_corr(d["log_return"], W),
                    "hsic_mean", "C410_XCORR")


def test_hsic_kernel_distinct_from_leadlag():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_leadlag(d["log_return"][0], _mkt_of(d), W),
                    "hsic_mean", "C408_LEADLAG")


def test_hsic_kernel_distinct_from_cdom():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_cdom(d["log_return"], W),
                    "hsic_mean", "C417_CDOM")


def test_hsic_kernel_distinct_from_xskew3():
    rng = np.random.default_rng(214)
    n_assets, n_bars, W = 5, 500, 128
    trend = np.cumsum(rng.normal(0.01, 0.001, size=n_bars), axis=0)
    lr = np.tile(trend, (n_assets, 1)) + rng.normal(0, 0.0001, size=(n_assets, n_bars))
    lr[:, 0] = 0.0
    ref = _ref_xskew3(lr[0], W)
    sa = R.compute_hsic_metrics(lr, W_q=W)["hsic_mean"][0, W - 1:]
    _assert_distinct(sa, ref, "C391_XSKEW3")


def test_hsic_kernel_distinct_from_qspread():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_qspread(d["log_return"][0], W), "hsic_mean", "C376_QSPREAD")


def test_hsic_kernel_distinct_from_lmom():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_lmom(d["log_return"][0], W), "hsic_mean", "C398_LMOM")


def test_hsic_kernel_distinct_from_spectral_coherence():
    d = _guard_base(); W = 128
    def _coh(x, mkt, W):
        n = len(x)
        out = np.full(n, np.nan, float)
        for t in range(W - 1, n):
            xr = x[t - W + 1:t + 1]
            mr = mkt[t - W + 1:t + 1]
            if not (np.isfinite(xr).all() and np.isfinite(mr).all()):
                continue
            X = np.fft.rfft(xr - xr.mean())
            M = np.fft.rfft(mr - mr.mean())
            Pxx = np.abs(X) ** 2; Pmm = np.abs(M) ** 2
            Pxm = np.abs(X * np.conj(M)) ** 2
            coh = Pxm / np.maximum(Pxx * Pmm, 1e-300)
            out[t] = float(np.max(coh[1:])) if len(coh) > 1 else np.nan
        return out
    _guarded_assert(d, _coh(d["log_return"][0], _mkt_of(d), W), "hsic_mean", "C420_COHERENCE")


def test_hsic_kernel_distinct_from_domfreq():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_domfreq(d["log_return"][0], W), "hsic_mean", "C404_DOMFREQ")


def test_hsic_kernel_distinct_from_specfm():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_specfm(d["log_return"][0], W), "hsic_mean", "C397_SPECFM")


def test_hsic_kernel_distinct_from_rqa():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_rqa(d["log_return"][0], W), "hsic_mean", "C425_RQA")


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
    test_hsic_matches_brute_force()
    test_hsic_matches_brute_force_10_assets()
    test_hsic_matches_brute_force_with_nan()
    test_hsic_defined_after_window_nan_before()
    test_hsic_non_finite_propagates()
    test_hsic_degenerate_window_is_nan()
    test_hsic_params()
    test_reference_config_matches_pre_registered_spec()
    test_iid_permuted_surrogate_same_marginal_deterministic()
    test_build_underlying_shapes_and_keys()
    test_build_scores_signals_lookbacks_causal()
    test_hsic_kernel_distinct_from_mutual_information()
    test_hsic_kernel_distinct_from_transfer_entropy()
    test_hsic_kernel_distinct_from_jsd()
    test_hsic_kernel_distinct_from_wasserstein()
    test_hsic_kernel_distinct_from_lyapunov()
    test_hsic_kernel_distinct_from_edfgof()
    test_hsic_kernel_distinct_from_cross_quantilogram()
    test_hsic_kernel_distinct_from_distance_correlation()
    test_hsic_kernel_distinct_from_hvg()
    test_hsic_kernel_distinct_from_markov_sign_transition()
    test_hsic_kernel_distinct_from_sign_autocorr()
    test_hsic_kernel_distinct_from_sign_count_entropy()
    test_hsic_kernel_distinct_from_multi_lag_autocov()
    test_hsic_kernel_distinct_from_avg_pairwise_corr()
    test_hsic_kernel_distinct_from_leadlag()
    test_hsic_kernel_distinct_from_cdom()
    test_hsic_kernel_distinct_from_xskew3()
    test_hsic_kernel_distinct_from_qspread()
    test_hsic_kernel_distinct_from_lmom()
    test_hsic_kernel_distinct_from_spectral_coherence()
    test_hsic_kernel_distinct_from_domfreq()
    test_hsic_kernel_distinct_from_specfm()
    test_hsic_kernel_distinct_from_rqa()
    print("All C439 HSIC runner tests passed")
