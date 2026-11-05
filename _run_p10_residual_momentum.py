#!/usr/bin/env python3
"""PRIORITY 10 / Campaign #6 Deliverable A: causal residual (idiosyncratic) return momentum.
Path A of HANDOFF Campaign #6 — genuinely different from P4 momentum/MR (single-asset raw returns),
P5 cross-sectional rank, P6 Donchian breakout, P7 range breakout-reversion, P9 pairwise OLS-hedge
spread z-score MR. Regresses each asset return on an EW leave-one-out market factor estimated
causally on the trailing IS window only; trades the residual (idiosyncratic) signal momentum.
Real cached spot 1h only, fail-closed, pre-stated, no in-sample tuning, no gate weakening.
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
  'beta_lookback': 240,          # trailing IS bars used for causal OLS beta (fixed per fold)
  'resid_z_lookback': 60,        # causal lookback for residual z-score
  'entry_z': 2.0,
  'exit_z': 0.5,
  'max_hold_bars': 72,
  'min_train_obs': 200,
  'min_resid_obs': 30,
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
    n=len(x)
    if n<10: return None
    xc=x-x.mean(); yc=y-y.mean()
    vx=float(np.dot(xc,xc))
    if not np.isfinite(vx) or vx<1e-18: return None
    b=float(np.dot(xc,yc)/vx)
    return b if np.isfinite(b) else None

def run_asset(df, sym):
    n=len(df)
    prices=df[sym].values.astype(float)
    ra=np.r_[0.0, np.diff(prices)/prices[:-1]]
    # leave-one-out EW market factor (causal, uses only contemporaneous other-asset returns)
    others=[a for a in df.columns if a!=sym]
    roth=df[others].values.astype(float) if others else np.zeros((n,1))
    if roth.shape[1]>0:
        rets_other=np.diff(roth,axis=0)/roth[:-1]
        rm=np.r_[0.0, rets_other.mean(axis=1)]
    else:
        rm=np.zeros(n)
    pos=np.zeros(n); oos=np.zeros(n,dtype=bool); is_m=np.zeros(n,dtype=bool)
    folds=[]; trades=0
    start=0
    while start+TRAIN+TEST<=n:
        tr_s,tr_e=start,start+TRAIN; te_s,te_e=start+TRAIN,start+TRAIN+TEST
        seg_r=ra[tr_s:tr_e]; seg_m=rm[tr_s:tr_e]
        ok=True; reasons=[]
        if len(seg_r)<PARAMS['min_train_obs'] or len(seg_m)<PARAMS['min_train_obs']:
            ok=False; reasons.append('insufficient_train')
        beta=None
        if ok:
            win=min(PARAMS['beta_lookback'], len(seg_r))
            beta=ols_beta(seg_r[-win:], seg_m[-win:])
            if beta is None:
                ok=False; reasons.append('no_beta')
        # residual series (causal, beta fixed from train IS window)
        resid=ra - beta*rm if beta is not None else np.full(n, np.nan)
        # causal residual z-score: trailing lookback up to current bar (exclusive for signal at bar i)
        if ok:
            cur=0.0; hold=0
            lo=max(tr_s+PARAMS['resid_z_lookback']+2, tr_s+1)
            for i in range(lo, te_e):
                zwin=resid[max(0,i-PARAMS['resid_z_lookback']):i]
                zwin=zwin[np.isfinite(zwin)]
                if len(zwin)<PARAMS['min_resid_obs']:
                    cur=0.0; hold=0
                else:
                    mu=float(np.mean(zwin)); sd=float(np.std(zwin,ddof=0))
                    if sd<1e-12: z=0.0
                    else: z=float((resid[i-1]-mu)/sd)
                    if cur==0.0:
                        if z>PARAMS['entry_z']: cur=1.0; hold=0; trades+=1
                        elif z<-PARAMS['entry_z']: cur=-1.0; hold=0; trades+=1
                    else:
                        hold+=1
                        if abs(z)<PARAMS['exit_z'] or hold>=PARAMS['max_hold_bars']: cur=0.0; hold=0
                if i<te_e:
                    pos[i]=cur
        folds.append({'train':[int(tr_s),int(tr_e)],'test':[int(te_s),int(te_e)],'ok':ok,'beta':None if beta is None else float(beta),'reasons':reasons})
        is_m[tr_s:tr_e]=True; oos[te_s:te_e]=True
        start+=STEP
    gross=pos*ra
    turn=np.abs(np.diff(np.r_[0.0,pos]))
    return {'asset':sym,'folds':folds,'trades':int(trades),'pos':pos,'gross':gross,'turn':turn,'oos':oos,'is_m':is_m,'ra':ra}

def summarize(gross, turn, mask, cost_rate):
    net=gross - turn*cost_rate
    if mask.sum()==0: return {'n':0,'sum':0.0,'mean':0.0}
    x=net[mask]; return {'n':int(mask.sum()),'sum':float(np.nansum(x)),'mean':float(np.nanmean(x))}

def main():
    df, inv = load()
    assets=[a for a in ASSETS if a in df.columns]
    rets=df[assets].pct_change().fillna(0.0)
    res={}
    for sym in assets:
        res[sym]=run_asset(df, sym)
    # B&H benchmark OOS union windows (standard WF windows)
    def wf_windows(n):
        ws=[]; st=0
        while st+TRAIN+TEST<=n: ws.append((st,st+TRAIN,st+TRAIN+TEST)); st+=STEP
        return ws
    ws=wf_windows(len(df))
    oos_union=np.zeros(len(df),dtype=bool)
    for s,_,e in ws: oos_union[s+TRAIN:e]=True
    by_asset={}
    for sym in assets:
        pr=res[sym]
        gross=pr['gross']; turn=pr['turn']; oos=pr['oos']; is_m=pr['is_m']
        has_exp=bool((np.abs(pr['pos'])>0).sum()>0)
        slices={}
        for fee,slip in COST_GRID:
            k=f'fee{fee}_slip{slip}_bps'; cr=(fee+slip)/10000.0
            slices[k]={'oos':summarize(gross,turn,oos,cr),'is':summarize(gross,turn,is_m,cr)}
        bh_oos=float(rets[sym].values[oos_union].sum()) if oos_union.sum() else 0.0
        for k in slices:
            slices[k]['bh_oos_sum']=bh_oos
            slices[k]['oos_net_gt_zero']=bool(slices[k]['oos']['sum']>0)
            slices[k]['oos_net_beat_bh']=bool(slices[k]['oos']['sum']>bh_oos)
        edge=bool(has_exp and all(slices[f'fee{f}_slip{s}_bps']['oos_net_gt_zero'] and slices[f'fee{f}_slip{s}_bps']['oos_net_beat_bh'] for f,s in COST_GRID))
        by_asset[sym]={'has_exposure':has_exp,'n_active_bars':int((np.abs(pr['pos'])>0).sum()),
                       'n_trades':int(pr['trades']),'bh_oos_sum':bh_oos,'cost_slices':slices,'oos_edge_proven':edge,
                       'folds_n':len(pr['folds']),'folds_ok_n':sum(1 for x in pr['folds'] if x['ok'])}
    n_edge=sum(1 for v in by_asset.values() if v['oos_edge_proven'])
    report={
      'report':'spot_residual_momentum_costed_oos',
      'generated_at_utc':datetime.now(timezone.utc).isoformat(),
      'mandate':'PRIORITY 10 / Campaign #6 Deliverable A — Path A: causal residual (idiosyncratic) return momentum on real cached spot 1h. Regress each asset return on causal trailing-IS leave-one-out EW market factor; trade residual z-score momentum. Genuinely different from P4-P9 families (no raw-return MR, no cross-sectional rank, no spread/OLS hedge pair, no breakout). Fail-closed, pre-stated, no tuning, no gate weakening.',
      'provenance':{'real_data_only':True,'fabricated_data':False,'fail_closed':True,'no_threshold_weakening':True,'new_external_feeds':False,'proxies':False,
        'data_source':'real cached Binance spot 1h (data/cache/*_2026-04-01_2026-10-30_1h.pkl + meta)','window':'2026-04-01..2026-10-30','bars':int(len(df)),'interval':'1h','assets':assets},
      'structural_novelty':{
        'different_from':['P4 momentum/mean_reversion (single-asset raw returns)','P5 cross_sectional_risk_adjusted_return_rank','P6 donchian_breakout_volfilter','P7 range_breakout_reversion_volband','P9 spot_zscore_regime_mean_reversion_pairs (pairwise OLS-hedge spread z-score MR)'],
        'what_is_new':'Per-asset idiosyncratic residual = asset return minus causal OLS beta on leave-one-out EW market factor (beta estimated on trailing IS window only); residual z-score momentum entries/exits; long/short single-asset; same WF 720/168/168 and 0-40bps cost grid; attribution vs B&H on same OOS windows.'
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
                                   'oos_0bps_sum':by_asset[s]['cost_slices']['fee0_slip0_bps']['oos']['sum'],
                                   'oos_40bps_sum':by_asset[s]['cost_slices']['fee20_slip20_bps']['oos']['sum']} for s in NAMED if s in by_asset}}
    }
    out=reports/f'spot_residual_momentum_costed_oos_{ts}.json'
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
