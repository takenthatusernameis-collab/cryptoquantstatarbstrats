# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261108T091348Z, C203 DONE — C204 NOT DONE, EXECUTE IMMEDIATELY, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs [[0,0],[5,5],[10,10],[20,20],[40,40]], B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C203 LOCKED (no reruns). C204 preselected, grep-zero observed, not yet executed — no artifacts on disk.**

## TIMESTAMPED INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (20261108T091348Z)
**PRIORITY 1 (HEAVY WORK): EXECUTE C204 NOW.** C203 complete (VOLUME_RQA_RTE_OVER_DET_RATIO_SHOCK_MR, no edge: cross-asset net sums fee0=+0.7245817, fee5=+0.3585817, fee10=-0.0074183, fee20=-0.7394183, fee40=-2.2034183 — fails all-cost-slices-positive / B&H mean rule; `edge_claim:NONE`). **C204 artifacts do NOT yet exist on disk — do not summarize status. Do not stop at status. Implement + run + emit artifacts.**

Produce **>= 4 NEW concrete C204 artifacts on disk** with **SHA256 computed from bytes**:
1) OOS result JSON  2) Ingest attempt JSON (campaign 204)  3) Superseding strategy_edge_registry JSON  4) Campaign summary JSON listing every new artifact + its sha256. Also produce/update the OOS script and `research_state/state.yaml`.

## VERIFIED BASELINE (20261108T050324Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1). pytest 9.2.0 available.
- Caches: `data/cache/volume_1h_full.pkl/meta/provenance`, spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl`.
- C202 LOCKED: OOS 9992f000f7ba3514f7c3c8f192befcfb95979f161dbef1287334d18d3090d392 (`reports/real_quote_volume_rqa_rte_over_entr_ratio_shock_mr_costed_oos_20261108T044616Z.json`, VOLUME_RQA_RTE_OVER_ENTR_RATIO_SHOCK_MR, edge_claim NONE). Registry 78a5906062f4eabdcf88ea06107fb4d0bc0dea69095213f9e21a636d48db4eab supersedes C201 f85e6bf3d4cae044a1097887559961349955021906e34513e1b2eb7e2c7a388c.
- C203 LOCKED (verified on disk): OOS 30d5beb900963bb0fe840cfdef77adcadfaf980a9eb4a1e07c9d28621b979f42 (`reports/real_quote_volume_rqa_rte_over_det_ratio_shock_mr_costed_oos_20261108T045258Z.json`, VOLUME_RQA_RTE_OVER_DET_RATIO_SHOCK_MR, edge_claim NONE). Ingest e569dc850c0d0e8474b4c16db4c1611a71907cc03efcc07879396acd1ac625c8 (`reports/real_feed_ingest_attempt_20261108T045258Z.json`). Registry d9a3cfe58c9637cd2e5f466cb8389fd129398cf9ac0ffa2708a7baa4a06d62fb (`reports/strategy_edge_registry_20261108T045258Z.json`) supersedes C202 78a5906062f4eabdcf88ea06107fb4d0bc0dea69095213f9e21a636d48db4eab. Script a5a3b5c5d2ffd7504e0f7d08cc7cd04d81a704fe43da3eef9d3f1169f81c19df (`scripts/run_real_quote_volume_rqa_rte_over_det_ratio_shock_mr_costed_oos.py`). Summary 9b2ce415a367fed681a8e025692bafa4852b1d58991cd2d4968264c27e64bd1a (`reports/campaign203_execution_summary_20261108T045258Z.json`). SHAs verified from bytes.
- C203 cross-asset OOS net sums: fee0_slip0=0.7245816627743846, fee5_slip5=0.3585816627743843, fee10_slip10=-0.007418337225615801, fee20_slip20=-0.7394183372256157, fee40_slip40=-2.2034183372256155 → **edge NOT proven**.
- Single durable handoff = this file + `research_state/state.yaml`.

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **No status-first.** Artifacts on disk are the deliverable.
- **No reruns of locked campaigns C104–C203.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence in artifacts + state.
- **Heavy work mandatory.** Implement and run C204 now. No status-only replies. No stop between campaigns.

## C204 — PRIMARY CANDIDATE (PRESELECTED, GREP-ZERO OBSERVED 20261108T045258Z; RUN-TIME RE-VERIFY REQUIRED)
**Strategy:** `VOLUME_RQA_RTE_OVER_LAM_RATIO_SHOCK_MR`
**Feature (pre-stated):** RQA ratio RTE/LAM on delay-embedded log-volume returns
- `r_t = ln(v_t)-ln(v_{t-1})`, embedding `X_i=(r_i,r_{i+tau})`, `m=2,tau=1`, trailing `W_RR=168`, `eps = 0.5*std(r_window)`, L-inf
- `RTE` (numerator) = Recurrence Time Entropy = Shannon entropy (nats) of white vertical line length (recurrence-time gap) distribution: per column j, lengths w of consecutive zeros between recurrent points (excluding trivial self at i==j), qualifying `w>=w_min` with count `n_w>0`, `p_w=n_w/sum_u n_u`, `RTE = -sum_w p_w*ln(p_w)`. Fail-closed if `<2` distinct qualifying gap lengths or entropy non-finite/non-positive.
- `LAM` (denominator) = RQA laminarity = (sum of vertical line lengths `v>=v_min_lam` belonging to vertical structures) / (sum of all off-diagonal recurrent points) in the trailing window. Fail-closed if denominator <= 0, LAM non-finite, or LAM <= 0.
- `RATIO_RTE_LAM = RTE / LAM`. Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,w_min=1,v_min_lam=2`.
- Fail-closed NaN/no-signal if RTE/LAM/ratio undefined/non-finite/degenerate or insufficient qualifying lines/gaps. Trailing/causal only.
**Distinctness:** Not used C125–C203. Grep `grep -rnE 'RTE_OVER_LAM|rte_over_lam|rqa_ratio_rte_over_lam|rqa_rte_over_lam_ratio' scripts/ strategies/ backtest/ utils/` returned **0 hits (20261108T045258Z)**. **Re-verify 0 non-self at run time before implementation.** (Ineligible: RTE_OVER_RR 11 hits; LAM_OVER_RTE used C199 is a different pairing — RTE/LAM pairing not used C125–C203.)
**Fallbacks (grep-zero observed 20261108T045258Z; verify at run):** `VOLUME_RQA_RTE_OVER_TT_RATIO_SHOCK_MR`, `VOLUME_RQA_RTE_OVER_TREND_RATIO_SHOCK_MR`, `VOLUME_RQA_RTE_OVER_VMAX_RATIO_SHOCK_MR` (each grep returned 0). Pick only a distinct grep-zero RQA-ratio candidate not used C125–C204.

