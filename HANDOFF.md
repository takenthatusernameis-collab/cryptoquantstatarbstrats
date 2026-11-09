# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261109T001931Z, C104–C239 LOCKED — edge_claim NONE, C239 DONE, C240 PRESELECTED HEAVY — EXECUTE NEXT, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C239 LOCKED (no reruns). C239 DONE on disk (edge_claim NONE). C240 preselected grep-zero (VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_HARMONIC_MEAN_SHOCK_MR) — execute C240 next, no status-first.** Latest registry = `reports/strategy_edge_registry_20261109T001931Z.json` (d7d4d6a4dbf091b6a273199e64ffaeba503b8a693b28163fcfd19886fced63cd). Latest OOS = C239 `76b139d6065b9366495f2fbdcb99bb9a2df4473bdaf0329d3b0a79f97fc3b61d` (oos_edge_proven false).

## TIMESTAMPED INITIAL TASK MESSAGE (20261109T001931Z) — HEAVY WORK MANDATORY
**PRIORITY 1: EXECUTE C240.** C239 is complete on disk (VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_GEOMEAN_SHOCK_MR, edge_claim NONE; cross-asset net sums fee0=-2.0690420139072594, fee5=-3.0970420139072603, fee10=-4.125042013907262, fee20=-6.181042013907261, fee40=-10.293042013907261 — all cost slices negative, beat_bh_mean_rule false; exposure true; oos_edge_proven false). C240 script does NOT yet exist on disk. **Do not summarize status. Do not stop at status. Implement + run C240 + emit >=4 artifacts with SHA256 from bytes + sync state.yaml + HANDOFF.**

## VERIFIED BASELINE (20261109T001931Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1, `/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python`).
- Caches: `data/cache/volume_1h_full.pkl/meta/provenance` (43658953.../4d321584.../c7ff2f27...), spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` (56075733...).
- **C235 DONE (locked):** VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_RANGE_SHOCK_MR, oos b1ea67400604f627f2232cfdf2511d6e06650e4968793f016d7dcbda8f49892b, edge_claim NONE.
- **C236 DONE (locked):** VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_GINI_SHOCK_MR, oos 81d9a4ae5708ce29cd2e5dcde1c163fa1e87379f3aa766dd65a344378f22d0ff, edge_claim NONE.
- **C237 DONE (locked):** VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_ENTROPY_SHOCK_MR, oos ca975ead97434b958a2c7dc7e03a1b472aeaceadcf0b99abea6213ab0e6d4ce5, edge_claim NONE.
- **C238 DONE (verified on disk):** VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_RMS_SHOCK_MR, oos 55af89a05949ac522c05f83fc35fc962cc6d25d448834d690e51f43fac95b23e, edge_claim NONE, oos_edge_proven false.
- **C239 DONE (verified on disk, SHAs from bytes):**
  - OOS 76b139d6065b9366495f2fbdcb99bb9a2df4473bdaf0329d3b0a79f97fc3b61d (`reports/real_quote_volume_rqa_rte_over_white_diag_line_length_geomean_shock_mr_costed_oos_20261109T001931Z.json`, VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_GEOMEAN_SHOCK_MR, campaign 239, edge_claim NONE, oos_edge_proven false, any_exposure_oos true, all_cost_slices_positive false, beat_bh_mean_rule false).
  - Ingest 64f421ec31003a36f5c14fccb0136cb57eb453208dbacd535f658679331742e0 (`reports/real_feed_ingest_attempt_20261109T001931Z.json`).
  - Registry d7d4d6a4dbf091b6a273199e64ffaeba503b8a693b28163fcfd19886fced63cd (`reports/strategy_edge_registry_20261109T001931Z.json`) supersedes reports/strategy_edge_registry_20261109T001601Z.json e2dbad920ae9ffa4f3ea373f180032f8160d8ffa6c93df4d165f8f39c0bb052f.
  - Script f41b02029ea1c565315cd15f476c36d97fbe799160796d75b8445ed6e33493ea (`scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_geomean_shock_mr_costed_oos.py`, campaign 239, WHITE_DIAG_LINE_LENGTH_GEOMEAN = geometric mean of lengths of qualifying WHITE diagonal segments, >=3 segments, geomean>0; fail-closed). Distinctness grep 0 non-self at run.
  - Summary 7874ce6df89ac47c73c6a5d08ba77757c3bd6ba67bed2a64bef6f5be98841c99 (`reports/campaign239_execution_summary_20261109T001931Z.json`).
- Single durable handoff = this file + `research_state/state.yaml`.

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **Env bottleneck cleared.** Reuse `/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python` (deps_ok). Runs are CPU-heavy (~8-12 min); run with patience — **must complete C240 in this session**; no status-only replies.
- **Collision guard required at start.** C240 primary candidate is grep-zero verified 20261109T001931Z.
- **No status-first.** Artifacts on disk are the deliverable.
- **No reruns of locked campaigns C104–C239.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Collision handling is fail-closed:** if a preselected candidate collides on grep, reject it, pick a distinct grep-zero fallback, record primary/fallback grep cmd/hits/evidence in all artifacts + state + HANDOFF.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence.
- **Heavy work mandatory.** No status-only replies. No stop between campaigns.

## C240 — NEXT FOCUS CAMPAIGN (PRESELECTED, GREP-ZERO VERIFIED 20261109T001931Z)
**Primary candidate:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_HARMONIC_MEAN_SHOCK_MR` — RQA ratio RTE / WHITE_DIAG_LINE_LENGTH_HARMONIC_MEAN on delay-embedded log-volume returns (RTE = recurrence time entropy of white vertical gap distribution, w>=w_min, LOI/self excluded; WHITE_DIAG_LINE_LENGTH_HARMONIC_MEAN = harmonic mean of lengths of qualifying WHITE diagonal segments (consecutive 0-cells/non-recurrent, length>=w_min=2) pooled over off-diagonal diagonals k!=0 with >=1 qualifying segment; fail-closed if <3 qualifying segments or harmonic mean non-finite/non-positive). Distinct from GEOMEAN(C239), RMS(C238), ENTROPY(C237), GINI(C236), RANGE(C235), CV(C234), IQR(C233), MAD(C232), KURTOSIS(C231), SKEWNESS(C230), COUNT_VARIANCE(C229), DIAG_COUNT_VARIANCE(C228), DIVERGENCE(C227), VARIANCE(C226), and prior C125-C239 families.
**grep evidence (20261109T001931Z):** `grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_HARMONIC_MEAN|WHITE_DIAG_LINE_LENGTH_HARMONIC_MEAN' scripts/ strategies/ backtest/ utils/ 2>&1` → 0 hits.
**Fallbacks (grep-zero verified 20261109T001931Z):** `RTE_OVER_WHITE_DIAG_LINE_LENGTH_P90_SHOCK_MR` (0). At C240 start grep-verify; if collision, pick a distinct grep-zero fallback not used C125–C239 and record evidence.

