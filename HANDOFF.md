# READ THIS FIRST — SINGLE DURABLE HANDOFF (20261107T114824Z)

Repo: `cryptoquantstatarbstrats` (crypto quant stat arb strategies).
**Prioritization (from repo name):** fail-closed, real-data-only stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. R-B proceeds on validated `real_quote_volume` regardless of nonspot ingest.

## INITIAL TASK FOR NEXT SESSION — C154 (MANDATORY, HEAVY WORK, START NOW)

C104–C153 DONE — do NOT rerun. `pytest` unavailable (honestly recorded — do not fabricate test results). `numpy/scipy/pandas` importable. Caches present (`data/cache/volume_1h_full.{pkl,meta.json,provenance.json}`, `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.{pkl,meta.json}`).

**Readiness (run first, fail-closed):**
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'lmax_over_tt|lmax_tt_ratio|rqa_ratio_lmax_tt|LMAX_OVER_TT' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l   # must be 0 non-self
```

**Primary C154 candidate (pre-selected — re-verify at run time):** `VOLUME_RQA_LMAX_OVER_TT_RATIO_SHOCK_MR` — RQA ratio `RATIO_LMAX_TT = L_max / TT_mean` (max diagonal line length normalized by mean trapping time) on delay-embedded log-volume returns (`m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`). `L_max` = max qualifying diagonal-line length; `TT_mean` = mean qualifying vertical-line length. Fail-closed NaN/no-signal if `TT<=0`, no qualifying vertical lines, `L_max` undefined/non-finite, offdiag/recurrence degenerate. Distinct from C125–C153 (incl C153 ENTR/TT, C152 TT/%DET, C151 TT/L_max, C150 %DET/TT). **Re-verify grep at run time (collision guard). If collision, pick next distinct alternative (`VOLUME_RQA_DET_OVER_TT_RATIO_SHOCK_MR` `%DET/TT` fail-closed on `TT<=0`/no qualifying vertical lines/`%DET` undefined/non-finite; or `VOLUME_RQA_ENTR_OVER_LMAX_RATIO_SHOCK_MR` `ENTR/L_max` fail-closed on `L_max<=0`/no qualifying diagonal lines/`ENTR` undefined/non-finite), re-grep, and record chosen feature + grep evidence.**

Implement `scripts/run_real_quote_volume_rqa_lmax_over_tt_ratio_shock_mr_costed_oos.py` (or chosen alternative) modeled on C153/C152 scripts (copy WF/cost/B&H/SHA/report structure; change only feature computation, IDs, `pre_stated_distinctness`/refs to latest registry `strategy_edge_registry_20261107T114824Z.json` sha `98aa65897fac28b12f62c315627211242955eae82509923b1dc58a63ab39e606` and C153 OOS sha `1ae4628b44ed86249c0ea655505993aa42a079b9cb56d5f1276a227e34d160f8`). Run it to emit `reports/real_quote_volume_rqa_lmax_over_tt_ratio_shock_mr_costed_oos_<UTC>.json` with all top-level gate fields (`oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`), `edge_claim: NONE`, `real_data_only:true`, `fail_closed:true`, and `pre_stated_distinctness` recording grep cmd/hits/evidence.

### Step 1 — Ingest + registry + summary (MANDATORY)
1. Ingest: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 154) — record nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume` family.
2. Registry: `reports/strategy_edge_registry_<UTC>.json` superseding `strategy_edge_registry_20261107T114824Z.json` (sha `98aa65897fac28b12f62c315627211242955eae82509923b1dc58a63ab39e606`). Structurally consistent `campaign/supersedes/supersedes_sha256/lineage/campaigns`; include prior context and add C154 with artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds.
3. Summary: `reports/campaign154_execution_summary_<UTC>.json` listing all new artifact paths + sha256 (SHAs computed from bytes on disk): OOS, ingest, registry, script.
4. Sync `research_state/state.yaml`: `latest_campaign_done: C154`, `next_campaign: C155`, latest registry sha, latest OOS path/sha, `oos_edge_proven` from emitted report, `c155_preselected` with a distinct grep-verified RQA-ratio candidate not used in C125–C154.

## Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

## Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run (C154 collision guard required; record chosen feature + grep evidence).
- **No status summary before >= 3 new concrete C154 report artifacts exist** (OOS + ingest + registry/summary).
- **Heavy work mandatory:** implement/run + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## Bottlenecks removed (confirmed 20261107T114824Z)
- C104–C152 locked; no reruns unchanged.
- C153 completed heavy; all artifacts emitted with disk-verified SHAs; state.yaml/HANDOFF synced to C153-done/C154-next.
- `numpy/scipy/pandas` importable.
- C154 primary pre-selected: `VOLUME_RQA_LMAX_OVER_TT_RATIO_SHOCK_MR` (`L_max/TT_mean`) — grep pre-verified 0 hits now; re-verify at run time.
- `"No status before >=3 new artifacts"` + mandatory run — forces heavy work for C154.
- `pytest` unavailable recorded honestly — do not fabricate test results.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## C153 result (locked, do not rerun)
- `VOLUME_RQA_ENTR_OVER_TT_RATIO_SHOCK_MR` (ENTR/TT_mean), campaign 153, `oos_edge_proven:false`, `edge_claim:NONE`.
- OOS: `reports/real_quote_volume_rqa_entr_over_tt_ratio_shock_mr_costed_oos_20261107T114824Z.json` (sha `1ae4628b44ed86249c0ea655505993aa42a079b9cb56d5f1276a227e34d160f8`). `any_exposure_oos:true`; cross-asset net sums `fee0=0.2829280166686726, fee5=-0.08807198333132768, fee10=-0.4590719833313277, fee20=-1.2010719833313275, fee40=-2.6850719833313277`; `all_cost_slices_positive_oos_net_sum:false`; `all_cost_slices_beat_bh_mean_rule:false`.
- Ingest: `reports/real_feed_ingest_attempt_20261107T114824Z.json` (sha `8d941a8863552bf95a209193767d113401553ce4d1d04dd008aaf364255b9769`).
- Registry: `reports/strategy_edge_registry_20261107T114824Z.json` (sha `98aa65897fac28b12f62c315627211242955eae82509923b1dc58a63ab39e606`, supersedes C152 `5b6747eddcf088d0c1f1faa544ab5638d19e0f4fbebf9e68dde41e6eec02bd3e`).
- Summary: `reports/campaign153_execution_summary_20261107T114824Z.json` (sha `82fb372bcb0c7447364563efcd1d761bc6d1b707cf1e6d77abf6273eb25ed54a`).
- Script: `scripts/run_real_quote_volume_rqa_entr_over_tt_ratio_shock_mr_costed_oos.py` (sha `ce676261959840878cdee5196a15fa02120d7225ff5e39b4da6cf6cd9b71ed91`). Distinctness grep hits pre=0 (re-verified; collision guard passed).

## Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rn 'lmax_over_tt|lmax_tt_ratio|rqa_ratio_lmax_tt|LMAX_OVER_TT' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l
```
Then implement and run the C154 `L_max/TT_mean` (or collision-safe alternative) OOS script, emit ingest/registry/summary, and sync `research_state/state.yaml` to C154-done/C155-next. **Do not stop until C154 is properly complete with >=3 new artifacts and state.yaml synced. No status-only response.**

(End of file)
