#!/usr/bin/env python3
"""Campaign #23 Path R (fail-closed, real data only): real_quote_volume-conditioned
strategy on real Binance spot quote volume (klines column 5) + real cached spot 1h.

PRE-STATED HYPOTHESIS (fixed before seeing OOS results): "Abnormal Quote Volume Momentum"
- For each asset, compute causal rolling z-score of quote_volume_usdt (lookback ZVOL=168h).
- Entry (abnormal volume surge): when vol_z > ENTRY_Z (1.5), take momentum direction of
  recent RET_LOOKBACK (24h) return: long if ret24 > 0, short if ret24 < 0.
- Exit: when vol_z < EXIT_Z (0.5) OR hold >= MAX_HOLD (24h) OR signal flips direction.
- Else flat. Execution shift t -> t+1 (signal on bar close, trade next bar).
- Walk-forward: rolling 720/168/168 (train/test/step). Cost grid: fee+slip bps pairs
  [[0,0],[5,0],[0,5],[5,5],[10,0],[0,10],[10,10],[20,0],[0,20],[20,20]] (0-40bps).
- Benchmark: buy-and-hold per asset (gross, no recurring turnover) on union of OOS WF windows.
- Pre-stated edge rule (fail-closed): oos_edge_proven=true IFF executed exposure>0 AND for
  ALL cost-grid slices OOS net sum > 0 AND OOS net sum > B&H OOS sum on same OOS windows.
  Else false. No in-sample tuning, no threshold weakening, no fabricated data/proxies.
"""
import json, os, pickle, hashlib
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
import pandas as pd

root = Path(__file__).resolve().parent
cache_dir = root / 'data' / 'cache'
reports = root / 'reports'
reports.mkdir(exist_ok=True)
ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')

SPOT_CACHE = '0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7'
VOL_META = cache_dir / 'volume_1h_full.meta.json'
COST_GRID = [[0,0],[5,0],[0,5],[5,5],[10,0],[0,10],[10,10],[20,0],[0,20],[20,20]]
TRAIN, TEST, STEP = 720, 168, 168
PARAMS = {
    'zvol_lookback': 168,
    'ret_lookback': 24,
    'entry_z': 1.5,
    'exit_z': 0.5,
    'max_hold_bars': 24,
    'min_vol_obs': 168,
}
NAMED = ['BTC','ETH','SOL','BNB']


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def wf_windows(n):
    ws = []; st = 0
    while st + TRAIN + TEST <= n:
        ws.append((st, st + TRAIN, st + TRAIN + TEST)); st += STEP
    return ws


def load_spot():
    pkl = cache_dir / f'{SPOT_CACHE}.pkl'
    meta = json.loads((cache_dir / f'{SPOT_CACHE}.meta.json').read_text())
    df = pickle.load(open(pkl, 'rb'))
    return df, meta, sha256_file(pkl)


def load_volume():
    from data.real_feed_loader import validate_and_load_real_feed
    prov = json.loads((cache_dir / 'volume_1h_full.provenance.json').read_text())
    df, report = validate_and_load_real_feed(VOL_META, 'real_quote_volume', provenance=prov)
    return df, report


