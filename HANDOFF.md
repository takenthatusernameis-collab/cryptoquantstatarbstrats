# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261108T233937Z, C104–C236 LOCKED — edge_claim NONE, C236 DONE, C237 PRESELECTED HEAVY — EXECUTE NEXT, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C236 LOCKED (no reruns). C236 DONE on disk (edge_claim NONE). C237 preselected grep-zero (VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_ENTROPY_SHOCK_MR) — execute C237 next, no status-first.** Latest registry = `reports/strategy_edge_registry_20261108T233928Z.json` (86c477648ec8565fdabd90faefdb647f1a3517bd32da35c25d5fe8e78b88e11c). Latest OOS = C236 `81d9a4ae5708ce29cd2e5dcde1c163fa1e87379f3aa766dd65a344378f22d0ff` (oos_edge_proven false).

## TIMESTAMPED INITIAL TASK MESSAGE (20261108T233937Z) — HEAVY WORK MANDATORY
**PRIORITY 1: EXECUTE C237.** C236 is complete on disk (VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_GINI_SHOCK_MR, edge_claim NONE; cross-asset net sums fee0=+0.978683, fee5=+0.022683, fee10=-0.933317, fee20=-2.845317, fee40=-6.669317 — not all cost slices positive, beat_bh_mean_rule true; exposure true; oos_edge_proven false). C236 artifacts emitted with SHA256 from bytes: OOS `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_gini_shock_mr_costed_oos_20261108T232527Z.json` (sha 81d9a4ae5708ce29cd2e5dcde1c163fa1e87379f3aa766dd65a344378f22d0ff), ingest `reports/real_feed_ingest_attempt_20261108T233900Z.json` (sha 4ac43bd46cab20e389b8091b3cdbb6fe4a6a9ec148bdd1e6a1610509a1eb9cc6), registry `reports/strategy_edge_registry_20261108T233928Z.json` (sha 86c477648ec8565fdabd90faefdb647f1a3517bd32da35c25d5fe8e78b88e11c) superseding 20261108T223145Z (6af5cb617b005aebb45e13602697cae80793021988ad2c0931d0d04f1e8f9127), script `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_gini_shock_mr_costed_oos.py` (sha 07f2a3ec85319802df7a93a347c09bc5d481dffcd69a63b20058cc63d7861e85), summary `reports/campaign236_execution_summary_20261108T233937Z.json` (sha 6d3d3aa60454b3b2604b38752b9cba3361f2a7d3b795a6c3c1e1abd42072e061). state.yaml + HANDOFF synced (latest_campaign_done C236, next_campaign C237). **Do not summarize status. Do not stop at status. Implement + run C237 + emit >=4 artifacts with SHA256 from bytes + sync state.yaml + HANDOFF.**

