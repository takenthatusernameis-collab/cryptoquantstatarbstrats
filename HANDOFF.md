# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261108T044616Z, C202 DONE — C203 EXECUTE IMMEDIATELY, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs [[0,0],[5,5],[10,10],[20,20],[40,40]], B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C202 LOCKED.**

## TIMESTAMPED INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (20261108T044616Z)
**PRIORITY 1 (HEAVY WORK): EXECUTE C203 NOW.** C202 complete (VOLUME_RQA_RTE_OVER_ENTR_RATIO_SHOCK_MR, no edge: cross-asset net sums fee0=+0.7819749, fee5=+0.3689749, fee10=-0.0440251, fee20=-0.8700251, fee40=-2.5220251 — fails all-cost-slices-positive). **No C203 artifacts exist. Do not summarize. Do not stop at status. Implement + run + emit artifacts.**

Produce **>= 4 NEW concrete C203 artifacts on disk** with **SHA256 computed from bytes**:
1) OOS result JSON  2) Ingest attempt JSON (campaign 203)  3) Superseding strategy_edge_registry JSON  4) Campaign summary JSON listing every new artifact + its sha256.  Also produce/update the OOS script and `research_state/state.yaml`.

## VERIFIED BASELINE (20261108T044616Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1). pytest 9.2.0 available.
- Caches: `data/cache/volume_1h_full.pkl/meta/provenance`, spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl`.
- C201 LOCKED: OOS 7c60d462cb08337d3994f342e76a0fa8e99cb073f9e936e30bd4bb8f14e5253b (`reports/real_quote_volume_rqa_entr_over_rte_ratio_shock_mr_costed_oos_20261108T040927Z.json`, VOLUME_RQA_ENTR_OVER_RTE_RATIO_SHOCK_MR, edge_claim NONE). Registry f85e6bf3d4cae044a1097887559961349955021906e34513e1b2eb7e2c7a388c supersedes C200 2273f16a9e39fb7b6e3c495a4eba0040e307fc9a9599094d3c913987f8e55799.
- C202 LOCKED (this session): OOS 9992f000f7ba3514f7c3c8f192befcfb95979f161dbef1287334d18d3090d392 (`reports/real_quote_volume_rqa_rte_over_entr_ratio_shock_mr_costed_oos_20261108T044616Z.json`, VOLUME_RQA_RTE_OVER_ENTR_RATIO_SHOCK_MR, edge_claim NONE). Ingest f49f33cc7151f000e4680c18bc62678bb2649c9fc5d3e2e697385e80503503e4 (`reports/real_feed_ingest_attempt_20261108T044616Z.json`). Registry 78a5906062f4eabdcf88ea06107fb4d0bc0dea69095213f9e21a636d48db4eab (`reports/strategy_edge_registry_20261108T044616Z.json`) supersedes C201 f85e6bf3d4cae044a1097887559961349955021906e34513e1b2eb7e2c7a388c. Script af335b1f68a628359398ec558964846c9c0cdf8f595a46ed5b5006e6707aee0c (`scripts/run_real_quote_volume_rqa_rte_over_entr_ratio_shock_mr_costed_oos.py`). Summary 35ea747b377824eef81af229a2e94e379d84e24682f3b4b457fa6652d09859e9 (`reports/campaign202_execution_summary_20261108T044616Z.json`).
- C202 cross-asset OOS net sums: fee0_slip0=0.7819749231630726, fee5_slip5=0.36897492316307223, fee10_slip10=-0.044025076836927884, fee20_slip20=-0.8700250768369278, fee40_slip40=-2.5220250768369277 → **edge NOT proven** (fails all-cost-slices-positive and B&H-mean rule at higher costs).
- Single durable handoff = this file + `research_state/state.yaml`.

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **No status-first.** Artifacts on disk are deliverable.
- **No reruns of locked campaigns C104–C202.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence in artifacts+state.
- **Heavy work mandatory.** Implement and run C203 now.

## C203 — PRIMARY CANDIDATE (PRESELECTED, GREP-ZERO VERIFIED 20261108T044616Z)
**Strategy:** `VOLUME_RQA_RTE_OVER_DET_RATIO_SHOCK_MR`
**Feature (pre-stated):** RQA ratio RTE/DET on delay-embedded log-volume returns
- `r_t = ln(v_t)-ln(v_{t-1})`, embedding `X_i=(r_i,r_{i+tau})`, `m=2,tau=1`, trailing `W_RR=168`, `eps = 0.5*std(r_window)`, L-inf
- `RTE` (numerator) = Recurrence Time Entropy = Shannon entropy (nats) of white vertical line length (recurrence-time gap) distribution: per column j, lengths w of consecutive zeros between recurrent points (excluding trivial self at i==j), qualifying `w>=w_min` with count `n_w>0`, `p_w=n_w/sum_u n_u`, `RTE = -sum_w p_w*ln(p_w)`. Fail-closed if `<2` distinct qualifying gap lengths or entropy non-finite/non-positive.
- `DET` (denominator) = RQA determinism (standard) = (sum of recurrent points belonging to diagonal lines of length >= `l_min`) / (sum of all off-diagonal recurrent points) in the trailing window. Compute over upper-triangle diagonals k>=1 (symmetric; avoid double-counting; exclude main diagonal). Fail-closed if denominator <= 0, DET non-finite, or DET <= 0.
- `RATIO_RTE_DET = RTE / DET`. `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2,w_min=1`.
- Fail-closed NaN/no-signal if RTE/DET/ratio undefined/non-finite/degenerate or insufficient qualifying lines/gaps. Trailing/causal only.
**Distinctness:** Not used C125–C202. Grep `grep -rnE 'RTE_OVER_DET|rte_over_det|rqa_ratio_rte_over_det|rqa_rte_over_det_ratio' scripts/ strategies/ backtest/ utils/` returned **0 hits (20261108T044616Z)**. **Re-verify 0 non-self at run time before implementation.** (Ineligible alternatives observed nonzero: DET_OVER_ENTR 10, LAM_OVER_ENTR 10, ENTR_OVER_DET 10, TT_OVER_ENTR 14.)
**Fallbacks (grep unverified / verify at run):** pick any distinct grep-zero RQA-ratio candidate not used C125–C203.

### Collision guard (RUN AT START)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rnE 'RTE_OVER_DET|rte_over_det|rqa_ratio_rte_over_det|rqa_rte_over_det_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self
```
If collision found: pick a distinct grep-zero RQA-ratio candidate not used C125–C203 (verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + `state.yaml`.

## REQUIRED C203 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_rte_over_det_ratio_shock_mr_costed_oos.py` (or collision-safe). Model after C188–C202. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T044616Z.json` (78a5906062f4eabdcf88ea06107fb4d0bc0dea69095213f9e21a636d48db4eab), cite C202 OOS SHA `9992f000f7ba3514f7c3c8f192befcfb95979f161dbef1287334d18d3090d392`. Emit `reports/real_quote_volume_rqa_rte_over_det_ratio_shock_mr_costed_oos_<UTC>.json` with required fields incl `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds.
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 203). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T044616Z.json` (78a5906062f4eabdcf88ea06107fb4d0bc0dea69095213f9e21a636d48db4eab). Include prior + all C203 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign203_execution_summary_<UTC>.json` listing **all new C203 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C203`, `next_campaign: C204`, latest registry/OOS sha+path, `oos_edge_proven`, `c204_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C203, with grep cmd/hits/evidence).

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_DET|rte_over_det|rqa_ratio_rte_over_det|rqa_rte_over_det_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self
# NOW: implement+run C203 -> emit >=4 artifacts with SHAs -> sync state.yaml
```

## NEXT FOCUS CAMPAIGN — C204 (AUTO-QUEUED, HEAVY)
After C203 complete and synced: preselect **distinct grep-verified** RQA-ratio candidate not used C125–C203 (verify; candidates with prior grep hits ineligible until rechecked zero). Record in `state.yaml.c204_preselected` and **execute C204 immediately** under same template. No status-only replies. No stop between campaigns.
