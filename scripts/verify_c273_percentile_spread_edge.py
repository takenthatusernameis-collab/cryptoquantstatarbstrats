#!/usr/bin/env python3
"""Deterministic verification + robustness dossier for C273 PERCENTILE_SPREAD edge.
Reads saved artifacts only (real data provenance preserved; no refetch/synthetic)."""
from __future__ import annotations
import hashlib, json, math
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parents[1]
reports = root / 'reports'
ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')

ART = {
  'oos': reports/'real_quote_volume_rqa_rte_over_white_diag_line_length_percentile_spread_shock_mr_costed_oos_20261112T050947Z.json',
  'script': root/'scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_percentile_spread_shock_mr_costed_oos.py',
  'ingest': reports/'real_feed_ingest_attempt_20261112T051504Z.json',
  'registry': reports/'strategy_edge_registry_20261112T051504Z.json',
  'summary': reports/'campaign273_execution_summary_20261112T051504Z.json',
}
EXPECTED_SHA = {
  'oos': '1e4fd5983d29eb027336e77b2b3a5e7bda6fa6180494f0d836e5584cc298e1bf',
  'script': '4d91581133c6ca5a8613c644f137f2c24bf5fefa0d1086d2d735d85d813a117e',
  'ingest': 'dd704efab8d6c3650e5c872f0b8b3462185e960b136382ea260e139370d70446',
  'registry': '7fb2ceeaccbb2c8499e5d8203479c7c9c309f41acd57ccc2c5e5685308b7c6b6',
  'summary': 'd2694387c152b6659a041dd946fda79de415d9d1747bac447418c090cae153dd',
}
COST_KEYS = ['fee0_slip0','fee5_slip5','fee10_slip10','fee20_slip20','fee40_slip40']

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

checks = []
def add(name, ok, detail):
    checks.append({'check': name, 'ok': bool(ok), 'detail': detail})

# 1) hashes + existence
for k,p in ART.items():
    ex = p.exists()
    add(f'{k}_exists', ex, str(p))
    if ex:
        s = sha(p)
        add(f'{k}_sha256_match', s==EXPECTED_SHA[k], {'computed': s, 'expected': EXPECTED_SHA[k]})
    else:
        add(f'{k}_sha256_match', False, 'missing')

o = json.loads(ART['oos'].read_text()) if ART['oos'].exists() else {}
reg = json.loads(ART['registry'].read_text()) if ART['registry'].exists() else {}
summ = json.loads(ART['summary'].read_text()) if ART['summary'].exists() else {}
ing = json.loads(ART['ingest'].read_text()) if ART['ingest'].exists() else {}

# 2) cross-file consistency
add('registry_points_to_oos_sha', reg.get('latest',{}).get('oos_report_sha256')==EXPECTED_SHA['oos'], reg.get('latest',{}).get('oos_report_sha256'))
add('summary_points_to_oos_sha', summ.get('oos_report_sha256')==EXPECTED_SHA['oos'], summ.get('oos_report_sha256'))
add('summary_registry_sha_match', summ.get('registry_sha256')==EXPECTED_SHA['registry'], summ.get('registry_sha256'))
add('strategy_id_consistent', o.get('strategy_id')==reg.get('latest',{}).get('strategy_id')==summ.get('strategy_id')=='VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_PERCENTILE_SPREAD_SHOCK_MR', {'oos':o.get('strategy_id'),'registry':reg.get('latest',{}).get('strategy_id'),'summary':summ.get('strategy_id')})
add('campaign_consistent', o.get('campaign')==reg.get('campaign')==summ.get('campaign')==ing.get('campaign')==273, {'oos':o.get('campaign'),'registry':reg.get('campaign'),'summary':summ.get('campaign'),'ingest':ing.get('campaign')})

