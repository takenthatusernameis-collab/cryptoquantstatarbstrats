"""Tests for C321 runner (scripts/run_c321_intraday_range_breakout_xsec_oos.py):
the costed out-of-sample cross-sectional INTRADAY RANGE / BREAKOUT /
OVERNIGHT-vs-INTRADAY SEASONALITY mean-reversion stat-arb over 1440
pre-registered configs on real USDT-M linear 5m perps.

These tests never fetch or fabricate market data. They exercise the runner's pure
functions on synthetic arrays (multiple-testing correction, single-leg cost
model, causal dollar-neutral cross-sectional positions, month-aligned
walk-forward splits, nan-aware trailing mean, bucket trailing stats, ewm baseline,
and the five intraday range/breakout/overnight-intraday signal builders), and
they validate the schema and flags of the emitted real-data artifacts (verdict,
registry, summary, binding constraint, sweep) produced by the full run.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import run_c321_intraday_range_breakout_xsec_oos as R  # noqa: E402


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


# ---------------------------------------------------------------- single-leg costs
def test_cost_rate_symmetric_and_perp_heavy():
    assert R.cost_rate_bps(10, 5, "symmetric") == 15.0
    assert R.cost_rate_bps(10, 5, "perp_heavy") == 20.0
    for fee in R.FEES:
        for slip in R.SLIPS:
            assert R.cost_rate_bps(fee, slip, "perp_heavy") >= R.cost_rate_bps(fee, slip, "symmetric")


def test_cost_grid_is_real_and_nonzero():
    assert min(R.FEES) >= 1 and max(R.FEES) == 20
    assert min(R.SLIPS) >= 1 and max(R.SLIPS) == 10
    for fee in R.FEES:
        for slip in R.SLIPS:
            for cv in R.COST_VARIANTS:
                assert R.cost_rate_bps(fee, slip, cv) > 0


# ---------------------------------------------------------------- positions
def _score_matrix():
    return np.array([
        [0.9, 0.9, 0.1, 0.1, 0.9, 0.1],
        [0.8, 0.8, 0.2, 0.2, 0.8, 0.2],
        [-0.8, -0.8, -0.2, -0.2, -0.8, -0.2],
        [-0.9, -0.9, -0.1, -0.1, -0.9, -0.1],
    ])


def test_positions_dollar_neutral_and_causal():
    pos = R.xsec_positions(_score_matrix(), 0.25, 1)
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


# ---------------------------------------------------------------- trailing ops
def test_trailing_nanmean_warmup_nan_and_value():
    x = np.array([[1.0, 2.0, 3.0, 4.0, 5.0]])
    out = R.trailing_nanmean(x, 3)
    assert np.isnan(out[0, 0]) and np.isnan(out[0, 1])
    assert np.isclose(out[0, 2], 2.0)   # mean(1,2,3)
    assert np.isclose(out[0, 3], 3.0)   # mean(2,3,4)
    assert np.isclose(out[0, 4], 4.0)   # mean(3,4,5)


def test_trailing_nanmean_ignores_nan():
    x = np.array([[1.0, np.nan, 3.0, 4.0]])
    out = R.trailing_nanmean(x, 2)
    assert np.isnan(out[0, 0])
    assert np.isclose(out[0, 1], 1.0)   # window [1,nan] -> 1
    assert np.isclose(out[0, 2], 3.0)   # window [nan,3] -> 3
    assert np.isclose(out[0, 3], 3.5)   # window [3,4] -> 3.5


def test_finite_or_nan_masks_nonfinite():
    x = np.array([[1.0, np.inf, -np.inf, np.nan, 5.0]])
    out = R.finite_or_nan(x)
    assert out[0, 0] == 1.0
    assert np.isnan(out[0, 1]) and np.isnan(out[0, 2]) and np.isnan(out[0, 3])
    assert out[0, 4] == 5.0


# ---------------------------------------------------------------- synthetic panels
def _base_bs(n_days=42, seed=0):
    """Synthetic structural panel: 3 assets over n_days UTC days of 288 bars.

    log_return, pos_range in [0,1], oi_spread per day, plus the tod/day index
    arrays that build_series would have produced. Deterministic (seeded)."""
    n_bars = n_days * R.TOD_BARS_PER_DAY
    t = np.arange(n_bars)
    tod_idx = (t % R.TOD_BARS_PER_DAY).astype(np.int64)
    day_ord = (t // R.TOD_BARS_PER_DAY).astype(np.int64)
    rng = np.random.default_rng(seed)
    r = rng.normal(0.0, 1e-4, size=(3, n_bars))
    pos_range = np.clip(0.5 + rng.normal(0.0, 0.01, size=(3, n_bars)), 0.0, 1.0)
    oi_spread = rng.normal(0.0, 1e-4, size=(3, n_days))
    return {"log_return": r, "tod_idx": tod_idx, "day_ord": day_ord,
            "pos_range": pos_range, "oi_spread": oi_spread,
            "n_bars": n_bars, "n_days": n_days}


def _bs_absr(n_days=6):
    """absr panel: asset0 seasonally-RICH range (big |r| at last bar), asset2
    seasonally-CHEAP range (small |r| at last bar), with non-zero trailing
    dispersion so the vol-scaled z-score is well defined."""
    n_bars = n_days * R.TOD_BARS_PER_DAY
    t = np.arange(n_bars)
    tod_idx = (t % R.TOD_BARS_PER_DAY).astype(np.int64)
    day_ord = (t // R.TOD_BARS_PER_DAY).astype(np.int64)
    r = np.zeros((3, n_bars))
    for d in range(n_days):
        r[0, d * R.TOD_BARS_PER_DAY + 287] = 0.001 * (d + 1)
        r[2, d * R.TOD_BARS_PER_DAY + 287] = -0.001 * (d + 1)
    r[0, -1] = 0.05    # asset0 rich range shock at last bar
    r[2, -1] = 0.0     # asset2 cheap (no shock) at last bar
    pos_range = np.full((3, n_bars), 0.5)
    oi_spread = np.zeros((3, n_days))
    return {"log_return": r, "tod_idx": tod_idx, "day_ord": day_ord,
            "pos_range": pos_range, "oi_spread": oi_spread,
            "n_bars": n_bars, "n_days": n_days}


def _bs_posrange(n_days=6):
    """pos_range panel: asset0 rich (near day high) at last bar, asset2 cheap
    (near day low) at last bar; trailing same-tod values ~0.5."""
    n_bars = n_days * R.TOD_BARS_PER_DAY
    t = np.arange(n_bars)
    tod_idx = (t % R.TOD_BARS_PER_DAY).astype(np.int64)
    day_ord = (t // R.TOD_BARS_PER_DAY).astype(np.int64)
    pos_range = np.full((3, n_bars), 0.5)
    for d in range(n_days):
        pos_range[0, d * R.TOD_BARS_PER_DAY + 287] = 0.5
        pos_range[2, d * R.TOD_BARS_PER_DAY + 287] = 0.5
    pos_range[0, -1] = 0.9    # asset0 near running high -> seasonally rich
    pos_range[2, -1] = 0.1    # asset2 near running low -> seasonally cheap
    r = np.zeros((3, n_bars))
    oi_spread = np.zeros((3, n_days))
    return {"log_return": r, "tod_idx": tod_idx, "day_ord": day_ord,
            "pos_range": pos_range, "oi_spread": oi_spread,
            "n_bars": n_bars, "n_days": n_days}


def _bs_oi(n_days=7):
    """oi_spread panel: asset0 rich overnight-minus-intraday on day 5, asset2
    cheap on day 5; the signal at day 6 must reflect day 5 (previous day)."""
    n_bars = n_days * R.TOD_BARS_PER_DAY
    t = np.arange(n_bars)
    tod_idx = (t % R.TOD_BARS_PER_DAY).astype(np.int64)
    day_ord = (t // R.TOD_BARS_PER_DAY).astype(np.int64)
    oi_spread = np.zeros((3, n_days))
    oi_spread[0, 5] = 0.05
    oi_spread[2, 5] = -0.05
    r = np.zeros((3, n_bars))
    pos_range = np.full((3, n_bars), 0.5)
    return {"log_return": r, "tod_idx": tod_idx, "day_ord": day_ord,
            "pos_range": pos_range, "oi_spread": oi_spread,
            "n_bars": n_bars, "n_days": n_days}


# ---------------------------------------------------------------- signal builders
def test_build_score_all_signals_shapes_and_warmup_nan():
    bs = _base_bs()
    for sig in R.SIGNALS:
        for L in (3, 5):
            sc = R.build_score(bs, sig, L)
            assert sc.shape == (3, bs["n_bars"]), (sig, L)
            # warmup exists (first occurrences / first L days are NaN)
            assert np.isnan(sc).any(), (sig, L)
            # finite somewhere past warmup
            assert np.isfinite(sc[:, -1]).any(), (sig, L)


def test_range_dev_rich_short_cheap_long():
    bs = _bs_absr()
    sc = R.build_score(bs, "range_dev", 2)
    col = sc[:, -1]
    assert np.isfinite(col[0]) and np.isfinite(col[2])
    # asset0 seasonally rich range -> score<0 (short); asset2 cheap -> score>0 (long)
    assert col[0] < 0.0 < col[2], col


def test_vol_z_rich_short_cheap_long():
    bs = _bs_absr()
    sc = R.build_score(bs, "vol_z", 2)
    col = sc[:, -1]
    assert np.isfinite(col[0]) and np.isfinite(col[2])
    assert col[0] < 0.0 < col[2], col


def test_ewm_dev_rich_short_cheap_long():
    bs = _bs_absr()
    sc = R.build_score(bs, "ewm_dev", 2)
    col = sc[:, -1]
    assert np.isfinite(col[0]) and np.isfinite(col[2])
    assert col[0] < 0.0 < col[2], col


def test_brk_dev_rich_short_cheap_long():
    bs = _bs_posrange()
    sc = R.build_score(bs, "brk_dev", 2)
    col = sc[:, -1]
    assert np.isfinite(col[0]) and np.isfinite(col[2])
    # asset0 near running high -> score<0 (short); asset2 near low -> score>0 (long)
    assert col[0] < 0.0 < col[2], col


def test_oi_dev_rich_short_cheap_long_and_causal():
    bs = _bs_oi()
    L = 2
    sc = R.build_score(bs, "oi_dev", L)
    day6 = bs["day_ord"] == 6
    col = sc[:, day6][:, 0]
    assert np.isfinite(col[0]) and np.isfinite(col[2])
    # day-5 oi_spread: asset0 rich -> score<0; asset2 cheap -> score>0 at day 6
    assert col[0] < 0.0 < col[2], col

    # causality: mutating the LAST day's oi_spread (day 6) must not change any
    # oi_dev value (there is no day 7 to consume it)
    bs2 = {k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in bs.items()}
    bs2["oi_spread"][:, 6] = 999.0
    sc2 = R.build_score(bs2, "oi_dev", L)
    assert np.allclose(np.nan_to_num(sc, nan=-12345.0), np.nan_to_num(sc2, nan=-12345.0))


def test_oi_dev_uses_previous_completed_day_not_current():
    """oi_dev at day k must equal -(oi_spread[k-1]-trailing_mean_{k-1}) and be
    independent of oi_spread[k]."""
    bs = _bs_oi()
    L = 2
    sc = R.build_score(bs, "oi_dev", L)
    day6 = bs["day_ord"] == 6
    # recompute expected from day 5 (previous day)
    oi = bs["oi_spread"]
    # trailing mean up to day5 for asset0 = mean(day4,day5)=mean(0,0.05)=0.025
    exp0 = -(oi[0, 5] - 0.025)
    assert np.isclose(sc[0, day6][0], exp0), (sc[0, day6][0], exp0)


def test_signals_are_distinct():
    bs = _base_bs(seed=1)
    L = 5
    s_range = R.build_score(bs, "range_dev", L)
    s_volz = R.build_score(bs, "vol_z", L)
    s_ewm = R.build_score(bs, "ewm_dev", L)
    s_brk = R.build_score(bs, "brk_dev", L)
    # range_dev (raw dev) vs vol_z (std-scaled) differ
    assert not np.allclose(np.nan_to_num(s_range, nan=0.0), np.nan_to_num(s_volz, nan=0.0))
    # range_dev vs ewm_dev (mean vs ewm baseline) differ
    assert not np.allclose(np.nan_to_num(s_range, nan=0.0), np.nan_to_num(s_ewm, nan=0.0))
    # brk_dev (position-in-range) is a different source than range_dev
    assert not np.allclose(np.nan_to_num(s_range, nan=0.0), np.nan_to_num(s_brk, nan=0.0))


# ---------------------------------------------------------------- grid size
def test_n_trials_is_1440_and_full_grid():
    assert R.N_TRIALS == 1440
    assert R.SIGNALS == ("range_dev", "brk_dev", "oi_dev", "vol_z", "ewm_dev")
    assert R.LOOKBACKS == (30, 60, 90)
    assert R.REBALANCES == (6, 12, 48)
    assert R.FEES == (1, 5, 10, 20)
    assert R.SLIPS == (1, 2, 5, 10)
    assert R.COST_VARIANTS == ("symmetric", "perp_heavy")
    assert R.ATTR_BUCKETS == ("range_dev", "brk_dev", "oi_dev", "vol_z", "ewm_dev", "placebo_noise")


# ---------------------------------------------------------------- artifact schema
def _load(name):
    candidates = sorted(
        p for p in (ROOT / "reports").glob(f"campaign321_{name}_*.json")
        if not p.name.endswith(".full.json")
    )
    assert candidates, f"missing artifact campaign321_{name}_*.json"
    p = candidates[-1]
    return json.loads(p.read_text())


def test_artifacts_exist_with_real_data_flags():
    for name in ("oos_sweep", "tradable_edge_registry", "summary", "verdict", "binding_constraint"):
        obj = _load(name)
        assert obj.get("real_data_only") is True, name
        assert obj.get("fabricated_data") is False, name
        assert obj.get("executed_fills") is False, name
        assert obj.get("campaign") == 321, name


def test_verdict_binding_and_counts():
    v = _load("verdict")
    assert v["verdict"] in ("RETRACTED", "EDGE_PROVEN")
    assert v["edge_proven"] in (True, False)
    if not v["edge_proven"]:
        assert v["binding_constraint"] is not None
    assert v["n_deterministic_edge"] >= 0
    for key in ("oos_sweep_sha256", "registry_sha256", "summary_sha256"):
        assert isinstance(v[key], str) and len(v[key]) == 64


def test_sweep_has_all_1440_configs_and_gates():
    sw = _load("oos_sweep")
    assert sw["config"]["n_trials"] == 1440
    assert len(sw["results"]) == 1440
    for r in sw["results"]:
        for k in ("p_value", "p_holm", "p_bh", "holm_reject", "bh_reject",
                  "signal", "lookback", "rebalance", "fee_bps", "slippage_bps",
                  "cost_variant", "edge_proven"):
            assert k in r, (k, r)
    mt = sw["gates"]["multiple_testing"]
    assert mt["holm_alpha"] == 0.05 and mt["bh_alpha"] == 0.05
    assert mt["n_survive_both"] >= 0
    attr = sw["gates"]["attribution"]
    assert set(attr["shares"].keys()) == {
        "range_dev", "brk_dev", "oi_dev", "vol_z", "ewm_dev", "placebo_noise"}
    assert attr["dominant"] in ("range_dev", "brk_dev", "oi_dev", "vol_z", "ewm_dev", "placebo_noise")


def test_registry_and_binding_constraint_consistent_with_verdict():
    v = _load("verdict")
    reg = _load("tradable_edge_registry")
    bc = _load("binding_constraint")
    assert reg["verdict"] == v["verdict"]
    assert bc["binding_constraint"] == v["binding_constraint"]
    assert bc["verdict"] == v["verdict"]


def test_summary_reports_attribution_shares():
    s = _load("summary")
    cfg = s["config"]
    assert cfg["cost_variants"] == ["symmetric", "perp_heavy"]
    assert len(cfg["fee_bps"]) == 4 and len(cfg["slippage_bps"]) == 4
    assert cfg["signals"] == ["range_dev", "brk_dev", "oi_dev", "vol_z", "ewm_dev"]
    attr = s["gates"]["attribution"]
    assert "shares" in attr and "dominant_share" in attr and "attribution_ok" in attr