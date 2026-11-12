#!/usr/bin/env python3
"""C273 split/asset decomposition + deterministic replication check.
Identical spec/params/caches as C273 PERCENTILE_SPREAD run; real cached data only."""
from __future__ import annotations
import hashlib, json, pickle, sys
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
cache_dir = root / "data" / "cache"
reports = root / "reports"
reports.mkdir(exist_ok=True)
ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')

SPOT_CACHE = cache_dir / "0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl"
SPOT_META = cache_dir / "0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.meta.json"
VOL_META = cache_dir / "volume_1h_full.meta.json"
VOL_PROV = cache_dir / "volume_1h_full.provenance.json"

C273_OOS = reports/"real_quote_volume_rqa_rte_over_white_diag_line_length_percentile_spread_shock_mr_costed_oos_20261112T050947Z.json"
C273_OOS_SHA = "1e4fd5983d29eb027336e77b2b3a5e7bda6fa6180494f0d836e5584cc298e1bf"

W_RR = 168
ALB = 336
M_EMB = 2
TAU = 1
EPS_SCALE = 0.5
W_MIN = 2
ENTRY_Z = 1.5
EXIT_Z = 0.5
MAX_HOLD = 24
TRAIN = 720
TEST = 168
STEP = 168
COST_GRID = [[0, 0], [5, 5], [10, 10], [20, 20], [40, 40]]
COST_KEYS = [f"fee{f}_slip{s}" for f,s in COST_GRID]

def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def load_spot():
    with open(SPOT_CACHE, "rb") as f:
        df = pickle.load(f)
    if isinstance(df, pd.Series):
        df = df.to_frame()
    return df

def load_volume():
    from data.real_feed_loader import validate_and_load_real_feed
    prov = json.loads(VOL_PROV.read_text()) if VOL_PROV.exists() else {}
    df, report = validate_and_load_real_feed(VOL_META, "real_quote_volume", provenance=prov)
    df = df.pivot_table(index="timestamp_utc", columns="symbol", values="quote_volume_usdt", aggfunc="first").sort_index()
    return df, report

def wf_splits(n: int, train: int, test: int, step: int):
    out = []
    i = 0
    while i + train + test <= n:
        out.append((i, i + train, i + train + test))
        i += step
    return out

def _qualifying_white_diag_segments(diag: np.ndarray, w_min: int):
    diag = np.asarray(diag)
    if diag.size == 0:
        return []
    padded = np.concatenate(([1.0], diag, [1.0]))
    ones = np.flatnonzero(padded)
    gaps = np.diff(ones) - 1
    gaps = gaps[gaps >= w_min]
    return gaps.astype(int).tolist()

def _white_diag_line_length_percentile_spread(R: np.ndarray, w_min: int) -> float:
    M_pts = R.shape[0]
    seg_lengths = []
    for k in range(-(M_pts - 1), M_pts):
        if k == 0:
            continue
        segs = _qualifying_white_diag_segments(np.diag(R, k=k), w_min)
        if segs:
            seg_lengths.extend(int(s) for s in segs)
    if len(seg_lengths) < 3:
        return np.nan
    arr = np.array(seg_lengths, dtype=float)
    if not np.all(np.isfinite(arr)) or not np.all(arr > 0):
        return np.nan
    p25 = float(np.percentile(arr, 25))
    p75 = float(np.percentile(arr, 75))
    med = float(np.median(arr))
    if not (np.isfinite(p25) and np.isfinite(p75) and np.isfinite(med)):
        return np.nan
    if med <= 0:
        return np.nan
    spread = (p75 - p25) / med
    if not np.isfinite(spread):
        return np.nan
    return float(spread)

