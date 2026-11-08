# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261108T220650Z, C104–C233 LOCKED — edge_claim NONE, C233 DONE, C234 PRESELECTED HEAVY — EXECUTE NEXT, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C233 LOCKED (no reruns). C233 DONE on disk (edge_claim NONE). C234 preselected grep-zero (VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_CV_SHOCK_MR) — execute C234 next, no status-first.** Latest registry = `reports/strategy_edge_registry_20261108T220650Z.json` (8c493deb7c96...). Latest OOS = C233 `d4322c91bb23...` (oos_edge_proven false).

## TIMESTAMPED INITIAL TASK MESSAGE (20261108T220650Z) — HEAVY WORK MANDATORY
**PRIORITY 1: EXECUTE C234.** C233 is complete on disk (VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_IQR_SHOCK_MR, edge_claim NONE; cross-asset net sums fee0=-1.859703456753104, fee5=-3.003703456753105, fee10=-4.1477034567531055, fee20=-6.435703456753105, fee40=-11.011703456753104 — fails all-cost-positive / B&H mean rule). C233 artifacts emitted with SHA256 from bytes: OOS `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_iqr_shock_mr_costed_oos_20261108T215934Z.json` (sha d4322c91bb23f8a8f274d404c6e59fb4730db7d06857f0bada5de50778aa639e), ingest `reports/real_feed_ingest_attempt_20261108T220650Z.json` (sha a7812c0918209236c2434f63090ad09567929cf3d3b4249d83b1167aa88485d5), registry `reports/strategy_edge_registry_20261108T220650Z.json` (sha 8c493deb7c96e9dc3acee1cbf7c18791677c49f1e15ea482fec8fd050e3b22f6) superseding 20261108T213825Z (38776820...), script `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_iqr_shock_mr_costed_oos.py` (sha 891485e841d4bd073728e42d0058a38d28ee70056c4313e951f2c1f5177f0e99), summary `reports/campaign233_execution_summary_20261108T220650Z.json` (sha edf86c24831d7dd403284acb4c95fc15af0815154b3a5440d3b3f80f0bc761bd). state.yaml + HANDOFF synced (latest_campaign_done C233, next_campaign C234). **Do not summarize status. Do not stop at status. Implement + run C234 + emit >=4 artifacts with SHA256 from bytes + sync state.yaml + HANDOFF.**

