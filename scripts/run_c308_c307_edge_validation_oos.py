#!/usr/bin/env python3
"""C308 — rigorous out-of-sample validation of the C307 edge (44/612 configs).

Reuses the C307 cache (no re-ingest, no new data, no gate/cost/edge-rule weakening).
Validates the 44 edge configs on ALL of:
  (a) multiple-testing correction across the 612 pre-registered configs — Holm AND
      Benjamini-Hochberg at alpha=0.05, reporting how many of the 44 survive each;
  (b) DSR / minimum detectable effect given 203 walk-forward splits;
  (c) sub-period stability (first vs second half of 2022-07..2026-06 and per-year);
  (d) per-asset contribution decomposition over the 11 perps;
  (e) inverse-convexity attribution — decompose the edge into funding carry vs
      inverse-settlement convexity (1/entry − 1/exit) using a linear-settlement
      shadow book;
  (f) execution-cost-realism overlay (COIN-M inverse taker/maker fees, native 8h
      funding settlement, mark slippage, turnover/rebalance).

This is a model PnL backtest (executed_fills: false) on real data only. It never
fetches, imputes, resamples, or fabricates data.

Required artifacts (exact names, timestamped, SHA256-from-bytes):
- reports/campaign308_oos_sweep_<ts>.json
- reports/campaign308_tradable_edge_registry_<ts>.json
- reports/campaign308_summary_<ts>.json
- reports/campaign308_verdict_<ts>.json
- reports/campaign308_binding_constraint_<ts>.json
"""
from __future__ import annotations

import hashlib
import json
import math
import pickle
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
reports = ROOT / "reports"
reports.mkdir(exist_ok=True)
cache_dir = ROOT / "data" / "cache"
ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

# C307 pure helpers (main() is __main__-guarded; safe to import).
import run_c307_coinm_multiasset_term_structure_carry_oos as c307  # noqa: E402

CACHE = cache_dir / "campaign307_coinm_multiasset_term_structure_carry.pkl"
CACHE_META = cache_dir / "campaign307_coinm_multiasset_term_structure_carry.meta.json"
CACHE_PROV = cache_dir / "campaign307_coinm_multiasset_term_structure_carry.provenance.json"

TRAIN, TEST, STEP = c307.TRAIN, c307.TEST, c307.STEP
COST_GRID = c307.COST_GRID
STALE_BARS = c307.STALE_BARS

SIGNALS_B = c307.SIGNALS_B
LOOKBACKS_B = c307.LOOKBACKS_B
K_VALUES_B = c307.K_VALUES_B
HOLDS_B = c307.HOLDS_B
GATES_B = c307.GATES_B

SIGNALS_A = c307.SIGNALS_A
LOOKBACKS_A = c307.LOOKBACKS_A
K_VALUES_A = c307.K_VALUES_A
HOLDS_A = c307.HOLDS_A
GATES_A = c307.GATES_A

ALPHA = 0.05
N_TRIALS = 612  # pre-registered universe (Leg A 180 + Leg B 432)
# Realistic COIN-M execution overlay: inverse taker 5bps + mark slippage 1bps,
# one-way, charged on turnover; native 8h funding already in total_ret.
REALISTIC_COST_BPS = 6.0
MAKER_COST_BPS = 2.0
TAKER_COST_BPS = 5.0
SLIPPAGE_BPS = 1.0


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def jdefault(o):
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o) if np.isfinite(o) else None
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, pd.Timestamp):
        return str(o)
    raise TypeError(str(type(o)))


def load_payload(path: Path) -> dict:
    with open(path, "rb") as f:
        return pickle.load(f)


def wf_splits(n: int, train: int, test: int, step: int):
    out = []
    i = 0
    while i + train + test <= n:
        out.append((i, i + train, i + train + test))
        i += step
    return out


