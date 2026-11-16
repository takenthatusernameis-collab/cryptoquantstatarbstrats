"""Tests for C333 runner (scripts/run_c333_microstructure_noise_xsec_oos.py):
costed OOS cross-sectional intraday MICROSTRUCTURE NOISE & EFFECTIVE SPREAD
SEASONAL DISLOCATION mean-reversion stat-arb over 864 pre-registered configs
on real USDT-M 5m perps.

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

import run_c333_microstructure_noise_xsec_oos as R  # noqa: E402


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


# ---------------------------------------------------------------- trailing microstructure stats
def test_rolling_var_axis1_zero_variance_nan():
    n_assets, n_days, n_buk = 1, 6, 1
    x = np.ones((n_assets, n_days, n_buk))  # constant -> var 0 -> NaN
    out = R._rolling_var_axis1(x, L=3)
    assert np.all(np.isnan(out))


def test_rolling_var_axis1_min_periods():
    n_assets, n_days, n_buk = 1, 6, 1
    x = np.arange(n_days, dtype=float).reshape(n_assets, n_days, n_buk)
    x[0, 2, 0] = np.nan  # one NaN in window days 0..2 -> only 2 finite < 3 -> NaN
    out = R._rolling_var_axis1(x, L=3)
    assert np.isnan(out[0, 2, 0])
    # NaN at day 2 affects windows ending at days 2,3,4 (windows: 0-2, 1-3, 2-4)
    assert np.isnan(out[0, 3, 0])
    assert np.isnan(out[0, 4, 0])
    # day 5 window (3,4,5) has 3 finite -> finite
    assert np.isfinite(out[0, 5, 0])


def test_rolling_cov_lag1_axis1_min_periods():
    n_assets, n_days, n_buk = 1, 7, 1  # need 7 days for day 5 to have 3 valid pairs after NaN at day 2
    x = np.arange(n_days, dtype=float).reshape(n_assets, n_days, n_buk)
    x[0, 2, 0] = np.nan
    out = R._rolling_cov_lag1_axis1(x, L=3)
    assert np.isnan(out[0, 2, 0])
    # NaN at day 2 affects windows ending at days 2,3,4
    assert np.isnan(out[0, 3, 0])
    assert np.isnan(out[0, 4, 0])
    # day 5 window (3,4,5) has pairs at 3,4,5 -> only 2 valid (day 3 invalid due to lag from day 2)
    # day 6 window (4,5,6) has pairs at 4,5,6 -> 3 valid
    assert np.isnan(out[0, 5, 0])
    assert np.isfinite(out[0, 6, 0])


def test_trailing_microstructure_v_bar_min_periods():
    n_assets = 2
    n_days = 5
    L = 3
    T = R.TOD_BARS_PER_DAY
    log_return = np.zeros((n_assets, n_days * T))
    vwap = np.ones((n_assets, n_days * T))
    perp_close = np.ones((n_assets, n_days * T))
    v = R._trailing_microstructure_v_bar(log_return, vwap, perp_close, n_days, L=3)
    # constant log_return -> var 0 -> noise_var NaN; cov 0 -> roll_spread NaN; vwap=close -> vwcl_spread 0
    assert np.all(np.isnan(v["noise_var"]))
    assert np.all(np.isnan(v["roll_spread"]))
    # vwcl_spread = 2*|close-vwap|/(close+vwap) = 0 everywhere (finite)
    assert np.all(v["vwcl_spread"] == 0.0)


def test_trailing_microstructure_v_bar_nonzero():
    n_assets = 1
    n_days = 6
    T = R.TOD_BARS_PER_DAY
    log_return = np.zeros((n_assets, n_days * T))
    vwap = np.ones((n_assets, n_days * T))
    perp_close = np.ones((n_assets, n_days * T))
    # create variation at tod=10, starting from day 0 with non-zero diff
    for d in range(n_days):
        log_return[0, d * T + 10] = float(d + 1) * 0.001
        vwap[0, d * T + 10] = 1.0 + float(d + 1) * 0.0005
        perp_close[0, d * T + 10] = 1.0 + float(d + 1) * 0.001
    v = R._trailing_microstructure_v_bar(log_return, vwap, perp_close, n_days, L=3)
    col_vwcl = v["vwcl_spread"][0, :]
    # vwcl_spread is positive where close != vwap
    assert col_vwcl[0 * T + 10] > 0  # d=0: first occurrence, finite
    assert col_vwcl[1 * T + 10] > 0
    assert col_vwcl[2 * T + 10] > 0


def test_build_scores_signals():
    n_assets = 3
    n_days = 8
    bs = {
        "log_return": np.zeros((n_assets, n_days * R.TOD_BARS_PER_DAY)),
        "vwap": np.ones((n_assets, n_days * R.TOD_BARS_PER_DAY)),
        "perp_close": np.ones((n_assets, n_days * R.TOD_BARS_PER_DAY)),
        "n_assets": n_assets, "n_days": n_days, "n_bars": n_days * R.TOD_BARS_PER_DAY,
    }
    scores = R.build_scores(bs)
    for sig in R.SIGNALS:
        for L in R.LOOKBACKS:
            assert (sig, L) in scores
            sc = scores[(sig, L)]
            assert sc.shape == (n_assets, n_days * R.TOD_BARS_PER_DAY)


# ---------------------------------------------------------------- real artifacts schema (if present)
def _find_latest(prefix: str):
    files = sorted((ROOT / "reports").glob(f"campaign333_{prefix}_*.json"))
    files = [f for f in files if ".full." not in f.name]
    return files[-1] if files else None


def test_artifacts_if_present_have_required_flags():
    p = _find_latest("verdict")
    if p is None:
        return
    v = json.loads(p.read_text())
    assert v["campaign"] == 333
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
    meta = json.loads((ROOT / "data" / "cache" / "campaign333_microstructure_noise_5m.meta.json").read_text())
    assert meta["campaign"] == 333
    assert meta["source_campaign"] == 312
    for f in ("log_return", "vwap", "notional", "trade_count", "signed_volume"):
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