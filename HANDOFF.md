# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261108T222452Z, C104–C234 LOCKED — edge_claim NONE, C234 DONE, C235 PRESELECTED HEAVY — EXECUTE NEXT, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C234 LOCKED (no reruns). C234 DONE on disk (edge_claim NONE). C235 preselected grep-zero (VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_RANGE_SHOCK_MR) — execute C235 next, no status-first.** Latest registry = `reports/strategy_edge_registry_20261108T222102Z.json` (b3fb37ce883d...). Latest OOS = C234 `3fb432918663...` (oos_edge_proven false).

## TIMESTAMPED INITIAL TASK MESSAGE (20261108T222452Z) — HEAVY WORK MANDATORY
**PRIORITY 1: EXECUTE C235.** C234 is complete on disk (VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_CV_SHOCK_MR, edge_claim NONE; cross-asset net sums fee0=+0.5621939679802503, fee5=-0.32780603201975045, fee10=-1.217806032019751, fee20=-2.997806032019751, fee40=-6.55780603201975 — fails all-cost-positive rule though beat_bh_mean_rule true; oos_edge_proven false). C234 artifacts emitted with SHA256 from bytes: OOS `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_cv_shock_mr_costed_oos_20261108T221325Z.json` (sha 3fb43291866383c8a7b710ac531f4ca8ed82aea08a5d88e1052f5693c1e39ff9), ingest `reports/real_feed_ingest_attempt_20261108T222102Z.json` (sha e50cbcaf70594bf7faa295259a9f6af58b4bdddb40e97b960ce31c628cc08561), registry `reports/strategy_edge_registry_20261108T222102Z.json` (sha b3fb37ce883d57cc12447443ead96e5f6c5fdc618979bcc65b997bd9a83eef16) superseding 20261108T220650Z (8c493deb7c96e9dc3acee1cbf7c18791677c49f1e15ea482fec8fd050e3b22f6), script `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_cv_shock_mr_costed_oos.py` (sha cd8c82ca495c468a6cf0b1261c329911fe08fb6cdc7f0e2683c2061e62e7c6db), summary `reports/campaign234_execution_summary_20261108T222102Z.json` (sha 656db6801b4e5f29ffdb16983fdef7e47c59fe0f76899e10693bbe20a19ae108). state.yaml + HANDOFF synced (latest_campaign_done C234, next_campaign C235). **Do not summarize status. Do not stop at status. Implement + run C235 + emit >=4 artifacts with SHA256 from bytes + sync state.yaml + HANDOFF.**

