# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261108T030419Z, C196 COMPLETE/LOCKED, C197 MANDATORY INITIAL TASK — EXECUTE NOW)
**Repo:** `cryptoquantstatarbstrats`. Fail-closed, **real-data-only** stat-arb edge validation — WF OOS 720/168/168, costs [[0,0],[5,5],[10,10],[20,20],[40,40]], B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C196 LOCKED.**

## TIMESTAMPED INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (20261108T030419Z)
**C197 has NOT been executed.** No C197/RTE_OVER_DIV artifacts exist on disk (checked `reports/`+`scripts/` at 20261108T030419Z). Do **not** produce a status summary first. **Execute C197 immediately** and produce **>= 3 NEW concrete C197 report artifacts on disk** (OOS + ingest + registry/superseding + summary) **each with SHA256 computed from bytes**, plus the OOS script and synced `research_state/state.yaml`. Heavy work is mandatory.

## VERIFIED BASELINE (20261108T030419Z — current checks)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1). pytest 9.2.0 available (do not fabricate).
- Caches present: `data/cache/volume_1h_full.pkl/meta/provenance`, spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl`.
- **C196 COMPLETE/LOCKED** (SHAs re-verified from bytes 20261108T030419Z): OOS `reports/real_quote_volume_rqa_entr_over_div_ratio_shock_mr_costed_oos_20261108T025803Z.json`=ffb28900b1750067cd8da2be960cf54c3b6c42a198741dc8e82bb9831825a256 (`VOLUME_RQA_ENTR_OVER_DIV_RATIO_SHOCK_MR`, `oos_edge_proven:false`, `edge_claim:NONE`). Ingest `reports/real_feed_ingest_attempt_20261108T025820Z.json`=2f7f297302086c1391949a2ff36ae031fed3f32bf8c21867218e23aeb92d1975. Registry `reports/strategy_edge_registry_20261108T025820Z.json`=3daa1bd367829596e339ecd4956601142e96f24a5c1b0c92e70932b6f8f1d5fc supersedes C195 e185079d39770b6cb8ae5b426d07f1459e585780bb513349478d5190749a2700. Script `scripts/run_real_quote_volume_rqa_entr_over_div_ratio_shock_mr_costed_oos.py`=ceb12d8ad24a67bef28d1c06addbcbc426a3e9f773b6e29ba2ffedcc34720d3b. Summary `reports/campaign196_execution_summary_20261108T025820Z.json`=020533573586baed83a5e4b4a590c39f3cfa30965cec157fc8f1feead850a3de.
- C196 cross-asset OOS net sums: fee0_slip0=-0.5765044133311339, fee5_slip5=-1.0145044133311343, fee10_slip10=-1.4525044133311342, fee20_slip20=-2.3285044133311343, fee40_slip40=-4.080504413331134 (edge_claim NONE).
- `git status` clean at check time (20261108T030419Z). No lock files / duplicate competing handoffs found.

## BOTTLENECKS REMOVED / NO EXCUSES (20261108T030419Z)
- C104–C196 locked with SHAs from bytes; no reruns, no stale cache re-scans, no gate/threshold weakening, no proxies labeled real.
- Deps/caches ready. Nonspot blocker does not block R-B on `real_quote_volume`.
- Single durable handoff = `HANDOFF.md` + `research_state/state.yaml`. **No status-only replies. No stop after status.**
- **C197 RTE_OVER_DIV collision guard = 0 non-self** at 20261108T030419Z (`grep -rnE 'RTE_OVER_DIV|rte_over_div|rqa_ratio_rte_over_div|rqa_rte_over_div_ratio' scripts/ strategies/ backtest/ utils/`). Re-verify at C197 run time before implementation.

## INITIAL TASK — C197 (MANDATORY, HEAVY WORK, START IMMEDIATELY)
**Execute C197 now.** Produce **>= 3 NEW concrete C197 report artifacts on disk** (OOS + ingest + registry/superseding + summary) **each with SHA256 computed from bytes**, plus OOS script and synced `research_state/state.yaml`.

### Primary candidate (preselected; run-time grep required)
`VOLUME_RQA_RTE_OVER_DIV_RATIO_SHOCK_MR` — RQA ratio RTE/DIV on delay-embedded log-volume returns. `RTE` = Recurrence Time Entropy (Shannon entropy, nats) of the **white vertical line length** (recurrence-time/gap) distribution from the RP: for each column `j`, measure lengths `w` of consecutive zeros (vertical white gaps) between recurrent points (excluding trivial self); collect qualifying `w>=w_min` (pre-stated `w_min=1`, all positive gaps) with count `n_w>0`, `p_w=n_w/sum_u n_u`, `RTE=-sum_w p_w*ln(p_w)`. `DIV` = divergence = `1/L_MAX` where `L_MAX` = max qualifying diagonal line length `k>=l_min` excl LOI. `RATIO_RTE_DIV = RTE/DIV`. Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2,w_min=1`. **Fail-closed NaN/no-signal** if RTE undefined/non-finite/degenerate (<2 distinct qualifying gap lengths or entropy non-finite/non-positive), DIV/L_MAX invalid (no qualifying diagonal lines or `L_MAX<=0`/non-finite), ratio non-finite, or insufficient qualifying lines/gaps. Trailing/causal only. Pre-stated distinctness: RTE/DIV pairing not used C125–C196 (C194 used RTE/other denominator RR; DIV denominator here is distinct) — grep 0 observed 20261108T030419Z; re-verify.

