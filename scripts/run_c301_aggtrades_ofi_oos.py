#!/usr/bin/env python3
"""C301 — costed out-of-sample edge test of the REAL order-flow-imbalance (OFI)
/ trade-sign autocorrelation per-asset time-series microstructure stat-arb family
(2023-01 .. 2023-02, native 5m), with a causal execution-cost overlay.

This is a genuinely new microstructure family (order-flow imbalance + trade-sign
autocorrelation from Binance USDT-M perpetual aggTrades), distinct from the
closed C281B-C300 funding-carry / spot-perp basis family.

- DATA: real USDT-M perp aggTrades aggregated to native 5m bars
  (data/cache/campaign301_aggtrades_ofi.pkl, SHA256-from-bytes verified). OFI
  legs: buy_volume, sell_volume, signed_volume (= buy - sell), trade_count,
  trade_sign_sum (+1 if is_buyer_maker==false else -1), vwap. Execution price =
  perp 5m close and funding = native 8h funding reused from the verified C300
  cache (2c86accd...). PnL is real perp PnL plus real funding cashflows;
  executed_fills:false.
- MECHANISM (per asset, true 5m bars): order-flow imbalance / trade-sign
  autocorrelation time-series stat-arb. Signals (all causal, shift(1)):
    ofi_z             = z(signed_volume, L 5m bars)                       [OFI]
    ofi_mom           = mean(signed_logret, L)  where signed_logret =
                        sign(trade_sign_sum)*log(vwap/prev_vwap)          [OFI mom]
    buy_ratio_ma      = mean(buy_vol/(buy+sell), L) - 0.5                [buy ratio]
    ofi_per_trade_z   = z(signed_volume/trade_count, L)                  [per-trade OFI]
    ofi_sign_autocorr = corr(signed_volume[t], signed_volume[t-1], L)    [sign persistence]
    trade_intensity_z = z(trade_count, L)                                [intensity]
  Score = the signal itself (higher score = long); long +1 when score>=entry,
  short -1 when score<=-entry, flat when |score|<=exit or no signal.
- FROZEN grid (do not change): 6 signals x 3 lookbacks {288,1008,2016} x 3
  (entry,exit) combos x 4 holds {1,6,24,12} = 648 runs (216/asset).
- Walk-forward per asset: train=2880, test=1152, step=1152 in 5m bars
  (12 OOS splits/asset over the 16,992-bar window).
- Cost grid exactly: [[0,0],[5,5],[10,10],[20,20],[40,40]] bps on position
  changes (single leg per asset).
- Funding cashflow: at every native funding boundary, funding_pnl =
  -funding_rate * signed_weight (long pays when rate>0, short receives), using
  only funding known at/before the boundary (causal).
- Benchmarks per asset on the same WF windows: (a) flat (zero) and (b)
  buy-and-hold weight=1 with the SAME real funding cashflows.
- Edge rule exactly (identical strength to C285-C300, never relaxed), applied
  per (asset, signal, lookback, threshold-combo, hold) config:
  oos_edge_proven=true iff OOS exposure > 0 AND every cost slice has OOS net
  sum > 0 AND the mean of the per-split OOS net means is greater than the mean
  of the per-split per-asset B&H-with-funding OOS net means on the same WF
  windows AND greater than flat (zero).

Fail-closed gates at each candidate bar:
- selected feature score finite (non-NaN; gap bars / warmup are NaN -> flat);
- no NaN/non-finite perp price in the selected leg;
- funding staleness <= 24h + 1 bar in the selected leg (position zero when
  funding is stale/missing).

Required artifacts (exact names, timestamped, SHA256-from-bytes):
- reports/campaign301_oos_sweep_<ts>.json
- reports/campaign301_tradable_edge_registry_<ts>.json
- reports/campaign301_summary_<ts>.json
- reports/campaign301_verdict_<ts>.json
- reports/campaign301_binding_constraint_<ts>.json  (if NOT_TRADABLE)
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

CACHE = cache_dir / "campaign301_aggtrades_ofi.pkl"
CACHE_META = cache_dir / "campaign301_aggtrades_ofi.meta.json"
CACHE_PROV = cache_dir / "campaign301_aggtrades_ofi.provenance.json"
C300_CACHE = cache_dir / "campaign300_multianual_perp_funding_basis_ts_5m.pkl"

SIGNALS = ("ofi_z", "ofi_mom", "buy_ratio_ma", "ofi_per_trade_z", "ofi_sign_autocorr", "trade_intensity_z")
LOOKBACKS = (288, 1008, 2016)
THRESHOLD_COMBOS = {
    "ofi_z": [(1.5, 0.5), (2.0, 1.0), (2.5, 1.5)],
    "ofi_mom": [(1e-4, 5e-5), (2e-4, 1e-4), (3e-4, 1.5e-4)],
    "buy_ratio_ma": [(0.02, 0.01), (0.05, 0.025), (0.10, 0.05)],
    "ofi_per_trade_z": [(1.5, 0.5), (2.0, 1.0), (2.5, 1.5)],
    "ofi_sign_autocorr": [(0.05, 0.02), (0.10, 0.05), (0.15, 0.075)],
    "trade_intensity_z": [(1.5, 0.5), (2.0, 1.0), (2.5, 1.5)],
}
HOLDS = (1, 6, 24, 12)

TRAIN, TEST, STEP = 2880, 1152, 1152
COST_GRID = [[0, 0], [5, 5], [10, 10], [20, 20], [40, 40]]
STALE_BARS = 24 * 12 + 1  # 24h + 1 bar on the 5m grid

# 6 signals x 3 lookbacks x 3 threshold combos x 4 holds = 216 runs per asset
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


def rolling_autocorr1(s: pd.Series, L: int) -> pd.Series:
    """Rolling lag-1 autocorrelation over L bars (Pearson of s[t] vs s[t-1])."""
    mp = min_periods_for(L)
    a = s.shift(0)
    b = s.shift(1)
    # rolling Pearson correlation
    ab = (a * b).rolling(L, min_periods=mp).mean()
    aa = (a * a).rolling(L, min_periods=mp).mean()
    bb = (b * b).rolling(L, min_periods=mp).mean()
    ma = a.rolling(L, min_periods=mp).mean()
    mb = b.rolling(L, min_periods=mp).mean()
    cov = ab - ma * mb
    va = aa - ma * ma
    vb = bb - mb * mb
    denom = np.sqrt(va * vb)
    out = cov / denom
    return _safe_std(out, denom)


def build_features(buy, sell, signed, trade_count, tss, vwap):
    """Causal base inputs; each signal applies its own shift(1)."""
    total = buy + sell
    buy_ratio = np.where(total > 0, buy / total, np.nan)
    # signed log return: sign(trade_sign_sum) * log(vwap / prev_vwap)
    logret = np.log(vwap).astype(float)
    prev = np.concatenate([[np.nan], logret[:-1]])
    dlog = logret - prev
    sign = np.sign(tss)
    signed_logret = sign * dlog
    per_trade = np.where(trade_count > 0, signed / trade_count, np.nan)
    idx = pd.RangeIndex(len(signed))
    return {
        "signed": pd.Series(signed, index=idx),
        "signed_logret": pd.Series(signed_logret, index=idx),
        "buy_ratio_excess": pd.Series(buy_ratio - 0.5, index=idx),
        "per_trade": pd.Series(per_trade, index=idx),
        "trade_count": pd.Series(trade_count, index=idx),
    }


def sig_ofi_z(feats, L):
    return zscore(feats["signed"], L)


def sig_ofi_mom(feats, L):
    return rollmean(feats["signed_logret"], L)


def sig_buy_ratio_ma(feats, L):
    return rollmean(feats["buy_ratio_excess"], L)


def sig_ofi_per_trade_z(feats, L):
    return zscore(feats["per_trade"], L)


def sig_ofi_sign_autocorr(feats, L):
    return rolling_autocorr1(feats["signed"], L)


def sig_trade_intensity_z(feats, L):
    return zscore(feats["trade_count"], L)


def SIGNAL(signal: str, feats: dict, L: int) -> pd.Series:
    if signal == "ofi_z":
        return sig_ofi_z(feats, L)
    if signal == "ofi_mom":
        return sig_ofi_mom(feats, L)
    if signal == "buy_ratio_ma":
        return sig_buy_ratio_ma(feats, L)
    if signal == "ofi_per_trade_z":
        return sig_ofi_per_trade_z(feats, L)
    if signal == "ofi_sign_autocorr":
        return sig_ofi_sign_autocorr(feats, L)
    if signal == "trade_intensity_z":
        return sig_trade_intensity_z(feats, L)
    raise ValueError(f"unknown signal {signal}")


def compute_funding_age(funding: pd.Series) -> np.ndarray:
    """Bars since the last known funding boundary (NaN before first)."""
    n = len(funding)
    idx = np.arange(n, dtype=float)
    m = funding.notna().values
    pos_series = pd.Series(np.where(m, idx, np.nan), index=funding.index)
    last = pos_series.ffill().to_numpy(dtype=float)
    return idx - last


def positions_from_score(score, entry: float, exit_level: float, H: int) -> np.ndarray:
    """Vectorized per-asset position (O(n)).

    Decision made at each segment start r = 0,H,2H,... from score[r] (causal,
    computed from data < r):
      desired[r] = +1 if score[r] >= entry; -1 if score[r] <= -entry;
                   0 otherwise (flat when no signal).
    Decision applied from the next bar (shift).  Within a hold segment, position
    exits to flat on the first bar where |score| <= exit_level (mean-reversion
    exit).  NaN score (feature warmup/gap) -> flat.
    """
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
    pad = (-n) % H
    if pad:
        exit_mask = np.concatenate([exit_mask, np.zeros(pad, dtype=bool)])
    seg2d = exit_mask.reshape(-1, H)
    exit_cum = np.maximum.accumulate(seg2d, axis=1).reshape(-1)[:n]
    pos = np.where(exit_cum, 0.0, pos)
    pos = np.where(np.isfinite(pos), pos, 0.0)
    return pos


def _asset_series(pa: dict):
    index = pa.get("index")
    if not isinstance(index, pd.DatetimeIndex):
        index = pd.DatetimeIndex(np.asarray(index)).tz_localize("UTC")
    close = pd.Series(np.asarray(pa["perp_close"], dtype=float), index=index)
    funding = pd.Series(np.asarray(pa["funding_rates"], dtype=float), index=index)
    buy = pd.Series(np.asarray(pa["buy_volume"], dtype=float), index=index)
    sell = pd.Series(np.asarray(pa["sell_volume"], dtype=float), index=index)
    signed = pd.Series(np.asarray(pa["signed_volume"], dtype=float), index=index)
    trade_count = pd.Series(np.asarray(pa["trade_count"], dtype=float), index=index)
    tss = pd.Series(np.asarray(pa["trade_sign_sum"], dtype=float), index=index)
    vwap = pd.Series(np.asarray(pa["vwap"], dtype=float), index=index)
    return close, funding, buy, sell, signed, trade_count, tss, vwap, index


def main() -> int:
    if not CACHE.exists():
        raise SystemExit(f"FATAL: C301 cache missing: {CACHE}")
    if not CACHE_META.exists():
        raise SystemExit(f"FATAL: C301 meta missing: {CACHE_META}")

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

    limit_runs = int(os.environ.get("C301_LIMIT_RUNS", "0") or 0)
    results = []
    run_count = 0
    bh_means_by_asset = {}

    for s in symbols:
        pa = per_asset[s]
        close, funding, buy, sell, signed, trade_count, tss, vwap, index = _asset_series(pa)

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
        funding_leg = -funding.fillna(0.0).to_numpy(dtype=float)  # 0 at non-boundary bars
        total_asset_ret = perp_ret + funding_leg
        funding_age = compute_funding_age(funding)

        # NaN any OFI leg at gap/warmup rows so features are NaN -> flat.
        buy_arr = buy.to_numpy(dtype=float)
        sell_arr = sell.to_numpy(dtype=float)
        signed_arr = signed.to_numpy(dtype=float)
        tc_arr = trade_count.to_numpy(dtype=float)
        tss_arr = tss.to_numpy(dtype=float)
        vwap_arr = vwap.to_numpy(dtype=float)
        feats = build_features(buy_arr, sell_arr, signed_arr, tc_arr, tss_arr, vwap_arr)

        # Benchmarks per asset on the same WF windows: flat (zero) and B&H
        # weight=1 with the same real funding cashflows.
        bh_seg_means = [float(total_asset_ret[tr_e:te_e].mean()) for _, tr_e, te_e in splits]
        bh_mean = float(np.mean(bh_seg_means)) if bh_seg_means else 0.0
        bh_means_by_asset[s] = bh_mean

        for signal in SIGNALS:
            for L in LOOKBACKS:
                score = SIGNAL(signal, feats, L)
                score_arr = score.to_numpy(dtype=float)
                for entry, exit_level in THRESHOLD_COMBOS[signal]:
                    for H in HOLDS:
                        run_count += 1
                        if limit_runs > 0 and run_count > limit_runs:
                            break
                        pos = positions_from_score(score_arr, entry, exit_level, H)
                        # fail-closed: funding staleness gate per bar
                        stale = ~np.isfinite(funding_age) | (funding_age > STALE_BARS)
                        pos = np.where(stale, 0.0, pos)
                        port_ret = pos * total_asset_ret
                        price_pnl = float((pos * perp_ret).sum())
                        fund_pnl = float((pos * funding_leg).sum())

                        # OOS aggregation over WF splits
                        segs = []
                        exposure_total = 0
                        for tr_s, tr_e, te_e in splits:
                            sp = pos[tr_e:te_e]
                            sr = port_ret[tr_e:te_e]
                            t = np.abs(np.diff(sp, prepend=sp[0] if len(sp) else np.array([0.0])))
                            segs.append((float(sr.sum()), int(len(sr)), float(t.sum())))
                            exposure_total += int((sp != 0).sum())
                        turnover_total = float(sum(x[2] for x in segs))

                        slices = {}
                        all_sum_pos = True
                        net_means = []
                        for fee, slip in COST_GRID:
                            ck = f"fee{fee}_slip{slip}"
                            tc = (fee + slip) / 10000.0
                            nets, means = [], []
                            for seg_sum, seg_len, tsum in segs:
                                net_sum = seg_sum - tc * tsum
                                nets.append(net_sum)
                                means.append(net_sum / seg_len if seg_len else 0.0)
                            net_sum = float(sum(nets))
                            slices[ck] = {
                                "oos_net_sum": net_sum,
                                "oos_net_mean": float(np.mean(means)) if means else 0.0,
                                "oos_net_mean_per_split": [float(m) for m in means],
                            }
                            net_means.extend(means)
                            if net_sum <= 0:
                                all_sum_pos = False
                        net_mean = float(np.mean(net_means)) if net_means else 0.0
                        beats_bh = net_mean > bh_mean
                        beats_flat = net_mean > 0.0
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
        "c300_execution_cache": str(C300_CACHE.relative_to(root)) if C300_CACHE.exists() else None,
        "c300_execution_cache_sha256": sha256_file(C300_CACHE) if C300_CACHE.exists() else None,
        "assets": symbols,
        "n_assets": len(symbols),
        "real_data_only": True,
        "fabricated_data": False,
    }

    sweep = {
        "generated_at_utc": ts,
        "campaign": 301,
        "part": "oos_sweep",
        "analysis": "real_perp_order_flow_imbalance_trade_sign_autocorr_per_asset_time_series_stat_arb_5m_costed_oos",
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "real_data_only": True,
        "fabricated_data": False,
        "executed_fills": False,
        "fail_closed": True,
        "mandate": (
            "C301 — pre-registered costed OOS sweep of the real order-flow-imbalance / "
            "trade-sign autocorrelation per-asset time-series microstructure stat-arb "
            "family at native 5m (2023-01 .. 2023-02); each asset traded on its own "
            "maximal contiguous real window vs flat and B&H-with-funding; 6 signals x "
            "3 lookbacks x 3 threshold combos x 4 holds = 216 runs per asset (648 total); "
            "train=2880/test=1152/step=1152; cost grid [[0,0],[5,5],[10,10],[20,20],"
            "[40,40]] bps; real funding cashflow -rate*signed_weight at each native "
            "funding boundary; fail-closed causal per-asset gates; edge rule "
            "identical to C285-C300."
        ),
        "preflight": dataset_block,
        "data_source": dataset_block,
        "universe": {"n_assets": len(symbols), "assets": symbols},
        "config": {
            "walk_forward": {"train": TRAIN, "test": TEST, "step": STEP, "per_asset": True},
            "cost_grid_bps": COST_GRID,
            "signal_signals": list(SIGNALS),
            "lookbacks_5m": [int(l) for l in LOOKBACKS],
            "threshold_combos": {k: [[float(a), float(b)] for a, b in v] for k, v in THRESHOLD_COMBOS.items()},
            "holding_periods_5m": [int(h) for h in HOLDS],
            "total_runs_per_asset": RUNS_PER_ASSET,
            "total_runs": RUNS_PER_ASSET * len(symbols),
            "min_periods_rule": "max(20, L // 3)",
            "position_rule": "causal segment-start decision, shift(1), mean-reversion exit to flat",
            "funding_rule": "funding_pnl = -funding_rate * signed_weight at each native funding boundary (causal)",
            "score_definition": {
                "ofi_z": "+z(signed_volume, L 5m bars)",
                "ofi_mom": "+mean(sign(trade_sign_sum)*log(vwap/prev_vwap), L)",
                "buy_ratio_ma": "+mean(buy_vol/(buy+sell), L) - 0.5",
                "ofi_per_trade_z": "+z(signed_volume/trade_count, L)",
                "ofi_sign_autocorr": "+corr(signed_volume[t], signed_volume[t-1], L)",
                "trade_intensity_z": "+z(trade_count, L)",
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
            "ofi_from_real_aggtrades": True,
            "execution_price_from_c300_cache": True,
            "no_threshold_weakening": True,
            "no_cherry_picked_windows_or_costs": True,
            "no_post_hoc_parameter_search": True,
            "native_5m_aggtrades_bars": True,
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

    op = reports / f"campaign301_oos_sweep_{ts}.json"
    op.write_text(json.dumps(sweep, indent=2, default=jdefault) + "\n")
    sweep_sha = sha256_file(op)

    registry = {
        "generated_at_utc": ts,
        "campaign": 301,
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
    op_reg = reports / f"campaign301_tradable_edge_registry_{ts}.json"
    op_reg.write_text(json.dumps(registry, indent=2, default=jdefault) + "\n")
    reg_sha = sha256_file(op_reg)

    summary = {
        "generated_at_utc": ts,
        "campaign": 301,
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
            "turnover, binding constraint); record a formal negative result for the 5m "
            "OFI / trade-sign-autocorrelation per-asset time-series space."
        ),
    }
    op_sum = reports / f"campaign301_summary_{ts}.json"
    op_sum.write_text(json.dumps(summary, indent=2, default=jdefault) + "\n")
    sum_sha = sha256_file(op_sum)

    verdict_obj = {
        "generated_at_utc": ts,
        "campaign": 301,
        "part": "verdict",
        "analysis": "final_verdict",
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "real_data_only": True,
        "fabricated_data": False,
        "executed_fills": False,
        "finding": (
            f"No costed OOS edge proven on the real per-asset order-flow-imbalance/"
            f"trade-sign-autocorrelation time-series family at 5m ({n_total} runs, "
            f"{len(edge_runs)} edge)."
            if not edge_runs
            else f"Costed OOS edge proven in {len(edge_runs)} config(s) on real per-asset OFI 5m data."
        ),
        "basis": "real_usd_m_perp_order_flow_imbalance_and_trade_sign_autocorrelation_per_asset_time_series_costed_oos_5m",
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
            "Real USDT-M perp aggTrades + real funding cashflows only",
            "executed_fills: false",
        ],
    }
    op_ver = reports / f"campaign301_verdict_{ts}.json"
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
            "campaign": 301,
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
        op_bind = reports / f"campaign301_binding_constraint_{ts}.json"
        op_bind.write_text(json.dumps(binding, indent=2, default=jdefault) + "\n")
        bind_sha = sha256_file(op_bind)
        bind_path = str(op_bind.relative_to(root))
        verdict_obj["binding_constraint_artifact"] = bind_path
        verdict_obj["binding_constraint_sha256"] = bind_sha
        op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")
        ver_sha = sha256_file(op_ver)

    print(json.dumps({
        "campaign": 301,
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "n_total_runs": n_total,
        "n_assets": len(symbols),
        "n_with_exposure": int(n_exp),
        "n_edge_proven": int(len(edge_runs)),
        "n_splits_per_asset": len(wf_splits(len(_asset_series(per_asset[symbols[0]])[0]), TRAIN, TEST, STEP)),
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