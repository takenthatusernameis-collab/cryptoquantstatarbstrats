# READ THIS FIRST — SINGLE DURABLE HANDOFF (20261107T105517Z)

Repo: `cryptoquantstatarbstrats` (crypto quant stat arb strategies).
**Prioritization (from repo name):** fail-closed, real-data-only stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. R-B proceeds on validated `real_quote_volume` regardless of nonspot ingest.

## INITIAL TASK FOR NEXT SESSION — C151 (MANDATORY, HEAVY WORK, START NOW)

C104–C150 DONE — do NOT rerun. `pytest` unavailable (honestly recorded — do not fabricate test results). `numpy/scipy/pandas` importable. Caches present (`data/cache/volume_1h_full.{pkl,meta.json,provenance.json}`, `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.{pkl,meta.json}`).

**Readiness (run first, fail-closed):**
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'tt_over_lmax|tt_lmax_ratio|rqa_ratio_tt_lmax|TT_OVER_LMAX' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l   # must be 0 non-self
```

**Primary C151 candidate (pre-selected — re-verify at run time):** `VOLUME_RQA_TT_OVER_LMAX_RATIO_SHOCK_MR` — RQA ratio `RATIO_TT_LMAX = TT / L_max` (trapping time normalized by longest diagonal line) on delay-embedded log-volume returns (`m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`). `TT` = mean qualifying vertical-line length (`l>=l_min`). `L_max` = maximum diagonal-line length (`l>=l_min`, `k!=0`). Fail-closed NaN/no-signal if `L_max<=0`, no qualifying diagonal lines, `TT` undefined/non-finite, or recurrence degenerate. Distinct from C125–C150 (incl C128 TT, C131 L_max, C144 TT/ENTR, C145 TT/%RR, C150 %DET/TT). **Re-verify grep at run time (collision guard). If collision, pick next distinct alternative (`VOLUME_RQA_TT_OVER_DET_RATIO_SHOCK_MR` `TT/%DET` fail-closed on `%DET<=0`/no qualifying diagonal lines/`TT` undefined/non-finite; or `VOLUME_RQA_ENTR_OVER_TT_RATIO_SHOCK_MR` `ENTR/TT` fail-closed on `TT<=0`/no qualifying vertical lines/`ENTR` undefined/non-finite), re-grep, and record chosen feature + grep evidence.**

Implement `scripts/run_real_quote_volume_rqa_tt_over_lmax_ratio_shock_mr_costed_oos.py` (or chosen alternative) modeled on C150/C149 scripts (copy WF/cost/B&H/SHA/report structure; change only feature computation, IDs, `pre_stated_distinctness`/refs to latest registry `strategy_edge_registry_20261107T105517Z.json` sha `bf44ee2026847640e468325f6a2b40e59a829b7b0a0aab68cf398fdd12209a37` and C150 OOS sha `19c41b642506fe8ed002ee85905e34a2eb6906fc08f1ae7175e78d0ea13e8dbe`). Run it to emit `reports/real_quote_volume_rqa_<chosen>_costed_oos_<UTC>.json` with all top-level gate fields (`oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`), `edge_claim: NONE`, `real_data_only:true`, `fail_closed:true`, and `pre_stated_distinctness` recording grep cmd/hits/evidence.

### Step 1 — Ingest + registry + summary (MANDATORY)
1. Ingest: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 151) — record nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume` family.
2. Registry: `reports/strategy_edge_registry_<UTC>.json` superseding `strategy_edge_registry_20261107T105517Z.json` (sha `bf44ee2026847640e468325f6a2b40e59a829b7b0a0aab68cf398fdd12209a37`). Structurally consistent `campaign/supersedes/supersedes_sha256/lineage/campaigns`; include C144–C150 context/entries and add C151 with artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds.
3. Summary: `reports/campaign151_execution_summary_<UTC>.json` listing all new artifact paths + sha256 (SHAs computed from bytes on disk): OOS, ingest, registry, script.
4. Sync `research_state/state.yaml`: `latest_campaign_done: C151`, `next_campaign: C152`, latest registry sha, latest OOS path/sha, `oos_edge_proven` from emitted report, `c152_preselected` with a distinct grep-verified RQA-ratio candidate not used in C125–C151.

## Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

## Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run (C151 collision guard required; record chosen feature + grep evidence).
- **No status summary before >= 3 new concrete C151 report artifacts exist** (OOS + ingest + registry/summary).
- **Heavy work mandatory:** implement/run + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## Bottlenecks removed (confirmed 20261107T105517Z)
- C104–C149 locked; no reruns unchanged.
- C150 completed heavy; all artifacts emitted with disk-verified SHAs; state.yaml/HANDOFF synced to C150-done/C151-next.
- `numpy/scipy/pandas` importable.
- C151 primary pre-selected: `VOLUME_RQA_TT_OVER_LMAX_RATIO_SHOCK_MR` (`TT/L_max`) — re-verify grep at run time.
- `"No status before >=3 new artifacts"` + mandatory run — forces heavy work for C151.
- `pytest` unavailable recorded honestly — do not fabricate test results.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## C150 result (locked, do not rerun)
- `VOLUME_RQA_DET_OVER_TT_RATIO_SHOCK_MR` (%DET/TT), campaign 150, `oos_edge_proven:false`, `edge_claim:NONE`.
- OOS: `reports/real_quote_volume_rqa_det_over_tt_ratio_shock_mr_costed_oos_20261107T105517Z.json` (sha `19c41b642506fe8ed002ee85905e34a2eb6906fc08f1ae7175e78d0ea13e8dbe`). `any_exposure_oos:true`; cross-asset net sums `fee0=+0.219286, fee5=-0.154714, fee10=-0.528714, fee20=-1.276714, fee40=-2.772714`; `all_cost_slices_positive_oos_net_sum:false`; `all_cost_slices_beat_bh_mean_rule:false`.
- Ingest: `reports/real_feed_ingest_attempt_20261107T105517Z.json` (sha `e8792bf5fdb47475004d2a50666cccd7aaa0b3124bfa03584867030e87b37128`).
- Registry: `reports/strategy_edge_registry_20261107T105517Z.json` (sha `bf44ee2026847640e468325f6a2b40e59a829b7b0a0aab68cf398fdd12209a37`, supersedes C149 `5cfc9cd4...`).
- Summary: `reports/campaign150_execution_summary_20261107T105517Z.json` (sha `b42ff1fe6168d7146fee70b76c5848efcc7922c6dde29f1d1a88230593a23ae9`).
- Script: `scripts/run_real_quote_volume_rqa_det_over_tt_ratio_shock_mr_costed_oos.py` (sha `28c21acea90720c65d0e24bb52ecb5aff32095475f6749ecba5a478b32d0caa7`). Distinctness grep hits pre=0 (re-verified; collision guard passed).

## Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rn 'tt_over_lmax|tt_lmax_ratio|rqa_ratio_tt_lmax|TT_OVER_LMAX' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l
```
Then implement and run the C151 `TT/L_max` (or collision-safe alternative) OOS script, emit ingest/registry/summary, and sync `research_state/state.yaml` to C151-done/C152-next. **Do not stop until C151 is properly complete with >=3 new artifacts and state.yaml synced. No status-only response.**
