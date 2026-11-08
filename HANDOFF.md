# READ THIS FIRST — SINGLE DURABLE HANDOFF (UPDATED: 20261108T010206Z, C190 COMPLETE, NEXT=C191)
**Repo:** `cryptoquantstatarbstrats`. Fail-closed, **real-data-only** stat-arb edge validation — WF OOS 720/168/168, costs [[0,0],[5,5],[10,10],[20,20],[40,40]], B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C190 LOCKED.**

## VERIFIED BASELINE (20261108T010206Z)
- deps_ok (numpy/scipy/pandas). pytest 9.2.0 available.
- Caches present: `data/cache/volume_1h_full.pkl/meta/provenance`, spot `0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl/meta`.
- **C190 COMPLETE/LOCKED**: OOS `reports/real_quote_volume_rqa_tt_over_rr_ratio_shock_mr_costed_oos_20261108T010005Z.json`=5929c7d0467665ec0a7f80ee19b9c3088ae423d0917ab18614c4e729a9b3d04a (`VOLUME_RQA_TT_OVER_RR_RATIO_SHOCK_MR`, `oos_edge_proven:false`, `edge_claim:NONE`). Ingest `reports/real_feed_ingest_attempt_20261108T010105Z.json`=1a443faee0053688808d5e97c8ba7ece8c70f698a00210ae13d675dbd81beed5. Registry `reports/strategy_edge_registry_20261108T010105Z.json`=e052c69a35c2fd0551781831391c44b7104b0d8dfe5534b7fe7e6115af26245a supersedes C189 f6af7d1836b30576f4193ea0ddd2d79db41a19ff224b904e30ccf1e7e2420ee8. Script `scripts/run_real_quote_volume_rqa_tt_over_rr_ratio_shock_mr_costed_oos.py`=17604acc2a7bc329d9f0b21cfb0f6f0cd13d4b1be0bfd0bd2a5143faaaca90de. Summary `reports/campaign190_execution_summary_20261108T010105Z.json`=473e55bdd609398585d5e573d0cc23f6586e635a2509ddbc5bd943ff6194e0e3. All SHAs verified from bytes 20261108T010206Z.
- Cross-asset OOS net sums: fee0_slip0=0.1047, fee5_slip5=-0.2213, fee10_slip10=-0.5473, fee20_slip20=-1.1993, fee40_slip40=-2.5033 (rule not satisfied; edge_claim NONE).

## BOTTLENECKS REMOVED / NO EXCUSES (20261108T010206Z)
- C104–C190 locked with SHAs from bytes; no reruns, no stale cache re-scans, no gate/threshold weakening, no proxies labeled real.
- Deps/caches ready. Nonspot blocker does not block R-B on `real_quote_volume`.
- Single durable handoff = `HANDOFF.md` + `research_state/state.yaml`. **No status-only replies. No stop after status.**
- C190 TT_OVER_RR collision guard 0 non-self at run time (20261108T010105Z). C191 LMAX_OVER_LAVG grep 0 observed (20261108T010105Z) — re-verify at C191 run time.

## INITIAL TASK — C191 (MANDATORY, HEAVY WORK, START IMMEDIATELY)
**Execute C191 now.** Produce **>= 3 NEW concrete C191 report artifacts on disk** (OOS + ingest + registry/superseding + summary) **each with SHA256 computed from bytes**, plus OOS script and synced `research_state/state.yaml`.

### Primary candidate (preselected; run-time grep required)
`VOLUME_RQA_LMAX_OVER_LAVG_RATIO_SHOCK_MR` — RQA ratio **LMAX/LAVG** on delay-embedded log-volume returns. `LMAX` = longest qualifying diagonal line length (k>=1,l>=l_min,excluding LOI). `LAVG` = mean qualifying diagonal line length. `RATIO_LMAX_LAVG = LMAX/LAVG`. Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`. **Fail-closed NaN/no-signal** if `LAVG==0` or undefined/non-finite/degenerate, `LMAX` undefined/non-finite/degenerate, denominator/ratio non-finite, or insufficient qualifying points. Trailing/causal only. Pre-stated distinctness: LMAX/LAVG pairing not used C125–C190; grep 0 observed at preselect.

### Collision guard (required at run time)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rnE 'LMAX_OVER_LAVG|lmax_over_lavg|rqa_ratio_lmax_over_lavg|rqa_lmax_over_lavg_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self for primary
```
If collides: pick a grep-zero fallback not used in C125–C191 (e.g., `DET_OVER_RR`, `TT_OVER_LAVG`, `RR_OVER_TT` — **verify 0 non-self at run time**), record chosen feature + grep cmd/hits/evidence in artifacts/state.

### Required C191 deliverables (all on disk, SHA256 from bytes)
1. **OOS script + run** (model on C188–C190): `scripts/run_real_quote_volume_rqa_lmax_over_lavg_ratio_shock_mr_costed_oos.py` (or collision-safe alternative). Change only feature computation, IDs, `pre_stated_distinctness`, and refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261108T010105Z.json` (e052c69a35c2fd0551781831391c44b7104b0d8dfe5534b7fe7e6115af26245a), cite C190 OOS SHA 5929c7d0467665ec0a7f80ee19b9c3088ae423d0917ab18614c4e729a9b3d04a. Emit `reports/real_quote_volume_rqa_lmax_over_lavg_ratio_shock_mr_costed_oos_<UTC>.json` with `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`, `edge_claim:"NONE"` unless rule holds, `real_data_only:true`, `fail_closed:true`, `pre_stated_distinctness`.
2. **Ingest:** `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 191) — nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`; include cache/provenance SHAs.
3. **Registry (superseding):** `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261108T010105Z.json` (e052c69a35c2fd0551781831391c44b7104b0d8dfe5534b7fe7e6115af26245a). Include prior + C191 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary:** `reports/campaign191_execution_summary_<UTC>.json` listing **all new C191 artifact paths + sha256 from bytes**.
5. **Sync state:** `research_state/state.yaml` → `latest_campaign_done:C191`, `next_campaign:C192`, latest registry/OOS sha+path, `oos_edge_proven`, `c192_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C191, with grep cmd/hits/evidence).

## Fail-closed edge rule (EXACT)
`oos_edge_proven=true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## Mandatory rules (HARD)
- Real data only; fail-closed. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if rule holds. Pre-state distinctness; grep-verify before implementation/run; record evidence.
- **No status summary before >= 3 new concrete C191 artifacts exist.** Heavy work mandatory.

## Immediate first actions (run, then build)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.meta.json data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rnE 'LMAX_OVER_LAVG|lmax_over_lavg|rqa_ratio_lmax_over_lavg|rqa_lmax_over_lavg_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 for primary
# implement+run C191 -> emit OOS+ingest+registry+summary (>=3) with SHAs -> sync state.yaml
```

## NEXT FOCUS CAMPAIGN — C192 (MANDATORY after C191)
Preselect a **distinct grep-verified** RQA-ratio candidate not used in C125–C191 (grep 0 non-self), record grep cmd/hits/evidence in `state.yaml.c192_preselected`, then **execute C192** under the same template. **No status-only replies. No stop after status.**