def run_asset(prices: pd.Series, vol: pd.Series):
    # align on common index, forward-fill not used (inner align) to avoid fabrication
    idx = prices.index.intersection(vol.index)
    p = prices.reindex(idx).astype(float)
    v = pd.to_numeric(vol.reindex(idx), errors='coerce')
    mask = p.notna() & v.notna() & (v > 0)
    p = p[mask]; v = v[mask]
    n = len(p)
    ret = p.pct_change().fillna(0.0).values
    vv = v.values.astype(float)
    # causal rolling vol z-score (use past window excluding current? include up to t for signal at t)
    vmean = pd.Series(vv).rolling(PARAMS['zvol_lookback'], min_periods=PARAMS['min_vol_obs']).mean().values
    vstd = pd.Series(vv).rolling(PARAMS['zvol_lookback'], min_periods=PARAMS['min_vol_obs']).std(ddof=0).values
    with np.errstate(divide='ignore', invalid='ignore'):
        volz = np.where((vstd > 1e-18) & np.isfinite(vstd), (vv - vmean) / vstd, np.nan)
    retN = pd.Series(p.values).pct_change(PARAMS['ret_lookback']).values
    # signal generation (causal, uses info up to t)
    sig = np.zeros(n)
    cur = 0.0; hold = 0
    warm = max(PARAMS['zvol_lookback'], PARAMS['ret_lookback']) + 2
    for i in range(warm, n):
        vz = volz[i]; rN = retN[i]
        if not np.isfinite(vz) or not np.isfinite(rN):
            nxt = cur; hold = hold + 1 if cur != 0 else 0
        else:
            desired = 0.0
            if vz > PARAMS['entry_z']:
                if rN > 0: desired = 1.0
                elif rN < 0: desired = -1.0
            if cur == 0.0:
                nxt = desired; hold = 0 if desired == 0 else 1
            else:
                hold += 1
                exit_cond = (vz < PARAMS['exit_z']) or (hold >= PARAMS['max_hold_bars']) or (desired != 0 and desired != cur)
                if exit_cond:
                    nxt = desired if (desired != 0 and desired != cur) else 0.0
                    hold = 0 if nxt == 0 else 1
                else:
                    nxt = cur
        cur = nxt
        if i + 1 < n:
            sig[i + 1] = cur  # execution shift
    gross = sig * ret
    turn = np.abs(np.diff(np.r_[0.0, sig]))
    ws = wf_windows(n)
    oos_union = np.zeros(n, dtype=bool)
    for _, tr_e, te_e in ws:
        oos_union[tr_e:te_e] = True
    bh_oos = float(np.nansum(ret[oos_union])) if oos_union.sum() else 0.0
    bh_is = float(np.nansum(ret[~oos_union]))
    has_exp = bool((np.abs(sig) > 0).sum() > 0)
    slices = {}
    for fee, slip in COST_GRID:
        cr = (fee + slip) / 10000.0
        net = gross - turn * cr
        oos_sum = float(np.nansum(net[oos_union]))
        is_sum = float(np.nansum(net[~oos_union]))
        slices[f'fee{fee}_slip{slip}_bps'] = {
            'oos_net_sum': oos_sum, 'is_net_sum': is_sum, 'bh_oos_sum': bh_oos,
            'oos_net_gt_zero': oos_sum > 0, 'oos_net_beat_bh': oos_sum > bh_oos,
            'total_turnover': float(np.nansum(turn)),
        }
    edge = bool(has_exp and all(
        slices[f'fee{f}_slip{s}_bps']['oos_net_gt_zero'] and slices[f'fee{f}_slip{s}_bps']['oos_net_beat_bh']
        for f, s in COST_GRID))
    return {
        'n_bars': n, 'window_start': str(idx[0]) if n else None, 'window_end': str(idx[-1]) if n else None,
        'n_wf_folds': len(ws), 'has_exposure': has_exp,
        'n_active_bars': int((np.abs(sig) > 0).sum()),
        'exposure_frac': float((np.abs(sig) > 0).mean()) if n else 0.0,
        'bh_oos_sum': bh_oos, 'bh_is_sum': bh_is,
        'cost_slices': slices, 'oos_edge_proven': edge,
    }


