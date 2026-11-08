# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261108T171046Z, C104–C220 LOCKED — edge_claim NONE, C221 PRESELECTED HEAVY — EXECUTE NEXT, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C220 LOCKED (no reruns). C221 preselected and grep-zero — execute C221 next, no status-first.**

## TIMESTAMPED INITIAL TASK MESSAGE (20261108T162135Z) — HEAVY WORK MANDATORY
**PRIORITY 1: EXECUTE C221.** C220 is complete on disk (VOLUME_RQA_RTE_OVER_WHITE_VERT_LINE_COUNT_DIVERGENCE_SHOCK_MR, `edge_claim:NONE`; cross-asset net sums fee0=-0.5045008233067952, fee5=-0.9665008233067957, fee10=-1.4285008233067957, fee20=-2.3525008233067957, fee40=-4.200500823306796 — fails all-cost-positive / B&H mean rule). **Do not summarize status. Do not stop at status. Implement + run C221 + emit >=4 artifacts with SHA256 from bytes + sync state.yaml + HANDOFF.**

## VERIFIED BASELINE (20261108T162135Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1).
- Caches: `data/cache/volume_1h_full.pkl/meta/provenance`, spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl`.
- **C219 DONE (locked):** OOS c11d7105... (VOLUME_RQA_RTE_OVER_DIAG_LINE_LENGTH_VARIANCE_SHOCK_MR, edge_claim NONE). Registry 15ad2742... superseded.
- **C220 DONE (verified on disk, SHAs from bytes):**
  - OOS a40a41178c6785fabed93c61d234adf50011b83878bd8599f0a0bd4fa2c2ee7e (`reports/real_quote_volume_rqa_rte_over_white_vert_line_count_divergence_shock_mr_costed_oos_20261108T162135Z.json`, VOLUME_RQA_RTE_OVER_WHITE_VERT_LINE_COUNT_DIVERGENCE_SHOCK_MR, edge_claim NONE, oos_edge_proven false).
  - Ingest 8fe26d17853e84eb153d6c0158406e9cd2b7ccffb09db8867fbfe7f3b6803b4c (`reports/real_feed_ingest_attempt_20261108T162135Z.json`).
  - Registry 2bdd04e7a3a43df9236abe09315d35489129be062b0658cc81b0bf56588a327f (`reports/strategy_edge_registry_20261108T162135Z.json`) supersedes `reports/strategy_edge_registry_20261108T161616Z.json` (15ad2742...).
  - Script 69d7b1d9e9d862803e7228c7167e60dd298a8997eee3617a3f3437d261705d1e (`scripts/run_real_quote_volume_rqa_rte_over_white_vert_line_count_divergence_shock_mr_costed_oos.py`).
  - Summary f85bac3621c1d5982849a675404e45f1deabc2c8c6ec39b9518d95a004fb1b71 (`reports/campaign220_execution_summary_20261108T162135Z.json`).
  - Distinctness grep 0 non-self at run (`RTE_OVER_WHITE_VERT_LINE_COUNT_DIVERGENCE`).
- Single durable handoff = this file + `research_state/state.yaml`. Latest registry = `reports/strategy_edge_registry_20261108T162135Z.json` (2bdd04e7...). Latest OOS = C220 `a40a4117...` (oos_edge_proven false).

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **No status-first.** Artifacts on disk are the deliverable.
- **No reruns of locked campaigns C104–C220.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Collision handling is fail-closed:** if a preselected candidate collides on grep, reject it, pick a distinct grep-zero fallback, record primary/fallback grep cmd/hits/evidence in all artifacts + state + HANDOFF.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence.
- **Heavy work mandatory.** No status-only replies. No stop between campaigns.

## C221 — NEXT FOCUS CAMPAIGN (PRESELECTED, GREP-ZERO VERIFIED 20261108T170640Z)
**Primary candidate:** `VOLUME_RQA_RTE_OVER_DIAG_LINE_DENSITY_DIVERGENCE_SHOCK_MR` — RQA ratio RTE / DIAG_LINE_DENSITY_DIVERGENCE on delay-embedded log-volume returns (RTE = recurrence time entropy of white vertical gap distribution, w>=w_min, LOI/self excluded; DIAG_LINE_DENSITY_DIVERGENCE = max(rho_k)-mean(rho_k) over off-diagonal diagonals k!=0 with >=1 qualifying diagonal run, where rho_k = (sum of qualifying run lengths l>=l_min on diagonal k) / (number of cells on diagonal k in embedded RP); fail-closed if <2 qualifying diagonals or divergence <=0/non-finite/undefined). Distinct from WHITE_VERT_LINE_COUNT_DIVERGENCE(C220), DIAG_LINE_LENGTH_VARIANCE(C219), DIAG_LINE_COUNT_DIVERGENCE(C218), VERT_LINE_LENGTH_VARIANCE(C217), VERT_LINE_COUNT_DIVERGENCE(C216), MAXDIAGLINE_DIVERGENCE(C214), diagonal L(C211), LMAX(C209), VMAX(C207), etc. Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2,w_min=1`. Trailing/causal only.
**Fallbacks (grep-zero 20261108T170640Z):** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_COUNT_DIVERGENCE_SHOCK_MR` (0), `VOLUME_RQA_RTE_OVER_DIAG_LINE_DENSITY_VARIANCE_SHOCK_MR` (0).

### COLLISION GUARD (RUN AT START)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_DIAG_LINE_DENSITY_DIVERGENCE|rte_over_diag_line_density_divergence' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self for chosen candidate
```
If collision found: pick a distinct grep-zero fallback not used C125–C220 (verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + `state.yaml`.

### REQUIRED C221 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_rte_over_diag_line_density_divergence_shock_mr_costed_oos.py` (or collision-safe). Model on C188–C220. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T162135Z.json` (2bdd04e7...), cite C220 OOS SHA `a40a41178c6785fabed93c61d234adf50011b83878bd8599f0a0bd4fa2c2ee7e`. Emit `reports/real_quote_volume_rqa_rte_over_diag_line_density_divergence_shock_mr_costed_oos_<UTC>.json` with `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds. **No carryover template text**.
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 221). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T162135Z.json` (2bdd04e7...). Include prior + all C221 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign221_execution_summary_<UTC>.json` listing **all new C221 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C221`, `next_campaign: C222`, latest registry/OOS sha+path, `oos_edge_proven`, `c222_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C221, with grep cmd/hits/evidence). Update this `HANDOFF.md`.

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_DIAG_LINE_DENSITY_DIVERGENCE|rte_over_diag_line_density_divergence' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self
# NOW: implement+run C221 -> emit >=4 artifacts with SHAs -> sync state.yaml + HANDOFF
```

## C222 (AUTO-QUEUED, HEAVY)
After C221 complete and synced: preselect a **distinct grep-verified** RQA-ratio candidate not used C125–C221, record in `state.yaml.c222_preselected`, and **execute C222 immediately** under same template. No status-only replies. No stop between campaigns.
