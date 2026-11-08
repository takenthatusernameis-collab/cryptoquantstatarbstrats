# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261108T035016Z, C199 MANDATORY — EXECUTE IMMEDIATELY, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs [[0,0],[5,5],[10,10],[20,20],[40,40]], B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C198 LOCKED.**

## TIMESTAMPED INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (20261108T035016Z)
**PRIORITY 1 (HEAVY WORK): EXECUTE C199 NOW.** C198 complete (TT_OVER_DIV, no edge: net sums negative at fee5_slip5 through fee40_slip40). **No C199 artifacts exist. Do not summarize. Do not stop at status. Implement + run + emit artifacts.**

You must produce **>= 4 NEW concrete C199 artifacts on disk** with **SHA256 computed from bytes**:
1) OOS result JSON for the new strategy
2) Ingest attempt JSON (campaign 199)
3) Superseding strategy_edge_registry JSON
4) Campaign summary JSON listing every new artifact + its sha256

Also produce/update: the OOS script and `research_state/state.yaml`.

## VERIFIED BASELINE (20261108T035016Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1). pytest 9.2.0 available.
- Caches: `data/cache/volume_1h_full.pkl/meta/provenance`, spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl`
- C198 LOCKED (verified by this session): OOS b724cc55140e72bfd389ec4222ce7b36d670c4997ff17e7244d114d393c12b95 (`reports/real_quote_volume_rqa_tt_over_div_ratio_shock_mr_costed_oos_20261108T035016Z.json`, VOLUME_RQA_TT_OVER_DIV_RATIO_SHOCK_MR, edge_claim NONE). Ingest 753c9f5d1e999030a3eb2dfb4cd2d04551bdadf33b3c25219f3b4124b5fc7622. Registry 2a3eace23f2f877fb076bf3c579959776b466ab63ee30765047d56d1e3656830 supersedes C197. Script d5f14a16fe6ea1937d15b00da591d7ed7a40fd7a8af1de4925744cdcc034b03d. Summary 6b6084c0296e3e1463522c2b43d922f61eb831f8180d1bcd926a1cba620a29b0.
- C198 cross-asset OOS net sums: fee0_slip0=0.07880244662796365, fee5_slip5=-0.3411975533720367, fee10_slip10=-0.7611975533720368, fee20_slip20=-1.6011975533720366, fee40_slip40=-3.281197553372037 → **edge NOT proven** (negative at fee5+).
- Single durable handoff = this file + `research_state/state.yaml`.

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **No status-first.** Status is not deliverable. Artifacts on disk are deliverable.
- **No reruns of locked campaigns.** C104–C198 locked with byte SHAs.
- **No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.**
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Must grep-verify candidate before implementation/run and record evidence in artifacts+state.
- **Heavy work mandatory.** If tempted to stop after analysis, implement and run C199 now.

## C199 — PRIMARY CANDIDATE (PRESELECTED, GREP-ZERO OBSERVED 20261108T035016Z)
**Strategy:** `VOLUME_RQA_LAM_OVER_RTE_RATIO_SHOCK_MR`
**Feature (pre-stated):** RQA ratio LAM/RTE on delay-embedded log-volume returns
- `r_t = ln(v_t)-ln(v_{t-1})`, embedding `X_i=(r_i,r_{i+tau})`, `m=2,tau=1`, trailing `W_RR=168`, `eps = 0.5*std(r_window)`, L-inf
- `LAM` = laminarity = (sum of vertical line lengths `l>=l_min`) / `sum(R)` (standard RQA LAM; main-diagonal convention consistent with implementation; fail-closed if `sum(R)<=0` or degenerate).
- `RTE` = Recurrence Time Entropy = Shannon entropy (nats) of white vertical line length (recurrence-time gap) distribution: for each column j, lengths w of consecutive zeros between recurrent points (excluding trivial self at i==j), qualifying `w>=w_min` with count `n_w>0`, `p_w=n_w/sum_u n_u`, `RTE = -sum_w p_w*ln(p_w)`.
- `RATIO_LAM_RTE = LAM/RTE`. `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2,w_min=1`.
- Fail-closed NaN/no-signal if LAM undefined/non-finite/degenerate, RTE undefined/non-finite/degenerate (`<2` distinct qualifying gap lengths or entropy non-finite/non-positive), ratio non-finite, or insufficient qualifying lines/gaps. Trailing/causal only.
**Distinctness:** Not used C125–C198 (LAM/RTE pairing novel). Grep 0 observed 20261108T035016Z (`LAM_OVER_RTE` patterns over scripts/strategies/backtest/utils) — **re-verify at run time before implementation**.
**Fallbacks (grep 0 observed 20261108T035016Z):** `VOLUME_RQA_DET_OVER_RTE_RATIO_SHOCK_MR`, `VOLUME_RQA_ENTR_OVER_RTE_RATIO_SHOCK_MR`. `LAM_OVER_ENTR` collides (do not use).

### Collision guard (RUN AT START)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rnE 'LAM_OVER_RTE|lam_over_rte|rqa_ratio_lam_over_rte|rqa_lam_over_rte_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self
```
If collision found: pick a grep-zero fallback not used C125–C198 (DET_OVER_RTE, ENTR_OVER_RTE — verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + `state.yaml`.

## REQUIRED C199 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_lam_over_rte_ratio_shock_mr_costed_oos.py` (or collision-safe). Model after C188–C198. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T035016Z.json` (2a3eace23f2f877fb076bf3c579959776b466ab63ee30765047d56d1e3656830), cite C198 OOS SHA `b724cc55140e72bfd389ec4222ce7b36d670c4997ff17e7244d114d393c12b95`. Emit `reports/real_quote_volume_rqa_lam_over_rte_ratio_shock_mr_costed_oos_<UTC>.json` with `strategy_id`, `candidate`, `feature_definition`, `pre_stated_distinctness{grep_cmd,hits,verified_utc,evidence}`, `real_data_only:true`, `fail_closed:true`, `data{spot_cache,spot_cache_sha256,...,volume_loader_report}`, `params`, `references`, `per_asset`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_rule`, `edge_claim:"NONE"` unless rule holds.
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 199). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T035016Z.json` (2a3eace23f2f877fb076bf3c579959776b466ab63ee30765047d56d1e3656830). Include prior + all C199 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign199_execution_summary_<UTC>.json` listing **all new C199 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C199`, `next_campaign: C200`, latest registry/OOS sha+path, `oos_edge_proven`, `c200_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C199, with grep cmd/hits/evidence).

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.meta.json data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rnE 'LAM_OVER_RTE|lam_over_rte|rqa_ratio_lam_over_rte|rqa_lam_over_rte_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self
# NOW: implement+run C199 -> emit >=4 artifacts with SHAs -> sync state.yaml
```

## NEXT FOCUS CAMPAIGN — C200 (AUTO-QUEUED, HEAVY)
After C199 complete and synced: preselect **distinct grep-verified** RQA-ratio candidate not used C125–C199 (grep 0 non-self). Candidates to check: DET_OVER_RTE, ENTR_OVER_RTE, or other novel pairings (verify each). Record in `state.yaml.c200_preselected` with grep cmd/hits/evidence and **execute C200 immediately** under same template. No status-only replies. No stop between campaigns.
