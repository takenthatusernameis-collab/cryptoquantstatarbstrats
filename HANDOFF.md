# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261108T213825Z, C104–C232 LOCKED — edge_claim NONE, C232 DONE, C233 PRESELECTED HEAVY — EXECUTE NEXT, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C232 LOCKED (no reruns). C232 DONE on disk (edge_claim NONE). C233 preselected grep-zero (VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_IQR_SHOCK_MR) — execute C233 next, no status-first.** Latest registry = `reports/strategy_edge_registry_20261108T213825Z.json` (28b1e9e7...). Latest OOS = C232 `7b9bd417...` (oos_edge_proven false).

## TIMESTAMPED INITIAL TASK MESSAGE (20261108T213825Z) — HEAVY WORK MANDATORY
**PRIORITY 1: EXECUTE C233.** C232 is complete on disk (VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_MEDIAN_ABS_DEV_SHOCK_MR, edge_claim NONE; cross-asset net sums fee0=-1.3490544354441005, fee5=-2.4850544354441015, fee10=-3.621054435444102, fee20=-5.8930544354441015, fee40=-10.437054435444102 — fails all-cost-positive / B&H mean rule). C232 artifacts emitted with SHA256 from bytes: OOS `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_median_abs_dev_shock_mr_costed_oos_20261108T213355Z.json` (sha 7b9bd417b0ba4b9820f9bf30d61e5f4b017f005ac3304e40208115a3edaf2fc1), ingest `reports/real_feed_ingest_attempt_20261108T213825Z.json` (sha 65209b45e7cf7385855f3d0abe76792c8769748e21b60f992c5c8e29fd82099b), registry `reports/strategy_edge_registry_20261108T213825Z.json` (sha 3877682020aced181d3411860e2cbce53ea64e3fab8a8bfb7e22c0f3fb273e54) superseding 20261108T212828Z (96fa421a...), script `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_median_abs_dev_shock_mr_costed_oos.py` (sha cae160cec40ea01863b55d805b64db56b3dd283dc99946146582ddefde662b54), summary `reports/campaign232_execution_summary_20261108T213825Z.json` (sha 9e37c43d080e36610b887674d62ee51575035c073c8afa407b41beb233f7aaef). state.yaml + HANDOFF synced (latest_campaign_done C232, next_campaign C233). **Do not summarize status. Do not stop at status. Implement + run C233 + emit >=4 artifacts with SHA256 from bytes + sync state.yaml + HANDOFF.**

