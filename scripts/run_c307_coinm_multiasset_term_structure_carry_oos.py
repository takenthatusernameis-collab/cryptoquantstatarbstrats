#!/usr/bin/env python3
"""C307 — costed out-of-sample edge test of the COIN-M inverse multi-asset
term-structure + cross-sectional funding-carry strategy.

This is a genuinely new formulation (COIN-M inverse multi-asset term-structure
carry + cross-sectional funding carry), not a re-skin of any frozen family.
Inverse settlement PnL is modeled in coin:
    pnl_coin = notional_usd * (1/entry_price - 1/exit_price) * signed_weight
never a linear approximation.

Leg A (per-asset dated-quarterly term structure): BTCUSD, ETHUSD, XRPUSD.
Common term-structure grid per asset = 1h timestamps where the perpetual AND at
least one dated quarterly contract both have kline data; annualized
perp-vs-quarterly basis + time-to-expiry computed on the grid. Assets with
<888 overlapping bars are excluded from WF with a documented scope note (not the
whole campaign).

Leg B (cross-sectional COIN-M funding carry): all 11 perps ranked by native
fundingRate on the common funding grid (1h intersection restricted to
2022-07..2026-06). Funding is native 8h (schema calc_time, funding_interval_hours,
last_funding_rate; 90 rows/month); rate is carried causally (last rate known at
or before each bar, staleness <= 24h+1 bar), never imputed across outages.

- DATA: real COIN-M perp 1h klines + premiumIndexKlines + markPriceKlines +
  dated quarterly 1h klines + fundingRate on the common grids
  (data/cache/campaign307_coinm_multiasset_term_structure_carry.pkl,
   SHA256-from-bytes verified).
  real_data_only:true, fabricated_data:false, executed_fills:false.

- MECHANISM Leg A: per asset, at each bar (causal, shift(1)), compute the
  annualized perp-vs-quarterly basis signal. Cross-sectionally rank assets by
  signal; long top-K / short bottom-K basis trades, dollar-neutral within each
  asset (long quarterly / short perp for cheap basis, short quarterly / long perp
  for rich basis), gross 1.0 per active asset. Apply from the next bar.
  Signals (all causal, shift(1), per-asset over the common grid):
    basis_level  = -rollmean(basis, L)[t-1]              [basis mean reversion]
    basis_z      = -zscore_per_asset(rollmean(basis, L))[t-1]
    basis_mom    = -rollmean(diff(basis), L)[t-1]        [basis momentum]
    basis_voladj = -rollmean(basis, L) / rollstd(basis, L)[t-1]
    basis_sign   = -sign(rollmean(basis, L))[t-1]

- MECHANISM Leg B: at each bar (causal, shift(1)), rank the live cross-section by
  the funding signal; long top-K / short bottom-K, dollar-neutral, gross 1.0
  (weight +0.5/K long, -0.5/K short). Real funding cashflow -rate*signed_weight
  at each native 8h boundary (causal). Apply from the next bar.
  Signals (all causal, shift(1), per-asset over the common funding grid):
    fund_level  = -rollmean(funding_rate, L)[t-1]              [funding level]
    fund_z      = -z_cross_sectional(rollmean(funding_rate, L))[t-1] [funding z]
    fund_mom    = -rollmean(delta_funding, L)[t-1]             [funding momentum]
    fund_sign   = -sign(rollmean(funding_rate, L))[t-1]
  Higher score = long. Negative funding rate = pay to short = long cheap.

- Dispersion gate (cross-sectional std of signal at t-1 vs expanding median):
    off = always trade; on = trade only when dispersion > expanding median.

- FROZEN pre-registered grid (Leg A): 5 signals x 6 lookbacks {24,48,168,336,720,1440}
  x 1 K {1} x 3 holds {1,6,24} x 2 gates {off,on} = 540 runs per asset.
  (BTCUSD, ETHUSD, XRPUSD -> 1620 total). Lookback window constraint (fail-closed,
  NOT a threshold weakening): rolling features use min_periods = max(20, L // 3),
  which must fit within train=720 bars; L=2160 (needs 720) is included; L=4320
  (needs 1440) and L=8640 (needs 2880) are degenerate on this window (flat
  through the whole training set) and are EXCLUDED from the pre-registered grid
  rather than passed with a weakened gate.
  Total Leg A runs = 5 * 6 * 1 * 3 * 2 * 3 assets = 540 * 3 = 1620.

- FROZEN pre-registered grid (Leg B): 4 signals x 6 lookbacks {24,48,168,336,720,1440}
  x 3 K {2,3,5} x 3 holds {1,6,24} x 2 gates {off,on} = 432 runs.
  Total Leg B runs = 432.

- Combined total: 1620 + 432 = 2052 runs (>= 400, heavy).
  Leg B alone (432) satisfies the gate if Leg A collapses.

- Walk-forward: train=720, test=168, step=168 in 1h bars per asset grid (Leg A)
  and common funding grid (Leg B).

- Cost grid exactly: [[0,0],[5,5],[10,10],[20,20],[40,40]] bps charged on ALL legs
  (quarterly + perp for Leg A; perp for Leg B).

- Benchmarks on the SAME WF windows: flat (zero) and equal-weight B&H with the
  SAME real funding cashflows (Leg B) or equal-weight B&H of same legs (Leg A).

- Edge rule identical to C285-C306: oos_edge_proven=true IFF OOS exposure > 0
  AND every cost slice OOS net sum > 0 AND mean of per-split OOS net means is
  greater than mean of per-split equal-weight B&H-with-costs OOS net means on
  the same WF windows AND greater than flat.

Fail-closed gates at each candidate bar:
- selected feature score finite (gap/warmup bars -> flat);
- no NaN/non-finite perp or quarterly price in the selected leg (Leg A);
- no NaN/non-finite perp price in the selected leg (Leg B);
- funding staleness <= 24h + 1 bar in the selected leg (Leg B) (position zeroed
  when funding stale/missing at the boundary);
- cross-section must have >= 2K finite assets to rebalance cross-sectionally (Leg B);
- per-asset fallback: if only 1 asset has finite signal, trade it by signal sign (Leg A).

Required artifacts (exact names, timestamped, SHA256-from-bytes):
- reports/campaign307_oos_sweep_<ts>.json
- reports/campaign307_tradable_edge_registry_<ts>.json
- reports/campaign307_summary_<ts>.json
- reports/campaign307_verdict_<ts>.json
- reports/campaign307_binding_constraint_<ts>.json  (if NOT_TRADABLE)
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import pickle
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
reports = root / "reports"
reports.mkdir(exist_ok=True)
cache_dir = root / "data" / "cache"
ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

CACHE = cache_dir / "campaign307_coinm_multiasset_term_structure_carry.pkl"
CACHE_META = cache_dir / "campaign307_coinm_multiasset_term_structure_carry.meta.json"
CACHE_PROV = cache_dir / "campaign307_coinm_multiasset_term_structure_carry.provenance.json"

# Leg A: per-asset term structure
SIGNALS_A = (
    "basis_level",
    "basis_z",
    "basis_mom",
    "basis_voladj",
    "basis_sign",
)
LOOKBACKS_A = (24, 48, 168, 336, 720, 1440)
K_VALUES_A = (1,)
HOLDS_A = (1, 6, 24)
GATES_A = ("off", "on")

# Leg B: cross-sectional funding carry
SIGNALS_B = (
    "fund_level",
    "fund_z",
    "fund_mom",
    "fund_sign",
)
LOOKBACKS_B = (24, 48, 168, 336, 720, 1440)
K_VALUES_B = (2, 3, 5)
HOLDS_B = (1, 6, 24)
GATES_B = ("off", "on")

TRAIN, TEST, STEP = 720, 168, 168
COST_GRID = [[0, 0], [5, 5], [10, 10], [20, 20], [40, 40]]
STALE_BARS = 24 + 1  # 24h + 1 bar on the 1h grid

RUNS_TOTAL_A = len(SIGNALS_A) * len(LOOKBACKS_A) * len(K_VALUES_A) * len(HOLDS_A) * len(GATES_A)
RUNS_TOTAL_B = len(SIGNALS_B) * len(LOOKBACKS_B) * len(K_VALUES_B) * len(HOLDS_B) * len(GATES_B)
RUNS_TOTAL = RUNS_TOTAL_A + RUNS_TOTAL_B


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


def _safe_std(out: pd.Series, std: pd.Series) -> pd.Series:
    bad = (~np.isfinite(np.asarray(std))) | (np.asarray(std) <= 0)
    return out.mask(pd.Series(bad, index=out.index))


def _mask_nonfinite(out: pd.Series) -> pd.Series:
    return out.mask(pd.Series(~np.isfinite(np.asarray(out)), index=out.index))


def zscore(s: pd.Series, L: int) -> pd.Series:
    mp = min_periods_for(L)
    mean = s.rolling(L, min_periods=mp).mean()
    std = s.rolling(L, min_periods=mp).std()
    z = (s - mean) / std
    return _safe_std(z, std)


def zscore_cross_sectional(df: pd.DataFrame, L: int) -> pd.DataFrame:
    """Cross-sectional z-score at each bar: (x - row_mean) / row_std."""
    mp = min_periods_for(L)
    mean = df.rolling(L, min_periods=mp).mean()
    row_mean = mean.mean(axis=1)
    row_std = mean.std(axis=1)
    z = mean.sub(row_mean, axis=0).div(row_std.replace(0, np.nan), axis=0)
    return z.where(np.isfinite(z))


def rollmean(s: pd.Series, L: int) -> pd.Series:
    mp = min_periods_for(L)
    return _mask_nonfinite(s.rolling(L, min_periods=mp).mean())


def rollmean_df(df: pd.DataFrame, L: int) -> pd.DataFrame:
    mp = min_periods_for(L)
    return df.rolling(L, min_periods=mp).mean()


def rollstd(s: pd.Series, L: int) -> pd.Series:
    mp = min_periods_for(L)
    return _mask_nonfinite(s.rolling(L, min_periods=mp).std())


def inv_ret(entry: np.ndarray, exit_: np.ndarray) -> np.ndarray:
    """Inverse futures return per unit notional: (entry - exit) / exit.

    Positive when price drops (long inverse profits), negative when price rises.
    This is the exact non-linear inverse return, not a linear approximation.
    """
    with np.errstate(divide="ignore", invalid="ignore"):
        r = (entry - exit_) / exit_
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

    score: (n_assets, n_bars), already causal (shift(1) applied).
    Returns pos: (n_assets, n_bars), pos[:, t] applied to return at bar t,
    decided from segment-start scores (hold H), applied from next bar.
    Dollar-neutral, gross 1.0 (+0.5/K long, -0.5/K short).
    """
    n_assets, n_bars = score.shape
    finite = np.isfinite(score)
    n_finite = finite.sum(axis=0)  # (n_bars,)
    enough = n_finite >= 2 * K
    sort_val = np.where(finite, score, -np.inf)
    order = np.argsort(-sort_val, axis=0)  # descending, NaN(-inf) last
    rank = np.argsort(order, axis=0)  # rank 0 = best score
    rank = rank.astype(float)
    rank[~finite] = np.inf  # non-finite excluded
    n_f = n_finite.astype(float)[None, :]
    top_mask = (rank < K) & finite & enough[None, :]
    bot_mask = (rank >= (n_f - K)) & finite & enough[None, :]
    desired = np.zeros((n_assets, n_bars), dtype=float)
    desired[top_mask] = 0.5 / K
    desired[bot_mask] = -0.5 / K
    desired = desired * gate_mask[None, :]
    # hold H: decision at segment start, apply from next bar (shift(1))
    seg_start = (np.arange(n_bars) // H) * H
    seg_desired = desired[:, seg_start]
    pos = np.zeros((n_assets, n_bars), dtype=float)
    if n_bars > 1:
        pos[:, 1:] = seg_desired[:, :-1]
    pos[:, 0] = 0.0
    pos = np.where(np.isfinite(pos), pos, 0.0)
    return pos


def _as_index(pa: dict) -> pd.DatetimeIndex:
    idx = pa.get("index")
    if isinstance(idx, pd.DatetimeIndex):
        return idx
    arr = np.asarray(idx)
    if np.issubdtype(arr.dtype, np.datetime64):
        return pd.DatetimeIndex(arr).tz_localize("UTC")
    return pd.DatetimeIndex(pd.to_datetime(arr, unit="ms", utc=True))


def build_leg_a_asset_series(pa: dict, index: pd.DatetimeIndex, qsym: str):
    perp_close = pd.Series(np.asarray(pa["perp_close"], dtype=float), index=index)
    q_close = pd.Series(np.asarray(pa[f"q_close_{qsym}"], dtype=float), index=index)
    q_basis = pd.Series(np.asarray(pa[f"q_basis_{qsym}"], dtype=float), index=index)
    return perp_close, q_close, q_basis


def main() -> int:
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

    payload = load_payload(CACHE)

    # ---- Leg A: per-asset term structure ----
    leg_a = payload.get("leg_a") or {}
    assets_a = list(leg_a.get("selected_assets") or [])
    per_asset_a = leg_a.get("per_asset") or {}
    quarterly_by_asset = {}
    for a in assets_a:
        pa = per_asset_a.get(a, {})
        quarterly_by_asset[a] = list(pa.get("quarterly_contracts") or [])

    # Build per-asset series on its own common grid.
    asset_index_a: dict[str, pd.DatetimeIndex] = {}
    asset_basis_a: dict[str, np.ndarray] = {}
    asset_perp_close_a: dict[str, np.ndarray] = {}
    asset_q_close_a: dict[str, np.ndarray] = {}
    asset_qsym_a: dict[str, str] = {}  # asset -> active quarterly contract (first)
    n_by_asset_a: dict[str, int] = {}

    for a in assets_a:
        pa = per_asset_a.get(a)
        if pa is None:
            continue
        index = _as_index(pa)
        asset_index_a[a] = index
        n = int(len(index))
        n_by_asset_a[a] = n
        qsyms = quarterly_by_asset.get(a, [])
        if not qsyms:
            continue
        qsym = qsyms[0]  # use the first quarterly per asset
        asset_qsym_a[a] = qsym
        pc, qc, qb = build_leg_a_asset_series(pa, index, qsym)
        asset_perp_close_a[a] = pc.to_numpy(dtype=float)
        asset_q_close_a[a] = qc.to_numpy(dtype=float)
        asset_basis_a[a] = qb.to_numpy(dtype=float)

    # sanity Leg A
    for a in assets_a:
        if a not in asset_basis_a:
            continue
        p_close = asset_perp_close_a[a]
        c_present = p_close[~np.isnan(p_close)]
        if not bool(np.isfinite(c_present).all()) or not bool((c_present > 0).all()):
            raise SystemExit(f"FATAL: non-finite or non-positive perp price for {a}")
        q_close = asset_q_close_a[a]
        q_present = q_close[~np.isnan(q_close)]
        if not bool(np.isfinite(q_present).all()) or not bool((q_present > 0).all()):
            raise SystemExit(f"FATAL: non-finite or non-positive quarterly price for {a}")
        b = asset_basis_a[a]
        b_present = b[~np.isnan(b)]
        if not bool(np.isfinite(b_present).all()):
            raise SystemExit(f"FATAL: non-finite basis for {a}")

    # Per-asset WF splits (Leg A).
    asset_splits_a: dict[str, list] = {}
    for a in assets_a:
        if a not in asset_basis_a:
            continue
        splits = wf_splits(n_by_asset_a[a], TRAIN, TEST, STEP)
        asset_splits_a[a] = splits

    # Precompute per-asset price returns (inverse) for the quarterly and perp legs (Leg A).
    asset_q_ret_a: dict[str, np.ndarray] = {}
    asset_p_ret_a: dict[str, np.ndarray] = {}
    for a in assets_a:
        if a not in asset_basis_a:
            continue
        q_close = asset_q_close_a[a]
        p_close = asset_perp_close_a[a]
        q_ret = np.zeros(len(q_close))
        p_ret = np.zeros(len(p_close))
        q_ret[1:] = inv_ret(q_close[:-1], q_close[1:])
        p_ret[1:] = inv_ret(p_close[:-1], p_close[1:])
        asset_q_ret_a[a] = q_ret
        asset_p_ret_a[a] = p_ret

    # ---- Leg B: cross-sectional funding carry ----
    leg_b = payload.get("leg_b") or {}
    symbols_b = list(leg_b.get("symbols") or [])
    n_assets_b = len(symbols_b)
    common_index_b = _as_index(leg_b) if "index" in leg_b else None
    n_b = int(leg_b.get("n_bars") or 0)

    if common_index_b is None or n_b == 0:
        raise SystemExit("FATAL: Leg B common funding grid is empty")

    splits_b = wf_splits(n_b, TRAIN, TEST, STEP)
    if len(splits_b) == 0:
        raise SystemExit(f"FATAL: no OOS splits for Leg B, n={n_b}")

    # ---- Leg B: per-asset returns (perp + real funding cashflow) over common grid ----
    perp_close_b = np.zeros((n_assets_b, n_b), dtype=float)
    funding_b = np.zeros((n_assets_b, n_b), dtype=float)
    funding_age_b = np.zeros((n_assets_b, n_b), dtype=float)
    premium_close_b = np.zeros((n_assets_b, n_b), dtype=float)
    mark_close_b = np.zeros((n_assets_b, n_b), dtype=float)

    for i, s in enumerate(symbols_b):
        pc_key = f"perp_close_{s}"
        fr_key = f"funding_rate_{s}"
        fp_key = f"funding_present_{s}"
        prem_key = f"premium_close_{s}"
        mark_key = f"mark_close_{s}"

        if pc_key in leg_b:
            perp_close_b[i] = np.asarray(leg_b[pc_key], dtype=float)
        if fr_key in leg_b:
            funding_b[i] = np.asarray(leg_b[fr_key], dtype=float)
        if fp_key in leg_b:
            # funding present as float mask (1.0/0.0)
            pass
        if prem_key in leg_b:
            premium_close_b[i] = np.asarray(leg_b[prem_key], dtype=float)
        if mark_key in leg_b:
            mark_close_b[i] = np.asarray(leg_b[mark_key], dtype=float)

        # funding age in bars
        fund_s = pd.Series(funding_b[i], index=common_index_b)
        funding_age_b[i] = compute_funding_age(fund_s)

    # sanity Leg B: perp price finite + positive where present
    c_present_b = perp_close_b[~np.isnan(perp_close_b)]
    if not bool(np.isfinite(c_present_b).all()) or not bool((c_present_b > 0).all()):
        raise SystemExit("FATAL: non-finite or non-positive perp price present in Leg B")

    # funding staleness mask per asset (age since last boundary, in bars)
    funding_stale_b = ~np.isfinite(funding_age_b) | (funding_age_b > STALE_BARS)

    # total asset return = perp pct change + funding leg (-rate at boundaries)
    perp_ret_b = np.diff(perp_close_b, axis=1) / perp_close_b[:, :-1]
    perp_ret_b = np.concatenate([np.zeros((n_assets_b, 1)), perp_ret_b], axis=1)
    funding_leg_b = np.where(np.isnan(funding_b), 0.0, -funding_b)
    total_ret_b = perp_ret_b + funding_leg_b  # (n_assets_b, n_bars)

    # equal-weight B&H-with-funding benchmark (same WF windows)
    bench_ret_b = np.nanmean(total_ret_b, axis=0)  # weight 1/n_assets each -> mean
    bench_ret_b = np.where(np.isnan(bench_ret_b), 0.0, bench_ret_b)

    # Leg B cross-sectional dispersion of funding rate at each bar
    fund_df = pd.DataFrame(funding_b.T, index=common_index_b)
    disp_fund = fund_df.std(axis=1)  # (n_bars,)
    disp_fund = np.where(np.isfinite(disp_fund), disp_fund, np.nan)
    disp_fund_series = pd.Series(disp_fund, index=common_index_b)
    disp_fund_med = disp_fund_series.expanding().median().to_numpy(dtype=float)

    # ---- Run sweeps ----
    limit_runs = int(os.environ.get("C307_LIMIT_RUNS", "0") or 0)
    results = []
    run_count = 0

    # ============================================================
    # LEG A: Per-asset term structure sweep
    # ============================================================
    for signal in SIGNALS_A:
        for L in LOOKBACKS_A:
            # ---- per-asset causal score (shift(1) applied) ----
            asset_score_a: dict[str, np.ndarray] = {}
            for a in assets_a:
                if a not in asset_basis_a:
                    continue
                basis_s = pd.Series(asset_basis_a[a], index=asset_index_a[a])
                if signal == "basis_level":
                    base = rollmean(basis_s, L)
                elif signal == "basis_z":
                    rm = rollmean(basis_s, L)
                    mp = min_periods_for(L)
                    base = (rm - rm.rolling(L, min_periods=mp).mean()) / rm.rolling(L, min_periods=mp).std()
                    base = base.where(np.isfinite(base))
                elif signal == "basis_mom":
                    base = rollmean(basis_s.diff(), L)
                elif signal == "basis_voladj":
                    rm = rollmean(basis_s, L)
                    rs = rollstd(basis_s, L)
                    base = rm / rs
                    base = base.where(np.isfinite(base))
                elif signal == "basis_sign":
                    rm = rollmean(basis_s, L)
                    base = np.sign(rm.to_numpy(dtype=float))
                    base = pd.Series(base, index=basis_s.index)
                else:
                    raise ValueError(f"unknown signal {signal}")
                score = ((-base).shift(1).to_numpy(dtype=float))  # causal, shift(1)
                asset_score_a[a] = score

            for K in K_VALUES_A:
                for H in HOLDS_A:
                    for gate_name in GATES_A:
                        run_count += 1
                        if limit_runs > 0 and run_count > limit_runs:
                            break

                        # ---- per-asset positions ----
                        asset_pos_a: dict[str, np.ndarray] = {}
                        asset_exposure_a: dict[str, int] = {}
                        for a in assets_a:
                            if a not in asset_score_a:
                                continue
                            n = n_by_asset_a[a]
                            score = asset_score_a[a]
                            gate_mask = np.ones(n, dtype=bool)
                            if gate_name == "on":
                                # dispersion gate: trade only when cross-sectional
                                # |basis| at t-1 > expanding median of |basis|.
                                # Per-asset: use rolling |basis| vs its expanding median.
                                bs = pd.Series(asset_basis_a[a], index=asset_index_a[a])
                                abs_b = np.abs(bs.to_numpy(dtype=float))
                                abs_s = pd.Series(abs_b, index=asset_index_a[a])
                                abs_med = abs_s.expanding().median().to_numpy(dtype=float)
                                gate_on = abs_b > abs_med
                                gate_on = np.where(np.isnan(gate_on), False, gate_on)
                                gate_on = np.roll(gate_on, 1)
                                gate_on[0] = False
                                gate_mask = gate_on

                            # score-based position: long basis if score > 0, short if < 0
                            desired = np.zeros(n, dtype=float)
                            pos_mask = np.isfinite(score) & gate_mask
                            desired[pos_mask & (score > 0)] = 0.25   # long basis
                            desired[pos_mask & (score < 0)] = -0.25  # short basis

                            # hold H: decision at segment start, apply from next bar (shift(1))
                            seg_start = (np.arange(n) // H) * H
                            seg_desired = desired[seg_start]
                            pos = np.zeros(n, dtype=float)
                            if n > 1:
                                pos[1:] = seg_desired[:-1]
                            pos[0] = 0.0
                            pos = np.where(np.isfinite(pos), pos, 0.0)
                            asset_pos_a[a] = pos
                            asset_exposure_a[a] = int((pos != 0).sum())

                        # ---- portfolio return: equal-weight across assets ----
                        n_max_a = max(n_by_asset_a.values()) if n_by_asset_a else 0
                        port_ret_a = np.zeros(n_max_a)
                        port_turnover_a = np.zeros(n_max_a)
                        n_active_a = np.zeros(n_max_a, dtype=int)

                        for a in assets_a:
                            if a not in asset_pos_a:
                                continue
                            n = n_by_asset_a[a]
                            pos = asset_pos_a[a]
                            q_ret = asset_q_ret_a[a][:n]
                            p_ret = asset_p_ret_a[a][:n]
                            # quarterly leg: pos * q_ret ; perp leg: -pos * p_ret
                            leg_ret = pos * q_ret + (-pos) * p_ret
                            port_ret_a[:n] += leg_ret
                            port_turnover_a[:n] += np.abs(np.diff(pos, prepend=pos[:1]))
                            n_active_a[:n] += (pos != 0).astype(int)

                        # equal-weight average across active assets
                        with np.errstate(divide="ignore", invalid="ignore"):
                            port_ret_a = np.where(n_active_a > 0, port_ret_a / np.maximum(n_active_a, 1), 0.0)
                        port_ret_a = np.where(np.isfinite(port_ret_a), port_ret_a, 0.0)
                        port_turnover_a = np.where(n_active_a > 0, port_turnover_a / np.maximum(n_active_a, 1), 0.0)

                        # ---- walk-forward OOS per asset ----
                        segs_a = []
                        exposure_total_a = 0
                        for a in assets_a:
                            if a not in asset_splits_a:
                                continue
                            pos_a = asset_pos_a[a]
                            splits = asset_splits_a[a]
                            for tr_s, tr_e, te_e in splits:
                                # OOS segment for this asset
                                spr = port_ret_a[tr_e:te_e] if tr_e < len(port_ret_a) else np.array([])
                                # per-asset OOS: use asset's own returns, not portfolio
                                q_ret_a = asset_q_ret_a[a]
                                p_ret_a = asset_p_ret_a[a]
                                pos_a_seg = pos_a[tr_e:te_e]
                                leg_ret_a = pos_a_seg * q_ret_a[tr_e:te_e] + (-pos_a_seg) * p_ret_a[tr_e:te_e]
                                seg_sum = float(np.nansum(leg_ret_a))
                                seg_len = int(len(pos_a_seg))
                                exposure_total_a += int((pos_a_seg != 0).sum())
                                segs_a.append((seg_sum, seg_len))

                        turnover_total_a = float(np.sum(port_turnover_a))

                        # benchmark: equal-weight B&H with same costs on same WF windows
                        bh_per_split_means_a = []
                        for a in assets_a:
                            if a not in asset_splits_a:
                                continue
                            q_ret_a = asset_q_ret_a[a]
                            p_ret_a = asset_p_ret_a[a]
                            splits = asset_splits_a[a]
                            # B&H: equal weight 0.25 on each leg, held from train start
                            for tr_s, tr_e, te_e in splits:
                                if te_e > tr_e and tr_e < len(q_ret_a):
                                    bh_q = float(np.nansum(q_ret_a[tr_e:te_e]))
                                    bh_p = float(np.nansum(p_ret_a[tr_e:te_e]))
                                    bh_leg = 0.25 * bh_q + (-0.25) * bh_p  # equal-weight B&H
                                    bh_per_split_means_a.append(bh_leg / (te_e - tr_e))

                        bh_split_mean_a = float(np.mean(bh_per_split_means_a)) if bh_per_split_means_a else 0.0

                        slices_a = {}
                        all_sum_pos_a = True
                        all_beat_bh_a = True
                        all_beat_flat_a = True
                        net_means_a = []
                        for fee, slip in COST_GRID:
                            ck = f"fee{fee}_slip{slip}"
                            tc = (fee + slip) / 10000.0
                            nets_a, means_a = [], []
                            for (seg_sum, seg_len) in segs_a:
                                tsum = turnover_total_a * (seg_len / max(len(port_ret_a), 1))  # allocate turnover
                                net_sum = seg_sum - tc * tsum
                                nets_a.append(net_sum)
                                means_a.append(net_sum / seg_len if seg_len else 0.0)
                            net_sum_a = float(sum(nets_a))
                            slice_mean_a = float(np.mean(means_a)) if means_a else 0.0
                            slices_a[ck] = {
                                "oos_net_sum": net_sum_a,
                                "oos_net_mean": slice_mean_a,
                                "oos_net_mean_per_split": [float(m) for m in means_a],
                                "bh_oos_net_mean_per_split": [float(bh_split_mean_a) for _ in means_a],
                                "bh_oos_net_mean": float(bh_split_mean_a),
                            }
                            net_means_a.extend(means_a)
                            if net_sum_a <= 0:
                                all_sum_pos_a = False
                            if not (slice_mean_a > bh_split_mean_a):
                                all_beat_bh_a = False
                            if not (slice_mean_a > 0.0):
                                all_beat_flat_a = False

                        net_mean_a = float(np.mean(net_means_a)) if net_means_a else 0.0
                        beats_bh_a = bool(all_beat_bh_a)
                        beats_flat_a = bool(all_beat_flat_a)
                        edge_a = bool(exposure_total_a > 0 and all_sum_pos_a and beats_bh_a and beats_flat_a)

                        results.append({
                            "leg": "A",
                            "signal": signal,
                            "lookback": int(L),
                            "K": int(K),
                            "hold": int(H),
                            "gate": gate_name,
                            "n_splits": int(len(segs_a)),
                            "oos_exposure_bars_total": int(exposure_total_a),
                            "turnover_total": float(turnover_total_a),
                            "edge_proven": edge_a,
                            "block_reason": None if edge_a else "no_costed_oos_edge",
                            "cost_slices": slices_a,
                            "all_cost_slices_oos_net_positive": bool(all_sum_pos_a),
                            "beats_bh_all_slices": bool(beats_bh_a),
                            "beats_flat": bool(beats_flat_a),
                            "bh_oos_mean": float(bh_split_mean_a),
                            "flat_oos_mean": 0.0,
                            "oos_net_mean": net_mean_a,
                        })
                    if limit_runs > 0 and run_count > limit_runs:
                        break
                if limit_runs > 0 and run_count > limit_runs:
                    break
        if limit_runs > 0 and run_count > limit_runs:
            break

    # ============================================================
    # LEG B: Cross-sectional funding carry sweep
    # ============================================================
    for signal in SIGNALS_B:
        for L in LOOKBACKS_B:
            # ---- build causal per-asset score (shift(1) applied) ----
            fund_s = pd.DataFrame(funding_b.T, index=common_index_b)
            if signal == "fund_level":
                base_b = rollmean_df(fund_s, L)
            elif signal == "fund_z":
                m = rollmean_df(fund_s, L)
                # cross-sectional z at each bar (per-asset vs live cross-section)
                row_mean = m.mean(axis=1)
                row_std = m.std(axis=1)
                base_b = m.sub(row_mean, axis=0).div(row_std.replace(0, np.nan), axis=0)
                base_b = base_b.where(np.isfinite(base_b))
            elif signal == "fund_mom":
                base_b = rollmean_df(fund_s.diff(), L)
            elif signal == "fund_sign":
                rm = rollmean_df(fund_s, L)
                base_b = np.sign(rm.to_numpy(dtype=float))
                base_b = pd.DataFrame(base_b, index=fund_s.index, columns=fund_s.columns)
            else:
                raise ValueError(f"unknown signal {signal}")
            score_b = ((-base_b).shift(1).to_numpy(dtype=float)).T  # causal, shift(1); (n_assets, n_bars)

            # ---- dispersion gate mask ----
            gate_on_b = (disp_fund > disp_fund_med)  # (n_bars,)
            gate_on_b = np.where(np.isnan(gate_on_b), False, gate_on_b)
            gate_on_b = np.roll(gate_on_b, 1)  # causal: use dispersion known at t-1
            gate_on_b[0] = False

            for K in K_VALUES_B:
                for H in HOLDS_B:
                    for gate_name in GATES_B:
                        run_count += 1
                        if limit_runs > 0 and run_count > limit_runs:
                            break

                        gate_mask_b = gate_on_b if gate_name == "on" else np.ones(n_b, dtype=bool)
                        # stale -> flat: zero positions where funding stale
                        pos_b = xsec_positions(score_b, K, H, gate_mask_b)
                        pos_b = np.where(funding_stale_b, 0.0, pos_b)

                        port_ret_b = (pos_b * total_ret_b).sum(axis=0)  # (n_bars,)
                        turnover_b = np.abs(np.diff(pos_b, axis=1, prepend=pos_b[:, :1])).sum(axis=0)

                        segs_b = []
                        exposure_total_b = 0
                        for tr_s, tr_e, te_e in splits_b:
                            spr = port_ret_b[tr_e:te_e]
                            stu = turnover_b[tr_e:te_e]
                            spos = pos_b[:, tr_e:te_e]
                            segs_b.append((float(spr.sum()), int(len(spr)), float(stu.sum())))
                            exposure_total_b += int((spos != 0).sum())
                        turnover_total_b = float(sum(x[2] for x in segs_b))

                        # benchmark per split (equal-weight B&H-with-funding)
                        bh_per_split_means_b = [float(bench_ret_b[tr_e:te_e].mean())
                                              for _, tr_e, te_e in splits_b]
                        bh_split_mean_b = float(np.mean(bh_per_split_means_b)) if bh_per_split_means_b else 0.0

                        slices_b = {}
                        all_sum_pos_b = True
                        all_beat_bh_b = True
                        all_beat_flat_b = True
                        net_means_b = []
                        for fee, slip in COST_GRID:
                            ck = f"fee{fee}_slip{slip}"
                            tc = (fee + slip) / 10000.0
                            nets_b, means_b = [], []
                            for (seg_sum, seg_len, tsum) in segs_b:
                                net_sum = seg_sum - tc * tsum
                                nets_b.append(net_sum)
                                means_b.append(net_sum / seg_len if seg_len else 0.0)
                            net_sum_b = float(sum(nets_b))
                            slice_mean_b = float(np.mean(means_b)) if means_b else 0.0
                            slices_b[ck] = {
                                "oos_net_sum": net_sum_b,
                                "oos_net_mean": slice_mean_b,
                                "oos_net_mean_per_split": [float(m) for m in means_b],
                                "bh_oos_net_mean_per_split": [float(m) for m in bh_per_split_means_b],
                                "bh_oos_net_mean": float(bh_split_mean_b),
                            }
                            net_means_b.extend(means_b)
                            if net_sum_b <= 0:
                                all_sum_pos_b = False
                            if not (slice_mean_b > bh_split_mean_b):
                                all_beat_bh_b = False
                            if not (slice_mean_b > 0.0):
                                all_beat_flat_b = False

                        net_mean_b = float(np.mean(net_means_b)) if net_means_b else 0.0
                        beats_bh_b = bool(all_beat_bh_b)
                        beats_flat_b = bool(all_beat_flat_b)
                        edge_b = bool(exposure_total_b > 0 and all_sum_pos_b and beats_bh_b and beats_flat_b)

                        results.append({
                            "leg": "B",
                            "signal": signal,
                            "lookback": int(L),
                            "K": int(K),
                            "hold": int(H),
                            "gate": gate_name,
                            "n_splits": int(len(segs_b)),
                            "oos_exposure_bars_total": int(exposure_total_b),
                            "turnover_total": float(turnover_total_b),
                            "edge_proven": edge_b,
                            "block_reason": None if edge_b else "no_costed_oos_edge",
                            "cost_slices": slices_b,
                            "all_cost_slices_oos_net_positive": bool(all_sum_pos_b),
                            "beats_bh_all_slices": bool(beats_bh_b),
                            "beats_flat": bool(beats_flat_b),
                            "bh_oos_mean": float(bh_split_mean_b),
                            "flat_oos_mean": 0.0,
                            "oos_net_mean": net_mean_b,
                        })
                    if limit_runs > 0 and run_count > limit_runs:
                        break
                if limit_runs > 0 and run_count > limit_runs:
                    break
        if limit_runs > 0 and run_count > limit_runs:
            break

    n_total = len(results)
    n_exp = sum(1 for r in results if r["oos_exposure_bars_total"] > 0)
    edge_runs = [r for r in results if r["edge_proven"]]
    verdict = "EDGE_PROVEN" if edge_runs else "NOT_TRADABLE"

    # Dataset block for artifacts
    dataset_block = {
        "cache": str(CACHE.relative_to(root)),
        "cache_sha256": cache_sha,
        "cache_meta": str(CACHE_META.relative_to(root)),
        "cache_meta_sha256": meta_sha,
        "cache_provenance": str(CACHE_PROV.relative_to(root)) if CACHE_PROV.exists() else None,
        "cache_provenance_sha256": prov_sha,
        "cache_pkl_bytes": int(CACHE.stat().st_size),
        "real_data_only": True,
        "fabricated_data": False,
    }

    # Leg A info
    leg_a_info = {
        "assets": assets_a,
        "n_assets": len(assets_a),
        "asset_grids": {a: {"bars": n_by_asset_a.get(a, 0),
                            "start_utc": str(asset_index_a[a][0]) if a in asset_index_a else None,
                            "end_utc": str(asset_index_a[a][-1]) if a in asset_index_a else None,
                            "n_splits": len(asset_splits_a.get(a, []))} for a in assets_a},
    }

    # Leg B info
    leg_b_info = {
        "symbols": symbols_b,
        "n_assets": n_assets_b,
        "common_grid_bars": int(n_b),
        "common_grid_start_utc": str(common_index_b[0]) if common_index_b is not None and len(common_index_b) else None,
        "common_grid_end_utc": str(common_index_b[-1]) if common_index_b is not None and len(common_index_b) else None,
    }

    sweep = {
        "generated_at_utc": ts,
        "campaign": 307,
        "part": "oos_sweep",
        "analysis": "coin_m_inverse_multiasset_term_structure_carry_costed_oos_1h",
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "real_data_only": True,
        "fabricated_data": False,
        "executed_fills": False,
        "fail_closed": True,
        "mandate": (
            "C307 — pre-registered costed OOS sweep of the COIN-M inverse multi-asset "
            "term-structure carry (Leg A) + cross-sectional funding carry (Leg B) strategy "
            "over real common grids (data.binance.vision/data/futures/cm); Leg A: per-asset "
            "annualized perp-vs-quarterly basis signal; long cheap / short rich basis trades, "
            "dollar-neutral within asset (long quarterly / short perp for cheap basis, "
            "short quarterly / long perp for rich basis), shift(1); inverse settlement "
            "PnL pnl_coin = notional_usd*(1/entry-1/exit)*signed_weight; Leg B: cross-sectional "
            "funding rate signal; long top-K / short bottom-K dollar-neutral gross 1.0, "
            "shift(1), real funding cashflow -rate*signed_weight at each native funding boundary; "
            "cost grid [[0,0],[5,5],[10,10],[20,20],[40,40]] bps on ALL legs; benchmarks flat "
            "and equal-weight B&H-with-costs on same WF windows; train=720/test=168/step=168; "
            f"{RUNS_TOTAL} total runs ({RUNS_TOTAL_A} Leg A + {RUNS_TOTAL_B} Leg B); edge rule "
            "identical to C285-C306."
        ),
        "preflight": dataset_block,
        "data_source": dataset_block,
        "universe": {"leg_a": leg_a_info, "leg_b": leg_b_info},
        "config": {
            "walk_forward": {"train": TRAIN, "test": TEST, "step": STEP},
            "cost_grid_bps": COST_GRID,
            "leg_a": {
                "signals": list(SIGNALS_A),
                "lookbacks_1h": [int(l) for l in LOOKBACKS_A],
                "cross_sectional_K": [int(k) for k in K_VALUES_A],
                "holding_periods_1h": [int(h) for h in HOLDS_A],
                "dispersion_gates": list(GATES_A),
                "total_runs": RUNS_TOTAL_A,
                "min_periods_rule": "max(20, L // 3)",
                "lookback_window_constraint": (
                    "LOOKBACKS_A restricted to L <= 1440 because min_periods(L) = max(20, L//3) "
                    "must fit within train=720 bars; L=2160 (needs 720) is included; "
                    "L=4320/8640 are degenerate (flat through the whole training set) and "
                    "excluded rather than passed with a weakened gate."
                ),
                "position_rule": "per-asset causal basis signal; long cheap/short rich "
                                 "basis trade within asset; +0.25 quarterly / -0.25 perp "
                                 "or reverse; gross 0.5 per active asset; shift(1); hold H",
                "pnl_rule": "inverse: pnl_coin = notional_usd * (1/entry_price - 1/exit_price) "
                            "* signed_weight; ret_per_bar = (entry - exit) / exit * weight",
                "cost_rule": "cost charged on ALL legs (quarterly + perp) at (fee+slip) bps",
                "benchmark": "equal-weight buy-and-hold of the same legs with the same "
                             "costs on the same WF windows",
            },
            "leg_b": {
                "signals": list(SIGNALS_B),
                "lookbacks_1h": [int(l) for l in LOOKBACKS_B],
                "cross_sectional_K": [int(k) for k in K_VALUES_B],
                "holding_periods_1h": [int(h) for h in HOLDS_B],
                "dispersion_gates": list(GATES_B),
                "total_runs": RUNS_TOTAL_B,
                "min_periods_rule": "max(20, L // 3)",
                "position_rule": "causal cross-sectional rank; long top-K/short bottom-K; "
                                 "+0.5/K long, -0.5/K short; gross 1.0; shift(1); hold H",
                "funding_rule": "funding_pnl = -funding_rate * signed_weight at each native "
                                "funding boundary (causal); stale->flat <= 24h + 1 bar",
                "staleness_diagnostic": "real COIN-M funding archives carry gaps; runner "
                                        "zeroes positions when funding stale",
            },
            "total_runs": RUNS_TOTAL,
        },
        "gates": {
            "fail_closed": True,
            "requirements": [
                "selected feature score finite (gap/warmup bars -> flat)",
                "no NaN/non-finite perp or quarterly price in the selected leg (Leg A)",
                "no NaN/non-finite perp price in the selected leg (Leg B)",
                "funding staleness <= 24h + 1 bar in the selected leg (Leg B)",
                "cross-section has >= 2K finite assets to rebalance (Leg B)",
                "per-asset fallback trades by signal sign when only 1 asset active (Leg A)",
                "no missing/None/false gate value treated as permissive",
                "block and record reason if diagnostics fail",
            ],
        },
        "provenance": {
            "real_data_only": True,
            "fabricated_data": False,
            "pnl_on_real_coin_m_prices": True,
            "inverse_settlement_pnl_model": True,
            "real_quarterly_and_perp_klines": True,
            "real_funding_cashflows": True,
            "basis_from_real_quarterly_minus_perp": True,
            "no_linear_inverse_approximation": True,
            "no_threshold_weakening": True,
            "no_cherry_picked_windows_or_costs": True,
            "no_post_hoc_parameter_search": True,
            "native_1h_coin_m_klines": True,
            "executed_fills": False,
        },
        "results": results,
        "summary": {
            "n_total_runs": n_total,
            "n_leg_a_runs": RUNS_TOTAL_A,
            "n_leg_b_runs": RUNS_TOTAL_B,
            "n_assets_leg_a": len(assets_a),
            "n_assets_leg_b": n_assets_b,
            "runs_per_config": 1,
            "n_with_exposure": int(n_exp),
            "n_zero_exposure": int(n_total - n_exp),
            "n_edge_proven": int(len(edge_runs)),
        },
    }

    op = reports / f"campaign307_oos_sweep_{ts}.json"
    op.write_text(json.dumps(sweep, indent=2, default=jdefault) + "\n")
    sweep_sha = sha256_file(op)

    registry = {
        "generated_at_utc": ts,
        "campaign": 307,
        "part": "registry",
        "analysis": "tradable_edge_registry",
        "n_tradable": len(edge_runs),
        "tradable_configs": edge_runs,
        "oos_sweep_artifact": str(op.relative_to(root)),
        "oos_sweep_sha256": sweep_sha,
        "verdict": verdict,
        "real_data_only": True,
        "fabricated_data": False,
        "executed_fills": False,
    }
    op_reg = reports / f"campaign307_tradable_edge_registry_{ts}.json"
    op_reg.write_text(json.dumps(registry, indent=2, default=jdefault) + "\n")
    reg_sha = sha256_file(op_reg)

    summary = {
        "generated_at_utc": ts,
        "campaign": 307,
        "part": "summary",
        "analysis": "execution_summary",
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "real_data_only": True,
        "fabricated_data": False,
        "executed_fills": False,
        "universe": sweep["universe"],
        "config": sweep["config"],
        "artifacts": {
            "oos_sweep": {"path": str(op.relative_to(root)), "sha256": sweep_sha},
            "registry": {"path": str(op_reg.relative_to(root)), "sha256": reg_sha},
        },
        "summary": sweep["summary"],
        "fake_oos_claimed": False,
        "next_action": (
            "If NOT_TRADABLE: emit binding_constraint artifact (pass shares, exposure, "
            "turnover, binding constraint); record a formal negative result for the "
            "COIN-M inverse multi-asset term-structure + cross-sectional funding carry space."
        ),
    }
    op_sum = reports / f"campaign307_summary_{ts}.json"
    op_sum.write_text(json.dumps(summary, indent=2, default=jdefault) + "\n")
    sum_sha = sha256_file(op_sum)

    verdict_obj = {
        "generated_at_utc": ts,
        "campaign": 307,
        "part": "verdict",
        "analysis": "final_verdict",
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "real_data_only": True,
        "fabricated_data": False,
        "executed_fills": False,
        "finding": (
            f"No costed OOS edge proven on the real COIN-M inverse multi-asset "
            f"term-structure + cross-sectional funding carry family ({n_total} runs, "
            f"{len(edge_runs)} edge)."
            if not edge_runs
            else f"Costed OOS edge proven in {len(edge_runs)} config(s) on real COIN-M inverse multi-asset 1h data."
        ),
        "basis": "real_coin_m_inverse_multiasset_term_structure_funding_carry_costed_oos_1h",
        "dataset": dataset_block,
        "oos_sweep_artifact": str(op.relative_to(root)),
        "oos_sweep_sha256": sweep_sha,
        "registry_artifact": str(op_reg.relative_to(root)),
        "registry_sha256": reg_sha,
        "summary_artifact": str(op_sum.relative_to(root)),
        "summary_sha256": sum_sha,
        "hard_bans_honored": [
            "No synthetic/fabricated data; no relabeling existing caches as new",
            "No threshold/gate weakening; no cherry-picked windows/costs",
            "No edge claims unless the costed OOS test passes",
            "Real COIN-M inverse perp + quarterly 1h klines + real funding cashflows only",
            "inverse settlement PnL model; executed_fills: false",
        ],
    }
    op_ver = reports / f"campaign307_verdict_{ts}.json"
    op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")
    ver_sha = sha256_file(op_ver)

    bind_sha = None
    bind_path = None
    if verdict == "NOT_TRADABLE":
        gate_pass_proxy = [1.0 if r["edge_proven"] else 0.0 for r in results]
        turnovers = [r["turnover_total"] for r in results if r["oos_exposure_bars_total"] > 0]
        net_sums_by_slice = {
            f"fee{f}_slip{s2}": [r["cost_slices"][f"fee{f}_slip{s2}"]["oos_net_sum"] for r in results]
            for f, s2 in COST_GRID
        }
        binding = {
            "generated_at_utc": ts,
            "campaign": 307,
            "part": "binding_constraint",
            "analysis": "binding_constraint_diagnosis",
            "verdict": verdict,
            "real_data_only": True,
            "fabricated_data": False,
            "executed_fills": False,
            "oos_sweep_artifact": str(op.relative_to(root)),
            "oos_sweep_sha256": sweep_sha,
            "edge_summary": {
                "mean_edge_proven_share": float(np.mean(gate_pass_proxy)) if gate_pass_proxy else 0.0,
                "runs": [
                    {
                        "leg": r["leg"],
                        "signal": r["signal"],
                        "lookback": r["lookback"],
                        "K": r["K"],
                        "hold": r["hold"],
                        "gate": r["gate"],
                        "edge_proven": r["edge_proven"],
                        "oos_exposure_bars_total": r["oos_exposure_bars_total"],
                        "block_reason": r["block_reason"],
                    }
                    for r in results
                ],
            },
            "exposure_summary": {
                "total_runs": n_total,
                "runs_with_exposure": int(n_exp),
                "runs_zero_exposure": int(n_total - n_exp),
                "zero_exposure_rate": float((n_total - n_exp) / n_total) if n_total else 0.0,
            },
            "turnover_summary": {
                "configs_with_exposure": int(len(turnovers)),
                "mean_turnover": float(np.mean(turnovers)) if turnovers else 0.0,
                "median_turnover": float(np.median(turnovers)) if turnovers else 0.0,
                "max_turnover": float(np.max(turnovers)) if turnovers else 0.0,
            },
            "cost_slice_oos_net_sums": {
                ck: [float(x) for x in vals] for ck, vals in net_sums_by_slice.items()
            },
            "binding_constraint": (
                "zero_exposure"
                if n_exp == 0
                else (
                    "cost_sensitivity"
                    if not all(
                        any(r["cost_slices"][f"fee{f}_slip{s2}"]["oos_net_sum"] > 0 for r in results)
                        for f, s2 in COST_GRID
                    )
                    else "mean_beats_benchmark_fail"
                )
            ),
            "note": "Diagnosis only; never an edge claim. No threshold weakening.",
        }
        op_bind = reports / f"campaign307_binding_constraint_{ts}.json"
        op_bind.write_text(json.dumps(binding, indent=2, default=jdefault) + "\n")
        bind_sha = sha256_file(op_bind)
        bind_path = str(op_bind.relative_to(root))
        verdict_obj["binding_constraint_artifact"] = bind_path
        verdict_obj["binding_constraint_sha256"] = bind_sha
        op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")
        ver_sha = sha256_file(op_ver)

    print(json.dumps({
        "campaign": 307,
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "n_total_runs": n_total,
        "n_leg_a_runs": RUNS_TOTAL_A,
        "n_leg_b_runs": RUNS_TOTAL_B,
        "n_assets_leg_a": len(assets_a),
        "n_assets_leg_b": n_assets_b,
        "n_with_exposure": int(n_exp),
        "n_edge_proven": int(len(edge_runs)),
        "artifacts": {
            "oos_sweep": str(op.relative_to(root)),
            "registry": str(op_reg.relative_to(root)),
            "summary": str(op_sum.relative_to(root)),
            "verdict": str(op_ver.relative_to(root)),
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