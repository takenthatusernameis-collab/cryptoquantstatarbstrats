# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261108T180900Z, C104–C222 LOCKED — edge_claim NONE, C223 PRESELECTED HEAVY — EXECUTE NEXT, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C222 LOCKED (no reruns). C223 preselected and grep-zero — execute C223 next, no status-first.**

## TIMESTAMPED INITIAL TASK MESSAGE (20261108T180900Z) — HEAVY WORK MANDATORY
**PRIORITY 1: EXECUTE C223.** C222 is complete on disk (VOLUME_RQA_RTE_OVER_DIAG_LINE_DENSITY_VARIANCE_SHOCK_MR, `edge_claim:NONE`; cross-asset net sums fee0=0.46703030248531685, fee5=-0.4909696975146838, fee10=-1.4489696975146835, fee20=-3.3649696975146832, fee40=-7.1969696975146835 — fails all-cost-positive / B&H mean rule at costed slices). **Do not summarize status. Do not stop at status. Implement + run C223 + emit >=4 artifacts with SHA256 from bytes + sync state.yaml + HANDOFF.**

## VERIFIED BASELINE (20261108T180900Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1).
- Caches: `data/cache/volume_1h_full.pkl/meta/provenance`, spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl`.
- **C221 DONE (locked):** OOS a9113bca... (VOLUME_RQA_RTE_OVER_DIAG_LINE_DENSITY_DIVERGENCE_SHOCK_MR, edge_claim NONE). Registry dd512fef... superseded.
- **C222 DONE (verified on disk, SHAs from bytes):**
  - OOS 62fc4bcaa896c87095b2c976047196fdf50d9c88e5636127022a736ddea6db82 (`reports/real_quote_volume_rqa_rte_over_diag_line_density_variance_shock_mr_costed_oos_20261108T172610Z.json`, VOLUME_RQA_RTE_OVER_DIAG_LINE_DENSITY_VARIANCE_SHOCK_MR, edge_claim NONE, oos_edge_proven false, any_exposure_oos true).
  - Ingest 9ce706dd195ef55bac084bb8fe5c9fb0cb68c3075b41239c2f641e6b9b795b14 (`reports/real_feed_ingest_attempt_20261108T172610Z.json`).
  - Registry e933070ee91d895e34c3ea6bc58861b62ba39f520d1e83410112e6f0d27e6506 (`reports/strategy_edge_registry_20261108T172610Z.json`) supersedes `reports/strategy_edge_registry_20261108T171915Z.json` (dd512fef...).
  - Script aa00ef84d4294f8c790c57bb554bee30934d03891ff84915cd379a347f1dccd6 (`scripts/run_real_quote_volume_rqa_rte_over_diag_line_density_variance_shock_mr_costed_oos.py`).
  - Summary 1ede787954666ae536171a889bf8378994fe4479bcf5090597e536f1e69d6ef3 (`reports/campaign222_execution_summary_20261108T172610Z.json`).
  - Distinctness grep 0 non-self at run (`RTE_OVER_DIAG_LINE_DENSITY_VARIANCE`).
- Single durable handoff = this file + `research_state/state.yaml`. Latest registry = `reports/strategy_edge_registry_20261108T172610Z.json` (e933070e...). Latest OOS = C222 `62fc4bca...` (oos_edge_proven false).

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **No status-first.** Artifacts on disk are the deliverable.
- **No reruns of locked campaigns C104–C222.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Collision handling is fail-closed:** if a preselected candidate collides on grep, reject it, pick a distinct grep-zero fallback, record primary/fallback grep cmd/hits/evidence in all artifacts + state + HANDOFF.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence.
- **Heavy work mandatory.** No status-only replies. No stop between campaigns.

## C223 — NEXT FOCUS CAMPAIGN (PRESELECTED, GREP-ZERO VERIFIED 20261108T180900Z)
**Primary candidate:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_DENSITY_DIVERGENCE_SHOCK_MR` — RQA ratio RTE / WHITE_DIAG_LINE_DENSITY_DIVERGENCE on delay-embedded log-volume returns (RTE = recurrence time entropy of white vertical gap distribution, w>=w_min, LOI/self excluded; WHITE_DIAG_LINE_DENSITY_DIVERGENCE = max(rho_k_white)-mean(rho_k_white) over off-diagonal diagonals k!=0 with >=1 qualifying white diagonal run/gap segment meeting explicit `w_min`, where rho_k_white is the white-run density/coverage on diagonal k relative to `M_pts-|k|`; fail-closed if <2 qualifying diagonals or divergence <=0/non-finite/undefined). Distinct from DIAG_LINE_DENSITY_VARIANCE(C222), DIAG_LINE_DENSITY_DIVERGENCE(C221), WHITE_VERT_LINE_COUNT_DIVERGENCE(C220), and prior C125-C221 families. Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2,w_min=2` (white diagonal definition must be explicit, trailing/causal).
**Fallbacks (grep-zero 20261108T180900Z):** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_COUNT_DIVERGENCE_SHOCK_MR` (0), `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_DENSITY_VARIANCE_SHOCK_MR` (0).

### COLLISION GUARD (RUN AT START)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_DENSITY_DIVERGENCE|rte_over_white_diag_line_density_divergence|WHITE_DIAG_LINE_DENSITY_DIVERGENCE|white_diag_line_density_divergence' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self
```
If collision found: pick a distinct grep-zero fallback not used C125–C222 (verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + state + HANDOFF.

### REQUIRED C223 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_density_divergence_shock_mr_costed_oos.py` (or collision-safe). Model on C188–C222. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T172610Z.json` (e933070e...), cite C222 OOS SHA `62fc4bcaa896c87095b2c976047196fdf50d9c88e5636127022a736ddea6db82`. Emit `reports/real_quote_volume_rqa_rte_over_white_diag_line_density_divergence_shock_mr_costed_oos_<UTC>.json` with `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds. **No carryover template text**.
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 223). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T172610Z.json` (e933070e...). Include prior + all C223 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign223_execution_summary_<UTC>.json` listing **all new C223 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C223`, `next_campaign: C224`, latest registry/OOS sha+path, `oos_edge_proven`, `c224_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C223, with grep cmd/hits/evidence). Update this `HANDOFF.md`.

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_DENSITY_DIVERGENCE|rte_over_white_diag_line_density_divergence|WHITE_DIAG_LINE_DENSITY_DIVERGENCE|white_diag_line_density_divergence' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self
# NOW: implement+run C223 -> emit >=4 artifacts with SHAs -> sync state.yaml + HANDOFF
```

## C224 (AUTO-QUEUED, HEAVY)
After C223 complete and synced: preselect a **distinct grep-verified** RQA-ratio candidate not used C125–C223, record in `state.yaml.c224_preselected`, and **execute C224 immediately** under same template. No status-only replies. No stop between campaigns.
