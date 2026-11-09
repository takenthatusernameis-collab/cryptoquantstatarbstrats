# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261109T003420Z, C104–C240 LOCKED — edge_claim NONE, C240 DONE, C241 PRESELECTED HEAVY — EXECUTE NEXT, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C240 LOCKED (no reruns). C240 DONE on disk (edge_claim NONE). C241 preselected grep-zero (VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_P90_SHOCK_MR) — execute C241 next, no status-first.** Latest registry = `reports/strategy_edge_registry_20261109T003420Z.json` (453a374c47bdb0a634ec91ecaa86a3cb461e6d2e13d604227eff49f162bdda19). Latest OOS = C240 `d24b0a8b45ec2ef767b53ff1f4493586fb8ac66d6208b60d6833cf8429093f23` (oos_edge_proven false).

## TIMESTAMPED INITIAL TASK MESSAGE (20261109T003420Z) — HEAVY WORK MANDATORY
**PRIORITY 1: EXECUTE C241.** C240 is complete on disk (VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_HARMONIC_MEAN_SHOCK_MR, edge_claim NONE; cross-asset net sums fee0=-0.2565430814052869, fee5=-1.7625430814052883, fee10=-3.2685430814052885, fee20=-6.2805430814052885, fee40=-12.304543081405287 — all cost slices negative, beat_bh_mean_rule false; exposure true; oos_edge_proven false). C241 script does NOT yet exist on disk. **Do not summarize status. Do not stop at status. Implement + run C241 + emit >=4 artifacts with SHA256 from bytes + sync state.yaml + HANDOFF.**

## VERIFIED BASELINE (20261109T003420Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1, `/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python`).
- Caches: spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` (56075733...), volume `data/cache/volume_1h_full.pkl/meta/provenance` (43658953.../4d321584.../c7ff2f27...).
- **C238 DONE (locked):** RMS, oos 55af89a05949ac522c05f83fc35fc962cc6d25d448834d690e51f43fac95b23e, edge_claim NONE.
- **C239 DONE (locked):** GEOMEAN, oos 76b139d6065b9366495f2fbdcb99bb9a2df4473bdaf0329d3b0a79f97fc3b61d, registry d7d4d6a4dbf091b6a273199e64ffaeba503b8a693b28163fcfd19886fced63cd, edge_claim NONE.
- **C240 DONE (verified on disk, SHAs from bytes):**
  - OOS d24b0a8b45ec2ef767b53ff1f4493586fb8ac66d6208b60d6833cf8429093f23 (`reports/real_quote_volume_rqa_rte_over_white_diag_line_length_harmonic_mean_shock_mr_costed_oos_20261109T003419Z.json`, VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_HARMONIC_MEAN_SHOCK_MR, campaign 240, edge_claim NONE, oos_edge_proven false, any_exposure_oos true, all_cost_slices_positive false, beat_bh_mean_rule false, cross-asset fee0=-0.2565430814052869 fee5=-1.7625430814052883 fee10=-3.2685430814052885 fee20=-6.2805430814052885 fee40=-12.304543081405287).
  - Ingest cfae5e5a6fbbb32862a27e4291c17e65c11dc7028291201c8f2ad2477f7c5c7c (`reports/real_feed_ingest_attempt_20261109T003420Z.json`, rb_unblocked true, nonspot blocked fail-closed).
  - Registry 453a374c47bdb0a634ec91ecaa86a3cb461e6d2e13d604227eff49f162bdda19 (`reports/strategy_edge_registry_20261109T003420Z.json`) supersedes `reports/strategy_edge_registry_20261109T001931Z.json` d7d4d6a4dbf091b6a273199e64ffaeba503b8a693b28163fcfd19886fced63cd.
  - Script 720899cfea531ef0b8eb5ca56199b57c5bc8183d7feca1d6efd516fc1f0447e7 (`scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_harmonic_mean_shock_mr_costed_oos.py`, campaign 240, WHITE_DIAG_LINE_LENGTH_HARMONIC_MEAN = harmonic mean n/sum(1/s_i) of qualifying WHITE diagonal segments, >=3 segments, hmean>0; fail-closed). Distinctness grep 0 non-self at run.
  - Summary 2599042c07f2f11f4c4e9f6ac43b8813e613b6fb474ff1d66ec96aed6c4bce4b (`reports/campaign240_execution_summary_20261109T003420Z.json`).
- Single durable handoff = this file + `research_state/state.yaml`.

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **Env bottleneck cleared.** Reuse `/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python` (deps_ok). Runs are CPU-heavy (~8-15 min); run with patience — **must complete C241 in this session**; no status-only replies.
- **Collision guard required at start.** C241 primary candidate is grep-zero verified 20261109T003420Z.
- **No status-first.** Artifacts on disk are the deliverable.
- **No reruns of locked campaigns C104–C240.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Collision handling is fail-closed:** if a preselected candidate collides on grep, reject it, pick a distinct grep-zero fallback, record primary/fallback grep cmd/hits/evidence in all artifacts + state + HANDOFF.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence.
- **Heavy work mandatory.** No status-only replies. No stop between campaigns.

## C241 — NEXT FOCUS CAMPAIGN (PRESELECTED, GREP-ZERO VERIFIED 20261109T003420Z)
**Primary candidate:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_P90_SHOCK_MR` — RQA ratio RTE / WHITE_DIAG_LINE_LENGTH_P90 on delay-embedded log-volume returns (RTE = recurrence time entropy of white vertical gap distribution, w>=w_min, LOI/self excluded; WHITE_DIAG_LINE_LENGTH_P90 = 90th percentile of lengths of qualifying WHITE diagonal segments (consecutive 0-cells/non-recurrent, length>=w_min=2) pooled over off-diagonal diagonals k!=0 with >=1 qualifying segment; fail-closed if <3 qualifying segments or P90 non-finite/non-positive). Distinct from HARMONIC_MEAN(C240), GEOMEAN(C239), RMS(C238), ENTROPY(C237), GINI(C236), RANGE(C235), CV(C234), IQR(C233), MAD(C232), KURTOSIS(C231), SKEWNESS(C230), COUNT_VARIANCE(C229), DIAG_COUNT_VARIANCE(C228), DIVERGENCE(C227), VARIANCE(C226), and prior C125-C240 families.
**grep evidence (20261109T003420Z):** `grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_P90|WHITE_DIAG_LINE_LENGTH_P90' scripts/ strategies/ backtest/ utils/ 2>&1` → 0 hits.
**Fallbacks (grep-zero verified 20261109T003420Z):** `RTE_OVER_WHITE_DIAG_LINE_LENGTH_P10_SHOCK_MR` (verify at start), `RTE_OVER_WHITE_DIAG_LINE_LENGTH_MEDIAN_ABS_DEV_SHOCK_MR` (verify at start). At C241 start grep-verify; if collision, pick a distinct grep-zero fallback not used C125–C240 and record evidence.

