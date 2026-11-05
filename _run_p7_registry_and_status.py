import json, glob, os
from pathlib import Path
from datetime import datetime, timezone
root=Path('/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats')
reports=root/'reports'
ts=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
# B
status={
  "report":"real_feed_unblock_status",
  "generated_at_utc":datetime.now(timezone.utc).isoformat(),
  "mandate":"PRIORITY 7 / Campaign #3 Deliverable B — re-check for newly added real feeds; honest blocked_no_real_feed if none. If genuinely new real feeds with provenance present, ingest + smallest fail-closed validation (not applicable).",
  "provenance":{"real_data_only":True,"fabricated_data":False,"fail_closed":True,"no_threshold_weakening":True},
  "recheck":{"cache_dir":"data/cache","repo_scan":"for funding/basis/perp_spot/dualvenue/iv_surface/vol_surface_term files with provenance (excluding blocked/status/inventory/unblock plan artifacts and code)",
             "new_real_feed_files_with_provenance_found":[],"notes":"Only known blocked/status artifacts found (e.g. reports/funding_basis_blocked_20261105T075839Z.json). No genuinely new real feed files with provenance added."},
  "assessment":{
    "cross_exchange_dual_venue_same_asset":"blocked_no_real_feed",
    "funding_basis_carry":"blocked_no_real_feed",
    "term_structure_real_iv_vol_surface":"blocked_no_real_feed"
  },
  "references":{
    "inventory":"reports/real_feed_inventory_20261105T084255Z.json",
    "unblock_plan":"reports/real_feed_unblock_plan_20261105T084447Z.json",
    "prior_status_p6":"reports/real_feed_unblock_status_20261105T093642Z.json"
  },
  "required_schemas_still_needed":{
    "funding_basis_carry":["perp/spot/funding timestamps aligned","fees/carry costs","real exchange provenance","net-of-cost validation"],
    "cross_exchange_dual_venue":["same-asset dual venue prices with timestamps","fees/transfer constraints","real provenance","fail-closed arb test"],
    "term_structure_real_iv_vol_surface":["real listed IV/vol surface by expiry/strike or term structure","fees/margin assumptions stated","real provider provenance","net-of-cost validation"]
  },
  "validation_run":"none_ingested_no_new_real_feeds_with_provenance"
}
bpath=reports/f'real_feed_unblock_status_{ts}.json'
json.dump(status, open(bpath,'w'), indent=2)
# C
prev_reg='reports/strategy_edge_registry_20261105T093702Z.json'
p7a='reports/spot_range_breakout_reversion_volband_costed_oos_20261105T094822Z.json'
p7a_d=json.load(open(root/p7a))
# build compact family entry
fam={
 "family":"range_breakout_reversion_volband",
 "data_status":"real_cached_verified",
 "diagnostic_evidence":[{"artifact":p7a,
   "key_metrics":{
     "assets":p7a_d['aggregate']['n_assets'],
     "bars_expected":5112,"window":"2026-04-01..2026-10-30","interval":"1h",
     "walk_forward":p7a_d['config']['walk_forward'],
     "cost_grid_bps_fee_slippage":p7a_d['config']['cost_grid_bps_fee_slippage'],
     "n_oos_edge_proven":p7a_d['aggregate']['n_oos_edge_proven'],
     "n_assets_all_slices_oos_net_positive":p7a_d['aggregate']['n_assets_all_slices_oos_net_positive'],
     "n_assets_all_slices_beat_benchmark":p7a_d['aggregate']['n_assets_all_slices_beat_benchmark'],
     "aggregate_oos_edge_proven_fail_closed":p7a_d['aggregate']['aggregate_oos_edge_proven_fail_closed'],
     "per_named":{
       k:{"oos_edge_proven":p7a_d['by_asset'][k]['oos_edge_proven'],
          "exposure":p7a_d['by_asset'][k]['exposure'],
          "oos_0bps_sum":p7a_d['by_asset'][k]['cost_slices']['fee0_slip0_bps']['oos_net_sum'],
          "bench_bh_oos_0bps_sum":p7a_d['by_asset'][k]['cost_slices']['fee0_slip0_bps']['bench_bh_oos_sum'],
          "oos_40bps_sum":p7a_d['by_asset'][k]['cost_slices']['fee20_slip20_bps']['oos_net_sum']} for k in ['BTC','ETH','SOL','BNB'] if k in p7a_d['by_asset']
     },
     "pre_stated_rule":p7a_d['config']['pre_stated_oos_edge_proven_rule'],
     "genuinely_different_from_p6_donchian_volfilter":True
   }}],
 "strategy_honors_fail_closed":{"verified":True,"method":"report flags real_data_only/fabricated_data=false/fail_closed/no_threshold_weakening/new_external_feeds=false/proxies=false; pre-stated rule applied"},
 "actionable_next_step":"NO PROVEN NET-OF-COST OOS EDGE (0/11) for range_breakout_reversion_volband on real cached spot 1h 2026-04-01..2026-10-30 (rolling 30d/7d, 0-40bps). Do not claim edge; do not tune in-sample. Deprioritize this exact spec until genuinely new real data/structure exists; pursue only pre-registered hypotheses on unseen real data."
}
reg={
 "report":"strategy_edge_registry",
 "supersedes":prev_reg,
 "generated_at_utc":datetime.now(timezone.utc).isoformat(),
 "mandate":"PRIORITY 7 / Campaign #3 Deliverable C — superseding registry: adds Deliverable A (range_breakout_reversion_volband, real cached spot, net-of-cost WF IS/OOS vs B&H) + Deliverable B feed status; fail-closed, real data only, no threshold weakening. Pairs unchanged/blocked.",
 "provenance":{"real_data_only":True,"fabricated_data":False,"fail_closed":True,"no_threshold_weakening":True,"new_external_feeds":False,"proxies":False},
 "pytest":{"command":"PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages /home/runner/work/_temp/kilo-home/.local/bin/pytest -q","passed":832,"skipped":1,"warnings":3573,"failed":0,"duration_s":42.42,"scope":"full tests/","note":"rerun this P7 session with env deps on PYTHONPATH"},
 "new_artifacts_this_session":[p7a, str(bpath.relative_to(root))],
 "real_feed_status":{
   "inventory_artifact":"reports/real_feed_inventory_20261105T084255Z.json",
   "unblock_plan_artifact":"reports/real_feed_unblock_plan_20261105T084447Z.json",
   "feed_unblock_status_artifact":str(bpath.relative_to(root)),
   "cross_exchange_dual_venue":"blocked_no_real_feed",
   "funding_basis_carry":"blocked_no_real_feed",
   "term_structure_real_iv_vol_surface":"blocked_no_real_feed",
   "pairs_cointegration":"PROVEN BLOCKED on current real cached universe/window (fail-closed); do not re-scan without NEW real dataset"
 },
 "families":[
   {"family":"pairs_cointegration","data_status":"real_cached_verified","diagnostic_evidence":[{"artifact":"reports/pairs_failclosed_audit_20261105T075431Z.json","key_metrics":{"n_audited":165,"n_diagnostic_blocked":165,"n_breaches_fail_closed":0,"overall_pass_fail_closed":True,"universe":"11 symbols x 55 pairs x {1h,4h,1d}=165","window":"2026-04-01..2026-10-30 Binance spot cached"}},{"artifact":"reports/pairs_leg_stationarity_impossibility_memo_20261105T065521Z.json","key_metrics":"leg-stationarity impossibility on cached universe (prior evidence)"}],"strategy_honors_fail_closed":{"verified":True},"actionable_next_step":"PROVEN BLOCKED (unchanged). Do not re-scan/weaken gates without genuinely NEW real dataset + new fail-closed audit."},
   {"family":"momentum","data_status":"real_cached_verified","diagnostic_evidence":[{"artifact":"reports/momentum_mr_costed_oos_20261105T081323Z.json","key_metrics":{"n_oos_edge_proven":0,"aggregate_oos_edge_proven_fail_closed":False,"window":"2026-04-01..2026-10-30 1h"}}],"strategy_honors_fail_closed":{"verified":True},"actionable_next_step":"NO PROVEN NET-OF-COST OOS EDGE (0/11). Unchanged."},
   {"family":"mean_reversion","data_status":"real_cached_verified","diagnostic_evidence":[{"artifact":"reports/momentum_mr_costed_oos_20261105T081323Z.json","key_metrics":{"n_oos_edge_proven":0,"aggregate_oos_edge_proven_fail_closed":False,"window":"2026-04-01..2026-10-30 1h"}}],"strategy_honors_fail_closed":{"verified":True},"actionable_next_step":"NO PROVEN NET-OF-COST OOS EDGE (0/11). Unchanged."},
   {"family":"cross_sectional_risk_adjusted_return_rank","data_status":"real_cached_verified","diagnostic_evidence":[{"artifact":"reports/spot_alt_signal_costed_oos_20261105T084619Z.json","key_metrics":{"oos_edge_proven":False,"window":"2026-04-01..2026-10-30 1h"}}],"strategy_honors_fail_closed":{"verified":True},"actionable_next_step":"NO PROVEN NET-OF-COST OOS EDGE. Unchanged."},
   {"family":"donchian_breakout_volfilter","data_status":"real_cached_verified","diagnostic_evidence":[{"artifact":"reports/spot_breakout_volfilter_costed_oos_20261105T093626Z.json","key_metrics":{"oos_edge_proven":False,"aggregate_oos_edge_proven_fail_closed":False,"window":"2026-04-01..2026-10-30 1h"}}],"strategy_honors_fail_closed":{"verified":True},"actionable_next_step":"NO PROVEN NET-OF-COST OOS EDGE. Unchanged (NOT same as P7 family)."},
   fam,
   {"family":"cross_exchange_same_asset_dual_venue","data_status":"blocked_no_real_feed","diagnostic_evidence":[{"artifact":"reports/cross_exchange_real_market.json","key_metrics":"single-venue only, not native dual-venue"}],"strategy_honors_fail_closed":{"verified":True},"actionable_next_step":"Blocked until cached dual-venue same-asset OHLCV with provenance + fees/transfer constraints."},
   {"family":"funding_basis_carry","data_status":"blocked_no_real_feed","diagnostic_evidence":[{"artifact":"reports/funding_basis_blocked_20261105T075839Z.json","key_metrics":"blocked no real feed"}],"strategy_honors_fail_closed":{"verified":True},"actionable_next_step":"Blocked until cached real funding/basis series with provenance."},
   {"family":"term_structure_carry_proxy","data_status":"blocked_no_real_feed","actionable_next_step":"Blocked (no real feed)."},
   {"family":"volatility_surface_arbitrage_proxy","data_status":"blocked_no_real_feed","actionable_next_step":"Blocked until real listed IV/vol surface by expiry/strike with provenance."}
 ],
 "summary":{
   "pairs_cointegration":"PROVEN BLOCKED (fail-closed) — unchanged.",
   "momentum":"NO PROVEN NET-OF-COST OOS EDGE (0/11) — unchanged.",
   "mean_reversion":"NO PROVEN NET-OF-COST OOS EDGE (0/11) — unchanged.",
   "cross_sectional_risk_adjusted_return_rank":"NO PROVEN NET-OF-COST OOS EDGE — unchanged.",
   "donchian_breakout_volfilter":"NO PROVEN NET-OF-COST OOS EDGE — unchanged (P6).",
   "range_breakout_reversion_volband":"NO PROVEN NET-OF-COST OOS EDGE (0/11, fail-closed) on real cached spot 1h 2026-04-01..2026-10-30, rolling 30d/7d, 0-40bps (P7, genuinely different from P6).",
   "blocked_no_real_feed":["cross_exchange_dual_venue","funding_basis_carry","term_structure_real_iv_vol_surface"],
   "overall":"No proven net-of-cost OOS edge on any tested family with available real data. Blocked families remain honest/unchanged. Pairs remain proven blocked."
 }
}
cpath=reports/f'strategy_edge_registry_{ts}.json'
json.dump(reg, open(cpath,'w'), indent=2)
print(bpath); print(cpath)
