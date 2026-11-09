# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261109T030859Z, C104–C246 LOCKED — edge_claim NONE, C246 DONE, C247 PRESELECTED HEAVY — PENDING, EXECUTE NEXT, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C246 LOCKED (no reruns). C246 DONE on disk (edge_claim NONE). C247 preselected grep-zero (VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_BOWLEY_SKEW_SHOCK_MR) — execute C247 next, no status-first.** Latest registry = `reports/strategy_edge_registry_20261109T030527Z.json` (ae20f66baec069066bc82c41156e314832512dc136b0b2f514b6df6682c2b67c). Latest OOS = C246 `d329801a5c06bd49fbc129da4930011abca1c5920d464c5e420a5399e889f83c` (oos_edge_proven false).

## TIMESTAMPED INITIAL TASK MESSAGE (20261109T030859Z) — HEAVY WORK MANDATORY
**PRIORITY 1: EXECUTE C247.** C246 is complete on disk (VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_TRIMEAN_SHOCK_MR, edge_claim NONE; cross-asset net sums fee0=-2.74688519798545, fee5=-3.812885197985451, fee10=-4.8788851979854515, fee20=-7.010885197985451, fee40=-11.27488519798545 — all cost slices negative; exposure true; oos_edge_proven false). C247 script does NOT yet exist on disk. **Do not summarize status. Do not stop at status. Implement + run C247 + emit >=4 artifacts with SHA256 from bytes + sync state.yaml + HANDOFF.** This is the only open campaign; no status-first replies, no stopping between campaigns.

## VERIFIED BASELINE (20261109T030859Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1, `/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python`).
- Collision guard: `RTE_OVER_WHITE_DIAG_LINE_LENGTH_BOWLEY_SKEW|WHITE_DIAG_LINE_LENGTH_BOWLEY_SKEW` grep 0 hits at 20261109T030859Z — C247 primary is collision-free, runnable now. Fallbacks grep-zero: YULE_K, KELLY_SKEW, MIDRANGE.
- Caches: spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` (5607573327c089e0ab990ac48f931752a99e6e89f60599cb2557246f0f5f8c9b), spot meta (d03556baeef34eae18d2122f4a17ec14e30fdd14e0a5616d914c5d0832d2d80d), volume `data/cache/volume_1h_full.pkl/meta/provenance` (4365895387de4e542165fd331e39da40d455a3de24c7254eb67ba890053d193c/4d321584d3c687ad9956908c0179a1eae7d629c296c491e1e5ad1259a890c616/c7ff2f27ec5a668128e4856f809efde4922563dba87be0648be6d802c6d21c89).
- **C104–C245 LOCKED (see state.yaml/registry).**
- **C246 DONE (verified on disk, SHAs from bytes):**
  - OOS d329801a5c06bd49fbc129da4930011abca1c5920d464c5e420a5399e889f83c (`reports/real_quote_volume_rqa_rte_over_white_diag_line_length_trimean_shock_mr_costed_oos_20261109T025803Z.json`, VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_TRIMEAN_SHOCK_MR, campaign 246, edge_claim NONE, oos_edge_proven false, any_exposure_oos true, all_cost_slices_positive false, all_cost_slices_beat_bh_mean_rule false, cross-asset fee0=-2.74688519798545 fee5=-3.812885197985451 fee10=-4.8788851979854515 fee20=-7.010885197985451 fee40=-11.27488519798545).
  - Ingest 68493346f251164a87921de108fb76d9ed1a8d15d2ddc2edbcbd74515c5f5b97 (`reports/real_feed_ingest_attempt_20261109T030527Z.json`, rb_unblocked true, nonspot blocked fail-closed).
  - Registry ae20f66baec069066bc82c41156e314832512dc136b0b2f514b6df6682c2b67c (`reports/strategy_edge_registry_20261109T030527Z.json`) supersedes `reports/strategy_edge_registry_20261109T023208Z.json` dbdd9fcc75b7e9f8419b6788c37c86a3516d3d81cc86185f62b945337ca817c6.
  - Script 850ece086849d084d97b8d9d15228134528593b57ef14a985be243559b1b941e (`scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_trimean_shock_mr_costed_oos.py`, campaign 246, WHITE_DIAG_LINE_LENGTH_TRIMEAN = (Q1 + 2*median + Q3)/4 of qualifying WHITE diagonal segments, Q1/median/Q3 = numpy.percentile 25/50/75 method='linear', >=3 segments, trimean>0; fail-closed). Distinctness grep 0 non-self at run.
  - Summary 81a82b991d5daa84b568a7efeefaaf0a903f2847ca611b67a6ad104b19f9f777 (`reports/campaign246_execution_summary_20261109T030527Z.json`).
- Single durable handoff = this file + `research_state/state.yaml`.

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **Env bottleneck cleared.** Reuse `/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python` (deps_ok). Runs are CPU-heavy; allow sufficient timeout (~30 min) — **must complete C247 in this session**; no status-only replies.
- **Collision guard verified 0 at start.** C247 primary candidate grep-zero verified 20261109T030859Z — proceed without fallback.
- **No status-first.** Artifacts on disk are the deliverable.
- **No reruns of locked campaigns C104–C246.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Collision handling is fail-closed:** if a preselected candidate collides on grep, reject it, pick a distinct grep-zero fallback, record primary/fallback grep cmd/hits/evidence in all artifacts + state + HANDOFF.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence.
- **Heavy work mandatory.** No status-only replies. No stop between campaigns.

## C247 — NEXT FOCUS CAMPAIGN (PRESELECTED, GREP-ZERO VERIFIED 20261109T030859Z)
**Primary candidate:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_BOWLEY_SKEW_SHOCK_MR` — RQA ratio RTE / WHITE_DIAG_LINE_LENGTH_BOWLEY_SKEW on delay-embedded log-volume returns (RTE = recurrence time entropy of white vertical gap distribution, w>=w_min, LOI/self excluded; WHITE_DIAG_LINE_LENGTH_BOWLEY_SKEW = Bowley skewness = (Q3 + Q1 - 2*median)/(Q3 - Q1) of lengths of qualifying WHITE diagonal segments (consecutive 0-cells/non-recurrent, length>=w_min=2) pooled over off-diagonal diagonals k!=0 with >=1 qualifying segment; Q1/median/Q3 = 25th/50th/75th percentiles (numpy.percentile, method='linear', pre-stated fixed); **fail-closed** if <3 qualifying segments, or (Q3-Q1) <= 0 / non-finite, or bowley skew non-finite, or resulting denominator/ratio undefined/non-finite/degenerate). Distinct from TRIMEAN(C246), MIDHINGE(C245), WINSORIZED_MEAN(C244), TRIMMED_MEAN(C243), P10(C242), P90(C241), HARMONIC_MEAN(C240), GEOMEAN(C239), RMS(C238), ENTROPY(C237), GINI(C236), RANGE(C235), CV(C234), IQR(C233), MAD(C232), KURTOSIS(C231), SKEWNESS(C230), COUNT_VARIANCE(C229), DIAG_COUNT_VARIANCE(C228), DIVERGENCE(C227), VARIANCE(C226), and prior C125-C246 families.
**grep evidence (20261109T030859Z):** `grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_BOWLEY_SKEW|WHITE_DIAG_LINE_LENGTH_BOWLEY_SKEW' scripts/ strategies/ backtest/ utils/ 2>&1` → 0 hits.
**Fallbacks (grep-zero verified candidates):** `RTE_OVER_WHITE_DIAG_LINE_LENGTH_YULE_K_SHOCK_MR`, `RTE_OVER_WHITE_DIAG_LINE_LENGTH_KELLY_SKEW_SHOCK_MR`, `RTE_OVER_WHITE_DIAG_LINE_LENGTH_MIDRANGE_SHOCK_MR` (all 0 hits verified 20261109T030859Z). At C247 start grep-verify; if collision, pick a distinct grep-zero fallback not used C125–C246 and record evidence.