### COLLISION GUARD (RUN AT START)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_P90|WHITE_DIAG_LINE_LENGTH_P90' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self
```
If collision found: pick a distinct grep-zero fallback not used C125–C240 (verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + state + HANDOFF.

### REQUIRED C241 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_p90_shock_mr_costed_oos.py` (or collision-safe). Model on C188–C240. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261109T003420Z.json` (453a374c47bdb0a634ec91ecaa86a3cb461e6d2e13d604227eff49f162bdda19), cite C240 OOS SHA `d24b0a8b45ec2ef767b53ff1f4493586fb8ac66d6208b60d6833cf8429093f23`, C239 OOS SHA `76b139d6065b9366495f2fbdcb99bb9a2df4473bdaf0329d3b0a79f97fc3b61d`, and C238 OOS SHA `55af89a05949ac522c05f83fc35fc962cc6d25d448834d690e51f43fac95b23e`. Emit `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_p90_shock_mr_costed_oos_<UTC>.json` with `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds. **No carryover template text; set `campaign: 241`.**
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 241). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261109T003420Z.json` (453a374c47bdb0a634ec91ecaa86a3cb461e6d2e13d604227eff49f162bdda19). Include prior + all C241 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign241_execution_summary_<UTC>.json` listing **all new C241 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C241`, `next_campaign: C242`, latest registry/OOS sha+path, `oos_edge_proven`, `c242_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C241, with grep cmd/hits/evidence). Update this `HANDOFF.md`.

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_P90|WHITE_DIAG_LINE_LENGTH_P90' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self
# NOW: implement+run C241 -> emit >=4 artifacts with SHAs -> sync state.yaml + HANDOFF
```
