#!/usr/bin/env python3
"""C273 parameter-perturbation sensitivity on real cached data only.
Pre-stated bounded grid around baseline: ENTRY_Z {1.25,1.5,1.75}, EXIT_Z {0.25,0.5,0.75}
with EXIT_Z<ENTRY_Z, W_RR {144,168,192}. ALB fixed 336 (>=2*max W_RR). Other params fixed."""
from __future__ import annotations
import hashlib, json, pickle, sys, itertools
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
VOL_META = cache_dir / "volume_1h_full.meta.json"
VOL_PROV = cache_dir / "volume_1h_full.provenance.json"
C273_OOS = reports/"real_quote_volume_rqa_rte_over_white_diag_line_length_percentile_spread_shock_mr_costed_oos_20261112T050947Z.json"

ALB = 336
M_EMB = 2
TAU = 1
EPS_SCALE = 0.5
W_MIN = 2
MAX_HOLD = 24
TRAIN = 720
TEST = 168
STEP = 168
COST_GRID = [[0, 0], [5, 5], [10, 10], [20, 20], [40, 40]]
COST_KEYS = [f"fee{f}_slip{s}" for f,s in COST_GRID]

WRR_GRID = [144, 168, 192]
ENTRY_GRID = [1.25, 1.5, 1.75]
EXIT_GRID = [0.25, 0.5, 0.75]

def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def load_spot():
    with open(SPOT_CACHE, "rb") as f:
        df = pickle.load(f)
    if isinstance(df, pd.Series): df = df.to_frame()
    return df

def load_volume():
    from data.real_feed_loader import validate_and_load_real_feed
    prov = json.loads(VOL_PROV.read_text()) if VOL_PROV.exists() else {}
    df, report = validate_and_load_real_feed(VOL_META, "real_quote_volume", provenance=prov)
    df = df.pivot_table(index="timestamp_utc", columns="symbol", values="quote_volume_usdt", aggfunc="first").sort_index()
    return df, report

def wf_splits(n, train, test, step):
    out=[]; i=0
    while i+train+test<=n:
        out.append((i,i+train,i+train+test)); i+=step
    return out

def _qualifying_white_diag_segments(diag, w_min):
    diag=np.asarray(diag)
    if diag.size==0: return []
    padded=np.concatenate(([1.0],diag,[1.0]))
    ones=np.flatnonzero(padded)
    gaps=np.diff(ones)-1
    gaps=gaps[gaps>=w_min]
    return gaps.astype(int).tolist()

def _pct_spread(R, w_min):
    M=R.shape[0]; seg=[]
    for k in range(-(M-1),M):
        if k==0: continue
        s=_qualifying_white_diag_segments(np.diag(R,k=k),w_min)
        if s: seg.extend(int(x) for x in s)
    if len(seg)<3: return np.nan
    arr=np.array(seg,dtype=float)
    if not np.all(np.isfinite(arr)) or not np.all(arr>0): return np.nan
    p25=float(np.percentile(arr,25)); p75=float(np.percentile(arr,75)); med=float(np.median(arr))
    if not (np.isfinite(p25) and np.isfinite(p75) and np.isfinite(med)): return np.nan
    if med<=0: return np.nan
    v=(p75-p25)/med
    return float(v) if np.isfinite(v) else np.nan

def compute_feat_series(r: pd.Series, w_rr: int):
    feats=[]
    idx_start=ALB
    for t in range(idx_start, len(r)):
        win=r.iloc[t-w_rr:t].to_numpy(dtype=float)
        if win.size!=w_rr or not np.all(np.isfinite(win)):
            feats.append(np.nan); continue
        std_w=float(np.std(win))
        if not np.isfinite(std_w) or std_w<=0:
            feats.append(np.nan); continue
        X=np.column_stack([win[:-1],win[1:]])
        eps=EPS_SCALE*std_w
        d=np.max(np.abs(X[:,None,:]-X[None,:,:]),axis=2)
        Rm=(d<=eps+1e-18).astype(float)
        feats.append(_pct_spread(Rm,W_MIN))
    return pd.Series(feats, index=r.index[idx_start:idx_start+len(feats)]).replace([np.inf,-np.inf],np.nan)

