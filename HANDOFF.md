# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261109T021829Z, C104–C244 LOCKED — edge_claim NONE, C244 DONE, C245 PRESELECTED HEAVY — EXECUTE NEXT, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C244 LOCKED (no reruns). C244 DONE on disk (edge_claim NONE). C245 preselected grep-zero (VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_MIDHINGE_SHOCK_MR) — execute C245 next, no status-first.** Latest registry = `reports/strategy_edge_registry_20261109T021829Z.json` (abdac7c759d7af3f7be8fa7596d552b643eca37b4cea0a3c1b5ad20a1cdef75b). Latest OOS = C244 `2fc63905932fb6c53db6aa02d411cd7e36ea866dc7bfbfa429e95364fb04f5f2` (oos_edge_proven false).

## TIMESTAMPED INITIAL TASK MESSAGE (20261109T021829Z) — HEAVY WORK MANDATORY
**PRIORITY 1: EXECUTE C245.** C244 is complete on disk (VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_WINSORIZED_MEAN_SHOCK_MR, edge_claim NONE; cross-asset net sums fee0=-2.6672959793605595, fee5=-3.46329597936056, fee10=-4.259295979360561, fee20=-5.851295979360561, fee40=-9.03529597936056 — all cost slices negative; exposure true; oos_edge_proven false). C245 script does NOT yet exist on disk. **Do not summarize status. Do not stop at status. Implement + run C245 + emit >=4 artifacts with SHA256 from bytes + sync state.yaml + HANDOFF.** This is the only open campaign; no status-first replies, no stopping between campaigns.

## VERIFIED BASELINE (20261109T021829Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1, `/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python`).
- Collision guard verified 0 hits for `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_MIDHINGE_SHOCK_MR` at 20261109T021829Z — C245 primary is collision-free, runnable now.
- Caches: spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` (56075733...), spot meta (d03556ba...), volume `data/cache/volume_1h_full.pkl/meta/provenance` (43658953.../4d321584.../c7ff2f27...).
- **C241–C243 LOCKED (see state.yaml/registry).**
- **C244 DONE (verified on disk, SHAs from bytes):**
  - OOS 2fc63905932fb6c53db6aa02d411cd7e36ea866dc7bfbfa429e95364fb04f5f2 (`reports/real_quote_volume_rqa_rte_over_white_diag_line_length_winsorized_mean_shock_mr_costed_oos_20261109T021110Z.json`, VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_WINSORIZED_MEAN_SHOCK_MR, campaign 244, edge_claim NONE, oos_edge_proven false, any_exposure_oos true, all_cost_slices_positive false, all_cost_slices_beat_bh_mean_rule false, cross-asset fee0=-2.6672959793605595 fee5=-3.46329597936056 fee10=-4.259295979360561 fee20=-5.851295979360561 fee40=-9.03529597936056).
  - Ingest 29c51a57898e997db9b3d0a114ad8daaadaa0198b2bdc3df2aa4adfa8cbb7d22 (`reports/real_feed_ingest_attempt_20261109T021829Z.json`, rb_unblocked true, nonspot blocked fail-closed).
  - Registry abdac7c759d7af3f7be8fa7596d552b643eca37b4cea0a3c1b5ad20a1cdef75b (`reports/strategy_edge_registry_20261109T021829Z.json`) supersedes `reports/strategy_edge_registry_20261109T014330Z.json` 9751625c168c58db60e03180a156f167e6039e816aa7cc4edb94494e7d39a381.
  - Script 4fbd87613aeab6d200eafc0763387c49bdd6e57057e1e3558f1d02ba0eaf5a41 (`scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_winsorized_mean_shock_mr_costed_oos.py`, campaign 244, WHITE_DIAG_LINE_LENGTH_WINSORIZED_MEAN = scipy.stats.mstats.winsorize limits [0.1,0.1] (10% each tail) then arithmetic mean of qualifying WHITE diagonal segments, >=3 segments, winsorized mean>0; fail-closed). Distinctness grep 0 non-self at run.
  - Summary 2c29ea949bc07ac1c695aa9ff9279ee4dc5d18a66a38e04b39e5cacc77488030 (`reports/campaign244_execution_summary_20261109T021829Z.json`).
- Single durable handoff = this file + `research_state/state.yaml`.

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **Env bottleneck cleared.** Reuse `/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python` (deps_ok). Runs are CPU-heavy; allow sufficient timeout (~30 min) — **must complete C245 in this session**; no status-only replies.
- **Collision guard verified 0 at start.** C245 primary candidate grep-zero verified 20261109T021829Z — proceed without fallback.
- **No status-first.** Artifacts on disk are the deliverable.
- **No reruns of locked campaigns C104–C244.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Collision handling is fail-closed:** if a preselected candidate collides on grep, reject it, pick a distinct grep-zero fallback, record primary/fallback grep cmd/hits/evidence in all artifacts + state + HANDOFF.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence.
- **Heavy work mandatory.** No status-only replies. No stop between campaigns.

## C245 — NEXT FOCUS CAMPAIGN (PRESELECTED, GREP-ZERO VERIFIED 20261109T021829Z)
**Primary candidate:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_MIDHINGE_SHOCK_MR` — RQA ratio RTE / WHITE_DIAG_LINE_LENGTH_MIDHINGE on delay-embedded log-volume returns (RTE = recurrence time entropy of white vertical gap distribution, w>=w_min, LOI/self excluded; WHITE_DIAG_LINE_LENGTH_MIDHINGE = midhinge = (Q1 + Q3)/2 of lengths of qualifying WHITE diagonal segments (consecutive 0-cells/non-recurrent, length>=w_min=2) pooled over off-diagonal diagonals k!=0 with >=1 qualifying segment; Q1/Q3 = 25th/75th percentiles (numpy percentile or equivalent, fixed method); fail-closed if <3 qualifying segments or midhinge non-finite/non-positive). Distinct from WINSORIZED_MEAN(C244), TRIMMED_MEAN(C243), P10(C242), P90(C241), HARMONIC_MEAN(C240), GEOMEAN(C239), RMS(C238), ENTROPY(C237), GINI(C236), RANGE(C235), CV(C234), IQR(C233), MAD(C232), KURTOSIS(C231), SKEWNESS(C230), COUNT_VARIANCE(C229), DIAG_COUNT_VARIANCE(C228), DIVERGENCE(C227), VARIANCE(C226), and prior C125-C244 families.
**grep evidence (20261109T021829Z):** `grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_MIDHINGE|WHITE_DIAG_LINE_LENGTH_MIDHINGE' scripts/ strategies/ backtest/ utils/ 2>&1` → 0 hits.
**Fallbacks (grep-zero verified candidates):** `RTE_OVER_WHITE_DIAG_LINE_LENGTH_TRIMEAN_SHOCK_MR`, `RTE_OVER_WHITE_DIAG_LINE_LENGTH_BOWLEY_SKEW_SHOCK_MR`, `RTE_OVER_WHITE_DIAG_LINE_LENGTH_YULE_K_SHOCK_MR` (verify at start). At C245 start grep-verify; if collision, pick a distinct grep-zero fallback not used C125–C244 and record evidence.