### Collision guard (required at run time)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rnE 'RTE_OVER_DIV|rte_over_div|rqa_ratio_rte_over_div|rqa_rte_over_div_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self for primary
```
If collides: pick a grep-zero fallback not used in C125–C196 (e.g., TT_OVER_DIV, LAM_OVER_RTE, DET_OVER_RTE, ENTR_OVER_RTE — verify at run time), record chosen feature + grep cmd/hits/evidence in artifacts/state.

### Required C197 deliverables (all on disk, SHA256 from bytes)
1. **OOS script + run** (model on C188–C196): `scripts/run_real_quote_volume_rqa_rte_over_div_ratio_shock_mr_costed_oos.py` (or collision-safe alternative). Change only feature computation, IDs, `pre_stated_distinctness`, and refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T025820Z.json` (3daa1bd367829596e339ecd4956601142e96f24a5c1b0c92e70932b6f8f1d5fc), cite C196 OOS SHA ffb28900b1750067cd8da2be960cf54c3b6c42a198741dc8e82bb9831825a256. Emit `reports/real_quote_volume_rqa_rte_over_div_ratio_shock_mr_costed_oos_<UTC>.json` with `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`, `edge_claim:"NONE"` unless rule holds, `real_data_only:true`, `fail_closed:true`, `pre_stated_distinctness`.
2. **Ingest:** `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 197) — nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`; include cache/provenance SHAs.
3. **Registry (superseding):** `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T025820Z.json` (3daa1bd367829596e339ecd4956601142e96f24a5c1b0c92e70932b6f8f1d5fc). Include prior + C197 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary:** `reports/campaign197_execution_summary_<UTC>.json` listing **all new C197 artifact paths + sha256 from bytes**.
5. **Sync state:** `research_state/state.yaml` → `latest_campaign_done:C197`, `next_campaign:C198`, latest registry/OOS sha+path, `oos_edge_proven`, `c198_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C197, with grep cmd/hits/evidence).

## Fail-closed edge rule (EXACT)
`oos_edge_proven=true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## Mandatory rules (HARD)
- Real data only; fail-closed. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if rule holds. Pre-state distinctness; grep-verify before implementation/run; record evidence.
- **No status summary before >= 3 new concrete C197 artifacts exist.** Heavy work mandatory.

## Immediate first actions (run, then build)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.meta.json data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rnE 'RTE_OVER_DIV|rte_over_div|rqa_ratio_rte_over_div|rqa_rte_over_div_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 for primary
# implement+run C197 -> emit OOS+ingest+registry+summary (>=4) with SHAs -> sync state.yaml + HANDOFF.md
```

## NEXT FOCUS CAMPAIGN — C198 (MANDATORY after C197)
Preselect a **distinct grep-verified** RQA-ratio candidate not used in C125–C197 (grep 0 non-self), record grep cmd/hits/evidence in `state.yaml.c198_preselected`, then **execute C198** under the same template. Candidate checks at 20261108T030419Z showed TT_OVER_DIV/LAM_OVER_RTE/DET_OVER_RTE/ENTR_OVER_RTE grep 0 (LAM_OVER_ENTR collides). **No status-only replies. No stop after status.**