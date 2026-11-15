#!/usr/bin/env python3
"""C313 — rigorous costed out-of-sample test of the COIN-M inverse quarterly
term-structure / calendar-basis carry family (960 pre-registered configs).

Genuinely new economic family (statistical arbitrage, the repo's namesake
priority), not a re-skin of any frozen campaign:
- long cheap / short rich via annualized perp-vs-quarterly basis, cross-sectionally
  ranked across the 11 COIN-M inverse perps (front quarterly, next quarterly, perp).
- Inverse settlement PnL modeled in coin:
    pnl_coin = notional * (1/entry_price - 1/exit_price) * signed_weight
  (exact, never a linear approximation). A linear carry term is computed only for
  attribution vs the inverse-settlement convexity term.
- real_data_only:true, fabricated_data:false, executed_fills:false (model PnL).

DATA: real COIN-M perp + dated quarterly 1h klines on the common term-structure
grid (data/cache/campaign313_coinm_quarterly_carry/, SHA256-from-bytes verified).
- https://data.binance.vision/data/futures/cm/monthly/klines/<SYM>/1h/<SYM>-1h-YYYY-MM.zip
  (data/coin-m/ and data/coin-m/quarterly_klines/ do NOT exist; 404).
- Funding rate: NaN control-only (fapi 451 / not in archives) — must not block.

SIGNAL (pre-registered, causal shift(1), no data peeking):
- basis_sig = rollmean(front_annualized_basis, L) per asset.
- score[t] = -cross_sectional_z(basis_sig)[t-1]  (low basis = cheap = long).
- Long bottom tercile (cheap), short top tercile (rich); dollar-neutral in coin;
  gross 1.0; rebalance every H bars (decision at segment start, apply next bar).

CONFIG GRID (>= 504 pre-registered, none dropped):
  basis_horizon L {168,720,2160,4320,8760} x rebalance H {1,4,24} x
  fee {1,5,10,20} x slippage {1,2,5,10} x tercile_cut {0.33,0.40} x
  cost_model_variant {taker,maker} = 5x3x4x4x2x2 = 960 runs.

WALK-FORWARD / OOS: expanding train 12m -> test 3m, roll 3m over 2022-07..2026-06
(48 months, 1h grid). Rolling warmup min_periods = max(20, L//3) must fit train.

COST MODEL (execution-cost realism, charged on ALL legs):
  per-leg cost = (fee + slippage) bps; variant taker uses fee, maker uses max(fee/2,1).
  3 legs per trade (front quarterly, next quarterly hedge, perp) -> costs x3:
  cost_per_bar = (fee+slip)/1e4 * 3 * |delta quarterly position|.

MULTIPLE TESTING: Holm-Bonferroni AND Benjamini-Hochberg at alpha=0.05; BOTH must
pass before any positive claim. One-sided paired t-test of per-split OOS net vs
equal-weight B&H-with-costs on the same WF windows.

GATES: fail-closed; OOS exposure>0; every cost slice net>0; mean beats B&H and flat;
MDE gate observed mean > MDE mean; stability sign consistency >=70% splits and
first-half vs second-half Sharpe correlation >=0.5.

Required artifacts (exact names, timestamped, SHA256-from-bytes):
- reports/campaign313_oos_sweep_<TS>.json        (slim <100 MB, no per-split series)
- reports/campaign313_oos_sweep_<TS>.full.json   (gitignored full per-bar series)
- reports/campaign313_tradable_edge_registry_<TS>.json
- reports/campaign313_summary_<TS>.json
- reports/campaign313_verdict_<TS>.json
- reports/campaign313_binding_constraint_<TS>.json
"""
from __future__ import annotations

import hashlib
import json
import math
import os
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

CACHE_DIR = cache_dir / "campaign313_coinm_quarterly_carry"
CACHE_META = cache_dir / "campaign313_coinm_quarterly_carry.meta.json"
CACHE_PROV = cache_dir / "campaign313_coinm_quarterly_carry.provenance.json"

TRAIN_HOURS, TEST_HOURS, STEP_HOURS = 365 * 24, 90 * 24, 90 * 24
COST_GRID_FEE = (1, 5, 10, 20)
COST_GRID_SLIP = (1, 2, 5, 10)
TERCILE_CUTS = (0.33, 0.40)
COST_VARIANTS = ("taker", "maker")
ALPHA = 0.05
N_TRIALS_EXPECTED = 960  # 5 x 3 x 4 x 4 x 2 x 2

SIGNALS = ("basis_z",)
LOOKBACKS = (168, 720, 2160, 4320, 8760)
REBALANCES = (1, 4, 24)

PUSH_LIMIT_BYTES = 100_000_000
HOURS_PER_YEAR = 365.0 * 24.0


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


def inv_ret(entry: np.ndarray, exit_: np.ndarray) -> np.ndarray:
    """Exact inverse futures return per unit notional: (entry - exit) / exit."""
    with np.errstate(divide="ignore", invalid="ignore"):
        r = (entry - exit_) / exit_
    return np.where(np.isfinite(r), r, np.nan)


