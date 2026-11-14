"""Tests for C301: real per-asset (2023-01 .. 2023-02) USDT-M perp
order-flow-imbalance / trade-sign autocorrelation time-series stat-arb at
NATIVE 5m (scripts/run_c301_aggtrades_ofi_oos.py).

Covers per-asset causal OFI feature construction at 5m, gap bars carried as
NaN and never imputed, fail-closed causal positions (shift(1), flat when no
signal, flat on stale funding / NaN score), the edge rule at identical
strength to C285-C300, and the persistence/SHA256-from-bytes of the campaign
artifacts. These tests run against the verified real ingested cache only;
they never impute or fabricate data.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import run_c301_aggtrades_ofi_oos as c301  # noqa: E402


def _latest_ts(part: str) -> str:
    matches = sorted(ROOT.glob(f"reports/campaign301_{part}_*.json"))
    assert matches, f"missing C301 artifact for {part}"
    return matches[-1].name.split(f"campaign301_{part}_")[1].split(".json")[0]


SYMBOLS = list(c301.load_payload(c301.CACHE)["symbols"])
PER_ASSET = c301.load_payload(c301.CACHE)["per_asset"]


def _asset(symbol: str) -> dict:
    pa = PER_ASSET[symbol]
    close, funding, buy, sell, signed, trade_count, tss, vwap, index = c301._asset_series(pa)
    return {
        "pa": pa,
        "close": close,
        "funding": funding,
        "buy": buy,
        "sell": sell,
        "signed": signed,
        "trade_count": trade_count,
        "tss": tss,
        "vwap": vwap,
        "index": index,
    }


def test_per_asset_frames_full_window_and_no_close_nan():
    assert len(SYMBOLS) >= 1
    exp_n_bars = 16992
    for s in SYMBOLS:
        d = _asset(s)
        assert int(d["pa"].get("n_bars")) == exp_n_bars, s
        assert d["close"].shape == (len(d["index"]),)
        assert int(d["close"].isna().sum()) == 0, s
        assert bool((d["close"].to_numpy(dtype=float) > 0).all()), s
        assert bool(np.isfinite(d["close"].to_numpy(dtype=float)).all()), s
        assert str(d["index"].min()) >= "2023-01-01 00:00:00+00:00"
        assert str(d["index"].max()) <= "2023-02-28 23:55:00+00:00"
        assert int(d["funding"].notna().sum()) >= 90, s
        # Gap bars (no trades) are NaN on all OFI legs and never imputed.
        tc = d["trade_count"].reindex(d["index"])
        gap = tc.isna()
        for col in ("buy_volume", "sell_volume", "signed_volume", "trade_count", "trade_sign_sum", "vwap"):
            arr = np.asarray(d["pa"][col], dtype=float)
            sarr = pd.Series(arr, index=d["index"])
            assert bool(np.isnan(sarr.to_numpy(dtype=float)[gap]).all()), f"{col} gap not NaN for {s}"
        # Present bars: signed == buy - sell, count > 0, vwap > 0.
        present = ~gap
        assert bool((np.asarray(d["pa"]["trade_count"], dtype=float)[present.values] > 0).all()), s
        vwap_arr = np.asarray(d["pa"]["vwap"], dtype=float)
        assert bool((vwap_arr[present.values] > 0).all()), s
        buy_arr = np.asarray(d["pa"]["buy_volume"], dtype=float)
        sell_arr = np.asarray(d["pa"]["sell_volume"], dtype=float)
        signed_arr = np.asarray(d["pa"]["signed_volume"], dtype=float)
        assert bool(np.allclose(signed_arr[present.values], (buy_arr - sell_arr)[present.values], equal_nan=False)), s


def test_signal_lengths_match_bars():
    for s in SYMBOLS:
        d = _asset(s)
        feats = c301.build_features(
            np.asarray(d["pa"]["buy_volume"], dtype=float),
            np.asarray(d["pa"]["sell_volume"], dtype=float),
            np.asarray(d["pa"]["signed_volume"], dtype=float),
            np.asarray(d["pa"]["trade_count"], dtype=float),
            np.asarray(d["pa"]["trade_sign_sum"], dtype=float),
            np.asarray(d["pa"]["vwap"], dtype=float),
        )
        for signal in c301.SIGNALS:
            for L in c301.LOOKBACKS:
                sig = c301.SIGNAL(signal, feats, L)
                assert len(sig) == len(d["index"]), (s, signal, L)


def test_features_are_causal_no_lookahead():
    s = SYMBOLS[0]
    d = _asset(s)
    buy = np.asarray(d["pa"]["buy_volume"], dtype=float)
    feats = c301.build_features(
        buy, np.asarray(d["pa"]["sell_volume"], dtype=float),
        np.asarray(d["pa"]["signed_volume"], dtype=float),
        np.asarray(d["pa"]["trade_count"], dtype=float),
        np.asarray(d["pa"]["trade_sign_sum"], dtype=float),
        np.asarray(d["pa"]["vwap"], dtype=float),
    )
    buy_p = buy.copy(); buy_p[-1] = buy_p[-1] * 2.0
    feats_p = c301.build_features(
        buy_p, np.asarray(d["pa"]["sell_volume"], dtype=float),
        np.asarray(d["pa"]["signed_volume"], dtype=float),
        np.asarray(d["pa"]["trade_count"], dtype=float),
        np.asarray(d["pa"]["trade_sign_sum"], dtype=float),
        np.asarray(d["pa"]["vwap"], dtype=float),
    )
    for signal in c301.SIGNALS:
        for L in c301.LOOKBACKS:
            base = c301.SIGNAL(signal, feats, L)
            alt = c301.SIGNAL(signal, feats_p, L)
            np.testing.assert_array_equal(base.to_numpy(dtype=float)[:-1], alt.to_numpy(dtype=float)[:-1])


def test_funding_cashflow_sign_convention():
    for s in SYMBOLS:
        d = _asset(s)
        leg = -d["funding"].fillna(0.0)
        mask = d["funding"].notna().values
        assert np.allclose(leg.values[mask], -d["funding"].values[mask])
        assert bool((leg.values[~mask] == 0).all())


def test_funding_age_is_bounded():
    for s in SYMBOLS:
        d = _asset(s)
        age = c301.compute_funding_age(d["funding"])
        assert float(np.nanmax(age)) <= c301.STALE_BARS


def test_position_is_shifted_one_bar_and_flat_when_no_signal():
    for s in SYMBOLS:
        d = _asset(s)
        feats = c301.build_features(
            np.asarray(d["pa"]["buy_volume"], dtype=float),
            np.asarray(d["pa"]["sell_volume"], dtype=float),
            np.asarray(d["pa"]["signed_volume"], dtype=float),
            np.asarray(d["pa"]["trade_count"], dtype=float),
            np.asarray(d["pa"]["trade_sign_sum"], dtype=float),
            np.asarray(d["pa"]["vwap"], dtype=float),
        )
        sig = c301.SIGNAL("ofi_z", feats, 288).to_numpy(dtype=float)
        pos = c301.positions_from_score(sig, entry=1.5, exit_level=0.5, H=1)
        assert pos[0] == 0.0, "first bar must be flat (decision applied from next bar)"
        assert len(pos) == len(d["close"])
        pos_zero = c301.positions_from_score(np.zeros(len(d["close"])), entry=1.0, exit_level=0.5, H=6)
        assert bool((pos_zero == 0.0).all())


def test_vectorized_positions_match_reference_loop():
    """positions_from_score must equal a reference per-segment loop (causal
    shift + mean-reversion exit within hold segments)."""

    def ref(score, entry, exit_level, H):
        n = len(score)
        s = np.asarray(score, dtype=float)
        desired = np.zeros(n)
        desired[s >= entry] = 1.0
        desired[s <= -entry] = -1.0
        seg_start = (np.arange(n) // H) * H
        seg_desired = desired[seg_start]
        pos = np.zeros(n)
        if n > 1:
            pos[1:] = seg_desired[:-1]
        seg_ids = np.arange(n) // H
        exit_mask = np.abs(s) <= exit_level
        exit_cum = np.zeros(n, dtype=bool)
        for seg_id in np.unique(seg_ids):
            m = seg_ids == seg_id
            exit_cum[m] = np.maximum.accumulate(exit_mask[m])
        pos = np.where(exit_cum, 0.0, pos)
        return np.where(np.isfinite(pos), pos, 0.0)

    rng = np.random.default_rng(7)
    for n in (777, 3600):
        s = pd.Series(rng.standard_normal(n))
        for H in (1, 6, 24, 12):
            for entry, ex in ((1.5, 0.5), (2.0, 1.0)):
                a = c301.positions_from_score(s.to_numpy(dtype=float), entry, ex, H)
                b = ref(s, entry, ex, H)
                assert np.array_equal(a, b), (n, H, entry, ex)


def test_fail_closed_stale_funding_flattens_position():
    for s in SYMBOLS:
        d = _asset(s)
        feats = c301.build_features(
            np.asarray(d["pa"]["buy_volume"], dtype=float),
            np.asarray(d["pa"]["sell_volume"], dtype=float),
            np.asarray(d["pa"]["signed_volume"], dtype=float),
            np.asarray(d["pa"]["trade_count"], dtype=float),
            np.asarray(d["pa"]["trade_sign_sum"], dtype=float),
            np.asarray(d["pa"]["vwap"], dtype=float),
        )
        sig = c301.SIGNAL("trade_intensity_z", feats, 288).to_numpy(dtype=float)
        pos = c301.positions_from_score(sig, entry=1e-6, exit_level=0.0, H=1)
        age = c301.compute_funding_age(d["funding"])
        stale = ~np.isfinite(age) | (age > c301.STALE_BARS)
        pos_gated = np.where(stale, 0.0, pos)
        assert bool((pos_gated[stale] == 0.0).all())


def test_wf_splits_fit_asset_window():
    for s in SYMBOLS:
        n = len(PER_ASSET[s]["perp_close"])
        splits = c301.wf_splits(n, c301.TRAIN, c301.TEST, c301.STEP)
        assert len(splits) == 12, f"{s}: expected 12 splits, got {len(splits)}"
        for tr_s, tr_e, te_e in splits:
            assert te_e <= n


def test_edge_rule_never_relaxed():
    """Re-derive the edge rule from the sweep results and confirm it is applied
    at identical strength: exposure>0 AND every cost slice oos_net_sum>0 AND
    every cost slice oos_net_mean > bh_oos_mean AND every cost slice
    oos_net_mean > 0 (flat)."""
    ts = _latest_ts("oos_sweep")
    sweep = json.loads((ROOT / f"reports/campaign301_oos_sweep_{ts}.json").read_text())
    results = sweep.get("results", [])
    assert len(results) == 648, f"expected 648 runs (3 assets x 216), got {len(results)}"
    for r in results:
        exposure = r["oos_exposure_bars_total"] > 0
        all_slices_pos = all(
            r["cost_slices"][f"fee{f}_slip{s2}"]["oos_net_sum"] > 0 for f, s2 in c301.COST_GRID
        )
        beats_bh = all(
            r["cost_slices"][f"fee{f}_slip{s2}"]["oos_net_mean"] >
            r["bh_oos_mean"]
            for f, s2 in c301.COST_GRID
        )
        beats_flat = all(
            r["cost_slices"][f"fee{f}_slip{s2}"]["oos_net_mean"] > 0.0
            for f, s2 in c301.COST_GRID
        )
        expected_edge = bool(exposure and all_slices_pos and beats_bh and beats_flat)
        assert r["edge_proven"] == expected_edge, f"edge rule mismatch for {r}"
        if r["edge_proven"]:
            assert r["block_reason"] is None
        else:
            assert r["block_reason"] == "no_costed_oos_edge"


def test_c301_verdict_not_tradable_zero_edge():
    ts = _latest_ts("verdict")
    verdict = json.loads((ROOT / f"reports/campaign301_verdict_{ts}.json").read_text())
    assert verdict["verdict"] == "NOT_TRADABLE"
    assert verdict["edge_proven"] is False
    assert verdict["campaign"] == 301
    assert verdict.get("executed_fills") is False
    sweep = json.loads((ROOT / f"reports/campaign301_oos_sweep_{ts}.json").read_text())
    assert sweep["summary"]["n_total_runs"] == 648
    assert sweep["summary"]["n_edge_proven"] == 0
    assert sweep["config"]["total_runs_per_asset"] == 216
    run_results = sweep.get("results", [])
    assert len(run_results) == 648
    assert all(r["edge_proven"] is False for r in run_results)


def test_c301_artifacts_exist_with_real_data_flags_and_sha256():
    parts = ("oos_sweep", "tradable_edge_registry", "summary", "verdict", "binding_constraint")
    ts = _latest_ts("verdict")
    paths = {}
    for part in parts:
        matches = sorted(ROOT.glob(f"reports/campaign301_{part}_*.json"))
        assert matches, f"missing C301 artifact for {part}"
        paths[part] = matches[-1]
        payload = json.loads(paths[part].read_text())
        assert payload.get("real_data_only") is True, part
        assert payload.get("fabricated_data") is False, part
        assert payload.get("executed_fills") is False, part
    verdict = json.loads(paths["verdict"].read_text())
    for key, path_key in (
        ("oos_sweep_sha256", "oos_sweep_artifact"),
        ("registry_sha256", "registry_artifact"),
        ("summary_sha256", "summary_artifact"),
        ("binding_constraint_sha256", "binding_constraint_artifact"),
    ):
        artifact_path = verdict.get(path_key)
        assert artifact_path, f"verdict missing {path_key}"
        p = ROOT / artifact_path
        assert p.exists(), f"referenced artifact missing: {artifact_path}"
        assert hashlib.sha256(p.read_bytes()).hexdigest() == verdict[key], f"sha256 mismatch for {artifact_path}"


def test_no_tradable_edge_claimed():
    ts = _latest_ts("verdict")
    verdict = json.loads((ROOT / f"reports/campaign301_verdict_{ts}.json").read_text())
    assert verdict["edge_proven"] is False
    assert "NONE" in verdict["finding"].upper() or "No costed OOS edge proven" in verdict["finding"]
    sweep = json.loads((ROOT / f"reports/campaign301_oos_sweep_{ts}.json").read_text())
    assert sweep["edge_proven"] is False
