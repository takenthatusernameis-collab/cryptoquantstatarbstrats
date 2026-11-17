"""Tests for C349 runner (scripts/run_c349_permutation_entropy_xsec_oos.py):
pure-function tests on synthetic arrays plus schema/flag validation of emitted
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

import run_c349_permutation_entropy_xsec_oos as R  # noqa: E402


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
    placebos = ("perm_ent_placebo", "perm_ent_norm_placebo")
    for pb in placebos:
        assert pb in R.SIGNALS
    reals = ("perm_ent_dev", "perm_ent_norm_dev")
    for r in reals:
        assert r in R.SIGNALS


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


# ---------------------------------------------------------------- Permutation entropy (Bandt–Pompe) metrics
def test_perm_ent_constant_return_not_nan():
    # constant return -> all 3-tuples have pattern 0 (a<=b<=c) -> p_0=1, ent=0
    r = np.full(400, 0.001)
    c = 100.0 * np.exp(np.cumsum(r))
    m = R.compute_perm_ent_metrics(r, W=60, m=3)
    assert np.isfinite(m["perm_ent"][60:]).all()
    assert np.isfinite(m["perm_ent_norm"][60:]).all()
    assert np.isnan(m["perm_ent"][:60]).all()
    assert np.isnan(m["perm_ent_norm"][:60]).all()
    # For constant returns, entropy should be 0
    fin = np.isfinite(m["perm_ent"])
    assert (m["perm_ent"][fin] >= -1e-9).all()
    assert (m["perm_ent"][fin] <= 1e-9).all()
    assert (m["perm_ent_norm"][fin] >= -1e-9).all()
    assert (m["perm_ent_norm"][fin] <= 1e-9).all()


def test_perm_ent_defined_after_window():
    rng = np.random.default_rng(1)
    r = rng.standard_normal(2000) * 0.001
    c = 100.0 * np.exp(np.cumsum(r))
    W = 60
    m = R.compute_perm_ent_metrics(r, W=W, m=3)
    # NaN for t < W (pre-registered: NaN if t < W)
    assert np.isnan(m["perm_ent"][:W]).all()
    assert np.isnan(m["perm_ent_norm"][:W]).all()
    # Finite for t >= W
    assert np.isfinite(m["perm_ent"][W:]).all()
    assert np.isfinite(m["perm_ent_norm"][W:]).all()


def test_perm_ent_bounds():
    # entropy should be in [0, ln(6)], normalized in [0, 1]
    rng = np.random.default_rng(2)
    r = rng.standard_normal(2000) * 0.001
    c = 100.0 * np.exp(np.cumsum(r))
    m = R.compute_perm_ent_metrics(r, W=60, m=3)
    fin = np.isfinite(m["perm_ent"])
    assert fin.sum() > 0
    assert (m["perm_ent"][fin] >= -1e-9).all()
    assert (m["perm_ent"][fin] <= R.PERM_LOG_FACT + 1e-9).all()
    assert (m["perm_ent_norm"][fin] >= -1e-9).all()
    assert (m["perm_ent_norm"][fin] <= 1.0 + 1e-9).all()


def test_perm_ent_matches_brute_force():
    rng = np.random.default_rng(5)
    r = rng.standard_normal(400) * 0.003
    c = 100.0 * np.exp(np.cumsum(r))
    for W in (5, 37, 120):
        m_fast = R.compute_perm_ent_metrics(r, W=W, m=3)
        m_brute = R._compute_perm_ent_bruteforce(r, W=W, m=3)
        fin = np.isfinite(m_fast["perm_ent"])
        assert np.allclose(m_fast["perm_ent"][fin], m_brute["perm_ent"][fin], rtol=1e-6)
        assert np.allclose(m_fast["perm_ent_norm"][fin], m_brute["perm_ent_norm"][fin], rtol=1e-6)


def test_perm_ent_nan_in_window_propagates():
    r = np.random.default_rng(0).standard_normal(200) * 0.001
    r[50] = np.nan
    W = 60
    m = R.compute_perm_ent_metrics(r, W=W, m=3)
    # Windows containing the NaN should have NaN output
    # The NaN is at index 50, so windows ending at t where t-W+1 <= 50 <= t
    # i.e., t in [50, 50+W-1] = [50, 109]
    for t in range(50, 110):
        assert np.isnan(m["perm_ent"][t]), f"t={t} should be NaN"
    # Outside that range should be finite (for t>=W)
    for t in range(W, 50):
        assert np.isfinite(m["perm_ent"][t]), f"t={t} should be finite"
    for t in range(110, 200):
        assert np.isfinite(m["perm_ent"][t]), f"t={t} should be finite"


def test_ordinal_pattern_ids_m3():
    # Test the vectorized pattern ID mapping
    # Each test uses array of length 3 -> 1 tuple

    # Pattern 0: a <= b <= c  e.g., (1, 2, 3)
    r = np.array([1.0, 2.0, 3.0])
    pid = R._ordinal_pattern_ids_m3(r)
    assert np.array_equal(pid, [0])

    # Pattern 1: a <= c < b  e.g., (1, 3, 2)
    r = np.array([1.0, 3.0, 2.0])
    pid = R._ordinal_pattern_ids_m3(r)
    assert np.array_equal(pid, [1])

    # Pattern 2: b < a <= c  e.g., (2, 1, 3)
    r = np.array([2.0, 1.0, 3.0])
    pid = R._ordinal_pattern_ids_m3(r)
    assert np.array_equal(pid, [2])

    # Pattern 3: c < a < b  e.g., (2, 3, 1)
    r = np.array([2.0, 3.0, 1.0])
    pid = R._ordinal_pattern_ids_m3(r)
    assert np.array_equal(pid, [3])

    # Pattern 4: b < c < a  e.g., (3, 1, 2)
    r = np.array([3.0, 1.0, 2.0])
    pid = R._ordinal_pattern_ids_m3(r)
    assert np.array_equal(pid, [4])

    # Pattern 5: c < b < a  e.g., (3, 2, 1)
    r = np.array([3.0, 2.0, 1.0])
    pid = R._ordinal_pattern_ids_m3(r)
    assert np.array_equal(pid, [5])

    # Test multiple consecutive tuples
    # Monotonically increasing -> all pattern 0
    r = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
    pid = R._ordinal_pattern_ids_m3(r)
    assert np.array_equal(pid, [0, 0, 0, 0])

    # Test NaN propagation
    r = np.array([1.0, 2.0, np.nan, 2.0, 3.0, 4.0])
    pid = R._ordinal_pattern_ids_m3(r)
    assert pid[0] == -1  # (1, 2, nan) -> NaN
    assert pid[1] == -1  # (2, nan, 2) -> NaN
    assert pid[2] == -1  # (nan, 2, 3) -> NaN
    assert pid[3] == 0   # (2, 3, 4) -> pattern 0


def test_ordinal_pattern_stable_tiebreaking():
    # Equal values should use positional tie-breaking (earlier index = smaller)
    # (1, 1, 1) -> all equal, stable sort gives (0,1,2) -> pattern 0
    r = np.array([1.0, 1.0, 1.0, 1.0])
    pid = R._ordinal_pattern_ids_m3(r)
    assert np.array_equal(pid, [0, 0])

    # (1, 1, 2) -> a=1, b=1, c=2. With stable tie-break, a<=b, b<=c, a<=c -> pattern 0
    r = np.array([1.0, 1.0, 2.0])
    pid = R._ordinal_pattern_ids_m3(r)
    assert pid[0] == 0

    # (2, 1, 1) -> a=2, b=1, c=1. Stable ranks: (2,0,1) -> pattern 4.
    r = np.array([2.0, 1.0, 1.0])
    pid = R._ordinal_pattern_ids_m3(r)
    assert pid[0] == 4

    # (1, 2, 1) -> a=1, b=2, c=1. a_le_b=True, b_le_c=False, a_le_c=True (1<=1) -> code=101b=5 -> pattern 1
    # ranks: (1,2,1) -> sorted indices [0,2,1] -> ranks [0,2,1] -> a=0, c=1, b=2 -> a<=c<b -> pattern 1. Correct.
    r = np.array([1.0, 2.0, 1.0])
    pid = R._ordinal_pattern_ids_m3(r)
    assert pid[0] == 1


def test_perm_ent_known_distribution():
    # Construct returns that produce uniform pattern distribution -> max entropy
    # This is hard to do analytically, but we can test that entropy is bounded
    rng = np.random.default_rng(42)
    r = rng.standard_normal(10000) * 0.01  # iid normal -> should approach uniform pattern distribution
    m = R.compute_perm_ent_metrics(r, W=256, m=3)
    fin = np.isfinite(m["perm_ent"])
    # For iid continuous, expected entropy approaches ln(6) ≈ 1.79176
    mean_ent = np.mean(m["perm_ent"][fin])
    mean_norm = np.mean(m["perm_ent_norm"][fin])
    assert mean_ent > 1.5  # Should be close to ln(6)
    assert mean_norm > 0.85


def test_reference_config_matches_pre_registered_spec():
    assert R.ATTR_REPRESENTATIVES == {"perm_ent_dev": "perm_ent_dev", "perm_ent_norm_dev": "perm_ent_norm_dev"}
    assert R.PLACEBO_SEED == 20261125
    assert R.STABILITY_MIN_SIGN_CONSISTENCY == 0.70
    assert R.STABILITY_MIN_SHARPE_CORR == 0.50
    assert R.TRAIN_M == 12 and R.TEST_M == 3 and R.ROLL_M == 3
    assert R.PERM_M == 3
    assert R.PERM_W == 256
    assert R.PERM_N_PATTERNS == 6
    assert np.isclose(R.PERM_LOG_FACT, math.log(6))


# ---------------------------------------------------------------- phase-randomized surrogate
def test_phase_randomized_surrogate_same_marginal_deterministic():
    rng = np.random.default_rng(0)
    x = rng.standard_normal(500) * 3.0 + 5.0
    s1 = R._phase_randomized_surrogate(x, R.PLACEBO_SEED)
    s2 = R._phase_randomized_surrogate(x, R.PLACEBO_SEED)
    assert np.array_equal(s1, s2)
    assert np.isclose(np.sort(s1), np.sort(x), equal_nan=True).all()


# ---------------------------------------------------------------- build_scores causal + shapes
def test_build_scores_signals_lookbacks_causal():
    n_assets = 3
    n_days = 8
    T = R.TOD_BARS_PER_DAY
    rng = np.random.default_rng(1)
    lr = rng.standard_normal((n_assets, n_days * T)) * 0.001
    c = 100.0 * np.exp(np.cumsum(lr, axis=1))
    bs = {
        "perp_close": c,
        "log_return": lr,
        "bucket": np.tile(np.arange(T), n_days),
        "n_assets": n_assets, "n_days": n_days, "n_bars": n_days * T,
    }
    series = R.build_underlying(bs)
    # series has keys "perm_ent" and "perm_ent_norm" (no lookback dimension for intrinsic metric)
    assert "perm_ent" in series
    assert "perm_ent_norm" in series
    assert series["perm_ent"].shape == (n_assets, n_days * T)
    scores = R.build_scores(series, bs["bucket"])
    for sig in R.SIGNALS:
        for L in R.LOOKBACKS:
            assert (sig, L) in scores
            sc = scores[(sig, L)]
            assert sc.shape == (n_assets, n_days * R.TOD_BARS_PER_DAY)
    # causal: first bar of every score series is NaN
    for key, sc in scores.items():
        assert np.isnan(sc[:, 0]).all(), key


# ---------------------------------------------------------------- real artifacts schema (if present)
def _find_latest(prefix: str):
    files = sorted((ROOT / "reports").glob(f"campaign349_{prefix}_*.json"))
    files = [f for f in files if ".full." not in f.name]
    return files[-1] if files else None


def test_artifacts_if_present_have_required_flags():
    p = _find_latest("verdict")
    if p is None:
        return
    v = json.loads(p.read_text())
    assert v["campaign"] == 349
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
    assert sw["config"]["perm_params"]["m"] == 3
    assert sw["config"]["perm_params"]["W"] == 256


def test_cache_meta_fields_are_genuinely_distinct():
    meta_path = ROOT / "data" / "cache" / "campaign349_permutation_entropy_5m.meta.json"
    if not meta_path.exists():
        return
    meta = json.loads(meta_path.read_text())
    assert meta["campaign"] == 349
    assert meta["source_campaign"] == 312
    for f in ("index_ms", "perp_close", "log_return", "abs_ret", "funding_rate"):
        assert f in meta["fields"]
    assert "perm_ent" not in meta["fields"] and "perm_ent_norm" not in meta["fields"]
    for f in ("hhi", "hhi_norm"):
        assert f not in meta["fields"]
    for f in ("pid", "vwvol", "price_impact"):
        assert f not in meta["fields"]
    for f in ("vol_cv", "notional_cv", "flow_cv", "tc_cv"):
        assert f not in meta["fields"]
    for f in ("vw_ret", "skew", "kurt"):
        assert f not in meta["fields"]
    for f in ("ret_acf", "signed_ret_acf"):
        assert f not in meta["fields"]
    for f in ("vcl1", "vcl5", "vcr"):
        assert f not in meta["fields"]
    for f in ("chop", "mrv", "sq_ret"):
        assert f not in meta["fields"]
    for f in ("clv", "clv_pos", "wr", "wr_ext"):
        assert f not in meta["fields"]
    for f in ("rs_norm", "rs_dir", "rs_raw"):
        assert f not in meta["fields"]
    for f in ("dd_long", "dd_frac", "dd_long_norm"):
        assert f not in meta["fields"]
    for f in ("sign_ent", "sign_ent_norm"):
        assert f not in meta["fields"]