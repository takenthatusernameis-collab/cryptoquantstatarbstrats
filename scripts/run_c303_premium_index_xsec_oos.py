#!/usr/bin/env python3
"""C303 — costed out-of-sample edge test of the cross-sectional premium-index
carry / dispersion strategy across 10 real USDT-M perpetuals.

This is a genuinely new formulation (cross-sectional premium-index carry), not
a re-skin of the closed funding/basis/OFI families. It directly attacks
C298's zero_exposure bottleneck: 10 real assets share a 58,959-bar common
premium-index grid (2020-01-31 08:00Z -> 2026-10-31 23:00Z), so K in {2,3,5}
is reachable and every in-grid rebalance has real exposure.

- DATA: real USDT-M perp premium-index 1h OHLC + real perp 1h close + real
  native 8h funding rate, all on the common intersection grid
  (data/cache/campaign303_premium_index_xsec.pkl, SHA256-from-bytes verified).
  real_data_only:true, fabricated_data:false, executed_fills:false.
- MECHANISM: at each bar (causal, shift(1)), rank the live cross-section by the
  premium signal; long top-K / short bottom-K, dollar-neutral, gross 1.0
  (weight +0.5/K long, -0.5/K short). Apply from the next bar. Real funding
  cashflow -rate*signed_weight at each native 8h boundary (causal).
- Signals (all causal, shift(1), per-asset over the common grid):
    prem_level = -rollmean(premium, L)[t-1]                    [premium level]
    prem_z     = -z_cross_sectional(rollmean(premium, L))[t-1] [premium z]
    prem_mom   = -rollmean(delta_premium, L)[t-1]              [premium momentum]
    prem_range = -rollmean(high-low, L)[t-1]                   [premium dispersion]
  Higher score = long. Premium is a mean-reverting fair-value spread: rich
  perps tend to revert, so the score is the negated premium.
- Dispersion gate (cross-sectional std of premium at t-1 vs expanding median):
    off = always trade; on = trade only when dispersion > expanding median.
- FROZEN pre-registered grid: 4 signals x 6 lookbacks {24,48,168,336,720,2160}
  x 3 K {2,3,5} x 3 holds {1,6,24} x 2 gates = 432 runs (>= 400, heavy).
- Walk-forward: train=720, test=168, step=168 in 1h bars over the common grid
  (~346 OOS splits).
- Cost grid exactly: [[0,0],[5,5],[10,10],[20,20],[40,40]] bps on turnover.
- Benchmarks on the SAME WF windows: flat (zero) and equal-weight B&H with the
  SAME real funding cashflows (weight 0.1 per asset).
- Edge rule identical to C285-C302, never relaxed: oos_edge_proven=true IFF
  OOS exposure > 0 AND every cost slice OOS net sum > 0 AND the mean of the
  per-split OOS net means is greater than the mean of the per-split equal-weight
  B&H-with-funding OOS net means on the same WF windows AND greater than flat.

Fail-closed gates at each candidate bar:
- selected feature score finite (gap/warmup bars -> flat);
- no NaN/non-finite perp price in the selected leg;
- funding staleness <= 24h + 1 bar in the selected leg (position zeroed when
  funding stale/missing at the boundary);
- cross-section must have >= 2K finite assets to rebalance.

Required artifacts (exact names, timestamped, SHA256-from-bytes):
- reports/campaign303_oos_sweep_<ts>.json
- reports/campaign303_tradable_edge_registry_<ts>.json
- reports/campaign303_summary_<ts>.json
- reports/campaign303_verdict_<ts>.json
- reports/campaign303_binding_constraint_<ts>.json  (if NOT_TRADABLE)
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

CACHE = cache_dir / "campaign303_premium_index_xsec.pkl"
CACHE_META = cache_dir / "campaign303_premium_index_xsec.meta.json"
CACHE_PROV = cache_dir / "campaign303_premium_index_xsec.provenance.json"

SIGNALS = ("prem_level", "prem_z", "prem_mom", "prem_range")
LOOKBACKS = (24, 48, 168, 336, 720, 2160)
K_VALUES = (2, 3, 5)
HOLDS = (1, 6, 24)
GATES = ("off", "on")

TRAIN, TEST, STEP = 720, 168, 168
COST_GRID = [[0, 0], [5, 5], [10, 10], [20, 20], [40, 40]]
STALE_BARS = 24 + 1  # 24h + 1 bar on the 1h grid

RUNS_TOTAL = len(SIGNALS) * len(LOOKBACKS) * len(K_VALUES) * len(HOLDS) * len(GATES)


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


def rollmean_df(df: pd.DataFrame, L: int) -> pd.DataFrame:
    mp = min_periods_for(L)
    return df.rolling(L, min_periods=mp).mean()


def rollstd(s: pd.Series, L: int) -> pd.Series:
    mp = min_periods_for(L)
    return _mask_nonfinite(s.rolling(L, min_periods=mp).std())


def build_asset_series(pa: dict, index: pd.DatetimeIndex):
    prem_close = pd.Series(np.asarray(pa["prem_close"], dtype=float), index=index)
    prem_high = pd.Series(np.asarray(pa["prem_high"], dtype=float), index=index)
    prem_low = pd.Series(np.asarray(pa["prem_low"], dtype=float), index=index)
    perp_close = pd.Series(np.asarray(pa["perp_close"], dtype=float), index=index)
    funding = pd.Series(np.asarray(pa["funding_rates"], dtype=float), index=index)
    return prem_close, prem_high, prem_low, perp_close, funding


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


def main() -> int:
    if not CACHE.exists():
        raise SystemExit(f"FATAL: C303 cache missing: {CACHE}")
    if not CACHE_META.exists():
        raise SystemExit(f"FATAL: C303 meta missing: {CACHE_META}")

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
    symbols = list(payload["symbols"])
    per_asset = payload["per_asset"]
    common_index = pd.DatetimeIndex(np.asarray(per_asset[symbols[0]]["index"]))
    n = int(len(common_index))
    n_assets = len(symbols)

    splits = wf_splits(n, TRAIN, TEST, STEP)
    if len(splits) == 0:
        raise SystemExit(f"FATAL: no OOS splits, n={n}, train={TRAIN}, test={TEST}, step={STEP}")

    # ---- per-asset returns (perp + real funding cashflow) over common grid ----
    prem_arrs = []
    close_arrs = []
    fund_arrs = []
    for s in symbols:
        pa = per_asset[s]
        pc, ph, pl, cl, fd = build_asset_series(pa, common_index)
        prem_arrs.append(np.stack([pc.to_numpy(dtype=float),
                                   ph.to_numpy(dtype=float),
                                   pl.to_numpy(dtype=float)]))
        close_arrs.append(cl.to_numpy(dtype=float))
        fund_arrs.append(fd.to_numpy(dtype=float))
    prem3 = np.stack(prem_arrs, axis=0)  # (n_assets, 3, n_bars): [close, high, low]
    prem_close = prem3[:, 0, :]
    prem_high = prem3[:, 1, :]
    prem_low = prem3[:, 2, :]
    close = np.stack(close_arrs, axis=0)  # (n_assets, n_bars)
    funding = np.stack(fund_arrs, axis=0)  # (n_assets, n_bars)

    # sanity: perp price finite + positive where present
    c_present = close[~np.isnan(close)]
    if not bool(np.isfinite(c_present).all()) or not bool((c_present > 0).all()):
        raise SystemExit("FATAL: non-finite or non-positive perp price present")
    prem_present = prem_close[~np.isnan(prem_close)]
    if not bool(np.isfinite(prem_present).all()):
        raise SystemExit("FATAL: non-finite premium close on present bars")

    # funding staleness mask per asset (age since last boundary, in bars)
    funding_age = np.stack([compute_funding_age(pd.Series(funding[a])) for a in range(n_assets)])
    funding_stale = ~np.isfinite(funding_age) | (funding_age > STALE_BARS)

    # total asset return = perp pct change + funding leg (-rate at boundaries)
    perp_ret = np.diff(close, axis=1) / close[:, :-1]
    perp_ret = np.concatenate([np.zeros((n_assets, 1)), perp_ret], axis=1)
    funding_leg = np.where(np.isnan(funding), 0.0, -funding)
    total_ret = perp_ret + funding_leg  # (n_assets, n_bars)

    # ---- equal-weight B&H-with-funding benchmark (same WF windows) ----
    bench_ret = np.nanmean(total_ret, axis=0)  # weight 0.1 each -> mean
    bench_ret = np.where(np.isnan(bench_ret), 0.0, bench_ret)

    # ---- features per asset (causal base inputs) ----
    prem_df = pd.DataFrame(prem_close.T, index=common_index)
    prem_high_df = pd.DataFrame(prem_high.T, index=common_index)
    prem_low_df = pd.DataFrame(prem_low.T, index=common_index)
    delta = prem_df.diff()
    hl = prem_high_df - prem_low_df

    # cross-sectional dispersion of premium at each bar (finite assets)
    disp = prem_df.std(axis=1)  # (n_bars,)
    disp = np.where(np.isfinite(disp), disp, np.nan)
    # expanding median of dispersion (causal): median over [0, t]
    disp_series = pd.Series(disp, index=common_index)
    disp_med = disp_series.expanding().median().to_numpy(dtype=float)

    limit_runs = int(os.environ.get("C303_LIMIT_RUNS", "0") or 0)
    results = []
    run_count = 0

    for signal in SIGNALS:
        for L in LOOKBACKS:
            # ---- build causal per-asset score (shift(1) applied) ----
            prem_s = prem_df
            if signal == "prem_level":
                base = rollmean_df(prem_s, L)
            elif signal == "prem_z":
                m = rollmean_df(prem_s, L)
                # cross-sectional z at each bar (per-asset vs live cross-section)
                row_mean = m.mean(axis=1)
                row_std = m.std(axis=1)
                base = m.sub(row_mean, axis=0).div(row_std.replace(0, np.nan), axis=0)
                base = base.where(np.isfinite(base))
            elif signal == "prem_mom":
                base = rollmean_df(delta, L)
            elif signal == "prem_range":
                base = rollmean_df(hl, L)
            else:
                raise ValueError(f"unknown signal {signal}")
            score = ((-base).shift(1).to_numpy(dtype=float)).T  # causal, shift(1); (n_assets, n_bars)

            # ---- dispersion gate mask ----
            if "on" in GATES:
                gate_on = (disp > disp_med)  # (n_bars,)
                gate_on = np.where(np.isnan(gate_on), False, gate_on)
                gate_on = np.roll(gate_on, 1)  # causal: use dispersion known at t-1
                gate_on[0] = False
            else:
                gate_on = np.ones(n, dtype=bool)

            for K in K_VALUES:
                for H in HOLDS:
                    for gate_name in GATES:
                        run_count += 1
                        if limit_runs > 0 and run_count > limit_runs:
                            break
                        gate_mask = gate_on if gate_name == "on" else np.ones(n, dtype=bool)
                        # stale -> flat: zero positions where funding stale
                        pos = xsec_positions(score, K, H, gate_mask)
                        pos = np.where(funding_stale, 0.0, pos)

                        port_ret = (pos * total_ret).sum(axis=0)  # (n_bars,)
                        turnover = np.abs(np.diff(pos, axis=1, prepend=pos[:, :1])).sum(axis=0)

                        segs = []
                        exposure_total = 0
                        for tr_s, tr_e, te_e in splits:
                            spr = port_ret[tr_e:te_e]
                            stu = turnover[tr_e:te_e]
                            spos = pos[:, tr_e:te_e]
                            segs.append((float(spr.sum()), int(len(spr)), float(stu.sum())))
                            exposure_total += int((spos != 0).sum())
                        turnover_total = float(sum(x[2] for x in segs))

                        # benchmark per split (equal-weight B&H-with-funding)
                        bh_per_split_means = [float(bench_ret[tr_e:te_e].mean())
                                              for _, tr_e, te_e in splits]
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
                            for (seg_sum, seg_len, tsum) in segs:
                                net_sum = seg_sum - tc * tsum
                                nets.append(net_sum)
                                means.append(net_sum / seg_len if seg_len else 0.0)
                            net_sum = float(sum(nets))
                            slice_mean = float(np.mean(means)) if means else 0.0
                            slices[ck] = {
                                "oos_net_sum": net_sum,
                                "oos_net_mean": slice_mean,
                                "oos_net_mean_per_split": [float(m) for m in means],
                                "bh_oos_net_mean_per_split": [float(m) for m in bh_per_split_means],
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
                            "n_splits": int(len(splits)),
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

    dataset_block = {
        "cache": str(CACHE.relative_to(root)),
        "cache_sha256": cache_sha,
        "cache_meta": str(CACHE_META.relative_to(root)),
        "cache_meta_sha256": meta_sha,
        "cache_provenance": str(CACHE_PROV.relative_to(root)) if CACHE_PROV.exists() else None,
        "cache_provenance_sha256": prov_sha,
        "cache_pkl_bytes": int(CACHE.stat().st_size),
        "symbols": symbols,
        "n_assets": n_assets,
        "common_grid_bars": int(n),
        "common_grid_start_utc": str(common_index[0]),
        "common_grid_end_utc": str(common_index[-1]),
        "real_data_only": True,
        "fabricated_data": False,
    }

    sweep = {
        "generated_at_utc": ts,
        "campaign": 303,
        "part": "oos_sweep",
        "analysis": "cross_sectional_premium_index_carry_costed_oos_1h",
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "real_data_only": True,
        "fabricated_data": False,
        "executed_fills": False,
        "fail_closed": True,
        "mandate": (
            "C303 — pre-registered costed OOS sweep of the cross-sectional USDT-M "
            "perpetual premium-index carry/dispersion strategy over the real common "
            "intersection grid (2020-01-31 08:00Z -> 2026-10-31 23:00Z, 58,959 bars, "
            "10 assets); rank cross-section by causal premium signal, long top-K / "
            "short bottom-K dollar-neutral gross 1.0, shift(1), real funding cashflow "
            "-rate*signed_weight at each native funding boundary; cost grid "
            "[[0,0],[5,5],[10,10],[20,20],[40,40]] bps; benchmarks flat and "
            "equal-weight B&H-with-funding on same WF windows; train=720/test=168/"
            "step=168; 432 runs; edge rule identical to C285-C302."
        ),
        "preflight": dataset_block,
        "data_source": dataset_block,
        "universe": {"n_assets": n_assets, "assets": symbols},
        "config": {
            "walk_forward": {"train": TRAIN, "test": TEST, "step": STEP, "n_splits": len(splits)},
            "cost_grid_bps": COST_GRID,
            "signals": list(SIGNALS),
            "lookbacks_1h": [int(l) for l in LOOKBACKS],
            "cross_sectional_K": [int(k) for k in K_VALUES],
            "holding_periods_1h": [int(h) for h in HOLDS],
            "dispersion_gates": list(GATES),
            "total_runs": RUNS_TOTAL,
            "min_periods_rule": "max(20, L // 3)",
            "position_rule": "causal cross-sectional rank; long top-K/short bottom-K; "
                             "+0.5/K long, -0.5/K short; gross 1.0; shift(1); hold H",
            "funding_rule": "funding_pnl = -funding_rate * signed_weight at each native "
                            "funding boundary (causal); stale->flat <= 24h + 1 bar",
            "staleness_diagnostic": "real altcoin funding archives carry gaps; runner "
                                    "zeroes positions when funding stale",
        },
        "gates": {
            "fail_closed": True,
            "requirements": [
                "selected feature score finite (gap/warmup bars -> flat)",
                "no NaN/non-finite perp price in the selected leg",
                "funding staleness <= 24h + 1 bar in the selected leg",
                "cross-section has >= 2K finite assets to rebalance",
                "no missing/None/false gate value treated as permissive",
            ],
        },
        "provenance": {
            "real_data_only": True,
            "fabricated_data": False,
            "pnl_on_real_perp_prices": True,
            "real_funding_cashflows": True,
            "premium_index_from_real_klines": True,
            "execution_price_from_real_klines": True,
            "funding_from_real_funding_rate_archives": True,
            "no_threshold_weakening": True,
            "no_cherry_picked_windows_or_costs": True,
            "no_post_hoc_parameter_search": True,
            "native_1h_premium_index": True,
            "executed_fills": False,
        },
        "results": results,
        "summary": {
            "n_total_runs": n_total,
            "n_assets": n_assets,
            "runs_per_config": 1,
            "n_with_exposure": int(n_exp),
            "n_zero_exposure": int(n_total - n_exp),
            "n_edge_proven": int(len(edge_runs)),
            "bh_oos_mean": bh_split_mean,
        },
    }

    op = reports / f"campaign303_oos_sweep_{ts}.json"
    op.write_text(json.dumps(sweep, indent=2, default=jdefault) + "\n")
    sweep_sha = sha256_file(op)

    registry = {
        "generated_at_utc": ts,
        "campaign": 303,
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
    op_reg = reports / f"campaign303_tradable_edge_registry_{ts}.json"
    op_reg.write_text(json.dumps(registry, indent=2, default=jdefault) + "\n")
    reg_sha = sha256_file(op_reg)

    summary = {
        "generated_at_utc": ts,
        "campaign": 303,
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
            "cross-sectional premium-index carry space."
        ),
    }
    op_sum = reports / f"campaign303_summary_{ts}.json"
    op_sum.write_text(json.dumps(summary, indent=2, default=jdefault) + "\n")
    sum_sha = sha256_file(op_sum)

    verdict_obj = {
        "generated_at_utc": ts,
        "campaign": 303,
        "part": "verdict",
        "analysis": "final_verdict",
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "real_data_only": True,
        "fabricated_data": False,
        "executed_fills": False,
        "finding": (
            f"No costed OOS edge proven on the real cross-sectional premium-index "
            f"carry family ({n_total} runs, {len(edge_runs)} edge)."
            if not edge_runs
            else f"Costed OOS edge proven in {len(edge_runs)} config(s) on real cross-sectional premium-index 1h data."
        ),
        "basis": "real_usdt_m_perp_cross_sectional_premium_index_carry_costed_oos_1h",
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
            "Real USDT-M perp premium-index 1h klines + real funding cashflows only",
            "executed_fills: false",
        ],
    }
    op_ver = reports / f"campaign303_verdict_{ts}.json"
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
            "campaign": 303,
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
        op_bind = reports / f"campaign303_binding_constraint_{ts}.json"
        op_bind.write_text(json.dumps(binding, indent=2, default=jdefault) + "\n")
        bind_sha = sha256_file(op_bind)
        bind_path = str(op_bind.relative_to(root))
        verdict_obj["binding_constraint_artifact"] = bind_path
        verdict_obj["binding_constraint_sha256"] = bind_sha
        op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")
        ver_sha = sha256_file(op_ver)

    print(json.dumps({
        "campaign": 303,
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "n_total_runs": n_total,
        "n_assets": n_assets,
        "n_with_exposure": int(n_exp),
        "n_edge_proven": int(len(edge_runs)),
        "n_splits": len(splits),
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
