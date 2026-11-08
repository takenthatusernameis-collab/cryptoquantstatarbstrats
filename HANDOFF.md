# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261108T212828Z, C104–C231 LOCKED — edge_claim NONE, C231 DONE, C232 PRESELECTED HEAVY — EXECUTE NEXT, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C231 LOCKED (no reruns). C231 DONE on disk (edge_claim NONE). C232 preselected grep-zero (VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_MEDIAN_ABS_DEV_SHOCK_MR) — execute C232 next, no status-first.** Latest registry = `reports/strategy_edge_registry_20261108T212828Z.json` (96fa421a...). Latest OOS = C231 `9a4fb5c0...` (oos_edge_proven false).

## TIMESTAMPED INITIAL TASK MESSAGE (20261108T212828Z) — HEAVY WORK MANDATORY
**PRIORITY 1: EXECUTE C232.** C231 is complete on disk (VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_KURTOSIS_SHOCK_MR, edge_claim NONE; cross-asset net sums fee0=-0.9927292321067769, fee5=-1.6447292321067775, fee10=-2.296729232106778, fee20=-3.600729232106778, fee40=-6.208729232106778 — fails all-cost-positive / B&H mean rule). C231 artifacts emitted with SHA256 from bytes: OOS `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_kurtosis_shock_mr_costed_oos_20261108T212312Z.json` (sha 9a4fb5c0952efb56d90e3a686a919f22208c68a9d810573a30599684d4602391), ingest `reports/real_feed_ingest_attempt_20261108T212828Z.json` (sha ae6851be9d4ccf23b0b3b8179f704e1ac939c2929fb3c89618ba9856a33d9d2a), registry `reports/strategy_edge_registry_20261108T212828Z.json` (sha 96fa421aea6f1a3a2bfd4d15d444638046e07b1e30988116bbf774a779fb3e40) superseding 20261108T211144Z (6b01e3d2...), script `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_kurtosis_shock_mr_costed_oos.py` (sha 9be645dc51bfeae9a1e08cf41b8a45879998722288f304f04ef3f3b29fcad877), summary `reports/campaign231_execution_summary_20261108T212828Z.json` (sha 936aa12e0376f1266c573f9c6327b2d0df0b57dd9d2f49189cdbd98e4359f55c). state.yaml + HANDOFF synced (latest_campaign_done C231, next_campaign C232). **Do not summarize status. Do not stop at status. Implement + run C232 + emit >=4 artifacts with SHA256 from bytes + sync state.yaml + HANDOFF.**

