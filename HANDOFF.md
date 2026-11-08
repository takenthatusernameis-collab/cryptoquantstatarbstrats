# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261108T040927Z, C201 DONE — C202 EXECUTE IMMEDIATELY, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs [[0,0],[5,5],[10,10],[20,20],[40,40]], B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C201 LOCKED.**

## TIMESTAMPED INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (20261108T040927Z)
**PRIORITY 1 (HEAVY WORK): EXECUTE C202 NOW.** C201 complete (VOLUME_RQA_ENTR_OVER_RTE_RATIO_SHOCK_MR, no edge: all cost-slice net sums negative). **No C202 artifacts exist. Do not summarize. Do not stop at status. Implement + run + emit artifacts.**

Produce **>= 4 NEW concrete C202 artifacts on disk** with **SHA256 computed from bytes**:
1) OOS result JSON  2) Ingest attempt JSON (campaign 202)  3) Superseding strategy_edge_registry JSON  4) Campaign summary JSON listing every new artifact + its sha256.  Also produce/update the OOS script and `research_state/state.yaml`.

## VERIFIED BASELINE (20261108T040927Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1). pytest 9.2.0 available.
- Caches: `data/cache/volume_1h_full.pkl/meta/provenance`, spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl`.
- C200 LOCKED: OOS dba56c09c695278b78ea451c17d4dff35c82bbb283f505b18b03560802bef35e (`reports/real_quote_volume_rqa_det_over_rte_ratio_shock_mr_costed_oos_20261108T040028Z.json`, VOLUME_RQA_DET_OVER_RTE_RATIO_SHOCK_MR, edge_claim NONE). Ingest c6ffe4b2d7239ac6231653e14b1fba3052e3280f3897bd07b7f2f70e1caf864b. Registry 2273f16a9e39fb7b6e3c495a4eba0040e307fc9a9599094d3c913987f8e55799 supersedes C199 12ee3349bbe59ec258d925f73a41ece80069c06ab45bbf7010b14a4e113a843f. Script 1b86dcc884c8a3b5ead3cee4c21d87bf0743c11d9df038e1c2f46c781fab6ed3. Summary c6dfd57d5a9fb3d8f95d5e17165bcf92275576f12914d06896f6b7f495e43094.
- C200 cross-asset OOS net sums: fee0_slip0=-0.527800647949167, fee5_slip5=-0.9138006479491674, fee10_slip10=-1.2998006479491675, fee20_slip20=-2.0718006479491673, fee40_slip40=-3.6158006479491673 → **edge NOT proven**.
- C201 LOCKED (this session): OOS 7c60d462cb08337d3994f342e76a0fa8e99cb073f9e936e30bd4bb8f14e5253b (`reports/real_quote_volume_rqa_entr_over_rte_ratio_shock_mr_costed_oos_20261108T040927Z.json`, VOLUME_RQA_ENTR_OVER_RTE_RATIO_SHOCK_MR, edge_claim NONE). Ingest 7cb0cf5ef12577eabbcfd7e1770183b26a705b6306a2db3cd34e07b75d188955 (`reports/real_feed_ingest_attempt_20261108T040927Z.json`). Registry f85e6bf3d4cae044a1097887559961349955021906e34513e1b2eb7e2c7a388c (`reports/strategy_edge_registry_20261108T040927Z.json`) supersedes C200 2273f16a.... Script fa65d9ada96bd172de1e29e359092d06d9d3b02baf00eec4de89792e6ac53dae (`scripts/run_real_quote_volume_rqa_entr_over_rte_ratio_shock_mr_costed_oos.py`). Summary f20926e0833191926f1b0cf1ba78cd41b96bc964ea4013ec291ad60770b9228c (`reports/campaign201_execution_summary_20261108T040927Z.json`).
- C201 cross-asset OOS net sums: fee0_slip0=-0.8040735287438145, fee5_slip5=-1.2290735287438148, fee10_slip10=-1.654073528743815, fee20_slip20=-2.504073528743815, fee40_slip40=-4.204073528743815 → **edge NOT proven**.
- Single durable handoff = this file + `research_state/state.yaml`.

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **No status-first.** Artifacts on disk are deliverable.
- **No reruns of locked campaigns C104–C201.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence in artifacts+state.
- **Heavy work mandatory.** Implement and run C202 now.

## C202 — PRIMARY CANDIDATE (PRESELECTED, GREP-ZERO OBSERVED 20261108T040927Z)
**Strategy:** `VOLUME_RQA_RTE_OVER_ENTR_RATIO_SHOCK_MR` (inverse numerator/denominator swap of C201 ENTR/RTE)
**Feature (pre-stated):** RQA ratio RTE/ENTR on delay-embedded log-volume returns
- `r_t = ln(v_t)-ln(v_{t-1})`, embedding `X_i=(r_i,r_{i+tau})`, `m=2,tau=1`, trailing `W_RR=168`, `eps = 0.5*std(r_window)`, L-inf
- `RTE` (numerator) = Recurrence Time Entropy = Shannon entropy (nats) of white vertical line length (recurrence-time gap) distribution: per column j, lengths w of consecutive zeros between recurrent points (excluding trivial self at i==j), qualifying `w>=w_min` with count `n_w>0`, `p_w=n_w/sum_u n_u`, `RTE = -sum_w p_w*ln(p_w)`. Fail-closed if `<2` distinct qualifying gap lengths or entropy non-finite/non-positive.
- `ENTR` (denominator) = Shannon entropy (nats) of diagonal line length distribution (standard RQA ENTR): qualifying diagonal lengths `l>=l_min` (upper-triangle diagonals k>=1, symmetric as appropriate), `P(l)=n_l/sum_u n_u`, `ENTR=-sum_l P(l)*ln(P(l))`. Fail-closed if `<2` distinct qualifying diagonal lengths or ENTR non-finite/non-positive.
- `RATIO_RTE_ENTR = RTE / ENTR`. `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2,w_min=1`.
- Fail-closed NaN/no-signal if RTE/ENTR/ratio undefined/non-finite/degenerate or insufficient qualifying lines/gaps. Trailing/causal only.
**Distinctness:** Not used C125–C201 (ENTR/OVER RTE used C201; DET/OVER RTE used C200; LAM/OVER RTE used C199). Grep 0 observed 20261108T040927Z — **re-verify at run time before implementation**.
**Fallbacks (grep unverified / verify at run):** pick any distinct grep-zero RQA-ratio candidate not used C125–C202. `VOLUME_RQA_RR_OVER_ENTR_RATIO_SHOCK_MR` is INELIGIBLE (nonzero grep; already implemented as C157-family script).

### Collision guard (RUN AT START)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rnE 'RTE_OVER_ENTR|rte_over_entr|rqa_ratio_rte_over_entr|rqa_rte_over_entr_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self
```
If collision found: pick a distinct grep-zero RQA-ratio candidate not used C125–C202 (verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + `state.yaml`.

## REQUIRED C202 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_rte_over_entr_ratio_shock_mr_costed_oos.py` (or collision-safe). Model after C188–C201. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T040927Z.json` (f85e6bf3d4cae044a1097887559961349955021906e34513e1b2eb7e2c7a388c), cite C201 OOS SHA `7c60d462cb08337d3994f342e76a0fa8e99cb073f9e936e30bd4bb8f14e5253b`. Emit `reports/real_quote_volume_rqa_rte_over_entr_ratio_shock_mr_costed_oos_<UTC>.json` with required fields incl `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds.
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 202). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T040927Z.json` (f85e6bf3d4cae044a1097887559961349955021906e34513e1b2eb7e2c7a388c). Include prior + all C202 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign202_execution_summary_<UTC>.json` listing **all new C202 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C202`, `next_campaign: C203`, latest registry/OOS sha+path, `oos_edge_proven`, `c203_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C202, with grep cmd/hits/evidence).

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_ENTR|rte_over_entr|rqa_ratio_rte_over_entr|rqa_rte_over_entr_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self
# NOW: implement+run C202 -> emit >=4 artifacts with SHAs -> sync state.yaml
```

## NEXT FOCUS CAMPAIGN — C203 (AUTO-QUEUED, HEAVY)
After C202 complete and synced: preselect **distinct grep-verified** RQA-ratio candidate not used C125–C202 (verify). Record in `state.yaml.c203_preselected` and **execute C203 immediately** under same template. No status-only replies. No stop between campaigns.
