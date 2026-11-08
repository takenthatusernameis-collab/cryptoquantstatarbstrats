# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261108T123055Z, C104–C211 LOCKED — edge_claim NONE, C212 PRESELECTED HEAVY — EXECUTE NEXT, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C211 LOCKED (no reruns). C212 preselected and grep-zero — execute C212 next, no status-first.**

## TIMESTAMPED INITIAL TASK MESSAGE (20261108T123055Z) — HEAVY WORK MANDATORY
**PRIORITY 1: EXECUTE C212.** C211 is complete on disk (VOLUME_RQA_RTE_OVER_L_RATIO_SHOCK_MR, `edge_claim:NONE`; cross-asset net sums fee0=+1.0481886475258184, fee5=+0.6531886475258181, fee10=+0.2581886475258179, fee20=-0.5318113524741819, fee40=-2.1118113524741813 — fails all-cost-positive / B&H mean rule). **Do not summarize status. Do not stop at status. Implement + run C212 + emit >=4 artifacts with SHA256 from bytes + sync state.yaml + HANDOFF.**

## VERIFIED BASELINE (20261108T123055Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1). pytest 9.2.0 available.
- Caches: `data/cache/volume_1h_full.pkl/meta/provenance`, spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl`.
- **C211 DONE (verified on disk, SHAs from bytes):**
  - OOS f987b29947f1a252c3a656315b89d6903fc0d6395d001b376bf5a63d2e68aa03 (`reports/real_quote_volume_rqa_rte_over_l_ratio_shock_mr_costed_oos_20261108T122845Z.json`, VOLUME_RQA_RTE_OVER_L_RATIO_SHOCK_MR, edge_claim NONE).
  - Ingest a3caf9596dbd7a309cd1e31349092b4238fe40a4907f7f89c045648effef03a9 (`reports/real_feed_ingest_attempt_20261108T122845Z.json`).
  - Registry 2a0bb7b0cca78d9732b7ecf650b2611017bfcd17c9b16d6cfde71c5f44fceeda (`reports/strategy_edge_registry_20261108T122845Z.json`) supersedes C210 `bb367557184ea9e36470d5aca9d5a2d585f8ace7ff2cbaed3061c64670707ec6`.
  - Script 2b561e31092c9cfd5c6fb1c157555d2348bd8a2ebc450289796c746c68d0bfe5 (`scripts/run_real_quote_volume_rqa_rte_over_l_ratio_shock_mr_costed_oos.py`).
  - Summary 2c53cb5480ab95eaa2267a29c14fee85a03be94f46ce17d5fb8b7f277bd56ab1 (`reports/campaign211_execution_summary_20261108T122845Z.json`).
  - Distinctness grep 0 non-self at run (`RTE_OVER_L\b`). L = mean diagonal line length (LAVG, k>=1 excluding LOI), distinct from WAVG(C210), LMAX(C209), black-vertical LAVG(C208), VMAX(C207), TREND(C206), TT(C205).
- Single durable handoff = this file + `research_state/state.yaml`. Latest registry = `reports/strategy_edge_registry_20261108T122845Z.json` (2a0bb7b0cca78d9732b7ecf650b2611017bfcd17c9b16d6cfde71c5f44fceeda).

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **No status-first.** Artifacts on disk are the deliverable.
- **No reruns of locked campaigns C104–C211.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence in artifacts + state.
- **Heavy work mandatory.** No status-only replies. No stop between campaigns.

## C212 — NEXT FOCUS CAMPAIGN (PRESELECTED, GREP-ZERO VERIFIED 20261108T123055Z)
**Primary candidate:** `VOLUME_RQA_RTE_OVER_VAVG_RATIO_SHOCK_MR` — RQA ratio RTE/VAVG on delay-embedded log-volume returns (RTE = recurrence time entropy; VAVG = mean qualifying black vertical/laminar line length, vertical runs of 1s with run length >= l_min, columns; exclude trivial self context per implementation, be explicit). Distinct from L diagonal(C211), WAVG(C210), LMAX(C209), black-vertical LAVG naming concept collision-guarded by exact grep, VMAX(C207), TREND(C206), TT(C205), LAM(C204), DET(C203), ENTR(C202). Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,w_min=1,l_min=2`. Fail-closed NaN/no-signal if RTE/VAVG/ratio undefined/non-finite/degenerate or insufficient qualifying lines/gaps. Trailing/causal only.
**Fallbacks (verify at run):** `VOLUME_RQA_RTE_OVER_WMAX_RATIO_SHOCK_MR` (grep-zero 20261108T123055Z), `VOLUME_RQA_RTE_OVER_LVAR_RATIO_SHOCK_MR` (verify). Pick only a distinct grep-zero candidate not used C125–C211.

### COLLISION GUARD (RUN AT START)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_VAVG|rte_over_vavg' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self for chosen candidate
```
If collision found: pick a distinct grep-zero fallback not used C125–C211 (verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + `state.yaml`.

### REQUIRED C212 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_rte_over_vavg_ratio_shock_mr_costed_oos.py` (or collision-safe). Model on C188–C211. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T122845Z.json` (2a0bb7b0cca78d9732b7ecf650b2611017bfcd17c9b16d6cfde71c5f44fceeda), cite C211 OOS SHA `f987b29947f1a252c3a656315b89d6903fc0d6395d001b376bf5a63d2e68aa03`. Emit `reports/real_quote_volume_rqa_rte_over_vavg_ratio_shock_mr_costed_oos_<UTC>.json` with `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds. **No carryover template text**: campaign/refs/denominator labels must match RTE/VAVG.
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 212). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T122845Z.json` (2a0bb7b0...). Include prior + all C212 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign212_execution_summary_<UTC>.json` listing **all new C212 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C212`, `next_campaign: C213`, latest registry/OOS sha+path, `oos_edge_proven`, `c213_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C212, with grep cmd/hits/evidence). Update this `HANDOFF.md`.

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_VAVG|rte_over_vavg' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self
# NOW: implement+run C212 -> emit >=4 artifacts with SHAs -> sync state.yaml + HANDOFF
```

## C213 (AUTO-QUEUED, HEAVY)
After C212 complete and synced: preselect a **distinct grep-verified** RQA-ratio candidate not used C125–C212, record in `state.yaml.c213_preselected`, and **execute C213 immediately** under same template. No status-only replies. No stop between campaigns.
