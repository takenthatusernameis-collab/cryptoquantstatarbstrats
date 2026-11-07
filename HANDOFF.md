# READ THIS FIRST — SINGLE DURABLE HANDOFF (20261107T114304Z)

Repo: `cryptoquantstatarbstrats` (crypto quant stat arb strategies).
**Prioritization (from repo name):** fail-closed, real-data-only stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. R-B proceeds on validated `real_quote_volume` regardless of nonspot ingest.

## INITIAL TASK FOR NEXT SESSION — C153 (MANDATORY, HEAVY WORK, START NOW)

C104–C152 DONE — do NOT rerun. `pytest` unavailable (honestly recorded — do not fabricate test results). `numpy/scipy/pandas` importable. Caches present (`data/cache/volume_1h_full.{pkl,meta.json,provenance.json}`, `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.{pkl,meta.json}`).

**Readiness (run first, fail-closed):**
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'entr_over_tt|entr_tt_ratio|rqa_ratio_entr_tt|ENTR_OVER_TT' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l   # must be 0 non-self
```

**Primary C153 candidate (pre-selected — re-verify at run time):** `VOLUME_RQA_ENTR_OVER_TT_RATIO_SHOCK_MR` — RQA ratio `RATIO_ENTR_TT = ENTR / TT_mean` (diagonal-line Shannon entropy normalized by trapping time) on delay-embedded log-volume returns (`m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`). `ENTR` = Shannon entropy over qualifying diagonal-line length distribution (natural log); `TT_mean` = mean qualifying vertical-line length (`l>=l_min`). Fail-closed NaN/no-signal if `TT<=0`, no qualifying vertical lines, `ENTR<=0`/undefined/non-finite, or offdiag/recurrence degenerate. Distinct from C125–C152 (incl C152 TT/%DET, C151 TT/L_max, C150 %DET/TT). **Re-verify grep at run time (collision guard). If collision, pick next distinct alternative (`VOLUME_RQA_LMAX_OVER_TT_RATIO_SHOCK_MR` `L_max/TT` fail-closed on `TT<=0`/no qualifying vertical lines/`L_max` undefined/non-finite; or `VOLUME_RQA_DET_OVER_TT_RATIO_SHOCK_MR` `%DET/TT` fail-closed on `TT<=0`/no qualifying vertical lines/`%DET` undefined/non-finite), re-grep, and record chosen feature + grep evidence.**

Implement `scripts/run_real_quote_volume_rqa_entr_over_tt_ratio_shock_mr_costed_oos.py` (or chosen alternative) modeled on C152/C151 scripts (copy WF/cost/B&H/SHA/report structure; change only feature computation, IDs, `pre_stated_distinctness`/refs to latest registry `strategy_edge_registry_20261107T114304Z.json` sha `5b6747eddcf088d0c1f1faa544ab5638d19e0f4fbebf9e68dde41e6eec02bd3e` and C152 OOS sha `90664fdafa66226f33b0dce9c3dfb2ba007502571ecc86fac47c86fbec76030a`). Run it to emit `reports/real_quote_volume_rqa_entr_over_tt_ratio_shock_mr_costed_oos_<UTC>.json` with all top-level gate fields (`oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`), `edge_claim: NONE`, `real_data_only:true`, `fail_closed:true`, and `pre_stated_distinctness` recording grep cmd/hits/evidence.

### Step 1 — Ingest + registry + summary (MANDATORY)
1. Ingest: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 153) — record nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume` family.
2. Registry: `reports/strategy_edge_registry_<UTC>.json` superseding `strategy_edge_registry_20261107T114304Z.json` (sha `5b6747eddcf088d0c1f1faa544ab5638d19e0f4fbebf9e68dde41e6eec02bd3e`). Structurally consistent `campaign/supersedes/supersedes_sha256/lineage/campaigns`; include prior context and add C153 with artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds.
3. Summary: `reports/campaign153_execution_summary_<UTC>.json` listing all new artifact paths + sha256 (SHAs computed from bytes on disk): OOS, ingest, registry, script.
4. Sync `research_state/state.yaml`: `latest_campaign_done: C153`, `next_campaign: C154`, latest registry sha, latest OOS path/sha, `oos_edge_proven` from emitted report, `c154_preselected` with a distinct grep-verified RQA-ratio candidate not used in C125–C153.

## Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

## Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run (C153 collision guard required; record chosen feature + grep evidence).
- **No status summary before >= 3 new concrete C153 report artifacts exist** (OOS + ingest + registry/summary).
- **Heavy work mandatory:** implement/run + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## Bottlenecks removed (confirmed 20261107T114304Z)
- C104–C150 locked; no reruns unchanged.
- C151 completed heavy; all artifacts emitted with disk-verified SHAs; state.yaml/HANDOFF synced to C151-done/C152-next.
- C152 completed heavy; all artifacts emitted with disk-verified SHAs; state.yaml/HANDOFF synced to C152-done/C153-next.
- `numpy/scipy/pandas` importable.
- C153 primary pre-selected: `VOLUME_RQA_ENTR_OVER_TT_RATIO_SHOCK_MR` (`ENTR/TT_mean`) — grep pre-verified 0 hits now; re-verify at run time.
- `"No status before >=3 new artifacts"` + mandatory run — forces heavy work for C153.
- `pytest` unavailable recorded honestly — do not fabricate test results.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## C152 result (locked, do not rerun)
- `VOLUME_RQA_TT_OVER_DET_RATIO_SHOCK_MR` (TT/%DET), campaign 152, `oos_edge_proven:false`, `edge_claim:NONE`.
- OOS: `reports/real_quote_volume_rqa_tt_over_det_ratio_shock_mr_costed_oos_20261107T114304Z.json` (sha `90664fdafa66226f33b0dce9c3dfb2ba007502571ecc86fac47c86fbec76030a`). `any_exposure_oos:true`; cross-asset net sums `fee0=-0.220951, fee5=-0.584951, fee10=-0.948951, fee20=-1.676951, fee40=-3.132951`; `all_cost_slices_positive_oos_net_sum:false`; `all_cost_slices_beat_bh_mean_rule:false`.
- Ingest: `reports/real_feed_ingest_attempt_20261107T114304Z.json` (sha `87475c4ef95ce2ab9513ed5307da39d9318d13044f0ed899e37386afcf5a6b08`).
- Registry: `reports/strategy_edge_registry_20261107T114304Z.json` (sha `5b6747eddcf088d0c1f1faa544ab5638d19e0f4fbebf9e68dde41e6eec02bd3e`, supersedes C151 `ba60832be0eb86898d8d3da400a52aa5a6ca2261f7036060f1b5e64d91be4802`).
- Summary: `reports/campaign152_execution_summary_20261107T114304Z.json` (sha `18399a4e18927f4e70023e14da9320b80fdaa9879f6ce71810f3d6445afa2296`).
- Script: `scripts/run_real_quote_volume_rqa_tt_over_det_ratio_shock_mr_costed_oos.py` (sha `961aee4ef067f0a78c706abfe77bc2b3d80475f2f5a2fd80984fe61937d3e789`). Distinctness grep hits pre=0 (re-verified; collision guard passed).

## Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rn 'entr_over_tt|entr_tt_ratio|rqa_ratio_entr_tt|ENTR_OVER_TT' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l
```
Then implement and run the C153 `ENTR/TT` (or collision-safe alternative) OOS script, emit ingest/registry/summary, and sync `research_state/state.yaml` to C153-done/C154-next. **Do not stop until C153 is properly complete with >=3 new artifacts and state.yaml synced. No status-only response.**

(End of file)
