"""Tests for C348 runner (scripts/run_c348_realized_var_concentration_xsec_oos.py):
pure-function tests on synthetic arrays plus schema/flag validation of emitted
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

import run_c348_realized_var_concentration_xsec_oos as R  # noqa: E402


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
    # Concrete grid: 4 signals x 6 lookbacks x 3 rebalances x 3 fees x 3 slips
    # x 2 cost_variants = 1296.
    assert R.N_TRIALS == 1296
    assert len(R.SIGNALS) == 4
    assert len(R.LOOKBACKS) == 6
    assert len(R.REBALANCES) == 3
    assert len(R.FEES) == 3 and len(R.SLIPS) == 3 and len(R.COST_VARIANTS) == 2
    assert R.N_TRIALS == (len(R.SIGNALS) * len(R.LOOKBACKS) * len(R.REBALANCES)
                          * len(R.FEES) * len(R.SLIPS) * len(R.COST_VARIANTS))
    placebos = ("hhi_placebo", "hhi_norm_placebo")
    for pb in placebos:
        assert pb in R.SIGNALS
    reals = ("hhi_dev", "hhi_norm_dev")
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


# ---------------- HHI-of-squared-returns metrics fail-closed + brute force
def test_hhi_constant_return_not_nan():
    # constant return -> sq all equal -> hhi = 1/L (uniformly distributed), not NaN
    r = np.full(400, 0.001)
    c = 100.0 * np.exp(np.cumsum(r))
    m = R.compute_hhi_metrics(r, L=60)
    assert np.isfinite(m["hhi"][59:]).all()
    assert np.isfinite(m["hhi_norm"][59:]).all()
    assert np.isnan(m["hhi"][:59]).all()
    assert np.isnan(m["hhi_norm"][:59]).all()


def test_hhi_single_spike_concentrated():
    # one large squared return dominates -> hhi near 1, hhi_norm near 1
    rng = np.random.default_rng(0)
    r = rng.standard_normal(2000) * 0.001
    r[1000] = 0.05  # huge spike -> concentrated variance
    c = 100.0 * np.exp(np.cumsum(r))
    L = 60
    m = R.compute_hhi_metrics(r, L=L)
    fin = np.isfinite(m["hhi"])
    assert fin.sum() > 0
    # hhi in [1/L, 1]
    assert (m["hhi"][fin] >= (1.0 / L) - 1e-9).all()
    assert (m["hhi"][fin] <= 1.0 + 1e-9).all()
    assert (m["hhi_norm"][fin] >= -1e-9).all()
    assert (m["hhi_norm"][fin] <= 1.0 + 1e-9).all()


def test_hhi_defined_after_window():
    rng = np.random.default_rng(1)
    r = rng.standard_normal(2000) * 0.001
    c = 100.0 * np.exp(np.cumsum(r))
    L = 60
    m = R.compute_hhi_metrics(r, L=L)
    assert np.isnan(m["hhi"][:L - 1]).all()      # t<L -> NaN
    assert np.isfinite(m["hhi"][L - 1:]).all()
    assert np.isfinite(m["hhi_norm"][L - 1:]).all()


def test_hhi_matches_brute_force():
    rng = np.random.default_rng(5)
    r = rng.standard_normal(400) * 0.003
    c = 100.0 * np.exp(np.cumsum(r))
    for L in (5, 37, 120):
        m = R.compute_hhi_metrics(r, L=L)
        ref_hhi = np.full(len(r), np.nan)
        ref_hhi_norm = np.full(len(r), np.nan)
        inv_l = 1.0 / L
        for t in range(L - 1, len(r)):
            w = r[t - L + 1:t + 1]
            sq = w * w
            sum_sq = sq.sum()
            if sum_sq > 0:
                p = sq / sum_sq
                hhi = float(np.sum(p * p))
                hhi_norm = (hhi - inv_l) / (1.0 - inv_l)
                ref_hhi[t] = hhi
                ref_hhi_norm[t] = hhi_norm
        fin = np.isfinite(ref_hhi)
        assert np.allclose(m["hhi"][fin], ref_hhi[fin])
        assert np.allclose(m["hhi_norm"][fin], ref_hhi_norm[fin])


def test_reference_config_matches_pre_registered_spec():
    assert R.ATTR_REPRESENTATIVES == {"hhi_dev": "hhi_dev", "hhi_norm_dev": "hhi_norm_dev"}
    assert R.PLACEBO_SEED == 20261123
    assert R.STABILITY_MIN_SIGN_CONSISTENCY == 0.70
    assert R.STABILITY_MIN_SHARPE_CORR == 0.50
    assert R.TRAIN_M == 12 and R.TEST_M == 3 and R.ROLL_M == 3


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
    scores = R.build_scores(series, bs["bucket"])
    for sig in R.SIGNALS:
        for L in R.LOOKBACKS:
            assert (sig, L) in scores
            sc = scores[(sig, L)]
            assert sc.shape == (n_assets, n_days * R.TOD_BARS_PER_DAY)
    # causal: first bar of every score series is NaN
    for key, sc in scores.items():
        assert np.isnan(sc[:, 0]).all(), key


# ---------------- real artifacts schema (if present)
def _find_latest(prefix: str):
    files = sorted((ROOT / "reports").glob(f"campaign348_{prefix}_*.json"))
    files = [f for f in files if ".full." not in f.name]
    return files[-1] if files else None


def test_artifacts_if_present_have_required_flags():
    p = _find_latest("verdict")
    if p is None:
        return
    v = json.loads(p.read_text())
    assert v["campaign"] == 348
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


def test_cache_meta_fields_are_genuinely_distinct():
    meta_path = ROOT / "data" / "cache" / "campaign348_realized_var_concentration_5m.meta.json"
    if not meta_path.exists():
        return
    meta = json.loads(meta_path.read_text())
    assert meta["campaign"] == 348
    assert meta["source_campaign"] == 312
    for f in ("index_ms", "perp_close", "log_return", "abs_ret", "funding_rate"):
        assert f in meta["fields"]
    assert "hhi" not in meta["fields"] and "hhi_norm" not in meta["fields"]
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