## VERIFIED BASELINE (20261108T220650Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1, via runner venv for execution).
- Caches: `data/cache/volume_1h_full.pkl/meta/provenance` (43658953.../4d321584.../c7ff2f27...), spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` (56075733...).
- **C231 DONE (locked):** VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_KURTOSIS_SHOCK_MR, oos 9a4fb5c0..., edge_claim NONE.
- **C232 DONE (locked):** VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_MEDIAN_ABS_DEV_SHOCK_MR, oos 7b9bd417..., edge_claim NONE.
- **C233 DONE (verified on disk, SHAs from bytes):**
  - OOS d4322c91bb23f8a8f274d404c6e59fb4730db7d06857f0bada5de50778aa639e (`reports/real_quote_volume_rqa_rte_over_white_diag_line_length_iqr_shock_mr_costed_oos_20261108T215934Z.json`, VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_IQR_SHOCK_MR, campaign 233, edge_claim NONE, oos_edge_proven false, any_exposure_oos true).
  - Ingest a7812c0918209236c2434f63090ad09567929cf3d3b4249d83b1167aa88485d5 (`reports/real_feed_ingest_attempt_20261108T220650Z.json`).
  - Registry 8c493deb7c96e9dc3acee1cbf7c18791677c49f1e15ea482fec8fd050e3b22f6 (`reports/strategy_edge_registry_20261108T220650Z.json`) supersedes 20261108T213825Z 3877682020aced181d3411860e2cbce53ea64e3fab8a8bfb7e22c0f3fb273e54.
  - Script 891485e841d4bd073728e42d0058a38d28ee70056c4313e951f2c1f5177f0e99 (`scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_iqr_shock_mr_costed_oos.py`, campaign 233, WHITE_DIAG_LINE_LENGTH_IQR = Q3-Q1 (numpy percentile linear, 75th-25th, scale=1), >=3 segments, fail-closed).
  - Summary edf86c24831d7dd403284acb4c95fc15af0815154b3a5440d3b3f80f0bc761bd (`reports/campaign233_execution_summary_20261108T220650Z.json`).
  - Distinctness grep 0 non-self at run (RTE_OVER_WHITE_DIAG_LINE_LENGTH_IQR/WHITE_DIAG_LINE_LENGTH_IQR).
- Single durable handoff = this file + `research_state/state.yaml`.

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **C233 completion bottleneck removed.** Script implemented and run (campaign 233, WHITE_DIAG_LINE_LENGTH_IQR = interquartile range Q3-Q1 (scale=1); fail-closed if <3 qualifying segments or IQR<=0/non-finite). Fixed OOS + ingest + registry + summary emitted with SHA256 from bytes; state.yaml/HANDOFF synced. C233 no longer blocks C234.
- **Env bottleneck noted:** system python lacked numpy/scipy/pandas; execution used `/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python` (deps_ok 2.5.4/1.18.1/3.1.1). Reuse or recreate venv for C234.
- **No status-first.** Artifacts on disk are the deliverable.
- **No reruns of locked campaigns C104–C233.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Collision handling is fail-closed:** if a preselected candidate collides on grep, reject it, pick a distinct grep-zero fallback, record primary/fallback grep cmd/hits/evidence in all artifacts + state + HANDOFF.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence.
- **Heavy work mandatory.** No status-only replies. No stop between campaigns.

## C234 — NEXT FOCUS CAMPAIGN (PRESELECTED, GREP-ZERO VERIFIED 20261108T220650Z)
**Primary candidate:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_CV_SHOCK_MR` — RQA ratio RTE / WHITE_DIAG_LINE_LENGTH_CV on delay-embedded log-volume returns (RTE = recurrence time entropy of white vertical gap distribution, w>=w_min, LOI/self excluded; WHITE_DIAG_LINE_LENGTH_CV = coefficient of variation = std(ddof=1)/mean of lengths of qualifying WHITE diagonal segments (consecutive 0-cells/non-recurrent, length>=w_min=2) pooled over off-diagonal diagonals k!=0 with >=1 qualifying segment; fail-closed if <3 qualifying segments or mean<=0 or std<=0 or CV<=0/non-finite). Distinct from WHITE_DIAG_LINE_LENGTH_IQR(C233), WHITE_DIAG_LINE_LENGTH_MAD(C232), WHITE_DIAG_LINE_LENGTH_KURTOSIS(C231), WHITE_DIAG_LINE_LENGTH_SKEWNESS(C230), WHITE_DIAG_LINE_COUNT_VARIANCE(C229), DIAG_LINE_COUNT_VARIANCE(C228), WHITE_DIAG_LINE_LENGTH_DIVERGENCE(C227), WHITE_DIAG_LINE_LENGTH_VARIANCE(C226), and prior C125-C233 families.
**grep evidence (20261108T220650Z):** `grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_CV|rte_over_white_diag_line_length_cv|WHITE_DIAG_LINE_LENGTH_CV|white_diag_line_length_cv' scripts/ strategies/ backtest/ utils/ 2>&1` → 0 hits.
**Fallback:** at C234 start grep-verify; if collision, pick a distinct grep-zero RQA-ratio candidate not used C125–C233 and record evidence.

### COLLISION GUARD (RUN AT START)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_CV|rte_over_white_diag_line_length_cv|WHITE_DIAG_LINE_LENGTH_CV|white_diag_line_length_cv' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self
```
If collision found: pick a distinct grep-zero fallback not used C125–C233 (verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + state + HANDOFF.

### REQUIRED C234 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_cv_shock_mr_costed_oos.py` (or collision-safe). Model on C188–C233. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T220650Z.json` (8c493deb7c96e9dc3acee1cbf7c18791677c49f1e15ea482fec8fd050e3b22f6), cite C233 OOS SHA `d4322c91bb23f8a8f274d404c6e59fb4730db7d06857f0bada5de50778aa639e` and C232 OOS SHA `7b9bd417b0ba4b9820f9bf30d61e5f4b017f005ac3304e40208115a3edaf2fc1`. Emit `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_cv_shock_mr_costed_oos_<UTC>.json` with `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds. **No carryover template text; set `campaign: 234`.**
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 234). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T220650Z.json` (8c493deb7c96e9dc3acee1cbf7c18791677c49f1e15ea482fec8fd050e3b22f6). Include prior + all C234 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign234_execution_summary_<UTC>.json` listing **all new C234 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C234`, `next_campaign: C235`, latest registry/OOS sha+path, `oos_edge_proven`, `c235_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C234, with grep cmd/hits/evidence). Update this `HANDOFF.md`.

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_CV|rte_over_white_diag_line_length_cv|WHITE_DIAG_LINE_LENGTH_CV|white_diag_line_length_cv' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self
# NOW: implement+run C234 -> emit >=4 artifacts with SHAs -> sync state.yaml + HANDOFF
```
