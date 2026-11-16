"""Tests for C335 runner (scripts/run_c335_vpin_toxicity_xsec_oos.py): costed OOS
cross-sectional intraday ORDER-FLOW TOXICITY / VPIN SEASONAL DISLOCATION
mean-reversion stat-arb over 864 pre-registered configs on real USDT-M 5m perps.

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

import run_c335_vpin_toxicity_xsec_oos as R  # noqa: E402


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


def test_n_trials_is_864():
    assert R.N_TRIALS == 864
    assert len(R.SIGNALS) == 3
    assert len(R.LOOKBACKS) == 3 and len(R.REBALANCES) == 3
    assert len(R.FEES) == 4 and len(R.SLIPS) == 4 and len(R.COST_VARIANTS) == 2


# ---------------------------------------------------------------- single-leg costs
def test_cost_rate_symmetric_and_perp_heavy():
    assert R.cost_rate_bps(10, 5, "symmetric") == 15.0
    assert R.cost_rate_bps(10, 5, "perp_heavy") == 20.0
    for fee in R.FEES:
        for slip in R.SLIPS:
            assert R.cost_rate_bps(fee, slip, "perp_heavy") >= R.cost_rate_bps(fee, slip, "symmetric")


# ---------------------------------------------------------------- positions
def test_positions_dollar_neutral_and_causal():
    score = np.array([
        [0.9, 0.9, 0.1, 0.1, 0.9, 0.1],
        [0.8, 0.8, 0.2, 0.2, 0.8, 0.2],
        [-0.8, -0.8, -0.2, -0.2, -0.8, -0.2],
        [-0.9, -0.9, -0.1, -0.1, -0.9, -0.1],
    ])
    pos = R.xsec_positions(score, 0.25, 1)
    assert pos.shape == (4, 6)
    assert np.allclose(pos.sum(axis=0), 0.0)
    assert np.all(pos[:, 0] == 0.0)
    assert pos[0, 2] > 0 and pos[3, 2] < 0


def test_positions_hold_reduces_turnover():
    score = np.tile(np.array([[0.9], [0.8], [-0.8], [-0.9]]), (1, 12))
    pos1 = R.xsec_positions(score, 0.25, 1)
    pos6 = R.xsec_positions(score, 0.25, 6)
    turn1 = np.abs(np.diff(pos1, axis=1)).sum()
    turn6 = np.abs(np.diff(pos6, axis=1)).sum()
    assert turn6 <= turn1


def test_positions_nan_asset_gets_zero_weight():
    score = np.array([[0.9, 0.9], [np.nan, 0.1], [-0.8, -0.2], [-0.9, -0.9]])
    pos = R.xsec_positions(score, 0.25, 1)
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


# ---------------------------------------------------------------- trailing same-bucket seasonal mean
def test_trailing_same_bucket_mean_excludes_current_and_nan():
    # bucket all 0; x has NaN at index 2
    bucket = np.zeros(6, dtype=np.int64)
    x = np.array([1.0, 2.0, np.nan, 4.0, 5.0, 6.0])
    base = R._trailing_same_bucket_mean(bucket, x[None, :], L=3, min_prev=2)[0]
    # index 0: no prev -> NaN
    # index 1: prev [1] count1 < 2 -> NaN
    # index 2: prev [1,2] count2 -> 1.5
    # index 3: prev [1,2,nan] finite2 -> 1.5
    # index 4: prev [2,nan,4] finite2 (window last 3 excl current: indices 1..3) -> 3.0
    # index 5: prev indices 2..4 = [nan,4,5] finite2 -> 4.5
    assert np.isnan(base[0]) and np.isnan(base[1])
    assert np.isclose(base[2], 1.5)
    assert np.isclose(base[3], 1.5)
    assert np.isclose(base[4], 3.0)
    assert np.isclose(base[5], 4.5)


def test_trailing_same_bucket_window_is_causal():
    bucket = np.zeros(5, dtype=np.int64)
    x = np.array([1.0, 1.0, 1.0, 100.0, 1.0])
    base = R._trailing_same_bucket_mean(bucket, x[None, :], L=3, min_prev=1)[0]
    # index 3 prev window [1,1,1] -> 1.0 (current 100 excluded)
    assert np.isclose(base[3], 1.0)


def test_build_scores_signals_and_lookbacks_distinct():
    n_assets = 3
    n_days = 8
    T = R.TOD_BARS_PER_DAY
    # build a bucket vector aligned to 288-bar days
    base_day_bucket = np.tile(np.arange(T), n_days)
    bs = {
        "vpin_bkt": np.ones((n_assets, n_days * T)) * 0.5,
        "vpin_ewm": np.ones((n_assets, n_days * T)) * 0.4,
        "toxicity_park": np.ones((n_assets, n_days * T)) * 0.1,
        "bucket": base_day_bucket,
        "n_assets": n_assets, "n_days": n_days, "n_bars": n_days * T,
    }
    scores = R.build_scores(bs)
    for sig in R.SIGNALS:
        for L in R.LOOKBACKS:
            assert (sig, L) in scores
            sc = scores[(sig, L)]
            assert sc.shape == (n_assets, n_days * R.TOD_BARS_PER_DAY)
    # distinctness: with >90 same-bucket occurrences and a non-linear pattern,
    # different L (30 vs 90) must produce different scores.
    nd = 120  # days -> 120 same-bucket occurrences per bucket
    Tb = R.TOD_BARS_PER_DAY
    big_bucket = np.tile(np.arange(Tb), nd)
    # deterministic non-linear pattern per bar index
    pat = (np.sin(np.arange(nd * Tb) * 0.01) + 1.0) * 0.5 + 0.01
    big = np.ones((n_assets, 1)) * pat[None, :]
    bs2 = {
        "vpin_bkt": big.copy(),
        "vpin_ewm": big.copy(),
        "toxicity_park": big.copy(),
        "bucket": big_bucket,
        "n_assets": n_assets, "n_days": nd, "n_bars": nd * Tb,
    }
    s2 = R.build_scores(bs2)
    a = s2[("vpin_bkt_dev", 30)]
    b = s2[("vpin_bkt_dev", 90)]
    fin = np.isfinite(a) & np.isfinite(b)
    assert fin.sum() > 0
    assert not np.allclose(a[fin], b[fin])


# ---------------------------------------------------------------- real artifacts schema (if present)
def _find_latest(prefix: str):
    files = sorted((ROOT / "reports").glob(f"campaign335_{prefix}_*.json"))
    files = [f for f in files if ".full." not in f.name]
    return files[-1] if files else None


def test_artifacts_if_present_have_required_flags():
    p = _find_latest("verdict")
    if p is None:
        return
    v = json.loads(p.read_text())
    assert v["campaign"] == 335
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
    assert sw["real_data_only"] is True and sw["fabricated_data"] is False


def test_cache_meta_fields_are_genuinely_distinct():
    meta = json.loads((ROOT / "data" / "cache" / "campaign335_vpin_toxicity_5m.meta.json").read_text())
    assert meta["campaign"] == 335
    assert meta["source_campaign"] == 312
    for f in ("log_return", "signed_volume", "notional", "vpin_bkt", "vpin_ewm", "toxicity_park"):
        assert f in meta["fields"]
    # genuinely-distinct from C334 price-impact coefficient
    assert "klambda_sv" not in meta["fields"]
    assert "impact_var" not in meta["fields"]
    # genuinely-distinct from C323 raw order-flow levels
    assert "ofi_ratio" not in meta["fields"]
    # genuinely-distinct from C324 Amihud
    assert "illiq" not in meta["fields"]
    # genuinely-distinct from C333 microstructure spread
    assert "roll_spread" not in meta["fields"]
    # toxicity halflife recorded
    assert meta["vpin_halflife_bars"] == 24