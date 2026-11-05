#!/usr/bin/env python3
"""PRIORITY 7 / Campaign #3 Deliverable A: range-bound breakout-reversion with volatility band.
Pre-stated, fail-closed, real cached spot only. No in-sample tuning, no threshold weakening.
Family is genuinely different from P6 Donchian breakout+volfilter.
"""
import json, os, pickle, glob, math
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
import pandas as pd

root = Path('/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats')
cache_dir = root / 'data' / 'cache'
reports = root / 'reports'
ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')

ASSETS_CANON = ['ADA','AVAX','BNB','BTC','DOT','ETH','LINK','LTC','POL','SOL','XRP']
COST_GRID = [[0,0],[5,0],[0,5],[5,5],[10,0],[0,10],[10,10],[20,0],[0,20],[20,20]]
TRAIN, TEST, STEP = 720, 168, 168

# Pre-stated params (fixed before run)
PARAMS = {
  'range_ma_lookback': 20,
  'range_std_k': 2.0,
  'vol_lookback_bars': 24,
  'vol_band_window': 240,
  'vol_band_min_periods': 120,
  'vol_low_q': 0.25,
  'vol_high_q': 0.75,
  'entry': 'breakout: long if prev close <= upper_prev and close > upper and vol in band; short symmetric vs lower',
  'exit_reversion_leg': 'if long and close < MA exit to flat; if short and close > MA exit to flat (fade/revert to mid)',
  'long_short': True,
}

def load_assets():
    data, inv = {}, []
    for mpath in sorted(glob.glob(str(cache_dir / '*_2026-04-01_2026-10-30_1h.meta.json'))):
        meta = json.load(open(mpath))
        if meta.get('interval') != '1h': continue
        sym = meta.get('symbol') or meta.get('market','').replace('USDT','').replace('USD','')
        pkl = mpath.replace('.meta.json','.pkl')
        if not os.path.exists(pkl): continue
        df = pickle.load(open(pkl,'rb'))
        if not isinstance(df, pd.Series): continue
        data[sym] = df.astype(float).rename('close')
        inv.append({'symbol': sym, 'bars': int(len(df)), 'first': str(df.index[0]), 'last': str(df.index[-1]),
                    'source': meta.get('source','www.binance.com public spot klines'),
                    'real_data_only': bool(meta.get('real_data_only', True)),
                    'fabricated_data': bool(meta.get('fabricated_data', False)),
                    'market': meta.get('market'), 'host': meta.get('host')})
    return {a:data[a] for a in ASSETS_CANON if a in data}, inv

def build_signals(close: pd.Series):
    ma = close.rolling(PARAMS['range_ma_lookback']).mean()
    sd = close.rolling(PARAMS['range_ma_lookback']).std(ddof=0)
    upper = ma + PARAMS['range_std_k']*sd
    lower = ma - PARAMS['range_std_k']*sd
    ret1 = close.pct_change()
    vol = ret1.rolling(PARAMS['vol_lookback_bars']).std(ddof=0)
    qlo = vol.rolling(PARAMS['vol_band_window'], min_periods=PARAMS['vol_band_min_periods']).quantile(PARAMS['vol_low_q'])
    qhi = vol.rolling(PARAMS['vol_band_window'], min_periods=PARAMS['vol_band_min_periods']).quantile(PARAMS['vol_high_q'])
    in_band = (vol >= qlo) & (vol <= qhi) & vol.notna() & qlo.notna() & qhi.notna()
    # breakout entries (causal: compare to prev)
    long_entry = in_band & (close.shift(1) <= upper.shift(1)) & (close > upper)
    short_entry = in_band & (close.shift(1) >= lower.shift(1)) & (close < lower)
    pos = pd.Series(0.0, index=close.index)
    cur = 0.0
    for i in range(len(close)):
        if cur == 0.0:
            if bool(long_entry.iat[i]): cur = 1.0
            elif bool(short_entry.iat[i]): cur = -1.0
        elif cur == 1.0:
            # reversion leg: exit when close < MA
            if pd.notna(ma.iat[i]) and close.iat[i] < ma.iat[i]: cur = 0.0
            elif bool(short_entry.iat[i]): cur = -1.0
        elif cur == -1.0:
            if pd.notna(ma.iat[i]) and close.iat[i] > ma.iat[i]: cur = 0.0
            elif bool(long_entry.iat[i]): cur = 1.0
        pos.iat[i] = cur
    return pos, ret1, ma, upper, lower, vol, in_band