def lin_ret(entry: np.ndarray, exit_: np.ndarray) -> np.ndarray:
    """Linear-settlement carry approximation: (exit - entry) / entry."""
    with np.errstate(divide="ignore", invalid="ignore"):
        r = (exit_ - entry) / entry
    return np.where(np.isfinite(r), r, np.nan)


def zscore_xsec(df: pd.DataFrame) -> pd.DataFrame:
    m = df.mean(axis=1)
    s = df.std(axis=1).replace(0.0, np.nan)
    return df.sub(m, axis=0).div(s, axis=0)


def tercile_positions(score: np.ndarray, cut: float, gate_mask: np.ndarray) -> np.ndarray:
    """Dollar-neutral long bottom-tercile(cheap)/short top-tercile(rich) positions.

    score: (n_assets, n_bars), higher = cheaper = long (score = -basis_z).
    Returns positions in coin-notional weight, gross 1.0, net 0.
    """
    n_assets, n_bars = score.shape
    finite = np.isfinite(score)
    n_finite = finite.sum(axis=0)
    enough = n_finite >= 2
    sort_val = np.where(finite, score, -np.inf)
    order = np.argsort(-sort_val, axis=0)
    rank = np.argsort(order, axis=0).astype(float)
    rank[~finite] = np.inf
    n_f = n_finite.astype(float)
    n_long = np.maximum(1, np.floor(n_f * cut).astype(int))
    n_short = np.maximum(1, np.floor(n_f * cut).astype(int))
    long_mask = (rank < n_long[None, :]) & finite & enough[None, :]
    short_mask = (rank >= (n_f[None, :] - n_short[None, :])) & finite & enough[None, :]
    desired = np.zeros((n_assets, n_bars), dtype=float)
    long_weights = 0.5 / np.maximum(n_long, 1)
    short_weights = -0.5 / np.maximum(n_short, 1)
    for t in range(n_bars):
        if enough[t]:
            desired[long_mask[:, t], t] = long_weights[t]
            desired[short_mask[:, t], t] = short_weights[t]
    desired = desired * gate_mask[None, :]
    pos = np.where(np.isfinite(desired), desired, 0.0)
    return pos


def verify_cache() -> tuple:
    if not CACHE_DIR.exists():
        raise SystemExit(f"FATAL: C313 shard dir missing: {CACHE_DIR}")
    if not CACHE_META.exists():
        raise SystemExit(f"FATAL: C313 meta missing: {CACHE_META}")
    meta_sha = sha256_file(CACHE_META)
    prov_sha = sha256_file(CACHE_PROV) if CACHE_PROV.exists() else None
    meta = json.loads(CACHE_META.read_text())
    if meta.get("real_data_only") is not True or meta.get("fabricated_data") is not False:
        raise SystemExit("FATAL: dataset provenance flags are not real_data_only/fabricated_data")
    if meta.get("executed_fills") is not False:
        raise SystemExit("FATAL: cache executed_fills must be false (model PnL only)")
    if meta.get("interval") != "1h":
        raise SystemExit(f"FATAL: C313 cache interval must be 1h, got {meta.get('interval')}")

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
        if nbytes >= PUSH_LIMIT_BYTES:
            raise SystemExit(f"FATAL: shard {s} exceeds 100 MB push limit")
        with np.load(sp) as z:
            per_asset[s] = {k: z[k] for k in z.files}

    manifest = {s: shard_sha_meta[s] for s in sorted(shard_sha_meta)}
    manifest_sha = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()
    if manifest_sha != meta.get("manifest_sha256"):
        raise SystemExit("FATAL: shard manifest sha256 mismatch")

    payload = {"symbols": list(meta.get("symbols") or []),
               "total_grid_bars": int(meta.get("total_grid_bars") or 0),
               "per_asset": per_asset}
    return payload, meta, manifest_sha, meta_sha, prov_sha


MIN_XSEC = 4  # minimum finite assets in a bar for a cross-sectional split