## VERIFIED BASELINE (20261108T233937Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1, `/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python`).
- Caches: `data/cache/volume_1h_full.pkl/meta/provenance` (43658953.../4d321584.../c7ff2f27...), spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` (56075733...).
- **C234 DONE (locked):** VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_CV_SHOCK_MR, oos 3fb432918663..., edge_claim NONE.
- **C235 DONE (verified on disk, SHAs from bytes):**
  - OOS b1ea67400604f627f2232cfdf2511d6e06650e4968793f016d7dcbda8f49892b (`reports/real_quote_volume_rqa_rte_over_white_diag_line_length_range_shock_mr_costed_oos_20261108T223131Z.json`, VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_RANGE_SHOCK_MR, campaign 235, edge_claim NONE, oos_edge_proven false, any_exposure_oos true, all_cost_slices_positive false, beat_bh_mean_rule false).
  - Ingest eced050cbd2062da12be6544598e1b31512a747f5c5edade855413258c3cb13c (`reports/real_feed_ingest_attempt_20261108T223145Z.json`).
  - Registry 6af5cb617b005aebb45e13602697cae80793021988ad2c0931d0d04f1e8f9127 (`reports/strategy_edge_registry_20261108T223145Z.json`) supersedes 20261108T222102Z b3fb37ce883d57cc12447443ead96e5f6c5fdc618979bcc65b997bd9a83eef16.
  - Script 3b7e76648fad0c9d0323ca8bc421d2d7c3e218e003feb8728578324995bce592 (`scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_range_shock_mr_costed_oos.py`, campaign 235, WHITE_DIAG_LINE_LENGTH_RANGE = max-min of qualifying white diagonal segment lengths, >=3 segments, range>0; fail-closed). Distinctness grep 0 non-self at run.
  - Summary f4c4bc7102c10dc8a2d3af27e8738b978f96f503300750eb680ba98ec797c0bd (`reports/campaign235_execution_summary_20261108T223145Z.json`).
- **C236 DONE (verified on disk, SHAs from bytes):**
  - OOS 81d9a4ae5708ce29cd2e5dcde1c163fa1e87379f3aa766dd65a344378f22d0ff (`reports/real_quote_volume_rqa_rte_over_white_diag_line_length_gini_shock_mr_costed_oos_20261108T232527Z.json`, VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_GINI_SHOCK_MR, campaign 236, edge_claim NONE, oos_edge_proven false, any_exposure_oos true, all_cost_slices_positive false, beat_bh_mean_rule true).
  - Ingest 4ac43bd46cab20e389b8091b3cdbb6fe4a6a9ec148bdd1e6a1610509a1eb9cc6 (`reports/real_feed_ingest_attempt_20261108T233900Z.json`).
  - Registry 86c477648ec8565fdabd90faefdb647f1a3517bd32da35c25d5fe8e78b88e11c (`reports/strategy_edge_registry_20261108T233928Z.json`) supersedes 20261108T223145Z 6af5cb617b005aebb45e13602697cae80793021988ad2c0931d0d04f1e8f9127.
  - Script 07f2a3ec85319802df7a93a347c09bc5d481dffcd69a63b20058cc63d7861e85 (`scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_gini_shock_mr_costed_oos.py`, campaign 236, WHITE_DIAG_LINE_LENGTH_GINI = Gini coefficient of qualifying white diagonal segment lengths, >=3 segments, mean>0, Gini>0; fail-closed). Distinctness grep 0 non-self at run.
  - Summary 6d3d3aa60454b3b2604b38752b9cba3361f2a7d3b795a6c3c1e1abd42072e061 (`reports/campaign236_execution_summary_20261108T233937Z.json`).
- Single durable handoff = this file + `research_state/state.yaml`.

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **C236 completion bottleneck removed.** Script implemented and run (campaign 236, WHITE_DIAG_LINE_LENGTH_GINI = Gini coefficient; fail-closed). Fixed OOS + ingest + registry + summary emitted with SHA256 from bytes; state.yaml/HANDOFF synced.
- **Env bottleneck noted:** reuse `/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python` (deps_ok 2.5.4/1.18.1/3.1.1).
- **No status-first.** Artifacts on disk are the deliverable.
- **No reruns of locked campaigns C104–C236.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Collision handling is fail-closed:** if a preselected candidate collides on grep, reject it, pick a distinct grep-zero fallback, record primary/fallback grep cmd/hits/evidence in all artifacts + state + HANDOFF.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence.
- **Heavy work mandatory.** No status-only replies. No stop between campaigns.

## C237 — NEXT FOCUS CAMPAIGN (PRESELECTED, GREP-ZERO VERIFIED 20261108T233937Z)
**Primary candidate:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_ENTROPY_SHOCK_MR` — RQA ratio RTE / WHITE_DIAG_LINE_LENGTH_ENTROPY on delay-embedded log-volume returns (RTE = recurrence time entropy of white vertical gap distribution, w>=w_min, LOI/self excluded; WHITE_DIAG_LINE_LENGTH_ENTROPY = Shannon entropy (nats) of lengths of qualifying WHITE diagonal segments (consecutive 0-cells/non-recurrent, length>=w_min=2) pooled over off-diagonal diagonals k!=0 with >=1 qualifying segment; fail-closed if <3 qualifying segments or entropy non-finite/non-positive). Distinct from GINI(C236), RANGE(C235), CV(C234), IQR(C233), MAD(C232), KURTOSIS(C231), SKEWNESS(C230), COUNT_VARIANCE(C229), DIAG_COUNT_VARIANCE(C228), DIVERGENCE(C227), VARIANCE(C226), and prior C125-C236 families.
**grep evidence (20261108T233937Z):** `grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_ENTROPY|WHITE_DIAG_LINE_LENGTH_ENTROPY' scripts/ strategies/ backtest/ utils/ 2>&1` → 0 hits.
**Fallbacks (grep-zero verified 20261108T233937Z):** `RTE_OVER_WHITE_DIAG_LINE_LENGTH_RMS` (0), `RTE_OVER_WHITE_DIAG_LINE_LENGTH_GEOMEAN` (0), `DET_OVER_WHITE_DIAG_LINE_LENGTH_RANGE` (0). At C237 start grep-verify; if collision, pick a distinct grep-zero fallback not used C125–C236 and record evidence.

### COLLISION GUARD (RUN AT START)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_ENTROPY|WHITE_DIAG_LINE_LENGTH_ENTROPY' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self
```
If collision found: pick a distinct grep-zero fallback not used C125–C236 (verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + state + HANDOFF.

### REQUIRED C237 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_entropy_shock_mr_costed_oos.py` (or collision-safe). Model on C188–C236. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T233928Z.json` (86c477648ec8565fdabd90faefdb647f1a3517bd32da35c25d5fe8e78b88e11c), cite C236 OOS SHA `81d9a4ae5708ce29cd2e5dcde1c163fa1e87379f3aa766dd65a344378f22d0ff` and C235 OOS SHA `b1ea67400604f627f2232cfdf2511d6e06650e4968793f016d7dcbda8f49892b` and C234 OOS SHA `3fb43291866383c8a7b710ac531f4ca8ed82aea08a5d88e1052f5693c1e39ff9`. Emit `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_entropy_shock_mr_costed_oos_<UTC>.json` with `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds. **No carryover template text; set `campaign: 237`.**
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 237). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T233928Z.json` (86c477648ec8565fdabd90faefdb647f1a3517bd32da35c25d5fe8e78b88e11c). Include prior + all C237 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign237_execution_summary_<UTC>.json` listing **all new C237 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C237`, `next_campaign: C238`, latest registry/OOS sha+path, `oos_edge_proven`, `c238_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C237, with grep cmd/hits/evidence). Update this `HANDOFF.md`.

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_ENTROPY|WHITE_DIAG_LINE_LENGTH_ENTROPY' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self
# NOW: implement+run C237 -> emit >=4 artifacts with SHAs -> sync state.yaml + HANDOFF
```