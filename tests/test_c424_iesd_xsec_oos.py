"""Tests for C424 runner (scripts/run_c424_iesd_xsec_oos.py): pure-function
tests on synthetic arrays (including a brute-force equality test for the
vectorized IESD inter-extremum-spacing kernel vs the per-window explicit
extrema + spacing + entropy reference) plus schema/flag validation of emitted
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

import run_c424_iesd_xsec_oos as R  # noqa: E402


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
    for pb in ("ies_mean_spacing_placebo", "ies_spacing_ent_placebo"):
        assert pb in R.SIGNALS
    for real in ("ies_mean_spacing_dev", "ies_spacing_ent_dev"):
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


def test_wf_splits_count_2023_2025():
    idx = pd.date_range("2023-01-01", "2026-01-01", freq="5min", tz="UTC")
    splits = R.wf_splits_by_month(idx, 12, 3, 3)
    assert len(splits) == 8


# ---------------------------------------------------------------- IESD kernel (brute-force equality)
def test_iesd_matches_brute_force():
    """The vectorized IESD kernel MUST equal the brute-force reference
    (per-window loop with explicit extrema + spacing + entropy). Compared
    with maxdiff < 1e-12 and matching NaN patterns."""
    rng = np.random.default_rng(20261288)
    n_assets, n_bars = 5, 4000
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    fast = R.compute_iesd_metrics(close, W=R.IESD_W)
    brute = R._iesd_bruteforce(close, W=R.IESD_W)
    for key in ("ies_mean_spacing", "ies_spacing_ent"):
        fv, fb = fast[key], brute[key]
        fin = np.isfinite(fv) & np.isfinite(fb)
        assert fin.sum() > 0, f"{key}: no finite overlapping points"
        assert np.array_equal(np.isnan(fv), np.isnan(fb)), f"{key}: NaN pattern mismatch"
        maxdiff = float(np.max(np.abs(fv[fin] - fb[fin]))) if fin.sum() else 0.0
        assert maxdiff < 1e-12, f"{key}: maxdiff={maxdiff} >= 1e-12"


def test_iesd_matches_brute_force_10_assets():
    """Brute-force equality with the full 10-asset panel (the real universe width)."""
    rng = np.random.default_rng(4244)
    n_assets, n_bars = 10, 1500
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    fast = R.compute_iesd_metrics(close, W=R.IESD_W)
    brute = R._iesd_bruteforce(close, W=R.IESD_W)
    for key in ("ies_mean_spacing", "ies_spacing_ent"):
        fv, fb = fast[key], brute[key]
        fin = np.isfinite(fv) & np.isfinite(fb)
        assert fin.sum() > 0, key
        maxdiff = float(np.max(np.abs(fv[fin] - fb[fin])))
        assert maxdiff < 1e-12, f"iesd_{key}: maxdiff={maxdiff}"


def test_iesd_matches_brute_force_with_nan():
    """Brute-force equality when the panel contains NaNs (global across assets)."""
    rng = np.random.default_rng(99)
    n_assets, n_bars = 4, 1200
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    close[1, 400] = np.nan
    close[2, 401] = np.nan
    fast = R.compute_iesd_metrics(close, W=R.IESD_W)
    brute = R._iesd_bruteforce(close, W=R.IESD_W)
    for key in ("ies_mean_spacing", "ies_spacing_ent"):
        fv, fb = fast[key], brute[key]
        fin = np.isfinite(fv) & np.isfinite(fb)
        assert np.array_equal(np.isnan(fv), np.isnan(fb)), f"{key}: NaN mismatch"
        maxdiff = float(np.max(np.abs(fv[fin] - fb[fin]))) if fin.sum() else 0.0
        assert maxdiff < 1e-12, f"{key}: maxdiff={maxdiff}"


def test_iesd_defined_after_window_nan_before():
    rng = np.random.default_rng(3)
    n_assets, n_bars = 3, 600
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.005, axis=1))
    W = R.IESD_W
    m = R.compute_iesd_metrics(close, W=W)
    for key in ("ies_mean_spacing", "ies_spacing_ent"):
        assert np.isnan(m[key][:, :W]).all(), key
        assert np.isfinite(m[key][:, W:]).any(), key


def test_iesd_non_finite_close_propagates():
    """A non-finite close in any asset at a bar -> NaN for all IESD outputs
    in every window covering that bar (global-across-assets finiteness gate)."""
    rng = np.random.default_rng(9)
    n_assets, n_bars = 4, 600
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.005, axis=1))
    close[0, 300] = np.inf
    W = R.IESD_W
    m = R.compute_iesd_metrics(close, W=W)
    for t in range(300, min(300 + W, n_bars)):
        for key in ("ies_mean_spacing", "ies_spacing_ent"):
            assert np.isnan(m[key][:, t]).all(), f"iesd_{key} t={t} should be NaN"
    for t in range(W, 300):
        for key in ("ies_mean_spacing", "ies_spacing_ent"):
            assert np.isfinite(m[key][:, t]).any(), f"iesd_{key} t={t} should be finite"


def test_iesd_params():
    assert R.IESD_W == 256


def test_iesd_mean_spacing_range():
    """ies_mean_spacing >= 1 where defined (at least one spacing gap of >=1 bar)."""
    rng = np.random.default_rng(2026)
    n_assets, n_bars = 2, 1000
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    W = R.IESD_W
    m = R.compute_iesd_metrics(close, W=W)
    fin = np.isfinite(m["ies_mean_spacing"])
    assert (m["ies_mean_spacing"][fin] >= 1.0 - 1e-12).all()


def test_iesd_spacing_ent_range():
    """ies_spacing_ent >= 0 where defined (Shannon entropy)."""
    rng = np.random.default_rng(2027)
    n_assets, n_bars = 2, 1000
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    W = R.IESD_W
    m = R.compute_iesd_metrics(close, W=W)
    fine = np.isfinite(m["ies_spacing_ent"])
    assert (m["ies_spacing_ent"][fine] >= -1e-12).all()


def test_reference_config_matches_pre_registered_spec():
    assert R.ATTR_REPRESENTATIVES == {
        "ies_mean_spacing_dev": "ies_mean_spacing_dev",
        "ies_spacing_ent_dev": "ies_spacing_ent_dev",
    }
    assert R.PLACEBO_SEED == 20261288
    assert R.STABILITY_MIN_SIGN_CONSISTENCY == 0.70
    assert R.STABILITY_MIN_SHARPE_CORR == 0.50
    assert R.DOMINANT_SHARE_MIN == 0.50
    assert R.TRAIN_M == 12 and R.TEST_M == 3 and R.ROLL_M == 3
    assert R.IESD_W == 256
    assert R.SIGNALS[0] == "ies_mean_spacing_dev"


# ---------------------------------------------------------------- phase-randomized surrogate
def test_phase_randomized_surrogate_same_marginal_deterministic():
    rng = np.random.default_rng(0)
    x = rng.standard_normal(500) * 3.0 + 5.0
    s1 = R._phase_randomized_surrogate(x, R.PLACEBO_SEED)
    s2 = R._phase_randomized_surrogate(x, R.PLACEBO_SEED)
    assert np.array_equal(s1, s2)
    assert np.isclose(np.sort(s1[np.isfinite(s1)]), np.sort(x[np.isfinite(x)]), equal_nan=True).all()


# ---------------------------------------------------------------- build_underlying / build_scores
def _synthetic_bs(n_assets=3, n_days=8, seed=1):
    rng = np.random.default_rng(seed)
    T = 288
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
    assert set(series.keys()) == {"ies_mean_spacing", "ies_spacing_ent"}
    for k in ("ies_mean_spacing", "ies_spacing_ent"):
        assert series[k].shape == (bs["n_assets"], bs["n_bars"])


def test_build_scores_signals_lookbacks_causal():
    bs = _synthetic_bs()
    series = R.build_underlying(bs)
    scores = R.build_scores(series, bs["bucket"])
    for sig in R.SIGNALS:
        for L in R.LOOKBACKS:
            assert (sig, L) in scores
            assert scores[(sig, L)].shape == (bs["n_assets"], bs["n_bars"])
    for key, sc in scores.items():
        assert np.isnan(sc[:, 0]).all(), key


# ---------------------------------------------------------------- kernel distinctness guards
def test_iesd_kernel_not_degenerate():
    """Rewrite guard: IESD metrics are not degenerate (not allclose to 0 where
    defined)."""
    rng = np.random.default_rng(55)
    n_assets, n_bars = 5, 1600
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    W = R.IESD_W
    mm = R.compute_iesd_metrics(close, W=W)
    for name in ("ies_mean_spacing", "ies_spacing_ent"):
        arr = mm[name]
        fin = np.isfinite(arr)
        assert fin.sum() > 0, f"iesd_{name}: no finite values"
        assert not np.allclose(arr[fin], 0.0, atol=1e-12), f"iesd_{name} collapses to 0"


# ---- inline prior-family reference statistics (distinctness guards)
def _signchop_style_stat(close, W):
    """Inline C344-style statistic: sign-change / chop rate of the return sign
    sequence over the window — sign flips of the return sign, NOT inter-extremum
    spacing distribution."""
    X = np.diff(np.log(close), axis=1)
    n_assets, n = X.shape
    out = np.full((n_assets, n), np.nan)
    for t in range(W, n):
        span = X[:, t - W + 1:t + 1]
        if not np.isfinite(span).all():
            continue
        for i in range(n_assets):
            s = np.sign(span[i])
            out[i, t] = float(np.mean(s[1:] != s[:-1])) if W > 1 else np.nan
    return out


def _signrun_style_stat(close, W):
    """Inline C374 SIGNRUN-style statistic: max run share / mean run length of
    signed runs — a single max/mean summary, NOT inter-extremum spacing entropy."""
    X = np.diff(np.log(close), axis=1)
    n_assets, n = X.shape
    out = np.full((n_assets, n), np.nan)
    for t in range(W, n):
        span = X[:, t - W + 1:t + 1]
        if not np.isfinite(span).all():
            continue
        for i in range(n_assets):
            s = np.sign(span[i])
            s2 = s[s != 0]
            if len(s2) < 2:
                continue
            change = s2[1:] != s2[:-1]
            starts = np.concatenate([[0], np.nonzero(change)[0] + 1])
            lens = np.diff(np.concatenate([starts, [len(s2)]]))
            out[i, t] = float(lens.max() / lens.mean()) if lens.mean() > 0 else np.nan
    return out


def _zcrpath_style_stat(close, W):
    """Inline C422 ZCRPATH-style statistic: zero-crossing rate of the
    cumulative-return path — crossings of cumsum(X), NOT inter-extremum spacing."""
    X = np.diff(np.log(close), axis=1)
    n_assets, n = X.shape
    out = np.full((n_assets, n), np.nan)
    for t in range(W, n):
        span = X[:, t - W + 1:t + 1]
        if not np.isfinite(span).all():
            continue
        for i in range(n_assets):
            x = span[i]
            C = np.cumsum(x)
            chg = C[:-1] * C[1:] < 0
            out[i, t] = float(chg.sum() / (W - 1))
    return out


def _runlen_style_stat(close, W):
    """Inline C423 RUNLEN-style statistic: run-length distribution entropy of
    consecutive same-sign returns — full run-length entropy, NOT inter-extremum
    spacing between local extrema of the price path."""
    X = np.diff(np.log(close), axis=1)
    n_assets, n = X.shape
    out = np.full((n_assets, n), np.nan)
    for t in range(W, n):
        span = X[:, t - W + 1:t + 1]
        if not np.isfinite(span).all():
            continue
        for i in range(n_assets):
            x = span[i]
            s = np.sign(x)
            s2 = s[s != 0.0]
            if len(s2) < 2:
                continue
            change = s2[1:] != s2[:-1]
            starts = np.concatenate([[0], np.nonzero(change)[0] + 1])
            lens = np.diff(np.concatenate([starts, [len(s2)]])).astype(float)
            signs_r = s2[starts]
            total = float(lens.sum())
            p = lens / total
            out[i, t] = float(-(p * np.log(p)).sum())
    return out


def _assert_distinct(sa, ref, name):
    fin = np.isfinite(sa) & np.isfinite(ref)
    assert fin.sum() > 0, name
    assert not np.allclose(sa[fin], ref[fin], atol=1e-6), f"IESD degenerates to {name}"


def test_iesd_kernel_distinct_from_signchop():
    """C344 sign-change/chop rate: legitimate distinctness-guard ref
    (sign flips of the return sign vs inter-extremum spacing distribution)."""
    rng = np.random.default_rng(214)
    n_assets, n_bars = 5, 1200
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    W = R.IESD_W
    mm = R.compute_iesd_metrics(close, W=W)
    sa = mm["ies_mean_spacing"][0, W:]
    ref = _signchop_style_stat(close, W)[0, W - 1:]
    _assert_distinct(sa, ref, "SIGNCHOP")


def test_iesd_kernel_distinct_from_signrun():
    """C374 SIGNRUN (max run share / mean run length): legitimate
    distinctness-guard ref (single max/mean summary vs inter-extremum spacing entropy)."""
    rng = np.random.default_rng(217)
    n_assets, n_bars = 5, 1200
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    W = R.IESD_W
    mm = R.compute_iesd_metrics(close, W=W)
    sa = mm["ies_mean_spacing"][0, W:]
    ref = _signrun_style_stat(close, W)[0, W - 1:]
    _assert_distinct(sa, ref, "SIGNRUN")


def test_iesd_kernel_distinct_from_zcrpath():
    """C422 ZCRPATH (zero-crossing rate of cumulative-return path): legitimate
    distinctness-guard ref (cumulative-path crossings vs inter-extremum spacing)."""
    rng = np.random.default_rng(219)
    n_assets, n_bars = 5, 1200
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    W = R.IESD_W
    mm = R.compute_iesd_metrics(close, W=W)
    sa = mm["ies_mean_spacing"][0, W:]
    ref = _zcrpath_style_stat(close, W)[0, W - 1:]
    _assert_distinct(sa, ref, "ZCRPATH")


def test_iesd_kernel_distinct_from_runlen():
    """C423 RUNLEN (run-length distribution entropy of consecutive return signs):
    legitimate distinctness-guard ref (run-length entropy vs inter-extremum spacing
    between local extrema of the price path)."""
    rng = np.random.default_rng(220)
    n_assets, n_bars = 5, 1200
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    W = R.IESD_W
    mm = R.compute_iesd_metrics(close, W=W)
    sa = mm["ies_mean_spacing"][0, W:]
    ref = _runlen_style_stat(close, W)[0, W - 1:]
    _assert_distinct(sa, ref, "RUNLEN")


# ---------------------------------------------------------------- guard tests (rewrite guards)
def test_artifact_campaign_is_424():
    """Rewrite guard: every emitted artifact self-identifies campaign 424."""
    for part in ("verdict", "summary", "registry", "oos_sweep"):
        files = sorted((ROOT / "reports").glob(f"campaign424_{part}_*.json"))
        files = [f for f in files if ".full." not in f.name]
        if not files:
            continue
        obj = json.loads(files[-1].read_text())
        assert obj["campaign"] == 424, f"{part} artifact campaign != 424: {obj.get('campaign')}"


def test_mandate_contains_iesd():
    """Rewrite guard: the C424 mandate names the IESD inter-extremum-spacing
    family (never prior families)."""
    p = sorted((ROOT / "reports").glob("campaign424_oos_sweep_*.json"))
    p = [f for f in p if ".full." not in f.name]
    if not p:
        return
    mandate = json.loads(p[-1].read_text())["mandate"]
    assert "IESD" in mandate, "mandate missing IESD"
    assert "ies_mean_spacing" in mandate, "mandate missing ies_mean_spacing"
    assert "ies_spacing_ent" in mandate, "mandate missing ies_spacing_ent"
    for bad in ("RUNLEN", "RUN-LENGTH", "runlen_ent", "runlen_asym",
                "ZCRPATH", "ZERO-CROSSING", "CUMULATIVE-RETURN", "SIGNCOH",
                "SIGN-SEQUENCE", "AUTOCORRELATION", "PEARSON",
                "SPECTRAL COHERENCE", "WELCH", "CROSS-SPECTRUM", "ACOVK",
                "AUTOCOVARIANCE", "SIGNCHOP", "TURNINGPT", "TURNING POINT",
                "KER", "EFFICIENCY RATIO", "PSLOPE", "TREND-SLOPE",
                "QREG", "QUANTILE-REGRESSION", "QUANTILE REGRESSION",
                "SCOH", "COH_MEAN", "COH_LOW"):
        assert bad not in mandate, f"mandate must not reference {bad} (prior campaign)"


def test_placebo_seed_is_20261288():
    assert R.PLACEBO_SEED == 20261288


def test_placebo_seed_unique_not_reserved():
    """Rewrite guard: C424 placebo seed must not collide with reserved seeds
    used by prior campaigns (20261224..20261287)."""
    assert not (20261224 <= R.PLACEBO_SEED <= 20261287), \
        "placebo seed must be outside 20261224-20261287"


# ---------------------------------------------------------------- real artifacts schema (if present)
def _find_latest(prefix: str):
    files = sorted((ROOT / "reports").glob(f"campaign424_{prefix}_*.json"))
    files = [f for f in files if ".full." not in f.name]
    return files[-1] if files else None


def test_artifacts_if_present_have_required_flags():
    p = _find_latest("verdict")
    if p is None:
        return
    v = json.loads(p.read_text())
    assert v["campaign"] == 424
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
    assert sw["config"]["iesd_params"]["window_W"] == 256


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
    test_iesd_matches_brute_force()
    test_iesd_matches_brute_force_10_assets()
    test_iesd_matches_brute_force_with_nan()
    test_iesd_defined_after_window_nan_before()
    test_iesd_non_finite_close_propagates()
    test_iesd_params()
    test_iesd_mean_spacing_range()
    test_iesd_spacing_ent_range()
    test_reference_config_matches_pre_registered_spec()
    test_phase_randomized_surrogate_same_marginal_deterministic()
    test_build_underlying_shapes_and_keys()
    test_build_scores_signals_lookbacks_causal()
    test_iesd_kernel_not_degenerate()
    test_iesd_kernel_distinct_from_signchop()
    test_iesd_kernel_distinct_from_signrun()
    test_iesd_kernel_distinct_from_zcrpath()
    test_iesd_kernel_distinct_from_runlen()
    test_artifact_campaign_is_424()
    test_mandate_contains_iesd()
    test_placebo_seed_is_20261288()
    test_placebo_seed_unique_not_reserved()
    test_artifacts_if_present_have_required_flags()
    print("All C424 IESD runner tests passed")
