# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261108T132123Z, C104–C213 LOCKED — edge_claim NONE, C214 PRESELECTED HEAVY — EXECUTE NEXT, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C213 LOCKED (no reruns). C214 preselected and grep-zero — execute C214 next, no status-first.**

## TIMESTAMPED INITIAL TASK MESSAGE (20261108T132123Z) — HEAVY WORK MANDATORY
**PRIORITY 1: EXECUTE C214.** C213 is complete on disk (VOLUME_RQA_RTE_OVER_WMAX_RATIO_SHOCK_MR, `edge_claim:NONE`; cross-asset net sums fee0=+0.14389016497749163, fee5=-0.26510983502250873, fee10=-0.6741098350225087, fee20=-1.4921098350225086, fee40=-3.1281098350225083 — fails all-cost-positive / B&H mean rule). **Do not summarize status. Do not stop at status. Implement + run C214 + emit >=4 artifacts with SHA256 from bytes + sync state.yaml + HANDOFF.**

## VERIFIED BASELINE (20261108T132123Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1). pytest 9.2.0 available.
- Caches: `data/cache/volume_1h_full.pkl/meta/provenance`, spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl`.
- **C212 DONE (verified on disk, SHAs from bytes):**
  - OOS bd8b0f0f727572f1f69c3479b0dfb3d444a26ea2ef1cf569a94527cc82ae2057 (`reports/real_quote_volume_rqa_rte_over_vavg_ratio_shock_mr_costed_oos_20261108T123534Z.json`, VOLUME_RQA_RTE_OVER_VAVG_RATIO_SHOCK_MR, edge_claim NONE).
  - Registry 6ba3d270c2cc07deae16a03580bfee474d99cc4acfcf91ce21ec5f29e2538387 (`reports/strategy_edge_registry_20261108T123534Z.json`).
- **C213 DONE (verified on disk, SHAs from bytes):**
  - OOS a19284df4be82279f89a8bdb715f672bfc0abade1ee8eead400b40dd9a41319f (`reports/real_quote_volume_rqa_rte_over_wmax_ratio_shock_mr_costed_oos_20261108T131955Z.json`, VOLUME_RQA_RTE_OVER_WMAX_RATIO_SHOCK_MR, edge_claim NONE, oos_edge_proven false).
  - Ingest 97c2f94bbf489b2955b0f835cbaa8edf773a9d1f74e5ecbcc9a96b202609e8fe (`reports/real_feed_ingest_attempt_20261108T131955Z.json`).
  - Registry e27c5e4668701f71fc762eb14e1279742a96bd4b6f70bb837510e4089aeaed22 (`reports/strategy_edge_registry_20261108T131955Z.json`) supersedes `reports/strategy_edge_registry_20261108T123534Z.json` (6ba3d270...).
  - Script f22df79b9f8c00eae82b5c5a40b8aeb8989b6e640d48d76a51c3901419cd1f80 (`scripts/run_real_quote_volume_rqa_rte_over_wmax_ratio_shock_mr_costed_oos.py`).
  - Summary 252931036ccfdd28323a7ac8e8b5791d96dc4b8fb1cdef3c158f51876f5fa3a3 (`reports/campaign213_execution_summary_20261108T131955Z.json`).
  - Distinctness grep 0 non-self at run (`RTE_OVER_WMAX`). WMAX = max qualifying white vertical/gap length, distinct from VAVG(C212), diagonal L(C211), WAVG(C210), LMAX(C209), black-vertical LAVG(C208), VMAX(C207), TREND(C206), TT(C205), LAM(C204), DET(C203), ENTR(C202).
- Single durable handoff = this file + `research_state/state.yaml`. Latest registry = `reports/strategy_edge_registry_20261108T131955Z.json` (e27c5e46...). Latest OOS = C213 `a19284df...` (oos_edge_proven false).

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **No status-first.** Artifacts on disk are the deliverable.
- **No reruns of locked campaigns C104–C213.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence in artifacts + state.
- **Heavy work mandatory.** No status-only replies. No stop between campaigns.

## C214 — NEXT FOCUS CAMPAIGN (PRESELECTED, GREP-ZERO VERIFIED 20261108T132123Z)
**Primary candidate:** `VOLUME_RQA_RTE_OVER_MAXDIAGLINE_DIVERGENCE_SHOCK_MR` — RQA ratio RTE / MAXDIAGLINE_DIVERGENCE on delay-embedded log-volume returns (RTE = recurrence time entropy; MAXDIAGLINE_DIVERGENCE = max diagonal line length minus mean diagonal line length, divergence of diagonal recurrence structure; fail-closed if denominator <=0/non-finite/undefined or insufficient diagonal lines). Distinct from VAVG(C212), WMAX(C213), diagonal L(C211), WAVG(C210), LMAX(C209), black-vertical LAVG(C208), VMAX(C207), TREND(C206), TT(C205), LAM(C204), DET(C203), ENTR(C202). Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168` (denominator divergence defined explicitly at run; fail-closed NaN/no-signal if RTE/MAXDIAGLINE_DIVERGENCE/ratio undefined/non-finite/degenerate). Trailing/causal only.
**Fallbacks (grep-zero 20261108T132123Z):** `VOLUME_RQA_RTE_OVER_MAXVERTLINE_DIVERGENCE_SHOCK_MR` (0 hits), `VOLUME_RQA_RTE_OVER_VERT_HORIZ_LINE_MAX_RATIO_SHOCK_MR` (0 hits). Pick only a distinct grep-zero candidate not used C125–C213.

### COLLISION GUARD (RUN AT START)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_MAXDIAGLINE_DIVERGENCE|rte_over_maxdiagline_divergence' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self for chosen candidate
```
If collision found: pick a distinct grep-zero fallback not used C125–C213 (verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + `state.yaml`.

### REQUIRED C214 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_rte_over_maxdiagline_divergence_shock_mr_costed_oos.py` (or collision-safe). Model on C188–C213. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T131955Z.json` (e27c5e46...), cite C213 OOS SHA `a19284df4be82279f89a8bdb715f672bfc0abade1ee8eead400b40dd9a41319f`. Emit `reports/real_quote_volume_rqa_rte_over_maxdiagline_divergence_shock_mr_costed_oos_<UTC>.json` with `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds. **No carryover template text**: campaign/refs/denominator labels must match RTE/MAXDIAGLINE_DIVERGENCE.
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 214). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T131955Z.json` (e27c5e46...). Include prior + all C214 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign214_execution_summary_<UTC>.json` listing **all new C214 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C214`, `next_campaign: C215`, latest registry/OOS sha+path, `oos_edge_proven`, `c215_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C214, with grep cmd/hits/evidence). Update this `HANDOFF.md`.

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_MAXDIAGLINE_DIVERGENCE|rte_over_maxdiagline_divergence' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self
# NOW: implement+run C214 -> emit >=4 artifacts with SHAs -> sync state.yaml + HANDOFF
```

## C215 (AUTO-QUEUED, HEAVY)
After C214 complete and synced: preselect a **distinct grep-verified** RQA-ratio candidate not used C125–C214, record in `state.yaml.c215_preselected`, and **execute C215 immediately** under same template. No status-only replies. No stop between campaigns.
