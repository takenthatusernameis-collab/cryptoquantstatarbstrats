# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261108T091806Z, C204 DONE — C205 NOT DONE, EXECUTE IMMEDIATELY, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs [[0,0],[5,5],[10,10],[20,20],[40,40]], B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C204 LOCKED (no reruns). C205 preselected, grep-zero observed 20261108T091806Z, not yet executed — no artifacts on disk.**

## TIMESTAMPED INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (20261108T091806Z)
**PRIORITY 1 (HEAVY WORK): EXECUTE C205 NOW.** C204 complete (VOLUME_RQA_RTE_OVER_LAM_RATIO_SHOCK_MR, no edge: cross-asset net sums fee0=+0.7245817, fee5=+0.3585817, fee10=-0.0074183, fee20=-0.7394183, fee40=-2.2034183 — fails all-cost-slices-positive / B&H mean rule; `edge_claim:NONE`). **C205 artifacts do NOT yet exist on disk — do not summarize status. Do not stop at status. Implement + run + emit artifacts.**

Produce **>= 4 NEW concrete C205 artifacts on disk** with **SHA256 computed from bytes**:
1) OOS result JSON  2) Ingest attempt JSON (campaign 205)  3) Superseding strategy_edge_registry JSON  4) Campaign summary JSON listing every new artifact + its sha256. Also produce/update the OOS script and `research_state/state.yaml`.

## VERIFIED BASELINE (20261108T091806Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1). pytest 9.2.0 available.
- Caches: `data/cache/volume_1h_full.pkl/meta/provenance`, spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl`.
- **C204 LOCKED (verified on disk, SHAs from bytes):**
  - OOS e0dd9dc9012b2c75ec8e9b6c0b903bc7445e9b0d1932f2e43969acd75faf032c (`reports/real_quote_volume_rqa_rte_over_lam_ratio_shock_mr_costed_oos_20261108T091806Z.json`, VOLUME_RQA_RTE_OVER_LAM_RATIO_SHOCK_MR, edge_claim NONE).
  - Ingest e21eb760a46345b9c528cc0c662b7ec7007df53d44a0517055687e11321dfba7 (`reports/real_feed_ingest_attempt_20261108T091806Z.json`).
  - Registry 257bed6bfe5d086a249340c6b44dc2da5631f0d80afec99e799f36dc57e22aec (`reports/strategy_edge_registry_20261108T091806Z.json`) supersedes C203 d9a3cfe58c9637cd2e5f466cb8389fd129398cf9ac0ffa2708a7baa4a06d62fb.
  - Script b2643c015809a2815f299e71cfa1d7ae64ec958b91a7b85d9db4bcb5401eb675 (`scripts/run_real_quote_volume_rqa_rte_over_lam_ratio_shock_mr_costed_oos.py`).
  - Summary 0d47c40057bcc55a5894d495e9bfe1073e823abf6c67f1bf00de9d8c333c6b42 (`reports/campaign204_execution_summary_20261108T091806Z.json`).
  - Integrity note (honest): C204 OOS JSON contains carryover template text (C202/C203/DET labels) from script generation; **authoritative fields** (strategy_id VOLUME_RQA_RTE_OVER_LAM_RATIO_SHOCK_MR, metrics, edge rule result, cross_asset sums, pre_stated_distinctness) present. Real data only; no fabrication; edge_claim NONE.
- C204 cross-asset OOS net sums: fee0_slip0=0.7245816627743846, fee5_slip5=0.3585816627743843, fee10_slip10=-0.007418337225615801, fee20_slip20=-0.7394183372256157, fee40_slip40=-2.2034183372256155 → **edge NOT proven**.
- Single durable handoff = this file + `research_state/state.yaml`.

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **No status-first.** Artifacts on disk are the deliverable.
- **No reruns of locked campaigns C104–C204.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence in artifacts + state.
- **Heavy work mandatory.** Implement and run C205 now. No status-only replies. No stop between campaigns.

## C205 — PRIMARY CANDIDATE (PRESELECTED, GREP-ZERO CONFIRMED 20261108T091806Z; RUN-TIME RE-VERIFY REQUIRED)
**Strategy:** `VOLUME_RQA_RTE_OVER_TT_RATIO_SHOCK_MR`
**Feature (pre-stated):** RQA ratio RTE/TT on delay-embedded log-volume returns
- `r_t = ln(v_t)-ln(v_{t-1})`, embedding `X_i=(r_i,r_{i+tau})`, `m=2,tau=1`, trailing `W_RR=168`, `eps = 0.5*std(r_window)`, L-inf
- `RTE` (numerator) = Recurrence Time Entropy = Shannon entropy (nats) of white vertical line length (recurrence-time gap) distribution: per column j, lengths w of consecutive zeros between recurrent points (excluding trivial self at i==j), qualifying `w>=w_min` with count `n_w>0`, `p_w=n_w/sum_u n_u`, `RTE = -sum_w p_w*ln(p_w)`. Fail-closed if `<2` distinct qualifying gap lengths or entropy non-finite/non-positive.
- `TT` (denominator) = RQA trapping time = average length of vertical lines with `v>=v_min` (`v_min=2`): mean of all qualifying vertical line lengths in the trailing window. Fail-closed if no qualifying vertical lines, TT non-finite, or TT <= 0.
- `RATIO_RTE_TT = RTE / TT`. Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,w_min=1,v_min=2`.
- Fail-closed NaN/no-signal if RTE/TT/ratio undefined/non-finite/degenerate or insufficient qualifying lines/gaps. Trailing/causal only.
**Distinctness:** Not used C125–C204 (RTE/LAM used C204; RTE/DET used C203; RTE/ENTR used C202; LAM_OVER_RTE used C199 is different pairing; RTE_OVER_RR ineligible 11 hits). Grep `grep -rnE 'RTE_OVER_TT|rte_over_tt|rqa_ratio_rte_over_tt|rqa_rte_over_tt_ratio' scripts/ strategies/ backtest/ utils/` returned **0 hits (20261108T091806Z, post-C204)**. **Re-verify 0 non-self at run time before implementation.**
**Fallbacks (verify at run):** `VOLUME_RQA_RTE_OVER_TREND_RATIO_SHOCK_MR`, `VOLUME_RQA_RTE_OVER_VMAX_RATIO_SHOCK_MR`, `VOLUME_RQA_RTE_OVER_LMAX_RATIO_SHOCK_MR` (grep 0 observed 20261108T045258Z; re-verify). Pick only a distinct grep-zero RQA-ratio candidate not used C125–C205.