def eval_combo(feat: pd.Series, r: pd.Series, entry_z: float, exit_z: float):
    rets=r.loc[feat.index].shift(-1).dropna()
    feat2=feat.loc[rets.index]
    splits=wf_splits(len(feat2),TRAIN,TEST,STEP)
    if len(splits)==0:
        return None
    pos=pd.Series(0.0,index=feat2.index)
    for (s0,tr_e,te_e) in splits:
        f_tr=feat2.iloc[s0:tr_e]; f_te=feat2.iloc[tr_e:te_e]
        f_tr_c=f_tr.dropna()
        if f_tr_c.shape[0]<50: continue
        mu=float(f_tr_c.mean()); sig=float(f_tr_c.std(ddof=0))
        if not np.isfinite(sig) or sig<=0: continue
        z=(f_te-mu)/sig
        for ti,zz in z.dropna().items():
            if zz>entry_z: pos.at[ti]=-1.0
            elif zz<-entry_z: pos.at[ti]=1.0
            else: pos.at[ti]=0.0
    arr=pos.to_numpy(dtype=float).copy()
    i=1
    while i<len(arr):
        if arr[i-1]!=0 and arr[i]==0:
            carry=arr[i-1]; j=i; held=0
            while j<len(arr) and arr[j]==0 and held<MAX_HOLD:
                arr[j]=carry; j+=1; held+=1
            i=j
        else: i+=1
    pos=pd.Series(arr,index=feat2.index)
    npn=rets.to_numpy(dtype=float); ppn=pos.to_numpy(dtype=float); bh=npn.copy()
    any_exp=bool((np.abs(pos.shift(1).fillna(0.0))>0).any())
    per_cost={}
    strat_means=[]; bh_means=[]
    for fee,slp in COST_GRID:
        ck=f"fee{fee}_slip{slp}"; tc=(fee+slp)/10000.0
        trades=np.abs(np.diff(np.concatenate([[0.0],ppn])))
        strat=ppn*npn - trades*tc
        oos_s=[]; oos_b=[]
        for (_,tr_e,te_e) in splits:
            oos_s.extend(strat[tr_e:te_e].tolist()); oos_b.extend(bh[tr_e:te_e].tolist())
        os=np.array(oos_s,dtype=float); ob=np.array(oos_b,dtype=float)
        per_cost[ck]={"oos_net_sum":float(os.sum()),"oos_net_mean":float(os.mean()) if os.size else np.nan,"bh_oos_net_mean":float(ob.mean()) if ob.size else np.nan}
    oos_mask=np.zeros(len(npn),dtype=bool)
    for (_,tr_e,te_e) in splits: oos_mask[tr_e:te_e]=True
    strat_means=float((ppn*npn)[oos_mask].mean()) if oos_mask.any() else np.nan
    bh_means=float(bh[oos_mask].mean()) if oos_mask.any() else np.nan
    return {"per_cost":per_cost,"any_exposure":any_exp,"strat_mean_oos":strat_means,"bh_mean_oos":bh_means,"n_splits":len(splits)}