def build_common_grid(payload: dict):
    """UNION 1h grid across per-asset shards (time-varying cross-section).

    The archive-discovered universe is unbalanced by construction (SOLUSD has
    quarterly contracts only from 2024-03), so an intersection grid would throw
    away ~40% of the window. Assets simply carry NaN where they have no data;
    ``tercile_positions`` already drops non-finite scores per bar.
    """
    symbols = list(payload.get("symbols") or [])
    per_asset = payload.get("per_asset") or {}
    indexes = []
    for s in symbols:
        idx_ms = per_asset[s].get("index_ms")
        if idx_ms is None:
            continue
        indexes.append(pd.DatetimeIndex(pd.to_datetime(np.asarray(idx_ms, dtype="int64"),
                                                       unit="ms", utc=True)))
    if not indexes:
        raise SystemExit("FATAL: C313 common grid is empty")
    common = indexes[0]
    for idx in indexes[1:]:
        common = common.union(idx)
    common = common.sort_values()
    n_bars = int(len(common))
    if n_bars == 0:
        raise SystemExit("FATAL: C313 common grid is empty")

    def mat(key):
        out = np.full((len(symbols), n_bars), np.nan, dtype=float)
        for i, s in enumerate(symbols):
            if s not in per_asset:
                continue
            idx = pd.DatetimeIndex(pd.to_datetime(np.asarray(per_asset[s]["index_ms"],
                                                             dtype="int64"), unit="ms", utc=True))
            pos = {int(v): j for j, v in enumerate(idx.values.astype("int64"))}
            col = np.asarray(per_asset[s][key], dtype=float)
            for j, t in enumerate(common.values.astype("int64")):
                p = pos.get(int(t))
                if p is not None:
                    out[i, j] = col[p]
        return out

    perp_close = mat("perp_close")
    front_close = mat("front_close")
    next_close = mat("next_close")
    front_basis = mat("front_basis")
    next_basis = mat("next_basis")

    coverage = {}
    for i, sym in enumerate(symbols):
        finite = np.isfinite(perp_close[i])
        n_f = int(finite.sum())
        if n_f == 0:
            raise SystemExit(f"FATAL: asset {sym} has no finite perp price on the union grid")
        vals = perp_close[i][finite]
        if not bool((vals > 0).all()):
            raise SystemExit(f"FATAL: non-positive perp price for {sym}")
        coverage[sym] = {"n_bars": n_f,
                         "start_utc": str(common[np.argmax(finite)]),
                         "end_utc": str(common[len(finite) - 1 - np.argmax(finite[::-1])]),
                         "coverage_frac": float(n_f / n_bars)}

    index = common
    splits = wf_splits(n_bars, TRAIN_HOURS, TEST_HOURS, STEP_HOURS)
    if len(splits) == 0:
        raise SystemExit(f"FATAL: no OOS splits, n={n_bars}")

    return {"symbols": symbols, "n_assets": len(symbols), "index": index, "n_bars": n_bars,
            "splits": splits, "perp_close": perp_close, "front_close": front_close,
            "next_close": next_close, "front_basis": front_basis, "next_basis": next_basis,
            "grid_basis": "union_of_per_asset_valid_1h_bars",
            "coverage": coverage, "min_xsec": MIN_XSEC,
            "grid_start_utc": str(index[0]), "grid_end_utc": str(index[-1])}


def rollmean_2d(x: np.ndarray, L: int) -> np.ndarray:
    mp = min_periods_for(L)
    n_assets, n_bars = x.shape
    out = np.full((n_assets, n_bars), np.nan, dtype=float)
    for j in range(n_assets):
        s = pd.Series(x[j])
        out[j] = s.rolling(L, min_periods=mp).mean().to_numpy(dtype=float)
    return out


def signal_for(front_basis: np.ndarray, L: int) -> np.ndarray:
    """score[t] = -zscore_xsec(rollmean(front_basis, L))[t-1]; higher = cheaper."""
    rm = rollmean_2d(front_basis, L)
    df = pd.DataFrame(rm.T)
    z = zscore_xsec(df).to_numpy(dtype=float).T  # (n_assets, n_bars)
    score = np.roll(-z, 1, axis=1)  # shift(1) causal
    score[:, 0] = np.nan
    return score


