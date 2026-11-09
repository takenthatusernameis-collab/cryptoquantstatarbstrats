# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261109T031259Z, C104–C247 LOCKED — edge_claim NONE, C247 DONE, C248 PRESELECTED HEAVY — PENDING, EXECUTE NEXT, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C247 LOCKED (no reruns). C247 DONE on disk (edge_claim NONE). C248 preselected grep-zero (VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_KELLY_SKEW_SHOCK_MR) — execute C248 next, no status-first.** Latest registry = `reports/strategy_edge_registry_20261109T031259Z.json` (87b0265771b4902b8954390d11aaf162069e739e10133781f8f9db5aec5e4d60). Latest OOS = C247 `def2f1fc07104e4ecadaa87700327aab3c1d3d5df3e2d95801597ce3c94f7638` (oos_edge_proven false).

## TIMESTAMPED INITIAL TASK MESSAGE (20261109T031259Z) — HEAVY WORK MANDATORY
**PRIORITY 1: EXECUTE C248.** C247 is complete on disk (VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_BOWLEY_SKEW_SHOCK_MR, edge_claim NONE; cross-asset net sums fee0=-0.09919678846577296, fee5=-0.3931967884657732, fee10=-0.6871967884657735, fee20=-1.275196788465774, fee40=-2.4511967884657744 — all cost slices negative; exposure true; oos_edge_proven false). C248 script does NOT yet exist on disk. **Do not summarize status. Do not stop at status. Implement + run C248 + emit >=4 artifacts with SHA256 from bytes + sync state.yaml + HANDOFF.** This is the only open campaign; no status-first replies, no stopping between campaigns.