def main():
    spot_df=load_spot(); vol_df, vol_report=load_volume()
    common=sorted(set(spot_df.columns).intersection(set(vol_df.columns)))
    c273=json.loads(C273_OOS.read_text())
    baseline_cross=c273['cross_asset']['oos_net_sums']
    # precompute returns + features per (sym,w_rr)
    per_sym={}
    for sym in common:
        sp=spot_df[sym].dropna(); vv=vol_df[sym].dropna()
        idx=sp.index.intersection(vv.index); sp=sp.loc[idx]; vv=vv.loc[idx]
        r=np.log(vv).diff().dropna()
        per_sym[sym]={'r':r,'feats':{}}
        for w in WRR_GRID:
            if len(r) < ALB + TRAIN + TEST + 50:
                per_sym[sym]['feats'][w]=None
            else:
                per_sym[sym]['feats'][w]=compute_feat_series(r,w)
    combos=[]
    for w in WRR_GRID:
        for ez in ENTRY_GRID:
            for xz in EXIT_GRID:
                if xz >= ez: continue
                combos.append({'W_RR':w,'ENTRY_Z':ez,'EXIT_Z':xz})
    grid_results=[]
    edge_positive_count=0
    for combo in combos:
        w=combo['W_RR']; ez=combo['ENTRY_Z']; xz=combo['EXIT_Z']
        cross={k:0.0 for k in COST_KEYS}
        any_exp=False; strat_ms=[]; bh_ms=[]
        ok=0
        for sym in common:
            r=per_sym[sym]['r']; feat=per_sym[sym]['feats'].get(w)
            if feat is None: continue
            if feat.dropna().shape[0] < TRAIN + TEST + 10: continue
            res=eval_combo(feat,r,ez,xz)
            if res is None: continue
            ok+=1
            if res['any_exposure']: any_exp=True
            strat_ms.append(res['strat_mean_oos']); bh_ms.append(res['bh_mean_oos'])
            for ck in COST_KEYS:
                cross[ck]+=res['per_cost'][ck]['oos_net_sum']
        all_pos=all(v>0 for v in cross.values())
        beat_bh=(np.nanmean(strat_ms)>np.nanmean(bh_ms)) if strat_ms and bh_ms else False
        edge=bool(any_exp and all_pos and beat_bh)
        if edge: edge_positive_count+=1
        is_baseline=(w==168 and ez==1.5 and xz==0.5)
        grid_results.append({
            'params': combo, 'is_baseline': is_baseline,
            'cross_asset_oos_net_sums': cross,
            'oos_edge_proven': edge, 'any_exposure_oos': any_exp,
            'all_cost_slices_positive_oos_net_sum': all_pos,
            'all_cost_slices_beat_bh_mean_rule': bool(beat_bh),
            'ok_assets': ok,
        })
    total=len(grid_results)
    # neighborhood stats
    all_pos_any=sum(1 for r in grid_results if r['all_cost_slices_positive_oos_net_sum'])
    share=edge_positive_count/total if total else 0
    # compare to baseline
    baseline_res=next((r for r in grid_results if r['is_baseline']), None)
    baseline_match=None
    if baseline_res:
        diffs={ck: baseline_res['cross_asset_oos_net_sums'][ck]-baseline_cross[ck] for ck in COST_KEYS}
        baseline_match=all(abs(v)<=1e-9 for v in diffs.values())
    if share>=0.7 and edge_positive_count>=1:
        assessment='robust_neighborhood'
    elif share>=0.4:
        assessment='moderately_sensitive'
    else:
        assessment='fragile_to_params'
    out={
        'generated_at_utc': ts,
        'campaign': 273,
        'analysis': 'parameter_perturbation_sensitivity',
        'strategy_id': 'VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_PERCENTILE_SPREAD_SHOCK_MR',
        'source_c273_oos': str(C273_OOS.relative_to(root)),
        'source_c273_oos_sha256': sha256_file(C273_OOS),
        'baseline_cross_asset_oos_net_sums': baseline_cross,
        'grid_spec': {
            'W_RR': WRR_GRID, 'ENTRY_Z': ENTRY_GRID, 'EXIT_Z': EXIT_GRID,
            'constraint': 'EXIT_Z < ENTRY_Z',
            'fixed': {'ALB':ALB,'m':M_EMB,'tau':TAU,'eps_scale':EPS_SCALE,'w_min':W_MIN,'MAX_HOLD':MAX_HOLD,'TRAIN':TRAIN,'TEST':TEST,'STEP':STEP,'cost_grid_bps':COST_GRID},
            'rationale': 'Bounded local perturbations around C273 baseline to assess edge stability over window length and z-thresholds on identical real cached data/WF/cost framework; ALB fixed at 336 >=2*max(W_RR).'
        },
        'total_combos': total,
        'edge_positive_combos': edge_positive_count,
        'edge_positive_share': share,
        'combos_all_cost_slices_positive': all_pos_any,
        'baseline_reproduced_in_grid': baseline_match,
        'baseline_grid_result': baseline_res,
        'sensitivity_assessment': assessment,
        'grid_results': grid_results,
        'volume_validation': vol_report,
        'provenance': {'real_data_only': True, 'network_refetch': False, 'synthetic_data': False, 'caches': {'spot': str(SPOT_CACHE.relative_to(root)), 'spot_sha256': sha256_file(SPOT_CACHE)}},
    }
    op=reports/f'campaign273_param_sensitivity_{ts}.json'
    op.write_text(json.dumps(out, indent=2, default=str)+'\n')
    print(json.dumps({'artifact':str(op.relative_to(root)),'sha256':sha256_file(op),'total_combos':total,'edge_positive_combos':edge_positive_count,'edge_positive_share':share,'combos_all_cost_slices_positive':all_pos_any,'baseline_reproduced_in_grid':baseline_match,'sensitivity_assessment':assessment,'script_sha256':sha256_file(Path(__file__))}, indent=2))

if __name__=='__main__':
    main()
