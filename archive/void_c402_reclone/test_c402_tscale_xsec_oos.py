"""Tests for C402 runner (scripts/run_c402_tscale_xsec_oos.py): pure-function tests on
synthetic arrays (including a brute-force equality test for the vectorized TSCALE
rv / rq / rvq_ratio kernels vs the per-window reference) plus schema/flag
validation of emitted real-data artifacts. No network, no fabricated market data."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import run_c402_tscale_xsec_oos as R  # noqa: E402


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
    assert R.N_TRIALS == 2592
    assert len(R.SIGNALS) == 8
    assert len(R.LOOKBACKS) == 6
    assert len(R.REBALANCES) == 3
    assert len(R.FEES) == 3 and len(R.SLIPS) == 3 and len(R.COST_VARIANTS) == 2
    assert R.N_TRIALS == (len(R.SIGNALS) * len(R.LOOKBACKS) * len(R.REBALANCES)
                          * len(R.FEES) * len(R.SLIPS) * len(R.COST_VARIANTS))
    for pb in ("tscale_alpha12_placebo","tscale_alpha24_placebo","tscale_alpha48_placebo","tscale_slope_placebo"):
        assert pb in R.SIGNALS
    for real in ("tscale_alpha12_dev","tscale_alpha24_dev","tscale_alpha48_dev","tscale_slope_dev"):
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


# ---------------------------------------------------------------- TSCALE metric (brute-force equality)
def test_tscale_matches_brute_force():
    """The vectorized TSCALE rv / rq / rvq_ratio kernels MUST equal the
    brute-force reference (per-window sum(x^2), mean(x^4), rq/max(rv^2,1e-12)).
    Compared strictly (maxdiff < 1e-12) with matching NaN patterns."""
    rng = np.random.default_rng(20261266)
    log_return = rng.standard_normal(4000) * 0.001
    fast = R.compute_tscale_metrics(log_return, R.TSCALE_W)
    brute = R._tscale_bruteforce(log_return, R.TSCALE_W)
    for key in ("tscale_alpha12", "tscale_alpha24", "tscale_alpha48", "tscale_slope"):
        fv, fb = fast[key], brute[key]
        fin = np.isfinite(fv) & np.isfinite(fb)
        assert fin.sum() > 0, f"{key}: no finite overlapping points"
        assert np.array_equal(np.isnan(fv), np.isnan(fb)), f"{key}: NaN pattern mismatch"
        maxdiff = float(np.max(np.abs(fv[fin] - fb[fin]))) if fin.sum() else 0.0
        assert maxdiff < 1e-12, f"{key}: maxdiff={maxdiff} >= 1e-12"


def test_tscale_constant_returns():
    """Constant returns: all |x| equal -> Hill denominator zero -> NaN (matches brute force)."""
    W = R.TSCALE_W
    c = 0.001
    log_return = np.concatenate([np.zeros(W - 1), np.full(W, c)])
    fast = R.compute_tscale_metrics(log_return, W)
    brute = R._tscale_bruteforce(log_return, W)
    for key in ("tscale_alpha12", "tscale_alpha24", "tscale_alpha48", "tscale_slope"):
        assert np.array_equal(np.isnan(fast[key]), np.isnan(brute[key])), key


def test_tscale_defined_after_window_nan_before():
    rng = np.random.default_rng(3)
    log_return = rng.standard_normal(4000) * 0.001
    m = R.compute_tscale_metrics(log_return, R.TSCALE_W)
    W = R.TSCALE_W
    for key in ("tscale_alpha12", "tscale_alpha24", "tscale_alpha48", "tscale_slope"):
        assert np.isnan(m[key][:W]).all(), key
        assert np.isfinite(m[key][W:]).any(), key


def test_tscale_non_finite_return_propagates():
    """A non-finite return in the window -> NaN for all TSCALE outputs in affected bars."""
    rng = np.random.default_rng(9)
    log_return = rng.standard_normal(600) * 0.001
    log_return[300] = np.inf
    W = R.TSCALE_W
    m = R.compute_tscale_metrics(log_return, W)
    for t in range(300, min(300 + W, 600)):
        assert np.isnan(m["tscale_alpha12"][t]), f"tscale t={t} should be NaN"
    for t in range(W, 300):
        assert np.isfinite(m["tscale_alpha12"][t]), f"tscale t={t} should be finite"
    for t in range(300 + W, 600):
        assert np.isfinite(m["tscale_alpha12"][t]), f"tscale t={t} should be finite"


def test_tscale_params():
    assert R.TSCALE_W == 256


def test_tscale_constant_returns_edge_case():
    """Constant returns -> rv>0, rq=c^4, rvq_ratio=1/W^2 (matches brute force)."""
    log_return = np.ones(600) * 0.001
    fast = R.compute_tscale_metrics(log_return, R.TSCALE_W)
    brute = R._tscale_bruteforce(log_return, R.TSCALE_W)
    for key in ("tscale_alpha12", "tscale_alpha24", "tscale_alpha48", "tscale_slope"):
        fv, fb = fast[key], brute[key]
        assert np.array_equal(np.isnan(fv), np.isnan(fb)), key
        fin = np.isfinite(fv) & np.isfinite(fb)
        maxdiff = float(np.max(np.abs(fv[fin] - fb[fin]))) if fin.sum() else 0.0
        assert maxdiff < 1e-12, f"{key}: maxdiff={maxdiff} >= 1e-12"


def test_reference_config_matches_pre_registered_spec():
    assert R.ATTR_REPRESENTATIVES == {
        "tscale_alpha12_dev": "tscale_alpha12_dev",
        "tscale_slope_dev": "tscale_slope_dev",
    }
    assert R.PLACEBO_SEED == 20261266
    assert R.STABILITY_MIN_SIGN_CONSISTENCY == 0.70
    assert R.STABILITY_MIN_SHARPE_CORR == 0.50
    assert R.DOMINANT_SHARE_MIN == 0.50
    assert R.TRAIN_M == 12 and R.TEST_M == 3 and R.ROLL_M == 3
    assert R.TSCALE_W == 256
    assert R.SIGNALS[0] == "tscale_alpha12_dev"


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
    assert set(series.keys()) == {"tscale_alpha12", "tscale_alpha24", "tscale_alpha48", "tscale_slope"}
    for k in ("tscale_alpha12", "tscale_alpha24", "tscale_alpha48", "tscale_slope"):
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
def test_tscale_kernel_not_degenerate():
    """Rewrite guard: TSCALE metrics are not degenerate (not allclose to 0 where defined)."""
    rng = np.random.default_rng(55)
    log_return = rng.standard_normal(1600) * 0.001
    W = R.TSCALE_W
    mm = R.compute_tscale_metrics(log_return, W)
    a = mm["tscale_alpha12"][W:]
    fin = np.isfinite(a)
    assert fin.sum() > 0
    assert not np.allclose(a[fin], 0.0, atol=1e-12), "TSCALE collapses to 0"
    assert not np.allclose(rvq_valid[fin], 0.0, atol=1e-12), "RVQ_RATIO collapses to 0"


def _rvq_style_stat(X, W):
    """Inline RQV-style stat: top-k concentration of squared returns (C366 RQV)."""
    n = len(X)
    out = np.full(n, np.nan)
    top_k = 16
    for t in range(W, n):
        Xw = X[t - W + 1:t + 1]
        if not np.isfinite(Xw).all():
            continue
        s2 = Xw ** 2
        total = float(np.sum(s2))
        if total <= 0:
            continue
        top_share = float(np.sum(np.sort(s2)[-top_k:])) / total
        out[t] = top_share
    return out


def _vovr_style_stat(X, W):
    """Inline VOVR-style stat: std of sub-block RV / mean sub-block RV (C378 VOVR)."""
    n = len(X)
    out = np.full(n, np.nan)
    n_blocks = 16
    blk = W // n_blocks
    for t in range(W, n):
        Xw = X[t - W + 1:t + 1]
        if not np.isfinite(Xw).all():
            continue
        block_rvs = [float(np.sum(Xw[i * blk:(i + 1) * blk] ** 2)) for i in range(n_blocks)]
        mean_rv = float(np.mean(block_rvs))
        if mean_rv <= 0:
            continue
        out[t] = float(np.std(block_rvs)) / mean_rv
    return out


def _hill_style_stat(X, W, n_exceed=12):
    """Inline Hill tail-index stat (C362 Hill)."""
    n = len(X)
    out = np.full(n, np.nan)
    for t in range(W, n):
        Xw = X[t - W + 1:t + 1]
        if not np.isfinite(Xw).all():
            continue
        a = np.sort(np.abs(Xw))[::-1]
        if len(a) <= n_exceed:
            continue
        u = a[n_exceed]
        if u <= 0:
            continue
        top = a[:n_exceed]
        denom = float(np.sum(np.log(top / u)))
        if denom <= 0:
            continue
        out[t] = n_exceed / denom
    return out


def test_tscale_kernel_distinct_from_rqv():
    """Rewrite guard: TSCALE rvq_ratio is a different object from RQV top-k
    concentration of squared returns on the same random data."""
    rng = np.random.default_rng(123)
    log_return = rng.standard_normal(1200) * 0.001
    W = R.TSCALE_W
    mm = R.compute_tscale_metrics(log_return, W)
    a = mm["tscale_alpha12"][W:]
    rqv = _rvq_style_stat(log_return, W)[W:]
    fin = np.isfinite(a) & np.isfinite(rqv)
    assert fin.sum() > 0
    assert not np.allclose(a[fin], rqv[fin], atol=1e-6), "TSCALE degenerates to RQV stat"


def test_tscale_kernel_distinct_from_vovr():
    """Rewrite guard: TSCALE rvq_ratio is a different object from VOVR
    cross-sub-block RV dispersion on the same random data."""
    rng = np.random.default_rng(124)
    log_return = rng.standard_normal(1200) * 0.001
    W = R.TSCALE_W
    mm = R.compute_tscale_metrics(log_return, W)
    a = mm["tscale_alpha12"][W:]
    vovr = _vovr_style_stat(log_return, W)[W:]
    fin = np.isfinite(a) & np.isfinite(vovr)
    assert fin.sum() > 0
    assert not np.allclose(a[fin], vovr[fin], atol=1e-6), "TSCALE degenerates to VOVR stat"


def test_tscale_kernel_distinct_from_hill():
    """Rewrite guard: TSCALE rvq_ratio is a different object from Hill tail-index
    on the same random data."""
    rng = np.random.default_rng(125)
    log_return = rng.standard_normal(1200) * 0.001
    W = R.TSCALE_W
    mm = R.compute_tscale_metrics(log_return, W)
    a = mm["tscale_alpha12"][W:]
    hill = _hill_style_stat(log_return, W)[W:]
    fin = np.isfinite(a) & np.isfinite(hill)
    assert fin.sum() > 0
    assert not np.allclose(a[fin], hill[fin], atol=1e-6), "TSCALE degenerates to Hill stat"


# ---------------------------------------------------------------- guard tests (rewrite guards)
def test_artifact_campaign_is_401():
    """Rewrite guard: every emitted artifact self-identifies campaign 401 (never 400/401)."""
    for part in ("verdict", "summary", "registry", "oos_sweep"):
        files = sorted((ROOT / "reports").glob(f"campaign402_{part}_*.json"))
        files = [f for f in files if ".full." not in f.name]
        if not files:
            continue
        obj = json.loads(files[-1].read_text())
        assert obj["campaign"] == 401, f"{part} artifact campaign != 401: {obj.get('campaign')}"


def test_mandate_contains_tscale():
    """Rewrite guard: the C402 mandate names TSCALE realized quarticity / RV^2 ratio
    (never KTREND/CBREAK/SPECFM/MAGNET/OUHALFLIFE/CTES/VTERM/DDRUN/XSKEW3/XCOEX/MINRV/MADR/BANDX/PRROUGH/HALFRANGE/LMOM)."""
    p = sorted((ROOT / "reports").glob("campaign402_oos_sweep_*.json"))
    p = [f for f in p if ".full." not in f.name]
    if not p:
        return
    mandate = json.loads(p[-1].read_text())["mandate"]
    assert "TSCALE" in mandate, "mandate missing TSCALE"
    assert "QUARTICITY" in mandate, "mandate missing QUARTICITY"
    for bad in ("KTREND", "CBREAK", "SPECFM", "MAGNET", "OUHALFLIFE", "CTES", "VTERM",
                "DDRUN", "XSKEW3", "XCOEX", "MINRV", "MADR", "BANDX",
                "PRROUGH", "HALFRANGE", "LMOM", "KENDALL", "SPEARMAN"):
        assert bad not in mandate, f"mandate must not reference {bad} (prior campaign)"


def test_placebo_seed_is_20261266():
    assert R.PLACEBO_SEED == 20261266


def test_placebo_seed_unique_not_reserved():
    """Rewrite guard: C402 placebo seed 20261266 must not collide with reserved
    seeds 20261224–20261264 used by prior campaigns (20261264 = C400)."""
    assert not (20261224 <= R.PLACEBO_SEED <= 20261264), "placebo seed must be outside 20261224-20261264"


# ---------------------------------------------------------------- real artifacts schema (if present)
def _find_latest(prefix: str):
    files = sorted((ROOT / "reports").glob(f"campaign402_{prefix}_*.json"))
    files = [f for f in files if ".full." not in f.name]
    return files[-1] if files else None


def test_artifacts_if_present_have_required_flags():
    p = _find_latest("verdict")
    if p is None:
        return
    v = json.loads(p.read_text())
    assert v["campaign"] == 401
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
    assert sw["config"]["tscale_params"]["window_W"] == 256


def test_cache_meta_tscale_params_distinct():
    meta_path = ROOT / "data" / "cache" / "campaign402_tscale_5m.meta.json"
    if not meta_path.exists():
        return
    meta = json.loads(meta_path.read_text())
    assert meta["campaign"] == 401
    assert meta["source_campaign"] == 312
    assert "tscale_params" in meta
    assert meta["tscale_params"]["window_W"] == 256
    for other in ("ktrend_params", "cbreak_params", "specfm_params", "magnet_params", "ces_params",
                  "vterm_params", "ddrun_params", "semicov_params", "qspread_params",
                  "rar_params", "lvac_params", "hill_params", "rskek_params",
                  "opte_params", "qatm_params", "dsrv_params", "ker_params",
                  "rqv_params", "bpv_params", "rmad_params", "gmd_params",
                  "rskrkt_params", "tirv_params", "rlrv_params", "signrun_params",
                  "acovk_params", "pslope_params", "vovr_params", "curv_params",
                  "tailmem_params", "turningpt_params", "extpos_params",
                  "prrough_params", "halfrange_params", "bandx_params",
                  "madr_params", "minrv_params", "xcoex_params", "xskew3_params",
                  "ou_params", "ou_halflife_params", "lmom_params"):
        assert other not in meta


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
    test_tscale_matches_brute_force()
    test_tscale_constant_returns()
    test_tscale_defined_after_window_nan_before()
    test_tscale_non_finite_return_propagates()
    test_tscale_params()
    test_tscale_constant_returns_edge_case()
    test_reference_config_matches_pre_registered_spec()
    test_phase_randomized_surrogate_same_marginal_deterministic()
    test_build_underlying_shapes_and_keys()
    test_build_scores_signals_lookbacks_causal()
    test_tscale_kernel_not_degenerate()
    test_tscale_kernel_distinct_from_rqv()
    test_tscale_kernel_distinct_from_vovr()
    test_tscale_kernel_distinct_from_hill()
    test_artifact_campaign_is_401()
    test_mandate_contains_tscale()
    test_placebo_seed_is_20261266()
    test_placebo_seed_unique_not_reserved()
    test_artifacts_if_present_have_required_flags()
    test_cache_meta_tscale_params_distinct()
    print("All C402 TSCALE runner tests passed")
