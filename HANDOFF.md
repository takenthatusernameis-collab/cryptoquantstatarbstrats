# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261108T191700Z, C104–C224 LOCKED — edge_claim NONE, C225 DONE, C226 PRESELECTED HEAVY — EXECUTE NEXT, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C224 LOCKED (no reruns). C225 DONE on disk (edge_claim NONE, not locked). C226 preselected and grep-zero — execute C226 next, no status-first.**

## TIMESTAMPED INITIAL TASK MESSAGE (20261108T191700Z) — HEAVY WORK MANDATORY
**PRIORITY 1: EXECUTE C226.** C225 is complete on disk (VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_COUNT_DIVERGENCE_SHOCK_MR, edge_claim NONE; cross-asset net sums fee0=0.11622082026510105, fee5=-1.6537791797348993, fee10=-3.423779179734899, fee20=-6.9637791797349, fee40=-14.0437791797349 — fails all-cost-positive / B&H mean rule). **Do not summarize status. Do not stop at status. Implement + run C226 + emit >=4 artifacts with SHA256 from bytes + sync state.yaml + HANDOFF.**

## VERIFIED BASELINE (20261108T191700Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1).
- Caches: `data/cache/volume_1h_full.pkl/meta/provenance` (43658953.../4d321584.../c7ff2f27...), spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` (56075733...).
- **C222 DONE (locked):** OOS 62fc4bca... (VOLUME_RQA_RTE_OVER_DIAG_LINE_DENSITY_VARIANCE_SHOCK_MR, edge_claim NONE).
- **C223 DONE (locked):** OOS 68cbd388... (VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_DENSITY_DIVERGENCE_SHOCK_MR, edge_claim NONE).
- **C224 DONE (verified on disk, SHAs from bytes):** OOS 01e730107d... (VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_DENSITY_VARIANCE_SHOCK_MR, edge_claim NONE, oos_edge_proven false). Registry 50bc0974... (`reports/strategy_edge_registry_20261108T183000Z.json`) supersedes 181704Z (e8b90fc1...).
- **C225 DONE (verified on disk, SHAs from bytes):**
  - OOS 62da7c2594bdba7be3b30903c7dd0a529a15491898a42690178ab3e690fc67f7 (`reports/real_quote_volume_rqa_rte_over_white_diag_line_count_divergence_shock_mr_costed_oos_20261108T191100Z.json`, VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_COUNT_DIVERGENCE_SHOCK_MR, edge_claim NONE, oos_edge_proven false, any_exposure_oos true). Duplicate run 190907Z sha 32776161...; 191100Z canonical.
  - Ingest 36b5f35bd8f6f694f913479e2c6cb3e99cd658c10e3e557789d15029df10059c (`reports/real_feed_ingest_attempt_20261108T191700Z.json`).
  - Registry fdc5be628b4c2da0c6d004f9566e14e35d0bdc8cd04e258649e5775d5185ca6d (`reports/strategy_edge_registry_20261108T191700Z.json`) supersedes `reports/strategy_edge_registry_20261108T183000Z.json` (50bc0974...).
  - Script 5d493f73fb1727ddf92ae8423a818f3668763b44d10b416e64a4eb915620ea7f (`scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_count_divergence_shock_mr_costed_oos.py`).
  - Summary 2e17fa1203f31927a883e168f4ae6cad214ece7a1c88a880f8eb4e7a41ffaf78 (`reports/campaign225_execution_summary_20261108T191700Z.json`).
  - Distinctness grep 0 non-self at run (RTE_OVER_WHITE_DIAG_LINE_COUNT_DIVERGENCE).
  - Known anomaly: C225 OOS artifacts' `references.c224_oos` path cites C222's path (`...diag_line_density_variance..._20261108T172610Z.json`) with C224's SHA 01e73010...; correct C224 OOS path is `...white_diag_line_density_variance..._20261108T182721Z.json`. Do not rerun C225; cite correct path in C226 references.
- Single durable handoff = this file + `research_state/state.yaml`. Latest registry = `reports/strategy_edge_registry_20261108T191700Z.json` (fdc5be62...). Latest OOS = C225 `62da7c25...` (oos_edge_proven false).

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **C225 completion bottleneck removed.** Ingest + registry + summary emitted (20261108T191700Z) and `state.yaml`/`HANDOFF.md` synced. C225 no longer blocks C226.
- **No status-first.** Artifacts on disk are the deliverable.
- **No reruns of locked campaigns C104–C224.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Collision handling is fail-closed:** if a preselected candidate collides on grep, reject it, pick a distinct grep-zero fallback, record primary/fallback grep cmd/hits/evidence in all artifacts + state + HANDOFF.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence.
- **Heavy work mandatory.** No status-only replies. No stop between campaigns.

## C226 — NEXT FOCUS CAMPAIGN (PRESELECTED, GREP-ZERO VERIFIED 20261108T191700Z)
**Primary candidate:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_VARIANCE_SHOCK_MR` — RQA ratio RTE / WHITE_DIAG_LINE_LENGTH_VARIANCE on delay-embedded log-volume returns (RTE = recurrence time entropy of white vertical gap distribution, w>=w_min, LOI/self excluded; WHITE_DIAG_LINE_LENGTH_VARIANCE = sample variance ddof=1 of len_k_white over off-diagonal diagonals k!=0 with >=1 qualifying white diagonal segment of consecutive 0s meeting w_min>=2, where len_k_white = mean qualifying white segment length on diagonal k; fail-closed if <2 qualifying diagonals or variance <=0/non-finite/undefined). Distinct from WHITE_DIAG_LINE_COUNT_DIVERGENCE(C225), WHITE_DIAG_LINE_DENSITY_VARIANCE(C224), WHITE_DIAG_LINE_DENSITY_DIVERGENCE(C223), DIAG_LINE_DENSITY_VARIANCE(C222), DIAG_LINE_DENSITY_DIVERGENCE(C221), and prior C125-C225 families. Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,w_min=2` (white diagonal segment definition explicit and trailing/causal).
**Fallbacks (grep-zero 20261108T191700Z):** `VOLUME_RQA_RTE_OVER_DIAG_LINE_COUNT_VARIANCE_SHOCK_MR` (0), `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_COUNT_VARIANCE_SHOCK_MR` (0).

### COLLISION GUARD (RUN AT START)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_VARIANCE|rte_over_white_diag_line_length_variance|WHITE_DIAG_LINE_LENGTH_VARIANCE|white_diag_line_length_variance' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self
```
If collision found: pick a distinct grep-zero fallback not used C125–C225 (verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + state + HANDOFF.

### REQUIRED C226 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_variance_shock_mr_costed_oos.py` (or collision-safe). Model on C188–C225. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T191700Z.json` (fdc5be62...), cite C225 OOS SHA `62da7c2594bdba7be3b30903c7dd0a529a15491898a42690178ab3e690fc67f7` and correct C224 OOS path `reports/real_quote_volume_rqa_rte_over_white_diag_line_density_variance_shock_mr_costed_oos_20261108T182721Z.json` (01e73010...). Emit `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_variance_shock_mr_costed_oos_<UTC>.json` with `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds. **No carryover template text.**
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 226). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T191700Z.json` (fdc5be62...). Include prior + all C226 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign226_execution_summary_<UTC>.json` listing **all new C226 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C226`, `next_campaign: C227`, latest registry/OOS sha+path, `oos_edge_proven`, `c227_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C226, with grep cmd/hits/evidence). Update this `HANDOFF.md`.

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_VARIANCE|rte_over_white_diag_line_length_variance|WHITE_DIAG_LINE_LENGTH_VARIANCE|white_diag_line_length_variance' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self
# NOW: implement+run C226 -> emit >=4 artifacts with SHAs -> sync state.yaml + HANDOFF
```

## C227 (AUTO-QUEUED, HEAVY)
After C226 complete and synced: preselect a **distinct grep-verified** RQA-ratio candidate not used C125–C226, record in `state.yaml.c227_preselected`, and **execute C227 immediately** under same template. No status-only replies. No stop between campaigns.
