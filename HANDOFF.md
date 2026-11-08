# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261108T183000Z, C104–C224 LOCKED — edge_claim NONE, C225 PRESELECTED HEAVY — EXECUTE NEXT, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C224 LOCKED (no reruns). C225 preselected and grep-zero — execute C225 next, no status-first.**

## TIMESTAMPED INITIAL TASK MESSAGE (20261108T183000Z) — HEAVY WORK MANDATORY
**PRIORITY 1: EXECUTE C225.** C224 is complete on disk (VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_DENSITY_VARIANCE_SHOCK_MR, `edge_claim:NONE`; cross-asset net sums fee0=-3.446650620966497, fee5=-5.198650620966498, fee10=-6.950650620966498, fee20=-10.454650620966499, fee40=-17.4626506209665 — fails all-cost-positive / B&H mean rule). **Do not summarize status. Do not stop at status. Implement + run C225 + emit >=4 artifacts with SHA256 from bytes + sync state.yaml + HANDOFF.**

## VERIFIED BASELINE (20261108T183000Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1).
- Caches: `data/cache/volume_1h_full.pkl/meta/provenance` (43658953.../4d321584.../c7ff2f27...), spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` (56075733...).
- **C222 DONE (locked):** OOS 62fc4bca... (VOLUME_RQA_RTE_OVER_DIAG_LINE_DENSITY_VARIANCE_SHOCK_MR, edge_claim NONE).
- **C223 DONE (locked):** OOS 68cbd388... (VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_DENSITY_DIVERGENCE_SHOCK_MR, edge_claim NONE).
- **C224 DONE (verified on disk, SHAs from bytes):**
  - OOS 01e730107d1e671e2bba1672e5a92dba3d2c589f36c130a6349efe5dd3e87e7d (`reports/real_quote_volume_rqa_rte_over_white_diag_line_density_variance_shock_mr_costed_oos_20261108T182721Z.json`, VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_DENSITY_VARIANCE_SHOCK_MR, edge_claim NONE, oos_edge_proven false, any_exposure_oos true).
  - Ingest 5f3fd9997a5cfd363eff5cd8a32cc031d479bb2b706740a1f1f1f9b320624b30 (`reports/real_feed_ingest_attempt_20261108T182721Z.json`).
  - Registry 50bc0974e68fa4069c94f0558e8749189f7594319027d3e096d9522e8fc7b5a2 (`reports/strategy_edge_registry_20261108T183000Z.json`) supersedes `reports/strategy_edge_registry_20261108T181704Z.json` (e8b90fc1...).
  - Script 9c52f039a7fdb4ba9965ddc205761699c294d099a7e8fbc0ca19fe14d0a7c10d (`scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_density_variance_shock_mr_costed_oos.py`).
  - Summary 813b880d6174f2aedb2cb2c82d0202f4c111a2ae6533f1aa7f2bf36665c44fb3 (`reports/campaign224_execution_summary_20261108T183000Z.json`).
  - Distinctness grep 0 non-self at run (RTE_OVER_WHITE_DIAG_LINE_DENSITY_VARIANCE).
- Single durable handoff = this file + `research_state/state.yaml`. Latest registry = `reports/strategy_edge_registry_20261108T183000Z.json` (50bc0974...). Latest OOS = C224 `01e730107d...` (oos_edge_proven false).

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **No status-first.** Artifacts on disk are the deliverable.
- **No reruns of locked campaigns C104–C224.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Collision handling is fail-closed:** if a preselected candidate collides on grep, reject it, pick a distinct grep-zero fallback, record primary/fallback grep cmd/hits/evidence in all artifacts + state + HANDOFF.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence.
- **Heavy work mandatory.** No status-only replies. No stop between campaigns.

## C225 — NEXT FOCUS CAMPAIGN (PRESELECTED, GREP-ZERO VERIFIED 20261108T183000Z)
**Primary candidate:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_COUNT_DIVERGENCE_SHOCK_MR` — RQA ratio RTE / WHITE_DIAG_LINE_COUNT_DIVERGENCE on delay-embedded log-volume returns (RTE = recurrence time entropy of white vertical gap distribution, w>=w_min, LOI/self excluded; WHITE_DIAG_LINE_COUNT_DIVERGENCE = max(cnt_k_white)-mean(cnt_k_white) over off-diagonal diagonals k!=0 with >=1 qualifying white diagonal segment of consecutive 0s meeting w_min>=2, where cnt_k_white counts qualifying white diagonal segments normalized by diagonal length (M_pts-|k|); fail-closed if <2 qualifying diagonals or divergence <=0/non-finite/undefined). Distinct from WHITE_DIAG_LINE_DENSITY_VARIANCE(C224), WHITE_DIAG_LINE_DENSITY_DIVERGENCE(C223), DIAG_LINE_DENSITY_VARIANCE(C222), DIAG_LINE_DENSITY_DIVERGENCE(C221), and prior C125-C224 families. Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,w_min=2` (white diagonal segment definition explicit and trailing/causal).
**Fallbacks (grep-zero 20261108T183000Z):** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_VARIANCE_SHOCK_MR` (0), `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_DENSITY_DIVERGENCE_SHOCK_MR` (0).

### COLLISION GUARD (RUN AT START)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_COUNT_DIVERGENCE|rte_over_white_diag_line_count_divergence|WHITE_DIAG_LINE_COUNT_DIVERGENCE|white_diag_line_count_divergence' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self
```
If collision found: pick a distinct grep-zero fallback not used C125–C224 (verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + state + HANDOFF.

### REQUIRED C225 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_count_divergence_shock_mr_costed_oos.py` (or collision-safe). Model on C188–C224. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T183000Z.json` (50bc0974...), cite C224 OOS SHA `01e730107d1e671e2bba1672e5a92dba3d2c589f36c130a6349efe5dd3e87e7d`. Emit `reports/real_quote_volume_rqa_rte_over_white_diag_line_count_divergence_shock_mr_costed_oos_<UTC>.json` with `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds. **No carryover template text**.
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 225). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T183000Z.json` (50bc0974...). Include prior + all C225 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign225_execution_summary_<UTC>.json` listing **all new C225 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C225`, `next_campaign: C226`, latest registry/OOS sha+path, `oos_edge_proven`, `c226_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C225, with grep cmd/hits/evidence). Update this `HANDOFF.md`.

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_COUNT_DIVERGENCE|rte_over_white_diag_line_count_divergence|WHITE_DIAG_LINE_COUNT_DIVERGENCE|white_diag_line_count_divergence' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self
# NOW: implement+run C225 -> emit >=4 artifacts with SHAs -> sync state.yaml + HANDOFF
```

## C226 (AUTO-QUEUED, HEAVY)
After C225 complete and synced: preselect a **distinct grep-verified** RQA-ratio candidate not used C125–C225, record in `state.yaml.c226_preselected`, and **execute C226 immediately** under same template. No status-only replies. No stop between campaigns.
