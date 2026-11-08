# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261108T223145Z, C104–C235 LOCKED — edge_claim NONE, C235 DONE, C236 PRESELECTED HEAVY — EXECUTE NEXT, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C235 LOCKED (no reruns). C235 DONE on disk (edge_claim NONE). C236 preselected grep-zero (VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_GINI_SHOCK_MR) — execute C236 next, no status-first.** Latest registry = `reports/strategy_edge_registry_20261108T223145Z.json` (6af5cb617b00...). Latest OOS = C235 `b1ea67400604...` (oos_edge_proven false).

## TIMESTAMPED INITIAL TASK MESSAGE (20261108T223145Z) — HEAVY WORK MANDATORY
**PRIORITY 1: EXECUTE C236.** C235 is complete on disk (VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_RANGE_SHOCK_MR, edge_claim NONE; cross-asset net sums fee0=-2.116147664628981, fee5=-2.826147664628982, fee10=-3.5361476646289822, fee20=-4.956147664628983, fee40=-7.796147664628982 — all cost slices negative, beat_bh_mean_rule false; exposure true; oos_edge_proven false). C235 artifacts emitted with SHA256 from bytes: OOS `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_range_shock_mr_costed_oos_20261108T223131Z.json` (sha b1ea67400604f627f2232cfdf2511d6e06650e4968793f016d7dcbda8f49892b), ingest `reports/real_feed_ingest_attempt_20261108T223145Z.json` (sha eced050cbd2062da12be6544598e1b31512a747f5c5edade855413258c3cb13c), registry `reports/strategy_edge_registry_20261108T223145Z.json` (sha 6af5cb617b005aebb45e13602697cae80793021988ad2c0931d0d04f1e8f9127) superseding 20261108T222102Z (b3fb37ce883d57cc12447443ead96e5f6c5fdc618979bcc65b997bd9a83eef16), script `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_range_shock_mr_costed_oos.py` (sha 3b7e76648fad0c9d0323ca8bc421d2d7c3e218e003feb8728578324995bce592), summary `reports/campaign235_execution_summary_20261108T223145Z.json` (sha f4c4bc7102c10dc8a2d3af27e8738b978f96f503300750eb680ba98ec797c0bd). state.yaml + HANDOFF synced (latest_campaign_done C235, next_campaign C236). **Do not summarize status. Do not stop at status. Implement + run C236 + emit >=4 artifacts with SHA256 from bytes + sync state.yaml + HANDOFF.**

