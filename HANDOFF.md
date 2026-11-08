# READ THIS FIRST — SINGLE DURABLE HANDOFF (UPDATED: 20261108T014412Z, C191 COMPLETE, NEXT=C192)
**Repo:** `cryptoquantstatarbstrats`. Fail-closed, **real-data-only** stat-arb edge validation — WF OOS 720/168/168, costs [[0,0],[5,5],[10,10],[20,20],[40,40]], B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C191 LOCKED.**

## VERIFIED BASELINE (20261108T014412Z)
- deps_ok (numpy/scipy/pandas). pytest 9.2.0 available.
- Caches present: `data/cache/volume_1h_full.pkl/meta/provenance`, spot `0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl/meta`.
- **C191 COMPLETE/LOCKED**: OOS `reports/real_quote_volume_rqa_lmax_over_lavg_ratio_shock_mr_costed_oos_20261108T014311Z.json`=313f6e904c049905b8ce87596b1af6953eaf36076be50c9a65f547e54b87768e (`VOLUME_RQA_LMAX_OVER_LAVG_RATIO_SHOCK_MR`, `oos_edge_proven:false`, `edge_claim:NONE`). Ingest `reports/real_feed_ingest_attempt_20261108T014412Z.json`=cbd550736f149f63b73060bda13d7b978af06aac9f78d86bd81a2798c65efc35. Registry `reports/strategy_edge_registry_20261108T014412Z.json`=7d2e0861e67726b03924550d7be29a68154010d79d3c6c2fa1177077edc848e0 supersedes C190 e052c69a35c2fd0551781831391c44b7104b0d8dfe5534b7fe7e6115af26245a. Script `scripts/run_real_quote_volume_rqa_lmax_over_lavg_ratio_shock_mr_costed_oos.py`=d1b56e7f47dcf1ec7e0055eb87d8ed7b7e9f5a85d2713dfa4ed692eb8205008b. Summary `reports/campaign191_execution_summary_20261108T014412Z.json`=d7f8dbed5e3f271e394da1197d16e478feb6db975a5cee624233a22d59dbe6b1. All SHAs verified from bytes 20261108T014412Z.
- Cross-asset OOS net sums: fee0_slip0=-0.0010, fee5_slip5=-0.4290, fee10_slip10=-0.8570, fee20_slip20=-1.7130, fee40_slip40=-3.4250 (rule not satisfied; edge_claim NONE).

## BOTTLENECKS REMOVED / NO EXCUSES (20261108T014412Z)
- C104–C191 locked with SHAs from bytes; no reruns, no stale cache re-scans, no gate/threshold weakening, no proxies labeled real.
- Deps/caches ready. Nonspot blocker does not block R-B on `real_quote_volume`.
- Single durable handoff = `HANDOFF.md` + `research_state/state.yaml`. **No status-only replies. No stop after status.**
- C191 LMAX_OVER_LAVG collision guard 0 non-self at run time (20261108T013847Z; all hits self). C192 LAVG_OVER_TT grep 0 observed (20261108T014412Z) — re-verify at C192 run time.

## INITIAL TASK — C192 (MANDATORY, HEAVY WORK, START IMMEDIATELY)
**Execute C192 now.** Produce **>= 3 NEW concrete C192 report artifacts on disk** (OOS + ingest + registry/superseding + summary) **each with SHA256 computed from bytes**, plus OOS script and synced `research_state/state.yaml`.

### Primary candidate (preselected; run-time grep required)
`VOLUME_RQA_LAVG_OVER_TT_RATIO_SHOCK_MR` — RQA ratio **LAVG/TT** on delay-embedded log-volume returns. `LAVG` = mean qualifying diagonal line length (k>=l_min, excluding LOI k=1). `TT` = trapping time = average length of vertical lines with length >= v_min on the recurrence matrix. `RATIO_LAVG_TT = LAVG/TT`. Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2,v_min=2`. **Fail-closed NaN/no-signal** if `TT==0` or undefined/non-finite/degenerate, `LAVG` undefined/non-finite/degenerate, ratio non-finite, or insufficient qualifying lines. Trailing/causal only. Pre-stated distinctness: LAVG/TT pairing not used C125–C191; grep 0 observed at preselect.

### Collision guard (required at run time)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rnE 'LAVG_OVER_TT|lavg_over_tt|rqa_ratio_lavg_over_tt|rqa_lavg_over_tt_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self for primary
```
If collides: pick a grep-zero fallback not used in C125–C192 (e.g., `DIV_OVER_RR`, `RTE_OVER_RR`, `TRANS_OVER_RR`, `CL_OVER_RR` — **verify 0 non-self at run time**; `DIV_OVER_RR` grep 0 observed 20261108T014412Z), record chosen feature + grep cmd/hits/evidence in artifacts/state.

### Required C192 deliverables (all on disk, SHA256 from bytes)
1. **OOS script + run** (model on C188–C191): `scripts/run_real_quote_volume_rqa_lavg_over_tt_ratio_shock_mr_costed_oos.py` (or collision-safe alternative). Change only feature computation, IDs, `pre_stated_distinctness`, and refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T014412Z.json` (7d2e0861e67726b03924550d7be29a68154010d79d3c6c2fa1177077edc848e0), cite C191 OOS SHA 313f6e904c049905b8ce87596b1af6953eaf36076be50c9a65f547e54b87768e. Emit `reports/real_quote_volume_rqa_lavg_over_tt_ratio_shock_mr_costed_oos_<UTC>.json` with `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`, `edge_claim:"NONE"` unless rule holds, `real_data_only:true`, `fail_closed:true`, `pre_stated_distinctness`.
2. **Ingest:** `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 192) — nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`; include cache/provenance SHAs.
3. **Registry (superseding):** `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T014412Z.json` (7d2e0861e67726b03924550d7be29a68154010d79d3c6c2fa1177077edc848e0). Include prior + C192 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary:** `reports/campaign192_execution_summary_<UTC>.json` listing **all new C192 artifact paths + sha256 from bytes**.
5. **Sync state:** `research_state/state.yaml` → `latest_campaign_done:C192`, `next_campaign:C193`, latest registry/OOS sha+path, `oos_edge_proven`, `c193_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C192, with grep cmd/hits/evidence).

## Fail-closed edge rule (EXACT)
`oos_edge_proven=true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## Mandatory rules (HARD)
- Real data only; fail-closed. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if rule holds. Pre-state distinctness; grep-verify before implementation/run; record evidence.
- **No status summary before >= 3 new concrete C192 artifacts exist.** Heavy work mandatory.

## Immediate first actions (run, then build)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.meta.json data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rnE 'LAVG_OVER_TT|lavg_over_tt|rqa_ratio_lavg_over_tt|rqa_lavg_over_tt_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 for primary
# implement+run C192 -> emit OOS+ingest+registry+summary (>=3) with SHAs -> sync state.yaml
```

## NEXT FOCUS CAMPAIGN — C193 (MANDATORY after C192)
Preselect a **distinct grep-verified** RQA-ratio candidate not used in C125–C192 (grep 0 non-self), record grep cmd/hits/evidence in `state.yaml.c193_preselected`, then **execute C193** under the same template. **No status-only replies. No stop after status.**
