#!/usr/bin/env python3
"""C302 — costed out-of-sample edge test of the multi-year (2020-01 .. 2026-10)
USDT-M perpetual-futures *premium-index* per-asset time-series stat-arb family.

This is a genuinely new REAL data family: ``premiumIndexKlines`` is the real-time
fair-value premium index (mark vs index) that Binance uses to set funding. It is a
distinct, higher-frequency real signal from the realized funding rate and the
perp/spot close basis used by C291/C293/C298/C299/C300, and it has never been
ingested by any prior campaign in this repository.

- DATA: real USDT-M perp premium-index 1h OHLC (native 1h, 2020-01..2026-10;
  data/cache/campaign302_premium_index_basis.pkl, SHA256-from-bytes verified).
  Execution price = real perp 1h close and funding = native 8h funding rate reused
  from the verified C299 cache (2c86... no: see C299 sha in meta). PnL is real perp
  PnL plus real funding cashflows; executed_fills:false.
- MECHANISM: per-asset premium-index time-series stat-arb. Signals (all causal,
  shift(1), premium index in absolute fraction ~ +/-1e-3):
    prem_level = premium close known at t-1 (ffill)            [carry/level]
    prem_z     = -z(premium, L)                                [premium z]
    prem_ma    = -rolling mean(premium, L)                     [premium ma]
    prem_mom   = -rolling mean(Δpremium, L)                    [premium momentum/reversion]
    prem_range = -rolling mean(high-low, L)                    [premium intrabar range]
    prem_vol   = -z(rolling std(premium, L), L)                [premium volatility]
  Higher score = long. Premium is a mean-reverting fair-value spread: high premium
  (perp rich vs index) tends to revert and longs pay funding, so the score is the
  negated premium (short the rich perp).
- FROZEN grid (do not change): 6 signals x 3 lookbacks {168,720,2160} x 3
  threshold combos x 3 holds {1,6,24} = 162 runs per asset (486 total over 3 assets).
- Walk-forward per asset: train=2160, test=720, step=720 in 1h bars over that
  asset's contiguous real window (C299 grid).
- Cost grid exactly: [[0,0],[5,5],[10,10],[20,20],[40,40]] bps on position changes
  (single leg per asset).
- Funding cashflow: at every native funding boundary, funding_pnl =
  -funding_rate * signed_weight (long pays when rate>0, short receives), using
  only funding known at/before the boundary (causal).
- Benchmarks per asset on the same WF windows: (a) flat (zero) and (b)
  buy-and-hold weight=1 with the SAME real funding cashflows.
- Edge rule exactly (identical strength to C285-C301, never relaxed), applied per
  (asset, signal, lookback, threshold-combo, hold) config:
  oos_edge_proven=true iff OOS exposure > 0 AND every cost slice has OOS net
  sum > 0 AND the mean of the per-split OOS net means is greater than the mean
  of the per-split per-asset B&H-with-funding OOS net means on the same WF
  windows AND greater than flat (zero).

Fail-closed gates at each candidate bar:
- selected feature score finite (non-NaN; warmup/gap bars -> flat);
- no NaN/non-finite perp price in the selected leg;
- funding staleness <= 24h + 1 bar in the selected leg (position zero when
  funding is stale/missing at the boundary).

Required artifacts (exact names, timestamped, SHA256-from-bytes):
- reports/campaign302_oos_sweep_<ts>.json
- reports/campaign302_tradable_edge_registry_<ts>.json
- reports/campaign302_summary_<ts>.json
- reports/campaign302_verdict_<ts>.json
- reports/campaign302_binding_constraint_<ts>.json  (if NOT_TRADABLE)
"""
from __future__ import annotations

import hashlib
import json
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

CACHE = cache_dir / "campaign302_premium_index_basis.pkl"
CACHE_META = cache_dir / "campaign302_premium_index_basis.meta.json"
CACHE_PROV = cache_dir / "campaign302_premium_index_basis.provenance.json"
C299_CACHE = cache_dir / "campaign299_multianual_perp_funding_basis_ts.pkl"

