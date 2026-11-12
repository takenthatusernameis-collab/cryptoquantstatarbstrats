#!/usr/bin/env python3
"""C275 split/asset decomposition + deterministic replication check (MEDCOUPLE).
Recomputes costed OOS on real cached data only using identical logic as C275 runner."""
from __future__ import annotations
import hashlib, json, pickle, sys
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
from scripts.run_c275_rte_over_white_diag_medcouple_shock_mr_costed_oos import (  # noqa: E402
    compute_feature_series, trading_signals, net_pnl,
    W_RR, M_EMB, TAU, EPS_SCALE, W_MIN, ENTRY_Z, EXIT_Z, MAX_HOLD,
    TRAIN, TEST, STEP, COST_GRID, SPOT_CACHE, VOL_META, VOL_PROV,
)
reports = root / 'reports'
reports.mkdir(exist_ok=True)
ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
COST_KEYS = [f'fee{f}_slip{s}' for f, s in COST_GRID]

def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def load_spot():
    with open(SPOT_CACHE, 'rb') as f:
        df = pickle.load(f)
    return df

def load_volume():
    from data.real_feed_loader import validate_and_load_real_feed  # noqa: E402
    prov = json.loads(VOL_PROV.read_text()) if VOL_PROV.exists() else {}
    df, report = validate_and_load_real_feed(VOL_META, 'real_quote_volume', provenance=prov)
    df = df.pivot_table(index='timestamp_utc', columns='symbol', values='quote_volume_usdt', aggfunc='first').sort_index()
    return df, report

def wf_splits(n: int):
    out = []
    i = 0
    while i + TRAIN + TEST <= n:
        out.append((i, i + TRAIN, i + TRAIN + TEST))
        i += STEP
    return out

