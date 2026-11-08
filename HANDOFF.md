# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261108T143601Z, C104–C218 LOCKED — edge_claim NONE, C219 PRESELECTED HEAVY — EXECUTE NEXT, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C218 LOCKED (no reruns). C219 preselected and grep-zero — execute C219 next, no status-first.**

## TIMESTAMPED INITIAL TASK MESSAGE (20261108T143601Z) — HEAVY WORK MANDATORY
**PRIORITY 1: EXECUTE C219.** C218 is complete on disk (VOLUME_RQA_RTE_OVER_DIAG_LINE_COUNT_DIVERGENCE_SHOCK_MR, `edge_claim:NONE`; cross-asset net sums fee0=0.21785912263211749, fee5=-0.2741408773678829, fee10=-0.7661408773678829, fee20=-1.7501408773678826, fee40=-3.718140877367883 — fails all-cost-positive / B&H mean rule). **Do not summarize status. Do not stop at status. Implement + run C219 + emit >=4 artifacts with SHA256 from bytes + sync state.yaml + HANDOFF.**

## VERIFIED BASELINE (20261108T143601Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1).
- Caches: `data/cache/volume_1h_full.pkl/meta/provenance`, spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl`.
- **C217 DONE (locked):** OOS bea428a8... (VOLUME_RQA_RTE_OVER_VERT_LINE_LENGTH_VARIANCE_SHOCK_MR, edge_claim NONE). Registry 66ae83a7... superseded.
- **C218 DONE (verified on disk, SHAs from bytes):**
  - OOS 3aecb9d9f04c7915c010f774d296c70ef2152020807e2069b774a3470f7b820c (`reports/real_quote_volume_rqa_rte_over_diag_line_count_divergence_shock_mr_costed_oos_20261108T143601Z.json`, VOLUME_RQA_RTE_OVER_DIAG_LINE_COUNT_DIVERGENCE_SHOCK_MR, edge_claim NONE, oos_edge_proven false).
  - Ingest 6c5b77a6105e8e7620991fe54bcaa1066afe82cc62e8fdc3b0d73074e2751af2 (`reports/real_feed_ingest_attempt_20261108T143601Z.json`).
  - Registry 1dbf7764063fd7cb559614d6b5440a38ea43802856d5a150b6da1a01deb1eb49 (`reports/strategy_edge_registry_20261108T143601Z.json`) supersedes `reports/strategy_edge_registry_20261108T143035Z.json` (66ae83a7...).
  - Script ab8b74326c71c5ea06b41ff907e5520204067524d88dcd991de1415152040bdf (`scripts/run_real_quote_volume_rqa_rte_over_diag_line_count_divergence_shock_mr_costed_oos.py`).
  - Summary 2c090dcfdafb41ac574fc1cd4a556887c0f3d41c20e09378ceb27cc492b6c123 (`reports/campaign218_execution_summary_20261108T143601Z.json`).
  - Distinctness grep 0 non-self at run (`RTE_OVER_DIAG_LINE_COUNT_DIVERGENCE`).
- Single durable handoff = this file + `research_state/state.yaml`. Latest registry = `reports/strategy_edge_registry_20261108T143601Z.json` (1dbf7764...). Latest OOS = C218 `3aecb9d9...` (oos_edge_proven false).

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **No status-first.** Artifacts on disk are the deliverable.
- **No reruns of locked campaigns C104–C218.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Collision handling is fail-closed:** if a preselected candidate collides on grep, reject it, pick a distinct grep-zero fallback, record primary/fallback grep cmd/hits/evidence in all artifacts + state + HANDOFF.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence.
- **Heavy work mandatory.** No status-only replies. No stop between campaigns.

## C219 — NEXT FOCUS CAMPAIGN (PRESELECTED, GREP-ZERO VERIFIED 20261108T143601Z)
**Primary candidate:** `VOLUME_RQA_RTE_OVER_DIAG_LINE_LENGTH_VARIANCE_SHOCK_MR` — RQA ratio RTE / DIAG_LINE_LENGTH_VARIANCE on delay-embedded log-volume returns (RTE = recurrence time entropy of white vertical gap distribution, w>=w_min, LOI/self excluded; DIAG_LINE_LENGTH_VARIANCE = sample variance ddof=1 of qualifying diagonal run lengths l>=l_min pooled across all off-diagonal diagonals k!=0 that have >=1 qualifying run; fail-closed if <2 qualifying lengths total or variance <=0/non-finite/undefined). Distinct from DIAG_LINE_COUNT_DIVERGENCE(C218), VERT_LINE_LENGTH_VARIANCE(C217), VERT_LINE_COUNT_DIVERGENCE(C216), MAXDIAGLINE_DIVERGENCE(C214), diagonal L(C211), LMAX(C209), VMAX(C207), etc. Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2,w_min=1`. Trailing/causal only.
**Fallbacks (grep-zero 20261108T143601Z):** `VOLUME_RQA_RTE_OVER_WHITE_VERT_LINE_COUNT_DIVERGENCE_SHOCK_MR` (0), `VOLUME_RQA_RTE_OVER_DIAG_LINE_DENSITY_DIVERGENCE_SHOCK_MR` (0), `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_COUNT_DIVERGENCE_SHOCK_MR` (0).

### COLLISION GUARD (RUN AT START)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_DIAG_LINE_LENGTH_VARIANCE|rte_over_diag_line_length_variance' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self for chosen candidate
```
If collision found: pick a distinct grep-zero fallback not used C125–C218 (verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + `state.yaml`.

### REQUIRED C219 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_rte_over_diag_line_length_variance_shock_mr_costed_oos.py` (or collision-safe). Model on C188–C218. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T143601Z.json` (1dbf7764...), cite C218 OOS SHA `3aecb9d9f04c7915c010f774d296c70ef2152020807e2069b774a3470f7b820c`. Emit `reports/real_quote_volume_rqa_rte_over_diag_line_length_variance_shock_mr_costed_oos_<UTC>.json` with `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds. **No carryover template text**.
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 219). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T143601Z.json` (1dbf7764...). Include prior + all C219 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign219_execution_summary_<UTC>.json` listing **all new C219 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C219`, `next_campaign: C220`, latest registry/OOS sha+path, `oos_edge_proven`, `c220_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C219, with grep cmd/hits/evidence). Update this `HANDOFF.md`.

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_DIAG_LINE_LENGTH_VARIANCE|rte_over_diag_line_length_variance' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self
# NOW: implement+run C219 -> emit >=4 artifacts with SHAs -> sync state.yaml + HANDOFF
```

## C220 (AUTO-QUEUED, HEAVY)
After C219 complete and synced: preselect a **distinct grep-verified** RQA-ratio candidate not used C125–C219, record in `state.yaml.c220_preselected`, and **execute C220 immediately** under same template. No status-only replies. No stop between campaigns.
