"""Tests for C354 runner (scripts/run_c354_higuchi_fractal_xsec_oos.py): pure-function
tests on synthetic arrays (including a brute-force equality test for the vectorized
Higuchi fractal-dimension kernel) plus schema/flag validation of emitted real-data
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

import run_c354_higuchi_fractal_xsec_oos as R  # noqa: E402


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
    for pb in ("hfd_placebo", "hfd_norm_placebo"):
        assert pb in R.SIGNALS
    for real in ("hfd_dev", "hfd_norm_dev"):
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


# ---------------------------------------------------------------- higuchi fractal dimension kernel
def test_hfd_matches_brute_force():
    # The vectorized sliding-window Higuchi kernel MUST equal the brute-force
    # reference (per-window explicit L(k) aggregation).
    rng = np.random.default_rng(5)
    for n in (300, 512, 700):
        r = rng.standard_normal(n) * 0.003
        fast = R.compute_hfd_metrics(r)
        brute = R._hfd_bruteforce(r, R.HFD_W)
        vf, vb = fast["hfd"], brute["hfd"]
        fin = np.isfinite(vf) & np.isfinite(vb)
        assert fin.sum() > 0
        assert np.array_equal(np.isnan(vf), np.isnan(vb))
        assert np.allclose(vf[fin], vb[fin], rtol=1e-9, atol=1e-9)


def test_hfd_defined_after_window_nan_before():
    rng = np.random.default_rng(1)
    r = rng.standard_normal(2000) * 0.001
    m = R.compute_hfd_metrics(r)
    W = R.HFD_W
    assert np.isnan(m["hfd"][:W]).all()
    assert np.isfinite(m["hfd"][W:]).all()


def test_hfd_nan_in_window_propagates():
    rng = np.random.default_rng(0)
    r = rng.standard_normal(600) * 0.001
    r[300] = np.nan
    W = R.HFD_W
    m = R.compute_hfd_metrics(r)
    for t in range(300, 300 + W):
        assert np.isnan(m["hfd"][t]), f"hfd t={t} should be NaN"
    for t in range(W, 300):
        assert np.isfinite(m["hfd"][t]), f"hfd t={t} should be finite"
    for t in range(300 + W, 600):
        assert np.isfinite(m["hfd"][t]), f"hfd t={t} should be finite"


def test_hfd_random_walk_in_range():
    # iid returns -> HFD finite and within the theoretical [1, 2] band (loose).
    rng = np.random.default_rng(42)
    r = rng.standard_normal(40000)
    m = R.compute_hfd_metrics(r)
    fin = np.isfinite(m["hfd"])
    assert fin.sum() > 1000
    mean_hfd = float(np.mean(m["hfd"][fin]))
    assert 0.8 < mean_hfd < 2.2


def test_hfd_constant_series_all_nan():
    # constant returns -> all first differences zero -> L(k)=0 -> degenerate -> NaN
    r = np.full(400, 0.25)
    m = R.compute_hfd_metrics(r)
    assert not np.isfinite(m["hfd"]).any()


def test_hfd_single_window_matches_manual():
    # explicit manual computation for one window, both L(1) and L(2) sanity
    rng = np.random.default_rng(9)
    w = rng.standard_normal(R.HFD_W) * 0.002
    got = R._hfd_single_window(w, R.HFD_KMAX)
    # manual recompute per spec (1-indexed -> 0-indexed)
    W = len(w)
    L = np.zeros(R.HFD_KMAX)
    for k in range(1, R.HFD_KMAX + 1):
        Lk = 0.0
        for mm in range(1, k + 1):
            N_m = (W - mm) // k
            if N_m <= 0:
                continue
            total = 0.0
            for i in range(1, N_m + 1):
                total += abs(w[mm - 1 + i * k] - w[mm - 1 + (i - 1) * k])
            Lk += (1.0 / k) * total * (W - 1) / (N_m * k)
        L[k - 1] = Lk
    k_arr = np.arange(1, R.HFD_KMAX + 1, dtype=float)
    log_k_inv = np.log(1.0 / k_arr)
    log_L = np.log(L)
    xm = log_k_inv.mean()
    ym = log_L.mean()
    expected = float(((log_k_inv - xm) * (log_L - ym)).sum() / ((log_k_inv - xm) ** 2).sum())
    assert np.isclose(got, expected, rtol=1e-12, atol=1e-12)


# ---------------------------------------------------------------- pre-registered spec constants
def test_reference_config_matches_pre_registered_spec():
    assert R.ATTR_REPRESENTATIVES == {"hfd_dev": "hfd_dev", "hfd_norm_dev": "hfd_norm_dev"}
    assert R.PLACEBO_SEED == 20261220
    assert R.STABILITY_MIN_SIGN_CONSISTENCY == 0.70
    assert R.STABILITY_MIN_SHARPE_CORR == 0.50
    assert R.DOMINANT_SHARE_MIN == 0.50
    assert R.TRAIN_M == 12 and R.TEST_M == 3 and R.ROLL_M == 3
    assert R.HFD_W == 256
    assert R.HFD_KMAX == 16


# ---------------------------------------------------------------- phase-randomized surrogate
def test_phase_randomized_surrogate_same_marginal_deterministic():
    rng = np.random.default_rng(0)
    x = rng.standard_normal(500) * 3.0 + 5.0
    s1 = R._phase_randomized_surrogate(x, R.PLACEBO_SEED)
    s2 = R._phase_randomized_surrogate(x, R.PLACEBO_SEED)
    assert np.array_equal(s1, s2)
    assert np.isclose(np.sort(s1), np.sort(x), equal_nan=True).all()


# ---------------------------------------------------------------- build_underlying / build_scores
def _synthetic_bs(n_assets=3, n_days=8, seed=1):
    rng = np.random.default_rng(seed)
    T = R.TOD_BARS_PER_DAY
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
    assert set(series.keys()) == {"hfd", "hfd_norm"}
    for k in ("hfd", "hfd_norm"):
        assert series[k].shape == (bs["n_assets"], bs["n_bars"])


def test_build_scores_signals_lookbacks_causal():
    bs = _synthetic_bs()
    series = R.build_underlying(bs)
    scores = R.build_scores(series, bs["bucket"])
    for sig in R.SIGNALS:
        for L in R.LOOKBACKS:
            assert (sig, L) in scores
            assert scores[(sig, L)].shape == (bs["n_assets"], bs["n_bars"])
    # causal: first bar of every score series is NaN
    for key, sc in scores.items():
        assert np.isnan(sc[:, 0]).all(), key


# ---------------------------------------------------------------- real artifacts schema (if present)
def _find_latest(prefix: str):
    files = sorted((ROOT / "reports").glob(f"campaign354_{prefix}_*.json"))
    files = [f for f in files if ".full." not in f.name]
    return files[-1] if files else None


def test_artifacts_if_present_have_required_flags():
    p = _find_latest("verdict")
    if p is None:
        return
    v = json.loads(p.read_text())
    assert v["campaign"] == 354
    assert v["real_data_only"] is True and v["fabricated_data"] is False
    assert v["executed_fills"] is False
    assert v["verdict"] in ("EDGE_PROVEN", "RETRACTED")
    assert isinstance(v["edge_proven"], bool)
    for k in ("oos_sweep_sha256", "registry_sha256", "summary_sha256"):
        assert isinstance(v[k], str) and len(v[k]) == 64
    reg = json.loads((ROOT / v["registry_artifact"]).read_text())
    assert reg["real_data_only"] is True and reg["fabricated_data"] is False
    sw = json.loads((ROOT / v["oos_sweep_artifact"]).read_text())
    assert sw["real_data_only"] is True and sw["fabricated_data"] is False
    assert sw["config"]["placebo_seed"] == R.PLACEBO_SEED
    assert sw["config"]["hfd_params"]["W"] == 256
    assert list(sw["config"]["hfd_params"]["scales_k"]) == list(range(1, 17))
    n_total = int(sw["summary"]["n_total_runs"])
    if n_total > 0:  # full sweep artifact (smoke/partial runs report 0)
        assert n_total == R.N_TRIALS
        assert sw["config"]["n_trials"] == R.N_TRIALS


def test_cache_meta_hfd_params_distinct():
    meta_path = ROOT / "data" / "cache" / "campaign354_higuchi_fractal_5m.meta.json"
    if not meta_path.exists():
        return
    meta = json.loads(meta_path.read_text())
    assert meta["campaign"] == 354
    assert meta["source_campaign"] == 312
    assert meta["hfd_params"]["window_W"] == 256
    assert list(meta["hfd_params"]["scales_k"]) == list(range(1, 17))
