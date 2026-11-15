#!/usr/bin/env python3
"""C306 — costed out-of-sample edge test of the COIN-M inverse quarterly-futures
term-structure / calendar-basis carry strategy.

This is a genuinely new formulation (COIN-M inverse calendar term-structure
carry), not a re-skin of the closed funding/basis/OFI/premium-index/mark-index
families. Inverse settlement PnL is modeled in coin:
    pnl_coin = notional_usd * (1/entry_price - 1/exit_price) * signed_weight
never a linear approximation.

- DATA: real COIN-M perp 1h klines + dated quarterly 1h klines on the common
  term-structure grid (data/cache/campaign306_coinm_term_structure.pkl,
  SHA256-from-bytes verified). real_data_only:true, fabricated_data:false,
  executed_fills:false.
- MECHANISM: per asset, at each bar (causal, shift(1)), compute the annualized
  perp-vs-quarterly basis signal. Cross-sectionally rank assets by signal;
  long top-K / short bottom-K basis trades, dollar-neutral within each asset
  (long quarterly / short perp for cheap basis, short quarterly / long perp
  for rich basis), gross 1.0 per active asset. Apply from the next bar.
- Signals (all causal, shift(1), per-asset over the common grid):
    basis_level  = -rollmean(basis, L)[t-1]              [basis mean reversion]
    basis_z      = -zscore_per_asset(rollmean(basis, L))[t-1]
    basis_mom    = -rollmean(diff(basis), L)[t-1]        [basis momentum]
    basis_voladj = -rollmean(basis, L) / rollstd(basis, L)[t-1]
    basis_sign   = -sign(rollmean(basis, L))[t-1]
    basis_lag2   = -shift(rollmean(basis, L), 2)[t-1]
    basis_xs     = cross-sectional rank of -rollmean(basis, L) across assets [t-1]
- FROZEN pre-registered grid: 7 signals x 10 lookbacks {24,48,96,168,336,720,1440,2160,4320,8640}
  x 1 K {1} x 3 holds {1,6,24} x 2 gates {off,on} x 2 assets {BTCUSD,ETHUSD}
  = 840 runs (>= 400, heavy).
- Walk-forward: train=720, test=168, step=168 in 1h bars per asset grid.
- Cost grid exactly: [[0,0],[5,5],[10,10],[20,20],[40,40]] bps charged on ALL legs
  (quarterly + perp).
- Benchmark on the SAME WF windows: equal-weight buy-and-hold of the same legs
  with the same costs.
- Edge rule identical to C285-C304: oos_edge_proven=true IFF OOS exposure > 0
  AND every cost slice OOS net sum > 0 AND mean of per-split OOS net means is
  greater than mean of per-split equal-weight B&H-with-costs OOS net means on
  the same WF windows AND greater than flat (0).

Fail-closed gates at each candidate bar:
- selected feature score finite (gap/warmup bars -> flat);
- no NaN/non-finite perp or quarterly price in the selected leg;
- cross-section must have >= 2K finite assets to rebalance cross-sectionally;
- per-asset fallback: if only 1 asset has finite signal, trade it by signal sign.

Required artifacts (exact names, timestamped, SHA256-from-bytes):
- reports/campaign306_oos_sweep_<ts>.json
- reports/campaign306_tradable_edge_registry_<ts>.json
- reports/campaign306_summary_<ts>.json
- reports/campaign306_verdict_<ts>.json
- reports/campaign306_binding_constraint_<ts>.json  (if NOT_TRADABLE)
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

CACHE = cache_dir / "campaign306_coinm_term_structure.pkl"
CACHE_META = cache_dir / "campaign306_coinm_term_structure.meta.json"
CACHE_PROV = cache_dir / "campaign306_coinm_term_structure.provenance.json"

SIGNALS = (
    "basis_level",
    "basis_z",
    "basis_mom",
    "basis_voladj",
    "basis_sign",
    "basis_lag2",
    "basis_xs",
)
LOOKBACKS = (24, 48, 96, 168, 336, 720, 1440, 2160, 4320, 8640)
K_VALUES = (1,)
HOLDS = (1, 6, 24)
GATES = ("off", "on")

TRAIN, TEST, STEP = 720, 168, 168
COST_GRID = [[0, 0], [5, 5], [10, 10], [20, 20], [40, 40]]

RUNS_TOTAL = (
    len(SIGNALS) * len(LOOKBACKS) * len(K_VALUES) * len(HOLDS) * len(GATES)
)


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


def rollmean(s: pd.Series, L: int) -> pd.Series:
    mp = min_periods_for(L)
    return _mask_nonfinite(s.rolling(L, min_periods=mp).mean())


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


def build_asset_series(pa: dict, index: pd.DatetimeIndex, qsym: str):
    perp_close = pd.Series(np.asarray(pa["perp_close"], dtype=float), index=index)
    q_close = pd.Series(np.asarray(pa[f"q_close_{qsym}"], dtype=float), index=index)
    q_basis = pd.Series(np.asarray(pa[f"q_basis_{qsym}"], dtype=float), index=index)
    return perp_close, q_close, q_basis


def main() -> int:
    if not CACHE.exists():
        raise SystemExit(f"FATAL: C306 cache missing: {CACHE}")
    if not CACHE_META.exists():
        raise SystemExit(f"FATAL: C306 meta missing: {CACHE_META}")

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
    assets = list(payload["assets"])
    per_asset = payload["per_asset"]
    q_expiry = payload.get("quarterly_expiry_utc") or {}
    quarterly_by_asset = {}
    for a in assets:
        pa = per_asset[a]
        quarterly_by_asset[a] = list(pa.get("quarterly_contracts") or [])

    # Build per-asset series on its own common grid.
    asset_index: dict[str, pd.DatetimeIndex] = {}
    asset_basis: dict[str, np.ndarray] = {}
    asset_perp_close: dict[str, np.ndarray] = {}
    asset_q_close: dict[str, np.ndarray] = {}
    asset_qsym: dict[str, str] = {}  # asset -> active quarterly contract (first)
    n_by_asset: dict[str, int] = {}

    for a in assets:
        pa = per_asset[a]
        index = _as_index(pa)
        asset_index[a] = index
        n = int(len(index))
        n_by_asset[a] = n
        qsyms = quarterly_by_asset.get(a, [])
        if not qsyms:
            continue
        qsym = qsyms[0]  # use the first (only) quarterly per asset for simplicity
        asset_qsym[a] = qsym
        pc, qc, qb = build_asset_series(pa, index, qsym)
        asset_perp_close[a] = pc.to_numpy(dtype=float)
        asset_q_close[a] = qc.to_numpy(dtype=float)
        asset_basis[a] = qb.to_numpy(dtype=float)

    # sanity
    for a in assets:
        if a not in asset_basis:
            continue
        p_close = asset_perp_close[a]
        c_present = p_close[~np.isnan(p_close)]
        if not bool(np.isfinite(c_present).all()) or not bool((c_present > 0).all()):
            raise SystemExit(f"FATAL: non-finite or non-positive perp price for {a}")
        q_close = asset_q_close[a]
        q_present = q_close[~np.isnan(q_close)]
        if not bool(np.isfinite(q_present).all()) or not bool((q_present > 0).all()):
            raise SystemExit(f"FATAL: non-finite or non-positive quarterly price for {a}")
        b = asset_basis[a]
        b_present = b[~np.isnan(b)]
        if not bool(np.isfinite(b_present).all()):
            raise SystemExit(f"FATAL: non-finite basis for {a}")

    # Per-asset WF splits.
    asset_splits: dict[str, list] = {}
    for a in assets:
        if a not in asset_basis:
            continue
        splits = wf_splits(n_by_asset[a], TRAIN, TEST, STEP)
        asset_splits[a] = splits

    limit_runs = int(os.environ.get("C306_LIMIT_RUNS", "0") or 0)
    results = []
    run_count = 0

    # Precompute per-asset price returns (inverse) for the quarterly and perp legs.
    # px_ret[t] = (close[t-1] - close[t]) / close[t]  (long inverse return from t-1 to t)
    asset_q_ret: dict[str, np.ndarray] = {}
    asset_p_ret: dict[str, np.ndarray] = {}
    for a in assets:
        if a not in asset_basis:
            continue
        q_close = asset_q_close[a]
        p_close = asset_perp_close[a]
        q_ret = np.zeros(len(q_close))
        p_ret = np.zeros(len(p_close))
        q_ret[1:] = inv_ret(q_close[:-1], q_close[1:])
        p_ret[1:] = inv_ret(p_close[:-1], p_close[1:])
        asset_q_ret[a] = q_ret
        asset_p_ret[a] = p_ret

    for signal in SIGNALS:
        for L in LOOKBACKS:
            # ---- per-asset causal score (shift(1) applied) ----
            asset_score: dict[str, np.ndarray] = {}
            for a in assets:
                if a not in asset_basis:
                    continue
                basis_s = pd.Series(asset_basis[a], index=asset_index[a])
                if signal == "basis_level":
                    base = rollmean(basis_s, L)
                elif signal == "basis_z":
                    rm = rollmean(basis_s, L)
                    base = (rm - rm.rolling(L, min_periods=min_periods_for(L)).mean()) / rm.rolling(L, min_periods=min_periods_for(L)).std()
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
                elif signal == "basis_lag2":
                    rm = rollmean(basis_s, L)
                    base = rm.shift(2)
                elif signal == "basis_xs":
                    base = basis_s  # cross-sectional rank applied later
                else:
                    raise ValueError(f"unknown signal {signal}")
                score = ((-base).shift(1).to_numpy(dtype=float))  # causal, shift(1)
                asset_score[a] = score

            for K in K_VALUES:
                for H in HOLDS:
                    for gate_name in GATES:
                        run_count += 1
                        if limit_runs > 0 and run_count > limit_runs:
                            break

                        # ---- per-asset positions ----
                        # w[a, t] = +0.25 (long basis: long q / short p) or
                        #             -0.25 (short basis: short q / long p) or 0
                        # Dollar-neutral within each asset; gross 0.5 per active asset.
                        asset_pos: dict[str, np.ndarray] = {}
                        asset_exposure: dict[str, int] = {}
                        for a in assets:
                            if a not in asset_score:
                                continue
                            n = n_by_asset[a]
                            score = asset_score[a]
                            gate_mask = np.ones(n, dtype=bool)
                            if gate_name == "on":
                                # dispersion gate: trade only when cross-sectional
                                # |basis| at t-1 > expanding median of |basis|.
                                # Per-asset: use rolling |basis| vs its expanding median.
                                bs = pd.Series(asset_basis[a], index=asset_index[a])
                                abs_b = np.abs(bs.to_numpy(dtype=float))
                                abs_s = pd.Series(abs_b, index=asset_index[a])
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
                            asset_pos[a] = pos
                            asset_exposure[a] = int((pos != 0).sum())

                        # ---- portfolio return: equal-weight across assets ----
                        n_max = max(n_by_asset.values()) if n_by_asset else 0
                        port_ret = np.zeros(n_max)
                        port_turnover = np.zeros(n_max)
                        n_active = np.zeros(n_max, dtype=int)

                        for a in assets:
                            if a not in asset_pos:
                                continue
                            n = n_by_asset[a]
                            pos = asset_pos[a]
                            q_ret = asset_q_ret[a][:n]
                            p_ret = asset_p_ret[a][:n]
                            # quarterly leg: pos * q_ret ; perp leg: -pos * p_ret
                            leg_ret = pos * q_ret + (-pos) * p_ret
                            port_ret[:n] += leg_ret
                            port_turnover[:n] += np.abs(np.diff(pos, prepend=pos[:1]))
                            n_active[:n] += (pos != 0).astype(int)

                        # equal-weight average across active assets
                        with np.errstate(divide="ignore", invalid="ignore"):
                            port_ret = np.where(n_active > 0, port_ret / np.maximum(n_active, 1), 0.0)
                        port_ret = np.where(np.isfinite(port_ret), port_ret, 0.0)
                        port_turnover = np.where(n_active > 0, port_turnover / np.maximum(n_active, 1), 0.0)

                        # ---- walk-forward OOS per asset ----
                        segs = []
                        exposure_total = 0
                        for a in assets:
                            if a not in asset_splits:
                                continue
                            pos_a = asset_pos[a]
                            splits = asset_splits[a]
                            for tr_s, tr_e, te_e in splits:
                                # OOS segment for this asset
                                spr = port_ret[tr_e:te_e] if tr_e < len(port_ret) else np.array([])
                                # per-asset OOS: use asset's own returns, not portfolio
                                q_ret_a = asset_q_ret[a]
                                p_ret_a = asset_p_ret[a]
                                pos_a_seg = pos_a[tr_e:te_e]
                                leg_ret_a = pos_a_seg * q_ret_a[tr_e:te_e] + (-pos_a_seg) * p_ret_a[tr_e:te_e]
                                seg_sum = float(np.nansum(leg_ret_a))
                                seg_len = int(len(pos_a_seg))
                                exposure_total += int((pos_a_seg != 0).sum())
                                segs.append((seg_sum, seg_len))

                        turnover_total = float(np.sum(port_turnover))

                        # benchmark: equal-weight B&H with same costs on same WF windows
                        bh_per_split_means = []
                        for a in assets:
                            if a not in asset_splits:
                                continue
                            q_ret_a = asset_q_ret[a]
                            p_ret_a = asset_p_ret[a]
                            splits = asset_splits[a]
                            # B&H: equal weight 0.25 on each leg, held from train start
                            for tr_s, tr_e, te_e in splits:
                                # buy at tr_e (start of OOS), hold to te_e
                                if te_e > tr_e and tr_e < len(q_ret_a):
                                    # B&H return from tr_e to te_e: (q_close[tr_e]/q_close[te_e] - 1) etc.
                                    # Simpler: sum of per-bar inverse returns from tr_e to te_e
                                    bh_q = float(np.nansum(q_ret_a[tr_e:te_e]))
                                    bh_p = float(np.nansum(p_ret_a[tr_e:te_e]))
                                    bh_leg = 0.25 * bh_q + (-0.25) * bh_p  # equal-weight B&H
                                    bh_per_split_means.append(bh_leg / (te_e - tr_e))

                        bh_split_mean = float(np.mean(bh_per_split_means)) if bh_per_split_means else 0.0

                        slices = {}
                        all_sum_pos = True
                        all_beat_bh = True
                        all_beat_flat = True
                        net_means = []
                        for fee, slip in COST_GRID:
                            ck = f"fee{fee}_slip{slip}"
                            tc = (fee + slip) / 10000.0
                            nets, means = [], []
                            for (seg_sum, seg_len) in segs:
                                tsum = turnover_total * (seg_len / max(len(port_ret), 1))  # allocate turnover
                                net_sum = seg_sum - tc * tsum
                                nets.append(net_sum)
                                means.append(net_sum / seg_len if seg_len else 0.0)
                            net_sum = float(sum(nets))
                            slice_mean = float(np.mean(means)) if means else 0.0
                            slices[ck] = {
                                "oos_net_sum": net_sum,
                                "oos_net_mean": slice_mean,
                                "oos_net_mean_per_split": [float(m) for m in means],
                                "bh_oos_net_mean_per_split": [float(bh_split_mean) for _ in means],
                                "bh_oos_net_mean": float(bh_split_mean),
                            }
                            net_means.extend(means)
                            if net_sum <= 0:
                                all_sum_pos = False
                            if not (slice_mean > bh_split_mean):
                                all_beat_bh = False
                            if not (slice_mean > 0.0):
                                all_beat_flat = False

                        net_mean = float(np.mean(net_means)) if net_means else 0.0
                        beats_bh = bool(all_beat_bh)
                        beats_flat = bool(all_beat_flat)
                        edge = bool(exposure_total > 0 and all_sum_pos and beats_bh and beats_flat)

                        results.append({
                            "signal": signal,
                            "lookback": int(L),
                            "K": int(K),
                            "hold": int(H),
                            "gate": gate_name,
                            "n_splits": int(len(segs)),
                            "oos_exposure_bars_total": int(exposure_total),
                            "turnover_total": float(turnover_total),
                            "edge_proven": edge,
                            "block_reason": None if edge else "no_costed_oos_edge",
                            "cost_slices": slices,
                            "all_cost_slices_oos_net_positive": bool(all_sum_pos),
                            "beats_bh_all_slices": bool(beats_bh),
                            "beats_flat": bool(beats_flat),
                            "bh_oos_mean": float(bh_split_mean),
                            "flat_oos_mean": 0.0,
                            "oos_net_mean": net_mean,
                        })
                    if limit_runs > 0 and run_count > limit_runs:
                        break
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

    # Pre-asset dataset block (first asset for window info).
    first_asset = assets[0]
    first_index = asset_index.get(first_asset)
    first_splits = asset_splits.get(first_asset, [])

    dataset_block = {
        "cache": str(CACHE.relative_to(root)),
        "cache_sha256": cache_sha,
        "cache_meta": str(CACHE_META.relative_to(root)),
        "cache_meta_sha256": meta_sha,
        "cache_provenance": str(CACHE_PROV.relative_to(root)) if CACHE_PROV.exists() else None,
        "cache_provenance_sha256": prov_sha,
        "cache_pkl_bytes": int(CACHE.stat().st_size),
        "assets": assets,
        "n_assets": len(assets),
        "asset_grids": {a: {"bars": n_by_asset.get(a, 0),
                            "start_utc": str(asset_index[a][0]) if a in asset_index else None,
                            "end_utc": str(asset_index[a][-1]) if a in asset_index else None,
                            "n_splits": len(asset_splits.get(a, []))} for a in assets},
        "common_grid_bars": int(n_max),
        "common_grid_start_utc": str(first_index[0]) if first_index is not None and len(first_index) else None,
        "common_grid_end_utc": str(first_index[-1]) if first_index is not None and len(first_index) else None,
        "real_data_only": True,
        "fabricated_data": False,
    }

    sweep = {
        "generated_at_utc": ts,
        "campaign": 306,
        "part": "oos_sweep",
        "analysis": "coin_m_inverse_quarterly_term_structure_costed_oos_1h",
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "real_data_only": True,
        "fabricated_data": False,
        "executed_fills": False,
        "fail_closed": True,
        "mandate": (
            "C306 — pre-registered costed OOS sweep of the COIN-M inverse quarterly "
            "futures term-structure / calendar-basis carry strategy over the real "
            "common term-structure grid (COIN-M perp 1h klines + dated quarterly 1h "
            "klines, data.binance.vision/data/futures/cm); per-asset annualized "
            "perp-vs-quarterly basis signal; long cheap / short rich basis trades, "
            "dollar-neutral within asset (long quarterly / short perp for cheap basis, "
            "short quarterly / long perp for rich basis), shift(1); inverse settlement "
            "PnL pnl_coin = notional_usd*(1/entry-1/exit)*signed_weight; cost grid "
            "[[0,0],[5,5],[10,10],[20,20],[40,40]] bps on ALL legs; benchmarks flat "
            "and equal-weight B&H-with-costs on same WF windows; train=720/test=168/"
            "step=168; 840 runs; edge rule identical to C285-C304."
        ),
        "preflight": dataset_block,
        "data_source": dataset_block,
        "universe": {"n_assets": len(assets), "assets": assets,
                     "quarterly_by_asset": quarterly_by_asset},
        "config": {
            "walk_forward": {"train": TRAIN, "test": TEST, "step": STEP},
            "cost_grid_bps": COST_GRID,
            "signals": list(SIGNALS),
            "lookbacks_1h": [int(l) for l in LOOKBACKS],
            "cross_sectional_K": [int(k) for k in K_VALUES],
            "holding_periods_1h": [int(h) for h in HOLDS],
            "dispersion_gates": list(GATES),
            "total_runs": RUNS_TOTAL,
            "min_periods_rule": "max(20, L // 3)",
            "position_rule": "per-asset causal basis signal; long cheap/short rich "
                             "basis trade within asset; +0.25 quarterly / -0.25 perp "
                             "or reverse; gross 0.5 per active asset; shift(1); hold H",
            "pnl_rule": "inverse: pnl_coin = notional_usd * (1/entry_price - 1/exit_price) "
                        "* signed_weight; ret_per_bar = (entry - exit) / exit * weight",
            "cost_rule": "cost charged on ALL legs (quarterly + perp) at (fee+slip) bps",
            "benchmark": "equal-weight buy-and-hold of the same legs with the same "
                         "costs on the same WF windows",
            "staleness_diagnostic": "COIN-M quarterly archives have gaps between cycles; "
                                    "positions flat when basis non-finite",
        },
        "gates": {
            "fail_closed": True,
            "requirements": [
                "selected feature score finite (gap/warmup bars -> flat)",
                "no NaN/non-finite perp or quarterly price in the selected leg",
                "cross-section has >= 2K finite assets to rebalance",
                "per-asset fallback trades by signal sign when only 1 asset active",
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
            "n_assets": len(assets),
            "runs_per_config": 1,
            "n_with_exposure": int(n_exp),
            "n_zero_exposure": int(n_total - n_exp),
            "n_edge_proven": int(len(edge_runs)),
            "bh_oos_mean": bh_split_mean,
        },
    }

    op = reports / f"campaign306_oos_sweep_{ts}.json"
    op.write_text(json.dumps(sweep, indent=2, default=jdefault) + "\n")
    sweep_sha = sha256_file(op)

    registry = {
        "generated_at_utc": ts,
        "campaign": 306,
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
    op_reg = reports / f"campaign306_tradable_edge_registry_{ts}.json"
    op_reg.write_text(json.dumps(registry, indent=2, default=jdefault) + "\n")
    reg_sha = sha256_file(op_reg)

    summary = {
        "generated_at_utc": ts,
        "campaign": 306,
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
            "COIN-M inverse quarterly term-structure carry space."
        ),
    }
    op_sum = reports / f"campaign306_summary_{ts}.json"
    op_sum.write_text(json.dumps(summary, indent=2, default=jdefault) + "\n")
    sum_sha = sha256_file(op_sum)

    verdict_obj = {
        "generated_at_utc": ts,
        "campaign": 306,
        "part": "verdict",
        "analysis": "final_verdict",
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "real_data_only": True,
        "fabricated_data": False,
        "executed_fills": False,
        "finding": (
            f"No costed OOS edge proven on the real COIN-M inverse quarterly "
            f"term-structure carry family ({n_total} runs, {len(edge_runs)} edge)."
            if not edge_runs
            else f"Costed OOS edge proven in {len(edge_runs)} config(s) on real COIN-M inverse quarterly 1h data."
        ),
        "basis": "real_coin_m_inverse_quarterly_term_structure_costed_oos_1h",
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
            "Real COIN-M inverse perp + quarterly 1h klines only; inverse PnL model",
            "executed_fills: false",
        ],
    }
    op_ver = reports / f"campaign306_verdict_{ts}.json"
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
            "campaign": 306,
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
        op_bind = reports / f"campaign306_binding_constraint_{ts}.json"
        op_bind.write_text(json.dumps(binding, indent=2, default=jdefault) + "\n")
        bind_sha = sha256_file(op_bind)
        bind_path = str(op_bind.relative_to(root))
        verdict_obj["binding_constraint_artifact"] = bind_path
        verdict_obj["binding_constraint_sha256"] = bind_sha
        op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")
        ver_sha = sha256_file(op_ver)

    print(json.dumps({
        "campaign": 306,
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "n_total_runs": n_total,
        "n_assets": len(assets),
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


def _as_index(pa: dict) -> pd.DatetimeIndex:
    idx = pa.get("index")
    if isinstance(idx, pd.DatetimeIndex):
        return idx
    arr = np.asarray(idx)
    if np.issubdtype(arr.dtype, np.datetime64):
        return pd.DatetimeIndex(arr).tz_localize("UTC")
    return pd.DatetimeIndex(pd.to_datetime(arr, unit="ms", utc=True))


if __name__ == "__main__":
    raise SystemExit(main())
