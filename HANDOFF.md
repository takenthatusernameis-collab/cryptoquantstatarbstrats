# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261108T182525Z, C104–C223 LOCKED — edge_claim NONE, C224 PRESELECTED HEAVY — EXECUTE NEXT, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C223 LOCKED (no reruns). C224 preselected and grep-zero — execute C224 next, no status-first.**

## TIMESTAMPED INITIAL TASK MESSAGE (20261108T182525Z) — HEAVY WORK MANDATORY
**PRIORITY 1: EXECUTE C224.** C223 is complete on disk (VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_DENSITY_DIVERGENCE_SHOCK_MR, `edge_claim:NONE`; cross-asset net sums fee0=1.2046801384777068, fee5=0.6086801384777063, fee10=0.012680138477706188, fee20=-1.1793198615222935, fee40=-3.5633198615222934 — fails all-cost-positive / B&H mean rule at fee20+). **Do not summarize status. Do not stop at status. Implement + run C224 + emit >=4 artifacts with SHA256 from bytes + sync state.yaml + HANDOFF.**

## VERIFIED BASELINE (20261108T182525Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1).
- Caches: `data/cache/volume_1h_full.pkl/meta/provenance` (43658953.../4d321584.../c7ff2f27...), spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` (56075733...).
- **C222 DONE (locked):** OOS 62fc4bca... (VOLUME_RQA_RTE_OVER_DIAG_LINE_DENSITY_VARIANCE_SHOCK_MR, edge_claim NONE).
- **C223 DONE (verified on disk, SHAs from bytes):**
  - OOS 68cbd388d8c73e4cce0ae186ded054693f1668fd44bb446287758bf197ad61c5 (`reports/real_quote_volume_rqa_rte_over_white_diag_line_density_divergence_shock_mr_costed_oos_20261108T181704Z.json`, VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_DENSITY_DIVERGENCE_SHOCK_MR, edge_claim NONE, oos_edge_proven false, any_exposure_oos true).
  - Ingest 2936c8d32b3a75428985a8b3962e0dea8f1d3df700822b51e17fb8c10ba5b350 (`reports/real_feed_ingest_attempt_20261108T181704Z.json`).
  - Registry e8b90fc1a95ed33c853c18b620bf43c2529a34a43e702ea1359c09b53623594d (`reports/strategy_edge_registry_20261108T181704Z.json`) supersedes `reports/strategy_edge_registry_20261108T172610Z.json` (e933070e...).
  - Script 6a7260237a58f735bd13f80c3a8e73405e0d85a1975e8a867d43bcea1be55d87 (`scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_density_divergence_shock_mr_costed_oos.py`).
  - Summary e038ad1b2a9a8e3be1c8b04b2e362c0dfbfcfff4f280225723f4db242ddcbf8d (`reports/campaign223_execution_summary_20261108T181704Z.json`).
  - Distinctness grep 0 non-self at run (`RTE_OVER_WHITE_DIAG_LINE_DENSITY_DIVERGENCE`/`WHITE_DIAG_LINE_DENSITY_DIVERGENCE`); post-run grep shows only the C223 script (self).
- Single durable handoff = this file + `research_state/state.yaml`. Latest registry = `reports/strategy_edge_registry_20261108T181704Z.json` (e8b90fc1...). Latest OOS = C223 `68cbd388...` (oos_edge_proven false).

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **No status-first.** Artifacts on disk are the deliverable.
- **No reruns of locked campaigns C104–C223.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Collision handling is fail-closed:** if a preselected candidate collides on grep, reject it, pick a distinct grep-zero fallback, record primary/fallback grep cmd/hits/evidence in all artifacts + state + HANDOFF.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence.
- **Heavy work mandatory.** No status-only replies. No stop between campaigns.

## C224 — NEXT FOCUS CAMPAIGN (PRESELECTED, GREP-ZERO VERIFIED 20261108T182525Z)
**Primary candidate:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_DENSITY_VARIANCE_SHOCK_MR` — RQA ratio RTE / WHITE_DIAG_LINE_DENSITY_VARIANCE on delay-embedded log-volume returns (RTE = recurrence time entropy of white vertical gap distribution, w>=w_min, LOI/self excluded; WHITE_DIAG_LINE_DENSITY_VARIANCE = sample variance ddof=1 of rho_k_white over off-diagonal diagonals k!=0 with >=1 qualifying white diagonal segment of consecutive 0s meeting `w_min=2`, where rho_k_white = (sum of qualifying white segment lengths on diagonal k)/(M_pts-|k|); fail-closed if <2 qualifying diagonals or variance <=0/non-finite/undefined). Distinct from WHITE_DIAG_LINE_DENSITY_DIVERGENCE(C223), DIAG_LINE_DENSITY_VARIANCE(C222), DIAG_LINE_DENSITY_DIVERGENCE(C221), and prior C125-C223 families. Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,w_min=2` (white diagonal segment definition explicit and trailing/causal).
**Fallbacks (grep-zero 20261108T182525Z):** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_COUNT_DIVERGENCE_SHOCK_MR` (0), `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_VARIANCE_SHOCK_MR` (0).

### COLLISION GUARD (RUN AT START)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_DENSITY_VARIANCE|rte_over_white_diag_line_density_variance|WHITE_DIAG_LINE_DENSITY_VARIANCE|white_diag_line_density_variance' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self
```
If collision found: pick a distinct grep-zero fallback not used C125–C223 (verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + state + HANDOFF.

### REQUIRED C224 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_density_variance_shock_mr_costed_oos.py` (or collision-safe). Model on C188–C223. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T181704Z.json` (e8b90fc1...), cite C223 OOS SHA `68cbd388d8c73e4cce0ae186ded054693f1668fd44bb446287758bf197ad61c5`. Emit `reports/real_quote_volume_rqa_rte_over_white_diag_line_density_variance_shock_mr_costed_oos_<UTC>.json` with `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds. **No carryover template text**.
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 224). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T181704Z.json` (e8b90fc1...). Include prior + all C224 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign224_execution_summary_<UTC>.json` listing **all new C224 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C224`, `next_campaign: C225`, latest registry/OOS sha+path, `oos_edge_proven`, `c225_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C224, with grep cmd/hits/evidence). Update this `HANDOFF.md`.

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_DENSITY_VARIANCE|rte_over_white_diag_line_density_variance|WHITE_DIAG_LINE_DENSITY_VARIANCE|white_diag_line_density_variance' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self
# NOW: implement+run C224 -> emit >=4 artifacts with SHAs -> sync state.yaml + HANDOFF
```

## C225 (AUTO-QUEUED, HEAVY)
After C224 complete and synced: preselect a **distinct grep-verified** RQA-ratio candidate not used C125–C224, record in `state.yaml.c225_preselected`, and **execute C225 immediately** under same template. No status-only replies. No stop between campaigns.