def main():
    spot_df = load_spot()
    vol_df, vol_report = load_volume()
    common = sorted(set(spot_df.columns).intersection(set(vol_df.columns)))
    if not common:
        raise SystemExit('NO_COMMON_ASSETS')
    spot = spot_df[common].sort_index()
    vol = vol_df[common].sort_index()
    common_idx = spot.index.intersection(vol.index)
    spot = spot.loc[common_idx]; vol = vol.loc[common_idx]
    close = spot.ffill().bfill().to_numpy(dtype=float)
    log_vol = np.log(np.clip(vol.ffill().bfill().to_numpy(dtype=float), 1e-12, None))

    saved_path = None
    for cand in sorted(reports.glob('real_quote_volume_rqa_rte_over_white_diag_line_length_medcouple_shock_mr_costed_oos_*.json')):
        saved_path = cand
    saved_oos = json.loads(saved_path.read_text()) if saved_path else None
    saved_cross = saved_oos.get('cross_asset', {}).get('oos_net_sums', {}) if saved_oos else {}

    assets = {}
    recomputed_cross = {k: 0.0 for k in COST_KEYS}
    split_cross = {}
    n_splits_global = 0

    for j, sym in enumerate(common):
        c = close[:, j]; lv = log_vol[:, j]
        feat = compute_feature_series(lv)
        T = len(c)
        splits = wf_splits(T)
        n_splits_global = max(n_splits_global, len(splits))
        per_cost = {}
        per_cost_split_nets = {}
        per_split = []
        for fee, slip in COST_GRID:
            ck = f'fee{fee}_slip{slip}'
            pos_full = trading_signals(feat, ENTRY_Z, EXIT_Z, MAX_HOLD)
            net = net_pnl(pos_full, c, fee, slip)
            oos_nets = []
            for si, (s0, tr_e, te_e) in enumerate(splits):
                end = min(te_e - 1, T)
                seg = net[s0:end] if end > s0 else np.array([])
                oos_nets.append(float(np.sum(seg)) if seg.size else 0.0)
                if si not in split_cross:
                    split_cross[si] = {k: 0.0 for k in COST_KEYS}
                    split_cross[si]['_meta'] = {'s0': int(s0), 'train_end': int(tr_e), 'test_end': int(te_e)}
                split_cross[si][ck] += float(np.sum(seg)) if seg.size else 0.0
            total = float(np.sum(oos_nets)) if oos_nets else 0.0
            recomputed_cross[ck] += total
            per_cost[ck] = {
                'oos_net_sum': total,
                'oos_net_mean': float(np.mean(oos_nets)) if oos_nets else None,
                'oos_n': int(len(oos_nets)),
                'mean_exposure': float(np.mean([float(np.mean(np.abs(pos_full[s0:te_e]) > 0)) for s0, _tr_e, te_e in splits if te_e <= T])) if splits else 0.0,
                'any_exposure_split': any(float(np.mean(np.abs(pos_full[s0:te_e]) > 0)) > 0 for s0, _tr_e, te_e in splits if te_e <= T),
            }
            per_cost_split_nets[ck] = oos_nets
        for si, (s0, tr_e, te_e) in enumerate(splits):
            row = {'split': si, 's0': int(s0), 'train_end': int(tr_e), 'test_end': int(te_e)}
            for fee, slip in COST_GRID:
                ck = f'fee{fee}_slip{slip}'
                row[ck] = per_cost_split_nets[ck][si]
            per_split.append(row)
        assets[sym] = {
            'status': 'ok', 'bars': int(T), 'n_splits': len(splits),
            'per_cost': per_cost,
            'per_cost_split_nets': per_cost_split_nets,
            'per_split': per_split,
        }

    per_split_cross_list = []
    for si in sorted(k for k in split_cross.keys() if isinstance(k, int)):
        row = {'split': si, **{k: v for k, v in split_cross[si].items() if not k.startswith('_')}, 'bounds': split_cross[si]['_meta']}
        per_split_cross_list.append(row)

    def split_stats(cost_key):
        vals = [r[cost_key] for r in per_split_cross_list]
        pos = sum(1 for v in vals if v > 0)
        return {
            'count': len(vals), 'positive': pos, 'negative_or_zero': len(vals) - pos,
            'positive_share': (pos / len(vals) if vals else None),
            'min': min(vals) if vals else None, 'max': max(vals) if vals else None,
            'mean': (sum(vals) / len(vals) if vals else None), 'values': vals,
        }

    asset_stats = {}
    for sym, a in assets.items():
        asset_stats[sym] = {}
        for ck in COST_KEYS:
            vals = a['per_cost_split_nets'][ck]
            pos = sum(1 for v in vals if v > 0)
            asset_stats[sym][ck] = {
                'oos_net_sum': a['per_cost'][ck]['oos_net_sum'],
                'positive_splits': pos, 'n_splits': len(vals),
                'positive_share': (pos / len(vals) if vals else None),
                'min_split': min(vals) if vals else None,
                'max_split': max(vals) if vals else None,
            }

    diffs = {}
    matches = True
    for ck in COST_KEYS:
        reported = float(saved_cross.get(ck, 0.0)) if saved_cross else None
        recomputed = recomputed_cross[ck]
        d = (recomputed - reported) if reported is not None else None
        diffs[ck] = {'reported': reported, 'recomputed': recomputed, 'diff_recomputed_minus_reported': d, 'within_tolerance': (d is None or abs(d) < 1e-9)}
        if d is not None and abs(d) >= 1e-9:
            matches = False

    ok_assets = [s for s, a in assets.items() if a.get('status') == 'ok']
    fee0 = split_stats('fee0_slip0')
    all_pos_assets_fee0 = sum(1 for s in asset_stats.values() if s['fee0_slip0']['oos_net_sum'] > 0)
    out = {
        'generated_at_utc': ts, 'campaign': 275,
        'analysis': 'split_asset_decomposition_and_replication',
        'strategy_id': 'VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_MEDCOUPLE_SHOCK_MR',
        'source_c275_oos': str(saved_path.relative_to(root)) if saved_path else None,
        'source_c275_oos_sha256': sha256_file(saved_path) if saved_path else None,
        'replication_matches_c275_oos': matches,
        'replication_diffs_recomputed_minus_reported': diffs,
        'c275_reported_cross_asset_oos_net_sums': saved_cross,
        'recomputed_cross_asset_oos_net_sums': recomputed_cross,
        'spec': {'W_RR': W_RR, 'ALB': 336, 'm': M_EMB, 'tau': TAU, 'eps_scale': EPS_SCALE, 'w_min': W_MIN,
                 'entry_z': ENTRY_Z, 'exit_z': EXIT_Z, 'max_hold': MAX_HOLD, 'train': TRAIN, 'test': TEST, 'step': STEP,
                 'cost_grid_bps': COST_GRID},
        'data_sources': {
            'spot_cache': str(SPOT_CACHE.relative_to(root)), 'spot_cache_sha256': sha256_file(SPOT_CACHE),
            'volume_meta': str(VOL_META.relative_to(root)), 'volume_meta_sha256': sha256_file(VOL_META),
            'volume_provenance': str(VOL_PROV.relative_to(root)), 'volume_provenance_sha256': sha256_file(VOL_PROV),
        },
        'ok_asset_count': len(ok_assets), 'n_splits_per_asset': n_splits_global,
        'common_assets': common,
        'cross_asset_per_split': per_split_cross_list,
        'cross_asset_split_stats': {ck: split_stats(ck) for ck in COST_KEYS},
        'per_asset_split_stats': asset_stats,
        'per_asset': assets,
        'volume_validation': vol_report,
        'stability_assessment': {
            'fee0_positive_split_share': fee0['positive_share'],
            'fee0_positive_splits': fee0['positive'],
            'fee0_total_splits': fee0['count'],
            'assets_positive_net_fee0': all_pos_assets_fee0,
            'assets_total_ok': len(ok_assets),
            'cross_asset_positive_all_cost_slices_recomputed': all(recomputed_cross[ck] > 0 for ck in COST_KEYS),
            'note': 'Computed from deterministic replication on real cached data only; no refetch/synthetic.',
        },
    }
    op = reports / f'campaign275_split_decomposition_{ts}.json'
    op.write_text(json.dumps(out, indent=2, default=str) + '\n')
    print(json.dumps({
        'artifact': str(op.relative_to(root)), 'sha256': sha256_file(op),
        'replication_matches_c275_oos': matches, 'diffs': diffs,
        'recomputed_cross': recomputed_cross,
        'stability_assessment': out['stability_assessment'],
    }, indent=2))

if __name__ == '__main__':
    main()
