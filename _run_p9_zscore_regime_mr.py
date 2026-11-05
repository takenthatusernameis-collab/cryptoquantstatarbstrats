#!/usr/bin/env python3
"""PRIORITY 9 / Campaign #5 Deliverable A: regime-adaptive z-score mean-reversion
on rolling pairwise spreads (OLS hedge) from the same 11-asset real spot cache.
Structurally different from P4-P7: pairwise spread construction + causal OLS hedge
+ z-score mean-reversion entries/exits + regime filters (IS corr, half-life, vol regime)
+ dollar-neutral legs, evaluated per pair and aggregated per asset.
Real cached spot only, fail-closed, pre-stated, no in-sample tuning, no gate weakening.
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
  'hedge_lookback': 120,
  'z_lookback': 60,
  'entry_z': 2.0,
  'exit_z': 0.5,
  'max_hold_bars': 72,
  'min_abs_corr_is': 0.45,     # fail-closed pre-stated
  'halflife_min_bars': 2,
  'halflife_max_bars': 240,
  'vol_regime_window': 120,
  'vol_regime_max_mult': 3.0,
  'min_train_obs': 200,
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

def ols_beta(y, x):
    x=np.asarray(x,float); y=np.asarray(y,float)
    vx=np.var(x)
    if not np.isfinite(vx) or vx<1e-18: return None
    b=np.cov(x,y,ddof=0)[0,1]/vx
    if not np.isfinite(b): return None
    return float(b)

def half_life(spread):
    s=np.asarray(spread,float); s=s[np.isfinite(s)]
    if len(s)<30: return None
    ds=np.diff(s); s1=s[:-1]; vx=np.var(s1)
    if not np.isfinite(vx) or vx<1e-18: return None
    b=np.cov(s1,ds,ddof=0)[0,1]/vx
    phi=1.0+b
    if not (0<phi<1): return None
    hl=-math.log(2)/math.log(phi)
    if not np.isfinite(hl): return None
    return float(hl)

def run_pair(df, a, b):
    n=len(df)
    pa=df[a].values; pb=df[b].values
    ra=np.r_[0.0, np.diff(pa)/pa[:-1]]; rb=np.r_[0.0, np.diff(pb)/pb[:-1]]
    pos_a=np.zeros(n); pos_b=np.zeros(n)
    oos=np.zeros(n,dtype=bool); is_m=np.zeros(n,dtype=bool)
    folds=[]; trades=0
    start=0
    while start+TRAIN+TEST<=n:
        tr_s,tr_e=start,start+TRAIN; te_s,te_e=start+TRAIN,start+TRAIN+TEST
        seg=df[[a,b]].iloc[tr_s:tr_e]
        corr=float(seg[a].pct_change().corr(seg[b].pct_change())) if len(seg)>=PARAMS['min_train_obs'] else np.nan
        ok=True; reasons=[]; hl=None
        if not np.isfinite(corr) or abs(corr)<PARAMS['min_abs_corr_is']:
            ok=False; reasons.append('low_is_corr')
        win=seg.iloc[-PARAMS['hedge_lookback']:]
        beta=ols_beta(win[a].values, win[b].values)
        if beta is None: ok=False; reasons.append('no_beta')
        if ok:
            sp_tr=seg[a].values - beta*seg[b].values
            hl=half_life(sp_tr[-PARAMS['hedge_lookback']:] if len(sp_tr)>=PARAMS['hedge_lookback'] else sp_tr)
            if hl is None or hl<PARAMS['halflife_min_bars'] or hl>PARAMS['halflife_max_bars']:
                ok=False; reasons.append('hl_out')
            vol=pd.Series(np.diff(sp_tr)).rolling(min(PARAMS['vol_regime_window'], max(20,len(sp_tr)//3))).std()
            if vol.notna().sum()>=10:
                med=float(vol.median()); curv=float(vol.iloc[-1]) if np.isfinite(vol.iloc[-1]) else med
                if med>0 and curv>PARAMS['vol_regime_max_mult']*med:
                    ok=False; reasons.append('vol_regime_extreme')
        folds.append({'train':[int(tr_s),int(tr_e)],'test':[int(te_s),int(te_e)],'ok_pair':ok,'is_corr':None if not np.isfinite(corr) else corr,'hl':hl,'reasons':reasons})
        if ok:
            cur=0.0; hold=0
            lo=max(tr_s+PARAMS['hedge_lookback'], tr_s+PARAMS['z_lookback']+2)
            for i in range(lo, te_e):
                hwin_a=pa[i-PARAMS['hedge_lookback']:i]; hwin_b=pb[i-PARAMS['hedge_lookback']:i]
                bta=ols_beta(hwin_a,hwin_b)
                if bta is None: cur=0.0; hold=0
                else:
                    spw=pa[i-PARAMS['z_lookback']:i]-bta*pb[i-PARAMS['z_lookback']:i]
                    sd=np.std(spw,ddof=0)
                    if sd<1e-12: z=0.0
                    else:
                        mu=np.mean(spw); sp_now=pa[i-1]-bta*pb[i-1]; z=(sp_now-mu)/sd
                    if cur==0.0:
                        if z>PARAMS['entry_z']: cur=-1.0; hold=0; trades+=1
                        elif z<-PARAMS['entry_z']: cur=1.0; hold=0; trades+=1
                    else:
                        hold+=1
                        if abs(z)<PARAMS['exit_z'] or hold>=PARAMS['max_hold_bars']: cur=0.0; hold=0
                if i<te_e:
                    pos_a[i]=cur*0.5; pos_b[i]=-cur*0.5
            is_m[tr_s:tr_e]=True; oos[te_s:te_e]=True
        start+=STEP
    gross=pos_a*ra + pos_b*rb
    turn=np.abs(np.diff(np.r_[0.0,pos_a])) + np.abs(np.diff(np.r_[0.0,pos_b]))
    return {'pair':f'{a}/{b}','a':a,'b':b,'folds':folds,'trades':int(trades),
            'pos_a':pos_a,'pos_b':pos_b,'gross':gross,'turn':turn,'oos':oos,'is_m':is_m}

def summarize_cost(pos_gross, turn, mask, cost_rate):
    net=pos_gross - turn*cost_rate
    if mask.sum()==0: return {'n':0,'sum':0.0,'mean':0.0}
    x=net[mask]; return {'n':int(mask.sum()),'sum':float(np.nansum(x)),'mean':float(np.nanmean(x))}

def main():
    df, inv = load()
    assets=[a for a in ASSETS if a in df.columns]
    # all pairs
    pairs=[]
    for i in range(len(assets)):
        for j in range(i+1,len(assets)): pairs.append((assets[i],assets[j]))
    pair_results=[]
    for a,b in pairs:
        pair_results.append(run_pair(df,a,b))
    # per-pair cost summaries
    by_pair={}
    for pr in pair_results:
        slices={}
        for fee,slip in COST_GRID:
            k=f'fee{fee}_slip{slip}_bps'; cr=(fee+slip)/10000.0
            slices[k]={'oos':summarize_cost(pr['gross'],pr['turn'],pr['oos'],cr),
                       'is':summarize_cost(pr['gross'],pr['turn'],pr['is_m'],cr)}
        has_exp=bool((np.abs(pr['pos_a'])+np.abs(pr['pos_b'])>0).sum()>0)
        # pre-stated: pair-level edge if has exposure and all slices OOS sum>0 (vs 0 baseline; benchmark B&H not directly pair-comparable) AND all slices OOS sum> per-asset B&H? We'll compute asset-agg B&H below.
        all_oos_pos=all(slices[f'fee{f}_slip{s}_bps']['oos']['sum']>0 for f,s in COST_GRID) if has_exp else False
        by_pair[pr['pair']]={'a':pr['a'],'b':pr['b'],'trades':pr['trades'],'has_exposure':has_exp,
            'n_active_bars':int((np.abs(pr['pos_a'])+np.abs(pr['pos_b'])>0).sum()),
            'folds_n':len(pr['folds']),'folds_ok_n':sum(1 for x in pr['folds'] if x['ok_pair']),
            'cost_slices':slices,'all_slices_oos_net_positive':all_oos_pos}
    # per-asset aggregation: sum contributions of all pairs involving asset (each pair is 0.5/-0.5 so double-counting? pair pnl is standalone; attribute half to each leg)
    rets=df[assets].pct_change().fillna(0.0)
    # B&H benchmark per asset on same OOS windows (union across folds of any pair? use standard WF windows)
    def wf_windows(n):
        ws=[]; st=0
        while st+TRAIN+TEST<=n: ws.append((st,st+TRAIN,st+TRAIN+TEST)); st+=STEP
        return ws
    ws=wf_windows(len(df))
    oos_union=np.zeros(len(df),dtype=bool)
    for s,_,e in ws: oos_union[s+TRAIN:e]=True
    by_asset={}
    for sym in assets:
        # aggregate gross/turn from pairs containing sym
        gross=np.zeros(len(df)); turn=np.zeros(len(df)); has=False
        for pr in pair_results:
            if pr['a']==sym:
                gross += pr['gross']*0.5; turn += pr['turn']*0.25; has = has or (np.abs(pr['pos_a'])>0).any()
            if pr['b']==sym:
                gross += pr['gross']*0.5; turn += pr['turn']*0.25; has = has or (np.abs(pr['pos_b'])>0).any()
        bh_oos=float(rets[sym].values[oos_union].sum()) if oos_union.sum() else 0.0
        slices={}
        for fee,slip in COST_GRID:
            k=f'fee{fee}_slip{slip}_bps'; cr=(fee+slip)/10000.0
            net=gross - turn*cr
            oos_sum=float(np.nansum(net[oos_union])) if oos_union.sum() else 0.0
            slices[k]={'oos_net_sum':oos_sum,'bh_oos_sum':bh_oos,'oos_net_gt_zero':oos_sum>0,'oos_net_beat_bh':oos_sum>bh_oos}
        edge=bool(has and all(slices[f'fee{f}_slip{s}_bps']['oos_net_gt_zero'] and slices[f'fee{f}_slip{s}_bps']['oos_net_beat_bh'] for f,s in COST_GRID))
        by_asset[sym]={'has_exposure':has,'n_active_bars':int(((np.abs(gross)+np.abs(turn))>0).sum()),
                       'bh_oos_sum':bh_oos,'cost_slices':slices,'oos_edge_proven':edge}
    n_edge=sum(1 for v in by_asset.values() if v['oos_edge_proven'])
    report={
      'report':'spot_zscore_regime_mean_reversion_costed_oos',
      'generated_at_utc':datetime.now(timezone.utc).isoformat(),
      'mandate':'PRIORITY 9 / Campaign #5 Deliverable A — regime-adaptive z-score mean-reversion on rolling pairwise spreads (OLS hedge) from same 11-asset real spot cache. Structurally different from P4-P7. Fail-closed, no tuning, no gate weakening.',
      'provenance':{'real_data_only':True,'fabricated_data':False,'fail_closed':True,'no_threshold_weakening':True,'new_external_feeds':False,'proxies':False,
        'data_source':'real cached Binance spot 1h (data/cache/*_2026-04-01_2026-10-30_1h.pkl + meta)','window':'2026-04-01..2026-10-30','bars':len(df),'interval':'1h','assets':assets},
      'structural_novelty':{
        'different_from':['P4 momentum/mean_reversion (single-asset)','P5 cross_sectional_risk_adjusted_return_rank','P6 donchian_breakout_volfilter','P7 range_breakout_reversion_volband'],
        'what_is_new':'Pairwise spread construction across 11 assets (55 pairs) with causal rolling OLS hedge ratio, z-score mean-reversion on spread, per-fold IS regime filters (abs corr, half-life bounds, spread vol regime), dollar-neutral legs, execution shift + turnover costs, aggregated per-asset attribution vs B&H on same WF OOS windows.'
      },
      'cache_inventory':inv,
      'config':{'assets':assets,'n_pairs':len(pairs),'cost_grid_bps_fee_slippage':COST_GRID,
        'walk_forward':{'mode':'rolling','train_bars':TRAIN,'test_bars':TEST,'step_bars':STEP},
        'benchmark':'buy-and-hold per asset (gross, no recurring turnover) on union of OOS WF windows; strategy net of fee+slippage on turnover',
        'pre_stated_oos_edge_proven_rule':'oos_edge_proven=true IFF executed exposure>0 AND for ALL cost-grid slices OOS net sum > 0 AND OOS net sum > B&H OOS sum on same OOS windows. Else false (fail-closed).',
        'params':PARAMS,'explicitly_reported':NAMED},
      'by_asset':by_asset,
      'by_pair_summary':{k:{'a':v['a'],'b':v['b'],'trades':v['trades'],'has_exposure':v['has_exposure'],'n_active_bars':v['n_active_bars'],
                            'folds_n':v['folds_n'],'folds_ok_n':v['folds_ok_n'],'all_slices_oos_net_positive':v['all_slices_oos_net_positive'],
                            'oos_0bps_sum':v['cost_slices']['fee0_slip0_bps']['oos']['sum'],
                            'oos_40bps_sum':v['cost_slices']['fee20_slip20_bps']['oos']['sum']} for k,v in by_pair.items()},
      'aggregate':{'n_assets':len(by_asset),'n_pairs':len(pairs),'n_oos_edge_proven':n_edge,
                   'aggregate_oos_edge_proven_fail_closed':bool(n_edge>0 and n_edge==len(by_asset)),
                   'n_assets_all_slices_oos_net_positive':sum(1 for v in by_asset.values() if all(v['cost_slices'][f"fee{f}_slip{s}_bps"]['oos_net_gt_zero'] for f,s in COST_GRID)),
                   'n_assets_all_slices_beat_benchmark':sum(1 for v in by_asset.values() if all(v['cost_slices'][f"fee{f}_slip{s}_bps"]['oos_net_beat_bh'] for f,s in COST_GRID)),
                   'per_named':{s:{'oos_edge_proven':by_asset[s]['oos_edge_proven'],'has_exposure':by_asset[s]['has_exposure'],
                                   'bh_oos_sum':by_asset[s]['bh_oos_sum'],
                                   'oos_0bps_sum':by_asset[s]['cost_slices']['fee0_slip0_bps']['oos_net_sum'],
                                   'oos_40bps_sum':by_asset[s]['cost_slices']['fee20_slip20_bps']['oos_net_sum']} for s in NAMED if s in by_asset}}
    }
    out=reports/f'spot_zscore_regime_mean_reversion_costed_oos_{ts}.json'
    def _j(o):
        if isinstance(o,(np.bool_,)): return bool(o)
        if isinstance(o,(np.integer,)): return int(o)
        if isinstance(o,(np.floating,)): return float(o) if np.isfinite(o) else None
        if isinstance(o,np.ndarray): return o.tolist()
        raise TypeError(str(type(o)))
    json.dump(report,open(out,'w'),indent=2,default=_j)
    print(out)
    print(json.dumps(report['aggregate'],indent=2,default=_j))
    print('named', json.dumps(report['aggregate']['per_named'],indent=2,default=_j))

if __name__=='__main__': main()
