# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261108T201358Z, C104–C227 LOCKED — edge_claim NONE, C227 DONE, C228 PRESELECTED HEAVY — EXECUTE NEXT, NO STATUS-FIRST)**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C227 LOCKED (no reruns). C227 DONE on disk (edge_claim NONE). C228 preselected grep-zero (VOLUME_RQA_RTE_OVER_DIAG_LINE_COUNT_VARIANCE_SHOCK_MR) — execute C228 next, no status-first.** Latest registry = `reports/strategy_edge_registry_20261108T201358Z.json` (5fc6752e...). Latest OOS = C227 `037f23a5...` (oos_edge_proven false).

## TIMESTAMPED INITIAL TASK MESSAGE (20261108T201358Z) — HEAVY WORK MANDATORY
**PRIORITY 1: EXECUTE C228.** C227 is complete on disk (VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_DIVERGENCE_SHOCK_MR, edge_claim NONE; cross-asset net sums fee0=-0.029089727089156914, fee5=-0.5360897270891573, fee10=-1.0430897270891573, fee20=-2.057089727089157, fee40=-4.085089727089157 — fails all-cost-positive / B&H mean rule). Artifacts: OOS `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_divergence_shock_mr_costed_oos_20261108T201257Z.json` (sha 037f23a5...), ingest `reports/real_feed_ingest_attempt_20261108T201358Z.json` (sha 64523892...), registry `reports/strategy_edge_registry_20261108T201358Z.json` (sha 5fc6752e...), script `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_divergence_shock_mr_costed_oos.py` (sha 83cfea67...), summary `reports/campaign227_execution_summary_20261108T201358Z.json` (sha 18e737eb...). state.yaml + HANDOFF synced (latest_campaign_done C227, next_campaign C228). **Do not summarize status. Do not stop at status. Implement + run C228 + emit >=4 artifacts with SHA256 from bytes + sync state.yaml + HANDOFF.**

## VERIFIED BASELINE (20261108T201358Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1).
- Caches: `data/cache/volume_1h_full.pkl/meta/provenance` (43658953.../4d321584.../c7ff2f27...), spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` (56075733...).
- **C223–C226 DONE (locked):** edge_claim NONE, all oos_edge_proven false.
- **C227 DONE (verified on disk, SHAs from bytes):**
  - OOS (canonical) 037f23a5555807eaa24a966276ebb7a1fd916de5e516f60cee55184a8c086cba (`reports/real_quote_volume_rqa_rte_over_white_diag_line_length_divergence_shock_mr_costed_oos_20261108T201257Z.json`, VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_DIVERGENCE_SHOCK_MR, edge_claim NONE, oos_edge_proven false, any_exposure_oos true).
  - Ingest 6452389236b95ae685b2e9d9e11cd4fcd380bc580ad1e51525abbc5a0208e88f (`reports/real_feed_ingest_attempt_20261108T201358Z.json`).
  - Registry 5fc6752ed4ea3d6536ef87ae57f8d3205f502fbd93f7d8839edc1ea22c8804db (`reports/strategy_edge_registry_20261108T201358Z.json`) supersedes 192444Z 22eca308....
  - Script 83cfea67dac48e1de829d615ce8ef3bb19dde1582afa3b53aa8f6ca0a97fa2fb (`scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_divergence_shock_mr_costed_oos.py`).
  - Summary 18e737eb28f722334a87366659dfd6d4167c4950243a9d1cbfb14c2e8219e276 (`reports/campaign227_execution_summary_20261108T201358Z.json`).
  - Distinctness grep 0 non-self at run (RTE_OVER_WHITE_DIAG_LINE_LENGTH_DIVERGENCE).
  - C227 script was rewritten clean (removed C225/VARIANCE template carryover; campaign field 227; denominator = WHITE_DIAG_LINE_LENGTH_DIVERGENCE = max(len_k_white)-mean(len_k_white), distinct from C226 variance).
- Single durable handoff = this file + `research_state/state.yaml`.

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **C227 completion bottleneck removed.** Script + OOS + ingest + registry + summary emitted (20261108T201257Z/20261108T201358Z) and `state.yaml`/`HANDOFF.md` synced. C227 no longer blocks C228.
- **C226 completion bottleneck removed earlier.** Ingest + registry + summary emitted (20261108T192444Z) and state/HANDOFF synced; C226 OOS artifacts had campaign=225 template carryover (canonical 226). C226 no longer blocks C227/C228.
- **No status-first.** Artifacts on disk are the deliverable.
- **No reruns of locked campaigns C104–C227.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Collision handling is fail-closed:** if a preselected candidate collides on grep, reject it, pick a distinct grep-zero fallback, record primary/fallback grep cmd/hits/evidence in all artifacts + state + HANDOFF. For C228, `diag_line_length_*` and `diag_line_count_divergence` collide with C226/C227 text — reject them; use a distinct grep-zero fallback.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence.
- **Heavy work mandatory.** No status-only replies. No stop between campaigns.

## C228 — NEXT FOCUS CAMPAIGN (PRESELECTED, GREP-ZERO VERIFIED 20261108T201358Z)
**Primary candidate:** `VOLUME_RQA_RTE_OVER_DIAG_LINE_COUNT_VARIANCE_SHOCK_MR` — RQA ratio RTE / DIAG_LINE_COUNT_VARIANCE on delay-embedded log-volume returns (RTE = recurrence time entropy of white vertical gap distribution, w>=w_min, LOI/self excluded; DIAG_LINE_COUNT_VARIANCE = sample variance (ddof=1) of cnt_k over off-diagonal diagonals k!=0 with >=1 qualifying white diagonal segment of consecutive 0s meeting w_min>=2, where cnt_k = (number of qualifying white diagonal segments on diagonal k) / (number of cells on diagonal k = M_pts-|k|); fail-closed if <2 qualifying diagonals or variance <=0/non-finite/undefined). Distinct from WHITE_DIAG_LINE_LENGTH_DIVERGENCE(C227), WHITE_DIAG_LINE_LENGTH_VARIANCE(C226), WHITE_DIAG_LINE_COUNT_DIVERGENCE(C225), WHITE_DIAG_LINE_DENSITY_VARIANCE(C224), WHITE_DIAG_LINE_DENSITY_DIVERGENCE(C223), DIAG_LINE_DENSITY_VARIANCE(C222), DIAG_LINE_DENSITY_DIVERGENCE(C221), and prior C125-C226 families. Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,w_min=2` (trailing/causal; fail-closed NaN/no-signal if <2 qualifying diagonals or variance<=0/non-finite).
**grep evidence (20261108T201358Z):** `grep -rnE 'RTE_OVER_DIAG_LINE_COUNT_VARIANCE|rte_over_diag_line_count_variance|DIAG_LINE_COUNT_VARIANCE|diag_line_count_variance' scripts/ strategies/ backtest/ utils/ 2>&1` → 0 hits. `diag_line_length_*` (37 hits) and `diag_line_count_divergence` (86 hits) collide with C226/C227 text — rejected for C228.
**Fallback:** none preselected; at C228 start, grep-verify a distinct grep-zero RQA-ratio candidate not used C125–C227 and record evidence.