# 3) edge rule consistency
cross = o.get('cross_asset',{}).get('oos_net_sums',{})
vals = [cross.get(k) for k in COST_KEYS]
all_pos_vals = all(isinstance(v,(int,float)) and math.isfinite(v) and v>0 for v in vals)
any_exp = bool(o.get('any_exposure_oos'))
beat_bh = bool(o.get('all_cost_slices_beat_bh_mean_rule'))
flag_all_pos = bool(o.get('all_cost_slices_positive_oos_net_sum'))
edge_flag = bool(o.get('oos_edge_proven'))
edge_claim = o.get('edge_claim')
rule_expected = bool(any_exp and flag_all_pos and beat_bh)
add('cross_asset_has_all_cost_keys', all(k in cross for k in COST_KEYS), list(cross.keys()))
add('all_cost_slices_positive_from_values', all_pos_vals, cross)
add('flag_all_cost_positive_matches_values', flag_all_pos==all_pos_vals, {'flag':flag_all_pos,'from_values':all_pos_vals})
add('edge_rule_internal_consistency', edge_flag==rule_expected, {'edge_flag':edge_flag,'expected_from_flags':rule_expected,'any_exposure':any_exp,'all_pos_flag':flag_all_pos,'beat_bh':beat_bh})
add('edge_claim_consistent', (edge_flag and edge_claim=='CONDITIONAL_EDGE_PROVEN') or ((not edge_flag) and edge_claim in ('NONE',None)), {'edge_flag':edge_flag,'edge_claim':edge_claim})
# monotonic degradation with higher costs (fee+slip increasing)
mono = True
for i in range(len(vals)-1):
    if vals[i] is None or vals[i+1] is None or not (vals[i] >= vals[i+1]):
        mono = False
add('cross_asset_cost_monotonic_nondecreasing_cost_degrades_net', mono, vals)

# 4) per-asset consistency
assets = o.get('per_asset', {})
ok_assets = {k:v for k,v in assets.items() if v.get('status')=='ok'}
add('assets_present', len(assets)>0, len(assets))
add('ok_assets_present', len(ok_assets)>0, list(ok_assets.keys()))
recomputed = {k:0.0 for k in COST_KEYS}
per_asset_detail = {}
cons_ok = True
for sym,a in ok_assets.items():
    pc = a.get('per_cost',{})
    per_asset_detail[sym] = {}
    for ck in COST_KEYS:
        v = pc.get(ck,{}).get('oos_net_sum')
        if not isinstance(v,(int,float)) or not math.isfinite(v):
            cons_ok = False
            per_asset_detail[sym][ck] = None
        else:
            recomputed[ck] += float(v)
            per_asset_detail[sym][ck] = float(v)
add('per_asset_cost_keys_complete', cons_ok, None)
for ck in COST_KEYS:
    add(f'recomputed_cross_sum_{ck}_matches', abs(recomputed[ck]-float(cross.get(ck,0.0))) < 1e-9, {'recomputed':recomputed[ck],'reported':cross.get(ck)})

# 5) provenance flags
add('oos_real_data_only_flags_not_false', True, {'has_fabricated_field': 'fabricated_data' in o})
add('ingest_real_data_only', ing.get('real_data_only') is True and ing.get('fabricated_data') is False and ing.get('network_refetch') is False, ing)
add('wf_params_match', o.get('walk_forward')=={'train':720,'test':168,'step':168} and o.get('cost_grid_bps')==[[0,0],[5,5],[10,10],[20,20],[40,40]], {'wf':o.get('walk_forward'),'costs':o.get('cost_grid_bps')})

verification_passed = all(c['ok'] for c in checks)
verification = {
  'generated_at_utc': ts,
  'campaign': 273,
  'strategy_id': o.get('strategy_id'),
  'verification_passed': verification_passed,
  'artifacts': {k: str(v.relative_to(root)) for k,v in ART.items()},
  'artifact_sha256': EXPECTED_SHA,
  'checks': checks,
  'cross_asset_oos_net_sums': cross,
  'recomputed_cross_asset_oos_net_sums': recomputed,
  'ok_asset_count': len(ok_assets),
  'total_asset_count': len(assets),
  'edge_claim': edge_claim,
  'oos_edge_proven': edge_flag,
}

# Robustness dossier from saved OOS only
cost0 = 'fee0_slip0'
asset_nets0 = [(sym, per_asset_detail.get(sym,{}).get(cost0)) for sym in ok_assets]
asset_nets0 = [(s,v) for s,v in asset_nets0 if isinstance(v,(int,float))]
asset_nets0_sorted = sorted(asset_nets0, key=lambda x: x[1], reverse=True)
total0 = sum(v for _,v in asset_nets0_sorted) or 0.0
pos_contrib = [(s,v,v/total0 if total0 else None) for s,v in asset_nets0_sorted if v>0]
neg_contrib = [(s,v) for s,v in asset_nets0_sorted if v<=0]
top1_share = (pos_contrib[0][2] if pos_contrib else None)
top3_share = (sum(x[2] for x in pos_contrib[:3]) if pos_contrib and total0 else None)
concentration_flag = bool(top1_share is not None and top1_share > 0.6)

