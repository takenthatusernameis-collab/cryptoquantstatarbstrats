# READ THIS FIRST — SINGLE DURABLE HANDOFF (UPDATED: 20261108T015950Z, C193 COMPLETE/LOCKED, NEXT=C194 MANDATORY INITIAL TASK)
**Repo:** `cryptoquantstatarbstrats`. Fail-closed, **real-data-only** stat-arb edge validation — WF OOS 720/168/168, costs [[0,0],[5,5],[10,10],[20,20],[40,40]], B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C193 LOCKED.**

## VERIFIED BASELINE (20261108T015950Z — current)
- deps_ok (numpy/scipy/pandas). pytest 9.2.0 available.
- Caches present: `data/cache/volume_1h_full.pkl/meta/provenance`, spot `0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl/meta`.
- **C193 COMPLETE/LOCKED**: OOS `reports/real_quote_volume_rqa_div_over_rr_ratio_shock_mr_costed_oos_20261108T015857Z.json`=ce7c1e69b8553b0a47f63ee9be77145e92a1d0b94678e151fbbe69b0b541704e (`VOLUME_RQA_DIV_OVER_RR_RATIO_SHOCK_MR`, `oos_edge_proven:false`, `edge_claim:NONE`). Ingest `reports/real_feed_ingest_attempt_20261108T015950Z.json`=670f86779fee0649aaaa953b4543bc613d736dd18d56c7e18be509e0cc97faa3. Registry `reports/strategy_edge_registry_20261108T015950Z.json`=7471b609d6fcab19362eb051e70e42e438021ab5b14dab23b59b0e530c970f4a supersedes C192 78d3fc45a916b81ba3ecc7f8251995c927691ed4335f7e97b454679ad01b0193. Script `scripts/run_real_quote_volume_rqa_div_over_rr_ratio_shock_mr_costed_oos.py`=a6745538c4c1c60b26a886561867f0b39012957e7a715339491999ed9a8adcd6. Summary `reports/campaign193_execution_summary_20261108T015950Z.json`=58df5548f3c56524e17f2a0808d5936e2f5222fb36ac372c6bcd577e0e1219d7. All SHAs verified from bytes 20261108T015950Z.
- Cross-asset OOS net sums: fee0_slip0=1.2528, fee5_slip5=0.9698, fee10_slip10=0.6868, fee20_slip20=0.1208, fee40_slip40=-1.0112 (rule not satisfied; edge_claim NONE).

## BOTTLENECKS REMOVED / NO EXCUSES (20261108T015950Z)
- C104–C193 locked with SHAs from bytes; no reruns, no stale cache re-scans, no gate/threshold weakening, no proxies labeled real.
- Deps/caches ready. Nonspot blocker does not block R-B on `real_quote_volume`.
- Single durable handoff = `HANDOFF.md` + `research_state/state.yaml`. **No status-only replies. No stop after status.**
- C193 DIV_OVER_RR collision guard 0 non-self at run time (20261108T015439Z). C194 RTE_OVER_RR grep 0 observed (20261108T015950Z); re-verify at C194 run time.

## INITIAL TASK — C194 (MANDATORY, HEAVY WORK, START IMMEDIATELY)
**Execute C194 now.** Produce **>= 3 NEW concrete C194 report artifacts on disk** (OOS + ingest + registry/superseding + summary) **each with SHA256 computed from bytes**, plus OOS script and synced `research_state/state.yaml`.

### Primary candidate (preselected; run-time grep required)
`VOLUME_RQA_RTE_OVER_RR_RATIO_SHOCK_MR` — RQA ratio RTE/ORR on delay-embedded log-volume returns. `RTE` = recurrence time entropy = Shannon entropy of qualifying diagonal line length distribution (k>=l_min, excl LOI). `ORR` = off-diagonal recurrence rate = fraction of off-diagonal recurrence points. `RATIO_RTE_ORR = RTE/ORR`. Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`. **Fail-closed NaN/no-signal** if distribution empty/degenerate, `ORR==0` or undefined/non-finite/degenerate, ratio non-finite, or insufficient qualifying lines/points. Trailing/causal only. Pre-stated distinctness: RTE/ORR pairing not used C125–C193; grep 0 observed at preselect.

### Collision guard (required at run time)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rnE 'RTE_OVER_RR|rte_over_rr|rqa_ratio_rte_over_rr|rqa_rte_over_rr_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self for primary
```
If collides: pick a grep-zero fallback not used in C125–C194, record chosen feature + grep cmd/hits/evidence in artifacts/state.

### Required C194 deliverables (all on disk, SHA256 from bytes)
1. **OOS script + run** (model on C188–C193): `scripts/run_real_quote_volume_rqa_rte_over_rr_ratio_shock_mr_costed_oos.py` (or collision-safe alternative). Change only feature computation, IDs, `pre_stated_distinctness`, and refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T015950Z.json` (7471b609d6fcab19362eb051e70e42e438021ab5b14dab23b59b0e530c970f4a), cite C193 OOS SHA ce7c1e69b8553b0a47f63ee9be77145e92a1d0b94678e151fbbe69b0b541704e. Emit `reports/real_quote_volume_rqa_rte_over_rr_ratio_shock_mr_costed_oos_<UTC>.json` with `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`, `edge_claim:"NONE"` unless rule holds, `real_data_only:true`, `fail_closed:true`, `pre_stated_distinctness`.
2. **Ingest:** `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 194) — nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`; include cache/provenance SHAs.
3. **Registry (superseding):** `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T015950Z.json` (7471b609d6fcab19362eb051e70e42e438021ab5b14dab23b59b0e530c970f4a). Include prior + C194 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary:** `reports/campaign194_execution_summary_<UTC>.json` listing **all new C194 artifact paths + sha256 from bytes**.
5. **Sync state:** `research_state/state.yaml` → `latest_campaign_done:C194`, `next_campaign:C195`, latest registry/OOS sha+path, `oos_edge_proven`, `c195_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C194, with grep cmd/hits/evidence).

## Fail-closed edge rule (EXACT)
`oos_edge_proven=true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## Mandatory rules (HARD)
- Real data only; fail-closed. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if rule holds. Pre-state distinctness; grep-verify before implementation/run; record evidence.
- **No status summary before >= 3 new concrete C194 artifacts exist.** Heavy work mandatory.

## Immediate first actions (run, then build)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.meta.json data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rnE 'RTE_OVER_RR|rte_over_rr|rqa_ratio_rte_over_rr|rqa_rte_over_rr_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 for primary
# implement+run C194 -> emit OOS+ingest+registry+summary (>=3) with SHAs -> sync state.yaml
```

## NEXT FOCUS CAMPAIGN — C195 (MANDATORY after C194)
Preselect a **distinct grep-verified** RQA-ratio candidate not used in C125–C194 (grep 0 non-self), record grep cmd/hits/evidence in `state.yaml.c195_preselected`, then **execute C195** under the same template. **No status-only replies. No stop after status.**
