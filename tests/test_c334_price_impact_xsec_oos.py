"""Tests for C334 runner (scripts/run_c334_price_impact_xsec_oos.py): costed OOS
cross-sectional intraday KYLE'S LAMBDA / PRICE-IMPACT COEFFICIENT SEASONAL
DISLOCATION mean-reversion stat-arb over 864 pre-registered configs on real
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

import run_c334_price_impact_xsec_oos as R  # noqa: E402


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


# ---------------------------------------------------------------- trailing price-impact stats
def test_trailing_same_bucket_min_periods():
    bucket = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    x = np.arange(8, dtype=float)
    x[2] = np.nan
    s, c = R._trailing_same_bucket(bucket, x, L=3)
    # bucket 0: occ0 x=0 count1; occ1 x=1 count2; occ2 nan count3(sum1); occ3 x=3 count3(sum 1+3=4? nan->0 => 1+3=4)
    # trailing L=3 incl current: occ2 window occ0,1,2 -> sum 0+1+0=1 count3
    assert c[2] == 3
    assert np.isclose(s[2], 1.0)
    # bucket boundary: occ4 (bucket1 first) count1
    assert c[4] == 1


def test_expanding_prev_mean_min_periods():
    bucket = np.array([0, 0, 0, 0, 0])
    lam = np.array([1.0, 2.0, np.nan, 4.0, 5.0])
    base = R._expanding_prev_mean(bucket, lam[None, :], min_prev=3)[0]
    # occ0: no prev -> NaN; occ1: prev [1] count1<3 NaN; occ2: prev [1,2] count2<3 NaN
    # occ3: prev [1,2,nan] finite count2<3 -> NaN; occ4: prev [1,2,nan,4] finite count3 -> (1+2+4)/3=7/3
    assert np.isnan(base[0]) and np.isnan(base[1]) and np.isnan(base[2]) and np.isnan(base[3])
    assert np.isclose(base[4], 7.0 / 3.0)


def test_klambda_zero_flow_nan():
    bucket = np.zeros(5, dtype=np.int64)
    r = np.ones(5)
    f = np.zeros(5)  # all zero flow -> sum(f^2)=0 -> NaN
    n_ = np.ones(5)
    pi = R._compute_price_impact(bucket, r[None, :], f[None, :], n_[None, :], L=3)
    assert np.all(np.isnan(pi["klambda_sv"][0]))


def test_klambda_nonzero():
    bucket = np.zeros(6, dtype=np.int64)
    r = np.array([0.0, 0.01, 0.02, 0.03, 0.04, 0.05])
    f = np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0])
    n_ = np.ones(6)
    pi = R._compute_price_impact(bucket, r[None, :], f[None, :], n_[None, :], L=3)
    # occ2 (index2): window r[0..2]*f / sum f^2 = (0+0.01+0.02)/3 = 0.01
    assert np.isclose(pi["klambda_sv"][0, 2], 0.01)
    # impact_var = lambda^2 * var(f); var(f)=0 (constant) -> NaN
    assert np.all(np.isnan(pi["impact_var"][0]))


def test_build_scores_signals():
    n_assets = 3
    n_days = 8
    T = R.TOD_BARS_PER_DAY
    bs = {
        "log_return": np.zeros((n_assets, n_days * T)),
        "signed_volume": np.ones((n_assets, n_days * T)),
        "notional": np.ones((n_assets, n_days * T)),
        "bucket": np.tile(np.arange(T)[None, :], (n_assets * n_days, 1)).ravel()[: n_days * T],
        "n_assets": n_assets, "n_days": n_days, "n_bars": n_days * T,
    }
    scores = R.build_scores(bs)
    for sig in R.SIGNALS:
        for L in R.LOOKBACKS:
            assert (sig, L) in scores
            sc = scores[(sig, L)]
            assert sc.shape == (n_assets, n_days * R.TOD_BARS_PER_DAY)


# ---------------------------------------------------------------- real artifacts schema (if present)
def _find_latest(prefix: str):
    files = sorted((ROOT / "reports").glob(f"campaign334_{prefix}_*.json"))
    files = [f for f in files if ".full." not in f.name]
    return files[-1] if files else None


def test_artifacts_if_present_have_required_flags():
    p = _find_latest("verdict")
    if p is None:
        return
    v = json.loads(p.read_text())
    assert v["campaign"] == 334
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
    meta = json.loads((ROOT / "data" / "cache" / "campaign334_price_impact_5m.meta.json").read_text())
    assert meta["campaign"] == 334
    assert meta["source_campaign"] == 312
    for f in ("log_return", "signed_volume", "notional", "trade_count"):
        assert f in meta["fields"]
    # genuinely-distinct from C332 price-flow fields
    assert "r_sv_align" not in meta["fields"]
    # genuinely-distinct from C331 tail-split fields
    assert "pos_part" not in meta["fields"]
    assert "neg_part" not in meta["fields"]
    # genuinely-distinct from C330 path fields
    assert "cumret" not in meta["fields"]
    assert "drawdown" not in meta["fields"]
    assert "runup" not in meta["fields"]
    assert "path_eff" not in meta["fields"]
    # genuinely-distinct from C324 Amihud
    assert "illiq" not in meta["fields"]
    # genuinely-distinct from C325 avg trade size
    assert "ats" not in meta["fields"]
    assert "svpt" not in meta["fields"]
    # genuinely-distinct from C333 microstructure noise/spread
    assert "roll_spread" not in meta["fields"]
    assert "vwcl_spread" not in meta["fields"]
    assert "noise_var" not in meta["fields"]
    # genuinely-distinct from C323 order-flow
    assert "ofi_ratio" not in meta["fields"]
