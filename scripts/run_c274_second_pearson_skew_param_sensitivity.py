#!/usr/bin/env python3
"""C274 parameter-perturbation sensitivity on real cached data only.
Pre-stated bounded grid around baseline: W_RR {144,168,192}, ENTRY_Z {1.25,1.5,1.75},
EXIT_Z {0.25,0.5,0.75} with EXIT_Z<ENTRY_Z; ALB fixed 336; other params fixed.
Same WF/costs/caches as C274 baseline. Reports edge-positive share and failing-combo details."""
from __future__ import annotations
import hashlib, json, pickle, sys, itertools
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
from scripts.run_c274_second_pearson_skew_oos_fast import (  # noqa: E402
    trading_signals, net_pnl,
    M_EMB, TAU, EPS_SCALE, W_MIN, MAX_HOLD,
    TRAIN, TEST, STEP, COST_GRID, SPOT_CACHE, VOL_META, VOL_PROV,
)
cache_dir = root / 'data' / 'cache'
reports = root / 'reports'
reports.mkdir(exist_ok=True)
ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
COST_KEYS = [f'fee{f}_slip{s}' for f, s in COST_GRID]
ALB = 336
WRR_GRID = [144, 168, 192]
ENTRY_GRID = [1.25, 1.5, 1.75]
EXIT_GRID = [0.25, 0.5, 0.75]
BASELINE = {'W_RR': 168, 'ENTRY_Z': 1.5, 'EXIT_Z': 0.5}

def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def load_spot():
    import pandas as pd
    with open(SPOT_CACHE, 'rb') as f:
        df = pickle.load(f)
    if isinstance(df, pd.Series):
        df = df.to_frame()
    return df

def load_volume():
    from data.real_feed_loader import validate_and_load_real_feed  # noqa: E402
    prov = json.loads(VOL_PROV.read_text()) if VOL_PROV.exists() else {}
    df, report = validate_and_load_real_feed(VOL_META, 'real_quote_volume', provenance=prov)
    df = df.pivot_table(index='timestamp_utc', columns='symbol', values='quote_volume_usdt', aggfunc='first').sort_index()
    return df, report

def compute_feature_series(log_vol: np.ndarray, w_rr: int):
    from scripts._vec_rqa import white_diag_segment_lengths  # noqa: E402
    T = len(log_vol)
    feat = np.full(T, np.nan, dtype=float)
    r_all = np.diff(log_vol)
    n_emb = w_rr - (M_EMB - 1) * TAU
    if n_emb < 3:
        return feat
    for i in range(w_rr, T):
        r_win = r_all[i - w_rr:i]
        if r_win.shape[0] != w_rr or not np.all(np.isfinite(r_win)):
            continue
        sd = float(np.std(r_win, ddof=0))
        if not np.isfinite(sd) or sd <= 0:
            continue
        eps = EPS_SCALE * sd
        X = np.column_stack([r_win[j:j + n_emb] for j in range(M_EMB)])
        d_inf = np.max(np.abs(X[:, None, :] - X[None, :, :]), axis=2)
        rec = (d_inf <= eps)
        segs = white_diag_segment_lengths(rec.astype(np.uint8), W_MIN)
        if len(segs) < 3:
            continue
        arr = np.asarray(segs, dtype=float)
        mean_l = float(np.mean(arr)); med_l = float(np.median(arr)); std_l = float(np.std(arr, ddof=0))
        if not np.isfinite(std_l) or std_l <= 0:
            continue
        skew = 3.0 * (mean_l - med_l) / std_l
        if np.isfinite(skew):
            feat[i] = skew
    return feat

import numpy as np  # noqa: E402

def walk_forward_splits(n: int):
    out = []
    i = 0
    while i + TRAIN + TEST <= n:
        out.append((i, i + TRAIN, i + TRAIN + TEST))
        i += STEP
    return out

