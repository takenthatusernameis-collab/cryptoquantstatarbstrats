# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261108T131955Z, C104–C212 LOCKED — edge_claim NONE, C213 PRESELECTED HEAVY — EXECUTE NEXT, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C212 LOCKED (no reruns). C213 preselected and grep-zero — execute C213 next, no status-first.**

## TIMESTAMPED INITIAL TASK MESSAGE (20261108T123656Z) — HEAVY WORK MANDATORY
**PRIORITY 1: EXECUTE C213.** C212 is complete on disk (VOLUME_RQA_RTE_OVER_VAVG_RATIO_SHOCK_MR, `edge_claim:NONE`; cross-asset net sums fee0=+0.8890509562115201, fee5=+0.6020509562115198, fee10=+0.31505095621151985, fee20=-0.25894904378848027, fee40=-1.4069490437884802 — fails all-cost-positive / B&H mean rule). **Do not summarize status. Do not stop at status. Implement + run C213 + emit >=4 artifacts with SHA256 from bytes + sync state.yaml + HANDOFF.**

## VERIFIED BASELINE (20261108T123656Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1). pytest 9.2.0 available.
- Caches: `data/cache/volume_1h_full.pkl/meta/provenance`, spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl`.
- **C212 DONE (verified on disk, SHAs from bytes):**
  - OOS bd8b0f0f727572f1f69c3479b0dfb3d444a26ea2ef1cf569a94527cc82ae2057 (`reports/real_quote_volume_rqa_rte_over_vavg_ratio_shock_mr_costed_oos_20261108T123534Z.json`, VOLUME_RQA_RTE_OVER_VAVG_RATIO_SHOCK_MR, edge_claim NONE).
  - Ingest 85cfc5968413f72bfd49d5931b9fe00bbde55d7c323eebfc84793c2d57264f18 (`reports/real_feed_ingest_attempt_20261108T123534Z.json`).
  - Registry 6ba3d270c2cc07deae16a03580bfee474d99cc4acfcf91ce21ec5f29e2538387 (`reports/strategy_edge_registry_20261108T123534Z.json`) supersedes C211 `2a0bb7b0cca78d9732b7ecf650b2611017bfcd17c9b16d6cfde71c5f44fceeda`.
  - Script aac627f24304eac1a54d21ed8ad4a2fabd3a3a2e3af1a9ce69967e8615324cf6 (`scripts/run_real_quote_volume_rqa_rte_over_vavg_ratio_shock_mr_costed_oos.py`).
  - Summary 06157a870ac5a964b73affd7b974a79e8730147b616a8e213cba340f881d32dc (`reports/campaign212_execution_summary_20261108T123534Z.json`).
  - Distinctness grep 0 non-self at run (`RTE_OVER_VAVG`). VAVG = mean vertical/laminar black line length (LOI/self excluded for laminar counting), distinct from diagonal L(C211), WAVG(C210), LMAX(C209), black-vertical LAVG context(C208), VMAX(C207), TREND(C206), TT(C205).
- Single durable handoff = this file + `research_state/state.yaml`. Latest registry = `reports/strategy_edge_registry_20261108T123534Z.json` (6ba3d270c2cc07deae16a03580bfee474d99cc4acfcf91ce21ec5f29e2538387).

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **No status-first.** Artifacts on disk are the deliverable.
- **No reruns of locked campaigns C104–C212.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence in artifacts + state.
- **Heavy work mandatory.** No status-only replies. No stop between campaigns.

## C213 — NEXT FOCUS CAMPAIGN (PRESELECTED, GREP-ZERO VERIFIED 20261108T123656Z)
**Primary candidate:** `VOLUME_RQA_RTE_OVER_WMAX_RATIO_SHOCK_MR` — RQA ratio RTE/WMAX on delay-embedded log-volume returns (RTE = recurrence time entropy; WMAX = maximum qualifying white vertical/gap length, gaps of consecutive 0s between recurrent points excluding trivial self, w>=w_min). Distinct from VAVG(C212), diagonal L(C211), WAVG(C210), LMAX(C209), black-vertical LAVG(C208), VMAX(C207), TREND(C206), TT(C205), LAM(C204), DET(C203), ENTR(C202). Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,w_min=1,l_min=2` (define/use l_min only if needed; WMAX is gap-based; be explicit). Fail-closed NaN/no-signal if RTE/WMAX/ratio undefined/non-finite/degenerate or insufficient qualifying gaps. Trailing/causal only.
**Fallbacks (grep-zero 20261108T123656Z):** `VOLUME_RQA_RTE_OVER_LVAR_RATIO_SHOCK_MR` (0 hits), `VOLUME_RQA_RTE_OVER_VVAR_RATIO_SHOCK_MR` (0 hits). Pick only a distinct grep-zero candidate not used C125–C212.

### COLLISION GUARD (RUN AT START)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WMAX|rte_over_wmax' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self for chosen candidate
```
If collision found: pick a distinct grep-zero fallback not used C125–C212 (verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + `state.yaml`.

### REQUIRED C213 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_rte_over_wmax_ratio_shock_mr_costed_oos.py` (or collision-safe). Model on C188–C212. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T123534Z.json` (6ba3d270...), cite C212 OOS SHA `bd8b0f0f727572f1f69c3479b0dfb3d444a26ea2ef1cf569a94527cc82ae2057`. Emit `reports/real_quote_volume_rqa_rte_over_wmax_ratio_shock_mr_costed_oos_<UTC>.json` with `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds. **No carryover template text**: campaign/refs/denominator labels must match RTE/WMAX.
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 213). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T123534Z.json` (6ba3d270...). Include prior + all C213 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign213_execution_summary_<UTC>.json` listing **all new C213 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C213`, `next_campaign: C214`, latest registry/OOS sha+path, `oos_edge_proven`, `c214_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C213, with grep cmd/hits/evidence). Update this `HANDOFF.md`.

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WMAX|rte_over_wmax' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self
# NOW: implement+run C213 -> emit >=4 artifacts with SHAs -> sync state.yaml + HANDOFF
```

## C214 (AUTO-QUEUED, HEAVY)
After C213 complete and synced: preselect a **distinct grep-verified** RQA-ratio candidate not used C125–C213, record in `state.yaml.c214_preselected`, and **execute C214 immediately** under same template. No status-only replies. No stop between campaigns.
