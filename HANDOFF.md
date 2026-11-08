# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261108T034505Z, C198 MANDATORY — EXECUTE IMMEDIATELY, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs [[0,0],[5,5],[10,10],[20,20],[40,40]], B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C197 LOCKED.**

## TIMESTAMPED INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (20261108T034505Z)
**PRIORITY 1 (HEAVY WORK): EXECUTE C198 NOW.** C197 complete (RTE_OVER_DIV, no edge: net sums negative at fee20_slip20/fee40_slip40). **No C198 artifacts exist. Do not summarize. Do not stop at status. Implement + run + emit artifacts.**

You must produce **>= 4 NEW concrete C198 artifacts on disk** with **SHA256 computed from bytes**:
1) OOS result JSON for the new strategy
2) Ingest attempt JSON (campaign 198)
3) Superseding strategy_edge_registry JSON
4) Campaign summary JSON listing every new artifact + its sha256

Also produce/update: the OOS script and `research_state/state.yaml`.

## VERIFIED BASELINE (20261108T034505Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1). pytest 9.2.0 available.
- Caches: `data/cache/volume_1h_full.pkl/meta/provenance`, spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl`
- C197 LOCKED (verified): OOS 2cecf4d65ade16f4fe7688249622ccf0be1d271366e7fc1a89c84e8d47b2641b (VOLUME_RQA_RTE_OVER_DIV_RATIO_SHOCK_MR, edge_claim NONE). Ingest cf89c8e360a955c45abb2ea4059979ec9489db94216a981dcc3505e3e7733360. Registry cf71df3a31b6656bfef0cf6aa658f095758d8de9ec4491a0c570be267a314e2a supersedes C196. Script cc4c74eee754a9e3064eb511dd703344c7fada1869123c7c03a0b906aec1af8c. Summary 8c1fcbe6b4105fd90b78f1524f8987c8e176209477a3d41692a378cd2b35bb2b.
- C197 cross-asset OOS net sums: fee0_slip0=1.187570235678757, fee5_slip5=0.8555702356787565, fee10_slip10=0.5235702356787564, fee20_slip20=-0.1404297643212436, fee40_slip40=-1.4684297643212432 → **edge NOT proven** (negative at fee20+/fee40+).
- git clean at check time. Single durable handoff = this file + `research_state/state.yaml`.

## BOTTLENOCKETS REMOVED / MANDATES (NO EXCUSES)
- **No status-first.** Status is not deliverable. Artifacts on disk are deliverable.
- **No reruns of locked campaigns.** C104–C197 locked with byte SHAs.
- **No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.**
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Must grep-verify candidate before implementation/run and record evidence in artifacts+state.
- **Heavy work mandatory.** If tempted to stop after analysis, implement and run C198 now.

## C198 — PRIMARY CANDIDATE (PRESELECTED, GREP-ZERO CONFIRMED)
**Strategy:** `VOLUME_RQA_TT_OVER_DIV_RATIO_SHOCK_MR`
**Feature (pre-stated):** RQA ratio TT/DIV on delay-embedded log-volume returns
- `r_t = ln(v_t)-ln(v_{t-1})`, embedding `X_i=(r_i,r_{i+tau})`, `m=2,tau=1`, trailing `W_RR=168`, `eps = 0.5*std(r_window)`, L-inf
- `TT` = trapping time = mean of qualifying diagonal line lengths `k>=l_min` (mean line length over diagonal lines, excl LOI).
- `DIV` = divergence = `1/L_MAX` where `L_MAX` = max qualifying diagonal line length `k>=l_min` excl LOI.
- `RATIO_TT_DIV = TT/DIV = TT * L_MAX`. `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`.
- Fail-closed NaN/no-signal if TT undefined/non-finite/degenerate (non-positive), DIV/L_MAX invalid (no qualifying diagonal lines or `L_MAX<=0`/non-finite), ratio non-finite, or insufficient qualifying lines. Trailing/causal only.
**Distinctness:** Not used C125–C197 (TT/DIV pairing novel; denominators differ from all RTE/ENTR/LAM/DET pairings). Grep 0 observed 20261108T034505Z — **re-verify at run time before implementation**.

### Collision guard (RUN AT START)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rnE 'TT_OVER_DIV|tt_over_div|rqa_ratio_tt_over_div|rqa_tt_over_div_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self
```
If collision found: pick a grep-zero fallback not used C125–C197 (e.g., LAM_OVER_RTE, DET_OVER_RTE, ENTR_OVER_RTE — verify; LAM_OVER_ENTR collides). Record chosen feature + grep cmd/hits/evidence in all artifacts + `state.yaml`.

## REQUIRED C198 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_tt_over_div_ratio_shock_mr_costed_oos.py` (or collision-safe). Model after C188–C197. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T034505Z.json` (cf71df3a31b6656bfef0cf6aa658f095758d8de9ec4491a0c570be267a314e2a), cite C197 OOS SHA `2cecf4d65ade16f4fe7688249622ccf0be1d271366e7fc1a89c84e8d47b2641b`. Emit `reports/real_quote_volume_rqa_tt_over_div_ratio_shock_mr_costed_oos_<UTC>.json` with `strategy_id`, `candidate`, `feature_definition`, `pre_stated_distinctness{grep_cmd,hits,verified_utc,evidence}`, `real_data_only:true`, `fail_closed:true`, `data{spot_cache,spot_cache_sha256,...,volume_loader_report}`, `params`, `references`, `per_asset`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_rule`, `edge_claim:"NONE"` unless rule holds.
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 198). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T034505Z.json` (cf71df3a31b6656bfef0cf6aa658f095758d8de9ec4491a0c570be267a314e2a). Include prior + all C198 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign198_execution_summary_<UTC>.json` listing **all new C198 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C198`, `next_campaign: C199`, latest registry/OOS sha+path, `oos_edge_proven`, `c199_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C198, with grep cmd/hits/evidence).

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.meta.json data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rnE 'TT_OVER_DIV|tt_over_div|rqa_ratio_tt_over_div|rqa_tt_over_div_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self
# NOW: implement+run C198 -> emit >=4 artifacts with SHAs -> sync state.yaml
```

## NEXT FOCUS CAMPAIGN — C199 (AUTO-QUEUED, HEAVY)
After C198 complete and synced: preselect **distinct grep-verified** RQA-ratio candidate not used C125–C198 (grep 0 non-self). Candidates to check: LAM_OVER_RTE, DET_OVER_RTE, ENTR_OVER_RTE (LAM_OVER_ENTR collides). Record in `state.yaml.c199_preselected` with grep cmd/hits/evidence and **execute C199 immediately** under same template. No status-only replies. No stop between campaigns.
