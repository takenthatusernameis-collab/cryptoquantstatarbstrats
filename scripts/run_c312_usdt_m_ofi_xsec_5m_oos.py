#!/usr/bin/env python3
"""C312 — rigorous costed out-of-sample test of the USDT-M LINEAR CROSS-SECTIONAL
order-flow-imbalance (OFI) carry family at NATIVE 5m (504 pre-registered configs).

This is a genuinely new economic family, not a re-skin of any frozen campaign:
- C310 (1h) and C311 (5m) tested COIN-M **inverse-settlement** OFI carry; both
  were COMPLETE FORMAL NEGATIVES dominated by inverse-settlement convexity
  (C310 OFI-carry share 0.088 vs convexity 0.912; C311 0.025 vs 0.975).
- C312 REMOVES the convexity confound by using **linear-settlement** USDT-M
  perps: PnL is exactly ``notional*(exit/entry - 1)*signed_weight``, so any
  surviving edge is attributable to OFI carry, not to ``1/entry - 1/exit``
  convexity.
- C301 (frozen) used 3 spot symbols over 2 months (aggTrades tick-OFI). C312 uses
  10 USDT-M linear perps over 36 months (2023-01..2025-12).

Signals (7, all causal shift(1); all distinct from C309 premium/mark basis):
  ofi_z             = cross-sectional z of rollmean(signed_volume, L)      [OFI]
  ofi_mom           = rollmean(signed_logret, L), signed_logret =
                      sign(trade_sign_sum)*log(vwap/prev_vwap)             [OFI mom]
  buy_ratio         = rollmean(buy_vol/(buy+sell) - 0.5, L)               [buy ratio]
  ofi_per_trade_z   = cross-sectional z of rollmean(signed_volume/trade_count, L)
  ofi_sign_autocorr = rolling lag-1 autocorr of signed_volume, L          [sign persistence]
  trade_intensity_z = cross-sectional z of rollmean(trade_count, L)       [intensity]
  amihud_z          = cross-sectional z of rollmean(|perp_ret|/notional, L) [illiquidity]

All OFI legs are derived from the taker buy/sell split in native USDT-M 5m klines
(signed_volume = 2*taker_buy_volume - volume); the ~52 GB aggTrades archive is NOT
streamed (see scripts/ingest_c312_usdt_m_ofi_5m.py).

Grid: 7 signals x 4 lookbacks{288,1008,2016,4032} 5m bars x K{2,3,5} x
holds{1,6,24} 5m bars x gates{off,on} = 504 runs (N_TRIALS = 504; all reported,
none dropped).
WF: train 720, test 168, step 168 over the ~315k-bar 5m common grid
(2023-01-01 -> 2025-12-31).
LINEAR PnL: pnl = notional*(exit/entry - 1)*signed_weight, computed bar-by-bar as
sum(pos * (close/close_prev - 1)) with positions decided at segment start and
applied from the next bar. Costs on ALL legs at [[0,0],[5,5],[10,10],[20,20],
[40,40]] bps plus the USDT-M realism overlay (taker 5bps + slippage 1bps = 6bps
one-way on turnover; maker 2bps reported separately). The USDT-M funding leg is
unreachable (fapi 451, not in monthly archives) and is excluded from total return.

Validates on ALL of:
  (a) multiple-testing correction across the 504 pre-registered configs — Holm
      AND Benjamini-Hochberg at alpha=0.05, reporting how many survive BOTH;
  (b) DSR / minimum detectable effect given the WF splits;
  (c) sub-period stability (first vs second half and per-year 2023/2024/2025);
  (d) per-asset contribution decomposition over the 10 USDT-M linear perps;
  (e) OFI-carry attribution — because settlement is linear there is NO convexity
      term, so any edge is attributable to OFI carry by construction;
  (f) execution-cost-realism overlay (taker 5bps / maker 2bps + 1bps slippage on
      turnover).

This is a model PnL backtest (executed_fills: false) on real data only. It never
fetches, imputes, resamples, or fabricates data.

Required artifacts (exact names, timestamped, SHA256-from-bytes):
- reports/campaign312_oos_sweep_<ts>.json
- reports/campaign312_tradable_edge_registry_<ts>.json
- reports/campaign312_summary_<ts>.json
- reports/campaign312_verdict_<ts>.json
- reports/campaign312_binding_constraint_<ts>.json
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
reports = ROOT / "reports"
reports.mkdir(exist_ok=True)
cache_dir = ROOT / "data" / "cache"
ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

CACHE_DIR = cache_dir / "campaign312_usdt_m_ofi_5m"
CACHE_META = cache_dir / "campaign312_usdt_m_ofi_5m.meta.json"
CACHE_PROV = cache_dir / "campaign312_usdt_m_ofi_5m.provenance.json"

TRAIN, TEST, STEP = 720, 168, 168
COST_GRID = ((0, 0), (5, 5), (10, 10), (20, 20), (40, 40))
ALPHA = 0.05
N_TRIALS = 504  # pre-registered universe: 7 x 4 x 3 x 3 x 2

SIGNALS = (
    "ofi_z", "ofi_mom", "buy_ratio", "ofi_per_trade_z",
    "ofi_sign_autocorr", "trade_intensity_z", "amihud_z",
)
LOOKBACKS = (288, 1008, 2016, 4032)  # 5m bars
K_VALUES = (2, 3, 5)
HOLDS = (1, 6, 24)  # 5m bars
GATES = ("off", "on")

# Realistic USDT-M execution overlay: taker 5bps + slippage 1bps = 6bps one-way on
# turnover. Maker 2bps reported separately (passive alt).
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
        if idx is None:
            idx = pa.get("index_ms")
    else:
        idx = getattr(pa, "index", None)
        if idx is None:
            idx = getattr(pa, "index_ms", None)
    if isinstance(idx, pd.DatetimeIndex):
        return idx if idx.tz is not None else idx.tz_localize("UTC")
    arr = np.asarray(idx)
    if np.issubdtype(arr.dtype, np.datetime64):
        return pd.DatetimeIndex(arr).tz_localize("UTC")
    return pd.DatetimeIndex(pd.to_datetime(arr, unit="ms", utc=True))


def rollmean_df(df: pd.DataFrame, L: int) -> pd.DataFrame:
    mp = min_periods_for(L)
    return df.rolling(L, min_periods=mp).mean()


def rollautocorr1_df(df: pd.DataFrame, L: int) -> pd.DataFrame:
    mp = min_periods_for(L)
    x = df.to_numpy(dtype=float)  # (n_bars, n_assets)
    n_bars, n_assets = x.shape
    out = np.full((n_bars, n_assets), np.nan, dtype=float)
    for j in range(n_assets):
        s = pd.Series(x[:, j])
        out[:, j] = s.rolling(L, min_periods=mp).apply(
            lambda w: (np.corrcoef(w[:-1], w[1:])[0, 1] if np.std(w) > 0 else np.nan),
            raw=True,
        )
    return pd.DataFrame(out, index=df.index, columns=df.columns)


def lin_ret_of(entry: np.ndarray, exit_: np.ndarray) -> np.ndarray:
    """Exact linear-settlement per-unit-notional return: (exit - entry)/entry."""
    with np.errstate(divide="ignore", invalid="ignore"):
        r = (exit_ - entry) / entry
    return np.where(np.isfinite(r), r, np.nan)


def xsec_positions(score: np.ndarray, K: int, H: int, gate_mask: np.ndarray) -> np.ndarray:
    """Cross-sectional long top-K / short bottom-K positions.

    score: (n_assets, n_bars), causal (shift(1) already applied).
    Dollar-neutral, gross 1.0 (+0.5/K long, -0.5/K short). High score = rich
    = short (score = -base), mirroring the C308/C309/C311 convention.
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
    factors = (m - np.arange(m)).astype(float)
    adj = ranked * factors
    adj = np.maximum.accumulate(adj)
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
    adj = np.minimum.accumulate(adj[::-1])[::-1]
    adj = np.minimum(adj, 1.0)
    out = np.empty(m, dtype=float)
    out[order] = adj
    reject = out <= ALPHA
    return out, reject


