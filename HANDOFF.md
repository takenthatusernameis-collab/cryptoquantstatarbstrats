# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261108T040028Z, C201 MANDATORY — EXECUTE IMMEDIATELY, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs [[0,0],[5,5],[10,10],[20,20],[40,40]], B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C200 LOCKED.**

## TIMESTAMPED INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (20261108T040028Z)
**PRIORITY 1 (HEAVY WORK): EXECUTE C201 NOW.** C200 complete (DET_OVER_RTE, no edge: all cost-slice net sums negative). **No C201 artifacts exist. Do not summarize. Do not stop at status. Implement + run + emit artifacts.**

Produce **>= 4 NEW concrete C201 artifacts on disk** with **SHA256 computed from bytes**:
1) OOS result JSON  2) Ingest attempt JSON (campaign 201)  3) Superseding strategy_edge_registry JSON  4) Campaign summary JSON listing every new artifact + its sha256.  Also produce/update the OOS script and `research_state/state.yaml`.

## VERIFIED BASELINE (20261108T040028Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1). pytest 9.2.0 available.
- Caches: `data/cache/volume_1h_full.pkl/meta/provenance` (4365895387de/4d321584d3c6/c7ff2f27ec5a), spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` (5607573327c0).
- C200 LOCKED (this session): OOS dba56c09c695278b78ea451c17d4dff35c82bbb283f505b18b03560802bef35e (`reports/real_quote_volume_rqa_det_over_rte_ratio_shock_mr_costed_oos_20261108T040028Z.json`, VOLUME_RQA_DET_OVER_RTE_RATIO_SHOCK_MR, edge_claim NONE). Ingest c6ffe4b2d7239ac6231653e14b1fba3052e3280f3897bd07b7f2f70e1caf864b. Registry 2273f16a9e39fb7b6e3c495a4eba0040e307fc9a9599094d3c913987f8e55799 supersedes C199 12ee3349bbe59ec258d925f73a41ece80069c06ab45bbf7010b14a4e113a843f. Script 1b86dcc884c8a3b5ead3cee4c21d87bf0743c11d9df038e1c2f46c781fab6ed3. Summary c6dfd57d5a9fb3d8f95d5e17165bcf92275576f12914d06896f6b7f495e43094.
- C200 cross-asset OOS net sums: fee0_slip0=-0.527800647949167, fee5_slip5=-0.9138006479491674, fee10_slip10=-1.2998006479491675, fee20_slip20=-2.0718006479491673, fee40_slip40=-3.6158006479491673 → **edge NOT proven**.
- Single durable handoff = this file + `research_state/state.yaml`.

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **No status-first.** Artifacts on disk are deliverable.
- **No reruns of locked campaigns C104–C200.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence in artifacts+state.
- **Heavy work mandatory.** Implement and run C201 now.

## C201 — PRIMARY CANDIDATE (PRESELECTED, GREP-ZERO OBSERVED 20261108T040028Z)
**Strategy:** `VOLUME_RQA_ENTR_OVER_RTE_RATIO_SHOCK_MR`
**Feature (pre-stated):** RQA ratio ENTR/RTE on delay-embedded log-volume returns
- `r_t = ln(v_t)-ln(v_{t-1})`, embedding `X_i=(r_i,r_{i+tau})`, `m=2,tau=1`, trailing `W_RR=168`, `eps = 0.5*std(r_window)`, L-inf
- `ENTR` = Shannon entropy (nats) of diagonal line length distribution (standard RQA ENTR): qualifying diagonal lengths `l>=l_min` (upper-triangle diagonals k>=1, symmetric as appropriate), `P(l)=n_l/sum_u n_u`, `ENTR=-sum_l P(l)*ln(P(l))`. Fail-closed if `<2` distinct qualifying diagonal lengths or ENTR non-finite/non-positive.
- `RTE` = Recurrence Time Entropy = Shannon entropy (nats) of white vertical line length (recurrence-time gap) distribution: per column j, lengths w of consecutive zeros between recurrent points (excluding trivial self at i==j), qualifying `w>=w_min` with count `n_w>0`, `p_w=n_w/sum_u n_u`, `RTE = -sum_w p_w*ln(p_w)`. Fail-closed if `<2` distinct qualifying gap lengths or entropy non-finite/non-positive.
- `RATIO_ENTR_RTE = ENTR/RTE`. `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2,w_min=1`.
- Fail-closed NaN/no-signal if ENTR/RTE/ratio undefined/non-finite/degenerate or insufficient qualifying lines/gaps. Trailing/causal only.
**Distinctness:** Not used C125–C200 (DET_OVER_RTE used C200). Grep 0 observed 20261108T040028Z — **re-verify at run time before implementation**.
**Fallbacks (grep unverified / verify at run):** `VOLUME_RQA_RR_OVER_ENTR_RATIO_SHOCK_MR`.

### Collision guard (RUN AT START)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rnE 'ENTR_OVER_RTE|entr_over_rte|rqa_ratio_entr_over_rte|rqa_entr_over_rte_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self
```
If collision found: pick a distinct grep-zero RQA-ratio candidate not used C125–C200 (verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + `state.yaml`.

## REQUIRED C201 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_entr_over_rte_ratio_shock_mr_costed_oos.py` (or collision-safe). Model after C188–C200. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T040028Z.json` (2273f16a9e39fb7b6e3c495a4eba0040e307fc9a9599094d3c913987f8e55799), cite C200 OOS SHA `dba56c09c695278b78ea451c17d4dff35c82bbb283f505b18b03560802bef35e`. Emit `reports/real_quote_volume_rqa_entr_over_rte_ratio_shock_mr_costed_oos_<UTC>.json` with required fields incl `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds.
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 201). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T040028Z.json` (2273f16a9e39fb7b6e3c495a4eba0040e307fc9a9599094d3c913987f8e55799). Include prior + all C201 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign201_execution_summary_<UTC>.json` listing **all new C201 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C201`, `next_campaign: C202`, latest registry/OOS sha+path, `oos_edge_proven`, `c202_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C201, with grep cmd/hits/evidence).

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'ENTR_OVER_RTE|entr_over_rte|rqa_ratio_entr_over_rte|rqa_entr_over_rte_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self
# NOW: implement+run C201 -> emit >=4 artifacts with SHAs -> sync state.yaml
```

## NEXT FOCUS CAMPAIGN — C202 (AUTO-QUEUED, HEAVY)
After C201 complete and synced: preselect **distinct grep-verified** RQA-ratio candidate not used C125–C201 (verify). Record in `state.yaml.c202_preselected` and **execute C202 immediately** under same template. No status-only replies. No stop between campaigns.