### COLLISION GUARD (RUN AT START)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_BOWLEY_SKEW|WHITE_DIAG_LINE_LENGTH_BOWLEY_SKEW' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self
```
If collision found: pick a distinct grep-zero fallback not used C125–C246 (verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + state + HANDOFF.

### REQUIRED C247 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_bowley_skew_shock_mr_costed_oos.py` (or collision-safe). Model on C188–C246. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261109T030527Z.json` (ae20f66baec069066bc82c41156e314832512dc136b0b2f514b6df6682c2b67c), cite C246 OOS SHA `d329801a5c06bd49fbc129da4930011abca1c5920d464c5e420a5399e889f83c`, C245 OOS SHA `39d97b75b78b377015e2a944a36ad1c5b8d15f6aff4160d552f0fa1acc899ddc`, and C244 OOS SHA `2fc63905932fb6c53db6aa02d411cd7e36ea866dc7bfbfa429e95364fb04f5f2`. Emit `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_bowley_skew_shock_mr_costed_oos_<UTC>.json` with `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds. **No carryover template text; set `campaign: 247`.**
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 247). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261109T030527Z.json` (ae20f66baec069066bc82c41156e314832512dc136b0b2f514b6df6682c2b67c). Include prior + all C247 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign247_execution_summary_<UTC>.json` listing **all new C247 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C247`, `next_campaign: C248`, latest registry/OOS sha+path, `oos_edge_proven`, `c248_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C247, with grep cmd/hits/evidence). Update this `HANDOFF.md`.

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_BOWLEY_SKEW|WHITE_DIAG_LINE_LENGTH_BOWLEY_SKEW' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self
# NOW: implement+run C247 -> emit >=4 artifacts with SHAs -> sync state.yaml + HANDOFF
```

# CONFIRMED AT REFRESH 20261109T030859Z: deps_ok; collision guard = 0 hits; NO C247 script on disk; C247 pending and unblocked — proceed to implement+run immediately.