### Collision guard (RUN AT START)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rnE 'RTE_OVER_LAM|rte_over_lam|rqa_ratio_rte_over_lam|rqa_rte_over_lam_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self
```
If collision found: pick a distinct grep-zero fallback (TT/TREND/VMAX above) not used C125–C204 (verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + `state.yaml`.

## REQUIRED C204 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_rte_over_lam_ratio_shock_mr_costed_oos.py` (or collision-safe). Model after C188–C203. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T045258Z.json` (d9a3cfe58c9637cd2e5f466cb8389fd129398cf9ac0ffa2708a7baa4a06d62fb), cite C203 OOS SHA `30d5beb900963bb0fe840cfdef77adcadfaf980a9eb4a1e07c9d28621b979f42`. Emit `reports/real_quote_volume_rqa_rte_over_lam_ratio_shock_mr_costed_oos_<UTC>.json` with required fields incl `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds.
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 204). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T045258Z.json` (d9a3cfe58c9637cd2e5f466cb8389fd129398cf9ac0ffa2708a7baa4a06d62fb). Include prior + all C204 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign204_execution_summary_<UTC>.json` listing **all new C204 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C204`, `next_campaign: C205`, latest registry/OOS sha+path, `oos_edge_proven`, `c205_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C204, with grep cmd/hits/evidence).

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_LAM|rte_over_lam|rqa_ratio_rte_over_lam|rqa_rte_over_lam_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self
# NOW: implement+run C204 -> emit >=4 artifacts with SHAs -> sync state.yaml + HANDOFF
```

## NEXT FOCUS CAMPAIGN — C205 (AUTO-QUEUED, HEAVY)
After C204 complete and synced: preselect **distinct grep-verified** RQA-ratio candidate not used C125–C204 (verify; RTE_OVER_RR remains ineligible at 11 hits unless rechecked zero). Record in `state.yaml.c205_preselected` and **execute C205 immediately** under same template. No status-only replies. No stop between campaigns.
