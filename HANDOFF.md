# READ THIS FIRST — SINGLE DURABLE HANDOFF (UPDATED: 20261108T005856Z, C189 COMPLETE, NEXT=C190)
**Repo:** `cryptoquantstatarbstrats`. Fail-closed, **real-data-only** stat-arb edge validation — WF OOS 720/168/168, costs [[0,0],[5,5],[10,10],[20,20],[40,40]], B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C189 LOCKED.**

## VERIFIED BASELINE (20261108T005856Z)
- deps_ok (numpy/scipy/pandas). pytest 9.2.0 available.
- Caches present: `data/cache/volume_1h_full.pkl/meta/provenance`, spot `0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl/meta`.
- **C188 LOCKED**: OOS `reports/real_quote_volume_rqa_trend_over_det_ratio_shock_mr_costed_oos_20261108T005102Z.json`=efe782e49e1fa6219f05e424d1d9901a12e2cb020cd6d8d6f13d39cc7269ec4e (`VOLUME_RQA_TREND_OVER_DET_RATIO_SHOCK_MR`, `oos_edge_proven:false`, `edge_claim:NONE`). Ingest `reports/real_feed_ingest_attempt_20261108T005205Z.json`=512c4cd75525e519bd72aef01f9b825d569f7af3575c8c14b1f2e5acd821bac6. Registry `reports/strategy_edge_registry_20261108T005205Z.json`=aadd225ddaf2bcc83cff6a1c41bb35105c7b8e651e994f152cedb2bb2a04d640 supersedes C187 1aca1a556e00763cec77945c6c48085b2ba77b1c486932444510d8221124eeb9. Script=7f83353fa022dbce8e3dd41bf9e9a4dfeac6ed27b5a5ddc758fde09b1ded97dd. Summary=8de537217997a3ff773579fc6661b8c6ad198892e8052f2f1dc60c6028865bc0.
- **C189 COMPLETE/LOCKED**: OOS `reports/real_quote_volume_rqa_lavg_over_rr_ratio_shock_mr_costed_oos_20261108T005624Z.json`=dce56d7da8c20d31bf8e3e9436785a3e938c1280288a09db990a7405fa9104c9 (`VOLUME_RQA_LAVG_OVER_RR_RATIO_SHOCK_MR`, `oos_edge_proven:false`, `edge_claim:NONE`, exposure true, all-cost-positive false, beats-BH-mean false; cross fee0_slip0=1.2867126710259322→fee40_slip40=-1.361287328974068). Ingest `reports/real_feed_ingest_attempt_20261108T005732Z.json`=ad2c787ae4cc23a4e9e544e788ed9aadd715e13d84566395daf81af3e83e7fde (nonspot blocked fail-closed, `rb_unblocked:true`). Registry `reports/strategy_edge_registry_20261108T005732Z.json`=f6af7d1836b30576f4193ea0ddd2d79db41a19ff224b904e30ccf1e7e2420ee8 supersedes C188 aadd225ddaf2bcc83cff6a1c41bb35105c7b8e651e994f152cedb2bb2a04d640. Script=ecd31bdaea66e2151cc339cb11ffc5d608e0308a3d0f0a38abb8a501106b7397. Summary=18d619ef5b30cb9f1c2b7e5cf3b9b409727d475282a60176df128e767ed55da2. Distinctness grep: `LAVG_OVER_RR|...` non-self hits 0 (self-only script hits; verified 20261108T005856Z); LAM_OVER_DET had collisions and was not used.

## BOTTLENECKS REMOVED / NO EXCUSES (20261108T005856Z)
- C104–C189 locked with SHAs from bytes; no reruns, no stale cache re-scans, no gate/threshold weakening, no proxies labeled real.
- Deps/caches ready. Nonspot blocker does not block R-B on `real_quote_volume`.
- Single durable handoff = `HANDOFF.md` + `research_state/state.yaml`. **No status-only replies. No stop after status.**