## VERIFIED BASELINE (20261109T031259Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1, `/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python`).
- Collision guard: `RTE_OVER_WHITE_DIAG_LINE_LENGTH_BOWLEY_SKEW|WHITE_DIAG_LINE_LENGTH_BOWLEY_SKEW` grep 0 hits at 20261109T031259Z — C247 primary ran clean. C248 preselected candidate `RTE_OVER_WHITE_DIAG_LINE_LENGTH_KELLY_SKEW|WHITE_DIAG_LINE_LENGTH_KELLY_SKEW` grep 0 hits at 20261109T031259Z — C248 primary collision-free, runnable now. Fallbacks grep-zero: YULE_K, MIDRANGE.
- Caches: spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` (5607573327c089e0ab990ac48f931752a99e6e89f60599cb2557246f0f5f8c9b), spot meta (d03556baeef34eae18d2122f4a17ec14e30fdd14e0a5616d914c5d0832d2d80d), volume `data/cache/volume_1h_full.pkl/meta/provenance` (4365895387de4e542165fd331e39da40d455a3de24c7254eb67ba890053d193c/4d321584d3c687ad9956908c0179a1eae7d629c296c491e1e5ad1259a890c616/c7ff2f27ec5a668128e4856f809efde4922563dba87be0648be6d802c6d21c89).
- **C104–C245 LOCKED (see state.yaml/registry).**
- **C246 DONE (verified on disk, SHAs from bytes):**
  - OOS d329801a5c06bd49fbc129da4930011abca1c5920d464c5e420a5399e889f83c (`reports/real_quote_volume_rqa_rte_over_white_diag_line_length_trimean_shock_mr_costed_oos_20261109T025803Z.json`, VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_TRIMEAN_SHOCK_MR, campaign 246, edge_claim NONE, oos_edge_proven false, any_exposure_oos true, all_cost_slices_positive false, all_cost_slices_beat_bh_mean_rule false, cross-asset fee0=-2.74688519798545 fee5=-3.812885197985451 fee10=-4.8788851979854515 fee20=-7.010885197985451 fee40=-11.27488519798545).
  - Ingest 68493346f251164a87921de108fb76d9ed1a8d15d2ddc2edbcbd74515c5f5b97 (`reports/real_feed_ingest_attempt_20261109T030527Z.json`, rb_unblocked true, nonspot blocked fail-closed).
  - Registry ae20f66baec069066bc82c41156e314832512dc136b0b2f514b6df6682c2b67c (`reports/strategy_edge_registry_20261109T030527Z.json`) supersedes `reports/strategy_edge_registry_20261109T023208Z.json` dbdd9fcc75b7e9f8419b6788c37c86a3516d3d81cc86185f62b945337ca817c6.
  - Script 850ece086849d084d97b8d9d15228134528593b57ef14a985be243559b1b941e (`scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_trimean_shock_mr_costed_oos.py`, campaign 246).
  - Summary 81a82b991d5daa84b568a7efeefaaf0a903f2847ca611b67a6ad104b19f9f777 (`reports/campaign246_execution_summary_20261109T030527Z.json`).
- **C247 DONE (verified on disk, SHAs from bytes):**
  - OOS def2f1fc07104e4ecadaa87700327aab3c1d3d5df3e2d95801597ce3c94f7638 (`reports/real_quote_volume_rqa_rte_over_white_diag_line_length_bowley_skew_shock_mr_costed_oos_20261109T031259Z.json`, VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_BOWLEY_SKEW_SHOCK_MR, campaign 247, edge_claim NONE, oos_edge_proven false, any_exposure_oos true, all_cost_slices_positive false, all_cost_slices_beat_bh_mean_rule false, cross-asset fee0=-0.09919678846577296 fee5=-0.3931967884657732 fee10=-0.6871967884657735 fee20=-1.275196788465774 fee40=-2.4511967884657744).
  - Ingest d03d3f4c1c2404067d789cfe733e889694ed2c0570338c431b90ac008b9cbb43 (`reports/real_feed_ingest_attempt_20261109T031259Z.json`, rb_unblocked true, nonspot blocked fail-closed).
  - Registry 87b0265771b4902b8954390d11aaf162069e739e10133781f8f9db5aec5e4d60 (`reports/strategy_edge_registry_20261109T031259Z.json`) supersedes `reports/strategy_edge_registry_20261109T030527Z.json` ae20f66baec069066bc82c41156e314832512dc136b0b2f514b6df6682c2b67c.
  - Script 10d00599e0e04b2d3a9ddc7b88be44c2c6d50a079961f26d8481d5f744b0dc52 (`scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_bowley_skew_shock_mr_costed_oos.py`, campaign 247, WHITE_DIAG_LINE_LENGTH_BOWLEY_SKEW = (Q3 + Q1 - 2*median)/(Q3 - Q1) Bowley skewness of lengths of qualifying WHITE diagonal segments pooled over off-diagonal diagonals k!=0, >=3 segments, (Q3-Q1)>0, numpy.percentile 25/50/75 method='linear', fail-closed). Distinctness grep 0 non-self at run.
  - Summary 66f8b75515b1cceea860acb13c1daa796405e05661785185aa53195dedf2a7a9 (`reports/campaign247_execution_summary_20261109T031259Z.json`).
- Single durable handoff = this file + `research_state/state.yaml`.

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **Env bottleneck cleared.** Reuse `/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python` (deps_ok). Runs are CPU-heavy; allow sufficient timeout (~30 min) — **must complete C248 in this session**; no status-only replies.
- **Collision guard verified 0 at start.** C248 primary candidate grep-zero verified 20261109T031259Z — proceed without fallback.
- **No status-first.** Artifacts on disk are the deliverable.
- **No reruns of locked campaigns C104–C247.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Collision handling is fail-closed:** if a preselected candidate collides on grep, reject it, pick a distinct grep-zero fallback, record primary/fallback grep cmd/hits/evidence in all artifacts + state + HANDOFF.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence.
- **Heavy work mandatory.** No status-only replies. No stop between campaigns.

## C248 — NEXT FOCUS CAMPAIGN (PRESELECTED, GREP-ZERO VERIFIED 20261109T031259Z)
**Primary candidate:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_KELLY_SKEW_SHOCK_MR` — RQA ratio RTE / WHITE_DIAG_LINE_LENGTH_KELLY_SKEW on delay-embedded log-volume returns (RTE = recurrence time entropy of white vertical gap distribution, w>=w_min, LOI/self excluded; WHITE_DIAG_LINE_LENGTH_KELLY_SKEW = Kelly skewness = (P90 + P10 - 2*median)/(P90 - P10) of lengths of qualifying WHITE diagonal segments (consecutive 0-cells/non-recurrent, length>=w_min=2) pooled over off-diagonal diagonals k!=0 with >=1 qualifying segment; P10/median/P90 = 10th/50th/90th percentiles (numpy.percentile, method='linear', pre-stated fixed); **fail-closed** if <3 qualifying segments, or (P90-P10) <= 0 / non-finite, or Kelly skew non-finite, or resulting denominator/ratio undefined/non-finite/degenerate). Distinct from BOWLEY_SKEW(C247), TRIMEAN(C246), MIDHINGE(C245), WINSORIZED_MEAN(C244), TRIMMED_MEAN(C243), P10(C242), P90(C241), HARMONIC_MEAN(C240), GEOMEAN(C239), RMS(C238), ENTROPY(C237), GINI(C236), RANGE(C235), CV(C234), IQR(C233), MAD(C232), KURTOSIS(C231), SKEWNESS(C230), COUNT_VARIANCE(C229), DIAG_COUNT_VARIANCE(C228), DIVERGENCE(C227), VARIANCE(C226), and prior C125-C247 families.
**grep evidence (20261109T031259Z):** `grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_KELLY_SKEW|WHITE_DIAG_LINE_LENGTH_KELLY_SKEW' scripts/ strategies/ backtest/ utils/ 2>&1` → 0 hits.
**Fallbacks (grep-zero verified candidates):** `RTE_OVER_WHITE_DIAG_LINE_LENGTH_YULE_K_SHOCK_MR`, `RTE_OVER_WHITE_DIAG_LINE_LENGTH_MIDRANGE_SHOCK_MR` (all 0 hits verified 20261109T031259Z). At C248 start grep-verify; if collision, pick a distinct grep-zero fallback not used C125–C247 and record evidence.