## VERIFIED BASELINE (20261108T222452Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1, `/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python`).
- Caches: `data/cache/volume_1h_full.pkl/meta/provenance` (43658953.../4d321584.../c7ff2f27...), spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` (56075733...).
- **C232 DONE (locked):** VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_MEDIAN_ABS_DEV_SHOCK_MR, oos 7b9bd417..., edge_claim NONE.
- **C233 DONE (locked):** VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_IQR_SHOCK_MR, oos d4322c91..., edge_claim NONE.
- **C234 DONE (verified on disk, SHAs from bytes):**
  - OOS 3fb43291866383c8a7b710ac531f4ca8ed82aea08a5d88e1052f5693c1e39ff9 (`reports/real_quote_volume_rqa_rte_over_white_diag_line_length_cv_shock_mr_costed_oos_20261108T221325Z.json`, VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_CV_SHOCK_MR, campaign 234, edge_claim NONE, oos_edge_proven false, any_exposure_oos true, all_cost_slices_positive false, beat_bh_mean_rule true).
  - Ingest e50cbcaf70594bf7faa295259a9f6af58b4bdddb40e97b960ce31c628cc08561 (`reports/real_feed_ingest_attempt_20261108T222102Z.json`).
  - Registry b3fb37ce883d57cc12447443ead96e5f6c5fdc618979bcc65b997bd9a83eef16 (`reports/strategy_edge_registry_20261108T222102Z.json`) supersedes 20261108T220650Z 8c493deb7c96e9dc3acee1cbf7c18791677c49f1e15ea482fec8fd050e3b22f6.
  - Script cd8c82ca495c468a6cf0b1261c329911fe08fb6cdc7f0e2683c2061e62e7c6db (`scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_cv_shock_mr_costed_oos.py`, campaign 234, WHITE_DIAG_LINE_LENGTH_CV = std(ddof=1)/mean of qualifying white diagonal segment lengths, >=3 segments, mean>0,std>0,CV>0; fail-closed).
  - Summary 656db6801b4e5f29ffdb16983fdef7e47c59fe0f76899e10693bbe20a19ae108 (`reports/campaign234_execution_summary_20261108T222102Z.json`).
  - Distinctness grep 0 non-self at selection/run (post-run grep hits only C234 script self). C234 no longer blocks C235.
- Single durable handoff = this file + `research_state/state.yaml`.

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **C234 completion bottleneck removed.** Script implemented and run (campaign 234, WHITE_DIAG_LINE_LENGTH_CV = std(ddof=1)/mean; fail-closed). Fixed OOS + ingest + registry + summary emitted with SHA256 from bytes; state.yaml/HANDOFF synced.
- **Env bottleneck noted:** reuse `/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python` (deps_ok 2.5.4/1.18.1/3.1.1).
- **No status-first.** Artifacts on disk are the deliverable.
- **No reruns of locked campaigns C104–C234.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Collision handling is fail-closed:** if a preselected candidate collides on grep, reject it, pick a distinct grep-zero fallback, record primary/fallback grep cmd/hits/evidence in all artifacts + state + HANDOFF.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence.
- **Heavy work mandatory.** No status-only replies. No stop between campaigns.

## C235 — NEXT FOCUS CAMPAIGN (PRESELECTED, GREP-ZERO VERIFIED 20261108T222452Z)
**Primary candidate:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_RANGE_SHOCK_MR` — RQA ratio RTE / WHITE_DIAG_LINE_LENGTH_RANGE on delay-embedded log-volume returns (RTE = recurrence time entropy of white vertical gap distribution, w>=w_min, LOI/self excluded; WHITE_DIAG_LINE_LENGTH_RANGE = max-min of lengths of qualifying WHITE diagonal segments (consecutive 0-cells/non-recurrent, length>=w_min=2) pooled over off-diagonal diagonals k!=0 with >=1 qualifying segment; fail-closed if <3 qualifying segments or range<=0/non-finite). Distinct from WHITE_DIAG_LINE_LENGTH_CV(C234), WHITE_DIAG_LINE_LENGTH_IQR(C233), WHITE_DIAG_LINE_LENGTH_MAD(C232), WHITE_DIAG_LINE_LENGTH_KURTOSIS(C231), WHITE_DIAG_LINE_LENGTH_SKEWNESS(C230), WHITE_DIAG_LINE_COUNT_VARIANCE(C229), DIAG_LINE_COUNT_VARIANCE(C228), WHITE_DIAG_LINE_LENGTH_DIVERGENCE(C227), WHITE_DIAG_LINE_LENGTH_VARIANCE(C226), and prior C125-C234 families.
**grep evidence (20261108T222452Z):** `grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_RANGE|WHITE_DIAG_LINE_LENGTH_RANGE' scripts/ strategies/ backtest/ utils/ 2>&1` → 0 hits.
**Fallback:** at C235 start grep-verify; if collision, pick a distinct grep-zero RQA-ratio candidate not used C125–C234 and record evidence.

### COLLISION GUARD (RUN AT START)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_RANGE|WHITE_DIAG_LINE_LENGTH_RANGE' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self
```
If collision found: pick a distinct grep-zero fallback not used C125–C234 (verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + state + HANDOFF.

### REQUIRED C235 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_range_shock_mr_costed_oos.py` (or collision-safe). Model on C188–C234. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T222102Z.json` (b3fb37ce883d57cc12447443ead96e5f6c5fdc618979bcc65b997bd9a83eef16), cite C234 OOS SHA `3fb43291866383c8a7b710ac531f4ca8ed82aea08a5d88e1052f5693c1e39ff9` and C233 OOS SHA `d4322c91bb23f8a8f274d404c6e59fb4730db7d06857f0bada5de50778aa639e`. Emit `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_range_shock_mr_costed_oos_<UTC>.json` with `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds. **No carryover template text; set `campaign: 235`.**
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 235). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T222102Z.json` (b3fb37ce883d57cc12447443ead96e5f6c5fdc618979bcc65b997bd9a83eef16). Include prior + all C235 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign235_execution_summary_<UTC>.json` listing **all new C235 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C235`, `next_campaign: C236`, latest registry/OOS sha+path, `oos_edge_proven`, `c236_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C235, with grep cmd/hits/evidence). Update this `HANDOFF.md`.

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_RANGE|WHITE_DIAG_LINE_LENGTH_RANGE' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self
# NOW: implement+run C235 -> emit >=4 artifacts with SHAs -> sync state.yaml + HANDOFF
```