# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261108T143035Z, C104–C217 LOCKED — edge_claim NONE, C218 PRESELECTED HEAVY — EXECUTE NEXT, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C217 LOCKED (no reruns). C218 preselected and grep-zero — execute C218 next, no status-first.**

## TIMESTAMPED INITIAL TASK MESSAGE (20261108T143035Z) — HEAVY WORK MANDATORY
**PRIORITY 1: EXECUTE C218.** C217 is complete on disk (VOLUME_RQA_RTE_OVER_VERT_LINE_LENGTH_VARIANCE_SHOCK_MR, `edge_claim:NONE`; cross-asset net sums fee0=0.2098032652698416, fee5=0.01880326526984144, fee10=-0.17219673473015865, fee20=-0.5541967347301585, fee40=-1.3181967347301584 — fails all-cost-positive / B&H mean rule). **Do not summarize status. Do not stop at status. Implement + run C218 + emit >=4 artifacts with SHA256 from bytes + sync state.yaml + HANDOFF.**

## VERIFIED BASELINE (20261108T143035Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1).
- Caches: `data/cache/volume_1h_full.pkl/meta/provenance`, spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl`.
- **C216 DONE (locked):** OOS 5d4049b1... (VOLUME_RQA_RTE_OVER_VERT_LINE_COUNT_DIVERGENCE_SHOCK_MR, fallback after primary VERT_HORIZ_LINE_MAX_RATIO grep collision 5 hits; edge_claim NONE). Registry ff6f8cd5... superseded.
- **C217 DONE (verified on disk, SHAs from bytes):**
  - OOS bea428a8623ca02c6c64cf87ac5014519d4c537de49a40cf238fa2728afc52be (`reports/real_quote_volume_rqa_rte_over_vert_line_length_variance_shock_mr_costed_oos_20261108T143035Z.json`, VOLUME_RQA_RTE_OVER_VERT_LINE_LENGTH_VARIANCE_SHOCK_MR, edge_claim NONE, oos_edge_proven false).
  - Ingest 894918dea715180c28170a0b8b6fc0271f2b086b2e81c9e1eed4f79f6860fe96 (`reports/real_feed_ingest_attempt_20261108T143035Z.json`).
  - Registry 66ae83a784ef617b320b913307b8d81bac62a02435b2c104d508870db41af560 (`reports/strategy_edge_registry_20261108T143035Z.json`) supersedes `reports/strategy_edge_registry_20261108T142556Z.json` (ff6f8cd5...).
  - Script 1107be1f1011b0c101ff26c65806775d521e3bdec685128ae3e74d2f88c2aa16 (`scripts/run_real_quote_volume_rqa_rte_over_vert_line_length_variance_shock_mr_costed_oos.py`).
  - Summary 8f3b7ca50bb54e652ad3ba48d715396b4c8fd679ed023b02aa3e90ca76ef93e1 (`reports/campaign217_execution_summary_20261108T143035Z.json`).
  - Distinctness grep 0 non-self at run (`RTE_OVER_VERT_LINE_LENGTH_VARIANCE`).
- Single durable handoff = this file + `research_state/state.yaml`. Latest registry = `reports/strategy_edge_registry_20261108T143035Z.json` (66ae83a7...). Latest OOS = C217 `bea428a8...` (oos_edge_proven false).

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **No status-first.** Artifacts on disk are the deliverable.
- **No reruns of locked campaigns C104–C217.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Collision handling is fail-closed:** if a preselected candidate collides on grep, reject it, pick a distinct grep-zero fallback, record primary/fallback grep cmd/hits/evidence in all artifacts + state + HANDOFF.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence.
- **Heavy work mandatory.** No status-only replies. No stop between campaigns.

## C218 — NEXT FOCUS CAMPAIGN (PRESELECTED, GREP-ZERO VERIFIED 20261108T143035Z)
**Primary candidate:** `VOLUME_RQA_RTE_OVER_DIAG_LINE_COUNT_DIVERGENCE_SHOCK_MR` — RQA ratio RTE / DIAG_LINE_COUNT_DIVERGENCE on delay-embedded log-volume returns (RTE = recurrence time entropy of white vertical gap distribution, w>=w_min, LOI/self excluded; DIAG_LINE_COUNT_DIVERGENCE = max(d_k)-mean(d_k) over off-diagonal diagonals k!=0 that have >=1 qualifying diagonal line, where d_k is number of qualifying diagonal runs of consecutive 1s with length l>=l_min on diagonal k; fail-closed if <2 diagonals with qualifying lines or divergence <=0/non-finite/undefined). Distinct from VERT_LINE_COUNT_DIVERGENCE(C216), VERT_LINE_LENGTH_VARIANCE(C217), MAXVERTLINE_DIVERGENCE(C215), MAXDIAGLINE_DIVERGENCE(C214), WMAX(C213), VAVG(C212), diagonal L(C211), WAVG(C210), LMAX(C209), VMAX(C207), TREND(C206), TT(C205), LAM(C204), DET(C203), ENTR(C202), existing VERT_HORIZ_LINE_MAX_RATIO. Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2,w_min=1`. Trailing/causal only.
**Fallbacks (grep-zero 20261108T143035Z):** `VOLUME_RQA_RTE_OVER_WHITE_LINE_LENGTH_VARIANCE_SHOCK_MR` (0), `VOLUME_RQA_RTE_OVER_BLACK_VERT_LINE_COUNT_RATIO_SHOCK_MR` (0), `VOLUME_RQA_RTE_OVER_DIAG_LINE_LENGTH_VARIANCE_SHOCK_MR` (0).

### COLLISION GUARD (RUN AT START)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_DIAG_LINE_COUNT_DIVERGENCE|rte_over_diag_line_count_divergence' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self for chosen candidate
```
If collision found: pick a distinct grep-zero fallback not used C125–C217 (verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + `state.yaml`.

### REQUIRED C218 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_rte_over_diag_line_count_divergence_shock_mr_costed_oos.py` (or collision-safe). Model on C188–C217. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T143035Z.json` (66ae83a7...), cite C217 OOS SHA `bea428a8623ca02c6c64cf87ac5014519d4c537de49a40cf238fa2728afc52be`. Emit `reports/real_quote_volume_rqa_rte_over_diag_line_count_divergence_shock_mr_costed_oos_<UTC>.json` with `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds. **No carryover template text**.
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 218). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T143035Z.json` (66ae83a7...). Include prior + all C218 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign218_execution_summary_<UTC>.json` listing **all new C218 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C218`, `next_campaign: C219`, latest registry/OOS sha+path, `oos_edge_proven`, `c219_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C218, with grep cmd/hits/evidence). Update this `HANDOFF.md`.

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_DIAG_LINE_COUNT_DIVERGENCE|rte_over_diag_line_count_divergence' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self
# NOW: implement+run C218 -> emit >=4 artifacts with SHAs -> sync state.yaml + HANDOFF
```

## C219 (AUTO-QUEUED, HEAVY)
After C218 complete and synced: preselect a **distinct grep-verified** RQA-ratio candidate not used C125–C218, record in `state.yaml.c219_preselected`, and **execute C219 immediately** under same template. No status-only replies. No stop between campaigns.