SIGNALS = ("prem_level", "prem_z", "prem_ma", "prem_mom", "prem_range", "prem_vol")
LOOKBACKS = (168, 720, 2160)
# Pre-registered (entry, exit) threshold combos per signal (>= 3). Premium index
# is an absolute fraction (~ +/-1e-3); level/range use level thresholds, z/vol use
# z thresholds.
THRESHOLD_COMBOS = {
    "prem_level": [(2e-4, 1e-4), (5e-4, 2e-4), (1e-3, 5e-4)],
    "prem_z": [(1.5, 0.5), (2.0, 1.0), (2.5, 1.5)],
    "prem_ma": [(2e-4, 1e-4), (5e-4, 2e-4), (1e-3, 5e-4)],
    "prem_mom": [(1e-5, 5e-6), (2e-5, 1e-5), (5e-5, 2e-5)],
    "prem_range": [(1e-4, 5e-5), (2e-4, 1e-4), (5e-4, 2e-4)],
    "prem_vol": [(1.5, 0.5), (2.0, 1.0), (2.5, 1.5)],
}
HOLDS = (1, 6, 24)

TRAIN, TEST, STEP = 2160, 720, 720
COST_GRID = [[0, 0], [5, 5], [10, 10], [20, 20], [40, 40]]
STALE_BARS = 24 + 1  # 24h + 1 bar on the 1h grid

# 6 signals x 3 lookbacks x 3 threshold combos x 3 holds = 162 runs per asset
RUNS_PER_ASSET = len(SIGNALS) * len(LOOKBACKS) * 3 * len(HOLDS)


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


def build_features(prem_close, prem_high, prem_low):
    """Causal base inputs; each signal applies its own shift(1)."""
    prem = prem_close.astype(float)
    delta = prem.diff()
    hl = (prem_high.astype(float) - prem_low.astype(float))
    return {"prem": prem, "delta": delta, "hl": hl}


def sig_prem_level(feats, L):
    return _mask_nonfinite(feats["prem"].ffill().shift(1))


def sig_prem_z(feats, L):
    return zscore(feats["prem"].shift(1), L)


def sig_prem_ma(feats, L):
    return rollmean(feats["prem"].shift(1), L)


def sig_prem_mom(feats, L):
    return rollmean(feats["delta"].shift(1), L)


def sig_prem_range(feats, L):
    return rollmean(feats["hl"].shift(1), L)


def sig_prem_vol(feats, L):
    return zscore(rollstd(feats["prem"].shift(1), L), L)


def SIGNAL(signal: str, feats: dict, L: int) -> pd.Series:
    """Causal score Series (higher score = long). Premium rich -> short (negated)."""
    if signal == "prem_level":
        return -sig_prem_level(feats, L)
    if signal == "prem_z":
        return -sig_prem_z(feats, L)
    if signal == "prem_ma":
        return -sig_prem_ma(feats, L)
    if signal == "prem_mom":
        return -sig_prem_mom(feats, L)
    if signal == "prem_range":
        return -sig_prem_range(feats, L)
    if signal == "prem_vol":
        return -sig_prem_vol(feats, L)
    raise ValueError(f"unknown signal {signal}")


def compute_funding_age(funding: pd.Series) -> np.ndarray:
    n = len(funding)
    idx = np.arange(n, dtype=float)
    m = funding.notna().values
    pos_series = pd.Series(np.where(m, idx, np.nan), index=funding.index)
    last = pos_series.ffill().to_numpy(dtype=float)
    return idx - last