def eval_asset(c, feat, entry_z, exit_z):
    T = len(c)
    splits = walk_forward_splits(T)
    pos_full = trading_signals(feat, entry_z, exit_z, MAX_HOLD)
    ret = np.zeros(T, dtype=float); ret[1:] = c[1:] / c[:-1] - 1.0
    any_exp = False
    cross = {k: 0.0 for k in COST_KEYS}
    split_nets = {k: [] for k in COST_KEYS}
    bh_split_nets = {k: [] for k in COST_KEYS}
    strat_means = []; bh_means = []
    oos_mask = np.zeros(T, dtype=bool)
    for (_, tr_e, te_e) in splits:
        oos_mask[tr_e:te_e] = True
    for fee, slip in COST_GRID:
        ck = f'fee{fee}_slip{slip}'
        gross = pos_full[:-1] * ret[1:]
        dpos = np.diff(np.concatenate([[0], pos_full]))
        cost = np.abs(dpos[1:]) * (fee + slip) / 10000.0
        net = gross - cost
        bh = c[1:] / c[:-1] - 1.0
        for si, (s0, tr_e, te_e) in enumerate(splits):
            end = min(te_e - 1, T)
            seg = net[s0:end] if end > s0 else np.array([])
            bh_seg = c[tr_e + 1:te_e] / c[tr_e:te_e - 1] - 1.0 if te_e <= T else np.array([])
            split_nets[ck].append(float(np.sum(seg)) if seg.size else 0.0)
            bh_split_nets[ck].append(float(np.sum(bh_seg)) if bh_seg.size else 0.0)
            cross[ck] += float(np.sum(seg)) if seg.size else 0.0
            strat_means.append(float(np.mean(seg)) if seg.size else np.nan)
            bh_means.append(float(np.mean(bh_seg)) if bh_seg.size else np.nan)
        if any(float(np.mean(np.abs(pos_full[s0:te_e]) > 0)) > 0 for s0, _tr_e, te_e in splits if te_e <= T):
            any_exp = True
    strat_mean_oos = float(np.mean([s for s in strat_means if not np.isnan(s)])) if strat_means else np.nan
    bh_mean_oos = float(np.mean([s for s in bh_means if not np.isnan(s)])) if bh_means else np.nan
    return {
        'cross_asset_oos_net_sums': cross, 'split_nets': split_nets, 'bh_split_nets': bh_split_nets,
        'any_exposure': any_exp, 'strat_mean_oos': strat_mean_oos, 'bh_mean_oos': bh_mean_oos,
        'n_splits': len(splits),
    }

