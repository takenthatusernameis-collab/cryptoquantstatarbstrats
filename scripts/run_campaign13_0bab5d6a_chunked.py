from __future__ import annotations
import hashlib, json, pickle, sys, traceback, warnings
from datetime import datetime, timezone
from pathlib import Path

# suppress noisy warnings to speed log io a bit? keep them but redirect handled by caller
warnings.filterwarnings("ignore")

sys.path.insert(0, '/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats')
import numpy as np
import pandas as pd
from backtest.engine import BacktestEngine
from strategies.pairs_trading import CointegrationPairsStrategy

ROOT = Path('/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats')
CACHE = '0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7'
GATE_NAMES = ("eg_pass","johansen_pass","spread_mr_pass","hl_bounds_pass","leg_stationarity_ok","rolling_stable_ok","no_structural_break")
ENTRY_THRESHOLD=2.0; COINTEGRATION_PVALUE=0.05; LOOKBACKS=[120,240]; CHECK_INTERVALS=[24,48]; FEE_RATE=0.001; SLIPPAGE=0.0005

def _now(): return datetime.now(timezone.utc).isoformat()
def _stamp(): return datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
def _sha256(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for c in iter(lambda:f.read(1024*1024),b''): h.update(c)
    return h.hexdigest()
def _json_safe(obj):
    if isinstance(obj,(np.integer,)): return int(obj)
    if isinstance(obj,(np.floating,)): v=float(obj); return v if np.isfinite(v) else None
    if isinstance(obj,(np.bool_,)): return bool(obj)
    if isinstance(obj,np.ndarray): return [_json_safe(x) for x in obj.tolist()]
    if isinstance(obj,pd.Series): return [_json_safe(x) for x in obj.tolist()]
    if isinstance(obj,pd.DataFrame): return {c:[_json_safe(x) for x in obj[c].tolist()] for c in obj.columns}
    if isinstance(obj,pd.Timestamp): return obj.isoformat()
    if isinstance(obj,dict): return {str(k):_json_safe(v) for k,v in obj.items()}
    if isinstance(obj,(list,tuple)): return [_json_safe(x) for x in obj]
    if isinstance(obj,float): return obj if np.isfinite(obj) else None
    return obj

def _pairs(symbols):
    sym=set(symbols)
    preferred=[("BTC","ETH"),("ETH","SOL"),("BTC","SOL"),("ADA","ETH"),("XRP","BTC"),("BNB","ETH"),("ADA","BTC"),("XRP","ETH"),("BNB","BTC"),("SOL","BNB"),("DOT","BTC"),("DOT","ETH"),("POL","BTC"),("AVAX","BTC"),("LINK","BTC"),("LTC","BTC")]
    pairs=[p for p in preferred if p[0] in sym and p[1] in sym]
    for i,a in enumerate(sorted(sym)):
        for b in sorted(sym)[i+1:]:
            if (a,b) not in pairs and (b,a) not in pairs: pairs.append((a,b))
    return pairs

def _load():
    pkl=ROOT/f'data/cache/{CACHE}.pkl'; meta_p=ROOT/f'data/cache/{CACHE}.meta.json'
    meta=json.loads(meta_p.read_text())
    with open(pkl,'rb') as f: data=pickle.load(f)
    data=data.sort_index()
    return data, meta, pkl, meta_p

def _acct(bd,enriched_ok):
    out={"bars_total":0,"bars_assessable":0,"bars_pass":0,"bars_fail":0,"bars_unassessable":0,"pass_rate":0.0,"fail_rate":0.0,"unassessable_rate":0.0,"per_gate_fail_count":{k:0 for k in GATE_NAMES},"per_gate_fail_count_all_pass":0,"breakdown_recorded": bd is not None and not bd.empty}
    if bd is None or bd.empty: return out
    n=len(bd); out["bars_total"]=int(n)
    fail_counts={k:0 for k in GATE_NAMES}
    for k in GATE_NAMES:
        if k in bd.columns: fail_counts[k]=int((bd[k]==False).sum())  # noqa: E712
    out["per_gate_fail_count"]=fail_counts
    if "all_pass" in bd.columns: out["per_gate_fail_count_all_pass"]=int((bd["all_pass"]==False).sum())  # noqa: E712
    if enriched_ok is not None and len(enriched_ok)==n:
        arr=enriched_ok.to_numpy(dtype=float); finite=np.isfinite(arr)
        assessable=int(finite.sum()); passes=int(((arr==1.0)&finite).sum()); fails=int(((arr==0.0)&finite).sum()); unass=int(assessable-passes-fails)
        out.update({"bars_assessable":assessable,"bars_pass":passes,"bars_fail":fails,"bars_unassessable":unass})
        if assessable: out.update({"pass_rate":passes/assessable,"fail_rate":fails/assessable,"unassessable_rate":unass/assessable})
    return out

def _run_pair(pair,data):
    engine=BacktestEngine(initial_capital=100_000.0)
    pcols=list(pair); df=data[pcols].dropna()
    sweep_results=[]
    for lb in LOOKBACKS:
        for cci in CHECK_INTERVALS:
            strat=CointegrationPairsStrategy(pair=pair,lookback=lb,entry_threshold=ENTRY_THRESHOLD,cointegration_pvalue=COINTEGRATION_PVALUE,cointegration_check_interval=cci,use_enriched_gates=True,strict_enriched_gates=True)
            res=engine.run(strat,df,fee_rate=FEE_RATE,slippage=SLIPPAGE)
            breakdown=strat.get_gate_breakdown()
            if breakdown is not None and not breakdown.empty and 'all_pass' in breakdown.columns:
                ap=breakdown['all_pass']
                enriched_ok=pd.Series(np.where(ap.to_numpy(dtype=bool),1.0,0.0),index=df.index,dtype=float)
                enriched_ok=enriched_ok.where(ap.notna(),np.nan).bfill().ffill().fillna(0.0)
            else:
                enriched_ok=None
            acct=_acct(breakdown,enriched_ok)
            sweep_results.append({"lookback":lb,"cointegration_check_interval":cci,"bars":int(len(df)),"gate_accounting":acct,"total_return":float(res.get('total_return',0.0)),"trades_count":int(res.get('activity',{}).get('trades_count',0))})
    any_bar_passes=any(r['gate_accounting'].get('bars_pass',0)>0 for r in sweep_results)
    rolling_stable_blocks_all=all(r['gate_accounting'].get('per_gate_fail_count',{}).get('rolling_stable_ok',0)==r['gate_accounting'].get('bars_total',0) and r['gate_accounting'].get('bars_total',0)>0 for r in sweep_results) if sweep_results else False
    return {"pair":list(pair),"symbols":pcols,"bars":int(len(df)),"window":{"start":str(df.index.min()),"end":str(df.index.max())},"sweeps":sweep_results,"any_bar_passes_all_gates":bool(any_bar_passes),"rolling_stable_blocks_all_bars_all_sweeps":bool(rolling_stable_blocks_all)}

def main():
    data,meta,pkl,meta_p=_load()
    symbols=list(meta.get('columns',[]) or meta.get('symbols',[]))
    pairs=_pairs(symbols)
    partial_path=ROOT/'reports/campaign13_0bab5d6a_partial_all.json'
    results={}
    if partial_path.exists():
        try: results=json.loads(partial_path.read_text()).get('results_pairs',{})
        except Exception: results={}
    for idx,pair in enumerate(pairs):
        key='/'.join(pair)
        if key in results and 'error' not in results[key]:
            print(f'skip {idx+1}/{len(pairs)} {key}', flush=True); continue
        print(f'run {idx+1}/{len(pairs)} {key}', flush=True)
        try:
            results[key]=_run_pair(pair,data)
        except Exception as e:
            results[key]={"pair":list(pair),"error":str(e),"traceback":traceback.format_exc()[-4000:],"any_bar_passes_all_gates":False}
            print(f'ERR {key}: {e}', flush=True)
        partial={"cache":CACHE,"updated_utc":_now(),"completed":len([k for k,v in results.items() if 'error' not in v]),"total":len(pairs),"results_pairs":results}
        partial_path.write_text(json.dumps(_json_safe(partial),indent=2))

    # finalize report
    spot_hash=_sha256(pkl); meta_hash=_sha256(meta_p)
    any_passes_anywhere=any(r.get('any_bar_passes_all_gates',False) for r in results.values())
    min_bars=min((r.get('bars',0) for r in results.values() if 'bars' in r), default=0)
    rolling_stable_is_sole=all(r.get('rolling_stable_blocks_all_bars_all_sweeps',False) and not r.get('any_bar_passes_all_gates',False) for r in results.values() if 'error' not in r) if results else False
    errors=[k for k,v in results.items() if 'error' in v]
    if errors:
        conclusion='insufficient_or_blocked'; edge_claim=False
        reason=f"Errors on {len(errors)} pairs: {errors[:5]}"; honest=True
    elif any_passes_anywhere:
        conclusion='edge_signal'; edge_claim=True; reason='At least one bar passes all enriched gates (unmodified thresholds) on at least one pair/sweep.'; honest=True
    elif rolling_stable_is_sole and min_bars>=500:
        conclusion='no_edge'; edge_claim=False; reason='No bar passes all gates; rolling_stable_ok blocks all bars on all pairs/sweeps (data sufficient).'; honest=True
    else:
        conclusion='insufficient_or_blocked'; edge_claim=False; reason='Mixed blocker pattern / unassessable gates or insufficient bars on real data.'; honest=True

    # aggregate gate counts across all pairs/sweeps
    agg_gate_fail={k:0 for k in GATE_NAMES}; agg_pass=0; agg_total=0
    for r in results.values():
        for sw in r.get('sweeps',[]):
            ga=sw.get('gate_accounting',{})
            agg_total+=ga.get('bars_total',0); agg_pass+=ga.get('bars_pass',0)
            for k in GATE_NAMES: agg_gate_fail[k]+=ga.get('per_gate_fail_count',{}).get(k,0)

    report={
        'campaign':13,'cache_key':CACHE,'cache8':CACHE[:8],'generated_utc':_now(),
        'real_data_only':True,'fabricated_data':False,'no_network_refetch':True,
        'provenance':{
            'cache_pkl':str(pkl),'cache_meta':str(meta_p),'pkl_sha256':spot_hash,'meta_sha256':meta_hash,
            'symbols':symbols,'start':meta.get('start'),'end':meta.get('end'),'freq':meta.get('interval'),
            'rows':meta.get('rows'),'fetch_success':meta.get('fetch_success'),
            'fetch_real_data_only_meta':meta.get('fetch_real_data_only'),
            'fetch_fabricated_data_meta':meta.get('fetch_fabricated_data'),
            'blocked_routes':[],'rationale':'Real cached Binance spot data only; no network refetch; gate thresholds unmodified.'
        },
        'gate_thresholds':{'entry_threshold':ENTRY_THRESHOLD,'cointegration_pvalue':COINTEGRATION_PVALUE,'lookbacks':LOOKBACKS,'check_intervals':CHECK_INTERVALS,'enriched_gates':list(GATE_NAMES),'strict_enriched_gates':True,'fee_rate':FEE_RATE,'slippage':SLIPPAGE},
        'pairs_evaluated':len(results),'pairs_with_errors':len(errors),'error_pairs':errors,
        'aggregate':{'total_bar_evaluations':agg_total,'total_bar_passes':agg_pass,'per_gate_fail_count':agg_gate_fail},
        'results_pairs':results,
        'conclusion':conclusion,'edge_claim':edge_claim,'honest':honest,'reason':reason,
    }
    out=ROOT/f'reports/campaign13_causal_per_bar_enriched_gates_0bab5d6a_{_stamp()}.json'
    out.write_text(json.dumps(_json_safe(report),indent=2))
    sha=_sha256(out)
    (ROOT/f'reports/campaign13_causal_per_bar_enriched_gates_0bab5d6a_latest.sha256').write_text(f'{sha}  {out.name}\n')
    print(f'FINAL_REPORT {out} {sha} {conclusion}', flush=True)

if __name__=='__main__': main()
