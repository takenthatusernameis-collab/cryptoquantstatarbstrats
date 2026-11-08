# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261108T192919Z, C104–C225 LOCKED — edge_claim NONE, C226 DONE, C227 PRESELECTED HEAVY — EXECUTE NEXT, NO STATUS-FIRST)**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C225 LOCKED (no reruns). C226 DONE on disk (edge_claim NONE). C227 preselected and grep-zero — execute C227 next, no status-first.**

## TIMESTAMPED INITIAL TASK MESSAGE (20261108T192444Z) — HEAVY WORK MANDATORY
**PRIORITY 1: EXECUTE C227.** C226 is complete on disk (VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_VARIANCE_SHOCK_MR, edge_claim NONE; cross-asset net sums fee0=-0.7869153295896248, fee5=-1.2579153295896253, fee10=-1.7289153295896253, fee20=-2.670915329589625, fee40=-4.554915329589625 — fails all-cost-positive / B&H mean rule). **Do not summarize status. Do not stop at status. Implement + run C227 + emit >=4 artifacts with SHA256 from bytes + sync state.yaml + HANDOFF.**

## VERIFIED BASELINE (20261108T192444Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1).
- Caches: `data/cache/volume_1h_full.pkl/meta/provenance` (43658953.../4d321584.../c7ff2f27...), spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` (56075733...).
- **C223 DONE (locked):** OOS 68cbd388... (VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_DENSITY_DIVERGENCE_SHOCK_MR, edge_claim NONE).
- **C224 DONE (locked):** OOS 01e730107d... (VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_DENSITY_VARIANCE_SHOCK_MR, edge_claim NONE).
- **C225 DONE (locked):** OOS 62da7c2594bdba7be3b30903c7dd0a529a15491898a42690178ab3e690fc67f7 (`reports/real_quote_volume_rqa_rte_over_white_diag_line_count_divergence_shock_mr_costed_oos_20261108T191100Z.json`, VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_COUNT_DIVERGENCE_SHOCK_MR, edge_claim NONE). Registry 191700Z fdc5be62... supersedes 183000Z 50bc0974....
- **C226 DONE (verified on disk, SHAs from bytes):**
  - OOS (canonical) c670c83caea7b53b58eb5138b3a17b74ae138569fb7a01557a212df550583665 (`reports/real_quote_volume_rqa_rte_over_white_diag_line_length_variance_shock_mr_costed_oos_20261108T192253Z.json`, VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_VARIANCE_SHOCK_MR, edge_claim NONE, oos_edge_proven false, any_exposure_oos true).
  - OOS (alt/earlier run, same nets) 31b95ecea91be4979e10a7f3c385a70f91791144db15d4ce251825b3cf7e665f (`..._20261108T192131Z.json`).
  - Ingest cc38b0f37894227679ef4176a865a5347e01044222b09b89d3a3ed699e94f8da (`reports/real_feed_ingest_attempt_20261108T192444Z.json`).
  - Registry 22eca308e0b063c2603ea1132ad102e5070c31755c643c113036dcf8f928c3db (`reports/strategy_edge_registry_20261108T192444Z.json`) supersedes 191700Z fdc5be62....
  - Script 9bf2cb2925f199beb1505c7e91a26ebebbd6c6b7252c0e21f4af6a1744ea2ce2 (`scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_variance_shock_mr_costed_oos.py`).
  - Summary 25dcd110b8b5c8b19f81421ec913f520a59e3c86736e269349f353ff7469a0d3 (`reports/campaign226_execution_summary_20261108T192444Z.json`).
  - Distinctness grep 0 non-self at run (RTE_OVER_WHITE_DIAG_LINE_LENGTH_VARIANCE).
  - **Known anomaly (C226):** OOS script/artifacts carry `campaign: 225` / template carryover text in header/out; canonical campaign is **226** per registry/summary/state. Do not rerun C226 to fix text; record anomaly.
- Single durable handoff = this file + `research_state/state.yaml`. Latest registry = `reports/strategy_edge_registry_20261108T192444Z.json` (22eca308...). Latest OOS = C226 `c670c83c...` (oos_edge_proven false).

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **C226 completion bottleneck removed.** Ingest + registry + summary emitted (20261108T192444Z) and `state.yaml`/`HANDOFF.md` synced (C226 OOS already on disk). C226 no longer blocks C227.
- **No status-first.** Artifacts on disk are the deliverable.
- **No reruns of locked campaigns C104–C225.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Collision handling is fail-closed:** if a preselected candidate collides on grep, reject it, pick a distinct grep-zero fallback, record primary/fallback grep cmd/hits/evidence in all artifacts + state + HANDOFF.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence.
- **Heavy work mandatory.** No status-only replies. No stop between campaigns.

## C227 — NEXT FOCUS CAMPAIGN (PRESELECTED, GREP-ZERO VERIFIED 20261108T192444Z)
**Primary candidate:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_DIVERGENCE_SHOCK_MR` — RQA ratio RTE / WHITE_DIAG_LINE_LENGTH_DIVERGENCE on delay-embedded log-volume returns (RTE = recurrence time entropy of white vertical gap distribution, w>=w_min, LOI/self excluded; WHITE_DIAG_LINE_LENGTH_DIVERGENCE = max(len_k_white)-mean(len_k_white) over off-diagonal diagonals k!=0 with >=1 qualifying white diagonal segment of consecutive 0s meeting w_min>=2, where len_k_white = mean qualifying white segment length on diagonal k; fail-closed if <2 qualifying diagonals or divergence <=0/non-finite/undefined). Distinct from WHITE_DIAG_LINE_LENGTH_VARIANCE(C226), WHITE_DIAG_LINE_COUNT_DIVERGENCE(C225), WHITE_DIAG_LINE_DENSITY_VARIANCE(C224), WHITE_DIAG_LINE_DENSITY_DIVERGENCE(C223), DIAG_LINE_DENSITY_VARIANCE(C222), DIAG_LINE_DENSITY_DIVERGENCE(C221), and prior C125-C226 families. Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,w_min=2` (white diagonal segment definition explicit and trailing/causal).
**Fallbacks (grep-zero 20261108T192444Z):** `VOLUME_RQA_RTE_OVER_DIAG_LINE_LENGTH_DIVERGENCE_SHOCK_MR` (0), `VOLUME_RQA_RTE_OVER_DIAG_LINE_COUNT_VARIANCE_SHOCK_MR` (0).

### COLLISION GUARD (RUN AT START)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_DIVERGENCE|rte_over_white_diag_line_length_divergence|WHITE_DIAG_LINE_LENGTH_DIVERGENCE|white_diag_line_length_divergence' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self
```
If collision found: pick a distinct grep-zero fallback not used C125–C226 (verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + state + HANDOFF.

### REQUIRED C227 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_divergence_shock_mr_costed_oos.py` (or collision-safe). Model on C188–C226. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T192444Z.json` (22eca308...), cite C226 OOS SHA `c670c83caea7b53b58eb5138b3a17b74ae138569fb7a01557a212df550583665` (canonical) and C225 OOS SHA `62da7c2594bdba7be3b30903c7dd0a529a15491898a42690178ab3e690fc67f7`. Emit `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_divergence_shock_mr_costed_oos_<UTC>.json` with `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds. **No carryover template text; set `campaign: 227`.**
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 227). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T192444Z.json` (22eca308...). Include prior + all C227 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign227_execution_summary_<UTC>.json` listing **all new C227 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C227`, `next_campaign: C228`, latest registry/OOS sha+path, `oos_edge_proven`, `c228_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C227, with grep cmd/hits/evidence). Update this `HANDOFF.md`.

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_DIVERGENCE|rte_over_white_diag_line_length_divergence|WHITE_DIAG_LINE_LENGTH_DIVERGENCE|white_diag_line_length_divergence' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self
# NOW: implement+run C227 -> emit >=4 artifacts with SHAs -> sync state.yaml + HANDOFF
```

## C228 (AUTO-QUEUED, HEAVY)
After C227 complete and synced: preselect a **distinct grep-verified** RQA-ratio candidate not used C125–C227, record in `state.yaml.c228_preselected`, and **execute C228 immediately** under same template. No status-only replies. No stop between campaigns.
