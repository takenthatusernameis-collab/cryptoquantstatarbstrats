# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261108T162000Z, C104–C219 LOCKED — edge_claim NONE, C220 PRESELECTED HEAVY — EXECUTE NEXT, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C219 LOCKED (no reruns). C220 preselected and grep-zero — execute C220 next, no status-first.**

## TIMESTAMPED INITIAL TASK MESSAGE (20261108T143601Z) — HEAVY WORK MANDATORY
**PRIORITY 1: EXECUTE C220.** C219 is complete on disk (VOLUME_RQA_RTE_OVER_DIAG_LINE_LENGTH_VARIANCE_SHOCK_MR, `edge_claim:NONE`; cross-asset net sums fee0=0.45961062411649733, fee5=0.12961062411649704, fee10=-0.20038937588350308, fee20=-0.8603893758835028, fee40=-2.180389375883503 — fails all-cost-positive / B&H mean rule). **Do not summarize status. Do not stop at status. Implement + run C220 + emit >=4 artifacts with SHA256 from bytes + sync state.yaml + HANDOFF.**

## VERIFIED BASELINE (20261108T161616Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1).
- Caches: `data/cache/volume_1h_full.pkl/meta/provenance`, spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl`.
- **C217 DONE (locked):** OOS bea428a8... (VOLUME_RQA_RTE_OVER_VERT_LINE_LENGTH_VARIANCE_SHOCK_MR, edge_claim NONE).
- **C218 DONE (verified on disk, SHAs from bytes):** OOS 3aecb9d9... (VOLUME_RQA_RTE_OVER_DIAG_LINE_COUNT_DIVERGENCE_SHOCK_MR, edge_claim NONE). Registry 1dbf7764... superseded.
- **C219 DONE (verified on disk, SHAs from bytes):**
  - OOS c11d71057300dcce0f9e14a6b9b7f50baf7ca877617757896eddc3f3f535f1d6 (`reports/real_quote_volume_rqa_rte_over_diag_line_length_variance_shock_mr_costed_oos_20261108T161616Z.json`, VOLUME_RQA_RTE_OVER_DIAG_LINE_LENGTH_VARIANCE_SHOCK_MR, edge_claim NONE, oos_edge_proven false).
  - Ingest 4a4ab9883ad949ecd20784d432b3e0658456a878006c7fa9732830f217a07749 (`reports/real_feed_ingest_attempt_20261108T161616Z.json`).
  - Registry 15ad27422c563b6cdb0286174803f138893a004f80dd9f3d852bacd8c200b60a (`reports/strategy_edge_registry_20261108T161616Z.json`) supersedes `reports/strategy_edge_registry_20261108T143601Z.json` (1dbf7764...).
  - Script 2935d5fa8374fbe5c5fc81a3e02324e0dffac7b59f9338f5216b394836254b3b (`scripts/run_real_quote_volume_rqa_rte_over_diag_line_length_variance_shock_mr_costed_oos.py`).
  - Summary 2368b1f0fba957e2c2bb1283fa6c8403872462486cf1aab8441d79173459e353 (`reports/campaign219_execution_summary_20261108T161616Z.json`).
  - Distinctness grep 0 non-self at run (`RTE_OVER_DIAG_LINE_LENGTH_VARIANCE`).
- Single durable handoff = this file + `research_state/state.yaml`. Latest registry = `reports/strategy_edge_registry_20261108T161616Z.json` (15ad2742...). Latest OOS = C219 `c11d7105...` (oos_edge_proven false).

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **No status-first.** Artifacts on disk are the deliverable.
- **No reruns of locked campaigns C104–C219.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Collision handling is fail-closed:** if a preselected candidate collides on grep, reject it, pick a distinct grep-zero fallback, record primary/fallback grep cmd/hits/evidence in all artifacts + state + HANDOFF.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence.
- **Heavy work mandatory.** No status-only replies. No stop between campaigns.

## C220 — NEXT FOCUS CAMPAIGN (PRESELECTED, GREP-ZERO VERIFIED 20261108T161616Z)
**Primary candidate:** `VOLUME_RQA_RTE_OVER_WHITE_VERT_LINE_COUNT_DIVERGENCE_SHOCK_MR` — RQA ratio RTE / WHITE_VERT_LINE_COUNT_DIVERGENCE on delay-embedded log-volume returns (RTE = recurrence time entropy of white vertical gap distribution, w>=w_min, LOI/self excluded; WHITE_VERT_LINE_COUNT_DIVERGENCE = max(c_k)-mean(c_k) over off-diagonal diagonals k!=0 where c_k = number of qualifying white vertical line runs of consecutive 0s (gaps) w>=w_min on diagonal k; fail-closed if <2 qualifying diagonals or divergence <=0/non-finite/undefined). Distinct from DIAG_LINE_LENGTH_VARIANCE(C219), DIAG_LINE_COUNT_DIVERGENCE(C218), VERT_LINE_LENGTH_VARIANCE(C217), VERT_LINE_COUNT_DIVERGENCE(C216), MAXDIAGLINE_DIVERGENCE(C214), diagonal L(C211), LMAX(C209), VMAX(C207), etc. Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2,w_min=1`. Trailing/causal only.
**Fallbacks (grep-zero 20261108T161616Z):** `VOLUME_RQA_RTE_OVER_DIAG_LINE_DENSITY_DIVERGENCE_SHOCK_MR` (0), `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_COUNT_DIVERGENCE_SHOCK_MR` (0).

### COLLISION GUARD (RUN AT START)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_VERT_LINE_COUNT_DIVERGENCE|rte_over_white_vert_line_count_divergence' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self for chosen candidate
```
If collision found: pick a distinct grep-zero fallback not used C125–C219 (verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + `state.yaml`.

### REQUIRED C220 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_rte_over_white_vert_line_count_divergence_shock_mr_costed_oos.py` (or collision-safe). Model on C188–C219. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T161616Z.json` (15ad2742...), cite C219 OOS SHA `c11d71057300dcce0f9e14a6b9b7f50baf7ca877617757896eddc3f3f535f1d6`. Emit `reports/real_quote_volume_rqa_rte_over_white_vert_line_count_divergence_shock_mr_costed_oos_<UTC>.json` with `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds. **No carryover template text**.
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 220). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T161616Z.json` (15ad2742...). Include prior + all C220 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign220_execution_summary_<UTC>.json` listing **all new C220 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C220`, `next_campaign: C221`, latest registry/OOS sha+path, `oos_edge_proven`, `c221_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C220, with grep cmd/hits/evidence). Update this `HANDOFF.md`.

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_VERT_LINE_COUNT_DIVERGENCE|rte_over_white_vert_line_count_divergence' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self
# NOW: implement+run C220 -> emit >=4 artifacts with SHAs -> sync state.yaml + HANDOFF
```

## C221 (AUTO-QUEUED, HEAVY)
After C220 complete and synced: preselect a **distinct grep-verified** RQA-ratio candidate not used C125–C220, record in `state.yaml.c221_preselected`, and **execute C221 immediately** under same template. No status-only replies. No stop between campaigns.