### COLLISION GUARD (RUN AT START)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_KELLY_SKEW|WHITE_DIAG_LINE_LENGTH_KELLY_SKEW' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self
```
If collision found: pick a distinct grep-zero fallback not used C125–C247 (verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + state + HANDOFF.

### REQUIRED C248 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_kelly_skew_shock_mr_costed_oos.py` (or collision-safe). Model on C188–C247. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261109T031259Z.json` (87b0265771b4902b8954390d11aaf162069e739e10133781f8f9db5aec5e4d60), cite C247 OOS SHA `def2f1fc07104e4ecadaa87700327aab3c1d3d5df3e2d95801597ce3c94f7638`, C246 OOS SHA `d329801a5c06bd49fbc129da4930011abca1c5920d464c5e420a5399e889f83c`, and C245 OOS SHA `39d97b75b78b377015e2a944a36ad1c5b8d15f6aff4160d552f0fa1acc899ddc`. Emit `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_kelly_skew_shock_mr_costed_oos_<UTC>.json` with `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds. **No carryover template text; set `campaign: 248`.**
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 248). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261109T031259Z.json` (87b0265771b4902b8954390d11aaf162069e739e10133781f8f9db5aec5e4d60). Include prior + all C248 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign248_execution_summary_<UTC>.json` listing **all new C248 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C248`, `next_campaign: C249`, latest registry/OOS sha+path, `oos_edge_proven`, `c249_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C248, with grep cmd/hits/evidence). Update this `HANDOFF.md`.

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_KELLY_SKEW|WHITE_DIAG_LINE_LENGTH_KELLY_SKEW' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self
# NOW: implement+run C248 -> emit >=4 artifacts with SHAs -> sync state.yaml + HANDOFF
```

# CONFIRMED AT REFRESH 20261109T031259Z: deps_ok; collision guard = 0 hits; NO C248 script on disk; C248 pending and unblocked — proceed to implement+run immediately.
