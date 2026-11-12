#!/usr/bin/env python3
"""C275 parameter-perturbation sensitivity on real cached data only (MEDCOUPLE).
Pre-stated bounded grid around baseline: W_RR {144,168,192}, ENTRY_Z {1.25,1.5,1.75},
EXIT_Z {0.25,0.5,0.75} with EXIT_Z<ENTRY_Z; ALB fixed 336; other params fixed.
Same WF/costs/caches as C275 baseline."""
from __future__ import annotations
import hashlib, json, pickle, sys
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
from scripts.run_c275_rte_over_white_diag_medcouple_shock_mr_costed_oos import (  # noqa: E402
    trading_signals, net_pnl, compute_feature_series as compute_feature_base,
    M_EMB, TAU, EPS_SCALE, W_MIN, MAX_HOLD,
    TRAIN, TEST, STEP, COST_GRID, SPOT_CACHE, VOL_META, VOL_PROV,
)
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
    with open(SPOT_CACHE, 'rb') as f:
        df = pickle.load(f)
    return df

def load_volume():
    from data.real_feed_loader import validate_and_load_real_feed  # noqa: E402
    prov = json.loads(VOL_PROV.read_text()) if VOL_PROV.exists() else {}
    df, report = validate_and_load_real_feed(VOL_META, 'real_quote_volume', provenance=prov)
    df = df.pivot_table(index='timestamp_utc', columns='symbol', values='quote_volume_usdt', aggfunc='first').sort_index()
    return df, report

# recompute feature with variable W_RR
from scripts.run_c275_rte_over_white_diag_medcouple_shock_mr_costed_oos import white_diag_segment_lengths, medcouple

def compute_feature_series_w(log_vol, w_rr):
    T = len(log_vol)
    feat = np.full(T, np.nan, dtype=float)
    r_all = np.diff(log_vol)
    n_emb = w_rr - (M_EMB - 1) * TAU
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
        mc = medcouple(arr)
        if mc is None or not np.isfinite(mc) or mc == 0.0:
            continue
        bsegs = []
        nrec = rec.shape[0]
        for k in range(-(nrec - 1), nrec):
            if k == 0:
                continue
            diag = np.diag(rec, k=k); count = 0
            for v in diag:
                if v != 0:
                    count += 1
                else:
                    if count >= 1:
                        bsegs.append(count)
                    count = 0
            if count >= 1:
                bsegs.append(count)
        if not bsegs:
            continue
        b = np.asarray(bsegs, dtype=float)
        total = float(np.sum(b))
        if total <= 0:
            continue
        p = b / total
        p = p[p > 0]
        rte = float(-np.sum(p * np.log(p)))
        if not np.isfinite(rte):
            continue
        ratio = rte / mc
        if np.isfinite(ratio):
            feat[i] = ratio
    return feat

def wf_eval(close, feat, entry_z, exit_z):
    T = len(close); oos_net = []; bh_oos = []; splits = 0; idx = 0; exposures = []
    pos_full = trading_signals(feat, entry_z, exit_z, MAX_HOLD)
    for fee, slip in COST_GRID:
        pass
    # compute per cost
    results = {}
    for fee, slip in COST_GRID:
        net = net_pnl(pos_full, close, fee, slip)
        oos = []; bh = []; idx = 0
        while idx + TRAIN + TEST <= T:
            te_s = idx + TRAIN; te_e = te_s + TEST
            end = min(te_e - 1, len(net))
            if end > te_s:
                oos.extend(net[te_s:end].tolist())
            if te_e <= T:
                bh.extend((close[te_s + 1:te_e] / close[te_s:te_e - 1] - 1.0).tolist())
            idx += STEP
        k = f'fee{fee}_slip{slip}'
        results[k] = {'oos_net_sum': float(np.sum(oos)) if oos else 0.0, 'oos_net_mean': float(np.mean(oos)) if oos else 0.0, 'bh_oos_mean': float(np.mean(bh)) if bh else 0.0}
    idx = 0
    while idx + TRAIN + TEST <= T:
        te_s = idx + TRAIN; te_e = te_s + TEST
        exposures.append(float(np.mean(np.abs(pos_full[te_s:te_e]) > 0)) if te_e <= T else 0.0)
        splits += 1; idx += STEP
    return results, any(e > 0 for e in exposures), splits