def positions_from_score(score, entry: float, exit_level: float, H: int) -> np.ndarray:
    s = np.asarray(score, dtype=float)
    n = s.shape[0]
    desired = np.zeros(n, dtype=float)
    desired[s >= entry] = 1.0
    desired[s <= -entry] = -1.0
    seg_start = (np.arange(n) // H) * H
    seg_desired = desired[seg_start]
    pos = np.zeros(n, dtype=float)
    if n > 1:
        pos[1:] = seg_desired[:-1]
    exit_mask = np.abs(s) <= exit_level
    seg_ids = np.arange(n) // H
    exit_cum = np.zeros(n, dtype=bool)
    for seg_id in np.unique(seg_ids):
        mask = seg_ids == seg_id
        exit_cum[mask] = np.maximum.accumulate(exit_mask[mask])
    pos = np.where(exit_cum, 0.0, pos)
    pos = np.where(np.isfinite(pos), pos, 0.0)
    return pos


def _asset_series(pa: dict):
    index = pa.get("index")
    if not isinstance(index, pd.DatetimeIndex):
        index = pd.DatetimeIndex(np.asarray(index))
    prem_open = pd.Series(np.asarray(pa["prem_open"], dtype=float), index=index)
    prem_high = pd.Series(np.asarray(pa["prem_high"], dtype=float), index=index)
    prem_low = pd.Series(np.asarray(pa["prem_low"], dtype=float), index=index)
    prem_close = pd.Series(np.asarray(pa["prem_close"], dtype=float), index=index)
    return prem_open, prem_high, prem_low, prem_close, index


def main() -> int:
    if not CACHE.exists():
        raise SystemExit(f"FATAL: C302 cache missing: {CACHE}")
    if not CACHE_META.exists():
        raise SystemExit(f"FATAL: C302 meta missing: {CACHE_META}")

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

    # C299 reuse (execution price + funding), verified.
    if not C299_CACHE.exists():
        raise SystemExit(f"FATAL: C299 cache missing: {C299_CACHE}")
    c299 = load_payload(C299_CACHE)
    c299_meta = json.loads((cache_dir / "campaign299_multianual_perp_funding_basis_ts.meta.json").read_text())
    c299_meta_sha = sha256_file(cache_dir / "campaign299_multianual_perp_funding_basis_ts.meta.json")
    if c299_meta.get("real_data_only") is not True or c299_meta.get("fabricated_data") is not False:
        raise SystemExit("FATAL: C299 reuse cache provenance flags invalid")
    if "executed_fills" in c299_meta and c299_meta.get("executed_fills") is not False:
        raise SystemExit("FATAL: C299 reuse cache executed_fills must be false")

    limit_runs = int(os.environ.get("C302_LIMIT_RUNS", "0") or 0)
    results = []
    run_count = 0
    bh_means_by_asset = {}

    for s in symbols:
        pa = per_asset[s]
        _, prem_high, prem_low, prem_close, index = _asset_series(pa)

        # execution price + funding from C299 reuse on the same index
        c299_pa = c299["per_asset"][s]
        c_idx = c299_pa["index"]
        if not isinstance(c_idx, pd.DatetimeIndex):
            c_idx = pd.DatetimeIndex(np.asarray(c_idx))
        close = pd.Series(np.asarray(c299_pa["closes"], dtype=float), index=c_idx).reindex(index)
        funding = pd.Series(np.asarray(c299_pa["funding_rates"], dtype=float), index=c_idx).reindex(index)

        # Premium gap bars (real archive outage, e.g. 2021-07-01) are carried as
        # NaN and NEVER imputed; features become NaN there and the position gate
        # flattens those bars. Present premium bars must be finite.
        prem_arr = prem_close.to_numpy(dtype=float)
        if not bool(np.isfinite(prem_arr[~np.isnan(prem_arr)]).all()):
            raise SystemExit(f"FATAL: non-finite premium close on present bars for {s}.")
        if int(close.isna().sum()) != 0:
            raise SystemExit(f"FATAL: NaN present in perp closes for {s}; refusing to impute.")
        if not bool(np.isfinite(close.to_numpy(dtype=float)).all()):
            raise SystemExit(f"FATAL: non-finite value present in perp closes for {s}.")
        if not bool((close.to_numpy(dtype=float) > 0).all()):
            raise SystemExit(f"FATAL: non-positive perp price for {s}; refusing to proceed.")

        n = len(close)
        splits = wf_splits(n, TRAIN, TEST, STEP)
        if len(splits) == 0:
            raise SystemExit(f"FATAL: no OOS splits for {s}, n={n}, train={TRAIN}, test={TEST}, step={STEP}")

        perp_ret = close.pct_change().fillna(0.0).to_numpy(dtype=float)
        funding_leg = -funding.fillna(0.0).to_numpy(dtype=float)
        total_asset_ret = perp_ret + funding_leg
        funding_age = compute_funding_age(funding)

        feats = build_features(prem_close, prem_high, prem_low)

        bh_seg_means = [float(total_asset_ret[tr_e:te_e].mean()) for _, tr_e, te_e in splits]
        bh_mean = float(np.mean(bh_seg_means)) if bh_seg_means else 0.0
        bh_means_by_asset[s] = bh_mean

        for signal in SIGNALS:
            for L in LOOKBACKS:
                score = SIGNAL(signal, feats, L)
                for entry, exit_level in THRESHOLD_COMBOS[signal]:
                    for H in HOLDS:
                        run_count += 1
                        if limit_runs > 0 and run_count > limit_runs:
                            break
                        pos = positions_from_score(score, entry, exit_level, H)
                        stale = ~np.isfinite(funding_age) | (funding_age > STALE_BARS)
                        pos = np.where(stale, 0.0, pos)
                        port_ret = pos * total_asset_ret
                        price_pnl = float((pos * perp_ret).sum())
                        fund_pnl = float((pos * funding_leg).sum())

                        segs = []
                        exposure_total = 0
                        for tr_s, tr_e, te_e in splits:
                            sp = pos[tr_e:te_e]
                            sr = port_ret[tr_e:te_e]
                            t = np.abs(np.diff(sp, prepend=sp[0] if len(sp) else np.array([0.0])))
                            segs.append((float(sr.sum()), int(len(sr)), float(t.sum())))
                            exposure_total += int((sp != 0).sum())
                        turnover_total = float(sum(x[2] for x in segs))

                        bh_per_split_means = [float(total_asset_ret[tr_e:te_e].mean()) for _, tr_e, te_e in splits]
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
                            "asset": s,
                            "signal": signal,
                            "lookback": int(L),
                            "entry": float(entry),
                            "exit": float(exit_level),
                            "hold": int(H),
                            "n_splits": int(len(splits)),
                            "oos_exposure_bars_total": int(exposure_total),
                            "turnover_total": float(turnover_total),
                            "price_pnl_sum": price_pnl,
                            "funding_pnl_sum": fund_pnl,
                            "cost_slices": slices,
                            "all_cost_slices_oos_net_positive": bool(all_sum_pos),
                            "beats_bh_all_slices": bool(beats_bh),
                            "beats_flat": bool(beats_flat),
                            "bh_oos_mean": float(bh_mean),
                            "flat_oos_mean": 0.0,
                            "oos_net_mean": net_mean,
                            "edge_proven": edge,
                            "block_reason": None if edge else "no_costed_oos_edge",
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
    bh_mean_agg = float(np.mean(list(bh_means_by_asset.values()))) if bh_means_by_asset else 0.0

    dataset_block = {
        "cache": str(CACHE.relative_to(root)),
        "cache_sha256": cache_sha,
        "cache_meta": str(CACHE_META.relative_to(root)),
        "cache_meta_sha256": meta_sha,
        "cache_provenance": str(CACHE_PROV.relative_to(root)) if CACHE_PROV.exists() else None,
        "cache_provenance_sha256": prov_sha,
        "cache_pkl_bytes": int(CACHE.stat().st_size),
        "c299_execution_cache": str(C299_CACHE.relative_to(root)),
        "c299_execution_cache_sha256": sha256_file(C299_CACHE),
        "c299_meta_sha256": c299_meta_sha,
        "assets": symbols,
        "n_assets": len(symbols),
        "real_data_only": True,
        "fabricated_data": False,
    }

    sweep = {
        "generated_at_utc": ts,
        "campaign": 302,
        "part": "oos_sweep",
        "analysis": "real_perp_premium_index_per_asset_time_series_stat_arb_1h_costed_oos",
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "real_data_only": True,
        "fabricated_data": False,
        "executed_fills": False,
        "fail_closed": True,
        "mandate": (
            "C302 — pre-registered costed OOS sweep of the real USDT-M perpetual-futures "
            "premium-index (fair-value premium mark-vs-index) per-asset time-series stat-arb "
            "family (2020-01 .. 2026-10, native 1h); each asset traded on its own C299 real "
            "window vs flat and B&H-with-funding; 6 signals x 3 lookbacks x 3 threshold combos "
            "x 3 holds = 162 runs per asset (486 total); train=2160/test=720/step=720; cost grid "
            "[[0,0],[5,5],[10,10],[20,20],[40,40]] bps; real funding cashflow -rate*signed_weight "
            "at each native funding boundary; fail-closed causal per-asset gates; edge rule "
            "identical to C285-C301."
        ),
        "preflight": dataset_block,
        "data_source": dataset_block,
        "universe": {"n_assets": len(symbols), "assets": symbols},
        "config": {
            "walk_forward": {"train": TRAIN, "test": TEST, "step": STEP, "per_asset": True},
            "cost_grid_bps": COST_GRID,
            "signal_signals": list(SIGNALS),
            "lookbacks_1h": [int(l) for l in LOOKBACKS],
            "threshold_combos": {k: [[float(a), float(b)] for a, b in v] for k, v in THRESHOLD_COMBOS.items()},
            "holding_periods_1h": [int(h) for h in HOLDS],
            "total_runs_per_asset": RUNS_PER_ASSET,
            "total_runs": RUNS_PER_ASSET * len(symbols),
            "min_periods_rule": "max(20, L // 3)",
            "position_rule": "causal segment-start decision, shift(1), mean-reversion exit to flat",
            "funding_rule": "funding_pnl = -funding_rate * signed_weight at each native funding boundary (causal)",
            "score_definition": {
                "prem_level": "-premium_index_close_ffill_known_at_t-1",
                "prem_z": "-z(premium_index, L 1h bars)",
                "prem_ma": "-mean(premium_index, L 1h bars)",
                "prem_mom": "-mean(Δpremium_index, L 1h bars)",
                "prem_range": "-mean(premium_high - premium_low, L 1h bars)",
                "prem_vol": "-z(std(premium_index, L), L)",
            },
            "signal_direction": "long +1 when score>=entry, short -1 when score<=-entry, flat when |score|<=exit or no signal",
        },
        "gates": {
            "fail_closed": True,
            "requirements": [
                "selected feature score finite (gap bars/warmup NaN -> flat)",
                "no NaN/non-finite perp price in the selected leg",
                "funding staleness <= 24h + 1 bar in the selected leg",
                "no missing/None/false gate value treated as permissive",
            ],
        },
        "provenance": {
            "real_data_only": True,
            "fabricated_data": False,
            "pnl_on_real_perp_prices": True,
            "real_funding_cashflows": True,
            "premium_index_from_real_klines": True,
            "execution_price_from_c299_cache": True,
            "no_threshold_weakening": True,
            "no_cherry_picked_windows_or_costs": True,
            "no_post_hoc_parameter_search": True,
            "native_1h_premium_index": True,
            "executed_fills": False,
        },
        "results": results,
        "summary": {
            "n_total_runs": n_total,
            "n_assets": len(symbols),
            "runs_per_asset": int(n_total / len(symbols)) if symbols else 0,
            "n_with_exposure": int(n_exp),
            "n_zero_exposure": int(n_total - n_exp),
            "n_edge_proven": int(len(edge_runs)),
            "bh_oos_mean": bh_mean_agg,
            "bh_oos_mean_by_asset": bh_means_by_asset,
        },
    }

    op = reports / f"campaign302_oos_sweep_{ts}.json"
    op.write_text(json.dumps(sweep, indent=2, default=jdefault) + "\n")
    sweep_sha = sha256_file(op)

    registry = {
        "generated_at_utc": ts,
        "campaign": 302,
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
    op_reg = reports / f"campaign302_tradable_edge_registry_{ts}.json"
    op_reg.write_text(json.dumps(registry, indent=2, default=jdefault) + "\n")
    reg_sha = sha256_file(op_reg)

    summary = {
        "generated_at_utc": ts,
        "campaign": 302,
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
            "turnover, binding constraint); record a formal negative result for the 1h "
            "premium-index per-asset time-series space."
        ),
    }
    op_sum = reports / f"campaign302_summary_{ts}.json"
    op_sum.write_text(json.dumps(summary, indent=2, default=jdefault) + "\n")
    sum_sha = sha256_file(op_sum)

    verdict_obj = {
        "generated_at_utc": ts,
        "campaign": 302,
        "part": "verdict",
        "analysis": "final_verdict",
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "real_data_only": True,
        "fabricated_data": False,
        "executed_fills": False,
        "finding": (
            f"No costed OOS edge proven on the real per-asset premium-index time-series "
            f"family ({n_total} runs, {len(edge_runs)} edge)."
            if not edge_runs
            else f"Costed OOS edge proven in {len(edge_runs)} config(s) on real per-asset premium-index 1h data."
        ),
        "basis": "real_usd_m_perp_premium_index_per_asset_time_series_costed_oos_1h",
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
    op_ver = reports / f"campaign302_verdict_{ts}.json"
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
            "campaign": 302,
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
                        "asset": r["asset"],
                        "signal": r["signal"],
                        "lookback": r["lookback"],
                        "entry": r["entry"],
                        "exit": r["exit"],
                        "hold": r["hold"],
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
            "funding_pnl_summary": {
                "mean_funding_pnl_sum": float(np.mean([r["funding_pnl_sum"] for r in results])) if results else 0.0,
                "mean_price_pnl_sum": float(np.mean([r["price_pnl_sum"] for r in results])) if results else 0.0,
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
        op_bind = reports / f"campaign302_binding_constraint_{ts}.json"
        op_bind.write_text(json.dumps(binding, indent=2, default=jdefault) + "\n")
        bind_sha = sha256_file(op_bind)
        bind_path = str(op_bind.relative_to(root))
        verdict_obj["binding_constraint_artifact"] = bind_path
        verdict_obj["binding_constraint_sha256"] = bind_sha
        op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")
        ver_sha = sha256_file(op_ver)

    print(json.dumps({
        "campaign": 302,
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "n_total_runs": n_total,
        "n_assets": len(symbols),
        "n_with_exposure": int(n_exp),
        "n_edge_proven": int(len(edge_runs)),
        "n_splits_per_asset": len(wf_splits(len(_asset_series(per_asset[symbols[0]])[3]), TRAIN, TEST, STEP)),
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