"""Tests for C337 runner (scripts/run_c337_orderflow_skew_xsec_oos.py): costed OOS
cross-sectional intraday ORDER-FLOW SKEW / ASYMMETRIC IMPULSE SEASONAL
DISLOCATION mean-reversion stat-arb over 7776 pre-registered configs on real
USDT-M 5m perps.

Pure-function tests on synthetic arrays plus schema/flag validation of emitted
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

import run_c337_orderflow_skew_xsec_oos as R  # noqa: E402


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


def test_n_trials_is_7776():
    assert R.N_TRIALS == 7776
    assert len(R.SIGNALS) == 8
    assert len(R.LOOKBACKS) == 6
    assert len(R.SEASONAL_WINDOWS) == 3
    assert len(R.REBALANCES) == 3
    assert len(R.FEES) == 3 and len(R.SLIPS) == 3 and len(R.COST_VARIANTS) == 2
    assert R.N_TRIALS == (len(R.SIGNALS) * len(R.LOOKBACKS) * len(R.SEASONAL_WINDOWS)
                          * len(R.REBALANCES) * len(R.FEES) * len(R.SLIPS)
                          * len(R.COST_VARIANTS))


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


# ---------------------------------------------------------------- skew & seasonal baseline
def test_skew_full_window_and_causal():
    n = 12
    x = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0])
    s = R._skew_1d(x, 4)
    # first 3 bars cannot have a full 4-bar window
    assert np.isnan(s[:3]).all()
    assert np.isfinite(s[3:]).all()


def test_skew_insufficient_window_is_nan():
    x = np.array([1.0, 2.0, 3.0])
    s = R._skew_1d(x, 5)
    assert np.isnan(s).all()


def test_skew_zero_variance_is_nan():
    x = np.ones(10)
    s = R._skew_1d(x, 5)
    assert np.isnan(s[4:]).all()


def test_trailing_same_bucket_stats_excludes_current_and_nan():
    bucket = np.zeros(6, dtype=np.int64)
    x = np.array([1.0, 2.0, np.nan, 4.0, 5.0, 6.0])
    m, sd = R._same_bucket_stats_1d(bucket, x, None, 2)
    assert np.isnan(m[0]) and np.isnan(m[1])
    assert np.isclose(m[2], 1.5)
    assert np.isclose(m[3], 1.5)
    assert np.isclose(m[4], 7.0 / 3.0)
    assert np.isclose(m[5], 3.0)
    assert np.isnan(sd[0]) and np.isnan(sd[1])


def test_trailing_same_bucket_window_is_causal():
    bucket = np.zeros(5, dtype=np.int64)
    x = np.array([1.0, 1.0, 1.0, 100.0, 1.0])
    m, _ = R._same_bucket_stats_1d(bucket, x, 3, 1)
    assert np.isclose(m[3], 1.0)


def test_ewma_warmup_nan():
    x = np.concatenate([np.full(20, np.nan), np.ones(30)])
    e = R._ewma_nan_aware(x, R.EWMA_HALFLIFE, R.EWMA_MIN_PERIODS)
    assert np.isnan(e[:43]).all()  # 20 NaN + need 24 finite -> first valid at index 43
    assert np.isfinite(e[44])


def test_phase_randomized_surrogate_same_marginal_deterministic():
    rng = np.random.default_rng(0)
    x = rng.standard_normal(500) * 3.0 + 5.0
    s1 = R._phase_randomized_surrogate(x, R.PLACEBO_SEED)
    s2 = R._phase_randomized_surrogate(x, R.PLACEBO_SEED)
    assert np.array_equal(s1, s2)  # deterministic
    assert np.isclose(np.sort(s1), np.sort(x), equal_nan=True).all()  # same marginal


def test_build_scores_signals_lookbacks_windows_distinct():
    n_assets = 3
    n_days = 8
    T = R.TOD_BARS_PER_DAY
    imb = np.ones((n_assets, n_days * T)) * 0.5
    asym = np.ones((n_assets, n_days * T)) * 0.25
    base_day_bucket = np.tile(np.arange(T), n_days)
    bs = {
        "imb": imb, "asym": asym, "bucket": base_day_bucket,
        "n_assets": n_assets, "n_days": n_days, "n_bars": n_days * T,
    }
    series = R.build_underlying(bs)
    scores = R.build_scores(series, bs["bucket"])
    for sig in R.SIGNALS:
        for L in R.LOOKBACKS:
            for w in R.SEASONAL_WINDOWS:
                assert (sig, L, w) in scores
                sc = scores[(sig, L, w)]
                assert sc.shape == (n_assets, n_days * R.TOD_BARS_PER_DAY)
    # causal: first bar of every score series is NaN
    for key, sc in scores.items():
        assert np.isnan(sc[:, 0]).all(), key


# ---------------------------------------------------------------- real artifacts schema (if present)
def _find_latest(prefix: str):
    files = sorted((ROOT / "reports").glob(f"campaign337_{prefix}_*.json"))
    files = [f for f in files if ".full." not in f.name]
    return files[-1] if files else None


def test_artifacts_if_present_have_required_flags():
    p = _find_latest("verdict")
    if p is None:
        return
    v = json.loads(p.read_text())
    assert v["campaign"] == 337
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
    meta = json.loads((ROOT / "data" / "cache" / "campaign337_orderflow_skew_5m.meta.json").read_text())
    assert meta["campaign"] == 337
    assert meta["source_campaign"] == 312
    for f in ("log_return", "imb", "buy_impulse", "sell_impulse", "asym"):
        assert f in meta["fields"]
    # genuinely-distinct from C336 persistence fields
    for f in ("sign_imbalance", "signed_vol_share", "notional_imb", "imb_ewm", "imb_ac1", "streak_len"):
        assert f not in meta["fields"]
    # genuinely-distinct from C335 VPIN/toxicity
    assert "vpin_bkt" not in meta["fields"]
    assert "vpin_ewm" not in meta["fields"]
    assert "toxicity_park" not in meta["fields"]
    # genuinely-distinct from C334 price-impact coefficient
    assert "klambda_sv" not in meta["fields"]
    assert "impact_var" not in meta["fields"]
    # genuinely-distinct from C323 raw order-flow levels
    assert "ofi_ratio" not in meta["fields"]