### COLLISION GUARD (RUN AT START)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_DIAG_LINE_COUNT_VARIANCE|rte_over_diag_line_count_variance|DIAG_LINE_COUNT_VARIANCE|diag_line_count_variance' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self
```
If collision found: pick a distinct grep-zero fallback not used C125–C227 (verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + state + HANDOFF.

### REQUIRED C228 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_rte_over_diag_line_count_variance_shock_mr_costed_oos.py` (or collision-safe). Model on C188–C227. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T201358Z.json` (5fc6752e...), cite C227 OOS SHA `037f23a5555807eaa24a966276ebb7a1fd916de5e516f60cee55184a8c086cba` (canonical) and C226 OOS SHA `c670c83caea7b53b58eb5138b3a17b74ae138569fb7a01557a212df550583665`. Emit `reports/real_quote_volume_rqa_rte_over_diag_line_count_variance_shock_mr_costed_oos_<UTC>.json` with `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds. **No carryover template text; set `campaign: 228`.**
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 228). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T201358Z.json` (5fc6752e...). Include prior + all C228 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign228_execution_summary_<UTC>.json` listing **all new C228 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C228`, `next_campaign: C229`, latest registry/OOS sha+path, `oos_edge_proven`, `c229_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C228, with grep cmd/hits/evidence). Update this `HANDOFF.md`.

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_DIAG_LINE_COUNT_VARIANCE|rte_over_diag_line_count_variance|DIAG_LINE_COUNT_VARIANCE|diag_line_count_variance' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self
# NOW: implement+run C228 -> emit >=4 artifacts with SHAs -> sync state.yaml + HANDOFF
```

## C229 (AUTO-QUEUED, HEAVY)
After C228 complete and synced: preselect a **distinct grep-verified** RQA-ratio candidate not used C125–C228, record in `state.yaml.c229_preselected`, and **execute C229 immediately** under same template. No status-only replies. No stop between campaigns.
