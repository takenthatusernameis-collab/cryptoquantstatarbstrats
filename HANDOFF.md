# READ THIS FIRST — SINGLE DURABLE HANDOFF (UPDATED: 20261108T015622Z, C192 COMPLETE/LOCKED, NEXT=C193 MANDATORY INITIAL TASK)
**Repo:** `cryptoquantstatarbstrats`. Fail-closed, **real-data-only** stat-arb edge validation — WF OOS 720/168/168, costs [[0,0],[5,5],[10,10],[20,20],[40,40]], B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C192 LOCKED.**

## VERIFIED BASELINE (20261108T015622Z — current, unchanged from 20261108T015439Z)
- deps_ok (numpy/scipy/pandas). pytest 9.2.0 available.
- Caches present: `data/cache/volume_1h_full.pkl/meta/provenance`, spot `0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl/meta`.
- **C192 COMPLETE/LOCKED**: OOS `reports/real_quote_volume_rqa_lavg_over_tt_ratio_shock_mr_costed_oos_20261108T015314Z.json`=4ea5074e8a8e89544a61eab06ae7e02d942d8a1bbb2b3a962f0f9bbeb77722f0 (`VOLUME_RQA_LAVG_OVER_TT_RATIO_SHOCK_MR`, `oos_edge_proven:false`, `edge_claim:NONE`). Ingest `reports/real_feed_ingest_attempt_20261108T015434Z.json`=9dd2ccd4f316d3632a6a538b8601a92297b28a9bccc44346b17cf054b7ec2b42. Registry `reports/strategy_edge_registry_20261108T015434Z.json`=78d3fc45a916b81ba3ecc7f8251995c927691ed4335f7e97b454679ad01b0193 supersedes C191 7d2e0861e67726b03924550d7be29a68154010d79d3c6c2fa1177077edc848e0. Script `scripts/run_real_quote_volume_rqa_lavg_over_tt_ratio_shock_mr_costed_oos.py`. Summary `reports/campaign192_execution_summary_20261108T015439Z.json`=e18902daa7ee37d1ae14f973b6f9202eda963b90671533bf2331f53ec977e2e3. All SHAs verified from bytes 20261108T015439Z.
- Cross-asset OOS net sums: fee0_slip0=0.7879, fee5_slip5=0.4979, fee10_slip10=0.2079, fee20_slip20=-0.3721, fee40_slip40=-1.5321 (rule not satisfied; edge_claim NONE).

## BOTTLENECKS REMOVED / NO EXCUSES (20261108T015439Z)
- C104–C192 locked with SHAs from bytes; no reruns, no stale cache re-scans, no gate/threshold weakening, no proxies labeled real.
- Deps/caches ready. Nonspot blocker does not block R-B on `real_quote_volume`.
- Single durable handoff = `HANDOFF.md` + `research_state/state.yaml`. **No status-only replies. No stop after status.**
- C192 LAVG_OVER_TT collision guard 0 non-self at run time (20261108T014412Z). C193 DIV_OVER_RR grep 0 observed (20261108T015439Z); RTE_OVER_RR fallback grep 0 — re-verify at C193 run time.

## INITIAL TASK — C193 (MANDATORY, HEAVY WORK, START IMMEDIATELY)
**Execute C193 now.** Produce **>= 3 NEW concrete C193 report artifacts on disk** (OOS + ingest + registry/superseding + summary) **each with SHA256 computed from bytes**, plus OOS script and synced `research_state/state.yaml`.

### Primary candidate (preselected; run-time grep required)
`VOLUME_RQA_DIV_OVER_RR_RATIO_SHOCK_MR` — RQA ratio **DIV/RR** on delay-embedded log-volume returns. `DIV` = divergence = 1/L_MAX (L_MAX = max qualifying diagonal line length k>=l_min, excluding LOI). `RR` = recurrence rate = fraction of off-diagonal recurrence points. `RATIO_DIV_RR = DIV/RR`. Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`. **Fail-closed NaN/no-signal** if `L_MAX<=0` or undefined/non-finite/degenerate, `RR==0` or undefined/non-finite/degenerate, ratio non-finite, or insufficient qualifying lines/points. Trailing/causal only. Pre-stated distinctness: DIV/RR pairing not used C125–C192; grep 0 observed at preselect.

### Collision guard (required at run time)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rnE 'DIV_OVER_RR|div_over_rr|rqa_ratio_div_over_rr|rqa_div_over_rr_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self for primary
```
If collides: pick a grep-zero fallback not used in C125–C193 (e.g., `RTE_OVER_RR` — **verify 0 non-self at run time**; `RTE_OVER_RR` grep 0 observed 20261108T015439Z), record chosen feature + grep cmd/hits/evidence in artifacts/state.

### Required C193 deliverables (all on disk, SHA256 from bytes)
1. **OOS script + run** (model on C188–C192): `scripts/run_real_quote_volume_rqa_div_over_rr_ratio_shock_mr_costed_oos.py` (or collision-safe alternative). Change only feature computation, IDs, `pre_stated_distinctness`, and refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T015434Z.json` (78d3fc45a916b81ba3ecc7f8251995c927691ed4335f7e97b454679ad01b0193), cite C192 OOS SHA 4ea5074e8a8e89544a61eab06ae7e02d942d8a1bbb2b3a962f0f9bbeb77722f0. Emit `reports/real_quote_volume_rqa_div_over_rr_ratio_shock_mr_costed_oos_<UTC>.json` with `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`, `edge_claim:"NONE"` unless rule holds, `real_data_only:true`, `fail_closed:true`, `pre_stated_distinctness`.
2. **Ingest:** `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 193) — nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`; include cache/provenance SHAs.
3. **Registry (superseding):** `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T015434Z.json` (78d3fc45a916b81ba3ecc7f8251995c927691ed4335f7e97b454679ad01b0193). Include prior + C193 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary:** `reports/campaign193_execution_summary_<UTC>.json` listing **all new C193 artifact paths + sha256 from bytes**.
5. **Sync state:** `research_state/state.yaml` → `latest_campaign_done:C193`, `next_campaign:C194`, latest registry/OOS sha+path, `oos_edge_proven`, `c194_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C193, with grep cmd/hits/evidence).

## Fail-closed edge rule (EXACT)
`oos_edge_proven=true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## Mandatory rules (HARD)
- Real data only; fail-closed. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if rule holds. Pre-state distinctness; grep-verify before implementation/run; record evidence.
- **No status summary before >= 3 new concrete C193 artifacts exist.** Heavy work mandatory.

## Immediate first actions (run, then build)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.meta.json data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rnE 'DIV_OVER_RR|div_over_rr|rqa_ratio_div_over_rr|rqa_div_over_rr_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 for primary
# implement+run C193 -> emit OOS+ingest+registry+summary (>=3) with SHAs -> sync state.yaml
```

## NEXT FOCUS CAMPAIGN — C194 (MANDATORY after C193)
Preselect a **distinct grep-verified** RQA-ratio candidate not used in C125–C193 (grep 0 non-self), record grep cmd/hits/evidence in `state.yaml.c194_preselected`, then **execute C194** under the same template. **No status-only replies. No stop after status.**
