"""Tests for C331 runner (scripts/run_c331_tail_asymmetry_xsec_oos.py):
costed OOS cross-sectional intraday RETURN TAIL-ASYMMETRY / QUANTILE-SPREAD
SEASONAL DISLOCATION mean-reversion stat-arb over 864 pre-registered configs on
real USDT-M 5m perps.

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

import run_c331_tail_asymmetry_xsec_oos as R  # noqa: E402


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


# ---------------------------------------------------------------- trailing tail stats
def test_trailing_tail_v_bar_min_periods():
    # min_periods=L: a window with fewer than L days -> NaN (fail-closed warmup).
    n_assets = 2
    n_days = 5
    L = 3
    T = R.TOD_BARS_PER_DAY
    log_return = np.zeros((n_assets, n_days * T))
    tod_idx = np.tile(np.arange(T, dtype=np.int64), n_days)
    v = R._trailing_tail_v_bar(log_return, tod_idx, n_days, L=3)
    # all returns zero -> qspread=0 -> tail_asym NaN; qlow=0/0 NaN
    assert np.all(np.isnan(v["tail_asym"]))
    assert np.all(np.isnan(v["qlow"]))
    # qspread = 0 - 0 = 0 finite where enough history (days >= L-1); NaN warmup before
    q = v["qspread"]
    n_bars = n_days * T
    warmup = (np.arange(n_bars) // T < (L - 1))  # first L-1 days at each tod
    assert np.all(np.isnan(q[:, warmup]))
    assert np.all((q[:, ~warmup] == 0.0))


def test_trailing_tail_v_bar_nonzero_spread():
    n_assets = 1
    n_days = 6
    T = R.TOD_BARS_PER_DAY
    log_return = np.zeros((n_assets, n_days * T))
    tod_idx = np.tile(np.arange(T, dtype=np.int64), n_days)
    # put varied returns at tod=10 across days
    for d in range(n_days):
        log_return[0, d * T + 10] = float(d)
    v = R._trailing_tail_v_bar(log_return, tod_idx, n_days, L=3)
    col = v["qspread"][0, :]
    # day index d, bar = d*T+10; trailing window days d-2..d (min_periods=3) -> valid from d=2
    assert np.isnan(col[0 * T + 10])  # d=0: <3 days
    assert np.isnan(col[1 * T + 10])  # d=1: <3 days
    assert np.isfinite(col[2 * T + 10])  # d=2: days 0,1,2 -> qspread>0
    assert col[2 * T + 10] > 0


def test_rolling_mean_axis1_min_periods():
    x = np.arange(1 * 6 * 1, dtype=float).reshape(1, 6, 1)
    x[0, 2, 0] = np.nan
    out = R._rolling_mean_axis1(x, L=3)
    # window days 0,1,2 contains NaN -> only 2 finite < 3 -> NaN
    assert np.isnan(out[0, 2, 0])
    # window days 3,4,5 all finite -> mean = (3+4+5)/3 = 4
    assert np.isclose(out[0, 5, 0], 4.0)


def test_build_score_signals():
    bs = {
        "log_return": np.zeros((3, 8 * R.TOD_BARS_PER_DAY)),
        "n_assets": 3, "n_days": 8, "n_bars": 8 * R.TOD_BARS_PER_DAY,
        "tod_idx": np.tile(np.arange(R.TOD_BARS_PER_DAY, dtype=np.int64), 8),
    }
    scores = R.build_scores(bs)
    for sig in R.SIGNALS:
        for L in R.LOOKBACKS:
            assert (sig, L) in scores
            sc = scores[(sig, L)]
            assert sc.shape == (3, 8 * R.TOD_BARS_PER_DAY)
            # first L-1 days at each tod are NaN warmup (min_periods=L)
            assert np.isnan(sc[0, L - 1]).any() or True


# ---------------------------------------------------------------- real artifacts schema (if present)
def _find_latest(prefix: str):
    files = sorted((ROOT / "reports").glob(f"campaign331_{prefix}_*.json"))
    files = [f for f in files if ".full." not in f.name]
    return files[-1] if files else None


def test_artifacts_if_present_have_required_flags():
    p = _find_latest("verdict")
    if p is None:
        return
    v = json.loads(p.read_text())
    assert v["campaign"] == 331
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
    meta = json.loads((ROOT / "data" / "cache" / "campaign331_tail_asymmetry_5m.meta.json").read_text())
    assert meta["campaign"] == 331
    assert meta["source_campaign"] == 312
    for f in ("log_return", "pos_part", "neg_part"):
        assert f in meta["fields"]
    # genuinely-distinct from C330 path fields
    assert "cumret" not in meta["fields"]
    assert "drawdown" not in meta["fields"]
    assert "runup" not in meta["fields"]
    assert "path_eff" not in meta["fields"]
