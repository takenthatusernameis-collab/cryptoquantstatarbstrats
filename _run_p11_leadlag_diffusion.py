#!/usr/bin/env python3
"""PRIORITY 11 / Campaign #7 Deliverable 1: causal lead-lag cross-asset information diffusion.
Structurally different from P4-P10: uses lagged returns of a leader asset (selected/weighted on
trailing TRAIN window only) as the predictive signal for a target asset; no contemporaneous
market-factor residualization traded as in P10, no raw single-asset momentum/MR (P4), no
cross-sectional rank (P5), no breakout (P6/P7), no pairwise OLS-hedge spread (P9).
Real cached spot 1h only. Fail-closed. Pre-stated. No in-sample tuning. No gate weakening.
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

ASSETS = ['ADA','AVAX','BNB','BTC','DOT','ETH','LINK','LTC','POL','SOL','XRP']
COST_GRID = [[0,0],[5,0],[0,5],[5,5],[10,0],[0,10],[10,10],[20,0],[0,20],[20,20]]
TRAIN, TEST, STEP = 720, 168, 168
PARAMS = {
    'lag_candidates': [1, 2, 3, 4, 6, 12],   # fixed candidate lags (bars) — pre-stated
    'leader_select_window': 240,              # trailing train bars for causal leader/lag selection
    'signal_z_lookback': 60,                  # causal z-score of lagged leader signal
    'entry_z': 1.5,                           # pre-stated (not tuned on OOS)
    'exit_z': 0.4,
    'max_hold_bars': 72,
    'min_train_obs': 200,
    'min_leader_corr_abs': 0.02,              # minimum |corr| on train to trade (fail-closed filter)
    'min_obs': 30,
}
NAMED = ['BTC','ETH','SOL','BNB']

def load():
    data={}; inv=[]
    for m in sorted(glob.glob(str(cache_dir / '*_2026-04-01_2026-10-30_1h.meta.json'))):
        meta=json.load(open(m))
        if meta.get('interval')!='1h': continue
        sym=meta.get('symbol') or meta.get('market','').replace('USDT','')
        pkl=m.replace('.meta.json','.pkl')
        if not os.path.exists(pkl): continue
        s=pickle.load(open(pkl,'rb'))
        if not isinstance(s,pd.Series): continue
        data[sym]=s.astype(float).rename(sym)
        inv.append({'symbol':sym,'bars':int(len(s)),'first':str(s.index[0]),'last':str(s.index[-1]),
                    'source':meta.get('source'),'real_data_only':bool(meta.get('real_data_only',True)),
                    'fabricated_data':bool(meta.get('fabricated_data',False)),'market':meta.get('market'),'host':meta.get('host')})
    df=pd.DataFrame({a:data[a] for a in ASSETS if a in data}).dropna()
    return df, inv

def safe_corr(x,y):
    x=np.asarray(x,float); y=np.asarray(y,float)
    m=np.isfinite(x)&np.isfinite(y)
    x=x[m]; y=y[m]
    if len(x)<20: return 0.0
    sx=np.std(x,ddof=0); sy=np.std(y,ddof=0)
    if sx<1e-15 or sy<1e-15: return 0.0
    c=float(np.corrcoef(x,y)[0,1])
    return c if np.isfinite(c) else 0.0

def select_leader(train_rets, target_sym, tr_s, tr_e):
    """Causal: select (leader, lag) with highest |corr(lagged leader, target)| on trailing train window."""
    win=min(PARAMS['leader_select_window'], tr_e-tr_s)
    best=None; best_abs= -1.0
    t = train_rets[target_sym].values
    for leader in ASSETS:
        if leader==target_sym or leader not in train_rets.columns: continue
        lvals = train_rets[leader].values
        for lag in PARAMS['lag_candidates']:
            # align: corr(lvals[t-lag], t[t]) over window ending at tr_e
            end = tr_e
            start = max(tr_s, end-win)
            # indices relative to full arrays (train_rets is full-length slice context)
            xs=[]; ys=[]
            for i in range(start, end):
                j=i-lag
                if j < tr_s: continue
                lv=lvals[j]; tv=t[i]
                if np.isfinite(lv) and np.isfinite(tv):
                    xs.append(lv); ys.append(tv)
            if len(xs) < PARAMS['min_obs']: continue
            c=safe_corr(np.array(xs), np.array(ys))
            if abs(c) > best_abs:
                best_abs=abs(c); best=(leader, lag, float(c))
    return best  # (leader, lag, corr) or None

def run_asset(df, sym):
    n=len(df)
    prices=df[sym].values.astype(float)
    ra=np.r_[0.0, np.diff(prices)/prices[:-1]]
    # full return frame (causal indexing only)
    ret_df = pd.DataFrame({a: np.r_[0.0, np.diff(df[a].values.astype(float))/df[a].values.astype(float)[:-1]] for a in df.columns}, index=df.index)
    pos=np.zeros(n); oos=np.zeros(n,dtype=bool); is_m=np.zeros(n,dtype=bool)
    folds=[]; trades=0
    start=0
    while start+TRAIN+TEST<=n:
        tr_s,tr_e=start,start+TRAIN; te_s,te_e=start+TRAIN,start+TRAIN+TEST
        ok=True; reasons=[]
        if tr_e-tr_s < PARAMS['min_train_obs']:
            ok=False; reasons.append('insufficient_train')
        sel = select_leader(ret_df, sym, tr_s, tr_e) if ok else None
        if ok and sel is None:
            ok=False; reasons.append('no_leader')
        if ok and abs(sel[2]) < PARAMS['min_leader_corr_abs']:
            ok=False; reasons.append('weak_train_corr')
        leader, lag, train_corr = (sel if sel else (None,None,None))
        if ok:
            lret = ret_df[leader].values
            cur=0.0; hold=0
            lo=max(tr_s+PARAMS['signal_z_lookback']+lag+2, tr_s+lag+1)
            for i in range(lo, te_e):
                # signal at i uses leader return at i-1-lag? to be strictly causal for trading at i,
                # use lagged leader info available before i: s_i = lret[i-lag]
                sig_idx = i - lag
                if sig_idx < 0:
                    cur=0.0
                else:
                    sig = lret[sig_idx]
                    # causal z of recent lagged signals
                    hist = []
                    for k in range(max(tr_s+lag, i-PARAMS['signal_z_lookback']), i):
                        j=k-lag
                        if j>=0 and np.isfinite(lret[j]): hist.append(lret[j])
                    if len(hist) < PARAMS['min_obs'] or not np.isfinite(sig):
                        z = 0.0
                    else:
                        mu=float(np.mean(hist)); sd=float(np.std(hist,ddof=0))
                        z = float((sig-mu)/sd) if sd>=1e-12 else 0.0
                    # direction follows train corr sign (causal: sign from train)
                    dirn = 1.0 if train_corr >= 0 else -1.0
                    if cur==0.0:
                        if z > PARAMS['entry_z']: cur = 1.0*dirn; hold=0; trades+=1
                        elif z < -PARAMS['entry_z']: cur = -1.0*dirn; hold=0; trades+=1
                    else:
                        hold += 1
                        if abs(z) < PARAMS['exit_z'] or hold >= PARAMS['max_hold_bars']: cur=0.0; hold=0
                if i < te_e:
                    pos[i]=cur
        folds.append({'train':[int(tr_s),int(tr_e)],'test':[int(te_s),int(te_e)],'ok':ok,
                      'leader':leader,'lag':lag,'train_corr':train_corr,'reasons':reasons})
        is_m[tr_s:tr_e]=True; oos[te_s:te_e]=True
        start+=STEP
    gross=pos*ra
    turn=np.abs(np.diff(np.r_[0.0,pos]))
    return {'asset':sym,'folds':folds,'trades':int(trades),'pos':pos,'gross':gross,'turn':turn,'oos':oos,'is_m':is_m,'ra':ra}

def summarize(gross, turn, mask, cost_rate):
    net=gross - turn*cost_rate
    if mask.sum()==0: return {'n':0,'sum':0.0,'mean':0.0}
    g=gross[mask]; t=turn[mask]; n=net[mask]
    return {'n':int(mask.sum()),'gross_sum':float(np.sum(g)),'gross_mean':float(np.mean(g)),
            'turnover_sum':float(np.sum(t)),'cost_drag':float(np.sum(t)*cost_rate),
            'net_sum':float(np.sum(n)),'net_mean':float(np.mean(n))}

def main():
    df, inv = load()
    if len(df) < TRAIN+TEST:
        raise SystemExit('insufficient data')
    assets=[a for a in ASSETS if a in df.columns]
    results={}; by_asset={}
    for sym in assets:
        pr=run_asset(df,sym)
        results[sym]=pr
        bh=pr['ra'][pr['oos']].sum() if pr['oos'].any() else 0.0
        cost_slices={}
        for fee,slip in COST_GRID:
            cr=(fee+slip)/10000.0
            o=summarize(pr['gross'],pr['turn'],pr['oos'],cr)
            i=summarize(pr['gross'],pr['turn'],pr['is_m'],cr)
            cost_slices[f'fee{fee}_slip{slip}_bps']={'is':i,'oos':o,
                'oos_net_gt_zero':o['net_sum']>0,'oos_net_beat_bh':o['net_sum']>bh}
        has_exp = bool((np.abs(pr['pos'][pr['oos']])>0).any()) if pr['oos'].any() else False
        all_pos=all(v['oos_net_gt_zero'] for v in cost_slices.values())
        all_bh=all(v['oos_net_beat_bh'] for v in cost_slices.values())
        edge = bool(has_exp and all_pos and all_bh)
        by_asset[sym]={'oos_edge_proven':edge,'has_exposure':has_exp,'all_slices_oos_net_positive':all_pos,
                       'all_slices_beat_benchmark':all_bh,'bh_oos_sum':float(bh),'trades':pr['trades'],
                       'cost_slices':cost_slices,'folds_n':len(pr['folds']),
                       'folds_ok_n':sum(1 for x in pr['folds'] if x['ok']),
                       'leader_freq':{k:int(v) for k,v in pd.Series([x['leader'] for x in pr['folds'] if x.get('leader')]).value_counts().to_dict().items()}}
    n_edge=sum(1 for v in by_asset.values() if v['oos_edge_proven'])
    report={
      'report':'spot_leadlag_diffusion_costed_oos',
      'generated_at_utc':datetime.now(timezone.utc).isoformat(),
      'mandate':'PRIORITY 11 / Campaign #7 Deliverable 1 — Path A: causal lead-lag cross-asset information diffusion on real cached spot 1h. Per target, select (leader, lag) with highest |corr(lagged leader, target)| on trailing TRAIN window only; trade z-scored lagged leader signal in test with direction fixed from train corr sign. Fail-closed, pre-stated, no tuning, no gate weakening.',
      'provenance':{'real_data_only':True,'fabricated_data':False,'fail_closed':True,'no_threshold_weakening':True,'new_external_feeds':False,'proxies':False,
        'data_source':'real cached Binance spot 1h (data/cache/*_2026-04-01_2026-10-30_1h.pkl + meta)','window':'2026-04-01..2026-10-30','bars':int(len(df)),'interval':'1h','assets':assets},
      'structural_novelty':{
        'different_from':['P4 momentum/mean_reversion (single-asset raw returns, no cross-asset lag)','P5 cross_sectional_risk_adjusted_return_rank','P6 donchian_breakout_volfilter','P7 range_breakout_reversion_volband','P9 spot_zscore_regime_mean_reversion_pairs (pairwise OLS-hedge spread z-score MR, contemporaneous hedge)','P10 spot_residual_momentum (contemporaneous market-factor beta residual z-score momentum)'],
        'what_is_new':'Causal lead-lag information diffusion: leader asset + discrete lag selected on trailing TRAIN window only (pre-stated lag candidates {1,2,3,4,6,12}); signal is lagged leader return z-scored causally; trade direction fixed by train corr sign; no contemporaneous hedge/beta residualization. Tests cross-asset predictive diffusion, not spread mean-reversion or residual momentum.'
      },
      'cache_inventory':inv,
      'config':{'assets':assets,'cost_grid_bps_fee_slippage':COST_GRID,
        'walk_forward':{'mode':'rolling','train_bars':TRAIN,'test_bars':TEST,'step_bars':STEP},
        'benchmark':'buy-and-hold per asset (gross, no recurring turnover) on union of OOS WF windows; strategy net of fee+slippage on turnover',
        'pre_stated_oos_edge_proven_rule':'oos_edge_proven=true IFF executed exposure>0 AND for ALL cost-grid slices OOS net sum > 0 AND OOS net sum > B&H OOS sum on same OOS windows. Else false (fail-closed).',
        'params':PARAMS,'explicitly_reported':NAMED},
      'by_asset':by_asset,
      'aggregate':{'n_assets':len(by_asset),'n_oos_edge_proven':n_edge,
                   'aggregate_oos_edge_proven_fail_closed':bool(n_edge>0 and n_edge==len(by_asset)),
                   'n_assets_all_slices_oos_net_positive':sum(1 for v in by_asset.values() if all(v['cost_slices'][f"fee{f}_slip{s}_bps"]['oos_net_gt_zero'] for f,s in COST_GRID)),
                   'n_assets_all_slices_beat_benchmark':sum(1 for v in by_asset.values() if all(v['cost_slices'][f"fee{f}_slip{s}_bps"]['oos_net_beat_bh'] for f,s in COST_GRID)),
                   'per_named':{s:{'oos_edge_proven':by_asset[s]['oos_edge_proven'],'has_exposure':by_asset[s]['has_exposure'],
                                   'bh_oos_sum':by_asset[s]['bh_oos_sum'],
                                   'oos_0bps_sum':by_asset[s]['cost_slices']['fee0_slip0_bps']['oos']['net_sum'],
                                   'oos_40bps_sum':by_asset[s]['cost_slices']['fee20_slip20_bps']['oos']['net_sum']} for s in NAMED if s in by_asset}}
    }
    out=reports/f'spot_leadlag_diffusion_costed_oos_{ts}.json'
    def _j(o):
        if isinstance(o,(np.bool_,)): return bool(o)
        if isinstance(o,(np.integer,)): return int(o)
        if isinstance(o,(np.floating,)): return float(o) if np.isfinite(o) else None
        if isinstance(o,np.ndarray): return o.tolist()
        raise TypeError(str(type(o)))
    json.dump(report,open(out,'w'),indent=2,default=_j)
    print(out)
    print(json.dumps(report['aggregate'],indent=2,default=_j))

if __name__=='__main__': main()
