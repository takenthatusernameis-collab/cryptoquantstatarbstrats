# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261108T211144Z, C104–C230 LOCKED — edge_claim NONE, C230 DONE, C231 PRESELECTED HEAVY — EXECUTE NEXT, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C230 LOCKED (no reruns). C230 DONE on disk (edge_claim NONE). C231 preselected grep-zero (VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_KURTOSIS_SHOCK_MR) — execute C231 next, no status-first.** Latest registry = `reports/strategy_edge_registry_20261108T211144Z.json` (6b01e3d2...). Latest OOS = C230 `b92adc7c...` (oos_edge_proven false).

## TIMESTAMPED INITIAL TASK MESSAGE (20261108T211144Z) — HEAVY WORK MANDATORY
**PRIORITY 1: EXECUTE C231.** C230 is complete on disk (VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_SKEWNESS_SHOCK_MR, edge_claim NONE; cross-asset net sums fee0=-0.17438866897960414, fee5=-0.4853886689796044, fee10=-0.7963886689796046, fee20=-1.4183886689796044, fee40=-2.6623886689796046 — fails all-cost-positive / B&H mean rule). C230 artifacts emitted with SHA256 from bytes: OOS `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_skewness_shock_mr_costed_oos_20261108T211144Z.json` (sha b92adc7c...), ingest `reports/real_feed_ingest_attempt_20261108T211144Z.json` (sha 6179ee09...), registry `reports/strategy_edge_registry_20261108T211144Z.json` (sha 6b01e3d2...), script `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_skewness_shock_mr_costed_oos.py` (sha acca7132...), summary `reports/campaign230_execution_summary_20261108T211144Z.json` (sha 8960224c...). state.yaml + HANDOFF synced (latest_campaign_done C230, next_campaign C231). **Do not summarize status. Do not stop at status. Implement + run C231 + emit >=4 artifacts with SHA256 from bytes + sync state.yaml + HANDOFF.**

