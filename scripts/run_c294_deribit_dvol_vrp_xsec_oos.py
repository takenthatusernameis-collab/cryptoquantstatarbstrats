#!/usr/bin/env python3
"""C294 — costed out-of-sample edge test of a NEW economic dimension: real implied
volatility (Deribit DVOL) variance-risk-premium / BTC-vs-ETH relative-value
statistical arbitrage.

NEW asset class vs C281B..C293 (all spot / perp price-or-funding on 5m):
- NEW DATA: real 30-day constant-maturity IMPLIED volatility (Deribit DVOL index,
  1h, BTC & ETH, contiguous 2023-03-24T14:00Z -> 2026-11-13T21:00Z, 31,928 bars) +
  real realized vol computed from Binance BTC/ETH spot 1h closes.
- NEW MECHANISM: variance risk premium / vol carry / BTC-vs-ETH relative value.
  Features (causal shift(1), 1h bars):
    iv_rv_spread = DVOL - trailing annualized realized vol over L   [VRP]
    iv_z         = rolling z(DVOL) over L                            [IV level]
    dvol_x_spread= z(DVOL_BTC - DVOL_ETH) over L                     [BTC/ETH RV]
  L in {24, 168, 720} 1h bars, min_periods = max(3, L//3).

Two reported PnL legs (both real-input):
- PRIMARY (real cashflow leg): spot relative value w_btc*r_btc - w_eth*r_eth from
  real Binance BTC/ETH 1h returns; cost charged on BOTH legs (turnover = sum|dw|).
  This is the formal edge claim.
- DIAGNOSTIC (variance-swap-proxy leg): notional*(RV_realized^2 - IV_entry^2)*sign(w)
  over the holding horizon from real DVOL/RV; artifact records
  pnl_model=variance_swap_proxy, executed_fills=false,
  inputs=real_dvol_iv+real_realized_vol; cost on vol notional. NEVER an executed fill.

Pre-registered protocol (no post-hoc parameter search):
- Universe: BTC & ETH (DVOL only returns these two).
- Cross-sectional portfolio at each 1h rebalance bar: rank the 2 assets by score;
  long top per-leg K_eff and short bottom K_eff.  With a 2-asset cross-section the
  per-leg count is K_eff = max(1, min(K, N//2)) = 1: long top-1 / short bottom-1,
  weight 0.5/K_eff = 0.5 per leg, gross 1.0, dollar-neutral, cap 0.5.
  Holding period H in {1,6,24} 1h bars. weights.shift(1).fillna(0.0) before PnL.
- Full pre-registered grid: 3 features x 3 lookbacks x 3 holds = 27 runs (K fixed=2).
- Walk-forward: train=720, test=168, step=168 1h bars.
- Cost grid exactly: [[0,0],[5,5],[10,10],[20,20],[40,40]] bps, charged on BOTH legs.
- Benchmarks (same costs, same WF windows): BTC-vs-ETH equal-weight buy-and-hold
  (primary comparison) AND always-long-vol (short VRP) buy-and-hold (diagnostic).
- Edge rule exactly (identical to C285/C286/C288/C290/C291/C292/C293, never relaxed):
  oos_edge_proven=true iff OOS exposure > 0 AND every cost slice has OOS net sum > 0
  AND the mean of the per-split OOS net means is greater than the mean of the
  per-split equal-weight B&H OOS net means on the same WF windows (same cost slice).

Fail-closed gates at each candidate 1h rebalance bar:
- selected feature score finite for at least 2*K_eff assets;
- cross-sectional score dispersion > 0;
- no NaN/non-finite spot price in any selected leg;
- no missing/None/false gate value treated as permissive.

Required artifacts (timestamped, SHA256-from-bytes):
- reports/campaign294_oos_sweep_<ts>.json
- reports/campaign294_tradable_edge_registry_<ts>.json
- reports/campaign294_summary_<ts>.json
- reports/campaign294_verdict_<ts>.json
- reports/campaign294_binding_constraint_<ts>.json (if NOT_TRADABLE)
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

PKL = cache_dir / "campaign294_deribit_dvol.pkl"
META = cache_dir / "campaign294_deribit_dvol.meta.json"
PROV = cache_dir / "campaign294_deribit_dvol.provenance.json"

FEATURES = ("iv_rv_spread", "iv_z", "dvol_x_spread")
LOOKBACKS = (24, 168, 720)  # 1h bars
K_REQUESTED = 2
HOLDS = (1, 6, 24)

TRAIN, TEST, STEP = 720, 168, 168
COST_GRID = [[0, 0], [5, 5], [10, 10], [20, 20], [40, 40]]
ANNUALIZATION = float(24 * 365)  # 8760 hourly bars/year
NOTIONAL = 1.0

# 3 features x 3 lookbacks x 3 holds = 27 runs (K fixed = 2)


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
    return max(3, L // 3)


def effective_k(k: int, n_assets: int) -> int:
    """Per-leg asset count for a cross-section of n_assets.

    With a 2-asset cross-section the only dollar-neutral construction is long the
    top-1 / short the bottom-1, so K_eff = max(1, min(K, N//2)) = 1.  Documented
    deviation from the requested K=2 (which is degenerate for N=2: long both and
    short both would cancel).
    """
    return max(1, min(int(k), n_assets // 2))


def _safe_std(out: pd.DataFrame, std: pd.DataFrame) -> pd.DataFrame:
    bad = (~np.isfinite(np.asarray(std))) | (np.asarray(std) <= 0)
    return out.mask(pd.DataFrame(bad, index=out.index, columns=out.columns))


def _mask_nonfinite(out: pd.DataFrame) -> pd.DataFrame:
    return out.mask(pd.DataFrame(~np.isfinite(np.asarray(out)), index=out.index, columns=out.columns))


def build_features(dvol: pd.DataFrame, spot: pd.DataFrame) -> dict:
    logret = np.log(spot).diff()
    spot_ret = spot.pct_change()
    return {"logret": logret, "spot_ret": spot_ret, "dvol": dvol}


def iv_rv_spread(feats: dict, L: int) -> pd.DataFrame:
    """DVOL - trailing annualized realized vol over L 1h bars, causal (shift(1))."""
    mp = min_periods_for(L)
    rv = feats["logret"].rolling(L, min_periods=mp).std() * float(np.sqrt(ANNUALIZATION))
    s = (feats["dvol"] - rv).shift(1)
    return _mask_nonfinite(s)


def iv_z(feats: dict, L: int) -> pd.DataFrame:
    """Rolling z-score of DVOL over L 1h bars, causal (shift(1))."""
    mp = min_periods_for(L)
    s = feats["dvol"].shift(1)
    mean = s.rolling(L, min_periods=mp).mean()
    std = s.rolling(L, min_periods=mp).std()
    z = (s - mean) / std
    return _safe_std(z, std)


def dvol_x_spread(feats: dict, L: int) -> pd.DataFrame:
    """Cross-sectional z of (DVOL_BTC - DVOL_ETH) over L 1h bars, causal (shift(1)).

    Per-asset score: BTC = +z (long BTC when BTC IV richer), ETH = -z.
    """
    mp = min_periods_for(L)
    dvol = feats["dvol"]
    raw = (dvol["BTC"] - dvol["ETH"]).shift(1)
    mean = raw.rolling(L, min_periods=mp).mean()
    std = raw.rolling(L, min_periods=mp).std()
    z = (raw - mean) / std
    bad = (~np.isfinite(np.asarray(std))) | (np.asarray(std) <= 0)
    z = z.mask(pd.Series(bad, index=z.index))
    out = pd.DataFrame({"BTC": z, "ETH": -z}, index=dvol.index)
    return _mask_nonfinite(out)


def SIGNAL(feature: str, feats: dict, L: int) -> pd.DataFrame:
    """Return a causal score DataFrame (higher score = long that asset)."""
    if feature == "iv_rv_spread":
        return iv_rv_spread(feats, L)
    if feature == "iv_z":
        return iv_z(feats, L)
    if feature == "dvol_x_spread":
        return dvol_x_spread(feats, L)
    raise ValueError(f"unknown feature {feature}")


def build_weights(signal_df: pd.DataFrame, price_df: pd.DataFrame, K_eff: int, H: int, r_start: int = 0):
    """Cross-sectional portfolio construction at each 1h rebalance bar (fail-closed)."""
    n = len(signal_df)
    sig = signal_df.to_numpy(dtype=float)
    px = price_df.to_numpy(dtype=float)
    m = sig.shape[1]
    weights = np.zeros((n, m), dtype=float)
    total_rebalances = 0
    passed_rebalances = 0
    blocked_reasons: dict[str, int] = {}
    r = r_start
    while r < n:
        total_rebalances += 1
        row = sig[r]
        finite = np.isfinite(row)
        ok = True
        reason = None
        if int(finite.sum()) < 2 * K_eff:
            ok = False
            reason = "signal_coverage"
        long_idx = short_idx = None
        if ok:
            vals = row[finite]
            dispersion = float(vals.max() - vals.min()) if len(vals) else 0.0
            if not (np.isfinite(dispersion) and dispersion > 0.0):
                ok = False
                reason = "zero_dispersion"
        if ok:
            order = np.argsort(-vals, kind="stable")
            finite_positions = np.where(finite)[0]
            long_idx = finite_positions[order[:K_eff]]
            short_idx = finite_positions[order[-K_eff:]]
            leg_idx = np.concatenate([long_idx, short_idx])
            if not bool(np.isfinite(px[r][leg_idx]).all()):
                ok = False
                reason = "price_nan"
        if ok:
            passed_rebalances += 1
            w = np.zeros(m, dtype=float)
            w[long_idx] = 0.5 / K_eff
            w[short_idx] = -0.5 / K_eff
        else:
            blocked_reasons[reason] = blocked_reasons.get(reason, 0) + 1
            w = np.zeros(m, dtype=float)
        end = min(r + H, n)
        weights[r:end] = w
        r += H

    return pd.DataFrame(weights, index=signal_df.index, columns=signal_df.columns), {
        "rebalance_bars_total": int(total_rebalances),
        "rebalance_bars_passed": int(passed_rebalances),
        "gate_pass_share": float(passed_rebalances / total_rebalances) if total_rebalances else 0.0,
        "blocked_rebalance_reasons": blocked_reasons,
    }


def _split_segments(port_ret: pd.Series, pos: pd.DataFrame, splits):
    seg = []
    exposure_total = 0
    for _, tr_e, te_e in splits:
        seg_pos = pos.iloc[tr_e:te_e]
        seg_ret = port_ret.iloc[tr_e:te_e]
        t = seg_pos.diff().abs().sum(axis=1)
        t.iloc[0] = float(seg_pos.iloc[0].abs().sum())
        seg.append((float(seg_ret.sum()), float(len(seg_ret)), float(t.sum())))
        exposure_total += int((seg_pos.abs().sum(axis=1) > 0).sum())
    return seg, exposure_total


def costed_oos(port_ret: pd.Series, pos: pd.DataFrame, splits, cost_grid, bh_mean_per_slice):
    """Costed OOS aggregation over the pre-registered cost grid.

    port_ret is the per-bar real spot relative-value PnL.  Turnover is
    sum|dw| across both legs (BTC and ETH); cost = tc * turnover on BOTH legs.
    bh_mean_per_slice: {cost_key: benchmark mean-per-split OOS net mean}.
    """
    seg, exposure_total = _split_segments(port_ret, pos, splits)
    turnover_total = float(sum(s[2] for s in seg))

    slices = {}
    all_sum_pos = True
    all_mean_beats = True
    for fee, slip in cost_grid:
        ck = f"fee{fee}_slip{slip}"
        tc = (fee + slip) / 10000.0
        nets, means = [], []
        for seg_sum, seg_len, tsum in seg:
            net_sum = seg_sum - tc * tsum
            nets.append(net_sum)
            means.append(net_sum / seg_len if seg_len else 0.0)
        net_sum = float(sum(nets))
        net_mean = float(np.mean(means)) if means else 0.0
        bh = float(bh_mean_per_slice.get(ck, 0.0))
        slices[ck] = {
            "oos_net_sum": net_sum,
            "oos_net_mean": net_mean,
            "oos_net_mean_per_split": [float(m) for m in means],
            "bh_oos_mean": bh,
            "beats_bh": bool(net_mean > bh),
        }
        if net_sum <= 0:
            all_sum_pos = False
        if net_mean <= bh:
            all_mean_beats = False
    return slices, exposure_total, turnover_total, all_sum_pos, all_mean_beats


def benchmark_spot_slices(bh_ret: pd.Series, spot_ret: pd.DataFrame, splits, cost_grid):
    """BTC-vs-ETH equal-weight B&H: constant 0.5/0.5, entry turnover at split start."""
    bh_mean_per_slice = {}
    for fee, slip in cost_grid:
        tc = (fee + slip) / 10000.0
        means = []
        for _, tr_e, te_e in splits:
            seg = bh_ret.iloc[tr_e:te_e]
            seg_len = float(len(seg))
            entry_turnover = float(1.0)  # 0 -> 0.5/0.5 = |0.5|+|0.5|
            net = float(seg.sum()) - tc * entry_turnover
            means.append(net / seg_len if seg_len else 0.0)
        bh_mean_per_slice[f"fee{fee}_slip{slip}"] = float(np.mean(means)) if means else 0.0
    return bh_mean_per_slice


def variance_swap_proxy(weights: pd.DataFrame, dvol: pd.DataFrame, logret: pd.DataFrame, H: int, splits) -> tuple[pd.Series, pd.Series]:
    """DIAGNOSTIC variance-swap-proxy leg (NOT executed fills).

    At each rebalance entry t (pos change), over the holding horizon (t, exit]:
      payoff_a = w[t,a] * (RV_realized_a^2 - IV_entry_a^2)
      RV_realized_a = annualized std of logret over the held period (decimal vol)
      IV_entry_a    = DVOL at entry (decimal vol)
    Payoff is assigned to the exit bar.  Returns (payoff_series, entry_turnover_series).
    """
    n = len(weights)
    m = weights.shape[1]
    w = weights.to_numpy(dtype=float)
    dv = dvol.to_numpy(dtype=float) / 100.0
    lr = logret.to_numpy(dtype=float)
    payoff = np.zeros(n, dtype=float)
    entry_turn = np.zeros(n, dtype=float)

    prev = np.vstack([np.zeros((1, m)), w[:-1]])
    entry_mask = np.any(np.abs(w - prev) > 1e-12, axis=1)
    for t in np.where(entry_mask)[0]:
        t = int(t)
        e = min(t + H, n)
        entry_turn[t] = float(np.abs(w[t] - prev[t]).sum())
        if e <= t + 1:
            payoff[min(e, n - 1)] += 0.0
            continue
        seg = lr[t + 1 : e + 1]
        if seg.shape[0] < 2:
            continue
        rv = np.nanstd(seg, axis=0, ddof=1) * float(np.sqrt(ANNUALIZATION))
        iv = dv[t]
        contrib = w[t] * (rv ** 2 - iv ** 2)
        payoff[min(e, n - 1)] += float(np.nansum(contrib))
    return pd.Series(payoff, index=weights.index), pd.Series(entry_turn, index=weights.index)


def main() -> int:
    if not PKL.exists():
        raise SystemExit(f"FATAL: C294 cache missing: {PKL}")
    if not META.exists():
        raise SystemExit(f"FATAL: C294 meta missing: {META}")

    pkl_sha = sha256_file(PKL)
    meta_sha = sha256_file(META)
    prov_sha = sha256_file(PROV) if PROV.exists() else None
    meta = json.loads(META.read_text())
    if pkl_sha != meta.get("sha256_from_bytes"):
        raise SystemExit(f"FATAL: sha256 mismatch: {pkl_sha} != {meta.get('sha256_from_bytes')}")
    if meta.get("real_data_only") is not True or meta.get("fabricated_data") is not False:
        raise SystemExit("FATAL: dataset provenance flags invalid")
    if meta.get("iv_definition") != "deribit_dvol_index":
        raise SystemExit("FATAL: iv_definition is not deribit_dvol_index")

    payload = load_payload(PKL)
    symbols = list(payload["symbols"])
    if symbols != ["BTC", "ETH"]:
        raise SystemExit(f"FATAL: expected [BTC, ETH], got {symbols}")

    dvol = payload["dvol"].astype(float).sort_index()
    spot = payload["spot_closes"].astype(float).sort_index()
    if not dvol.index.equals(spot.index):
        raise SystemExit("FATAL: DVOL/spot index mismatch")

    for name, df in (("dvol", dvol), ("spot", spot)):
        vals = df.to_numpy(dtype=float)
        if int(np.isnan(vals).sum()) != 0 or not bool(np.isfinite(vals).all()):
            raise SystemExit(f"FATAL: {name} contain NaN/non-finite values")
    if not bool((spot.to_numpy(dtype=float) > 0).all()):
        raise SystemExit("FATAL: non-positive spot price")

    n = len(dvol)
    splits = wf_splits(n, TRAIN, TEST, STEP)
    if len(splits) < 2:
        raise SystemExit(f"FATAL: too few OOS splits: {len(splits)}")

    K_eff = effective_k(K_REQUESTED, len(symbols))
    feats = build_features(dvol, spot)
    spot_ret = feats["spot_ret"].fillna(0.0)
    logret = feats["logret"]

    # BTC-vs-ETH equal-weight B&H (primary benchmark, same WF windows and costs)
    bh_ret = (0.5 * spot_ret["BTC"] + 0.5 * spot_ret["ETH"]).rename("bh")
    bh_mean_per_slice = benchmark_spot_slices(bh_ret, spot_ret, splits, COST_GRID)
    bh_spot_mean = float(np.mean(list(bh_mean_per_slice.values())))

    # Always-long-vol (short VRP) B&H benchmark for the DIAGNOSTIC variance leg.
    # Constant short-vol position w=(-0.5,-0.5); payoff at each split end.
    bh_var_means = []
    for _, tr_e, te_e in splits:
        seg_lr = logret.to_numpy(dtype=float)[tr_e + 1 : te_e + 1]
        iv = dvol.to_numpy(dtype=float)[tr_e] / 100.0
        if seg_lr.shape[0] < 2:
            bh_var_means.append(0.0)
            continue
        rv = np.nanstd(seg_lr, axis=0, ddof=1) * float(np.sqrt(ANNUALIZATION))
        contrib = -0.5 * (rv ** 2 - iv ** 2)
        bh_var_means.append(float(np.nansum(contrib)))
    bh_var_mean = float(np.mean(bh_var_means)) if bh_var_means else 0.0

    limit_runs = int(os.environ.get("C294_LIMIT_RUNS", "0") or 0)
    results = []
    run_count = 0

    for feature in FEATURES:
        for L in LOOKBACKS:
            signal = SIGNAL(feature, feats, L)
            for H in HOLDS:
                run_count += 1
                if limit_runs > 0 and run_count > limit_runs:
                    break
                weights, gate_stats = build_weights(signal, dvol, K_eff, H, r_start=0)
                pos = weights.shift(1).fillna(0.0)

                # PRIMARY: real spot relative-value PnL
                spot_pnl = (pos * spot_ret).sum(axis=1)
                slices, exposure_total, turnover_total, all_sum_pos, all_mean_beats = costed_oos(
                    spot_pnl, pos, splits, COST_GRID, bh_mean_per_slice
                )
                edge = bool(exposure_total > 0 and all_sum_pos and all_mean_beats)

                # DIAGNOSTIC: variance-swap-proxy leg (never executed fills)
                vsp_payoff, vsp_turn = variance_swap_proxy(pos, dvol, logret, H, splits)
                vsp_slices, _, _, _, vsp_beats = costed_oos(
                    vsp_payoff, pos, splits, COST_GRID, {k: bh_var_mean for k in bh_mean_per_slice}
                )
                vsp_mean = float(np.mean([vsp_slices[k]["oos_net_mean"] for k in vsp_slices]))

                results.append({
                    "feature": feature,
                    "lookback": int(L),
                    "hold": int(H),
                    "K_requested": int(K_REQUESTED),
                    "K_effective": int(K_eff),
                    "n_splits": int(len(splits)),
                    "rebalance_bars_total": gate_stats["rebalance_bars_total"],
                    "rebalance_bars_passed": gate_stats["rebalance_bars_passed"],
                    "gate_pass_share": gate_stats["gate_pass_share"],
                    "blocked_rebalance_reasons": gate_stats["blocked_rebalance_reasons"],
                    "oos_exposure_bars_total": int(exposure_total),
                    "turnover_total": float(turnover_total),
                    "spot_pnl_sum": float(spot_pnl.sum()),
                    "cost_slices": slices,
                    "all_cost_slices_oos_net_positive": bool(all_sum_pos),
                    "beats_bh_all_slices": bool(all_mean_beats),
                    "edge_proven": edge,
                    "block_reason": None if edge else "no_costed_oos_edge",
                    "variance_swap_proxy": {
                        "pnl_model": "variance_swap_proxy",
                        "executed_fills": False,
                        "inputs": "real_dvol_iv+real_realized_vol",
                        "oos_net_mean": vsp_mean,
                        "bh_oos_mean": bh_var_mean,
                        "beats_bh_all_slices": bool(vsp_beats),
                        "cost_slices": vsp_slices,
                    },
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

    dataset_block = {
        "cache": str(PKL.relative_to(root)),
        "cache_sha256": pkl_sha,
        "meta": str(META.relative_to(root)),
        "meta_sha256": meta_sha,
        "provenance": str(PROV.relative_to(root)) if PROV.exists() else None,
        "provenance_sha256": prov_sha,
        "bars": int(n),
        "interval": "1h",
        "assets": symbols,
        "n_assets": len(symbols),
        "window": {"start": str(dvol.index.min()), "end": str(dvol.index.max())},
        "iv_definition": "deribit_dvol_index",
        "rv_definition": "annualized_std_of_1h_log_returns_times_sqrt_8760",
        "real_data_only": True,
        "fabricated_data": False,
    }

    sweep = {
        "generated_at_utc": ts,
        "campaign": 294,
        "part": "oos_sweep",
        "analysis": "real_implied_vol_variance_risk_premium_and_btc_eth_relative_value_xsec_stat_arb_costed_oos",
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "real_data_only": True,
        "fabricated_data": False,
        "fail_closed": True,
        "mandate": (
            "C294 — pre-registered costed OOS sweep of a NEW asset class: real implied volatility "
            "(Deribit DVOL) variance-risk-premium / BTC-vs-ETH relative-value stat-arb on 1h bars. "
            "3 features x 3 lookbacks x 3 holds = 27 runs (K=2, effective per-leg K=1 for a 2-asset "
            "cross-section); train=720/test=168/step=168 1h bars; cost grid "
            "[[0,0],[5,5],[10,10],[20,20],[40,40]] bps on BOTH legs; PRIMARY real spot relative-value "
            "PnL (real Binance BTC/ETH 1h returns) + DIAGNOSTIC variance-swap-proxy leg "
            "(executed_fills=false); BTC-vs-ETH B&H and always-long-vol (short VRP) B&H benchmarks; "
            "edge rule identical to C285/C286/C288/C290/C291/C292/C293."
        ),
        "preflight": dataset_block,
        "data_source": dataset_block,
        "universe": {"n_assets": len(symbols), "assets": symbols},
        "config": {
            "walk_forward": {"train": TRAIN, "test": TEST, "step": STEP, "n_splits": len(splits)},
            "cost_grid_bps": COST_GRID,
            "signal_features": list(FEATURES),
            "lookbacks_1h": [int(l) for l in LOOKBACKS],
            "K_requested": K_REQUESTED,
            "K_effective": K_eff,
            "holding_periods_1h": [int(h) for h in HOLDS],
            "total_runs": 3 * 3 * 3,
            "min_periods_rule": "max(3, L // 3)",
            "position_rule": "weights.shift(1).fillna(0.0)",
            "cost_rule": "tc * sum|dw| across both legs (BTC and ETH), charged on BOTH legs",
            "pnl_primary": "w_btc*r_btc - w_eth*r_eth from real Binance BTC/ETH 1h returns",
            "pnl_diagnostic": "variance_swap_proxy: notional*(RV_realized^2 - IV_entry^2)*sign(w); executed_fills=false",
            "score_definition": {
                "iv_rv_spread": "DVOL - trailing annualized realized vol over L 1h bars (per asset)",
                "iv_z": "rolling z(DVOL) over L 1h bars (per asset)",
                "dvol_x_spread": "z(DVOL_BTC - DVOL_ETH) over L 1h bars; BTC=+z, ETH=-z",
            },
            "signal_direction": "higher score = long that asset (pairwise long top-1 / short bottom-1)",
        },
        "benchmarks": {
            "btc_eth_bh": {"mean_per_split_oos_net_by_slice": bh_mean_per_slice, "overall_mean": bh_spot_mean},
            "always_long_vol_short_vrp": {"mean_per_split_oos_net": bh_var_mean},
        },
        "aggregate": {
            "n_total_runs": n_total,
            "n_with_exposure": n_exp,
            "n_edge_proven": int(len(edge_runs)),
            "n_zero_exposure": n_total - n_exp,
            "benchmark_btc_eth_bh_oos_mean": bh_spot_mean,
            "benchmark_always_long_vol_oos_mean": bh_var_mean,
        },
        "runs": results,
    }
    op_sweep = reports / f"campaign294_oos_sweep_{ts}.json"
    op_sweep.write_text(json.dumps(sweep, indent=2, default=jdefault))
    sweep_sha = sha256_file(op_sweep)

    registry = {
        "generated_at_utc": ts,
        "campaign": 294,
        "part": "tradable_edge_registry",
        "real_data_only": True,
        "fabricated_data": False,
        "analysis": "tradable_edge_registry",
        "n_tradable": len(edge_runs),
        "tradable_configs": edge_runs,
        "config": sweep["config"],
        "universe": sweep["universe"],
        "data_source": dataset_block,
        "oos_sweep_artifact": str(op_sweep.relative_to(root)),
        "oos_sweep_sha256": sweep_sha,
        "sha256_from_bytes": sweep_sha,
    }
    op_reg = reports / f"campaign294_tradable_edge_registry_{ts}.json"
    op_reg.write_text(json.dumps(registry, indent=2, default=jdefault))
    reg_sha = sha256_file(op_reg)

    summary = {
        "generated_at_utc": ts,
        "campaign": 294,
        "part": "summary",
        "real_data_only": True,
        "fabricated_data": False,
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "n_total_runs": n_total,
        "n_with_exposure": n_exp,
        "n_edge_proven": int(len(edge_runs)),
        "n_zero_exposure": n_total - n_exp,
        "benchmark_btc_eth_bh_oos_mean": bh_spot_mean,
        "benchmark_always_long_vol_oos_mean": bh_var_mean,
        "universe": sweep["universe"],
        "artifacts": {
            "sweep": str(op_sweep.relative_to(root)),
            "registry": str(op_reg.relative_to(root)),
        },
        "oos_sweep_sha256": sweep_sha,
        "registry_sha256": reg_sha,
    }
    op_sum = reports / f"campaign294_summary_{ts}.json"
    op_sum.write_text(json.dumps(summary, indent=2, default=jdefault))
    sum_sha = sha256_file(op_sum)

    explanation = (
        f"No costed OOS edge proven on the real implied-vol VRP / BTC-vs-ETH relative-value "
        f"family ({n_total} runs, {len(edge_runs)} edge, {n_exp} with exposure)."
        if not edge_runs
        else f"Costed OOS edge proven in {len(edge_runs)} config(s) on real Deribit DVOL / Binance spot data."
    )
    binding_path = None
    binding_sha = None
    if not edge_runs:
        has_exposure = n_exp > 0
        cost0_ok = sum(1 for r in results if r["cost_slices"]["fee0_slip0"]["oos_net_sum"] > 0)
        sum_pos_all = sum(1 for r in results if r["all_cost_slices_oos_net_positive"])
        beats_all = sum(1 for r in results if r["beats_bh_all_slices"])
        if not has_exposure:
            binding = "no_exposure"
        elif cost0_ok == 0:
            binding = "signal_quality"
        elif not sum_pos_all:
            binding = "cost_sensitivity"
        elif not beats_all:
            binding = "benchmark_dominance"
        else:
            binding = "edge_rule_not_met"
        binding_doc = {
            "generated_at_utc": ts,
            "campaign": 294,
            "part": "binding_constraint",
            "real_data_only": True,
            "fabricated_data": False,
            "verdict": verdict,
            "binding_constraint": binding,
            "diagnosis": {
                "n_total_runs": n_total,
                "n_with_exposure": n_exp,
                "n_cost0_slice_net_positive": cost0_ok,
                "n_all_cost_slices_net_positive": sum_pos_all,
                "n_beats_bh_all_slices": beats_all,
                "benchmark_btc_eth_bh_oos_mean": bh_spot_mean,
                "benchmark_always_long_vol_oos_mean": bh_var_mean,
                "mean_gate_pass_share": float(np.mean([r["gate_pass_share"] for r in results])) if results else 0.0,
            },
            "cost_slice_oos_net_sums": {
                f"fee{f}_slip{s}": [r["cost_slices"][f"fee{f}_slip{s}"]["oos_net_sum"] for r in results]
                for f, s in COST_GRID
            },
            "explanation": explanation,
            "universe": sweep["universe"],
            "oos_sweep_artifact": str(op_sweep.relative_to(root)),
            "oos_sweep_sha256": sweep_sha,
            "note": "Diagnosis only; never an edge claim. No threshold weakening.",
        }
        op_b = reports / f"campaign294_binding_constraint_{ts}.json"
        op_b.write_text(json.dumps(binding_doc, indent=2, default=jdefault))
        binding_path = op_b
        binding_sha = sha256_file(op_b)

    verdict_doc = {
        "generated_at_utc": ts,
        "campaign": 294,
        "part": "verdict",
        "real_data_only": True,
        "fabricated_data": False,
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "edge_claim": "EDGE_PROVEN" if edge_runs else "NONE",
        "explanation": explanation,
        "universe": sweep["universe"],
        "aggregate": sweep["aggregate"],
        "oos_sweep_artifact": str(op_sweep.relative_to(root)),
        "oos_sweep_sha256": sweep_sha,
        "registry_artifact": str(op_reg.relative_to(root)),
        "registry_sha256": reg_sha,
        "summary_artifact": str(op_sum.relative_to(root)),
        "summary_sha256": sum_sha,
        "artifacts": {
            "sweep": str(op_sweep.relative_to(root)),
            "registry": str(op_reg.relative_to(root)),
            "summary": str(op_sum.relative_to(root)),
        },
    }
    if binding_path is not None:
        verdict_doc["binding_constraint_artifact"] = str(binding_path.relative_to(root))
        verdict_doc["binding_constraint_sha256"] = binding_sha
        verdict_doc["artifacts"]["binding_constraint"] = str(binding_path.relative_to(root))
    op_v = reports / f"campaign294_verdict_{ts}.json"
    op_v.write_text(json.dumps(verdict_doc, indent=2, default=jdefault))
    verdict_sha = sha256_file(op_v)

    artifacts = {
        "sweep": {"path": str(op_sweep.relative_to(root)), "sha256": sweep_sha},
        "registry": {"path": str(op_reg.relative_to(root)), "sha256": reg_sha},
        "summary": {"path": str(op_sum.relative_to(root)), "sha256": sum_sha},
        "verdict": {"path": str(op_v.relative_to(root)), "sha256": verdict_sha},
    }
    if binding_path is not None:
        artifacts["binding_constraint"] = {"path": str(binding_path.relative_to(root)), "sha256": binding_sha}

    final = {
        "ok": True,
        "campaign": 294,
        "verdict": verdict,
        "edge_proven": bool(edge_runs),
        "n_total_runs": n_total,
        "n_with_exposure": n_exp,
        "n_edge_proven": int(len(edge_runs)),
        "n_assets": len(symbols),
        "n_splits": len(splits),
        "artifacts": artifacts,
        "real_data_only": True,
        "fabricated_data": False,
    }
    print(json.dumps(final, indent=2, default=jdefault))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())