def main():
    spot_df = load_spot()
    vol_df, vol_report = load_volume()
    common = sorted(set(spot_df.columns).intersection(set(vol_df.columns)))
    if not common:
        raise SystemExit('NO_COMMON_ASSETS')
    spot = spot_df[common].sort_index(); vol = vol_df[common].sort_index()
    common_idx = spot.index.intersection(vol.index)
    spot = spot.loc[common_idx]; vol = vol.loc[common_idx]
    close = spot.ffill().bfill().to_numpy(dtype=float)
    log_vol = np.log(np.clip(vol.ffill().bfill().to_numpy(dtype=float), 1e-12, None))

    saved_oos = None
    for cand in sorted(reports.glob('real_quote_volume_rqa_rte_over_white_diag_line_length_second_pearson_skew_shock_mr_costed_oos_*.json')):
        saved_path = cand
    saved_oos = json.loads(saved_path.read_text()) if saved_path else None
    saved_baseline_cross = saved_oos.get('cross_asset', {}).get('oos_net_sums', {}) if saved_oos else None

    # precompute features per (sym, w_rr)
    sym_to_idx = {s: i for i, s in enumerate(common)}
    per_sym = {}
    for sym in common:
        i = sym_to_idx[sym]
        c = close[:, i]
        lv = log_vol[:, i]
        per_sym[sym] = {'c': c, 'feats': {w: compute_feature_series(lv, w) for w in WRR_GRID}}

    combos = []
    for w in WRR_GRID:
        for ez in ENTRY_GRID:
            for xz in EXIT_GRID:
                if xz >= ez:
                    continue
                combos.append({'W_RR': w, 'ENTRY_Z': ez, 'EXIT_Z': xz})

    grid_results = []
    edge_positive_count = 0
    for combo in combos:
        w = combo['W_RR']; ez = combo['ENTRY_Z']; xz = combo['EXIT_Z']
        cross = {k: 0.0 for k in COST_KEYS}
        any_exp = False
        strat_ms = []; bh_ms = []
        ok = 0
        per_asset_results = {}
        for sym in common:
            c = per_sym[sym]['c']; feat = per_sym[sym]['feats'][w]
            res = eval_asset(c, feat, ez, xz)
            if res is None:
                continue
            ok += 1
            per_asset_results[sym] = res
            if res['any_exposure']:
                any_exp = True
            strat_ms.append(res['strat_mean_oos']); bh_ms.append(res['bh_mean_oos'])
            for ck in COST_KEYS:
                cross[ck] += res['cross_asset_oos_net_sums'][ck]
        all_pos = all(v > 0 for v in cross.values())
        beat_bh = (np.nanmean(strat_ms) > np.nanmean(bh_ms)) if strat_ms and bh_ms else False
        edge = bool(any_exp and all_pos and beat_bh)
        if edge:
            edge_positive_count += 1
        is_baseline = (w == BASELINE['W_RR'] and ez == BASELINE['ENTRY_Z'] and xz == BASELINE['EXIT_Z'])
        diffs = None
        baseline_match = None
        if saved_baseline_cross and is_baseline:
            diffs = {ck: cross[ck] - float(saved_baseline_cross[ck]) for ck in COST_KEYS}
            baseline_match = all(abs(d) < 1e-9 for d in diffs.values())
        grid_results.append({
            'params': combo, 'is_baseline': is_baseline,
            'cross_asset_oos_net_sums': cross,
            'oos_edge_proven': edge, 'any_exposure_oos': any_exp,
            'all_cost_slices_positive_oos_net_sum': all_pos,
            'all_cost_slices_beat_bh_mean_rule': bool(beat_bh),
            'ok_assets': ok,
            'baseline_diff_vs_saved_oos': diffs,
            'baseline_matches_saved_oos': baseline_match,
            'per_asset': {sym: {'cross_asset_oos_net_sums': r['cross_asset_oos_net_sums'],
                                'any_exposure': r['any_exposure'],
                                'strat_mean_oos': r['strat_mean_oos'], 'bh_mean_oos': r['bh_mean_oos']}
                          for sym, r in per_asset_results.items()},
        })
    total = len(grid_results)
    all_pos_any = sum(1 for r in grid_results if r['all_cost_slices_positive_oos_net_sum'])
    share = edge_positive_count / total if total else 0
    baseline_res = next((r for r in grid_results if r['is_baseline']), None)
    if share >= 0.7 and edge_positive_count >= 1:
        assessment = 'robust_neighborhood'
    elif share >= 0.4:
        assessment = 'moderately_sensitive'
    else:
        assessment = 'fragile_to_params'
    fails = [r for r in grid_results if not r['oos_edge_proven']]
    out = {
        'generated_at_utc': ts, 'campaign': 274,
        'analysis': 'parameter_perturbation_sensitivity',
        'strategy_id': 'VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_SECOND_PEARSON_SKEW_SHOCK_MR',
        'source_c274_oos': str(saved_path.relative_to(root)) if saved_path else None,
        'source_c274_oos_sha256': sha256_file(saved_path) if saved_path else None,
        'baseline_cross_asset_oos_net_sums': saved_baseline_cross,
        'grid_spec': {
            'W_RR': WRR_GRID, 'ENTRY_Z': ENTRY_GRID, 'EXIT_Z': EXIT_GRID,
            'constraint': 'EXIT_Z < ENTRY_Z',
            'fixed': {'ALB': ALB, 'm': M_EMB, 'tau': TAU, 'eps_scale': EPS_SCALE, 'w_min': W_MIN,
                      'MAX_HOLD': MAX_HOLD, 'TRAIN': TRAIN, 'TEST': TEST, 'STEP': STEP, 'cost_grid_bps': COST_GRID},
            'rationale': 'Bounded local perturbations around C274 baseline to assess edge stability over window length and z-thresholds on identical real cached data/WF/cost framework; ALB fixed at 336.',
        },
        'total_combos': total,
        'edge_positive_combos': edge_positive_count,
        'edge_positive_share': share,
        'combos_all_cost_slices_positive': all_pos_any,
        'baseline_reproduced_in_grid': bool(baseline_res and baseline_res['baseline_matches_saved_oos']),
        'baseline_grid_result': baseline_res,
        'sensitivity_assessment': assessment,
        'failing_combos_count': len(fails),
        'failing_combos_summary': [
            {'params': r['params'],
             'cross_asset_oos_net_sums': r['cross_asset_oos_net_sums'],
             'any_exposure_oos': r['any_exposure_oos'],
             'all_cost_slices_positive_oos_net_sum': r['all_cost_slices_positive_oos_net_sum'],
             'all_cost_slices_beat_bh_mean_rule': r['all_cost_slices_beat_bh_mean_rule']}
            for r in fails
        ],
        'grid_results': grid_results,
        'volume_validation': vol_report,
        'provenance': {'real_data_only': True, 'network_refetch': False, 'synthetic_data': False,
                       'caches': {'spot': str(SPOT_CACHE.relative_to(root)), 'spot_sha256': sha256_file(SPOT_CACHE)}},
    }
    op = reports / f'campaign274_param_sensitivity_{ts}.json'
    op.write_text(json.dumps(out, indent=2, default=str) + '\n')
    print(json.dumps({
        'artifact': str(op.relative_to(root)), 'sha256': sha256_file(op),
        'total_combos': total, 'edge_positive_combos': edge_positive_count,
        'edge_positive_share': share, 'combos_all_cost_slices_positive': all_pos_any,
        'baseline_reproduced_in_grid': out['baseline_reproduced_in_grid'],
        'sensitivity_assessment': assessment, 'failing_combos_count': len(fails),
    }, indent=2))

if __name__ == '__main__':
    main()
