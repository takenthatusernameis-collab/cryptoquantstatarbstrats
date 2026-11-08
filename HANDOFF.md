# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261108T030836Z, C197 MANDATORY — EXECUTE IMMEDIATELY, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs [[0,0],[5,5],[10,10],[20,20],[40,40]], B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C196 LOCKED.**

## TIMESTAMPED INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (20261108T030836Z)
**PRIORITY 1 (HEAVY WORK): EXECUTE C197 NOW.** No C197/RTE_OVER_DIV artifacts exist. **Do not summarize. Do not stop at status. Implement + run + emit artifacts.**

You must produce **>= 4 NEW concrete C197 artifacts on disk** with **SHA256 computed from bytes**:
1) OOS result JSON for the new strategy
2) Ingest attempt JSON (campaign 197)
3) Superseding strategy_edge_registry JSON
4) Campaign summary JSON listing every new artifact + its sha256

Also produce/update: the OOS script and `research_state/state.yaml`.

## VERIFIED BASELINE (20261108T030836Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1). pytest 9.2.0 available.
- Caches: `data/cache/volume_1h_full.pkl/meta/provenance`, spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl`
- C196 LOCKED (verified): OOS ffb28900b1750067cd8da2be960cf54c3b6c42a198741dc8e82bb9831825a256 (VOLUME_RQA_ENTR_OVER_DIV_RATIO_SHOCK_MR, edge_claim NONE). Ingest 2f7f297302086c1391949a2ff36ae031fed3f32bf8c21867218e23aeb92d1975. Registry 3daa1bd367829596e339ecd4956601142e96f24a5c1b0c92e70932b6f8f1d5fc supersedes C195. Script ceb12d8ad24a67bef28d1c06addbcbc426a3e9f773b6e29ba2ffedcc34720d3b. Summary 020533573586baed83a5e4b4a590c39f3cfa30965cec157fc8f1feead850a3de.
- C196 cross-asset OOS net sums: fee0_slip0=-0.5765044133311339, fee5_slip5=-1.0145044133311343, fee10_slip10=-1.4525044133311342, fee20_slip20=-2.3285044133311343, fee40_slip40=-4.080504413331134
- git clean at check time. Single durable handoff = this file + `research_state/state.yaml`.

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **No status-first.** Status is not deliverable. Artifacts on disk are deliverable.
- **No reruns of locked campaigns.** C104–C196 locked with byte SHAs.
- **No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.**
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Must grep-verify candidate before implementation/run and record evidence in artifacts+state.
- **Heavy work mandatory.** If tempted to stop after analysis, implement and run C197 now.

## C197 — PRIMARY CANDIDATE (PRESELECTED, GREP-ZERO CONFIRMED)
**Strategy:** `VOLUME_RQA_RTE_OVER_DIV_RATIO_SHOCK_MR`
**Feature (pre-stated):** RQA ratio RTE/DIV on delay-embedded log-volume returns
- `r_t = ln(v_t)-ln(v_{t-1})`, embedding `X_i=(r_i,r_{i+tau})`, `m=2,tau=1`, trailing `W_RR=168`, `eps = 0.5*std(r_window)`, L-inf
- `RTE` = Shannon entropy (nats) of **white vertical line length** (recurrence-time/gap) distribution from RP: for each column `j`, lengths `w` of consecutive zeros (vertical white gaps) between recurrent points (excluding trivial self). Collect `w>=w_min` (pre-stated `w_min=1`, all positive gaps), `n_w>0`, `p_w=n_w/sum_u n_u`, `RTE = -sum_w p_w*ln(p_w)`.
- `DIV` = divergence = `1/L_MAX` where `L_MAX` = max qualifying diagonal line length `k>=l_min` excl LOI.
- `RATIO_RTE_DIV = RTE/DIV`. `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2,w_min=1`.
**Fail-closed NaN/no-signal** if RTE undefined/non-finite/degenerate (<2 distinct qualifying gap lengths or entropy non-finite/non-positive), DIV/L_MAX invalid (no qualifying diagonal lines or `L_MAX<=0`/non-finite), ratio non-finite, or insufficient qualifying lines/gaps. Trailing/causal only.
**Distinctness:** Not used C125–C196 (C194 used RTE/other denominator RR; DIV denominator distinct). Grep 0 non-self observed 20261108T030419Z — **re-verify at run time before implementation**.

### Collision guard (RUN AT START)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rnE 'RTE_OVER_DIV|rte_over_div|rqa_ratio_rte_over_div|rqa_rte_over_div_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self
```
If collision found: pick a grep-zero fallback not used C125–C196 (e.g., TT_OVER_DIV, LAM_OVER_RTE, DET_OVER_RTE, ENTR_OVER_RTE — verify; LAM_OVER_ENTR collides). Record chosen feature + grep cmd/hits/evidence in all artifacts + `state.yaml`.

## REQUIRED C197 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_rte_over_div_ratio_shock_mr_costed_oos.py` (or collision-safe). Model after C188–C196. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T025820Z.json` (3daa1bd367829596e339ecd4956601142e96f24a5c1b0c92e70932b6f8f1d5fc), cite C196 OOS SHA `ffb28900b1750067cd8da2be960cf54c3b6c42a198741dc8e82bb9831825a256`. Emit `reports/real_quote_volume_rqa_rte_over_div_ratio_shock_mr_costed_oos_<UTC>.json` with `strategy_id`, `candidate`, `feature_definition`, `pre_stated_distinctness{grep_cmd,hits,verified_utc,evidence}`, `real_data_only:true`, `fail_closed:true`, `data{spot_cache,spot_cache_sha256,...,volume_loader_report}`, `params`, `references`, `per_asset`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_rule`, `edge_claim:"NONE"` unless rule holds.
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 197). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T025820Z.json` (3daa1bd367829596e339ecd4956601142e96f24a5c1b0c92e70932b6f8f1d5fc). Include prior + all C197 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign197_execution_summary_<UTC>.json` listing **all new C197 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C197`, `next_campaign: C198`, latest registry/OOS sha+path, `oos_edge_proven`, `c198_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C197, with grep cmd/hits/evidence).

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.meta.json data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rnE 'RTE_OVER_DIV|rte_over_div|rqa_ratio_rte_over_div|rqa_rte_over_div_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self
# NOW: implement+run C197 -> emit >=4 artifacts with SHAs -> sync state.yaml
```

## NEXT FOCUS CAMPAIGN — C198 (AUTO-QUEUED, HEAVY)
After C197 complete and synced: preselect **distinct grep-verified** RQA-ratio candidate not used C125–C197 (grep 0 non-self). Candidates to check: TT_OVER_DIV, LAM_OVER_RTE, DET_OVER_RTE, ENTR_OVER_RTE (LAM_OVER_ENTR collides). Record in `state.yaml.c198_preselected` with grep cmd/hits/evidence and **execute C198 immediately** under same template. No status-only replies. No stop between campaigns.
