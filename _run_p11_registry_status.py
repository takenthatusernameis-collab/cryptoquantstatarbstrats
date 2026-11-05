import json, glob, os
from pathlib import Path
from datetime import datetime, timezone
root=Path('/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats')
reports=root/'reports'
ts=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
now=datetime.now(timezone.utc).isoformat()
pytest={'command':'PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages /home/runner/work/_temp/kilo-home/.local/bin/pytest -q',
        'passed':832,'skipped':1,'failed':0,'warnings':3573,'duration_s':40.20,'scope':'full tests/','note':'rerun P11 session'}

# Feed unblock status (covers P10 gap)
feed={
 'report':'real_feed_unblock_status','generated_at_utc':now,
 'mandate':'PRIORITY 11 / Campaign #7 Deliverable 2 — honest re-check for newly added real feeds with provenance; covers missing P10 artifact. No fabrication/proxies.',
 'provenance':{'real_data_only':True,'fabricated_data':False,'fail_closed':True,'no_threshold_weakening':True,'new_external_feeds':False},
 'recheck':{'cache_dir':'data/cache',
            'new_real_feed_files_with_provenance_found':[],
            'spot_1h_caches_verified':'11 assets 2026-04-01..2026-10-30 1h present (unchanged)',
            'notes':'No genuinely new real feed files with provenance added (funding/basis/spot-perp/dual-venue/real IV/vol surface). Only existing spot 1h caches + prior artifacts.'},
 'assessment':{'cross_exchange_dual_venue_same_asset':'blocked_no_real_feed',
               'funding_basis_carry':'blocked_no_real_feed',
               'term_structure_real_iv_vol_surface':'blocked_no_real_feed',
               'pairs_cointegration':'PROVEN BLOCKED on current real cached universe/window (fail-closed); do not re-scan without NEW real dataset'},
 'required_schemas_still_needed':{
   'funding_basis_carry':['perp/spot/funding timestamps aligned','fees/carry costs','real exchange provenance','net-of-cost validation'],
   'cross_exchange_dual_venue':['same-asset dual venue prices with timestamps','fees/transfer constraints','real provenance','fail-closed arb test'],
   'term_structure_real_iv_vol_surface':['real listed IV/vol surface by expiry/strike or term structure','fees/margin assumptions stated','real provider provenance','net-of-cost validation']},
 'references':{'inventory':'reports/real_feed_inventory_20261105T084255Z.json',
               'unblock_plan':'reports/real_feed_unblock_plan_20261105T084447Z.json',
               'prior_status_p9':'reports/real_feed_unblock_status_20261105T095713Z.json'},
 'validation_run':'none_ingested_no_new_real_feeds_with_provenance'}
fpath=reports/f'real_feed_unblock_status_{ts}.json'
json.dump(feed,open(fpath,'w'),indent=2)

# Load latest costed artifacts for key metrics
def load_latest(pattern):
    fs=sorted(glob.glob(str(reports/pattern)))
    return fs[-1] if fs else None

p10=load_latest('spot_residual_momentum_costed_oos_20261105T100459Z.json')
p11=load_latest('spot_leadlag_diffusion_costed_oos_*.json')
p9=load_latest('spot_zscore_regime_mean_reversion_costed_oos_20261105T095617Z.json')

def agg(path):
    if not path: return {}
    d=json.load(open(path))
    return d.get('aggregate',{})

a10=agg(p10); a11=agg(p11); a9=agg(p9)