def one_sided_p(diffs: np.ndarray) -> float:
    d = np.asarray(diffs, dtype=float)
    d = d[np.isfinite(d)]
    if len(d) < 2:
        return 1.0
    if float(np.std(d)) <= 0:
        return 1.0 if float(np.mean(d)) <= 0 else 0.0
    return float(stats.ttest_1samp(d, 0.0, alternative="greater").pvalue)


def verify_cache() -> tuple:
    if not CACHE_DIR.exists():
        raise SystemExit(f"FATAL: C312 shard dir missing: {CACHE_DIR}")
    if not CACHE_META.exists():
        raise SystemExit(f"FATAL: C312 meta missing: {CACHE_META}")
    meta_sha = sha256_file(CACHE_META)
    prov_sha = sha256_file(CACHE_PROV) if CACHE_PROV.exists() else None
    meta = json.loads(CACHE_META.read_text())
    if meta.get("real_data_only") is not True or meta.get("fabricated_data") is not False:
        raise SystemExit("FATAL: dataset provenance flags are not real_data_only/fabricated_data")
    if meta.get("executed_fills") is not False:
        raise SystemExit("FATAL: cache executed_fills must be false (model PnL only)")
    if meta.get("interval") != "5m":
        raise SystemExit(f"FATAL: C312 cache interval must be 5m, got {meta.get('interval')}")

    shard_sha_meta = meta.get("shard_sha256") or {}
    shard_bytes_meta = meta.get("shard_bytes") or {}
    per_asset = {}
    for s, expected in shard_sha_meta.items():
        sp = CACHE_DIR / f"{s}.npz"
        if not sp.exists():
            raise SystemExit(f"FATAL: shard missing: {sp}")
        actual = sha256_file(sp)
        if actual != expected:
            raise SystemExit(f"FATAL: shard sha256 mismatch for {s}")
        nbytes = sp.stat().st_size
        if nbytes != int(shard_bytes_meta.get(s, -1)):
            raise SystemExit(f"FATAL: shard byte size mismatch for {s}")
        if nbytes >= 100_000_000:
            raise SystemExit(f"FATAL: shard {s} exceeds 100 MB push limit")
        with np.load(sp) as z:
            per_asset[s] = {k: z[k] for k in z.files}

    manifest = {s: shard_sha_meta[s] for s in sorted(shard_sha_meta)}
    manifest_sha = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()
    if manifest_sha != meta.get("manifest_sha256"):
        raise SystemExit("FATAL: shard manifest sha256 mismatch")

    payload = {
        "symbols": list(meta.get("symbols") or []),
        "n_grid_bars": int(meta.get("n_grid_bars") or 0),
        "per_asset": per_asset,
    }
    return payload, meta, manifest_sha, meta_sha, prov_sha