## VERIFIED BASELINE (20261108T211144Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1).
- Caches: `data/cache/volume_1h_full.pkl/meta/provenance` (43658953.../4d321584.../c7ff2f27...), spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` (56075733...).
- **C223–C228 DONE (locked):** edge_claim NONE, all oos_edge_proven false.
- **C229 DONE (verified on disk, SHAs from bytes):**
  - OOS 98a2d1f07e25d57bf31260ee6cfd6c10c1af4a69938bb9f446774ddeb79acbd6 (`reports/real_quote_volume_rqa_rte_over_white_diag_line_count_variance_shock_mr_costed_oos_20261108T203235Z.json`, VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_COUNT_VARIANCE_SHOCK_MR, campaign 229, edge_claim NONE, oos_edge_proven false, any_exposure_oos true).
  - Ingest 8b97ae6fb039b6d03a126284a9e0044905b69af26310ffaa37e762f023ba7d0e (`reports/real_feed_ingest_attempt_20261108T203312Z.json`).
  - Registry d0e372129157ef70ecabbe0fba8608d2835a7c26548a6d893ba8bf5c184f51a2 (`reports/strategy_edge_registry_20261108T203312Z.json`) supersedes 20261108T202506Z 509503bf...
  - Script 70f30d070c36dc8fbdb571067edddb116cc7e7015c428ac9c08a6451f4e6a1bb (`scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_count_variance_shock_mr_costed_oos.py`, campaign 229, correct WHITE_DIAG_LINE_COUNT_VARIANCE definition).
  - Summary b84fba4267ee48dae71d9d3e3a90d6a4604e60265b7afef5f830f37c87963201 (`reports/campaign229_execution_summary_20261108T203312Z.json`).
  - Distinctness grep 0 non-self at run (RTE_OVER_WHITE_DIAG_LINE_COUNT_VARIANCE/WHITE_DIAG_LINE_COUNT_VARIANCE).
- **C230 DONE (verified on disk, SHAs from bytes):**
  - OOS b92adc7c512c7bded370ba7ceb04b4dbdd2ff29becf0ce0a40a7d11b696222f7 (`reports/real_quote_volume_rqa_rte_over_white_diag_line_length_skewness_shock_mr_costed_oos_20261108T211144Z.json`, VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_SKEWNESS_SHOCK_MR, campaign 230, edge_claim NONE, oos_edge_proven false, any_exposure_oos true).
  - Ingest 6179ee09162edb2b91e02631890dd4f22847c9c876b75af6142aa1eb51d13e72 (`reports/real_feed_ingest_attempt_20261108T211144Z.json`).
  - Registry 6b01e3d24d5f60e52fb7a2284b686d15d000eeebe5d39c058e2ad0f11df79a14 (`reports/strategy_edge_registry_20261108T211144Z.json`) supersedes 20261108T203312Z d0e37212...
  - Script acca713261c79ab98e152f44bb111422434904fdace2d5d49531919bba5bf824 (`scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_skewness_shock_mr_costed_oos.py`, campaign 230, WHITE_DIAG_LINE_LENGTH_SKEWNESS definition).
  - Summary 8960224c3b7c3d48bdf783322b5a4c1d0cb5dec834c04450ebc09a5259e01f55 (`reports/campaign230_execution_summary_20261108T211144Z.json`).
  - Distinctness grep 0 non-self at run (RTE_OVER_WHITE_DIAG_LINE_LENGTH_SKEWNESS/WHITE_DIAG_LINE_LENGTH_SKEWNESS).
- Single durable handoff = this file + `research_state/state.yaml`.

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **C229 completion bottleneck removed.** Script implemented and run (campaign 229, correct WHITE_DIAG_LINE_COUNT_VARIANCE = sample variance (ddof=1) of `cnt_k_white` over off-diagonal diagonals `k!=0` with >=1 qualifying WHITE/non-recurrent diagonal segment of consecutive 0s meeting `w_min>=2`, where `cnt_k_white = (qualifying white segment count) / (cells on diagonal k = M_pts-|k|)`). Fixed OOS + ingest + registry + summary emitted (20261108T203235Z/203312Z) with SHA256 from bytes; state.yaml/HANDOFF synced. C229 no longer blocks C230.
- **C230 completion bottleneck removed.** Script implemented and run (campaign 230, WHITE_DIAG_LINE_LENGTH_SKEWNESS = Fisher-Pearson adjusted skewness (sample, bias-corrected where finite; fail-closed if <3 qualifying white diagonal segment lengths or variance<=0/non-finite) of lengths of qualifying WHITE diagonal segments (consecutive 0-cells/non-recurrent, length>=w_min=2) pooled over off-diagonal diagonals k!=0 with >=1 qualifying segment). Fixed OOS + ingest + registry + summary emitted (20261108T211144Z) with SHA256 from bytes; state.yaml/HANDOFF synced. C230 no longer blocks C231.
- **No status-first.** Artifacts on disk are the deliverable.
- **No reruns of locked campaigns C104–C230.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Collision handling is fail-closed:** if a preselected candidate collides on grep, reject it, pick a distinct grep-zero fallback, record primary/fallback grep cmd/hits/evidence in all artifacts + state + HANDOFF. `diag_line_length_*` (89 hits) and `diag_line_count_divergence` collide with C226/C227 text — rejected for C228/C229/C230 context.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence.
- **Heavy work mandatory.** No status-only replies. No stop between campaigns.

## C231 — NEXT FOCUS CAMPAIGN (PRESELECTED, GREP-ZERO VERIFIED 20261108T211144Z)
**Primary candidate:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_KURTOSIS_SHOCK_MR` — RQA ratio RTE / WHITE_DIAG_LINE_LENGTH_KURTOSIS on delay-embedded log-volume returns (RTE = recurrence time entropy of white vertical gap distribution, w>=w_min, LOI/self excluded; WHITE_DIAG_LINE_LENGTH_KURTOSIS = Fisher-Pearson adjusted kurtosis (sample, bias-corrected where finite; fail-closed if <4 qualifying white diagonal segment lengths or variance<=0/non-finite) of lengths of qualifying WHITE diagonal segments (consecutive 0-cells/non-recurrent, length>=w_min=2) pooled over off-diagonal diagonals k!=0 with >=1 qualifying segment; fail-closed if kurtosis non-finite/undefined or insufficient segments). Distinct from WHITE_DIAG_LINE_COUNT_VARIANCE(C229), WHITE_DIAG_LINE_LENGTH_SKEWNESS(C230), DIAG_LINE_COUNT_VARIANCE(C228), WHITE_DIAG_LINE_LENGTH_DIVERGENCE(C227), WHITE_DIAG_LINE_LENGTH_VARIANCE(C226), WHITE_DIAG_LINE_COUNT_DIVERGENCE(C225), and prior C125-C230 families.
**grep evidence (20261108T211144Z):** `grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_KURTOSIS|rte_over_white_diag_line_length_kurtosis|WHITE_DIAG_LINE_LENGTH_KURTOSIS|white_diag_line_length_kurtosis' scripts/ strategies/ backtest/ utils/ 2>&1` → 0 hits.
**Fallback:** none preselected; at C231 start, grep-verify a distinct grep-zero RQA-ratio candidate not used C125–C230 and record evidence.

### COLLISION GUARD (RUN AT START)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_KURTOSIS|rte_over_white_diag_line_length_kurtosis|WHITE_DIAG_LINE_LENGTH_KURTOSIS|white_diag_line_length_kurtosis' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self
```
If collision found: pick a distinct grep-zero fallback not used C125–C230 (verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + state + HANDOFF.

### REQUIRED C231 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_kurtosis_shock_mr_costed_oos.py` (or collision-safe). Model on C188–C230. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T211144Z.json` (6b01e3d2...), cite C230 OOS SHA `b92adc7c512c7bded370ba7ceb04b4dbdd2ff29becf0ce0a40a7d11b696222f7` and C229 OOS SHA `98a2d1f07e25d57bf31260ee6cfd6c10c1af4a69938bb9f446774ddeb79acbd6`. Emit `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_kurtosis_shock_mr_costed_oos_<UTC>.json` with `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds. **No carryover template text; set `campaign: 231`.**
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 231). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T211144Z.json` (6b01e3d2...). Include prior + all C231 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign231_execution_summary_<UTC>.json` listing **all new C231 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C231`, `next_campaign: C232`, latest registry/OOS sha+path, `oos_edge_proven`, `c232_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C231, with grep cmd/hits/evidence). Update this `HANDOFF.md`.

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_KURTOSIS|rte_over_white_diag_line_length_kurtosis|WHITE_DIAG_LINE_LENGTH_KURTOSIS|white_diag_line_length_kurtosis' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self
# NOW: implement+run C231 -> emit >=4 artifacts with SHAs -> sync state.yaml + HANDOFF
```

(End of file - total 119 lines)