### COLLISION GUARD (RUN AT START)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_HARMONIC_MEAN|WHITE_DIAG_LINE_LENGTH_HARMONIC_MEAN' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self
```
If collision found: pick a distinct grep-zero fallback not used C125–C239 (verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + state + HANDOFF.

### REQUIRED C240 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_harmonic_mean_shock_mr_costed_oos.py` (or collision-safe). Model on C188–C239. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261109T001931Z.json` (d7d4d6a4dbf091b6a273199e64ffaeba503b8a693b28163fcfd19886fced63cd), cite C239 OOS SHA `76b139d6065b9366495f2fbdcb99bb9a2df4473bdaf0329d3b0a79f97fc3b61d`, C238 OOS SHA `55af89a05949ac522c05f83fc35fc962cc6d25d448834d690e51f43fac95b23e`, and C237 OOS SHA `ca975ead97434b958a2c7dc7e03a1b472aeaceadcf0b99abea6213ab0e6d4ce5`. Emit `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_harmonic_mean_shock_mr_costed_oos_<UTC>.json` with `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds. **No carryover template text; set `campaign: 240`.**
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 240). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261109T001931Z.json` (d7d4d6a4dbf091b6a273199e64ffaeba503b8a693b28163fcfd19886fced63cd). Include prior + all C240 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign240_execution_summary_<UTC>.json` listing **all new C240 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C240`, `next_campaign: C241`, latest registry/OOS sha+path, `oos_edge_proven`, `c241_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C240, with grep cmd/hits/evidence). Update this `HANDOFF.md`.

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_HARMONIC_MEAN|WHITE_DIAG_LINE_LENGTH_HARMONIC_MEAN' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self
# NOW: implement+run C240 -> emit >=4 artifacts with SHAs -> sync state.yaml + HANDOFF
```