def main():
    spot, spot_meta, spot_sha = load_spot()
    vol_df, vol_report = load_volume()
    # pivot volume long -> wide by symbol
    vol_wide = vol_df.pivot_table(index='timestamp_utc', columns='symbol', values='quote_volume_usdt', aggfunc='first').sort_index()
    # ensure tz-aware UTC alignment
    if spot.index.tz is None:
        spot.index = spot.index.tz_localize('UTC')
    if vol_wide.index.tz is None:
        vol_wide.index = vol_wide.index.tz_localize('UTC')
    assets = [a for a in spot.columns if a in vol_wide.columns]
    by_asset = {}
    for a in assets:
        by_asset[a] = run_asset(spot[a], vol_wide[a])
    n_edge = sum(1 for v in by_asset.values() if v['oos_edge_proven'])
    n_all_pos = sum(1 for v in by_asset.values() if all(v['cost_slices'][f"fee{f}_slip{s}_bps"]['oos_net_gt_zero'] for f,s in COST_GRID))
    n_all_bh = sum(1 for v in by_asset.values() if all(v['cost_slices'][f"fee{f}_slip{s}_bps"]['oos_net_beat_bh'] for f,s in COST_GRID))
    report = {
        'report': 'real_quote_volume_abnormal_momentum_costed_oos',
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'campaign': 23,
        'path': 'R',
        'family': 'real_quote_volume',
        'mandate': 'Campaign #23 Path R — pre-stated costed OOS test of Abnormal Quote Volume Momentum using real Binance spot quote volume (klines col 5) with verifiable provenance. Fail-closed, real data only, no fabrication, no proxies labeled real, no threshold weakening.',
        'provenance': {
            'real_data_only': True, 'fabricated_data': False, 'fail_closed': True,
            'no_threshold_weakening': True, 'no_proxies_labeled_real': True,
            'new_external_feeds_ingested_this_session': False,
            'feed_present_and_validated_fail_closed': True,
            'spot_cache': {'path': f'data/cache/{SPOT_CACHE}.pkl', 'sha256': spot_sha, 'bars': int(len(spot)), 'assets': list(spot.columns)},
            'volume_feed': {
                'meta': 'data/cache/volume_1h_full.meta.json',
                'pkl': 'data/cache/volume_1h_full.pkl',
                'provenance_cert': 'data/cache/volume_1h_full.provenance.json',
                'validation': {k: vol_report.get(k) for k in ['ok','refused','reason','rows','family_spec','multi_symbol_long_frame','provenance_merged']},
                'source_provider': 'www.binance.com public klines endpoint (column 5 quote asset volume)',
                'real_data_only': True, 'fabricated_data': False,
            },
            'intersection_assets_tested': assets,
        },
        'pre_stated_hypothesis': {
            'name': 'Abnormal Quote Volume Momentum',
            'description': 'Causal rolling z-score of real quote_volume_usdt; abnormal volume (z>1.5) triggers momentum direction from 24h return; exit on vol normalization, max hold, or direction flip. Execution shifted t->t+1.',
            'params': PARAMS,
            'params_fixed_before_oos_evaluation': True,
            'no_in_sample_tuning': True,
        },
        'config': {
            'assets': assets, 'n_assets': len(assets),
            'cost_grid_bps_fee_slippage': COST_GRID,
            'walk_forward': {'mode': 'rolling', 'train_bars': TRAIN, 'test_bars': TEST, 'step_bars': STEP},
            'benchmark': 'buy-and-hold per asset (gross, no recurring turnover) on union of OOS WF windows; strategy net of fee+slippage on turnover',
            'pre_stated_oos_edge_proven_rule': 'oos_edge_proven=true IFF executed exposure>0 AND for ALL cost-grid slices OOS net sum > 0 AND OOS net sum > B&H OOS sum on same OOS windows. Else false (fail-closed).',
            'explicitly_reported': NAMED,
        },
        'by_asset': by_asset,
        'aggregate': {
            'n_assets': len(by_asset), 'n_oos_edge_proven': n_edge,
            'aggregate_oos_edge_proven_fail_closed': bool(n_edge > 0 and n_edge == len(by_asset)),
            'n_assets_all_slices_oos_net_positive': n_all_pos,
            'n_assets_all_slices_beat_benchmark': n_all_bh,
            'per_named': {sym: {
                'oos_edge_proven': by_asset[sym]['oos_edge_proven'], 'has_exposure': by_asset[sym]['has_exposure'],
                'bh_oos_sum': by_asset[sym]['bh_oos_sum'],
                'oos_0bps_sum': by_asset[sym]['cost_slices']['fee0_slip0_bps']['oos_net_sum'],
                'oos_40bps_sum': by_asset[sym]['cost_slices']['fee20_slip20_bps']['oos_net_sum'],
                'all_slices_beat_bh': all(by_asset[sym]['cost_slices'][f"fee{f}_slip{sl}_bps"]['oos_net_beat_bh'] for f,sl in COST_GRID),
            } for sym in NAMED if sym in by_asset},
        },
        'honest_assessment': (
            f"PROVEN NET-OF-COST OOS EDGE (fail-closed rule met) for {n_edge}/{len(by_asset)} assets." if n_edge > 0
            else "NO PROVEN NET-OF-COST OOS EDGE. oos_edge_proven=false for all tested assets under pre-stated fail-closed rule."
        ),
    }
    out = reports / f'real_quote_volume_abnormal_momentum_costed_oos_{ts}.json'
    out.write_text(json.dumps(report, indent=2, default=str), encoding='utf-8')
    print(out)
    print('n_edge', n_edge, 'n_assets', len(by_asset), 'named', report['aggregate']['per_named'])
    # emit sha256 for artifact
    print('sha256', sha256_file(out))

if __name__ == '__main__':
    main()