## VERIFIED BASELINE (20261108T223145Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1, `/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python`).
- Caches: `data/cache/volume_1h_full.pkl/meta/provenance` (43658953.../4d321584.../c7ff2f27...), spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` (56075733...).
- **C234 DONE (locked):** VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_CV_SHOCK_MR, oos 3fb432918663..., edge_claim NONE.
- **C235 DONE (verified on disk, SHAs from bytes):**
  - OOS b1ea67400604f627f2232cfdf2511d6e06650e4968793f016d7dcbda8f49892b (`reports/real_quote_volume_rqa_rte_over_white_diag_line_length_range_shock_mr_costed_oos_20261108T223131Z.json`, VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_RANGE_SHOCK_MR, campaign 235, edge_claim NONE, oos_edge_proven false, any_exposure_oos true, all_cost_slices_positive false, beat_bh_mean_rule false).
  - Ingest eced050cbd2062da12be6544598e1b31512a747f5c5edade855413258c3cb13c (`reports/real_feed_ingest_attempt_20261108T223145Z.json`).
  - Registry 6af5cb617b005aebb45e13602697cae80793021988ad2c0931d0d04f1e8f9127 (`reports/strategy_edge_registry_20261108T223145Z.json`) supersedes 20261108T222102Z b3fb37ce883d57cc12447443ead96e5f6c5fdc618979bcc65b997bd9a83eef16.
  - Script 3b7e76648fad0c9d0323ca8bc421d2d7c3e218e003feb8728578324995bce592 (`scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_range_shock_mr_costed_oos.py`, campaign 235, WHITE_DIAG_LINE_LENGTH_RANGE = max-min of qualifying white diagonal segment lengths, >=3 segments, range>0; fail-closed). Distinctness grep 0 non-self at run.
  - Summary f4c4bc7102c10dc8a2d3af27e8738b978f96f503300750eb680ba98ec797c0bd (`reports/campaign235_execution_summary_20261108T223145Z.json`).
- Single durable handoff = this file + `research_state/state.yaml`.

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **C235 completion bottleneck removed.** Script implemented and run (campaign 235, WHITE_DIAG_LINE_LENGTH_RANGE = max-min; fail-closed). Fixed OOS + ingest + registry + summary emitted with SHA256 from bytes; state.yaml/HANDOFF synced.
- **Env bottleneck noted:** reuse `/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python` (deps_ok 2.5.4/1.18.1/3.1.1).
- **No status-first.** Artifacts on disk are the deliverable.
- **No reruns of locked campaigns C104–C235.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Collision handling is fail-closed:** if a preselected candidate collides on grep, reject it, pick a distinct grep-zero fallback, record primary/fallback grep cmd/hits/evidence in all artifacts + state + HANDOFF.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence.
- **Heavy work mandatory.** No status-only replies. No stop between campaigns.

## C236 — NEXT FOCUS CAMPAIGN (PRESELECTED, GREP-ZERO VERIFIED 20261108T223145Z)
**Primary candidate:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_GINI_SHOCK_MR` — RQA ratio RTE / WHITE_DIAG_LINE_LENGTH_GINI on delay-embedded log-volume returns (RTE = recurrence time entropy of white vertical gap distribution, w>=w_min, LOI/self excluded; WHITE_DIAG_LINE_LENGTH_GINI = Gini coefficient of lengths of qualifying WHITE diagonal segments (consecutive 0-cells/non-recurrent, length>=w_min=2) pooled over off-diagonal diagonals k!=0 with >=1 qualifying segment; fail-closed if <3 qualifying segments or mean<=0 or Gini<=0/non-finite). Distinct from WHITE_DIAG_LINE_LENGTH_RANGE(C235), WHITE_DIAG_LINE_LENGTH_CV(C234), WHITE_DIAG_LINE_LENGTH_IQR(C233), WHITE_DIAG_LINE_LENGTH_MAD(C232), WHITE_DIAG_LINE_LENGTH_KURTOSIS(C231), WHITE_DIAG_LINE_LENGTH_SKEWNESS(C230), WHITE_DIAG_LINE_COUNT_VARIANCE(C229), DIAG_LINE_COUNT_VARIANCE(C228), WHITE_DIAG_LINE_LENGTH_DIVERGENCE(C227), WHITE_DIAG_LINE_LENGTH_VARIANCE(C226), and prior C125-C235 families.
**grep evidence (20261108T223145Z):** `grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_GINI|WHITE_DIAG_LINE_LENGTH_GINI' scripts/ strategies/ backtest/ utils/ 2>&1` → 0 hits.
**Fallbacks (grep-zero verified 20261108T223145Z):** `RTE_OVER_WHITE_DIAG_LINE_LENGTH_ENTROPY` (0), `RTE_OVER_WHITE_DIAG_LINE_LENGTH_RMS` (0), `RTE_OVER_WHITE_DIAG_LINE_LENGTH_GEOMEAN` (0), `DET_OVER_WHITE_DIAG_LINE_LENGTH_RANGE` (0). At C236 start grep-verify; if collision, pick a distinct grep-zero fallback not used C125–C235 and record evidence.

### COLLISION GUARD (RUN AT START)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_GINI|WHITE_DIAG_LINE_LENGTH_GINI' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self
```
If collision found: pick a distinct grep-zero fallback not used C125–C235 (verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + state + HANDOFF.

### REQUIRED C236 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_gini_shock_mr_costed_oos.py` (or collision-safe). Model on C188–C235. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T223145Z.json` (6af5cb617b005aebb45e13602697cae80793021988ad2c0931d0d04f1e8f9127), cite C235 OOS SHA `b1ea67400604f627f2232cfdf2511d6e06650e4968793f016d7dcbda8f49892b` and C234 OOS SHA `3fb43291866383c8a7b710ac531f4ca8ed82aea08a5d88e1052f5693c1e39ff9`. Emit `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_gini_shock_mr_costed_oos_<UTC>.json` with `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds. **No carryover template text; set `campaign: 236`.**
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 236). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T223145Z.json` (6af5cb617b005aebb45e13602697cae80793021988ad2c0931d0d04f1e8f9127). Include prior + all C236 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign236_execution_summary_<UTC>.json` listing **all new C236 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C236`, `next_campaign: C237`, latest registry/OOS sha+path, `oos_edge_proven`, `c237_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C236, with grep cmd/hits/evidence). Update this `HANDOFF.md`.

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_GINI|WHITE_DIAG_LINE_LENGTH_GINI' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self
# NOW: implement+run C236 -> emit >=4 artifacts with SHAs -> sync state.yaml + HANDOFF
```