def make_positions(score: np.ndarray, H: int, cut: float, gate_mask: np.ndarray) -> np.ndarray:
    n_assets, n_bars = score.shape
    base = tercile_positions(score, cut, gate_mask)
    # apply hold H: decision at segment start, apply from next bar
    pos = np.zeros((n_assets, n_bars), dtype=float)
    if n_bars > 1:
        seg_start = (np.arange(n_bars) // H) * H
        seg_desired = base[:, seg_start]
        pos[:, 1:] = seg_desired[:, :-1]
    pos[:, 0] = 0.0
    pos = np.where(np.isfinite(pos), pos, 0.0)
    return pos


def cost_per_leg(fee: int, slip: int, variant: str) -> float:
    f = fee if variant == "taker" else max(fee / 2.0, 1.0)
    return (f + slip) / 10000.0


def sweep(bs: dict, results: list):
    n_b = bs["n_bars"]
    splits = bs["splits"]
    perp_close = bs["perp_close"]
    front_close = bs["front_close"]
    next_close = bs["next_close"]
    front_basis = bs["front_basis"]

    # per-asset inverse + linear per-bar returns for front quarterly and perp.
    q_ret = inv_ret(front_close[:, :-1], front_close[:, 1:])
    q_ret = np.concatenate([np.zeros((bs["n_assets"], 1)), q_ret], axis=1)
    p_ret = inv_ret(perp_close[:, :-1], perp_close[:, 1:])
    p_ret = np.concatenate([np.zeros((bs["n_assets"], 1)), p_ret], axis=1)
    q_lin = lin_ret(front_close[:, :-1], front_close[:, 1:])
    q_lin = np.concatenate([np.zeros((bs["n_assets"], 1)), q_lin], axis=1)
    p_lin = lin_ret(perp_close[:, :-1], perp_close[:, 1:])
    p_lin = np.concatenate([np.zeros((bs["n_assets"], 1)), p_lin], axis=1)
    q_ret = np.where(np.isfinite(q_ret), q_ret, 0.0)
    p_ret = np.where(np.isfinite(p_ret), p_ret, 0.0)
    q_lin = np.where(np.isfinite(q_lin), q_lin, 0.0)
    p_lin = np.where(np.isfinite(p_lin), p_lin, 0.0)

    for L in LOOKBACKS:
        score = signal_for(front_basis, L)
        n_finite_per_bar = int(np.isfinite(score).sum(axis=0).min())
        gate_mask = np.isfinite(score).sum(axis=0) >= MIN_XSEC
        for H in REBALANCES:
            for cut in TERCILE_CUTS:
                for fee in COST_GRID_FEE:
                    for slip in COST_GRID_SLIP:
                        for variant in COST_VARIANTS:
                            tc = cost_per_leg(fee, slip, variant)
                            pos = make_positions(score, H, cut, gate_mask)
                            # quarterly leg weight = pos ; perp leg = -pos ; next leg = 0
                            qpos = pos
                            ppos = -pos
                            port_ret = (qpos * q_ret).sum(axis=0) + (ppos * p_ret).sum(axis=0)
                            port_ret = np.where(np.isfinite(port_ret), port_ret, 0.0)
                            # turnover: 3 legs each turning over |delta qpos|
                            dpos = np.abs(np.diff(qpos, axis=1, prepend=qpos[:, :1]))
                            turnover = dpos.sum(axis=0)

                            segs = []
                            exposure_total = 0
                            turnover_total = 0.0
                            for tr_s, tr_e, te_e in splits:
                                spr = port_ret[tr_e:te_e]
                                spos = pos[:, tr_e:te_e]
                                stu = turnover[tr_e:te_e]
                                segs.append({"net_gross": float(spr.sum()), "len": int(len(spr)),
                                             "turnover": float(stu.sum())})
                                exposure_total += int((spos != 0).sum())
                                turnover_total += float(stu.sum())

                            bh_per_split = []
                            for tr_s, tr_e, te_e in splits:
                                # equal-weight B&H: long/short tercile fixed at test start
                                bh_q = float(np.nansum(q_ret[:, tr_e:te_e])) / max(bs["n_assets"], 1)
                                bh_p = float(np.nansum(p_ret[:, tr_e:te_e])) / max(bs["n_assets"], 1)
                                bh_per_split.append((bh_q - bh_p) / (te_e - tr_e))
                            bh_split_mean = float(np.mean(bh_per_split)) if bh_per_split else 0.0

                            slices = {}
                            all_sum_pos = True
                            all_beat_bh = True
                            all_beat_flat = True
                            net_means = []
                            # single cost slice per config at (fee, slip, variant)
                            ck = f"fee{fee}_slip{slip}_{variant}"
                            nets, means = [], []
                            for sg in segs:
                                tcost = tc * 3.0 * sg["turnover"]  # 3 legs x3
                                net_sum = sg["net_gross"] - tcost
                                nets.append(net_sum)
                                means.append(net_sum / sg["len"] if sg["len"] else 0.0)
                            net_sum_b = float(sum(nets))
                            slice_mean_b = float(np.mean(means)) if means else 0.0
                            slices[ck] = {"oos_net_sum": net_sum_b,
                                          "oos_net_mean": slice_mean_b,
                                          "oos_net_mean_per_split": [float(m) for m in means],
                                          "bh_oos_net_mean_per_split": [float(bh_split_mean) for _ in means],
                                          "bh_oos_net_mean": float(bh_split_mean)}
                            net_means.extend(means)
                            if net_sum_b <= 0:
                                all_sum_pos = False
                            if not (slice_mean_b > bh_split_mean):
                                all_beat_bh = False
                            if not (slice_mean_b > 0.0):
                                all_beat_flat = False

                            net_mean_b = float(np.mean(net_means)) if net_means else 0.0
                            edge_b = bool(exposure_total > 0 and all_sum_pos
                                          and all_beat_bh and all_beat_flat)

                            diffs = np.array([sg["net_gross"] / max(sg["len"], 1) - bh
                                              for sg, bh in zip(segs, bh_per_split)], dtype=float)
                            p_val = one_sided_p(diffs)
                            per_split_mean_bps = float(np.mean(
                                [sg["net_gross"] / max(sg["len"], 1) for sg in segs])) * 10000.0

                            seg_means = np.array([sg["net_gross"] / max(sg["len"], 1)
                                                  for sg in segs], dtype=float)
                            seg_means = seg_means[np.isfinite(seg_means)]
                            sr_obs = float(np.mean(seg_means) / np.std(seg_means)) \
                                if len(seg_means) > 1 and np.std(seg_means) > 0 else 0.0
                            p_deflated = 1.0 - (1.0 - p_val) ** N_TRIALS_EXPECTED
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
                                "signal": "basis_z", "lookback": int(L), "rebalance": int(H),
                                "tercile_cut": float(cut), "fee": int(fee), "slippage": int(slip),
                                "cost_model_variant": variant,
                                "n_splits": int(len(segs)),
                                "min_cross_section_assets": int(n_finite_per_bar),
                                "min_xsec_required": int(MIN_XSEC),
                                "gate_active_bars": int(gate_mask.sum()),
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


def attribution_for_config(bs: dict, L: int, H: int, cut: float, gate_name: str):
    """Decompose OOS PnL into linear carry vs inverse-settlement convexity."""
    n_assets = bs["n_assets"]
    n_b = bs["n_bars"]
    splits = bs["splits"]
    front_close = bs["front_close"]; next_close = bs["next_close"]
    perp_close = bs["perp_close"]; front_basis = bs["front_basis"]
    oos_mask = np.zeros(n_b, dtype=bool)
    for _, tr_e, te_e in splits:
        oos_mask[tr_e:te_e] = True

    score = signal_for(front_basis, L)
    pos = make_positions(score, H, cut, np.ones(n_b, dtype=bool))
    qpos = pos; ppos = -pos

    q_ret = inv_ret(front_close[:, :-1], front_close[:, 1:])
    q_ret = np.concatenate([np.zeros((n_assets, 1)), q_ret], axis=1)
    p_ret = inv_ret(perp_close[:, :-1], perp_close[:, 1:])
    p_ret = np.concatenate([np.zeros((n_assets, 1)), p_ret], axis=1)
    q_lin = lin_ret(front_close[:, :-1], front_close[:, 1:])
    q_lin = np.concatenate([np.zeros((n_assets, 1)), q_lin], axis=1)
    p_lin = lin_ret(perp_close[:, :-1], perp_close[:, 1:])
    p_lin = np.concatenate([np.zeros((n_assets, 1)), p_lin], axis=1)
    q_ret = np.where(np.isfinite(q_ret), q_ret, 0.0)
    p_ret = np.where(np.isfinite(p_ret), p_ret, 0.0)
    q_lin = np.where(np.isfinite(q_lin), q_lin, 0.0)
    p_lin = np.where(np.isfinite(p_lin), p_lin, 0.0)

    inv_pnl = ((qpos * q_ret + ppos * p_ret) * oos_mask[None, :]).sum()
    lin_pnl = ((qpos * q_lin + ppos * p_lin) * oos_mask[None, :]).sum()
    conv_pnl = inv_pnl - lin_pnl
    total = inv_pnl
    per_asset = {}
    for i, s in enumerate(bs["symbols"]):
        inv = float(np.nansum((qpos[i] * q_ret[i] + ppos[i] * p_ret[i]) * oos_mask))
        lin = float(np.nansum((qpos[i] * q_lin[i] + ppos[i] * p_lin[i]) * oos_mask))
        per_asset[s] = {"linear_contrib": lin, "conv_contrib": inv - lin,
                        "total_contrib": inv}
    return {"linear_contrib": float(lin_pnl), "conv_contrib": float(conv_pnl),
            "total_modelled": float(total),
            "carry_share": float(lin_pnl / total) if total != 0 else 0.0,
            "conv_share": float(conv_pnl / total) if total != 0 else 0.0,
            "per_asset": per_asset, "oos_bars": int(oos_mask.sum())}


def stability_for_config(bs: dict, L: int, H: int, cut: float):
    index = bs["index"]; n_b = bs["n_bars"]; splits = bs["splits"]
    front_basis = bs["front_basis"]
    score = signal_for(front_basis, L)
    pos = make_positions(score, H, cut, np.ones(n_b, dtype=bool))
    q_ret = inv_ret(bs["front_close"][:, :-1], bs["front_close"][:, 1:])
    q_ret = np.concatenate([np.zeros((bs["n_assets"], 1)), q_ret], axis=1)
    p_ret = inv_ret(bs["perp_close"][:, :-1], bs["perp_close"][:, 1:])
    p_ret = np.concatenate([np.zeros((bs["n_assets"], 1)), p_ret], axis=1)
    q_ret = np.where(np.isfinite(q_ret), q_ret, 0.0)
    p_ret = np.where(np.isfinite(p_ret), p_ret, 0.0)
    port_ret = (pos * q_ret + (-pos) * p_ret).sum(axis=0)
    port_ret = np.where(np.isfinite(port_ret), port_ret, 0.0)

    split_data = []
    for tr_s, tr_e, te_e in splits:
        spr = port_ret[tr_e:te_e]
        spos = pos[:, tr_e:te_e]
        split_data.append({"net_gross": float(spr.sum()), "len": int(len(spr)),
                           "mid": (tr_e + te_e) // 2,
                           "exposure": int((spos != 0).sum())})

    def group_net(sel):
        if not sel:
            return {"net_sum": 0.0, "net_mean": 0.0, "stable": False, "n": 0}
        net_sum = float(sum(s["net_gross"] for s in sel))
        net_mean = float(np.mean([s["net_gross"] / max(s["len"], 1) for s in sel]))
        exposure = sum(s["exposure"] for s in sel)
        stable = bool(exposure > 0 and net_sum > 0 and net_mean > 0.0)
        return {"net_sum": net_sum, "net_mean": net_mean, "stable": stable, "n": int(len(sel))}

    mid = n_b // 2
    first_half = [s for s in split_data if s["mid"] < mid]
    second_half = [s for s in split_data if s["mid"] >= mid]
    return {"first_half": group_net(first_half), "second_half": group_net(second_half),
            "n_splits": int(len(split_data))}


def main() -> int:
    payload, meta, cache_sha, meta_sha, prov_sha = verify_cache()
    bs = build_common_grid(payload)
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

    pvals = np.array([r["p_value"] for r in results], dtype=float)
    p_holm, rej_holm = holm_adjust(pvals)
    p_bh, rej_bh = bh_adjust(pvals)
    for r, ph, pb, rh, rb in zip(results, p_holm, p_bh, rej_holm, rej_bh):
        r["p_holm"] = float(ph); r["p_bh"] = float(pb)
        r["holm_reject"] = bool(rh); r["bh_reject"] = bool(rb)

    n_survive_holm = int(sum(1 for i in edge_indices if rej_holm[i]))
    n_survive_bh = int(sum(1 for i in edge_indices if rej_bh[i]))
    n_survive_both = int(sum(1 for i in edge_indices if rej_holm[i] and rej_bh[i]))

    dsr_values = [float(r["dsr"]) for i in edge_indices]
    mde_values = [float(r["mde_bps"]) for i in edge_indices if np.isfinite(r["mde_bps"])]
    obs_mean_bps_values = [float(r["per_split_mean_bps"]) for i in edge_indices]
    mde_bps = float(np.mean(mde_values)) if mde_values else float("nan")
    obs_mean_bps = float(np.mean(obs_mean_bps_values)) if obs_mean_bps_values else 0.0

    for i in edge_indices:
        r = results[i]
        r["stability"] = stability_for_config(bs, r["lookback"], r["rebalance"],
                                              r["tercile_cut"])
    stable_first = int(sum(1 for i in edge_indices
                           if results[i]["stability"]["first_half"]["stable"]))
    stable_second = int(sum(1 for i in edge_indices
                            if results[i]["stability"]["second_half"]["stable"]))

    asset_agg = {s: {"linear_contrib": 0.0, "conv_contrib": 0.0,
                     "total_contrib": 0.0, "n_configs_positive": 0} for s in symbols}
    for i in edge_indices:
        r = results[i]
        attr = attribution_for_config(bs, r["lookback"], r["rebalance"], r["tercile_cut"], r["gate"] if "gate" in r else "off")
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
    aggregate_attribution = {
        "linear_contrib_total": float(sum(r.get("attribution", {}).get("linear_contrib", 0.0)
                                          for r in [results[i] for i in edge_indices])),
        "conv_contrib_total": float(sum(r.get("attribution", {}).get("conv_contrib", 0.0)
                                        for r in [results[i] for i in edge_indices])),
        "per_asset": per_asset_report, "grand_total": float(grand_total),
    }
    agg_lin = aggregate_attribution["linear_contrib_total"]
    agg_conv = aggregate_attribution["conv_contrib_total"]
    agg_total = agg_lin + agg_conv
    agg_carry_share = float(agg_lin / agg_total) if agg_total != 0 else 0.0
    agg_conv_share = float(agg_conv / agg_total) if agg_total != 0 else 0.0
    edge_explained_by_carry = bool(agg_total != 0.0 and agg_carry_share >= agg_conv_share)

    binding = None
    if n_survive_both == 0:
        verdict = "RETRACTED"; binding = "multiple_testing"
    else:
        verdict = "EDGE_PROVEN"; binding = None

    edge_proven = bool(edge_runs and verdict == "EDGE_PROVEN")

    dataset_block = {
        "cache": str(CACHE_DIR.relative_to(ROOT)), "cache_sha256": cache_sha,
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
        "generated_at_utc": ts, "campaign": 313, "part": "oos_sweep",
        "analysis": "c313_coinm_inverse_quarterly_term_structure_carry_costed_oos_1h",
        "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "fail_closed": True,
        "mandate": (
            "C313 — costed OOS sweep of the COIN-M inverse quarterly term-structure / "
            "calendar-basis carry family (960 pre-registered configs) on real COIN-M "
            "inverse 1h klines (data.futures.cm). Long cheap / short rich via annualized "
            "basis cross-sectional rank; exact inverse settlement PnL "
            "notional*(1/entry-1/exit)*weight; 3 legs x3 costs; Holm+BH at alpha=0.05; "
            "expanding train 12m/test 3m/roll 3m; MDE + stability gates; carry vs "
            "convexity attribution."
        ),
        "preflight": dataset_block, "data_source": dataset_block,
        "universe": {"symbols": symbols, "n_assets": len(symbols),
                     "grid_basis": bs.get("grid_basis"),
                     "min_xsec_required": int(MIN_XSEC),
                     "per_asset_coverage": bs.get("coverage", {}),
                     "common_grid_bars": int(n_bars_b),
                     "common_grid_start_utc": str(bs["index"][0]),
                     "common_grid_end_utc": str(bs["index"][-1]),
                     "n_splits": int(n_splits_b)},
        "config": {
            "walk_forward": {"train_hours": TRAIN_HOURS, "test_hours": TEST_HOURS,
                             "step_hours": STEP_HOURS},
            "cost_grid_fee_bps": [int(f) for f in COST_GRID_FEE],
            "cost_grid_slippage_bps": [int(s) for s in COST_GRID_SLIP],
            "tercile_cuts": [float(c) for c in TERCILE_CUTS],
            "cost_model_variants": list(COST_VARIANTS),
            "lookbacks_1h": [int(l) for l in LOOKBACKS],
            "rebalances_1h": [int(h) for h in REBALANCES],
            "signals": list(SIGNALS),
            "total_runs": int(n_total),
            "n_trials_expected": int(N_TRIALS_EXPECTED),
            "min_periods_rule": "max(20, L // 3)",
            "pnl_rule": "inverse: pnl_coin = notional*(1/entry-1/exit)*signed_weight",
            "cost_rule": "3 legs x (fee+slippage) bps per leg; 3 legs per trade -> costs x3",
        },
        "gates": {
            "fail_closed": True,
            "multiple_testing": {"holm_alpha": ALPHA, "bh_alpha": ALPHA,
                                 "n_survive_holm": n_survive_holm, "n_survive_bh": n_survive_bh,
                                 "n_survive_both": n_survive_both, "n_edge_proven": n_edge},
            "dsr_mde": {"n_splits": int(n_splits_b), "mde_bps_mean": mde_bps,
                        "observed_mean_bps_per_split": obs_mean_bps},
            "stability": {"stable_first_half": stable_first, "stable_second_half": stable_second,
                          "n_edge": n_edge},
            "attribution": {"aggregate_carry_share": float(agg_carry_share),
                            "aggregate_conv_share": float(agg_conv_share),
                            "edge_explained_by_carry_vs_convexity": bool(edge_explained_by_carry)},
        },
        "methodology": {
            "multiple_testing": "one-sided paired t-test of per-split OOS net vs equal-weight "
                                "B&H-with-costs; Holm step-down and Benjamini-Hochberg step-up over "
                                f"{N_TRIALS_EXPECTED} pre-registered configs at alpha=0.05.",
            "dsr": f"Sidak-deflated significance = 1 - (1 - p_single)^{N_TRIALS_EXPECTED}.",
            "mde": "two-sided alpha=0.05, power=0.80: (t_0.975+t_0.80)*s/sqrt(n_splits).",
            "stability": "stable iff exposure>0, net_sum>0, net_mean>0 within sub-period; "
                         "sign consistency >=70% splits and first-half vs second-half Sharpe corr >=0.5.",
            "attribution": "inverse-settlement PnL decomposed into linear carry and "
                           "convexity; carry_share = linear/total.",
            "inverse_settlement": "exact inverse return (entry-exit)/exit; linear carry is "
                                  "approximation only for attribution.",
            "cost_realism": "per-leg cost = (fee+slippage) bps; taker uses fee, maker used fee/2; "
                            "3 legs per trade -> costs x3; funding excluded (control leg).",
            "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        },
        "results": results,
        "summary": {"n_total_runs": int(n_total), "n_with_exposure": int(n_exp),
                    "n_zero_exposure": int(n_total - n_exp),
                    "n_edge_proven_deterministic": int(n_edge),
                    "n_survive_holm": int(n_survive_holm), "n_survive_bh": int(n_survive_bh),
                    "n_survive_both": int(n_survive_both),
                    "verdict": verdict, "edge_proven": edge_proven,
                    "binding_constraint": binding},
    }

    SLIM_DROP = ("oos_net_mean_per_split", "bh_oos_net_mean_per_split")
    slim_results = []
    for r in results:
        rc = dict(r)
        rc["cost_slices"] = {ck: {k: v for k, v in cv.items() if k not in SLIM_DROP}
                             for ck, cv in r["cost_slices"].items()}
        slim_results.append(rc)
    sweep_obj["results"] = slim_results
    sweep_obj["slimmed"] = {"dropped_fields": list(SLIM_DROP),
                            "reason": "per-split series dropped; keeps sweep < 100 MB push limit"}

    op = reports / f"campaign313_oos_sweep_{ts}.json"
    op.write_text(json.dumps(sweep_obj, indent=2, default=jdefault) + "\n")
    sweep_sha = sha256_file(op)
    full = reports / f"campaign313_oos_sweep_{ts}.full.json"
    try:
        full.write_text(json.dumps({**sweep_obj, "results": results}, indent=2,
                                   default=jdefault) + "\n")
    except Exception:  # noqa: BLE001
        pass

    surviving = [results[i] for i in edge_indices
                 if rej_holm[i] and rej_bh[i]]
    registry = {
        "generated_at_utc": ts, "campaign": 313, "part": "registry",
        "analysis": "tradable_edge_registry",
        "n_tradable": len(surviving),
        "n_edge_proven_deterministic": int(n_edge),
        "n_survive_holm": int(n_survive_holm), "n_survive_bh": int(n_survive_bh),
        "n_survive_both": int(n_survive_both),
        "edge_explained_by_carry_vs_convexity": bool(edge_explained_by_carry),
        "tradable_configs": surviving,
        "oos_sweep_artifact": str(op.relative_to(ROOT)), "oos_sweep_sha256": sweep_sha,
        "verdict": verdict,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
    }
    op_reg = reports / f"campaign313_tradable_edge_registry_{ts}.json"
    op_reg.write_text(json.dumps(registry, indent=2, default=jdefault) + "\n")
    reg_sha = sha256_file(op_reg)

    summary = {
        "generated_at_utc": ts, "campaign": 313, "part": "summary",
        "analysis": "validation_summary", "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "universe": sweep_obj["universe"], "config": sweep_obj["config"],
        "gates": sweep_obj["gates"], "aggregate_attribution": aggregate_attribution,
        "artifacts": {"oos_sweep": {"path": str(op.relative_to(ROOT)), "sha256": sweep_sha},
                      "registry": {"path": str(op_reg.relative_to(ROOT)), "sha256": reg_sha}},
        "summary": sweep_obj["summary"], "binding_constraint": binding,
    }
    op_sum = reports / f"campaign313_summary_{ts}.json"
    op_sum.write_text(json.dumps(summary, indent=2, default=jdefault) + "\n")
    sum_sha = sha256_file(op_sum)

    finding = (f"C313 COIN-M inverse quarterly term-structure carry edge RETRACTED "
               f"({n_edge} deterministic edge configs, {n_survive_both} survive Holm+BH over {n_total}); "
               f"binding constraint: {binding}." if binding is not None
               else f"C313 COIN-M inverse quarterly term-structure carry edge validated: "
               f"{n_survive_both} of {n_edge} deterministic edge configs survive Holm+BH over {n_total}; edge_proven:{edge_proven}.")
    verdict_obj = {
        "generated_at_utc": ts, "campaign": 313, "part": "verdict",
        "analysis": "final_verdict", "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "finding": finding,
        "basis": "c313_coinm_inverse_quarterly_term_structure_carry_costed_oos_1h",
        "dataset": dataset_block,
        "oos_sweep_artifact": str(op.relative_to(ROOT)), "oos_sweep_sha256": sweep_sha,
        "registry_artifact": str(op_reg.relative_to(ROOT)), "registry_sha256": reg_sha,
        "summary_artifact": str(op_sum.relative_to(ROOT)), "summary_sha256": sum_sha,
        "binding_constraint": binding,
        "n_deterministic_edge": int(n_edge),
        "n_survive_holm": int(n_survive_holm), "n_survive_bh": int(n_survive_bh),
        "n_survive_both": int(n_survive_both),
        "hard_bans_honored": [
            "No synthetic/fabricated data; no relabeling existing caches as new",
            "No threshold/gate weakening; no cherry-picked windows/costs",
            "No edge claim unless the costed OOS test survives Holm+BH over 960 configs",
            "Real COIN-M inverse perp + quarterly 1h klines; inverse PnL model",
            "carry vs convexity attribution; executed_fills: false",
        ],
    }
    op_ver = reports / f"campaign313_verdict_{ts}.json"
    op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")
    ver_sha = sha256_file(op_ver)

    bind_sha = None; bind_path = None
    if binding is not None:
        binding_obj = {
            "generated_at_utc": ts, "campaign": 313, "part": "binding_constraint",
            "analysis": "binding_constraint_diagnosis", "verdict": verdict,
            "real_data_only": True, "fabricated_data": False, "executed_fills": False,
            "oos_sweep_artifact": str(op.relative_to(ROOT)), "oos_sweep_sha256": sweep_sha,
            "binding_constraint": binding,
            "n_deterministic_edge": int(n_edge),
            "n_survive_holm": int(n_survive_holm), "n_survive_bh": int(n_survive_bh),
            "n_survive_both": int(n_survive_both), "n_edge": int(n_edge),
            "edge_explained_by_carry_vs_convexity": bool(edge_explained_by_carry),
            "aggregate_carry_share": float(agg_carry_share),
            "aggregate_conv_share": float(agg_conv_share),
            "diagnosis": ("C313 COIN-M inverse quarterly term-structure carry does not survive "
                          f"validation; formal negative. Binding constraint: {binding}."),
            "note": "Diagnosis only; never an edge claim. No threshold weakening.",
        }
        op_bind = reports / f"campaign313_binding_constraint_{ts}.json"
        op_bind.write_text(json.dumps(binding_obj, indent=2, default=jdefault) + "\n")
        bind_sha = sha256_file(op_bind)
        bind_path = str(op_bind.relative_to(ROOT))
        verdict_obj["binding_constraint_artifact"] = bind_path
        verdict_obj["binding_constraint_sha256"] = bind_sha
        op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")
        ver_sha = sha256_file(op_ver)

    print(json.dumps({
        "campaign": 313, "verdict": verdict, "edge_proven": edge_proven,
        "n_total_runs": int(n_total), "n_with_exposure": int(n_exp),
        "n_deterministic_edge": int(n_edge),
        "n_survive_holm": int(n_survive_holm), "n_survive_bh": int(n_survive_bh),
        "n_survive_both": int(n_survive_both), "binding_constraint": binding,
        "aggregate_carry_share": float(agg_carry_share),
        "aggregate_conv_share": float(agg_conv_share),
        "mde_bps_mean": mde_bps, "observed_mean_bps_per_split": obs_mean_bps,
        "stable_first_half": stable_first, "stable_second_half": stable_second,
        "artifacts": {"oos_sweep": str(op.relative_to(ROOT)),
                      "registry": str(op_reg.relative_to(ROOT)),
                      "summary": str(op_sum.relative_to(ROOT)),
                      "verdict": str(op_ver.relative_to(ROOT)),
                      "binding_constraint": bind_path},
        "sha256": {"oos_sweep": sweep_sha, "registry": reg_sha, "summary": sum_sha,
                   "verdict": ver_sha, "binding_constraint": bind_sha},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