## VERIFIED BASELINE (20261108T212828Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1).
- Caches: `data/cache/volume_1h_full.pkl/meta/provenance` (43658953.../4d321584.../c7ff2f27...), spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` (56075733...).
- **C229 DONE (locked):** VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_COUNT_VARIANCE_SHOCK_MR, oos 98a2d1f0..., edge_claim NONE.
- **C230 DONE (locked):** VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_SKEWNESS_SHOCK_MR, oos b92adc7c..., edge_claim NONE.
- **C231 DONE (verified on disk, SHAs from bytes):**
  - OOS 9a4fb5c0952efb56d90e3a686a919f22208c68a9d810573a30599684d4602391 (`reports/real_quote_volume_rqa_rte_over_white_diag_line_length_kurtosis_shock_mr_costed_oos_20261108T212312Z.json`, VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_KURTOSIS_SHOCK_MR, campaign 231, edge_claim NONE, oos_edge_proven false, any_exposure_oos true).
  - Ingest ae6851be9d4ccf23b0b3b8179f704e1ac939c2929fb3c89618ba9856a33d9d2a (`reports/real_feed_ingest_attempt_20261108T212828Z.json`).
  - Registry 96fa421aea6f1a3a2bfd4d15d444638046e07b1e30988116bbf774a779fb3e40 (`reports/strategy_edge_registry_20261108T212828Z.json`) supersedes 20261108T211144Z 6b01e3d2...
  - Script 9be645dc51bfeae9a1e08cf41b8a45879998722288f304f04ef3f3b29fcad877 (`scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_kurtosis_shock_mr_costed_oos.py`, campaign 231, Fisher-Pearson adjusted kurtosis excess fisher=True,bias=False, >=4 segments, fail-closed).
  - Summary 936aa12e0376f1266c573f9c6327b2d0df0b57dd9d2f49189cdbd98e4359f55c (`reports/campaign231_execution_summary_20261108T212828Z.json`).
  - Distinctness grep 0 non-self at run (RTE_OVER_WHITE_DIAG_LINE_LENGTH_KURTOSIS/WHITE_DIAG_LINE_LENGTH_KURTOSIS).
- Single durable handoff = this file + `research_state/state.yaml`.

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **C231 completion bottleneck removed.** Script implemented and run (campaign 231, WHITE_DIAG_LINE_LENGTH_KURTOSIS = Fisher-Pearson adjusted kurtosis (excess, sample, bias-corrected; scipy `kurtosis(fisher=True,bias=False)`); fail-closed if <4 qualifying WHITE diagonal segment lengths or variance<=0/non-finite or kurtosis non-finite/undefined; qualifying segments = consecutive 0-cells/non-recurrent, length>=w_min=2 pooled over off-diagonal diagonals k!=0). Fixed OOS + ingest + registry + summary emitted with SHA256 from bytes; state.yaml/HANDOFF synced. C231 no longer blocks C232.
- **No status-first.** Artifacts on disk are the deliverable.
- **No reruns of locked campaigns C104–C231.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Collision handling is fail-closed:** if a preselected candidate collides on grep, reject it, pick a distinct grep-zero fallback, record primary/fallback grep cmd/hits/evidence in all artifacts + state + HANDOFF.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence.
- **Heavy work mandatory.** No status-only replies. No stop between campaigns.

## C232 — NEXT FOCUS CAMPAIGN (PRESELECTED, GREP-ZERO VERIFIED 20261108T212828Z)
**Primary candidate:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_MEDIAN_ABS_DEV_SHOCK_MR` — RQA ratio RTE / WHITE_DIAG_LINE_LENGTH_MAD on delay-embedded log-volume returns (RTE = recurrence time entropy of white vertical gap distribution, w>=w_min, LOI/self excluded; WHITE_DIAG_LINE_LENGTH_MAD = median absolute deviation from median (raw MAD, scale=1) of lengths of qualifying WHITE diagonal segments (consecutive 0-cells/non-recurrent, length>=w_min=2) pooled over off-diagonal diagonals k!=0 with >=1 qualifying segment; fail-closed if <3 qualifying segments or MAD<=0/non-finite). Distinct from WHITE_DIAG_LINE_LENGTH_KURTOSIS(C231), WHITE_DIAG_LINE_LENGTH_SKEWNESS(C230), WHITE_DIAG_LINE_COUNT_VARIANCE(C229), DIAG_LINE_COUNT_VARIANCE(C228), WHITE_DIAG_LINE_LENGTH_DIVERGENCE(C227), WHITE_DIAG_LINE_LENGTH_VARIANCE(C226), and prior C125-C231 families.
**grep evidence (20261108T212828Z):** `grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_MAD|rte_over_white_diag_line_length_mad|RTE_OVER_WHITE_DIAG_LINE_LENGTH_MEDIAN_ABS_DEV|WHITE_DIAG_LINE_LENGTH_MAD|WHITE_DIAG_LINE_LENGTH_MEDIAN_ABS_DEV|white_diag_line_length_mad|white_diag_line_length_median_abs_dev' scripts/ strategies/ backtest/ utils/ 2>&1` → 0 hits.
**Fallback:** at C232 start grep-verify; if collision, pick a distinct grep-zero RQA-ratio candidate not used C125–C231 and record evidence.

### COLLISION GUARD (RUN AT START)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_MAD|rte_over_white_diag_line_length_mad|RTE_OVER_WHITE_DIAG_LINE_LENGTH_MEDIAN_ABS_DEV|WHITE_DIAG_LINE_LENGTH_MAD|WHITE_DIAG_LINE_LENGTH_MEDIAN_ABS_DEV|white_diag_line_length_mad|white_diag_line_length_median_abs_dev' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self
```
If collision found: pick a distinct grep-zero fallback not used C125–C231 (verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + state + HANDOFF.

### REQUIRED C232 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_median_abs_dev_shock_mr_costed_oos.py` (or collision-safe). Model on C188–C231. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T212828Z.json` (96fa421a...), cite C231 OOS SHA `9a4fb5c0952efb56d90e3a686a919f22208c68a9d810573a30599684d4602391` and C230 OOS SHA `b92adc7c512c7bded370ba7ceb04b4dbdd2ff29becf0ce0a40a7d11b696222f7`. Emit `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_median_abs_dev_shock_mr_costed_oos_<UTC>.json` with `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds. **No carryover template text; set `campaign: 232`.**
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 232). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T212828Z.json` (96fa421a...). Include prior + all C232 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign232_execution_summary_<UTC>.json` listing **all new C232 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C232`, `next_campaign: C233`, latest registry/OOS sha+path, `oos_edge_proven`, `c233_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C232, with grep cmd/hits/evidence). Update this `HANDOFF.md`.

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_MAD|rte_over_white_diag_line_length_mad|RTE_OVER_WHITE_DIAG_LINE_LENGTH_MEDIAN_ABS_DEV|WHITE_DIAG_LINE_LENGTH_MAD|WHITE_DIAG_LINE_LENGTH_MEDIAN_ABS_DEV|white_diag_line_length_mad|white_diag_line_length_median_abs_dev' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self
# NOW: implement+run C232 -> emit >=4 artifacts with SHAs -> sync state.yaml + HANDOFF
```