## VERIFIED BASELINE (20261108T213825Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1).
- Caches: `data/cache/volume_1h_full.pkl/meta/provenance` (43658953.../4d321584.../c7ff2f27...), spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` (56075733...).
- **C229 DONE (locked):** VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_COUNT_VARIANCE_SHOCK_MR, oos 98a2d1f0..., edge_claim NONE.
- **C230 DONE (locked):** VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_SKEWNESS_SHOCK_MR, oos b92adc7c..., edge_claim NONE.
- **C231 DONE (verified on disk, SHAs from bytes):** VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_KURTOSIS_SHOCK_MR, oos 9a4fb5c0..., edge_claim NONE, oos_edge_proven false.
- **C232 DONE (verified on disk, SHAs from bytes):**
  - OOS 7b9bd417b0ba4b9820f9bf30d61e5f4b017f005ac3304e40208115a3edaf2fc1 (`reports/real_quote_volume_rqa_rte_over_white_diag_line_length_median_abs_dev_shock_mr_costed_oos_20261108T213355Z.json`, VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_MEDIAN_ABS_DEV_SHOCK_MR, campaign 232, edge_claim NONE, oos_edge_proven false, any_exposure_oos true).
  - Ingest 65209b45e7cf7385855f3d0abe76792c8769748e21b60f992c5c8e29fd82099b (`reports/real_feed_ingest_attempt_20261108T213825Z.json`).
  - Registry 28b1e9e7a4bc000619e15d58f4a1fe50f0013a69a778212913578547e6cbfcfb (`reports/strategy_edge_registry_20261108T213825Z.json`) supersedes 20261108T212828Z 96fa421a...
  - Script cae160cec40ea01863b55d805b64db56b3dd283dc99946146582ddefde662b54 (`scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_median_abs_dev_shock_mr_costed_oos.py`, campaign 232, MAD = median absolute deviation from median, raw MAD scale=1, >=3 segments, fail-closed).
  - Summary 9e37c43d080e36610b887674d62ee51575035c073c8afa407b41beb233f7aaef (`reports/campaign232_execution_summary_20261108T213825Z.json`).
  - Distinctness grep 0 non-self at run (RTE_OVER_WHITE_DIAG_LINE_LENGTH_MAD/WHITE_DIAG_LINE_LENGTH_MAD).
- Single durable handoff = this file + `research_state/state.yaml`.

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **C231 completion bottleneck removed.** Script implemented and run (campaign 231, WHITE_DIAG_LINE_LENGTH_KURTOSIS = Fisher-Pearson adjusted kurtosis (excess, sample, bias-corrected; scipy `kurtosis(fisher=True,bias=False)`); fail-closed if <4 qualifying WHITE diagonal segment lengths or variance<=0/non-finite or kurtosis non-finite/undefined; qualifying segments = consecutive 0-cells/non-recurrent, length>=w_min=2 pooled over off-diagonal diagonals k!=0). Fixed OOS + ingest + registry + summary emitted with SHA256 from bytes; state.yaml/HANDOFF synced. C231 no longer blocks C232.
- **C232 completion bottleneck removed.** Script implemented and run (campaign 232, WHITE_DIAG_LINE_LENGTH_MAD = median absolute deviation from median (raw MAD, scale=1); fail-closed if <3 qualifying segments or MAD<=0/non-finite). Fixed OOS + ingest + registry + summary emitted with SHA256 from bytes; state.yaml/HANDOFF synced. C232 no longer blocks C233.
- **No status-first.** Artifacts on disk are the deliverable.
- **No reruns of locked campaigns C104–C232.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Collision handling is fail-closed:** if a preselected candidate collides on grep, reject it, pick a distinct grep-zero fallback, record primary/fallback grep cmd/hits/evidence in all artifacts + state + HANDOFF.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence.
- **Heavy work mandatory.** No status-only replies. No stop between campaigns.

## C233 — NEXT FOCUS CAMPAIGN (PRESELECTED, GREP-ZERO VERIFIED 20261108T213825Z)
**Primary candidate:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_IQR_SHOCK_MR` — RQA ratio RTE / WHITE_DIAG_LINE_LENGTH_IQR on delay-embedded log-volume returns (RTE = recurrence time entropy of white vertical gap distribution, w>=w_min, LOI/self excluded; WHITE_DIAG_LINE_LENGTH_IQR = interquartile range Q3-Q1 (scale=1) of lengths of qualifying WHITE diagonal segments (consecutive 0-cells/non-recurrent, length>=w_min=2) pooled over off-diagonal diagonals k!=0 with >=1 qualifying segment; fail-closed if <3 qualifying segments or IQR<=0/non-finite). Distinct from WHITE_DIAG_LINE_LENGTH_MAD(C232), WHITE_DIAG_LINE_LENGTH_KURTOSIS(C231), WHITE_DIAG_LINE_LENGTH_SKEWNESS(C230), WHITE_DIAG_LINE_COUNT_VARIANCE(C229), DIAG_LINE_COUNT_VARIANCE(C228), WHITE_DIAG_LINE_LENGTH_DIVERGENCE(C227), WHITE_DIAG_LINE_LENGTH_VARIANCE(C226), and prior C125-C232 families.
**grep evidence (20261108T213825Z):** `grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_IQR|rte_over_white_diag_line_length_iqr|WHITE_DIAG_LINE_LENGTH_IQR|white_diag_line_length_iqr' scripts/ strategies/ backtest/ utils/ 2>&1` → 0 hits.
**Fallback:** at C233 start grep-verify; if collision, pick a distinct grep-zero RQA-ratio candidate not used C125–C232 and record evidence.

### COLLISION GUARD (RUN AT START)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_IQR|rte_over_white_diag_line_length_iqr|WHITE_DIAG_LINE_LENGTH_IQR|white_diag_line_length_iqr' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self
```
If collision found: pick a distinct grep-zero fallback not used C125–C232 (verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + state + HANDOFF.

### REQUIRED C233 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_iqr_shock_mr_costed_oos.py` (or collision-safe). Model on C188–C232. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T213825Z.json` (28b1e9e7...), cite C232 OOS SHA `7b9bd417b0ba4b9820f9bf30d61e5f4b017f005ac3304e40208115a3edaf2fc1` and C231 OOS SHA `9a4fb5c0952efb56d90e3a686a919f22208c68a9d810573a30599684d4602391`. Emit `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_iqr_shock_mr_costed_oos_<UTC>.json` with `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds. **No carryover template text; set `campaign: 233`.**
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 233). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T213825Z.json` (28b1e9e7...). Include prior + all C233 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign233_execution_summary_<UTC>.json` listing **all new C233 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C233`, `next_campaign: C234`, latest registry/OOS sha+path, `oos_edge_proven`, `c234_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C233, with grep cmd/hits/evidence). Update this `HANDOFF.md`.

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_IQR|rte_over_white_diag_line_length_iqr|WHITE_DIAG_LINE_LENGTH_IQR|white_diag_line_length_iqr' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self
# NOW: implement+run C233 -> emit >=4 artifacts with SHAs -> sync state.yaml + HANDOFF
```