def build_series(payload: dict):
    symbols = list(payload.get("symbols") or [])
    n_assets = len(symbols)
    per_asset = payload.get("per_asset") or {}
    index = _as_index(per_asset[symbols[0]])
    n_b = int(payload.get("n_grid_bars") or len(index))
    if n_b == 0:
        raise SystemExit("FATAL: C312 common grid is empty")
    splits = wf_splits(n_b, TRAIN, TEST, STEP)
    if len(splits) == 0:
        raise SystemExit(f"FATAL: no OOS splits, n={n_b}")

    def mat(key):
        out = np.zeros((n_assets, n_b), dtype=float)
        for i, s in enumerate(symbols):
            out[i] = np.asarray(per_asset[s][key], dtype=float)
        return out

    # Shards store total_volume and signed_volume; derive buy/sell legs.
    total_volume = mat("total_volume")
    signed_volume = mat("signed_volume")
    buy_volume = 0.5 * (total_volume + signed_volume)
    sell_volume = 0.5 * (total_volume - signed_volume)
    trade_count = mat("trade_count")
    trade_sign_sum = mat("trade_sign_sum")
    notional = mat("notional")
    vwap = mat("vwap")
    perp_close = mat("perp_close")

    if not bool(np.isfinite(perp_close).all()) or not bool((perp_close > 0).all()):
        raise SystemExit("FATAL: non-finite or non-positive perp price")

    # Derived per-bar quantities (NaN on gap bars, never imputed).
    tot_vol = buy_volume + sell_volume
    buy_ratio = np.where(tot_vol > 0, buy_volume / tot_vol - 0.5, np.nan)
    ofi_per_trade = np.where(trade_count > 0, signed_volume / trade_count, np.nan)
    perp_ret = np.zeros_like(perp_close)
    perp_ret[:, 1:] = np.diff(np.log(perp_close), axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        amihud = np.where(notional > 0, np.abs(perp_ret) / notional, np.nan)
    vlog = np.zeros_like(vwap)
    with np.errstate(divide="ignore", invalid="ignore"):
        vlog[:, 1:] = np.log(vwap[:, 1:] / vwap[:, :-1])
    signed_logret = np.sign(np.nan_to_num(trade_sign_sum)) * vlog

    # LINEAR-settlement per-bar return and equal-weight buy&hold benchmark.
    lin_ret = np.diff(perp_close, axis=1) / perp_close[:, :-1]
    lin_ret = np.concatenate([np.zeros((n_assets, 1)), lin_ret], axis=1)
    lin_ret = np.where(np.isfinite(lin_ret), lin_ret, 0.0)
    bench_ret = np.nanmean(lin_ret, axis=0)
    bench_ret = np.where(np.isnan(bench_ret), 0.0, bench_ret)

    # Cross-sectional dispersion gate on the OFI level (signed_volume).
    ofi_df = pd.DataFrame(signed_volume.T, index=index)
    disp = ofi_df.std(axis=1)
    disp = np.where(np.isfinite(disp), disp, np.nan)
    disp_series = pd.Series(disp, index=index)
    disp_med = disp_series.expanding().median().to_numpy(dtype=float)
    gate_on = (disp > disp_med)
    gate_on = np.where(np.isnan(gate_on), False, gate_on)
    gate_on = np.roll(gate_on, 1)
    gate_on[0] = False

    return {
        "symbols": symbols, "n_assets": n_assets, "index": index, "n_bars": n_b,
        "splits": splits, "perp_close": perp_close, "lin_ret": lin_ret,
        "bench_ret": bench_ret, "gate_on": gate_on,
        "buy_volume": buy_volume, "sell_volume": sell_volume, "signed_volume": signed_volume,
        "trade_count": trade_count, "notional": notional, "vwap": vwap,
        "buy_ratio": buy_ratio, "ofi_per_trade": ofi_per_trade,
        "signed_logret": signed_logret, "amihud": amihud,
        "ofi_df": ofi_df,
    }


def _xsec_z(df: pd.DataFrame) -> pd.DataFrame:
    m = df.mean(axis=1)
    s = df.std(axis=1).replace(0.0, np.nan)
    return df.sub(m, axis=0).div(s, axis=0).where(lambda x: np.isfinite(x))


def base_for(bs: dict, signal: str, L: int) -> pd.DataFrame:
    if signal == "ofi_z":
        return _xsec_z(rollmean_df(bs["ofi_df"], L))
    if signal == "ofi_mom":
        return rollmean_df(pd.DataFrame(bs["signed_logret"].T, index=bs["index"],
                                        columns=bs["symbols"]), L)
    if signal == "buy_ratio":
        return rollmean_df(pd.DataFrame(bs["buy_ratio"].T, index=bs["index"],
                                       columns=bs["symbols"]), L)
    if signal == "ofi_per_trade_z":
        df = pd.DataFrame(bs["ofi_per_trade"].T, index=bs["index"], columns=bs["symbols"])
        return _xsec_z(rollmean_df(df, L))
    if signal == "ofi_sign_autocorr":
        return rollautocorr1_df(bs["ofi_df"], L)
    if signal == "trade_intensity_z":
        df = pd.DataFrame(bs["trade_count"].T, index=bs["index"], columns=bs["symbols"])
        return _xsec_z(rollmean_df(df, L))
    if signal == "amihud_z":
        df = pd.DataFrame(bs["amihud"].T, index=bs["index"], columns=bs["symbols"])
        return _xsec_z(rollmean_df(df, L))
    raise ValueError(f"unknown signal {signal}")


def sweep(bs: dict, results: list):
    n_b = bs["n_bars"]
    splits = bs["splits"]
    lin_ret = bs["lin_ret"]
    bench_ret = bs["bench_ret"]
    gate_on = bs["gate_on"]

    for signal in SIGNALS:
        for L in LOOKBACKS:
            base = base_for(bs, signal, L).where(lambda x: np.isfinite(x))
            score = ((-base).shift(1).to_numpy(dtype=float)).T  # (n_assets, n_bars)
            for K in K_VALUES:
                for H in HOLDS:
                    for gate_name in GATES:
                        gate_mask = gate_on if gate_name == "on" else np.ones(n_b, dtype=bool)
                        pos = xsec_positions(score, K, H, gate_mask)

                        port_ret = (pos * lin_ret).sum(axis=0)
                        turnover = np.abs(np.diff(pos, axis=1, prepend=pos[:, :1])).sum(axis=0)

                        segs = []
                        exposure_total = 0
                        turnover_total = 0.0
                        for tr_s, tr_e, te_e in splits:
                            spr = port_ret[tr_e:te_e]
                            stu = turnover[tr_e:te_e]
                            spos = pos[:, tr_e:te_e]
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
                                "oos_net_sum": net_sum_b, "oos_net_mean": slice_mean_b,
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
                        edge_b = bool(exposure_total > 0 and all_sum_pos and all_beat_bh and all_beat_flat)

                        diffs = np.array([sg["net_gross"] / max(sg["len"], 1) - bh
                                          for sg, bh in zip(segs, bh_per_split)], dtype=float)
                        p_val = one_sided_p(diffs)
                        per_split_mean_bps = float(np.mean([sg["net_gross"] / max(sg["len"], 1) for sg in segs])) * 10000.0

                        seg_means = np.array([sg["net_gross"] / max(sg["len"], 1) for sg in segs], dtype=float)
                        seg_means = seg_means[np.isfinite(seg_means)]
                        sr_obs = float(np.mean(seg_means) / np.std(seg_means)) if len(seg_means) > 1 and np.std(seg_means) > 0 else 0.0
                        p_deflated = 1.0 - (1.0 - p_val) ** N_TRIALS
                        dsr = 1.0 - p_deflated
                        n_spl = len(splits)
                        if n_spl > 1 and np.std(seg_means) > 0:
                            s = float(np.std(seg_means, ddof=1))
                            t_a = float(stats.t.ppf(1.0 - ALPHA / 2.0, df=n_spl - 1))
                            t_b = float(stats.t.ppf(0.80, df=n_spl - 1))
                            mde_bps = (t_a + t_b) * s / math.sqrt(n_spl) * 10000.0
                        else:
                            mde_bps = float("nan")

                        results.append({
                            "signal": signal, "lookback": int(L), "K": int(K),
                            "hold": int(H), "gate": gate_name,
                            "n_splits": int(len(segs)),
                            "oos_exposure_bars_total": int(exposure_total),
                            "turnover_total": float(turnover_total),
                            "edge_proven": edge_b,
                            "block_reason": None if edge_b else "no_costed_oos_edge",
                            "cost_slices": slices,
                            "all_cost_slices_oos_net_positive": bool(all_sum_pos),
                            "beats_bh_all_slices": bool(all_beat_bh),
                            "beats_flat": bool(all_beat_flat),
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


def attribution_for_config(bs: dict, signal: str, L: int, K: int, H: int, gate_name: str):
    """Decompose OOS PnL into OFI carry (linear) and per-asset contributions.

    Because USDT-M settles LINEARLY there is NO convexity term: the exact PnL is
    the linear PnL, so the OFI-carry share is 1.0 by construction and any edge is
    attributable to OFI carry (this is the whole point of C312).
    """
    symbols = bs["symbols"]
    n_b = bs["n_bars"]
    lin_ret = bs["lin_ret"]
    gate_on = bs["gate_on"]
    splits = bs["splits"]

    oos_mask = np.zeros(n_b, dtype=bool)
    for _, tr_e, te_e in splits:
        oos_mask[tr_e:te_e] = True

    base = base_for(bs, signal, L).where(lambda x: np.isfinite(x))
    score = ((-base).shift(1).to_numpy(dtype=float)).T
    gate_mask = gate_on if gate_name == "on" else np.ones(n_b, dtype=bool)
    pos = xsec_positions(score, K, H, gate_mask)
    pos_prev = np.zeros_like(pos)
    pos_prev[:, 1:] = pos[:, :-1]

    lin_contrib = float(np.nansum(pos_prev * lin_ret * oos_mask[None, :]))
    total_modelled = lin_contrib
    conv_contrib = 0.0

    per_asset = {}
    for i, s in enumerate(symbols):
        lin = float(np.nansum(pos_prev[i] * lin_ret[i] * oos_mask))
        per_asset[s] = {"linear_contrib": lin, "conv_contrib": 0.0, "total_contrib": lin}

    return {
        "linear_contrib": lin_contrib,
        "conv_contrib": conv_contrib,
        "total_modelled": total_modelled,
        "ofi_carry_share": (lin_contrib / total_modelled) if total_modelled != 0 else 0.0,
        "conv_share": 0.0,
        "lin_share": (lin_contrib / total_modelled) if total_modelled != 0 else 0.0,
        "per_asset": per_asset,
        "oos_bars": int(oos_mask.sum()),
    }


def stability_for_config(bs: dict, signal: str, L: int, K: int, H: int, gate_name: str, cost_bps: float = 0.0):
    index = bs["index"]
    n_b = bs["n_bars"]
    splits = bs["splits"]
    lin_ret = bs["lin_ret"]
    bench_ret = bs["bench_ret"]
    gate_on = bs["gate_on"]

    base = base_for(bs, signal, L).where(lambda x: np.isfinite(x))
    score = ((-base).shift(1).to_numpy(dtype=float)).T
    gate_mask = gate_on if gate_name == "on" else np.ones(n_b, dtype=bool)
    pos = xsec_positions(score, K, H, gate_mask)
    port_ret = (pos * lin_ret).sum(axis=0)

    tc = cost_bps / 10000.0
    split_data = []
    for tr_s, tr_e, te_e in splits:
        spr = port_ret[tr_e:te_e]
        spos = pos[:, tr_e:te_e]
        pre = np.zeros_like(pos[:, :1]); pre[:, 0] = pos[:, tr_e]
        window = pos[:, tr_e:te_e]
        turnover = float(np.abs(np.diff(window, axis=1, prepend=pre)).sum())
        split_data.append({
            "net_gross": float(spr.sum()), "len": int(len(spr)), "turnover": turnover,
            "bh_mean": float(bench_ret[tr_e:te_e].mean()), "mid": (tr_e + te_e) // 2,
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


def cost_realism_for_config(bs: dict, signal: str, L: int, K: int, H: int, gate_name: str):
    index = bs["index"]
    n_b = bs["n_bars"]
    splits = bs["splits"]
    lin_ret = bs["lin_ret"]
    bench_ret = bs["bench_ret"]
    gate_on = bs["gate_on"]

    base = base_for(bs, signal, L).where(lambda x: np.isfinite(x))
    score = ((-base).shift(1).to_numpy(dtype=float)).T
    gate_mask = gate_on if gate_name == "on" else np.ones(n_b, dtype=bool)
    pos = xsec_positions(score, K, H, gate_mask)
    port_ret = (pos * lin_ret).sum(axis=0)

    split_data = []
    for tr_s, tr_e, te_e in splits:
        spr = port_ret[tr_e:te_e]
        spos = pos[:, tr_e:te_e]
        pre = np.zeros_like(pos[:, :1]); pre[:, 0] = pos[:, tr_e]
        window = pos[:, tr_e:te_e]
        turnover = float(np.abs(np.diff(window, axis=1, prepend=pre)).sum())
        split_data.append({"net_gross": float(spr.sum()), "len": int(len(spr)),
                           "turnover": turnover, "bh_mean": float(bench_ret[tr_e:te_e].mean()),
                           "exposure": int((spos != 0).sum())})

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


def main() -> int:
    payload, meta, cache_sha, meta_sha, prov_sha = verify_cache()
    bs = build_series(payload)
    symbols = bs["symbols"]
    n_bars_b = bs["n_bars"]
    splits_b = bs["splits"]
    n_splits_b = len(splits_b)

    results = []
    sweep(bs, results)

    n_total = len(results)
    edge_runs = [r for r in results if r["edge_proven"]]
    n_edge = len(edge_runs)
    n_exp = sum(1 for r in results if r["oos_exposure_bars_total"] > 0)
    edge_indices = [i for i, r in enumerate(results) if r["edge_proven"]]

    # (a) multiple-testing correction (Holm + BH) over all 504 configs.
    pvals = np.array([r["p_value"] for r in results], dtype=float)
    p_holm, rej_holm = holm_adjust(pvals)
    p_bh, rej_bh = bh_adjust(pvals)
    for r, ph, pb, rh, rb in zip(results, p_holm, p_bh, rej_holm, rej_bh):
        r["p_holm"] = float(ph)
        r["p_bh"] = float(pb)
        r["holm_reject"] = bool(rh)
        r["bh_reject"] = bool(rb)

    n_survive_holm = int(sum(1 for i in edge_indices if rej_holm[i]))
    n_survive_bh = int(sum(1 for i in edge_indices if rej_bh[i]))
    n_survive_both = int(sum(1 for i in edge_indices if rej_holm[i] and rej_bh[i]))

    # (b) DSR / MDE given the splits.
    dsr_values = [float(r["dsr"]) for i in edge_indices]
    n_dsr_ge_95 = int(sum(1 for v in dsr_values if v >= 0.95))
    n_dsr_ge_90 = int(sum(1 for v in dsr_values if v >= 0.90))
    mde_values = [float(r["mde_bps"]) for i in edge_indices if np.isfinite(r["mde_bps"])]
    obs_mean_bps_values = [float(r["per_split_mean_bps"]) for i in edge_indices]
    mde_bps = float(np.mean(mde_values)) if mde_values else float("nan")
    obs_mean_bps = float(np.mean(obs_mean_bps_values)) if obs_mean_bps_values else 0.0

    # (c) sub-period stability.
    for i in edge_indices:
        r = results[i]
        r["stability"] = stability_for_config(bs, r["signal"], r["lookback"], r["K"], r["hold"], r["gate"])
    stable_first = int(sum(1 for i in edge_indices if results[i]["stability"]["first_half"]["stable"]))
    stable_second = int(sum(1 for i in edge_indices if results[i]["stability"]["second_half"]["stable"]))
    stable_per_year = {}
    for i in edge_indices:
        for y, v in results[i]["stability"]["per_year"].items():
            stable_per_year[y] = stable_per_year.get(y, 0) + (1 if v["stable"] else 0)

    # (d) per-asset + (e) linear OFI-carry attribution.
    asset_agg = {s: {"linear_contrib": 0.0, "conv_contrib": 0.0,
                     "total_contrib": 0.0, "n_configs_positive": 0} for s in symbols}
    for i in edge_indices:
        r = results[i]
        attr = attribution_for_config(bs, r["signal"], r["lookback"], r["K"], r["hold"], r["gate"])
        r["attribution"] = attr
        for s in symbols:
            c = attr["per_asset"][s]
            asset_agg[s]["linear_contrib"] += c["linear_contrib"]
            asset_agg[s]["conv_contrib"] += c["conv_contrib"]
            asset_agg[s]["total_contrib"] += c["total_contrib"]
            if c["total_contrib"] > 0:
                asset_agg[s]["n_configs_positive"] += 1
    grand_total = sum(asset_agg[s]["total_contrib"] for s in symbols)
    per_asset_report = {}
    for s in symbols:
        tc = asset_agg[s]["total_contrib"]
        per_asset_report[s] = {
            "linear_contrib": float(asset_agg[s]["linear_contrib"]),
            "conv_contrib": float(asset_agg[s]["conv_contrib"]),
            "total_contrib": float(tc),
            "share_of_edge": float(tc / grand_total) if grand_total != 0 else 0.0,
            "n_configs_positive": int(asset_agg[s]["n_configs_positive"]),
            "n_configs": int(len(edge_indices)),
        }
    edge_res = [results[i] for i in edge_indices]
    aggregate_attribution = {
        "linear_contrib_total": float(sum(r.get("attribution", {}).get("linear_contrib", 0.0) for r in edge_res)),
        "conv_contrib_total": float(sum(r.get("attribution", {}).get("conv_contrib", 0.0) for r in edge_res)),
        "per_asset": per_asset_report,
        "grand_total": float(grand_total),
    }

    agg_lin = aggregate_attribution["linear_contrib_total"]
    agg_conv = aggregate_attribution["conv_contrib_total"]
    agg_total = agg_lin  # linear settlement: total == linear
    agg_ofi_carry_share = (agg_lin / agg_total) if agg_total != 0 else 0.0
    agg_conv_share = 0.0
    # Linear settlement: there is no convexity term, so any modelled edge is
    # attributable to OFI carry by construction.
    edge_explained_by_ofi_carry = bool(agg_total != 0.0 and agg_ofi_carry_share >= agg_conv_share)

    # (f) execution-cost-realism overlay.
    cost_realism_results = {}
    n_survive_realistic = 0
    for i in edge_indices:
        r = results[i]
        cr = cost_realism_for_config(bs, r["signal"], r["lookback"], r["K"], r["hold"], r["gate"])
        r["cost_realism"] = cr
        cost_realism_results[i] = cr
        if cr["realistic_taker_plus_slippage"]["survive"]:
            n_survive_realistic += 1

    binding = None
    if n_survive_both == 0:
        verdict = "RETRACTED"
        binding = "multiple_testing"
    elif n_survive_realistic < n_edge:
        verdict = "RETRACTED"
        binding = "execution_cost"
    else:
        verdict = "EDGE_PROVEN"
        binding = None

    edge_proven = bool(edge_runs and verdict == "EDGE_PROVEN")

    dataset_block = {
        "cache": str(CACHE_DIR.relative_to(ROOT)),
        "cache_sha256": cache_sha,
        "cache_meta": str(CACHE_META.relative_to(ROOT)),
        "cache_meta_sha256": meta_sha,
        "cache_provenance": str(CACHE_PROV.relative_to(ROOT)) if CACHE_PROV.exists() else None,
        "cache_provenance_sha256": prov_sha,
        "storage": "per_asset_float32_npz_shards",
        "total_shard_bytes": int(meta.get("total_shard_bytes") or 0),
        "max_shard_bytes": int(meta.get("max_shard_bytes") or 0),
        "under_push_limit": bool(meta.get("under_push_limit")),
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "source_host": meta.get("source_host"),
    }

    sweep_obj = {
        "generated_at_utc": ts,
        "campaign": 312,
        "part": "oos_sweep",
        "analysis": "c312_usdt_m_linear_cross_sectional_ofi_carry_oos_5m",
        "verdict": verdict,
        "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "fail_closed": True,
        "mandate": (
            "C312 — test the USDT-M LINEAR CROSS-SECTIONAL order-flow-imbalance "
            "(OFI) carry family at NATIVE 5m (504 pre-registered configs) on real "
            "USDT-M 5m klines (taker buy/sell split; the ~52 GB aggTrades archive is "
            "not streamed) with linear settlement PnL notional*(exit/entry-1)*weight. "
            "This removes the inverse-settlement convexity confound that dominated "
            "C310 (0.912) and C311 (0.975), so any edge is attributable to OFI carry. "
            "Multiple-testing (Holm+BH over 504 configs), DSR/MDE given the WF splits, "
            "sub-period + per-year (2023/2024/2025) stability, per-asset attribution "
            "over 10 perps, and USDT-M execution-cost-realism overlay (taker 5bps / "
            "maker 2bps + 1bps slippage on turnover)."
        ),
        "preflight": dataset_block,
        "data_source": dataset_block,
        "universe": {
            "symbols": symbols, "n_assets": len(symbols),
            "common_grid_bars": int(n_bars_b),
            "common_grid_start_utc": str(bs["index"][0]),
            "common_grid_end_utc": str(bs["index"][-1]),
            "n_splits": int(n_splits_b),
        },
        "config": {
            "walk_forward": {"train": TRAIN, "test": TEST, "step": STEP},
            "cost_grid_bps": [list(c) for c in COST_GRID],
            "alpha": ALPHA, "n_trials": N_TRIALS,
            "signals": list(SIGNALS),
            "lookbacks_5m": [int(l) for l in LOOKBACKS],
            "cross_sectional_K": [int(k) for k in K_VALUES],
            "holding_periods_5m": [int(h) for h in HOLDS],
            "dispersion_gates": list(GATES),
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
            "attribution": {"aggregate_ofi_carry_share": float(agg_ofi_carry_share),
                            "aggregate_conv_share": float(agg_conv_share),
                            "edge_explained_by_ofi_carry": bool(edge_explained_by_ofi_carry)},
            "cost_realism": {"realistic_cost_bps": REALISTIC_COST_BPS,
                             "taker_cost_bps": TAKER_COST_BPS, "maker_cost_bps": MAKER_COST_BPS,
                             "slippage_bps": SLIPPAGE_BPS,
                             "n_survive_realistic": int(n_survive_realistic), "n_edge": n_edge},
        },
        "methodology": {
            "multiple_testing": "one-sided paired t-test of per-split OOS net vs equal-weight B&H "
                                "(0 bps); Holm step-down and Benjamini-Hochberg step-up over 504 "
                                "pre-registered configs at alpha=0.05.",
            "dsr": "Šidák-deflated significance = 1 - (1 - p_single)^504 over 504 trials.",
            "mde": "two-sided alpha=0.05, power=0.80: (t_{0.975}+t_{0.80})*s/sqrt(n_splits).",
            "stability": "split assigned to sub-period by test-window midpoint bar; stable iff "
                         "exposure>0, net_sum>0, net_mean>B&H and net_mean>0 within the sub-period.",
            "attribution": "per-asset OOS contribution = sum(pos*lin_ret) [linear-settlement PnL]; "
                           "because settlement is linear there is NO convexity term, so the "
                           "OFI-carry share is 1.0 by construction.",
            "linear_settlement": "exact linear-settlement return (exit-entry)/entry; no convexity "
                                 "term (contrast C310/C311 inverse 1/entry-1/exit convexity).",
            "cost_realism": "one-way USDT-M cost on turnover: realistic = taker 5bps + slippage 1bps = 6bps; "
                            "also reported at taker 5bps and maker 2bps. USDT-M funding excluded "
                            "(control leg only, unreachable in this environment).",
            "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        },
        "results": results,
        "summary": {
            "n_total_runs": int(n_total),
            "n_with_exposure": int(n_exp),
            "n_zero_exposure": int(n_total - n_exp),
            "n_edge_proven_deterministic": int(n_edge),
            "n_survive_holm": int(n_survive_holm),
            "n_survive_bh": int(n_survive_bh),
            "n_survive_both": int(n_survive_both),
            "n_survive_cost_realism": int(n_survive_realistic),
            "verdict": verdict, "edge_proven": edge_proven, "binding_constraint": binding,
        },
    }

    # Keep the on-disk sweep bounded (GitHub hard-rejects any single blob >= 100 MB
    # on push). The per-split OOS net-mean series are already summarized by each
    # slice's ``oos_net_mean`` / the top-level ``per_split_mean_bps`` and are not
    # needed for the verdict, registry, or summary; drop them from the serialized
    # sweep so the artifact stays small. Keep the full blob on disk as *.full.json.
    SLIM_DROP = ("oos_net_mean_per_split", "bh_oos_net_mean_per_split")
    slim_results = []
    for r in results:
        rc = dict(r)
        rc["cost_slices"] = {
            ck: {k: v for k, v in cv.items() if k not in SLIM_DROP}
            for ck, cv in r["cost_slices"].items()
        }
        slim_results.append(rc)
    sweep_obj["results"] = slim_results
    sweep_obj["slimmed"] = {
        "dropped_fields": list(SLIM_DROP),
        "reason": "per-split OOS net-mean series summarized by oos_net_mean; "
                  "keeps the sweep artifact under the 100 MB GitHub push limit.",
    }

    op = reports / f"campaign312_oos_sweep_{ts}.json"
    op.write_text(json.dumps(sweep_obj, indent=2, default=jdefault) + "\n")
    sweep_sha = sha256_file(op)
    # keep the full (unslimmed) sweep on disk for audit, gitignored
    full = reports / f"campaign312_oos_sweep_{ts}.full.json"
    try:
        full.write_text(json.dumps({**sweep_obj, "results": results}, indent=2, default=jdefault) + "\n")
    except Exception:  # noqa: BLE001
        pass

    surviving = [results[i] for i in edge_indices
                 if rej_holm[i] and rej_bh[i]
                 and cost_realism_results[i]["realistic_taker_plus_slippage"]["survive"]
                 and edge_explained_by_ofi_carry]
    registry = {
        "generated_at_utc": ts, "campaign": 312, "part": "registry",
        "analysis": "tradable_edge_registry",
        "n_tradable": len(surviving),
        "n_edge_proven_deterministic": int(n_edge),
        "n_survive_holm": int(n_survive_holm), "n_survive_bh": int(n_survive_bh),
        "n_survive_both": int(n_survive_both), "n_survive_cost_realism": int(n_survive_realistic),
        "edge_explained_by_ofi_carry": bool(edge_explained_by_ofi_carry),
        "tradable_configs": surviving,
        "oos_sweep_artifact": str(op.relative_to(ROOT)), "oos_sweep_sha256": sweep_sha,
        "verdict": verdict,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
    }
    op_reg = reports / f"campaign312_tradable_edge_registry_{ts}.json"
    op_reg.write_text(json.dumps(registry, indent=2, default=jdefault) + "\n")
    reg_sha = sha256_file(op_reg)

    summary = {
        "generated_at_utc": ts, "campaign": 312, "part": "summary",
        "analysis": "validation_summary", "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "universe": sweep_obj["universe"], "config": sweep_obj["config"],
        "gates": sweep_obj["gates"], "aggregate_attribution": aggregate_attribution,
        "artifacts": {
            "oos_sweep": {"path": str(op.relative_to(ROOT)), "sha256": sweep_sha},
            "registry": {"path": str(op_reg.relative_to(ROOT)), "sha256": reg_sha},
        },
        "summary": sweep_obj["summary"], "binding_constraint": binding,
    }
    op_sum = reports / f"campaign312_summary_{ts}.json"
    op_sum.write_text(json.dumps(summary, indent=2, default=jdefault) + "\n")
    sum_sha = sha256_file(op_sum)

    finding = (
        f"C312 USDT-M linear cross-sectional OFI carry edge RETRACTED "
        f"({n_edge} deterministic edge configs, {n_survive_both} survive Holm+BH over 504); "
        f"binding constraint: {binding}."
        if binding is not None
        else f"C312 USDT-M linear cross-sectional OFI carry edge validated: "
        f"{n_survive_both} of {n_edge} deterministic edge configs survive Holm+BH over 504; edge_proven:{edge_proven}."
    )
    verdict_obj = {
        "generated_at_utc": ts, "campaign": 312, "part": "verdict",
        "analysis": "final_verdict", "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "finding": finding,
        "basis": "c312_usdt_m_linear_cross_sectional_ofi_carry_costed_oos_5m",
        "dataset": dataset_block,
        "oos_sweep_artifact": str(op.relative_to(ROOT)), "oos_sweep_sha256": sweep_sha,
        "registry_artifact": str(op_reg.relative_to(ROOT)), "registry_sha256": reg_sha,
        "summary_artifact": str(op_sum.relative_to(ROOT)), "summary_sha256": sum_sha,
        "binding_constraint": binding,
        "n_deterministic_edge": int(n_edge),
        "n_survive_holm": int(n_survive_holm), "n_survive_bh": int(n_survive_bh),
        "n_survive_both": int(n_survive_both), "n_survive_cost_realism": int(n_survive_realistic),
        "hard_bans_honored": [
            "No synthetic/fabricated data; no relabeling existing caches as new",
            "No threshold/gate weakening; no cherry-picked windows/costs",
            "No edge claim unless the costed OOS test survives Holm+BH over 504 configs",
            "Real USDT-M linear 5m klines taker buy/sell split; funding excluded (control leg)",
            "linear-settlement (no convexity) attribution; executed_fills: false",
        ],
    }
    op_ver = reports / f"campaign312_verdict_{ts}.json"
    op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")
    ver_sha = sha256_file(op_ver)

    bind_sha = None; bind_path = None; binding_obj = None
    if binding is not None:
        binding_obj = {
            "generated_at_utc": ts, "campaign": 312, "part": "binding_constraint",
            "analysis": "binding_constraint_diagnosis", "verdict": verdict,
            "real_data_only": True, "fabricated_data": False, "executed_fills": False,
            "oos_sweep_artifact": str(op.relative_to(ROOT)), "oos_sweep_sha256": sweep_sha,
            "binding_constraint": binding,
            "n_deterministic_edge": int(n_edge),
            "n_survive_holm": int(n_survive_holm), "n_survive_bh": int(n_survive_bh),
            "n_survive_both": int(n_survive_both), "n_survive_cost_realism": int(n_survive_realistic),
            "n_edge": int(n_edge),
            "edge_explained_by_ofi_carry": bool(edge_explained_by_ofi_carry),
            "aggregate_ofi_carry_share": float(agg_ofi_carry_share),
            "aggregate_conv_share": float(agg_conv_share),
            "diagnosis": (
                "C312 USDT-M linear cross-sectional OFI carry does not survive validation; formal negative. "
                f"Binding constraint: {binding}."
            ),
            "note": "Diagnosis only; never an edge claim. No threshold weakening.",
        }
        op_bind = reports / f"campaign312_binding_constraint_{ts}.json"
        op_bind.write_text(json.dumps(binding_obj, indent=2, default=jdefault) + "\n")
        bind_sha = sha256_file(op_bind)
        bind_path = str(op_bind.relative_to(ROOT))
        verdict_obj["binding_constraint_artifact"] = bind_path
        verdict_obj["binding_constraint_sha256"] = bind_sha
        op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")
        ver_sha = sha256_file(op_ver)

    print(json.dumps({
        "campaign": 312, "verdict": verdict, "edge_proven": edge_proven,
        "n_total_runs": int(n_total), "n_with_exposure": int(n_exp),
        "n_deterministic_edge": int(n_edge),
        "n_survive_holm": int(n_survive_holm), "n_survive_bh": int(n_survive_bh),
        "n_survive_both": int(n_survive_both), "n_survive_cost_realism": int(n_survive_realistic),
        "binding_constraint": binding,
        "aggregate_ofi_carry_share": float(agg_ofi_carry_share),
        "aggregate_conv_share": float(agg_conv_share),
        "mde_bps_mean": mde_bps, "observed_mean_bps_per_split": obs_mean_bps,
        "stable_first_half": stable_first, "stable_second_half": stable_second,
        "artifacts": {
            "oos_sweep": str(op.relative_to(ROOT)), "registry": str(op_reg.relative_to(ROOT)),
            "summary": str(op_sum.relative_to(ROOT)), "verdict": str(op_ver.relative_to(ROOT)),
            "binding_constraint": bind_path,
        },
        "sha256": {"oos_sweep": sweep_sha, "registry": reg_sha, "summary": sum_sha,
                   "verdict": ver_sha, "binding_constraint": bind_sha},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())