def main():
    spot_df = load_spot()
    vol_df, vol_report = load_volume()
    common = sorted(set(spot_df.columns).intersection(set(vol_df.columns)))
    if len(common) == 0:
        raise SystemExit("NO_COMMON_ASSETS")

    c273 = json.loads(C273_OOS.read_text())
    c273_cross = c273["cross_asset"]["oos_net_sums"]

    assets = {}
    recomputed_cross = {k:0.0 for k in COST_KEYS}
    # collect per-split cross sums: split_index -> cost_key -> sum
    split_cross = {}

    for sym in common:
        sp = spot_df[sym].dropna()
        vv = vol_df[sym].dropna()
        idx = sp.index.intersection(vv.index)
        sp = sp.loc[idx]; vv = vv.loc[idx]
        r = np.log(vv).diff().dropna()
        if len(r) < ALB + TRAIN + TEST + 50:
            assets[sym] = {"status":"insufficient"}; continue
        feats = []
        for t in range(ALB, len(r)):
            win = r.iloc[t - W_RR : t].to_numpy(dtype=float)
            if win.size != W_RR or not np.all(np.isfinite(win)):
                feats.append(np.nan); continue
            std_w = float(np.std(win))
            if not np.isfinite(std_w) or std_w <= 0:
                feats.append(np.nan); continue
            X = np.column_stack([win[:-1], win[1:]])
            eps = EPS_SCALE * std_w
            d = np.max(np.abs(X[:, None, :] - X[None, :, :]), axis=2)
            Rm = (d <= eps + 1e-18).astype(float)
            feats.append(_white_diag_line_length_percentile_spread(Rm, W_MIN))
        feat = pd.Series(feats, index=r.index[ALB : ALB + len(feats)]).replace([np.inf,-np.inf], np.nan)
        if feat.dropna().shape[0] < TRAIN + TEST + 10:
            assets[sym] = {"status":"feature_insufficient"}; continue
        rets = r.loc[feat.index].shift(-1).dropna()
        feat = feat.loc[rets.index]
        pos = pd.Series(0.0, index=feat.index)
        splits = wf_splits(len(feat), TRAIN, TEST, STEP)
        if len(splits) == 0:
            assets[sym] = {"status":"no_splits"}; continue

        for (s0, tr_e, te_e) in splits:
            f_tr = feat.iloc[s0:tr_e]; f_te = feat.iloc[tr_e:te_e]
            f_tr_c = f_tr.dropna()
            if f_tr_c.shape[0] < 50:
                continue
            mu = float(f_tr_c.mean()); sig = float(f_tr_c.std(ddof=0))
            if not np.isfinite(sig) or sig <= 0:
                continue
            z = (f_te - mu) / sig
            for ti, zz in z.dropna().items():
                if zz > ENTRY_Z: pos.at[ti] = -1.0
                elif zz < -ENTRY_Z: pos.at[ti] = 1.0
                else: pos.at[ti] = 0.0
        arr_pos = pos.to_numpy(dtype=float).copy()
        i = 1
        while i < len(arr_pos):
            if arr_pos[i - 1] != 0 and arr_pos[i] == 0:
                carry = arr_pos[i - 1]; j = i; held = 0
                while j < len(arr_pos) and arr_pos[j] == 0 and held < MAX_HOLD:
                    arr_pos[j] = carry; j += 1; held += 1
                i = j
            else:
                i += 1
        pos = pd.Series(arr_pos, index=feat.index)

        npn = rets.to_numpy(dtype=float)
        ppn = pos.to_numpy(dtype=float)
        bh = npn.copy()
        per_split = []
        per_cost = {}
        for fee, slp in COST_GRID:
            ck = f"fee{fee}_slip{slp}"
            tc = (fee + slp) / 10000.0
            trades = np.abs(np.diff(np.concatenate([[0.0], ppn])))
            strat = ppn * npn - trades * tc
            oos_nets = []
            for si,(s0,tr_e,te_e) in enumerate(splits):
                seg = strat[tr_e:te_e]
                seg_bh = bh[tr_e:te_e]
                oos_nets.append(float(np.sum(seg)))
                if si not in split_cross:
                    split_cross[si] = {k:0.0 for k in COST_KEYS}
                    split_cross[si]['_meta'] = {'s0':int(s0),'tr_e':int(tr_e),'te_e':int(te_e)}
                split_cross[si][ck] += float(np.sum(seg))
            oos_np = np.array([strat[tr_e:te_e].sum() for (_,tr_e,te_e) in splits], dtype=float)
            oos_bh = np.array([bh[tr_e:te_e].sum() for (_,tr_e,te_e) in splits], dtype=float)
            total = float(oos_np.sum())
            recomputed_cross[ck] += total
            per_cost[ck] = {
                "oos_net_sum": total,
                "oos_net_mean": float(np.mean([strat[tr_e:te_e].mean() for (_,tr_e,te_e) in splits])) if splits else None,
                "bh_oos_net_mean": float(np.mean([bh[tr_e:te_e].mean() for (_,tr_e,te_e) in splits])) if splits else None,
                "oos_n": int(sum(te_e-tr_e for (_,tr_e,te_e) in splits)),
                "exposure_bars": float((np.abs(pos.shift(1).fillna(0.0)) > 0).sum()),
                "per_split_oos_net_sum": [float(strat[tr_e:te_e].sum()) for (_,tr_e,te_e) in splits],
            }
        for si,(s0,tr_e,te_e) in enumerate(splits):
            row = {"split": si, "s0": int(s0), "train_end": int(tr_e), "test_end": int(te_e)}
            for fee,slp in COST_GRID:
                ck=f"fee{fee}_slip{slp}"
                row[ck]=per_cost[ck]["per_split_oos_net_sum"][si]
            per_split.append(row)
        assets[sym] = {
            "status":"ok","bars":int(len(sp)),"ratio_finite_bars":int(np.isfinite(feat.to_numpy()).sum()),
            "n_splits": len(splits),
            "per_cost": {ck: {k:v for k,v in per_cost[ck].items() if k!="per_split_oos_net_sum"} for ck in COST_KEYS},
            "per_cost_split_nets": {ck: per_cost[ck]["per_split_oos_net_sum"] for ck in COST_KEYS},
            "per_split": per_split,
        }

    # replication diffs
    diffs = {}
    matches = True
    for ck in COST_KEYS:
        d = recomputed_cross[ck]-float(c273_cross[ck])
        diffs[ck] = d
        if abs(d) > 1e-9:
            matches = False

    # stability summary
    ok_assets = {s:a for s,a in assets.items() if a.get('status')=='ok'}
    n_splits = None
    for a in ok_assets.values():
        n_splits = a['n_splits']; break
    per_split_cross_list = []
    for si in sorted(k for k in split_cross.keys() if isinstance(k,int)):
        row = {"split": si, **{k:v for k,v in split_cross[si].items() if not k.startswith('_')}, "bounds": split_cross[si]['_meta']}
        per_split_cross_list.append(row)

    def split_stats(cost_key):
        vals = [r[cost_key] for r in per_split_cross_list]
        pos = sum(1 for v in vals if v>0)
        return {"count": len(vals), "positive": pos, "negative_or_zero": len(vals)-pos, "positive_share": (pos/len(vals) if vals else None), "min": min(vals) if vals else None, "max": max(vals) if vals else None, "mean": (sum(vals)/len(vals) if vals else None), "values": vals}

    asset_stats = {}
    for sym,a in ok_assets.items():
        asset_stats[sym] = {}
        for ck in COST_KEYS:
            vals = a['per_cost_split_nets'][ck]
            pos = sum(1 for v in vals if v>0)
            asset_stats[sym][ck] = {"oos_net_sum": a['per_cost'][ck]['oos_net_sum'], "positive_splits": pos, "n_splits": len(vals), "positive_share": pos/len(vals) if vals else None, "min_split": min(vals) if vals else None, "max_split": max(vals) if vals else None}

    out = {
        "generated_at_utc": ts,
        "campaign": 273,
        "analysis": "split_asset_decomposition_and_replication",
        "strategy_id": "VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_PERCENTILE_SPREAD_SHOCK_MR",
        "source_c273_oos": str(C273_OOS.relative_to(root)),
        "source_c273_oos_sha256": sha256_file(C273_OOS),
        "expected_c273_oos_sha256": C273_OOS_SHA,
        "replication_matches_c273": matches,
        "replication_diffs_recomputed_minus_reported": diffs,
        "c273_reported_cross_asset_oos_net_sums": c273_cross,
        "recomputed_cross_asset_oos_net_sums": recomputed_cross,
        "spec": {"W_RR":W_RR,"alb":ALB,"m":M_EMB,"tau":TAU,"eps_scale":EPS_SCALE,"w_min":W_MIN,"entry_z":ENTRY_Z,"exit_z":EXIT_Z,"max_hold":MAX_HOLD,"train":TRAIN,"test":TEST,"step":STEP,"cost_grid_bps":COST_GRID},
        "data_sources": {"spot_cache": str(SPOT_CACHE.relative_to(root)), "spot_cache_sha256": sha256_file(SPOT_CACHE), "volume_provenance_sha256": sha256_file(VOL_PROV) if VOL_PROV.exists() else None},
        "ok_asset_count": len(ok_assets),
        "n_splits_per_asset": n_splits,
        "cross_asset_per_split": per_split_cross_list,
        "cross_asset_split_stats": {ck: split_stats(ck) for ck in COST_KEYS},
        "per_asset_split_stats": asset_stats,
        "per_asset": assets,
        "volume_validation": vol_report,
        "stability_assessment": None,
    }
    # stability summary
    fee0 = out['cross_asset_split_stats']['fee0_slip0']
    broad = fee0['positive_share'] is not None and fee0['positive_share'] >= 0.6
    all_pos_assets_fee0 = sum(1 for s in asset_stats.values() if s['fee0_slip0']['oos_net_sum']>0)
    out['stability_assessment'] = {
        "fee0_positive_split_share": fee0['positive_share'],
        "fee0_positive_splits": fee0['positive'],
        "fee0_total_splits": fee0['count'],
        "assets_positive_net_fee0": all_pos_assets_fee0,
        "assets_total_ok": len(ok_assets),
        "cross_asset_positive_all_cost_slices_recomputed": all(recomputed_cross[ck]>0 for ck in COST_KEYS),
        "broad_split_support_fee0_ge_60pct": broad,
        "note": "Computed from deterministic replication on real cached data only; no refetch/synthetic."
    }
    op = reports/f'campaign273_split_decomposition_{ts}.json'
    op.write_text(json.dumps(out, indent=2, default=str)+'\n')
    print(json.dumps({
        'artifact': str(op.relative_to(root)), 'sha256': sha256_file(op),
        'replication_matches_c273': matches, 'diffs': diffs,
        'recomputed_cross': recomputed_cross,
        'stability_assessment': out['stability_assessment']
    }, indent=2))

if __name__ == '__main__':
    main()
