# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261109T000329Z, C104–C237 LOCKED — edge_claim NONE, C237 DONE, C238 PRESELECTED HEAVY — EXECUTE NEXT, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C237 LOCKED (no reruns). C237 DONE on disk (edge_claim NONE). C238 preselected grep-zero (VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_RMS_SHOCK_MR) — execute C238 next, no status-first.** Latest registry = `reports/strategy_edge_registry_20261109T000025Z.json` (e135272fd9a0251e50f252d58c3643216c6c8ec4347be41afa459fbdfac2f95c). Latest OOS = C237 `ca975ead97434b958a2c7dc7e03a1b472aeaceadcf0b99abea6213ab0e6d4ce5` (oos_edge_proven false).

## TIMESTAMPED INITIAL TASK MESSAGE (20261109T000329Z) — HEAVY WORK MANDATORY
**PRIORITY 1: EXECUTE C238.** C237 is complete on disk (VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_ENTROPY_SHOCK_MR, edge_claim NONE; cross-asset net sums fee0=+0.556657, fee5=-0.225343, fee10=-1.007343, fee20=-2.571343, fee40=-5.699343 — not all cost slices positive, beat_bh_mean_rule true; exposure true; oos_edge_proven false). C238 script does NOT yet exist on disk (collision guard 0 verified). **Do not summarize status. Do not stop at status. Implement + run C238 + emit >=4 artifacts with SHA256 from bytes + sync state.yaml + HANDOFF.**

## VERIFIED BASELINE (20261109T000329Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1, `/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python`).
- Caches: `data/cache/volume_1h_full.pkl/meta/provenance` (43658953.../4d321584.../c7ff2f27...), spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` (56075733...).
- **C234 DONE (locked):** VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_CV_SHOCK_MR, oos 3fb432918663..., edge_claim NONE.
- **C235 DONE (locked):** VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_RANGE_SHOCK_MR, oos b1ea67400604f..., edge_claim NONE.
- **C236 DONE (locked):** VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_GINI_SHOCK_MR, oos 81d9a4ae5708ce29cd2e5dcde1c163fa1e87379f3aa766dd65a344378f22d0ff, edge_claim NONE.
- **C237 DONE (verified on disk, SHAs from bytes):**
  - OOS ca975ead97434b958a2c7dc7e03a1b472aeaceadcf0b99abea6213ab0e6d4ce5 (`reports/real_quote_volume_rqa_rte_over_white_diag_line_length_entropy_shock_mr_costed_oos_20261108T235238Z.json`, VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_ENTROPY_SHOCK_MR, campaign 237, edge_claim NONE, oos_edge_proven false, any_exposure_oos true, all_cost_slices_positive false, beat_bh_mean_rule true).
  - Ingest 18e204bd4f2bc3feb11fef43f8227341f2014f461bf8a935c5b556065f7071f2 (`reports/real_feed_ingest_attempt_20261109T000025Z.json`).
  - Registry e135272fd9a0251e50f252d58c3643216c6c8ec4347be41afa459fbdfac2f95c (`reports/strategy_edge_registry_20261109T000025Z.json`) supersedes 20261108T233928Z 86c477648ec8565fdabd90faefdb647f1a3517bd32da35c25d5fe8e78b88e11c.
  - Script 1ff0e463478b2c656c1744e4abbe6b72959dbad029e0cdd05569985eeb27fa01 (`scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_entropy_shock_mr_costed_oos.py`, campaign 237, WHITE_DIAG_LINE_LENGTH_ENTROPY = Shannon entropy (nats) of qualifying white diagonal segment lengths, >=3 segments, >=2 distinct lengths, entropy>0; fail-closed). Distinctness grep 0 non-self at run.
  - Summary 0ca4c27018bd07c2202e24b975b7c637fafac438eacb94ccfce8817970872b4f (`reports/campaign237_execution_summary_20261109T000025Z.json`).
- Single durable handoff = this file + `research_state/state.yaml`.

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **Env bottleneck cleared.** Reuse `/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python` (deps_ok verified 20261109T000329Z). C237 run is CPU-heavy (~8-12 min); run in background/with patience if needed, but **must complete C238 in this session** — no status-only replies.
- **Collision guard cleared (0 hits).** `grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_RMS|WHITE_DIAG_LINE_LENGTH_RMS' scripts/ strategies/ backtest/ utils/ 2>&1` → 0 non-self. C238 primary candidate is clean.
- **No status-first.** Artifacts on disk are the deliverable.
- **No reruns of locked campaigns C104–C237.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Collision handling is fail-closed:** if a preselected candidate collides on grep, reject it, pick a distinct grep-zero fallback, record primary/fallback grep cmd/hits/evidence in all artifacts + state + HANDOFF.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence.
- **Heavy work mandatory.** No status-only replies. No stop between campaigns.