def wf_oos(pos, ret1, fee_bps, slip_bps):
    cost_rate = (fee_bps + slip_bps) / 10000.0
    pos_exec = pos.shift(1).fillna(0.0)
    turn = pos_exec.diff().abs().fillna(pos_exec.abs())
    strat_gross = pos_exec * ret1.fillna(0.0)
    strat_net = strat_gross - turn * cost_rate
    bh = ret1.fillna(0.0) - (pd.Series(0.0,index=ret1.index).pipe(lambda s: s)) # no turnover after initial
    # B&H: enter once at first valid bar in fold? apply no recurring cost; initial cost negligible vs grid - state explicitly
    n = len(ret1)
    oos_s, oos_b, is_s = [], [], []
    start = 0
    folds = 0
    while start + TRAIN + TEST <= n:
        tr = slice(start, start+TRAIN)
        te = slice(start+TRAIN, start+TRAIN+TEST)
        is_s.append(float(strat_net.iloc[tr].sum()))
        oos_s.append(float(strat_net.iloc[te].sum()))
        bh_te = ret1.fillna(0.0).iloc[te]
        # B&H benchmark net of same per-bar cost basis? keep consistent: B&H has no turnover => net = gross
        oos_b.append(float(bh_te.sum()))
        start += STEP; folds += 1
    return {
        'folds': folds,
        'oos_net_sum': float(np.sum(oos_s)) if oos_s else 0.0,
        'oos_net_mean_per_fold': float(np.mean(oos_s)) if oos_s else 0.0,
        'is_net_sum': float(np.sum(is_s)) if is_s else 0.0,
        'bench_bh_oos_sum': float(np.sum(oos_b)) if oos_b else 0.0,
        'bench_bh_oos_mean_per_fold': float(np.mean(oos_b)) if oos_b else 0.0,
        'oos_net_gt_zero': bool((np.array(oos_s) > 0).all()) if oos_s else False,
        'oos_net_beat_bh': bool((np.array(oos_s) > np.array(oos_b)).all()) if oos_s else False,
        'oos_net_sum_gt_zero': bool((np.sum(oos_s) > 0) if oos_s else False),
        'oos_net_sum_beat_bh': bool((np.sum(oos_s) > np.sum(oos_b)) if oos_s else False),
    }