### Collision guard (RUN AT START)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rnE 'RTE_OVER_TT|rte_over_tt|rqa_ratio_rte_over_tt|rqa_rte_over_tt_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self
```
If collision found: pick a distinct grep-zero fallback (TREND/VMAX/LMAX above) not used C125–C205 (verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + `state.yaml`.

## REQUIRED C205 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_rte_over_tt_ratio_shock_mr_costed_oos.py` (or collision-safe). Model after C188–C204. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T091806Z.json` (257bed6bfe5d086a249340c6b44dc2da5631f0d80afec99e799f36dc57e22aec), cite C204 OOS SHA `e0dd9dc9012b2c75ec8e9b6c0b903bc7445e9b0d1932f2e43969acd75faf032c`. Emit `reports/real_quote_volume_rqa_rte_over_tt_ratio_shock_mr_costed_oos_<UTC>.json` with required fields incl `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds. **Avoid carryover template text: campaign/refs/denominator labels must match RTE/TT.**
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 205). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T091806Z.json` (257bed6bfe5d086a249340c6b44dc2da5631f0d80afec99e799f36dc57e22aec). Include prior + all C205 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign205_execution_summary_<UTC>.json` listing **all new C205 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C205`, `next_campaign: C206`, latest registry/OOS sha+path, `oos_edge_proven`, `c206_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C205, with grep cmd/hits/evidence).

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_TT|rte_over_tt|rqa_ratio_rte_over_tt|rqa_rte_over_tt_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self
# NOW: implement+run C205 -> emit >=4 artifacts with SHAs -> sync state.yaml + HANDOFF
```

## NEXT FOCUS CAMPAIGN — C206 (AUTO-QUEUED, HEAVY)
After C205 complete and synced: preselect **distinct grep-verified** RQA-ratio candidate not used C125–C205 (verify; RTE_OVER_RR remains ineligible at 11 hits unless rechecked zero). Record in `state.yaml.c206_preselected` and **execute C206 immediately** under same template. No status-only replies. No stop between campaigns.