## C238 — NEXT FOCUS CAMPAIGN (PRESELECTED, GREP-ZERO VERIFIED 20261109T000329Z)
**Primary candidate:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_RMS_SHOCK_MR` — RQA ratio RTE / WHITE_DIAG_LINE_LENGTH_RMS on delay-embedded log-volume returns (RTE = recurrence time entropy of white vertical gap distribution, w>=w_min, LOI/self excluded; WHITE_DIAG_LINE_LENGTH_RMS = root-mean-square of lengths of qualifying WHITE diagonal segments (consecutive 0-cells/non-recurrent, length>=w_min=2) pooled over off-diagonal diagonals k!=0 with >=1 qualifying segment; fail-closed if <3 qualifying segments or RMS non-finite/non-positive). Distinct from ENTROPY(C237), GINI(C236), RANGE(C235), CV(C234), IQR(C233), MAD(C232), KURTOSIS(C231), SKEWNESS(C230), COUNT_VARIANCE(C229), DIAG_COUNT_VARIANCE(C228), DIVERGENCE(C227), VARIANCE(C226), and prior C125-C237 families.
**grep evidence (20261109T000329Z):** `grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_RMS|WHITE_DIAG_LINE_LENGTH_RMS' scripts/ strategies/ backtest/ utils/ 2>&1` → 0 hits.
**Fallbacks (grep-zero verified 20261109T000329Z):** `RTE_OVER_WHITE_DIAG_LINE_LENGTH_GEOMEAN` (0), `RTE_OVER_WHITE_DIAG_LINE_LENGTH_HARMONIC_MEAN` (0), `DET_OVER_WHITE_DIAG_LINE_LENGTH_RANGE` (0), `RTE_OVER_WHITE_DIAG_LINE_LENGTH_P90` (0). At C238 start grep-verify; if collision, pick a distinct grep-zero fallback not used C125–C237 and record evidence.

### COLLISION GUARD (RUN AT START)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_RMS|WHITE_DIAG_LINE_LENGTH_RMS' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self
```
If collision found: pick a distinct grep-zero fallback not used C125–C237 (verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + state + HANDOFF.

### REQUIRED C238 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_rms_shock_mr_costed_oos.py` (or collision-safe). Model on C188–C237. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261109T000025Z.json` (e135272fd9a0251e50f252d58c3643216c6c8ec4347be41afa459fbdfac2f95c), cite C237 OOS SHA `ca975ead97434b958a2c7dc7e03a1b472aeaceadcf0b99abea6213ab0e6d4ce5`, C236 OOS SHA `81d9a4ae5708ce29cd2e5dcde1c163fa1e87379f3aa766dd65a344378f22d0ff`, and C235 OOS SHA `b1ea67400604f627f2232cfdf2511d6e06650e4968793f016d7dcbda8f49892b`. Emit `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_rms_shock_mr_costed_oos_<UTC>.json` with `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds. **No carryover template text; set `campaign: 238`.**
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 238). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261109T000025Z.json` (e135272fd9a0251e50f252d58c3643216c6c8ec4347be41afa459fbdfac2f95c). Include prior + all C238 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign238_execution_summary_<UTC>.json` listing **all new C238 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C238`, `next_campaign: C239`, latest registry/OOS sha+path, `oos_edge_proven`, `c239_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C238, with grep cmd/hits/evidence). Update this `HANDOFF.md`.

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_RMS|WHITE_DIAG_LINE_LENGTH_RMS' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self
# NOW: implement+run C238 -> emit >=4 artifacts with SHAs -> sync state.yaml + HANDOFF
```