# Build registry superseding latest
reg={
 'report':'strategy_edge_registry','supersedes':'reports/strategy_edge_registry_20261105T095736Z.json',
 'generated_at_utc':now,
 'mandate':'PRIORITY 11 / Campaign #7 Deliverable 3 — superseding registry: adds P10 residual_momentum (covered gap) + P11 lead-lag diffusion (structurally new) + feed status; fail-closed, real data only, no threshold weakening. Pairs unchanged/blocked.',
 'provenance':{'real_data_only':True,'fabricated_data':False,'fail_closed':True,'no_threshold_weakening':True,'new_external_feeds':False,'proxies':False},
 'pytest':pytest,
 'new_artifacts_this_session':[os.path.basename(p11) if p11 else 'spot_leadlag_diffusion_costed_oos_missing', os.path.basename(fpath), None],
 'real_feed_status':{'inventory_artifact':'reports/real_feed_inventory_20261105T084255Z.json',
   'unblock_plan_artifact':'reports/real_feed_unblock_plan_20261105T084447Z.json',
   'feed_unblock_status_artifact':os.path.basename(fpath),
   'cross_exchange_dual_venue':'blocked_no_real_feed','funding_basis_carry':'blocked_no_real_feed',
   'term_structure_real_iv_vol_surface':'blocked_no_real_feed',
   'pairs_cointegration':'PROVEN BLOCKED on current real cached universe/window (fail-closed); do not re-scan without NEW real dataset'},
 'families':[
   {'family':'pairs_cointegration','data_status':'real_cached_verified',
    'diagnostic_evidence':[{'artifact':'reports/pairs_failclosed_audit_20261105T075431Z.json','key_metrics':{'n_audited':165,'n_diagnostic_blocked':165,'overall_pass_fail_closed':True}}],
    'strategy_honors_fail_closed':{'verified':True},
    'actionable_next_step':'PROVEN BLOCKED (unchanged). Do not re-scan/weaken gates without genuinely NEW real dataset + new fail-closed audit.'},
   {'family':'momentum','data_status':'real_cached_verified','diagnostic_evidence':[{'artifact':'reports/momentum_mr_costed_oos_20261105T081323Z.json','key_metrics':{'n_oos_edge_proven':0}}],'strategy_honors_fail_closed':{'verified':True},'actionable_next_step':'NO PROVEN NET-OF-COST OOS EDGE (0/11). Unchanged.'},
   {'family':'mean_reversion','data_status':'real_cached_verified','diagnostic_evidence':[{'artifact':'reports/momentum_mr_costed_oos_20261105T081323Z.json','key_metrics':{'n_oos_edge_proven':0}}],'strategy_honors_fail_closed':{'verified':True},'actionable_next_step':'NO PROVEN NET-OF-COST OOS EDGE (0/11). Unchanged.'},
   {'family':'cross_sectional_risk_adjusted_return_rank','data_status':'real_cached_verified','diagnostic_evidence':[{'artifact':'reports/spot_alt_signal_costed_oos_20261105T084619Z.json','key_metrics':{'oos_edge_proven':False}}],'strategy_honors_fail_closed':{'verified':True},'actionable_next_step':'NO PROVEN NET-OF-COST OOS EDGE. Unchanged.'},
   {'family':'donchian_breakout_volfilter','data_status':'real_cached_verified','diagnostic_evidence':[{'artifact':'reports/spot_breakout_volfilter_costed_oos_20261105T093626Z.json','key_metrics':{'oos_edge_proven':False,'n_oos_edge_proven':0}}],'strategy_honors_fail_closed':{'verified':True},'actionable_next_step':'NO PROVEN NET-OF-COST OOS EDGE (0/11). Unchanged.'},
   {'family':'range_breakout_reversion_volband','data_status':'real_cached_verified','diagnostic_evidence':[{'artifact':'reports/spot_range_breakout_reversion_volband_costed_oos_20261105T094822Z.json','key_metrics':{'oos_edge_proven':False,'n_oos_edge_proven':0}}],'strategy_honors_fail_closed':{'verified':True},'actionable_next_step':'NO PROVEN NET-OF-COST OOS EDGE (0/11). Unchanged.'},
   {'family':'spot_zscore_regime_mean_reversion_pairs','data_status':'real_cached_verified','diagnostic_evidence':[{'artifact':'reports/spot_zscore_regime_mean_reversion_costed_oos_20261105T095617Z.json','key_metrics':{'n_pairs':55,'n_oos_edge_proven':a9.get('n_oos_edge_proven',0),'aggregate_oos_edge_proven_fail_closed':a9.get('aggregate_oos_edge_proven_fail_closed',False),'window':'2026-04-01..2026-10-30 1h','per_named':a9.get('per_named',{})}}],'strategy_honors_fail_closed':{'verified':True},'actionable_next_step':'NO PROVEN NET-OF-COST OOS EDGE (0/11). Structurally different (pairwise OLS-hedge spread MR) but fails net-of-cost/benchmark rule. Unchanged.'},
   {'family':'spot_residual_momentum','data_status':'real_cached_verified','diagnostic_evidence':[{'artifact':'reports/spot_residual_momentum_costed_oos_20261105T100459Z.json','key_metrics':{'n_oos_edge_proven':a10.get('n_oos_edge_proven',0),'aggregate_oos_edge_proven_fail_closed':a10.get('aggregate_oos_edge_proven_fail_closed',False),'n_assets_all_slices_oos_net_positive':a10.get('n_assets_all_slices_oos_net_positive',0),'n_assets_all_slices_beat_benchmark':a10.get('n_assets_all_slices_beat_benchmark',0),'window':'2026-04-01..2026-10-30 1h','per_named':a10.get('per_named',{})}}],'strategy_honors_fail_closed':{'verified':True},'actionable_next_step':'NO PROVEN NET-OF-COST OOS EDGE (0/11). Causal idiosyncratic residual momentum (P10). BTC gross>BH at 0bps but fails costs/all-slice+benchmark rule. Unchanged unless new hypothesis.'},
   {'family':'spot_leadlag_diffusion','data_status':'real_cached_verified','diagnostic_evidence':[{'artifact':os.path.basename(p11) if p11 else None,'key_metrics':{'n_oos_edge_proven':a11.get('n_oos_edge_proven',0),'aggregate_oos_edge_proven_fail_closed':a11.get('aggregate_oos_edge_proven_fail_closed',False),'n_assets_all_slices_oos_net_positive':a11.get('n_assets_all_slices_oos_net_positive',0),'n_assets_all_slices_beat_benchmark':a11.get('n_assets_all_slices_beat_benchmark',0),'window':'2026-04-01..2026-10-30 1h','per_named':a11.get('per_named',{})}}],'strategy_honors_fail_closed':{'verified':True},'actionable_next_step':'NO PROVEN NET-OF-COST OOS EDGE (0/11). P11 causal lead-lag diffusion (train-selected leader+lag, lagged leader z-score). Structurally different from P4-P10; fails net-of-cost/benchmark rule.'},
   {'family':'cross_exchange_dual_venue_arbitrage','data_status':'no_real_feed','diagnostic_evidence':[],'strategy_honors_fail_closed':{'verified':None},'actionable_next_step':'BLOCKED_NO_REAL_FEED. Ingest real dual-venue same-asset feed with provenance; validate fail-closed.'},
   {'family':'funding_basis_carry','data_status':'no_real_feed','diagnostic_evidence':[],'strategy_honors_fail_closed':{'verified':None},'actionable_next_step':'BLOCKED_NO_REAL_FEED. Ingest real perp/spot/funding feed with provenance; validate fail-closed net-of-carry/costs.'},
   {'family':'term_structure_vol_arbitrage_real_iv','data_status':'no_real_feed','diagnostic_evidence':[],'strategy_honors_fail_closed':{'verified':None},'actionable_next_step':'BLOCKED_NO_REAL_FEED. Ingest real listed IV/vol surface with provenance; validate fail-closed net-of-costs.'}
 ],
 'top_priority_next':{
   'blocked_real_feeds':{'cross_exchange_dual_venue':'blocked_no_real_feed','funding_basis_carry':'blocked_no_real_feed','term_structure_real_iv_vol_surface':'blocked_no_real_feed','pairs_cointegration':'PROVEN BLOCKED on current real cached universe/window (no re-scan, no weakening)'},
   'spot_1h_cached_status':'EXHAUSTED across tested structurally distinct families on 11-asset 2026-04-01..2026-10-30 1h (P4 raw mom/MR, P5 xsec rank, P6 Donchian, P7 range breakout-reversion+volband, P9 pairwise OLS-hedge spread MR, P10 residual momentum, P11 lead-lag diffusion): 0/11 net-of-cost OOS edge proven each. All obvious/pre-stated structurally distinct spot-only hypotheses on this window appear exhausted.',
   'recommendation':'NEXT SESSION: (1) if NO new real feed/provenance ingested, produce Path C spot_universe_exhausted_memo with explicit remaining micro-hypotheses ruled out + feed acquisition checklist + 2 other artifacts; do NOT repeat structurally similar tests. (2) if new real feed IS ingested, validate fail-closed net-of-cost OOS. No fabrication/proxies/threshold weakening.'
 },
 'notes':['No family has proven net-of-cost OOS edge on real cached data.','Pairs 165/165 blocked unchanged; no weakening.','Real feed families remain blocked by absence of real provenance data.','P10/P11 added; registry covers P10 gap.','Spot-only structurally distinct families on current window appear exhausted (fail-closed).']
}
rpath=reports/f'strategy_edge_registry_{ts}.json'
reg['new_artifacts_this_session'][2]=os.path.basename(rpath)
json.dump(reg,open(rpath,'w'),indent=2)
print(fpath)
print(rpath)
print(json.dumps({'p10':a10.get('n_oos_edge_proven'),'p11':a11.get('n_oos_edge_proven')},indent=2))
