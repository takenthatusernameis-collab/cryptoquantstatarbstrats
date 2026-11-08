# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261108T035536Z, C200 MANDATORY — EXECUTE IMMEDIATELY, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs [[0,0],[5,5],[10,10],[20,20],[40,40]], B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C199 LOCKED.**

## TIMESTAMPED INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (20261108T035536Z)
**PRIORITY 1 (HEAVY WORK): EXECUTE C200 NOW.** C199 complete (LAM_OVER_RTE, no edge: all cost-slice net sums negative). **No C200 artifacts exist. Do not summarize. Do not stop at status. Implement + run + emit artifacts.**

Produce **>= 4 NEW concrete C200 artifacts on disk** with **SHA256 computed from bytes**:
1) OOS result JSON  2) Ingest attempt JSON (campaign 200)  3) Superseding strategy_edge_registry JSON  4) Campaign summary JSON listing every new artifact + its sha256.  Also produce/update the OOS script and `research_state/state.yaml`.

## VERIFIED BASELINE (20261108T035536Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1). pytest 9.2.0 available.
- Caches: `data/cache/volume_1h_full.pkl/meta/provenance` (4365895387de/4d321584d3c6/c7ff2f27ec5a), spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` (5607573327c0).
- C199 LOCKED (this session): OOS 71ebc9ce4071f552ee0c4d75535059d2289e7369d055de84c838b35aeb2d798e (`reports/real_quote_volume_rqa_lam_over_rte_ratio_shock_mr_costed_oos_20261108T035536Z.json`, VOLUME_RQA_LAM_OVER_RTE_RATIO_SHOCK_MR, edge_claim NONE). Ingest 70912f43d4fd7d21c1b5925cde5d271468bc7c49678e172b259fc199c14904bc. Registry 12ee3349bbe59ec258d925f73a41ece80069c06ab45bbf7010b14a4e113a843f supersedes C198 2a3eace23f2f877fb076bf3c579959776b466ab63ee30765047d56d1e3656830. Script d93f667558c1e5fb489eed2c381124a4c3fa217f37e7e6e97a91e74e82ff4f28. Summary ab649b06f4a34e6d0387ffa87c0e7b0d4b37e272aba81c652751db2a2d1d0c2f.
- C199 cross-asset OOS net sums: fee0_slip0=-0.4628169730475371, fee5_slip5=-0.7518169730475374, fee10_slip10=-1.0408169730475374, fee20_slip20=-1.6188169730475375, fee40_slip40=-2.774816973047537 → **edge NOT proven**.
- Single durable handoff = this file + `research_state/state.yaml`.

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **No status-first.** Artifacts on disk are deliverable.
- **No reruns of locked campaigns C104–C199.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence in artifacts+state.
- **Heavy work mandatory.** Implement and run C200 now.

## C200 — PRIMARY CANDIDATE (PRESELECTED, GREP-ZERO OBSERVED 20261108T035536Z)
**Strategy:** `VOLUME_RQA_DET_OVER_RTE_RATIO_SHOCK_MR`
**Feature (pre-stated):** RQA ratio DET/RTE on delay-embedded log-volume returns
- `r_t = ln(v_t)-ln(v_{t-1})`, embedding `X_i=(r_i,r_{i+tau})`, `m=2,tau=1`, trailing `W_RR=168`, `eps = 0.5*std(r_window)`, L-inf
- `DET` = determinism = (sum of diagonal line lengths `l>=l_min`) / `sum(R)` (standard RQA DET). Fail-closed if `sum(R)<=0` or DET not in `(0,1]`.
- `RTE` = Recurrence Time Entropy = Shannon entropy (nats) of white vertical line length (recurrence-time gap) distribution: per column j, lengths w of consecutive zeros between recurrent points (excluding trivial self at i==j), qualifying `w>=w_min` with count `n_w>0`, `p_w=n_w/sum_u n_u`, `RTE = -sum_w p_w*ln(p_w)`. Fail-closed if `<2` distinct qualifying gap lengths or entropy non-finite/non-positive.
- `RATIO_DET_RTE = DET/RTE`. `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2,w_min=1`.
- Fail-closed NaN/no-signal if DET/RTE/ratio undefined/non-finite/degenerate or insufficient qualifying lines/gaps. Trailing/causal only.
**Distinctness:** Not used C125–C199 (LAM_OVER_RTE used C199; DET_OVER_RTE novel). Grep 0 observed 20261108T035536Z — **re-verify at run time before implementation**.
**Fallbacks (grep 0 observed 20261108T035536Z):** `VOLUME_RQA_ENTR_OVER_RTE_RATIO_SHOCK_MR`. `LAM_OVER_ENTR` collides (do not use).

### Collision guard (RUN AT START)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rnE 'DET_OVER_RTE|det_over_rte|rqa_ratio_det_over_rte|rqa_det_over_rte_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self
```
If collision found: pick grep-zero `ENTR_OVER_RTE` (verify) or another novel RQA-ratio not used C125–C199. Record chosen feature + grep cmd/hits/evidence in all artifacts + `state.yaml`.

## REQUIRED C200 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_det_over_rte_ratio_shock_mr_costed_oos.py` (or collision-safe). Model after C188–C199. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T035536Z.json` (12ee3349bbe59ec258d925f73a41ece80069c06ab45bbf7010b14a4e113a843f), cite C199 OOS SHA `71ebc9ce4071f552ee0c4d75535059d2289e7369d055de84c838b35aeb2d798e`. Emit `reports/real_quote_volume_rqa_det_over_rte_ratio_shock_mr_costed_oos_<UTC>.json` with required fields incl `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds.
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 200). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T035536Z.json` (12ee3349bbe59ec258d925f73a41ece80069c06ab45bbf7010b14a4e113a843f). Include prior + all C200 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign200_execution_summary_<UTC>.json` listing **all new C200 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C200`, `next_campaign: C201`, latest registry/OOS sha+path, `oos_edge_proven`, `c201_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C200, with grep cmd/hits/evidence).

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'DET_OVER_RTE|det_over_rte|rqa_ratio_det_over_rte|rqa_det_over_rte_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self
# NOW: implement+run C200 -> emit >=4 artifacts with SHAs -> sync state.yaml
```

## NEXT FOCUS CAMPAIGN — C201 (AUTO-QUEUED, HEAVY)
After C200 complete and synced: preselect **distinct grep-verified** RQA-ratio candidate not used C125–C200 (`ENTR_OVER_RTE` if still zero, or other novel pairing — verify). Record in `state.yaml.c201_preselected` and **execute C201 immediately** under same template. No status-only replies. No stop between campaigns.
