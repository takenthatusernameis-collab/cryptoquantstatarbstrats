# READ THIS FIRST — SINGLE DURABLE HANDOFF (20261107T105953Z)

Repo: `cryptoquantstatarbstrats` (crypto quant stat arb strategies).
**Prioritization (from repo name):** fail-closed, real-data-only stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. R-B proceeds on validated `real_quote_volume` regardless of nonspot ingest.

## INITIAL TASK FOR NEXT SESSION — C152 (MANDATORY, HEAVY WORK, START NOW)

C104–C151 DONE — do NOT rerun. `pytest` unavailable (honestly recorded — do not fabricate test results). `numpy/scipy/pandas` importable. Caches present (`data/cache/volume_1h_full.{pkl,meta.json,provenance.json}`, `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.{pkl,meta.json}`).

**Readiness (run first, fail-closed):**
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'tt_over_det|tt_det_ratio|rqa_ratio_tt_det|TT_OVER_DET' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l   # must be 0 non-self
```

**Primary C152 candidate (pre-selected — re-verify at run time):** `VOLUME_RQA_TT_OVER_DET_RATIO_SHOCK_MR` — RQA ratio `RATIO_TT_DET = TT / %DET` (trapping time normalized by determinism) on delay-embedded log-volume returns (`m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`). `TT` = mean qualifying vertical-line length (`l>=l_min`). `%DET` = (sum of diagonal-line points for qualifying diagonal lines `l>=l_min`, `k!=0`) / offdiag recurrence sum. Fail-closed NaN/no-signal if `%DET<=0`, no qualifying diagonal lines/offdiag degenerate, or `TT` undefined/non-finite. Distinct from C125–C151 (incl C128 TT, C126 %DET, C150 %DET/TT, C151 TT/L_max). **Re-verify grep at run time (collision guard). If collision, pick next distinct alternative (`VOLUME_RQA_ENTR_OVER_TT_RATIO_SHOCK_MR` `ENTR/TT` fail-closed on `TT<=0`/no qualifying vertical lines/`ENTR` undefined/non-finite; or `VOLUME_RQA_LMAX_OVER_TT_RATIO_SHOCK_MR` `L_max/TT` fail-closed on `TT<=0`/no qualifying vertical lines/`L_max` undefined/non-finite), re-grep, and record chosen feature + grep evidence.**

Implement `scripts/run_real_quote_volume_rqa_tt_over_det_ratio_shock_mr_costed_oos.py` (or chosen alternative) modeled on C151/C150 scripts (copy WF/cost/B&H/SHA/report structure; change only feature computation, IDs, `pre_stated_distinctness`/refs to latest registry `strategy_edge_registry_20261107T105953Z.json` sha `ba60832be0eb86898d8d3da400a52aa5a6ca2261f7036060f1b5e64d91be4802` and C151 OOS sha `6caa21838b5bc5e8291586d8735896ad74ac00bf490f8746a98696ea4eb9e531`). Run it to emit `reports/real_quote_volume_rqa_<chosen>_costed_oos_<UTC>.json` with all top-level gate fields (`oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`), `edge_claim: NONE`, `real_data_only:true`, `fail_closed:true`, and `pre_stated_distinctness` recording grep cmd/hits/evidence.

### Step 1 — Ingest + registry + summary (MANDATORY)
1. Ingest: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 152) — record nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume` family.
2. Registry: `reports/strategy_edge_registry_<UTC>.json` superseding `strategy_edge_registry_20261107T105953Z.json` (sha `ba60832be0eb86898d8d3da400a52aa5a6ca2261f7036060f1b5e64d91be4802`). Structurally consistent `campaign/supersedes/supersedes_sha256/lineage/campaigns`; include prior context and add C152 with artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds.
3. Summary: `reports/campaign152_execution_summary_<UTC>.json` listing all new artifact paths + sha256 (SHAs computed from bytes on disk): OOS, ingest, registry, script.
4. Sync `research_state/state.yaml`: `latest_campaign_done: C152`, `next_campaign: C153`, latest registry sha, latest OOS path/sha, `oos_edge_proven` from emitted report, `c153_preselected` with a distinct grep-verified RQA-ratio candidate not used in C125–C152.

## Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

## Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run (C152 collision guard required; record chosen feature + grep evidence).
- **No status summary before >= 3 new concrete C152 report artifacts exist** (OOS + ingest + registry/summary).
- **Heavy work mandatory:** implement/run + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## Bottlenecks removed (confirmed 20261107T105953Z)
- C104–C150 locked; no reruns unchanged.
- C151 completed heavy; all artifacts emitted with disk-verified SHAs; state.yaml/HANDOFF synced to C151-done/C152-next.
- `numpy/scipy/pandas` importable.
- C152 primary pre-selected: `VOLUME_RQA_TT_OVER_DET_RATIO_SHOCK_MR` (`TT/%DET`) — grep pre-verified 0 hits now; re-verify at run time.
- `"No status before >=3 new artifacts"` + mandatory run — forces heavy work for C152.
- `pytest` unavailable recorded honestly — do not fabricate test results.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## C151 result (locked, do not rerun)
- `VOLUME_RQA_TT_OVER_LMAX_RATIO_SHOCK_MR` (TT/L_max), campaign 151, `oos_edge_proven:false`, `edge_claim:NONE`.
- OOS: `reports/real_quote_volume_rqa_tt_over_lmax_ratio_shock_mr_costed_oos_20261107T105953Z.json` (sha `6caa21838b5bc5e8291586d8735896ad74ac00bf490f8746a98696ea4eb9e531`). `any_exposure_oos:true`; cross-asset net sums `fee0=-0.312559, fee5=-0.609559, fee10=-0.906559, fee20=-1.500559, fee40=-2.688559`; `all_cost_slices_positive_oos_net_sum:false`; `all_cost_slices_beat_bh_mean_rule:false`.
- Ingest: `reports/real_feed_ingest_attempt_20261107T105953Z.json` (sha `c8235c658fab1f9653dc0efcb2795d230776386dc39d0b7dd99e6cda29aca235`).
- Registry: `reports/strategy_edge_registry_20261107T105953Z.json` (sha `ba60832be0eb86898d8d3da400a52aa5a6ca2261f7036060f1b5e64d91be4802`, supersedes C150 `bf44ee20...`).
- Summary: `reports/campaign151_execution_summary_20261107T105953Z.json` (sha `1fdfd943d51009c1f1a6925f3949f016debad80ecaaae5d1b4565e8d92442198`).
- Script: `scripts/run_real_quote_volume_rqa_tt_over_lmax_ratio_shock_mr_costed_oos.py` (sha `2851603d44c12b3e58232cdd11ff65e74bef809872bc69486c5b6c7c266910c4`). Distinctness grep hits pre=0 (re-verified; collision guard passed).

## Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rn 'tt_over_det|tt_det_ratio|rqa_ratio_tt_det|TT_OVER_DET' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l
```
Then implement and run the C152 `TT/%DET` (or collision-safe alternative) OOS script, emit ingest/registry/summary, and sync `research_state/state.yaml` to C152-done/C153-next. **Do not stop until C152 is properly complete with >=3 new artifacts and state.yaml synced. No status-only response.**