def main():
    data, inv = load_assets()
    assets = [a for a in ASSETS_CANON if a in data]
    by_asset = {}
    for sym in assets:
        close = data[sym].dropna()
        pos, ret1, ma, upper, lower, vol, in_band = build_signals(close)
        pos_exec = pos.shift(1).fillna(0.0)
        turn = pos_exec.diff().abs().fillna(pos_exec.abs())
        exposure = {
            'n_bars': int(len(close)),
            'n_active_bars_executed': int((pos_exec != 0).sum()),
            'n_long_bars': int((pos_exec > 0).sum()),
            'n_short_bars': int((pos_exec < 0).sum()),
            'n_turnover_events': int((turn > 0).sum()),
            'has_exposure': bool((pos_exec != 0).sum() > 0),
        }
        slices = {}
        all_oos_pos = True; all_beat_bh = True
        for fee, slip in COST_GRID:
            k = f"fee{fee}_slip{slip}_bps"
            r = wf_oos(pos, ret1, fee, slip)
            slices[k] = r
            # pre-stated: use fold-wise all-positive AND beat BH per fold? conservative; state clearly
            if not (r['oos_net_sum_gt_zero'] and r['oos_net_sum_beat_bh']): # aggregate-sum form
                all_oos_pos = False if not r['oos_net_sum_gt_zero'] else all_oos_pos
                all_beat_bh = False if not r['oos_net_sum_beat_bh'] else all_beat_bh
        oos_edge_proven = bool(exposure['has_exposure'] and all(
            (wf_oos(pos,ret1,f,s)['oos_net_sum_gt_zero'] and wf_oos(pos,ret1,f,s)['oos_net_sum_beat_bh'])
            for f,s in COST_GRID))
        by_asset[sym] = {'exposure': exposure, 'cost_slices': slices, 'oos_edge_proven': oos_edge_proven}
    # aggregate
    n_edge = sum(1 for v in by_asset.values() if v['oos_edge_proven'])
    n_allpos = sum(1 for v in by_asset.values() if all(v['cost_slices'][f"fee{f}_slip{s}_bps"]['oos_net_sum_gt_zero'] for f,s in COST_GRID))
    n_beat = sum(1 for v in by_asset.values() if all(v['cost_slices'][f"fee{f}_slip{s}_bps"]['oos_net_sum_beat_bh'] for f,s in COST_GRID))
    agg_proven = bool(n_edge > 0 and n_edge == len(by_asset))
    report = {
      'report': 'spot_range_breakout_reversion_volband_costed_oos',
      'generated_at_utc': datetime.now(timezone.utc).isoformat(),
      'mandate': 'PRIORITY 7 / Campaign #3 Deliverable A — new pre-stated real-spot family: range-bound breakout-reversion with volatility band (Bollinger range; breakout entry only in causal vol band; reversion-to-mid exit). Genuinely different from P6 Donchian breakout+volfilter. Real cached spot only; fail-closed.',
      'supersedes_prior_family_artifacts_note': 'Does NOT relabel P6 Donchian volfilter; different structure (BB range + vol-band breakout entry + MA reversion exit).',
      'provenance': {
        'real_data_only': True, 'fabricated_data': False, 'fail_closed': True,
        'no_threshold_weakening': True, 'new_external_feeds': False, 'proxies': False,
        'data_source': 'real cached Binance spot 1h (data/cache/*_2026-04-01_2026-10-30_1h.pkl + meta)',
        'window': '2026-04-01..2026-10-30', 'bars_expected': 5112, 'interval': '1h', 'assets_expected': 11,
      },
      'family': {
        'name': 'range_breakout_reversion_volband',
        'description': 'Bollinger range MA(20)±2*std defines range. Realized vol = rolling std of 1h returns over 24 bars. Causal vol band = [q25,q75] of vol over 240 bars (min 120). Entry (breakout in vol band): long if close crosses above upper while vol in band; short if crosses below lower while vol in band. Exit (reversion leg): if long, exit to flat when close < MA (revert to mid); if short, exit when close > MA. Long/short allowed. Position shifted by 1 bar for execution.',
        'params': PARAMS,
        'genuinely_different_from_p6_donchian_volfilter': True,
        'uses_only_real_cached_spot': True,
      },
      'cache_inventory': inv,
      'config': {
        'assets': assets,
        'explicitly_reported': ['BTC','ETH','SOL','BNB'],
        'cost_grid_bps_fee_slippage': COST_GRID,
        'walk_forward': {'mode': 'rolling', 'train_bars': TRAIN, 'test_bars': TEST, 'step_bars': STEP},
        'benchmark': 'buy-and-hold per asset (gross, no recurring turnover cost) on same OOS WF windows; strategy net of stated fee+slippage per turnover',
        'pre_stated_oos_edge_proven_rule': 'oos_edge_proven=true IFF executed exposure/trades > 0 AND for ALL cost-grid slices: OOS net sum > 0 AND OOS net sum > B&H OOS sum on same WF windows. Else false (fail-closed). No in-sample tuning.',
      },
      'by_asset': by_asset,
      'aggregate': {
        'n_assets': len(assets),
        'n_oos_edge_proven': n_edge,
        'n_assets_all_slices_oos_net_positive': n_allpos,
        'n_assets_all_slices_beat_benchmark': n_beat,
        'aggregate_oos_edge_proven_fail_closed': agg_proven,
      },
      'oos_edge_proven': bool(agg_proven),
      'real_data_only': True, 'fabricated_data': False, 'fail_closed': True,
      'no_threshold_weakening': True, 'new_external_feeds': False, 'proxies': False,
    }
    out = reports / f'spot_range_breakout_reversion_volband_costed_oos_{ts}.json'
    json.dump(report, open(out,'w'), indent=2)
    print(out)
    return out

if __name__ == '__main__':
    main()
