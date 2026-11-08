# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261108T122345Z, C104–C210 LOCKED — edge_claim NONE, C211 AUTO-QUEUED HEAVY — EXECUTE IMMEDIATELY, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C210 LOCKED (no reruns). C211 is preselected and grep-zero — execute C211 immediately, no status-first, no stop between campaigns.**

## TIMESTAMPED INITIAL TASK MESSAGE (20261108T122345Z) — HEAVY WORK MANDATORY
**PRIORITY 1: EXECUTE C211 NOW.** C210 is complete on disk (VOLUME_RQA_RTE_OVER_WAVG_RATIO_SHOCK_MR, `edge_claim:NONE`; cross-asset net sums fee0=+0.7094048671901464, fee5=+0.31440486719014604, fee10=-0.08059513280985406, fee20=-0.8705951328098539, fee40=-2.4505951328098536 — fails all-cost-positive / B&H mean rule). **Do not summarize status. Do not stop at status. Implement + run C211 + emit >=4 artifacts with SHA256 from bytes + sync state.yaml + HANDOFF.**

## VERIFIED BASELINE (20261108T122345Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1). pytest 9.2.0 available.
- Caches: `data/cache/volume_1h_full.pkl/meta/provenance`, spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl`.
- **C210 DONE (verified on disk, SHAs from bytes):**
  - OOS 99643e3535f41703519bcc3c33081e370c02f38d5d8d7cae8ac81077d23c741c (`reports/real_quote_volume_rqa_rte_over_wavg_ratio_shock_mr_costed_oos_20261108T121953Z.json`, VOLUME_RQA_RTE_OVER_WAVG_RATIO_SHOCK_MR, edge_claim NONE).
  - Ingest efc01e8e49a01574b1c8ed4ab6bf63148b8794cdb0c8fca17282394033282645 (`reports/real_feed_ingest_attempt_20261108T121953Z.json`).
  - Registry bb367557184ea9e36470d5aca9d5a2d585f8ace7ff2cbaed3061c64670707ec6 (`reports/strategy_edge_registry_20261108T121953Z.json`) supersedes C209 `0b66773ab515bb51a32908e5d52caa56ef96a523f49aaf6a95e05f234ef7c5c1`.
  - Script 3698a90e44bc45190d15560995bf29058d563b406ed61ceec5efa1578094870d (`scripts/run_real_quote_volume_rqa_rte_over_wavg_ratio_shock_mr_costed_oos.py`).
  - Summary ebb0418d4da33dcdfc5d0e1af960a2981af9f9265a92ec5da2db8a6c9e918399 (`reports/campaign210_execution_summary_20261108T121953Z.json`).
  - Distinctness grep 0 non-self at run (RTE_OVER_WAVG). WAVG distinct from LMAX/LAVG/VMAX/TT/TREND pairings.
- Single durable handoff = this file + `research_state/state.yaml`. Latest registry = `reports/strategy_edge_registry_20261108T121953Z.json` (bb367557184ea9e36470d5aca9d5a2d585f8ace7ff2cbaed3061c64670707ec6).

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **No status-first.** Artifacts on disk are the deliverable.
- **No reruns of locked campaigns C104–C210.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence in artifacts + state.
- **Heavy work mandatory.** No status-only replies. No stop between campaigns.

## C211 — NEXT FOCUS CAMPAIGN (PRESELECTED, GREP-ZERO VERIFIED 20261108T122345Z)
**Primary candidate:** `VOLUME_RQA_RTE_OVER_L_RATIO_SHOCK_MR` — RQA ratio RTE/L on delay-embedded log-volume returns (RTE = recurrence time entropy; L = mean diagonal line length). Distinct from LMAX(C209), LAVG(C208), VMAX(C207), TT(C205), TREND(C206), WAVG(C210), LAM(C204), DET(C203), ENTR(C202), RR-ineligible pairings. Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,w_min=1,l_min=2`. Fail-closed NaN/no-signal if RTE/L/ratio undefined/non-finite/degenerate or insufficient qualifying lines/gaps. Trailing/causal only.
**Fallbacks (verify at run):** `VOLUME_RQA_RTE_OVER_WMAX_RATIO_SHOCK_MR`, `VOLUME_RQA_RTE_OVER_LMEAN_RATIO_SHOCK_MR`. Pick only a distinct grep-zero candidate not used C125–C210.

### COLLISION GUARD (RUN AT START)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_L\b|rte_over_l[^a-z]' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self for chosen candidate
```
If collision found: pick a distinct grep-zero fallback not used C125–C210 (verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + `state.yaml`.

### REQUIRED C211 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_rte_over_l_ratio_shock_mr_costed_oos.py` (or collision-safe). Model on C188–C210. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T121953Z.json` (bb367557184ea9e36470d5aca9d5a2d585f8ace7ff2cbaed3061c64670707ec6), cite C210 OOS SHA `99643e3535f41703519bcc3c33081e370c02f38d5d8d7cae8ac81077d23c741c`. Emit `reports/real_quote_volume_rqa_rte_over_l_ratio_shock_mr_costed_oos_<UTC>.json` with `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds. **No carryover template text**: campaign/refs/denominator labels must match RTE/L.
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 211). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T121953Z.json` (bb367557...). Include prior + all C211 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign211_execution_summary_<UTC>.json` listing **all new C211 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C211`, `next_campaign: C212`, latest registry/OOS sha+path, `oos_edge_proven`, `c212_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C211, with grep cmd/hits/evidence). Update this `HANDOFF.md`.

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_L\b|rte_over_l[^a-z]' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self
# NOW: implement+run C211 -> emit >=4 artifacts with SHAs -> sync state.yaml + HANDOFF
```

## C212 (AUTO-QUEUED, HEAVY)
After C211 complete and synced: preselect a **distinct grep-verified** RQA-ratio candidate not used C125–C211, record in `state.yaml.c212_preselected`, and **execute C212 immediately** under same template. No status-only replies. No stop between campaigns.