## INITIAL TASK — C190 (MANDATORY, HEAVY WORK, START IMMEDIATELY)
**Execute C190 now.** Produce **>= 3 NEW concrete C190 report artifacts on disk** (OOS + ingest + registry/superseding + summary) **each with SHA256 computed from bytes**, plus OOS script and synced `research_state/state.yaml`.

### Primary candidate (preselected; run-time grep required)
`VOLUME_RQA_TT_OVER_RR_RATIO_SHOCK_MR` — RQA ratio **TT/RR** on delay-embedded log-volume returns. `TT` = trapping time = average length of vertical/laminar lines (v>=`v_min`, pre-stated, e.g. `v_min=2`) on the recurrence matrix (vertical-line RQA). `RR` = recurrence rate = `sum(R) / M_pts^2` on the full recurrence matrix (pre-stated). `RATIO_TT_RR = TT / RR`. Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,v_min=2`. **Fail-closed NaN/no-signal** if `RR==0` or undefined/non-finite/degenerate, `TT` undefined/non-finite/degenerate, denominator/ratio non-finite, or insufficient qualifying points. Trailing/causal only. Pre-stated distinctness: TT/RR pairing not used C125–C189; grep 0 observed at preselect.

### Collision guard (required at run time)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rnE 'TT_OVER_RR|tt_over_rr|rqa_ratio_tt_over_rr|rqa_tt_over_rr_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self for primary
```
If collides: pick a grep-zero fallback not used in C125–C190 (e.g., `LMAX_OVER_LAVG`, `DET_OVER_RR`, `TT_OVER_LAVG` — **verify 0 non-self at run time**), record chosen feature + grep cmd/hits/evidence in artifacts/state.

### Required C190 deliverables (all on disk, SHA256 from bytes)
1. **OOS script + run** (model on C188–C189): `scripts/run_real_quote_volume_rqa_tt_over_rr_ratio_shock_mr_costed_oos.py` (or collision-safe alternative). Change only feature computation, IDs, `pre_stated_distinctness`, and refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T005732Z.json` (f6af7d1836b30576f4193ea0ddd2d79db41a19ff224b904e30ccf1e7e2420ee8), cite C189 OOS SHA dce56d7da8c20d31bf8e3e9436785a3e938c1280288a09db990a7405fa9104c9. Emit `reports/real_quote_volume_rqa_tt_over_rr_ratio_shock_mr_costed_oos_<UTC>.json` with `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`, `edge_claim:"NONE"` unless rule holds, `real_data_only:true`, `fail_closed:true`, `pre_stated_distinctness`.
2. **Ingest:** `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 190) — nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`; include cache/provenance SHAs.
3. **Registry (superseding):** `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T005732Z.json` (f6af7d1836b30576f4193ea0ddd2d79db41a19ff224b904e30ccf1e7e2420ee8). Include prior + C190 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary:** `reports/campaign190_execution_summary_<UTC>.json` listing **all new C190 artifact paths + sha256 from bytes**.
5. **Sync state:** `research_state/state.yaml` → `latest_campaign_done:C190`, `next_campaign:C191`, latest registry/OOS sha+path, `oos_edge_proven`, `c191_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C190, with grep cmd/hits/evidence).

## Fail-closed edge rule (EXACT)
`oos_edge_proven=true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## Mandatory rules (HARD)
- Real data only; fail-closed. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if rule holds. Pre-state distinctness; grep-verify before implementation/run; record evidence.
- **No status summary before >= 3 new concrete C190 artifacts exist.** Heavy work mandatory.

## Immediate first actions (run, then build)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.meta.json data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rnE 'TT_OVER_RR|tt_over_rr|rqa_ratio_tt_over_rr|rqa_tt_over_rr_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 for primary
# implement+run C190 -> emit OOS+ingest+registry+summary (>=3) with SHAs -> sync state.yaml
```

## NEXT FOCUS CAMPAIGN — C191 (MANDATORY after C190)
Preselect a **distinct grep-verified** RQA-ratio candidate not used in C125–C190 (grep 0 non-self), record grep cmd/hits/evidence in `state.yaml.c191_preselected`, then **execute C191** under the same template. **No status-only replies. No stop after status.**