### COLLISION GUARD (RUN AT START)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_MIDHINGE|WHITE_DIAG_LINE_LENGTH_MIDHINGE' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self
```
If collision found: pick a distinct grep-zero fallback not used C125–C244 (verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + state + HANDOFF.

### REQUIRED C245 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_midhinge_shock_mr_costed_oos.py` (or collision-safe). Model on C188–C244. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261109T021829Z.json` (abdac7c759d7af3f7be8fa7596d552b643eca37b4cea0a3c1b5ad20a1cdef75b), cite C244 OOS SHA `2fc63905932fb6c53db6aa02d411cd7e36ea866dc7bfbfa429e95364fb04f5f2`, C243 OOS SHA `35bd7caf8c10d0c333219c5df005d614efe57a87bb193e817dab02bd4dc1c712`, and C242 OOS SHA `5655c52e9bae7e7a7b90b1aef133497bbd6e6eb1bbecec58e977ca0e13242808`. Emit `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_midhinge_shock_mr_costed_oos_<UTC>.json` with `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds. **No carryover template text; set `campaign: 245`.**
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 245). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261109T021829Z.json` (abdac7c759d7af3f7be8fa7596d552b643eca37b4cea0a3c1b5ad20a1cdef75b). Include prior + all C245 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign245_execution_summary_<UTC>.json` listing **all new C245 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C245`, `next_campaign: C246`, latest registry/OOS sha+path, `oos_edge_proven`, `c246_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C245, with grep cmd/hits/evidence). Update this `HANDOFF.md`.

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_MIDHINGE|WHITE_DIAG_LINE_LENGTH_MIDHINGE' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self
# NOW: implement+run C245 -> emit >=4 artifacts with SHAs -> sync state.yaml + HANDOFF
```
