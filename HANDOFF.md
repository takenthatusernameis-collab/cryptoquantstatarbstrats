# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261108T172359Z, C104–C221 LOCKED — edge_claim NONE, C222 PRESELECTED HEAVY — EXECUTE NEXT, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C221 LOCKED (no reruns). C222 preselected and grep-zero — execute C222 next, no status-first.**

## TIMESTAMPED INITIAL TASK MESSAGE (20261108T172359Z) — HEAVY WORK MANDATORY
**PRIORITY 1: EXECUTE C222.** C221 is complete on disk (VOLUME_RQA_RTE_OVER_DIAG_LINE_DENSITY_DIVERGENCE_SHOCK_MR, `edge_claim:NONE`; cross-asset net sums fee0=-0.011321488706244054, fee5=-0.8213214887062446, fee10=-1.6313214887062444, fee20=-3.2513214887062443, fee40=-6.4913214887062445 — fails all-cost-positive / B&H mean rule). **Do not summarize status. Do not stop at status. Implement + run C222 + emit >=4 artifacts with SHA256 from bytes + sync state.yaml + HANDOFF.**

## VERIFIED BASELINE (20261108T172359Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1).
- Caches: `data/cache/volume_1h_full.pkl/meta/provenance`, spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl`.
- **C220 DONE (locked):** OOS a40a4117... (VOLUME_RQA_RTE_OVER_WHITE_VERT_LINE_COUNT_DIVERGENCE_SHOCK_MR, edge_claim NONE). Registry 2bdd04e7... superseded.
- **C221 DONE (verified on disk, SHAs from bytes):**
  - OOS a9113bcaa3a8d4dd7819774962bceabb463728b6b199bd7115118d033e005671 (`reports/real_quote_volume_rqa_rte_over_diag_line_density_divergence_shock_mr_costed_oos_20261108T171915Z.json`, VOLUME_RQA_RTE_OVER_DIAG_LINE_DENSITY_DIVERGENCE_SHOCK_MR, edge_claim NONE, oos_edge_proven false, any_exposure_oos true).
  - Ingest 1f6dd8b73e2a7d1a9619bb005390e052913162b81f660e50077210eca5ac115f (`reports/real_feed_ingest_attempt_20261108T171915Z.json`).
  - Registry dd512fef5216c6fc9d4758c1bfb6f75211ba55e8f6ed9bb18ee82bc750348bec (`reports/strategy_edge_registry_20261108T171915Z.json`) supersedes `reports/strategy_edge_registry_20261108T162135Z.json` (2bdd04e7...).
  - Script e3b6c9cf0c74fa183244c445906c313d9dfac6b9ba37a7a7959bf11c15691629 (`scripts/run_real_quote_volume_rqa_rte_over_diag_line_density_divergence_shock_mr_costed_oos.py`).
  - Summary 234529fe7f4398d420f462472a7b8f2f4f1ee0fb769e1a1fa8d610d152866b20 (`reports/campaign221_execution_summary_20261108T171915Z.json`).
  - Distinctness grep 0 non-self at run (`RTE_OVER_DIAG_LINE_DENSITY_DIVERGENCE`).
- Single durable handoff = this file + `research_state/state.yaml`. Latest registry = `reports/strategy_edge_registry_20261108T171915Z.json` (dd512fef...). Latest OOS = C221 `a9113bca...` (oos_edge_proven false).

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **No status-first.** Artifacts on disk are the deliverable.
- **No reruns of locked campaigns C104–C221.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Collision handling is fail-closed:** if a preselected candidate collides on grep, reject it, pick a distinct grep-zero fallback, record primary/fallback grep cmd/hits/evidence in all artifacts + state + HANDOFF.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence.
- **Heavy work mandatory.** No status-only replies. No stop between campaigns.

## C222 — NEXT FOCUS CAMPAIGN (PRESELECTED, GREP-ZERO VERIFIED 20261108T172246Z)
**Primary candidate:** `VOLUME_RQA_RTE_OVER_DIAG_LINE_DENSITY_VARIANCE_SHOCK_MR` — RQA ratio RTE / DIAG_LINE_DENSITY_VARIANCE on delay-embedded log-volume returns (RTE = recurrence time entropy of white vertical gap distribution, w>=w_min, LOI/self excluded; DIAG_LINE_DENSITY_VARIANCE = sample variance ddof=1 of rho_k over off-diagonal diagonals k!=0 with >=1 qualifying diagonal run, where rho_k = (sum of qualifying run lengths l>=l_min on diagonal k) / (number of cells on diagonal k M_pts-|k|); fail-closed if <2 qualifying diagonals or variance <=0/non-finite/undefined). Distinct from DIAG_LINE_DENSITY_DIVERGENCE(C221), WHITE_VERT_LINE_COUNT_DIVERGENCE(C220), DIAG_LINE_LENGTH_VARIANCE(C219), DIAG_LINE_COUNT_DIVERGENCE(C218), VERT_LINE_LENGTH_VARIANCE(C217), VERT_LINE_COUNT_DIVERGENCE(C216), MAXDIAGLINE_DIVERGENCE(C214), diagonal L(C211), LMAX(C209), VMAX(C207). Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2,w_min=1`. Trailing/causal only.
**Fallbacks (grep-zero 20261108T172246Z):** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_DENSITY_DIVERGENCE_SHOCK_MR` (0), `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_COUNT_DIVERGENCE_SHOCK_MR` (0).

### COLLISION GUARD (RUN AT START)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_DIAG_LINE_DENSITY_VARIANCE|rte_over_diag_line_density_variance' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self
```
If collision found: pick a distinct grep-zero fallback not used C125–C221 (verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + `state.yaml`.

### REQUIRED C222 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_rte_over_diag_line_density_variance_shock_mr_costed_oos.py` (or collision-safe). Model on C188–C221. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T171915Z.json` (dd512fef...), cite C221 OOS SHA `a9113bcaa3a8d4dd7819774962bceabb463728b6b199bd7115118d033e005671`. Emit `reports/real_quote_volume_rqa_rte_over_diag_line_density_variance_shock_mr_costed_oos_<UTC>.json` with `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds. **No carryover template text**.
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 222). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T171915Z.json` (dd512fef...). Include prior + all C222 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign222_execution_summary_<UTC>.json` listing **all new C222 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C222`, `next_campaign: C223`, latest registry/OOS sha+path, `oos_edge_proven`, `c223_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C222, with grep cmd/hits/evidence). Update this `HANDOFF.md`.

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_DIAG_LINE_DENSITY_VARIANCE|rte_over_diag_line_density_variance' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self
# NOW: implement+run C222 -> emit >=4 artifacts with SHAs -> sync state.yaml + HANDOFF
```

## C223 (AUTO-QUEUED, HEAVY)
After C222 complete and synced: preselect a **distinct grep-verified** RQA-ratio candidate not used C125–C222, record in `state.yaml.c223_preselected`, and **execute C223 immediately** under same template. No status-only replies. No stop between campaigns.