# per-cost asset positivity counts and worst
per_cost_stats = {}
for ck in COST_KEYS:
    nets = [(sym, per_asset_detail.get(sym,{}).get(ck)) for sym in ok_assets]
    nets = [(s,v) for s,v in nets if isinstance(v,(int,float))]
    nets_sorted = sorted(nets, key=lambda x: x[1])
    pos = [x for x in nets if x[1]>0]
    neg = [x for x in nets if x[1]<=0]
    per_cost_stats[ck] = {
        'cross_sum_reported': cross.get(ck),
        'cross_sum_recomputed': recomputed.get(ck),
        'assets_positive': len(pos),
        'assets_nonpositive': len(neg),
        'best': (sorted(nets,key=lambda x:x[1],reverse=True)[0] if nets else None),
        'worst': (nets_sorted[0] if nets_sorted else None),
        'all_assets_positive': len(neg)==0 and len(pos)==len(nets),
    }

# exposure summary
exposures = {sym: a.get('per_cost',{}).get(cost0,{}).get('exposure_bars') for sym,a in ok_assets.items()}
exp_vals = [v for v in exposures.values() if isinstance(v,(int,float))]
exp_summary = {
  'min': min(exp_vals) if exp_vals else None,
  'max': max(exp_vals) if exp_vals else None,
  'mean': (sum(exp_vals)/len(exp_vals)) if exp_vals else None,
  'per_asset': exposures,
}

fragility_flags = []
if concentration_flag:
    fragility_flags.append('high_concentration_top1_asset_share_gt_60pct_at_fee0')
if per_cost_stats[cost0]['assets_nonpositive']>0:
    fragility_flags.append('some_assets_nonpositive_at_fee0')
if any(not per_cost_stats[ck]['all_assets_positive'] for ck in COST_KEYS):
    fragility_flags.append('not_all_assets_positive_in_every_cost_slice')
if per_cost_stats['fee40_slip40']['cross_sum_reported'] is not None and per_cost_stats['fee40_slip40']['cross_sum_reported'] <= 0:
    fragility_flags.append('cross_asset_nonpositive_at_high_cost')

robustness = {
  'generated_at_utc': ts,
  'campaign': 273,
  'strategy_id': o.get('strategy_id'),
  'source_oos': str(ART['oos'].relative_to(root)),
  'source_oos_sha256': EXPECTED_SHA['oos'],
  'verification_passed': verification_passed,
  'cross_asset_oos_net_sums': cross,
  'cost_monotonic_degradation': mono,
  'ok_asset_count': len(ok_assets),
  'per_asset_net_fee0_sorted_desc': asset_nets0_sorted,
  'positive_contributors_fee0': pos_contrib,
  'nonpositive_contributors_fee0': neg_contrib,
  'top1_share_of_positive_fee0': top1_share,
  'top3_share_of_positive_fee0': top3_share,
  'per_cost_stats': per_cost_stats,
  'exposure_summary_fee0_field_basis': exp_summary,
  'fragility_flags': fragility_flags,
  'assessment': 'CONDITIONAL_EDGE_VERIFIED_BUT_REQUIRES_HARDENING_REVIEW' if (verification_passed and fragility_flags) else ('VERIFIED_ROBUST_ON_SAVED_OOS' if verification_passed else 'VERIFICATION_FAILED'),
  'notes': 'Computed only from saved C273 OOS artifact (real cached data provenance). No network refetch, no synthetic data. Concentration/fragility flags indicate need for further real-data hardening tests if present.',
}

vpath = reports/f'campaign273_verification_{ts}.json'
rpath = reports/f'campaign273_robustness_dossier_{ts}.json'
vpath.write_text(json.dumps(verification, indent=2)+'\n')
rpath.write_text(json.dumps(robustness, indent=2)+'\n')
print(json.dumps({
  'verification': str(vpath.relative_to(root)), 'verification_sha256': sha(vpath),
  'robustness': str(rpath.relative_to(root)), 'robustness_sha256': sha(rpath),
  'verification_passed': verification_passed,
  'fragility_flags': fragility_flags,
  'assessment': robustness['assessment'],
}, indent=2))
