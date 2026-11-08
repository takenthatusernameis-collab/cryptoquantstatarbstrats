# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261108T133543Z, C104–C215 LOCKED — edge_claim NONE, C216 PRESELECTED HEAVY — EXECUTE NEXT, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C215 LOCKED (no reruns). C216 preselected and grep-zero — execute C216 next, no status-first.**

## TIMESTAMPED INITIAL TASK MESSAGE (20261108T133543Z) — HEAVY WORK MANDATORY
**PRIORITY 1: EXECUTE C216.** C215 is complete on disk (VOLUME_RQA_RTE_OVER_MAXVERTLINE_DIVERGENCE_SHOCK_MR, `edge_claim:NONE`; cross-asset net sums fee0=0.09179416775637406, fee5=-0.10820583224362611, fee10=-0.3082058322436262, fee20=-0.7082058322436261, fee40=-1.508205832243626 — fails all-cost-positive / B&H mean rule). **Do not summarize status. Do not stop at status. Implement + run C216 + emit >=4 artifacts with SHA256 from bytes + sync state.yaml + HANDOFF.**

## VERIFIED BASELINE (20261108T133543Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1). pytest 9.2.0 available.
- Caches: `data/cache/volume_1h_full.pkl/meta/provenance`, spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl`.
- **C214 DONE (verified):** OOS aa9b3e65... (`reports/real_quote_volume_rqa_rte_over_maxdiagline_divergence_shock_mr_costed_oos_20261108T132919Z.json`, VOLUME_RQA_RTE_OVER_MAXDIAGLINE_DIVERGENCE_SHOCK_MR, edge_claim NONE). Registry 684475cd... superseded.
- **C215 DONE (verified on disk, SHAs from bytes):**
  - OOS d6f8a8633e8b062f051299b4a2e14cbbec67b943bc0ebb00de96898907848d13 (`reports/real_quote_volume_rqa_rte_over_maxvertline_divergence_shock_mr_costed_oos_20261108T133543Z.json`, VOLUME_RQA_RTE_OVER_MAXVERTLINE_DIVERGENCE_SHOCK_MR, edge_claim NONE, oos_edge_proven false).
  - Ingest 24cb675c9fcf38650606fa622753fe648e2ecc843d77f1fc50474ba1fe60cd9f (`reports/real_feed_ingest_attempt_20261108T133543Z.json`).
  - Registry 93d680e08abae269ac846a2dad5a18fb338ab11e0c708648b3300e5d41af053e (`reports/strategy_edge_registry_20261108T133543Z.json`) supersedes `reports/strategy_edge_registry_20261108T132919Z.json` (684475cd...).
  - Script c36930d4ba54b514ce649bf3dcbe6f6c84dbcb23874e154903e53875ea8334c0 (`scripts/run_real_quote_volume_rqa_rte_over_maxvertline_divergence_shock_mr_costed_oos.py`).
  - Summary 5fecd9fa1f8327b03f2e567a524b45fd9520945ea1e38024416c14d57ef8ec39 (`reports/campaign215_execution_summary_20261108T133543Z.json`).
  - Distinctness grep 0 non-self at run (`RTE_OVER_MAXVERTLINE_DIVERGENCE`).
- Single durable handoff = this file + `research_state/state.yaml`. Latest registry = `reports/strategy_edge_registry_20261108T133543Z.json` (93d680e0...). Latest OOS = C215 `d6f8a863...` (oos_edge_proven false).

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **No status-first.** Artifacts on disk are the deliverable.
- **No reruns of locked campaigns C104–C215.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence in artifacts + state.
- **Heavy work mandatory.** No status-only replies. No stop between campaigns.

## C216 — NEXT FOCUS CAMPAIGN (PRESELECTED, GREP-ZERO VERIFIED 20261108T133543Z)
**Primary candidate:** `VOLUME_RQA_RTE_OVER_VERT_HORIZ_LINE_MAX_RATIO_SHOCK_MR` — RQA ratio RTE / VERT_HORIZ_LINE_MAX_RATIO on delay-embedded log-volume returns (RTE = recurrence time entropy of white vertical gap distribution, w>=w_min, LOI/self excluded; VERT_HORIZ_LINE_MAX_RATIO = max qualifying black vertical line length / max qualifying diagonal line length over off-diagonal diagonals, l>=l_min, LOI excluded as appropriate; fail-closed if max diagonal <=0/non-finite/undefined, max vertical undefined/non-finite, or insufficient qualifying lines). Distinct from MAXVERTLINE_DIVERGENCE(C215), MAXDIAGLINE_DIVERGENCE(C214), WMAX(C213), VAVG(C212), diagonal L(C211), WAVG(C210), LMAX(C209), black-vertical LAVG(C208), VMAX(C207), TREND(C206), TT(C205), LAM(C204), DET(C203), ENTR(C202). Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2,w_min=1` (ratio VMAX_qual/LMAX_qual_offdiag defined explicitly at run; fail-closed NaN/no-signal if denominator<=0/non-finite/undefined). Trailing/causal only.
**Fallback (grep-zero 20261108T133543Z):** `VOLUME_RQA_RTE_OVER_VERT_LINE_COUNT_DIVERGENCE_SHOCK_MR` (0 hits). Pick only a distinct grep-zero candidate not used C125–C215.

### COLLISION GUARD (RUN AT START)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_VERT_HORIZ_LINE_MAX_RATIO|rte_over_vert_horiz_line_max_ratio|VERT_HORIZ_LINE_MAX_RATIO' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self for chosen candidate
```
If collision found: pick a distinct grep-zero fallback not used C125–C215 (verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + `state.yaml`.

### REQUIRED C216 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_rte_over_vert_horiz_line_max_ratio_shock_mr_costed_oos.py` (or collision-safe). Model on C188–C215. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T133543Z.json` (93d680e0...), cite C215 OOS SHA `d6f8a8633e8b062f051299b4a2e14cbbec67b943bc0ebb00de96898907848d13`. Emit `reports/real_quote_volume_rqa_rte_over_vert_horiz_line_max_ratio_shock_mr_costed_oos_<UTC>.json` with `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds. **No carryover template text**: campaign/refs/denominator labels must match RTE/VERT_HORIZ_LINE_MAX_RATIO.
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 216). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T133543Z.json` (93d680e0...). Include prior + all C216 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign216_execution_summary_<UTC>.json` listing **all new C216 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C216`, `next_campaign: C217`, latest registry/OOS sha+path, `oos_edge_proven`, `c217_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C216, with grep cmd/hits/evidence). Update this `HANDOFF.md`.

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_VERT_HORIZ_LINE_MAX_RATIO|rte_over_vert_horiz_line_max_ratio|VERT_HORIZ_LINE_MAX_RATIO' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self
# NOW: implement+run C216 -> emit >=4 artifacts with SHAs -> sync state.yaml + HANDOFF
```

## C217 (AUTO-QUEUED, HEAVY)
After C216 complete and synced: preselect a **distinct grep-verified** RQA-ratio candidate not used C125–C216, record in `state.yaml.c217_preselected`, and **execute C217 immediately** under same template. No status-only replies. No stop between campaigns.