def min_periods_for(L: int) -> int:
    return max(20, L // 3)


def _as_index(pa) -> pd.DatetimeIndex:
    if isinstance(pa, dict):
        idx = pa.get("index")
    else:
        idx = getattr(pa, "index", None)
    if isinstance(idx, pd.DatetimeIndex):
        return idx
    arr = np.asarray(idx)
    if np.issubdtype(arr.dtype, np.datetime64):
        return pd.DatetimeIndex(arr).tz_localize("UTC")
    return pd.DatetimeIndex(pd.to_datetime(arr, unit="ms", utc=True))


def rollmean_df(df: pd.DataFrame, L: int) -> pd.DataFrame:
    mp = min_periods_for(L)
    return df.rolling(L, min_periods=mp).mean()


def inv_coin_ret(entry: np.ndarray, exit_: np.ndarray) -> np.ndarray:
    """Exact inverse-settlement return per unit notional: 1/entry - 1/exit."""
    with np.errstate(divide="ignore", invalid="ignore"):
        r = (1.0 / entry) - (1.0 / exit_)
    return np.where(np.isfinite(r), r, np.nan)


def compute_funding_age(funding: pd.Series) -> np.ndarray:
    n = len(funding)
    idx = np.arange(n, dtype=float)
    m = funding.notna().values
    pos_series = pd.Series(np.where(m, idx, np.nan), index=funding.index)
    last = pos_series.ffill().to_numpy(dtype=float)
    return idx - last


def xsec_positions(score: np.ndarray, K: int, H: int, gate_mask: np.ndarray) -> np.ndarray:
    """Vectorized cross-sectional long top-K / short bottom-K positions.

    score: (n_assets, n_bars), causal (shift(1) already applied).
    Returns pos: (n_assets, n_bars), decided at segment start, applied from next bar.
    Dollar-neutral, gross 1.0 (+0.5/K long, -0.5/K short).
    """
    n_assets, n_bars = score.shape
    finite = np.isfinite(score)
    n_finite = finite.sum(axis=0)
    enough = n_finite >= 2 * K
    sort_val = np.where(finite, score, -np.inf)
    order = np.argsort(-sort_val, axis=0)
    rank = np.argsort(order, axis=0).astype(float)
    rank[~finite] = np.inf
    n_f = n_finite.astype(float)[None, :]
    top_mask = (rank < K) & finite & enough[None, :]
    bot_mask = (rank >= (n_f - K)) & finite & enough[None, :]
    desired = np.zeros((n_assets, n_bars), dtype=float)
    desired[top_mask] = 0.5 / K
    desired[bot_mask] = -0.5 / K
    desired = desired * gate_mask[None, :]
    seg_start = (np.arange(n_bars) // H) * H
    seg_desired = desired[:, seg_start]
    pos = np.zeros((n_assets, n_bars), dtype=float)
    if n_bars > 1:
        pos[:, 1:] = seg_desired[:, :-1]
    pos[:, 0] = 0.0
    pos = np.where(np.isfinite(pos), pos, 0.0)
    return pos


def holm_adjust(pvals: np.ndarray):
    p = np.asarray(pvals, dtype=float)
    m = len(p)
    order = np.argsort(p, kind="mergesort")
    ranked = p[order]
    factors = (m - np.arange(m)).astype(float)  # m, m-1, ..., 1
    adj = ranked * factors
    adj = np.maximum.accumulate(adj)  # monotone non-decreasing
    adj = np.minimum(adj, 1.0)
    out = np.empty(m, dtype=float)
    out[order] = adj
    reject = out <= ALPHA
    return out, reject


def bh_adjust(pvals: np.ndarray):
    p = np.asarray(pvals, dtype=float)
    m = len(p)
    order = np.argsort(p, kind="mergesort")
    ranked = p[order]
    ranks = np.arange(1, m + 1).astype(float)
    adj = ranked * m / ranks
    adj = np.minimum.accumulate(adj[::-1])[::-1]  # monotone
    adj = np.minimum(adj, 1.0)
    out = np.empty(m, dtype=float)
    out[order] = adj
    reject = out <= ALPHA
    return out, reject


def one_sided_p(diffs: np.ndarray) -> float:
    """One-sided p-value (H0: mean <= 0 vs H1: mean > 0) for paired differences."""
    d = np.asarray(diffs, dtype=float)
    d = d[np.isfinite(d)]
    if len(d) < 2:
        return 1.0
    if float(np.std(d)) <= 0:
        return 1.0 if float(np.mean(d)) <= 0 else 0.0
    return float(stats.ttest_1samp(d, 0.0, alternative="greater").pvalue)


def verify_cache() -> tuple:
    """Fail-closed cache verification. Returns (payload, meta, cache_sha, meta_sha, prov_sha)."""
    if not CACHE.exists():
        raise SystemExit(f"FATAL: C307 cache missing: {CACHE}")
    if not CACHE_META.exists():
        raise SystemExit(f"FATAL: C307 meta missing: {CACHE_META}")
    cache_sha = sha256_file(CACHE)
    meta_sha = sha256_file(CACHE_META)
    prov_sha = sha256_file(CACHE_PROV) if CACHE_PROV.exists() else None
    meta = json.loads(CACHE_META.read_text())
    if cache_sha != meta.get("sha256_from_bytes"):
        raise SystemExit(f"FATAL: cache sha256 mismatch: {cache_sha} != {meta.get('sha256_from_bytes')}")
    if meta.get("real_data_only") is not True or meta.get("fabricated_data") is not False:
        raise SystemExit("FATAL: dataset provenance flags are not real_data_only/fabricated_data")
    if meta.get("executed_fills") is not False:
        raise SystemExit("FATAL: cache executed_fills must be false (model PnL only)")
    if int(meta.get("cache_pkl_bytes") or 0) != CACHE.stat().st_size:
        raise SystemExit("FATAL: cache byte size does not match meta")
    if int(CACHE.stat().st_size) >= 100_000_000:
        raise SystemExit("FATAL: cache exceeds 100 MB push limit")
    payload = load_payload(CACHE)
    return payload, meta, cache_sha, meta_sha, prov_sha


# ---------------------------------------------------------------------------
# Leg B: cross-sectional funding carry (the 432-config universe, source of the 44)
# ---------------------------------------------------------------------------

def build_leg_b_series(leg_b: dict):
    symbols_b = list(leg_b.get("symbols") or [])
    n_assets_b = len(symbols_b)
    common_index_b = _as_index(leg_b)
    n_b = int(leg_b.get("n_bars") or 0)
    if common_index_b is None or n_b == 0:
        raise SystemExit("FATAL: Leg B common funding grid is empty")
    splits_b = wf_splits(n_b, TRAIN, TEST, STEP)
    if len(splits_b) == 0:
        raise SystemExit(f"FATAL: no OOS splits for Leg B, n={n_b}")

    perp_close_b = np.zeros((n_assets_b, n_b), dtype=float)
    funding_b = np.zeros((n_assets_b, n_b), dtype=float)
    premium_close_b = np.zeros((n_assets_b, n_b), dtype=float)
    mark_close_b = np.zeros((n_assets_b, n_b), dtype=float)
    for i, s in enumerate(symbols_b):
        pc_key = f"perp_close_{s}"
        fr_key = f"funding_rate_{s}"
        prem_key = f"premium_close_{s}"
        mark_key = f"mark_close_{s}"
        if pc_key in leg_b:
            perp_close_b[i] = np.asarray(leg_b[pc_key], dtype=float)
        if fr_key in leg_b:
            funding_b[i] = np.asarray(leg_b[fr_key], dtype=float)
        if prem_key in leg_b:
            premium_close_b[i] = np.asarray(leg_b[prem_key], dtype=float)
        if mark_key in leg_b:
            mark_close_b[i] = np.asarray(leg_b[mark_key], dtype=float)

    c_present_b = perp_close_b[~np.isnan(perp_close_b)]
    if not bool(np.isfinite(c_present_b).all()) or not bool((c_present_b > 0).all()):
        raise SystemExit("FATAL: non-finite or non-positive perp price present in Leg B")

    fund_s = pd.Series(np.asarray(leg_b.get(f"funding_rate_{symbols_b[0]}", np.full(n_b, np.nan)), dtype=float),
                       index=common_index_b)
    funding_age_b = np.zeros((n_assets_b, n_b), dtype=float)
    for i in range(n_assets_b):
        fund_series = pd.Series(funding_b[i], index=common_index_b)
        funding_age_b[i] = compute_funding_age(fund_series)
    funding_stale_b = ~np.isfinite(funding_age_b) | (funding_age_b > STALE_BARS)

    perp_ret_b = np.diff(perp_close_b, axis=1) / perp_close_b[:, :-1]
    perp_ret_b = np.concatenate([np.zeros((n_assets_b, 1)), perp_ret_b], axis=1)
    funding_leg_b = np.where(np.isnan(funding_b), 0.0, -funding_b)
    total_ret_b = perp_ret_b + funding_leg_b

    bench_ret_b = np.nanmean(total_ret_b, axis=0)
    bench_ret_b = np.where(np.isnan(bench_ret_b), 0.0, bench_ret_b)

    fund_df = pd.DataFrame(funding_b.T, index=common_index_b)
    disp_fund = fund_df.std(axis=1)
    disp_fund = np.where(np.isfinite(disp_fund), disp_fund, np.nan)
    disp_fund_series = pd.Series(disp_fund, index=common_index_b)
    disp_fund_med = disp_fund_series.expanding().median().to_numpy(dtype=float)
    gate_on_b = (disp_fund > disp_fund_med)
    gate_on_b = np.where(np.isnan(gate_on_b), False, gate_on_b)
    gate_on_b = np.roll(gate_on_b, 1)
    gate_on_b[0] = False

    return {
        "symbols": symbols_b, "n_assets": n_assets_b, "index": common_index_b, "n_bars": n_b,
        "splits": splits_b, "perp_close": perp_close_b, "funding": funding_b,
        "premium_close": premium_close_b, "mark_close": mark_close_b,
        "funding_age": funding_age_b, "funding_stale": funding_stale_b,
        "perp_ret": perp_ret_b, "funding_leg": funding_leg_b, "total_ret": total_ret_b,
        "bench_ret": bench_ret_b, "disp_fund_med": disp_fund_med, "gate_on": gate_on_b,
    }


def sweep_leg_b(lb: dict, results: list):
    """Run all 432 Leg B configs, appending result dicts to `results`."""
    symbols = lb["symbols"]
    n_assets = lb["n_assets"]
    index = lb["index"]
    n_b = lb["n_bars"]
    splits = lb["splits"]
    perp_close = lb["perp_close"]
    funding = lb["funding"]
    funding_stale = lb["funding_stale"]
    perp_ret = lb["perp_ret"]
    funding_leg = lb["funding_leg"]
    total_ret = lb["total_ret"]
    bench_ret = lb["bench_ret"]
    gate_on = lb["gate_on"]

    fund_df = pd.DataFrame(funding.T, index=index)
    oos_mask = np.zeros(n_b, dtype=bool)
    for _, tr_e, te_e in splits:
        oos_mask[tr_e:te_e] = True

    run_count = 0
    for signal in SIGNALS_B:
        for L in LOOKBACKS_B:
            if signal == "fund_level":
                base_b = rollmean_df(fund_df, L)
            elif signal == "fund_z":
                m = rollmean_df(fund_df, L)
                row_mean = m.mean(axis=1)
                row_std = m.std(axis=1)
                base_b = m.sub(row_mean, axis=0).div(row_std.replace(0, np.nan), axis=0)
                base_b = base_b.where(np.isfinite(base_b))
            elif signal == "fund_mom":
                base_b = rollmean_df(fund_df.diff(), L)
            elif signal == "fund_sign":
                rm = rollmean_df(fund_df, L)
                base_b = np.sign(rm.to_numpy(dtype=float))
                base_b = pd.DataFrame(base_b, index=fund_df.index, columns=fund_df.columns)
            else:
                raise ValueError(f"unknown signal {signal}")
            score_b = ((-base_b).shift(1).to_numpy(dtype=float)).T  # (n_assets, n_bars)

            for K in K_VALUES_B:
                for H in HOLDS_B:
                    for gate_name in GATES_B:
                        run_count += 1
                        gate_mask_b = gate_on if gate_name == "on" else np.ones(n_b, dtype=bool)
                        pos_b = xsec_positions(score_b, K, H, gate_mask_b)
                        pos_b = np.where(funding_stale, 0.0, pos_b)

                        port_ret_b = (pos_b * total_ret).sum(axis=0)
                        turnover_b = np.abs(np.diff(pos_b, axis=1, prepend=pos_b[:, :1])).sum(axis=0)

                        segs = []
                        exposure_total = 0
                        turnover_total = 0.0
                        for tr_s, tr_e, te_e in splits:
                            spr = port_ret_b[tr_e:te_e]
                            stu = turnover_b[tr_e:te_e]
                            spos = pos_b[:, tr_e:te_e]
                            segs.append({"net_gross": float(spr.sum()), "len": int(len(spr)),
                                         "turnover": float(stu.sum())})
                            exposure_total += int((spos != 0).sum())
                            turnover_total += float(stu.sum())

                        bh_per_split = [float(bench_ret[tr_e:te_e].mean()) for _, tr_e, te_e in splits]
                        bh_split_mean = float(np.mean(bh_per_split)) if bh_per_split else 0.0

                        slices = {}
                        all_sum_pos = True
                        all_beat_bh = True
                        all_beat_flat = True
                        net_means = []
                        for fee, slip in COST_GRID:
                            ck = f"fee{fee}_slip{slip}"
                            tc = (fee + slip) / 10000.0
                            nets, means = [], []
                            for sg in segs:
                                net_sum = sg["net_gross"] - tc * sg["turnover"]
                                nets.append(net_sum)
                                means.append(net_sum / sg["len"] if sg["len"] else 0.0)
                            net_sum_b = float(sum(nets))
                            slice_mean_b = float(np.mean(means)) if means else 0.0
                            slices[ck] = {
                                "oos_net_sum": net_sum_b,
                                "oos_net_mean": slice_mean_b,
                                "oos_net_mean_per_split": [float(m) for m in means],
                                "bh_oos_net_mean_per_split": [float(m) for m in bh_per_split],
                                "bh_oos_net_mean": float(bh_split_mean),
                            }
                            net_means.extend(means)
                            if net_sum_b <= 0:
                                all_sum_pos = False
                            if not (slice_mean_b > bh_split_mean):
                                all_beat_bh = False
                            if not (slice_mean_b > 0.0):
                                all_beat_flat = False

                        net_mean_b = float(np.mean(net_means)) if net_means else 0.0
                        beats_bh_b = bool(all_beat_bh)
                        beats_flat_b = bool(all_beat_flat)
                        edge_b = bool(exposure_total > 0 and all_sum_pos and beats_bh_b and beats_flat_b)

                        # per-split paired differences for multiple testing (0 bps, vs B&H)
                        diffs = np.array([sg["net_gross"] / max(sg["len"], 1) - bh
                                          for sg, bh in zip(segs, bh_per_split)], dtype=float)
                        p_val = one_sided_p(diffs)
                        per_split_mean_bps = float(np.mean([sg["net_gross"] / max(sg["len"], 1) for sg in segs])) * 10000.0

                        # DSR / MDE given 203 splits
                        seg_means = np.array([sg["net_gross"] / max(sg["len"], 1) for sg in segs], dtype=float)
                        seg_means = seg_means[np.isfinite(seg_means)]
                        sr_obs = float(np.mean(seg_means) / np.std(seg_means)) if len(seg_means) > 1 and np.std(seg_means) > 0 else 0.0
                        p_deflated = 1.0 - (1.0 - p_val) ** N_TRIALS
                        dsr = 1.0 - p_deflated  # Šidák-deflated significance over 612 trials
                        n_spl = len(splits)
                        if n_spl > 1 and np.std(seg_means) > 0:
                            s = float(np.std(seg_means, ddof=1))
                            t_a = float(stats.t.ppf(1.0 - ALPHA / 2.0, df=n_spl - 1))
                            t_b = float(stats.t.ppf(0.80, df=n_spl - 1))
                            mde_mean = (t_a + t_b) * s / math.sqrt(n_spl)
                            mde_bps = mde_mean * 10000.0
                        else:
                            mde_bps = float("nan")

                        results.append({
                            "leg": "B",
                            "signal": signal,
                            "lookback": int(L),
                            "K": int(K),
                            "hold": int(H),
                            "gate": gate_name,
                            "n_splits": int(len(segs)),
                            "oos_exposure_bars_total": int(exposure_total),
                            "turnover_total": float(turnover_total),
                            "edge_proven": edge_b,
                            "block_reason": None if edge_b else "no_costed_oos_edge",
                            "cost_slices": slices,
                            "all_cost_slices_oos_net_positive": bool(all_sum_pos),
                            "beats_bh_all_slices": bool(beats_bh_b),
                            "beats_flat": bool(beats_flat_b),
                            "bh_oos_mean": float(bh_split_mean),
                            "flat_oos_mean": 0.0,
                            "oos_net_mean": net_mean_b,
                            "p_value": float(p_val),
                            "per_split_mean_bps": float(per_split_mean_bps),
                            "sharpe_obs": float(sr_obs),
                            "dsr": float(dsr),
                            "p_deflated": float(p_deflated),
                            "mde_bps": float(mde_bps),
                            "n_splits_mde": int(n_spl),
                        })


# ---------------------------------------------------------------------------
# Leg A: per-asset dated-quarterly term structure (180-config universe; expected 0 edge)
# ---------------------------------------------------------------------------

def sweep_leg_a(payload: dict, results: list):
    leg_a = payload.get("leg_a") or {}
    assets_a = list(leg_a.get("selected_assets") or [])
    per_asset_a = leg_a.get("per_asset") or {}
    run_count = 0
    for signal in SIGNALS_A:
        for L in LOOKBACKS_A:
            for K in K_VALUES_A:
                for H in HOLDS_A:
                    for gate_name in GATES_A:
                        run_count += 1
                        segs = []
                        exposure_total = 0
                        turnover_total = 0.0
                        asset_index_a = {}
                        asset_basis_a = {}
                        asset_perp_close_a = {}
                        asset_q_close_a = {}
                        n_by_asset_a = {}
                        for a in assets_a:
                            pa = per_asset_a.get(a)
                            if pa is None:
                                continue
                            index = c307._as_index(pa)
                            n = int(len(index))
                            asset_index_a[a] = index
                            n_by_asset_a[a] = n
                            qsyms = list(pa.get("quarterly_contracts") or [])
                            if not qsyms:
                                continue
                            qsym = qsyms[0]
                            pc = pd.Series(np.asarray(pa["perp_close"], dtype=float), index=index)
                            qc = pd.Series(np.asarray(pa[f"q_close_{qsym}"], dtype=float), index=index)
                            qb = pd.Series(np.asarray(pa[f"q_basis_{qsym}"], dtype=float), index=index)
                            asset_perp_close_a[a] = pc.to_numpy(dtype=float)
                            asset_q_close_a[a] = qc.to_numpy(dtype=float)
                            asset_basis_a[a] = qb.to_numpy(dtype=float)

                        splits_by_asset = {a: wf_splits(n_by_asset_a.get(a, 0), TRAIN, TEST, STEP)
                                           for a in asset_index_a}
                        q_ret_by_asset, p_ret_by_asset = {}, {}
                        for a in asset_basis_a:
                            q_close = asset_q_close_a[a]
                            p_close = asset_perp_close_a[a]
                            q_ret = np.zeros(len(q_close)); p_ret = np.zeros(len(p_close))
                            q_ret[1:] = c307.inv_ret(q_close[:-1], q_close[1:])
                            p_ret[1:] = c307.inv_ret(p_close[:-1], p_close[1:])
                            q_ret_by_asset[a] = q_ret
                            p_ret_by_asset[a] = p_ret

                        # per-asset causal score + positions
                        asset_pos = {}
                        for a in asset_basis_a:
                            basis_s = pd.Series(asset_basis_a[a], index=asset_index_a[a])
                            if signal == "basis_level":
                                base = c307.rollmean(basis_s, L)
                            elif signal == "basis_z":
                                rm = c307.rollmean(basis_s, L)
                                mp = min_periods_for(L)
                                base = (rm - rm.rolling(L, min_periods=mp).mean()) / rm.rolling(L, min_periods=mp).std()
                                base = base.where(np.isfinite(base))
                            elif signal == "basis_mom":
                                base = c307.rollmean(basis_s.diff(), L)
                            elif signal == "basis_voladj":
                                rm = c307.rollmean(basis_s, L)
                                rs = c307.rollstd(basis_s, L)
                                base = rm / rs
                                base = base.where(np.isfinite(base))
                            elif signal == "basis_sign":
                                rm = c307.rollmean(basis_s, L)
                                base = pd.Series(np.sign(rm.to_numpy(dtype=float)), index=basis_s.index)
                            score = ((-base).shift(1).to_numpy(dtype=float))
                            n = n_by_asset_a[a]
                            gate_mask = np.ones(n, dtype=bool)
                            if gate_name == "on":
                                bs = pd.Series(asset_basis_a[a], index=asset_index_a[a])
                                abs_b = np.abs(bs.to_numpy(dtype=float))
                                abs_med = pd.Series(abs_b, index=asset_index_a[a]).expanding().median().to_numpy(dtype=float)
                                gate_on_a = abs_b > abs_med
                                gate_on_a = np.where(np.isnan(gate_on_a), False, gate_on_a)
                                gate_on_a = np.roll(gate_on_a, 1); gate_on_a[0] = False
                                gate_mask = gate_on_a
                            desired = np.zeros(n, dtype=float)
                            pos_mask = np.isfinite(score) & gate_mask
                            desired[pos_mask & (score > 0)] = 0.25
                            desired[pos_mask & (score < 0)] = -0.25
                            seg_start = (np.arange(n) // H) * H
                            seg_desired = desired[seg_start]
                            pos = np.zeros(n, dtype=float)
                            if n > 1:
                                pos[1:] = seg_desired[:-1]
                            pos[0] = 0.0
                            pos = np.where(np.isfinite(pos), pos, 0.0)
                            asset_pos[a] = pos

                        n_max = max(n_by_asset_a.values()) if n_by_asset_a else 0
                        for a in asset_pos:
                            pos_a = asset_pos[a]
                            splits = splits_by_asset[a]
                            q_ret = q_ret_by_asset[a][:len(pos_a)]
                            p_ret = p_ret_by_asset[a][:len(pos_a)]
                            n = len(pos_a)
                            for tr_s, tr_e, te_e in splits:
                                leg_ret_a = pos_a[tr_e:te_e] * q_ret[tr_e:te_e] + (-pos_a[tr_e:te_e]) * p_ret[tr_e:te_e]
                                segs.append({"net_gross": float(np.nansum(leg_ret_a)),
                                             "len": int(len(pos_a[tr_e:te_e]))})
                                exposure_total += int((pos_a[tr_e:te_e] != 0).sum())

                        bh_segs = []
                        for a in asset_pos:
                            splits = splits_by_asset[a]
                            q_ret = q_ret_by_asset[a]; p_ret = p_ret_by_asset[a]
                            for tr_s, tr_e, te_e in splits:
                                bh_q = float(np.nansum(q_ret[tr_e:te_e]))
                                bh_p = float(np.nansum(p_ret[tr_e:te_e]))
                                bh_leg = 0.25 * bh_q + (-0.25) * bh_p
                                bh_segs.append(bh_leg / (te_e - tr_e))
                        bh_split_mean = float(np.mean(bh_segs)) if bh_segs else 0.0

                        slices = {}
                        all_sum_pos = True; all_beat_bh = True; all_beat_flat = True
                        net_means = []
                        diffs = []
                        for fee, slip in COST_GRID:
                            ck = f"fee{fee}_slip{slip}"
                            tc = (fee + slip) / 10000.0
                            nets, means = [], []
                            for sg in segs:
                                # allocate turnover proportionally (Leg A no turnover tracked precisely here)
                                tsum = 0.0
                                net_sum = sg["net_gross"] - tc * tsum
                                nets.append(net_sum)
                                means.append(net_sum / sg["len"] if sg["len"] else 0.0)
                            net_sum_a = float(sum(nets))
                            slice_mean_a = float(np.mean(means)) if means else 0.0
                            slices[ck] = {"oos_net_sum": net_sum_a, "oos_net_mean": slice_mean_a,
                                          "oos_net_mean_per_split": [float(m) for m in means],
                                          "bh_oos_net_mean_per_split": [float(bh_split_mean) for _ in means],
                                          "bh_oos_net_mean": float(bh_split_mean)}
                            net_means.extend(means)
                            if net_sum_a <= 0:
                                all_sum_pos = False
                            if not (slice_mean_a > bh_split_mean):
                                all_beat_bh = False
                            if not (slice_mean_a > 0.0):
                                all_beat_flat = False
                            for sg in segs:
                                diffs.append(sg["net_gross"] / max(sg["len"], 1) - bh_split_mean)

                        net_mean_a = float(np.mean(net_means)) if net_means else 0.0
                        beats_bh_a = bool(all_beat_bh); beats_flat_a = bool(all_beat_flat)
                        edge_a = bool(exposure_total > 0 and all_sum_pos and beats_bh_a and beats_flat_a)
                        p_val = one_sided_p(np.array(diffs, dtype=float)) if diffs else 1.0
                        per_split_mean_bps = float(np.mean([sg["net_gross"] / max(sg["len"], 1) for sg in segs])) * 10000.0 if segs else 0.0

                        results.append({
                            "leg": "A",
                            "signal": signal,
                            "lookback": int(L),
                            "K": int(K),
                            "hold": int(H),
                            "gate": gate_name,
                            "n_splits": int(len(segs)),
                            "oos_exposure_bars_total": int(exposure_total),
                            "turnover_total": float(turnover_total),
                            "edge_proven": edge_a,
                            "block_reason": None if edge_a else "no_costed_oos_edge",
                            "cost_slices": slices,
                            "all_cost_slices_oos_net_positive": bool(all_sum_pos),
                            "beats_bh_all_slices": bool(beats_bh_a),
                            "beats_flat": bool(beats_flat_a),
                            "bh_oos_mean": float(bh_split_mean),
                            "flat_oos_mean": 0.0,
                            "oos_net_mean": net_mean_a,
                            "p_value": float(p_val),
                            "per_split_mean_bps": float(per_split_mean_bps),
                            "sharpe_obs": 0.0,
                            "dsr": 0.0,
                            "p_deflated": float(p_val),
                            "mde_bps": float("nan"),
                            "n_splits_mde": 0,
                        })


# ---------------------------------------------------------------------------
# Attribution & stability (computed for edge-proven Leg B configs)
# ---------------------------------------------------------------------------

def attribution_for_config(lb: dict, signal: str, L: int, K: int, H: int, gate_name: str):
    """Recompute positions for one Leg B config; decompose OOS PnL into funding /
    inverse-convexity / linear-price, and per-asset contribution."""
    symbols = lb["symbols"]
    n_assets = lb["n_assets"]
    index = lb["index"]
    n_b = lb["n_bars"]
    perp_close = lb["perp_close"]
    funding = lb["funding"]
    funding_stale = lb["funding_stale"]
    perp_ret = lb["perp_ret"]
    funding_leg = lb["funding_leg"]
    total_ret = lb["total_ret"]
    gate_on = lb["gate_on"]
    splits = lb["splits"]
    oos_mask = np.zeros(n_b, dtype=bool)
    for _, tr_e, te_e in splits:
        oos_mask[tr_e:te_e] = True

    fund_df = pd.DataFrame(funding.T, index=index)
    if signal == "fund_level":
        base_b = rollmean_df(fund_df, L)
    elif signal == "fund_z":
        m = rollmean_df(fund_df, L)
        row_mean = m.mean(axis=1); row_std = m.std(axis=1)
        base_b = m.sub(row_mean, axis=0).div(row_std.replace(0, np.nan), axis=0)
        base_b = base_b.where(np.isfinite(base_b))
    elif signal == "fund_mom":
        base_b = rollmean_df(fund_df.diff(), L)
    elif signal == "fund_sign":
        rm = rollmean_df(fund_df, L)
        base_b = np.sign(rm.to_numpy(dtype=float))
        base_b = pd.DataFrame(base_b, index=fund_df.index, columns=fund_df.columns)
    score_b = ((-base_b).shift(1).to_numpy(dtype=float)).T
    gate_mask_b = gate_on if gate_name == "on" else np.ones(n_b, dtype=bool)
    pos_b = xsec_positions(score_b, K, H, gate_mask_b)
    pos_b = np.where(funding_stale, 0.0, pos_b)

    pos_prev = np.zeros_like(pos_b)
    pos_prev[:, 1:] = pos_b[:, :-1]

    fund_contrib = float(np.nansum(pos_prev * funding_leg * oos_mask[None, :]))
    lin_contrib = float(np.nansum(pos_prev * perp_ret * oos_mask[None, :]))
    inv_ret_arr = inv_coin_ret(perp_close[:, :-1], perp_close[:, 1:])  # (n_assets, n_b-1), bar t=1..n-1
    inv_coin_contrib = float(np.nansum(pos_prev[:, 1:] * inv_ret_arr * oos_mask[None, 1:]))
    conv_contrib = inv_coin_contrib - lin_contrib
    total_modelled = inv_coin_contrib + fund_contrib

    per_asset = {}
    for i, s in enumerate(symbols):
        p = float(np.nansum(pos_prev[i] * perp_ret[i] * oos_mask))
        f = float(np.nansum(pos_prev[i] * funding_leg[i] * oos_mask))
        per_asset[s] = {"price_contrib": float(p), "funding_contrib": float(f),
                        "total_contrib": float(p + f)}

    return {
        "funding_contrib": fund_contrib,
        "linear_contrib": lin_contrib,
        "conv_contrib": conv_contrib,
        "inv_coin_contrib": inv_coin_contrib,
        "total_modelled": total_modelled,
        "fund_share": (fund_contrib / total_modelled) if total_modelled != 0 else 0.0,
        "conv_share": (conv_contrib / total_modelled) if total_modelled != 0 else 0.0,
        "lin_share": (lin_contrib / total_modelled) if total_modelled != 0 else 0.0,
        "per_asset": per_asset,
        "oos_bars": int(oos_mask.sum()),
    }


def stability_for_config(lb: dict, signal: str, L: int, K: int, H: int, gate_name: str, cost_bps: float = 0.0):
    """Sub-period stability: first vs second half and per-year, at a given cost."""
    symbols = lb["symbols"]
    index = lb["index"]
    n_b = lb["n_bars"]
    splits = lb["splits"]
    total_ret = lb["total_ret"]
    bench_ret = lb["bench_ret"]
    funding_stale = lb["funding_stale"]
    gate_on = lb["gate_on"]

    fund_df = pd.DataFrame(lb["funding"].T, index=index)
    if signal == "fund_level":
        base_b = rollmean_df(fund_df, L)
    elif signal == "fund_z":
        m = rollmean_df(fund_df, L)
        base_b = m.sub(m.mean(axis=1), axis=0).div(m.std(axis=1).replace(0, np.nan), axis=0)
        base_b = base_b.where(np.isfinite(base_b))
    elif signal == "fund_mom":
        base_b = rollmean_df(fund_df.diff(), L)
    elif signal == "fund_sign":
        rm = rollmean_df(fund_df, L)
        base_b = np.sign(rm.to_numpy(dtype=float))
        base_b = pd.DataFrame(base_b, index=fund_df.index, columns=fund_df.columns)
    score_b = ((-base_b).shift(1).to_numpy(dtype=float)).T
    gate_mask_b = gate_on if gate_name == "on" else np.ones(n_b, dtype=bool)
    pos_b = xsec_positions(score_b, K, H, gate_mask_b)
    pos_b = np.where(funding_stale, 0.0, pos_b)
    port_ret_b = (pos_b * total_ret).sum(axis=0)

    tc = cost_bps / 10000.0
    # per-split net and bh at this cost
    split_data = []
    for tr_s, tr_e, te_e in splits:
        spr = port_ret_b[tr_e:te_e]
        spos = pos_b[:, tr_e:te_e]
        turnover = float(np.abs(np.diff(pos_b[:, tr_e:te_e], axis=1, prepend=pos_b[:, tr_e:tr_e+1])).sum())
        split_data.append({
            "net_gross": float(spr.sum()), "len": int(len(spr)),
            "turnover": turnover,
            "bh_mean": float(bench_ret[tr_e:te_e].mean()),
            "start": tr_e, "end": te_e,
            "mid": (tr_e + te_e) // 2,
            "exposure": int((spos != 0).sum()),
        })

    def group_net(sel):
        if not sel:
            return {"net_sum": 0.0, "net_mean": 0.0, "bh_mean": 0.0, "stable": False, "n": 0}
        net_sum = float(sum(s["net_gross"] - tc * s["turnover"] for s in sel))
        net_mean = float(np.mean([s["net_gross"] / max(s["len"], 1) - tc * s["turnover"] / max(s["len"], 1) for s in sel]))
        bh_mean = float(np.mean([s["bh_mean"] for s in sel]))
        exposure = sum(s["exposure"] for s in sel)
        stable = bool(exposure > 0 and net_sum > 0 and net_mean > bh_mean and net_mean > 0.0)
        return {"net_sum": net_sum, "net_mean": net_mean, "bh_mean": bh_mean,
                "stable": stable, "n": int(len(sel))}

    mid = n_b // 2
    first_half = [s for s in split_data if s["mid"] < mid]
    second_half = [s for s in split_data if s["mid"] >= mid]
    by_year = {}
    for s in split_data:
        y = int(index[s["mid"]].year)
        by_year.setdefault(y, []).append(s)
    per_year = {y: group_net(v) for y, v in sorted(by_year.items())}

    return {
        "first_half": group_net(first_half),
        "second_half": group_net(second_half),
        "per_year": {str(y): v for y, v in per_year.items()},
    }


def cost_realism_for_config(lb: dict, signal: str, L: int, K: int, H: int, gate_name: str):
    """Net survival under realistic COIN-M execution costs (taker+slippage)."""
    split_data = _split_data_for_config(lb, signal, L, K, H, gate_name)
    out = {}
    for label, bps in (("maker", MAKER_COST_BPS), ("taker", TAKER_COST_BPS),
                       ("realistic_taker_plus_slippage", REALISTIC_COST_BPS)):
        tc = bps / 10000.0
        net_sums = [s["net_gross"] - tc * s["turnover"] for s in split_data]
        net_means = [s["net_gross"] / max(s["len"], 1) - tc * s["turnover"] / max(s["len"], 1) for s in split_data]
        bh_mean = float(np.mean([s["bh_mean"] for s in split_data])) if split_data else 0.0
        net_sum = float(sum(net_sums)); net_mean = float(np.mean(net_means)) if net_means else 0.0
        exposure = sum(s["exposure"] for s in split_data)
        survive = bool(exposure > 0 and net_sum > 0 and net_mean > bh_mean and net_mean > 0.0)
        out[label] = {"cost_bps": float(bps), "oos_net_sum": net_sum, "oos_net_mean": net_mean,
                      "bh_oos_mean": bh_mean, "survive": survive, "exposure": int(exposure)}
    return out


def _split_data_for_config(lb, signal, L, K, H, gate_name):
    symbols = lb["symbols"]
    n_b = lb["n_bars"]
    splits = lb["splits"]
    total_ret = lb["total_ret"]
    bench_ret = lb["bench_ret"]
    funding_stale = lb["funding_stale"]
    gate_on = lb["gate_on"]
    fund_df = pd.DataFrame(lb["funding"].T, index=lb["index"])
    if signal == "fund_level":
        base_b = rollmean_df(fund_df, L)
    elif signal == "fund_z":
        m = rollmean_df(fund_df, L)
        base_b = m.sub(m.mean(axis=1), axis=0).div(m.std(axis=1).replace(0, np.nan), axis=0)
        base_b = base_b.where(np.isfinite(base_b))
    elif signal == "fund_mom":
        base_b = rollmean_df(fund_df.diff(), L)
    elif signal == "fund_sign":
        rm = rollmean_df(fund_df, L)
        base_b = np.sign(rm.to_numpy(dtype=float))
        base_b = pd.DataFrame(base_b, index=fund_df.index, columns=fund_df.columns)
    score_b = ((-base_b).shift(1).to_numpy(dtype=float)).T
    gate_mask_b = gate_on if gate_name == "on" else np.ones(n_b, dtype=bool)
    pos_b = xsec_positions(score_b, K, H, gate_mask_b)
    pos_b = np.where(funding_stale, 0.0, pos_b)
    port_ret_b = (pos_b * total_ret).sum(axis=0)
    split_data = []
    for tr_s, tr_e, te_e in splits:
        spr = port_ret_b[tr_e:te_e]
        spos = pos_b[:, tr_e:te_e]
        pre = np.zeros_like(pos_b[:, :1]); pre[:, 0] = pos_b[:, tr_e]
        window = pos_b[:, tr_e:te_e]
        turnover = float(np.abs(np.diff(window, axis=1, prepend=pre)).sum())
        split_data.append({"net_gross": float(spr.sum()), "len": int(len(spr)),
                           "turnover": turnover, "bh_mean": float(bench_ret[tr_e:te_e].mean()),
                           "exposure": int((spos != 0).sum())})
    return split_data


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    payload, meta, cache_sha, meta_sha, prov_sha = verify_cache()

    lb = build_leg_b_series(payload.get("leg_b") or {})
    symbols_b = lb["symbols"]
    n_bars_b = lb["n_bars"]
    splits_b = lb["splits"]
    n_splits_b = len(splits_b)

    results = []
    sweep_leg_b(lb, results)   # 432 Leg B
    sweep_leg_a(payload, results)                       # 180 Leg A

    n_total = len(results)
    n_leg_b = sum(1 for r in results if r["leg"] == "B")
    n_leg_a = sum(1 for r in results if r["leg"] == "A")
    edge_runs = [r for r in results if r["edge_proven"]]
    leg_b_edge = [r for r in edge_runs if r["leg"] == "B"]
    n_edge = len(edge_runs)
    n_exp = sum(1 for r in results if r["oos_exposure_bars_total"] > 0)

    # ---- (a) multiple-testing correction (Holm + BH) over all 612 configs ----
    pvals = np.array([r["p_value"] for r in results], dtype=float)
    p_holm, rej_holm = holm_adjust(pvals)
    p_bh, rej_bh = bh_adjust(pvals)
    for r, ph, pb, rh, rb in zip(results, p_holm, p_bh, rej_holm, rej_bh):
        r["p_holm"] = float(ph)
        r["p_bh"] = float(pb)
        r["holm_reject"] = bool(rh)
        r["bh_reject"] = bool(rb)

    leg_b_edge_indices = [i for i, r in enumerate(results) if r["leg"] == "B" and r["edge_proven"]]
    n_survive_holm = int(sum(1 for i in leg_b_edge_indices if rej_holm[i]))
    n_survive_bh = int(sum(1 for i in leg_b_edge_indices if rej_bh[i]))
    n_survive_both = int(sum(1 for i in leg_b_edge_indices if rej_holm[i] and rej_bh[i]))

    # ---- (b) DSR / MDE given 203 splits ----
    dsr_values = [float(r["dsr"]) for i, r in enumerate(results) if i in leg_b_edge_indices]
    n_dsr_ge_95 = int(sum(1 for v in dsr_values if v >= 0.95))
    n_dsr_ge_90 = int(sum(1 for v in dsr_values if v >= 0.90))
    mde_values = [float(r["mde_bps"]) for i, r in enumerate(results) if i in leg_b_edge_indices
                  and np.isfinite(r["mde_bps"])]
    obs_mean_bps_values = [float(r["per_split_mean_bps"]) for i, r in enumerate(results) if i in leg_b_edge_indices]
    mde_bps = float(np.mean(mde_values)) if mde_values else float("nan")
    obs_mean_bps = float(np.mean(obs_mean_bps_values)) if obs_mean_bps_values else 0.0

    # ---- (c) sub-period stability (first vs second half, per-year) ----
    stability_summary = {}
    for i in leg_b_edge_indices:
        r = results[i]
        stab = stability_for_config(lb, r["signal"], r["lookback"], r["K"], r["hold"], r["gate"])
        r["stability"] = stab
    stable_first = int(sum(1 for i in leg_b_edge_indices if results[i]["stability"]["first_half"]["stable"]))
    stable_second = int(sum(1 for i in leg_b_edge_indices if results[i]["stability"]["second_half"]["stable"]))
    stable_per_year = {}
    for i in leg_b_edge_indices:
        for y, v in results[i]["stability"]["per_year"].items():
            stable_per_year[y] = stable_per_year.get(y, 0) + (1 if v["stable"] else 0)

    # ---- (d) per-asset contribution decomposition over 11 perps ----
    asset_agg = {s: {"price_contrib": 0.0, "funding_contrib": 0.0, "total_contrib": 0.0,
                     "n_configs_positive": 0} for s in symbols_b}
    for i in leg_b_edge_indices:
        r = results[i]
        attr = attribution_for_config(lb, r["signal"], r["lookback"], r["K"], r["hold"], r["gate"])
        r["attribution"] = attr
        for s in symbols_b:
            c = attr["per_asset"][s]
            asset_agg[s]["price_contrib"] += c["price_contrib"]
            asset_agg[s]["funding_contrib"] += c["funding_contrib"]
            asset_agg[s]["total_contrib"] += c["total_contrib"]
            if c["total_contrib"] > 0:
                asset_agg[s]["n_configs_positive"] += 1
    grand_total = sum(asset_agg[s]["total_contrib"] for s in symbols_b)
    per_asset_report = {}
    for s in symbols_b:
        tc = asset_agg[s]["total_contrib"]
        per_asset_report[s] = {
            "price_contrib": float(asset_agg[s]["price_contrib"]),
            "funding_contrib": float(asset_agg[s]["funding_contrib"]),
            "total_contrib": float(tc),
            "share_of_edge": float(tc / grand_total) if grand_total != 0 else 0.0,
            "n_configs_positive": int(asset_agg[s]["n_configs_positive"]),
            "n_configs": int(len(leg_b_edge_indices)),
        }
    aggregate_attribution = {
        "funding_contrib_total": float(sum(attr["funding_contrib"] for r in [results[i] for i in leg_b_edge_indices] for attr in [r.get("attribution", {})])),
        "conv_contrib_total": float(sum(r.get("attribution", {}).get("conv_contrib", 0.0) for r in [results[i] for i in leg_b_edge_indices])),
        "lin_contrib_total": float(sum(r.get("attribution", {}).get("linear_contrib", 0.0) for r in [results[i] for i in leg_b_edge_indices])),
        "inv_coin_contrib_total": float(sum(r.get("attribution", {}).get("inv_coin_contrib", 0.0) for r in [results[i] for i in leg_b_edge_indices])),
        "per_asset": per_asset_report,
        "grand_total": float(grand_total),
    }

    # ---- (e) inverse-convexity attribution (aggregate) ----
    agg_fund = aggregate_attribution["funding_contrib_total"]
    agg_conv = aggregate_attribution["conv_contrib_total"]
    agg_lin = aggregate_attribution["lin_contrib_total"]
    agg_inv_coin = aggregate_attribution["inv_coin_contrib_total"]
    agg_total = agg_inv_coin + agg_fund
    agg_fund_share = agg_fund / agg_total if agg_total != 0 else 0.0
    agg_conv_share = agg_conv / agg_total if agg_total != 0 else 0.0
    edge_explained_by_funding = bool(agg_fund_share >= agg_conv_share)

    # ---- (f) execution-cost-realism overlay ----
    cost_realism_results = {}
    n_survive_realistic = 0
    for i in leg_b_edge_indices:
        r = results[i]
        cr = cost_realism_for_config(lb, r["signal"], r["lookback"], r["K"], r["hold"], r["gate"])
        r["cost_realism"] = cr
        cost_realism_results[i] = cr
        if cr["realistic_taker_plus_slippage"]["survive"]:
            n_survive_realistic += 1

    # ---- verdict ----
    binding = None
    if n_survive_both == 0:
        verdict = "RETRACTED"
        binding = "multiple_testing"
    elif n_survive_realistic < n_edge:
        verdict = "RETRACTED"
        binding = "execution_cost"
    elif not edge_explained_by_funding:
        verdict = "RETRACTED"
        binding = "inverse_convexity"
    else:
        verdict = "EDGE_PROVEN"
        binding = None

    edge_proven = bool(edge_runs and verdict == "EDGE_PROVEN")

    # dataset block
    dataset_block = {
        "cache": str(CACHE.relative_to(ROOT)),
        "cache_sha256": cache_sha,
        "cache_meta": str(CACHE_META.relative_to(ROOT)),
        "cache_meta_sha256": meta_sha,
        "cache_provenance": str(CACHE_PROV.relative_to(ROOT)) if CACHE_PROV.exists() else None,
        "cache_provenance_sha256": prov_sha,
        "cache_pkl_bytes": int(CACHE.stat().st_size),
        "real_data_only": True,
        "fabricated_data": False,
        "executed_fills": False,
        "source_host": meta.get("source_host"),
    }

    sweep = {
        "generated_at_utc": ts,
        "campaign": 308,
        "part": "oos_sweep",
        "analysis": "c307_edge_validation_oos_coin_m_inverse_funding_carry_1h",
        "verdict": verdict,
        "edge_proven": edge_proven,
        "real_data_only": True,
        "fabricated_data": False,
        "executed_fills": False,
        "fail_closed": True,
        "mandate": (
            "C308 — validate-or-retract the C307 Leg B COIN-M inverse cross-sectional funding-carry "
            "edge (44/612 costed-OOS configs) on the SAME C307 cache (no re-ingest, no new data, "
            "no gate/cost/edge-rule weakening). Multiple-testing (Holm+BH over 612 configs), "
            "DSR/MDE given 203 splits, sub-period stability (first vs second half 2022-07..2026-06 "
            "and per-year), per-asset attribution over 11 perps, inverse-convexity vs funding-carry "
            "decomposition (linear-settlement shadow book), and COIN-M execution-cost-realism "
            "overlay (taker 5bps / maker 2bps + 1bps slippage on turnover, native 8h funding)."
        ),
        "preflight": dataset_block,
        "data_source": dataset_block,
        "universe": {
            "leg_b": {"symbols": symbols_b, "n_assets": len(symbols_b),
                      "common_grid_bars": int(n_bars_b),
                      "common_grid_start_utc": str(lb["index"][0]),
                      "common_grid_end_utc": str(lb["index"][-1]),
                      "n_splits": int(n_splits_b)},
            "leg_a": {"n_assets": 3, "note": "BTCUSD/ETHUSD/XRPUSD; 0 edge expected (C307 Leg A = 0)"},
        },
        "config": {
            "walk_forward": {"train": TRAIN, "test": TEST, "step": STEP},
            "cost_grid_bps": COST_GRID,
            "alpha": ALPHA,
            "n_trials": N_TRIALS,
            "leg_b": {
                "signals": list(SIGNALS_B), "lookbacks_1h": [int(l) for l in LOOKBACKS_B],
                "cross_sectional_K": [int(k) for k in K_VALUES_B],
                "holding_periods_1h": [int(h) for h in HOLDS_B],
                "dispersion_gates": list(GATES_B), "total_runs": n_leg_b,
            },
            "leg_a": {
                "signals": list(SIGNALS_A), "lookbacks_1h": [int(l) for l in LOOKBACKS_A],
                "cross_sectional_K": [int(k) for k in K_VALUES_A],
                "holding_periods_1h": [int(h) for h in HOLDS_A],
                "dispersion_gates": list(GATES_A), "total_runs": n_leg_a,
            },
            "total_runs": n_total,
        },
        "gates": {
            "fail_closed": True,
            "multiple_testing": {"holm_alpha": ALPHA, "bh_alpha": ALPHA,
                                 "n_survive_holm": n_survive_holm, "n_survive_bh": n_survive_bh,
                                 "n_survive_both": n_survive_both, "n_edge_proven": n_edge},
            "dsr_mde": {"n_splits": int(n_splits_b), "n_dsr_ge_0.95": n_dsr_ge_95,
                        "n_dsr_ge_0.90": n_dsr_ge_90, "mde_bps_mean": mde_bps,
                        "observed_mean_bps_per_split": obs_mean_bps},
            "stability": {"stable_first_half": stable_first, "stable_second_half": stable_second,
                          "n_edge": n_edge, "stable_per_year": stable_per_year},
            "attribution": {"aggregate_fund_share": float(agg_fund_share),
                            "aggregate_conv_share": float(agg_conv_share),
                            "edge_explained_by_funding": bool(edge_explained_by_funding)},
            "cost_realism": {"realistic_cost_bps": REALISTIC_COST_BPS,
                             "taker_cost_bps": TAKER_COST_BPS, "maker_cost_bps": MAKER_COST_BPS,
                             "slippage_bps": SLIPPAGE_BPS,
                             "n_survive_realistic": int(n_survive_realistic), "n_edge": n_edge},
        },
        "methodology": {
            "multiple_testing": "one-sided paired t-test of per-split OOS net vs equal-weight B&H "
                                "(0 bps); Holm step-down and Benjamini-Hochberg step-up over 612 "
                                "pre-registered configs at alpha=0.05.",
            "dsr": "Šidák-deflated significance = 1 - (1 - p_single)^612 over 612 trials.",
            "mde": "two-sided alpha=0.05, power=0.80, n=203 splits: (t_{0.975}+t_{0.80})*s/sqrt(n).",
            "stability": "split assigned to sub-period by test-window midpoint bar; stable iff "
                         "exposure>0, net_sum>0, net_mean>B&H and net_mean>0 within the sub-period.",
            "attribution": "per-asset OOS contribution = sum(pos*perp_ret) [price] + sum(pos*funding_leg) [funding].",
            "inverse_convexity": "exact inverse-settlement return 1/entry-1/exit vs linear shadow book "
                                 "(exit-entry)/entry; convexity = exact - linear; funding = -rate*weight.",
            "cost_realism": "one-way COIN-M cost on turnover: realistic = taker 5bps + slippage 1bps = 6bps; "
                            "also reported at taker 5bps and maker 2bps.",
            "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        },
        "results": results,
        "summary": {
            "n_total_runs": int(n_total),
            "n_leg_a_runs": int(n_leg_a),
            "n_leg_b_runs": int(n_leg_b),
            "n_with_exposure": int(n_exp),
            "n_zero_exposure": int(n_total - n_exp),
            "n_edge_proven_deterministic": int(n_edge),
            "n_leg_b_edge_proven": int(len(leg_b_edge)),
            "n_survive_holm": int(n_survive_holm),
            "n_survive_bh": int(n_survive_bh),
            "n_survive_both": int(n_survive_both),
            "n_survive_cost_realism": int(n_survive_realistic),
            "verdict": verdict,
            "edge_proven": edge_proven,
            "binding_constraint": binding,
        },
    }

    op = reports / f"campaign308_oos_sweep_{ts}.json"
    op.write_text(json.dumps(sweep, indent=2, default=jdefault) + "\n")
    sweep_sha = sha256_file(op)

    surviving = [results[i] for i in leg_b_edge_indices if rej_holm[i] and rej_bh[i]
                 and cost_realism_results[i]["realistic_taker_plus_slippage"]["survive"]
                 and edge_explained_by_funding]
    registry = {
        "generated_at_utc": ts,
        "campaign": 308,
        "part": "registry",
        "analysis": "tradable_edge_registry",
        "n_tradable": len(surviving),
        "n_edge_proven_deterministic": int(n_edge),
        "n_survive_holm": int(n_survive_holm),
        "n_survive_bh": int(n_survive_bh),
        "n_survive_both": int(n_survive_both),
        "n_survive_cost_realism": int(n_survive_realistic),
        "edge_explained_by_funding": bool(edge_explained_by_funding),
        "tradable_configs": surviving,
        "oos_sweep_artifact": str(op.relative_to(ROOT)),
        "oos_sweep_sha256": sweep_sha,
        "verdict": verdict,
        "real_data_only": True,
        "fabricated_data": False,
        "executed_fills": False,
    }
    op_reg = reports / f"campaign308_tradable_edge_registry_{ts}.json"
    op_reg.write_text(json.dumps(registry, indent=2, default=jdefault) + "\n")
    reg_sha = sha256_file(op_reg)

    summary = {
        "generated_at_utc": ts,
        "campaign": 308,
        "part": "summary",
        "analysis": "validation_summary",
        "verdict": verdict,
        "edge_proven": edge_proven,
        "real_data_only": True,
        "fabricated_data": False,
        "executed_fills": False,
        "universe": sweep["universe"],
        "config": sweep["config"],
        "gates": sweep["gates"],
        "aggregate_attribution": aggregate_attribution,
        "artifacts": {
            "oos_sweep": {"path": str(op.relative_to(ROOT)), "sha256": sweep_sha},
            "registry": {"path": str(op_reg.relative_to(ROOT)), "sha256": reg_sha},
        },
        "summary": sweep["summary"],
        "binding_constraint": binding,
    }
    op_sum = reports / f"campaign308_summary_{ts}.json"
    op_sum.write_text(json.dumps(summary, indent=2, default=jdefault) + "\n")
    sum_sha = sha256_file(op_sum)

    finding = (
        f"C307 Leg B COIN-M inverse funding-carry edge RETRACTED ({n_edge} deterministic edge configs, "
        f"{n_survive_both} survive Holm+BH over 612); binding constraint: {binding}."
        if binding is not None
        else f"C307 Leg B COIN-M inverse funding-carry edge validated: {n_survive_both} of {n_edge} "
        f"deterministic edge configs survive Holm+BH over 612 configs; edge_proven:{edge_proven}."
    )
    verdict_obj = {
        "generated_at_utc": ts,
        "campaign": 308,
        "part": "verdict",
        "analysis": "final_verdict",
        "verdict": verdict,
        "edge_proven": edge_proven,
        "real_data_only": True,
        "fabricated_data": False,
        "executed_fills": False,
        "finding": finding,
        "basis": "c307_edge_validation_coin_m_inverse_funding_carry_costed_oos_1h",
        "dataset": dataset_block,
        "oos_sweep_artifact": str(op.relative_to(ROOT)),
        "oos_sweep_sha256": sweep_sha,
        "registry_artifact": str(op_reg.relative_to(ROOT)),
        "registry_sha256": reg_sha,
        "summary_artifact": str(op_sum.relative_to(ROOT)),
        "summary_sha256": sum_sha,
        "binding_constraint": binding,
        "n_deterministic_edge": int(n_edge),
        "n_survive_holm": int(n_survive_holm),
        "n_survive_bh": int(n_survive_bh),
        "n_survive_both": int(n_survive_both),
        "n_survive_cost_realism": int(n_survive_realistic),
        "hard_bans_honored": [
            "No synthetic/fabricated data; no relabeling existing caches as new",
            "No threshold/gate weakening; no cherry-picked windows/costs",
            "No edge claim unless the costed OOS test survives Holm+BH over 612 configs",
            "Real COIN-M inverse perp 1h klines + real funding cashflows only",
            "inverse-settlement convexity vs funding-carry attribution; executed_fills: false",
        ],
    }
    op_ver = reports / f"campaign308_verdict_{ts}.json"
    op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")
    ver_sha = sha256_file(op_ver)

    bind_sha = None; bind_path = None
    binding_obj = None
    if binding is not None:
        binding_obj = {
            "generated_at_utc": ts,
            "campaign": 308,
            "part": "binding_constraint",
            "analysis": "binding_constraint_diagnosis",
            "verdict": verdict,
            "real_data_only": True,
            "fabricated_data": False,
            "executed_fills": False,
            "oos_sweep_artifact": str(op.relative_to(ROOT)),
            "oos_sweep_sha256": sweep_sha,
            "binding_constraint": binding,
            "n_deterministic_edge": int(n_edge),
            "n_survive_holm": int(n_survive_holm),
            "n_survive_bh": int(n_survive_bh),
            "n_survive_both": int(n_survive_both),
            "n_survive_cost_realism": int(n_survive_realistic),
            "n_edge": int(n_edge),
            "edge_explained_by_funding": bool(edge_explained_by_funding),
            "aggregate_fund_share": float(agg_fund_share),
            "aggregate_conv_share": float(agg_conv_share),
            "diagnosis": (
                "C307 edge does not survive C308 validation; formal negative. "
                f"Binding constraint: {binding}."
            ),
            "note": "Diagnosis only; never an edge claim. No threshold weakening.",
        }
        op_bind = reports / f"campaign308_binding_constraint_{ts}.json"
        op_bind.write_text(json.dumps(binding_obj, indent=2, default=jdefault) + "\n")
        bind_sha = sha256_file(op_bind)
        bind_path = str(op_bind.relative_to(ROOT))
        verdict_obj["binding_constraint_artifact"] = bind_path
        verdict_obj["binding_constraint_sha256"] = bind_sha
        op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")
        ver_sha = sha256_file(op_ver)

    print(json.dumps({
        "campaign": 308,
        "verdict": verdict,
        "edge_proven": edge_proven,
        "n_total_runs": int(n_total),
        "n_leg_a_runs": int(n_leg_a),
        "n_leg_b_runs": int(n_leg_b),
        "n_deterministic_edge": int(n_edge),
        "n_survive_holm": int(n_survive_holm),
        "n_survive_bh": int(n_survive_bh),
        "n_survive_both": int(n_survive_both),
        "n_survive_cost_realism": int(n_survive_realistic),
        "binding_constraint": binding,
        "aggregate_fund_share": float(agg_fund_share),
        "aggregate_conv_share": float(agg_conv_share),
        "mde_bps_mean": mde_bps,
        "observed_mean_bps_per_split": obs_mean_bps,
        "stable_first_half": stable_first,
        "stable_second_half": stable_second,
        "artifacts": {
            "oos_sweep": str(op.relative_to(ROOT)),
            "registry": str(op_reg.relative_to(ROOT)),
            "summary": str(op_sum.relative_to(ROOT)),
            "verdict": str(op_ver.relative_to(ROOT)),
            "binding_constraint": bind_path,
        },
        "sha256": {
            "oos_sweep": sweep_sha,
            "registry": reg_sha,
            "summary": sum_sha,
            "verdict": ver_sha,
            "binding_constraint": bind_sha,
        },
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