def main():
    spot_df = load_spot()
    vol_df, vol_report = load_volume()
    common = sorted(set(spot_df.columns).intersection(set(vol_df.columns)))
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
    saved_baseline_cross = saved_oos.get('cross_asset', {}).get('oos_net_sums', {}) if saved_oos else {}

    sym_to_idx = {s: i for i, s in enumerate(common)}
    feats_by_w = {w: {} for w in WRR_GRID}
    for sym in common:
        i = sym_to_idx[sym]
        for w in WRR_GRID:
            feats_by_w[w][sym] = compute_feature_series_w(log_vol[:, i], w)
        print(f'feat {sym}', flush=True)

    combos = []
    for w in WRR_GRID:
        for ez in ENTRY_GRID:
            for xz in EXIT_GRID:
                if xz >= ez: continue
                combos.append({'W_RR': w, 'ENTRY_Z': ez, 'EXIT_Z': xz})

    grid_results = []
    edge_positive_count = 0
    for combo in combos:
        w = combo['W_RR']; ez = combo['ENTRY_Z']; xz = combo['EXIT_Z']
        cross = {k: 0.0 for k in COST_KEYS}
        any_exp = False
        strat_ms = []; bh_ms = []
        ok = 0
        for sym in common:
            c = close[:, sym_to_idx[sym]]
            feat = feats_by_w[w][sym]
            per_cost, any_e, _ = wf_eval(c, feat, ez, xz)
            ok += 1
            if any_e: any_exp = True
            # use fee0 mean for bh comparison consistency (means same across costs? bh is same)
            for ck in COST_KEYS:
                cross[ck] += per_cost[ck]['oos_net_sum']
            # collect means for beat-bh rule as cross-asset mean of per-asset mean_oos_net vs mean_bh
            strat_ms.append(per_cost['fee0_slip0']['oos_net_mean'])
            bh_ms.append(per_cost['fee0_slip0']['bh_oos_mean'])
        all_pos = all(v > 0 for v in cross.values())
        # recompute beat_bh properly per cost slice mean
        beat_bh = True
        for ck in COST_KEYS:
            sm = []; bm = []
            for sym in common:
                c = close[:, sym_to_idx[sym]]; feat = feats_by_w[w][sym]
                per_cost, _, _ = wf_eval(c, feat, ez, xz)
                sm.append(per_cost[ck]['oos_net_mean']); bm.append(per_cost[ck]['bh_oos_mean'])
            if not (np.nanmean(sm) > np.nanmean(bm)): beat_bh = False
        edge = bool(any_exp and all_pos and beat_bh)
        if edge: edge_positive_count += 1
        is_baseline = (w == BASELINE['W_RR'] and ez == BASELINE['ENTRY_Z'] and xz == BASELINE['EXIT_Z'])
        diffs = None; baseline_match = None
        if saved_baseline_cross and is_baseline:
            diffs = {ck: cross[ck] - float(saved_baseline_cross.get(ck, 0.0)) for ck in COST_KEYS}
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
        'generated_at_utc': ts, 'campaign': 275,
        'analysis': 'parameter_perturbation_sensitivity',
        'strategy_id': 'VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_MEDCOUPLE_SHOCK_MR',
        'source_c275_oos': str(saved_path.relative_to(root)) if saved_path else None,
        'source_c275_oos_sha256': sha256_file(saved_path) if saved_path else None,
        'baseline_cross_asset_oos_net_sums': saved_baseline_cross,
        'grid_spec': {
            'W_RR': WRR_GRID, 'ENTRY_Z': ENTRY_GRID, 'EXIT_Z': EXIT_GRID,
            'constraint': 'EXIT_Z < ENTRY_Z',
            'fixed': {'ALB': ALB, 'm': M_EMB, 'tau': TAU, 'eps_scale': EPS_SCALE, 'w_min': W_MIN,
                      'MAX_HOLD': MAX_HOLD, 'TRAIN': TRAIN, 'TEST': TEST, 'STEP': STEP, 'cost_grid_bps': COST_GRID},
            'rationale': 'Bounded local perturbations around C275 baseline on identical real cached data/WF/cost framework; ALB fixed at 336.',
        },
        'total_combos': total,
        'edge_positive_combos': edge_positive_count,
        'edge_positive_share': share,
        'combos_all_cost_slices_positive': all_pos_any,
        'baseline_reproduced_in_grid': bool(baseline_res and baseline_res.get('baseline_matches_saved_oos')),
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
    op = reports / f'campaign275_param_sensitivity_{ts}.json'
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
