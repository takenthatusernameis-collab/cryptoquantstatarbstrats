# READ THIS FIRST — SINGLE DURABLE HANDOFF (20261107T173330Z)

Repo: `cryptoquantstatarbstrats` (crypto quant stat arb strategies).
**Prioritization (from repo name):** fail-closed, real-data-only stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. R-B proceeds on validated `real_quote_volume` regardless of nonspot ingest.

## VERIFIED THIS SESSION (20261107T173330Z) — no reruns needed
- `numpy/scipy/pandas` importable. `pytest` unavailable (recorded honestly — do NOT fabricate test results).
- Real caches present + SHA-verified (from bytes): `data/cache/volume_1h_full.pkl` (4365895387de4e542165fd331e39da40d455a3de24c7254eb67ba890053d193c), `data/cache/volume_1h_full.meta.json` (4d321584d3c687ad9956908c0179a1eae7d629c296c491e1e5ad1259a890c616), `data/cache/volume_1h_full.provenance.json` (c7ff2f27ec5a668128e4856f809efde4922563dba87be0648be6d802c6d21c89), spot `0bab5d6a...631fcf7.pkl` (5607573327c089e0ab990ac48f931752a99e6e89f60599cb2557246f0f5f8c9b).
- **C166 completed (this session)** — artifacts on disk with SHAs (verified): OOS `reports/real_quote_volume_rqa_vmax_over_lam_ratio_shock_mr_costed_oos_20261107T164659Z.json` (87d630102068c8539e7eed8441d237db37d20fe14fbf515b6c4ee489357d467e), ingest `reports/real_feed_ingest_attempt_20261107T173330Z.json` (fb4bb81400d74036aa06526fb217f61b83232b27cf9f8c2353b446b4631ea128), registry `reports/strategy_edge_registry_20261107T173330Z.json` (f400501ed85c734d6f3093595b7594c631862af82c2fc28f58fbc7fd4d233762), summary `reports/campaign166_execution_summary_20261107T173330Z.json` (85d480312bb2db49206eea8a963a4d98c03845d972d8cef08723a1cf3ab4d691), script `scripts/run_real_quote_volume_rqa_vmax_over_lam_ratio_shock_mr_costed_oos.py` (b2fed7637425d530900fd1fd8b731c4be40434d975736e94e92a50939c44f2f8).
- **C166 collision guard:** `VMAX_OVER_LAM` grep returned 0 hits across `scripts/ strategies/ backtest/ utils/` before implementation existed (run-time requirement satisfied). **C167 preselection `TT_OVER_TREND` verified 0 hits** (20261107T173330Z): `tt_over_trend|trend_over_tt|TT_OVER_TREND|TREND_OVER_TT|rqa_ratio_tt_over_trend|RQA_TT_OVER_TREND`. Re-verify again at run time (0 non-self).

## C104–C166 DONE — LOCKED, do NOT rerun unchanged
- **C166 result (locked):** `VOLUME_RQA_VMAX_OVER_LAM_RATIO_SHOCK_MR` (RQA ratio `V_max/%LAM`), `oos_edge_proven:false`, `edge_claim:NONE`. `any_exposure_oos:true`; cross-asset net sums `fee0=0.1198857017085776, fee5=-0.2651142982914227, fee10=-0.6501142982914228, fee20=-1.4201142982914225, fee40=-2.9601142982914226`; `all_cost_slices_positive_oos_net_sum:false`; `all_cost_slices_beat_bh_mean_rule:false`.
- Latest registry (superseding): `reports/strategy_edge_registry_20261107T173330Z.json` (f400501ed85c734d6f3093595b7594c631862af82c2fc28f58fbc7fd4d233762, supersedes C165 bc2c0f706547edfc14e38f66343c1fcdcf940b6a434dce530dd290371e6a588f). Ingest: `reports/real_feed_ingest_attempt_20261107T173330Z.json` (fb4bb81400d74036aa06526fb217f61b83232b27cf9f8c2353b446b4631ea128). No prior campaign reruns; no stale cache re-scans.

## INITIAL TASK FOR NEXT SESSION — C167 (MANDATORY, HEAVY WORK, START IMMEDIATELY)
**Timestamped directive (20261107T173330Z): execute C167 now. No status-only replies. No status summary before >= 3 new concrete C167 report artifacts exist on disk (OOS + ingest + registry/summary), each with SHA256 from bytes.**

**Primary C167 candidate (pre-selected — MUST re-verify grep at run time):** `VOLUME_RQA_TT_OVER_TREND_RATIO_SHOCK_MR` — RQA ratio `TT/TREND` (trapping time `TT` = mean vertical-line length among qualifying `l>=l_min`, normalized by `TREND` determinism) shock on delay-embedded log-volume returns (`m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`), trailing/causal. Fail-closed NaN/no-signal if `TREND==0` or undefined/non-finite, `TT` undefined/non-finite, no qualifying vertical lines, offdiag/recurrence degenerate, or undefined. Distinct from C125–C166 (incl C165 `TREND/%LAM` — inverse/related numerator-denominator family tokens differ; explicit `TT_OVER_TREND` tokens verified absent).

**Collision guard (run-time, required):**
```bash
grep -rn 'tt_over_trend|trend_over_tt|TT_OVER_TREND|TREND_OVER_TT|rqa_ratio_tt_over_trend|RQA_TT_OVER_TREND' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l
```
Must be **0 non-self**. Verified 0 this session (20261107T173330Z). If collides, pick next distinct grep-zero alternative (`rr_over_trend` / `vmax_over_trend` verified 0 at 20261107T173330Z — re-verify), re-grep, and record chosen feature + grep evidence.

### Required C167 deliverables (all on disk, SHA256 from bytes)
1. **Implement/run OOS script** (model on C166): `scripts/run_real_quote_volume_rqa_tt_over_trend_ratio_shock_mr_costed_oos.py` (or collision-safe alternative). Change only feature computation, IDs, `pre_stated_distinctness`, and refs to latest registry `reports/strategy_edge_registry_20261107T173330Z.json` (f400501ed85c734d6f3093595b7594c631862af82c2fc28f58fbc7fd4d233762) + C166 OOS sha `87d630102068c8539e7eed8441d237db37d20fe14fbf515b6c4ee489357d467e`. Emit `reports/real_quote_volume_rqa_tt_over_trend_ratio_shock_mr_costed_oos_<UTC>.json` with `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`, `edge_claim: NONE` unless rule holds, `real_data_only:true`, `fail_closed:true`, and `pre_stated_distinctness` (grep cmd/hits/evidence; explicit distinctness from C165/C166 and prior TT/TREND-related families as relevant).
2. **Ingest artifact:** `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 167) — nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`; include cache/provenance SHAs.
3. **Registry (superseding):** `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261107T173330Z.json` (f400501ed85c734d6f3093595b7594c631862af82c2fc28f58fbc7fd4d233762). Structurally consistent lineage; include prior context + C167 artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds. **Verify grep for C168 preselection; do not copy stale candidates.**
4. **Summary:** `reports/campaign167_execution_summary_<UTC>.json` listing all new artifact paths + sha256 (from bytes on disk): OOS, ingest, registry, script.
5. **Sync state:** `research_state/state.yaml` → `latest_campaign_done: C167`, `next_campaign: C168`, latest registry sha, latest OOS path/sha, `oos_edge_proven` from emitted report, `c168_preselected` (distinct grep-verified RQA-ratio candidate not used in C125–C167, grep evidence recorded).

## Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

## Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run (C167 collision guard required; record evidence).
- **No status summary before >= 3 new concrete C167 report artifacts exist** (OOS + ingest + registry/summary).
- **Heavy work mandatory:** implement/run + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## Bottlenecks removed (confirmed 20261107T173330Z)
- C104–C166 locked; no reruns unchanged. C166 artifacts/SHA integrity verified.
- `numpy/scipy/pandas` importable; caches present. `pytest` unavailable recorded honestly — do not fabricate.
- C166 `VMAX_OVER_LAM` collision guard satisfied (0 hits before implementation). C167 `TT_OVER_TREND` grep verified **0 hits** (20261107T173330Z). Re-verify at run time.
- `"No status before >=3 new artifacts"` + mandatory heavy work enforced.
- Nonspot ingest does **NOT** block R-B on `real_quote_volume`.
- State is truthful (`latest_campaign_done: C166`, `next_campaign: C167`).

## Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'tt_over_trend|trend_over_tt|TT_OVER_TREND|TREND_OVER_TT|rqa_ratio_tt_over_trend|RQA_TT_OVER_TREND' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l   # must be 0 non-self
```
Then implement/run C167 `TT/TREND` (or collision-safe alternative), emit ingest+registry+summary, sync `research_state/state.yaml` to C167-done/C168-next with a grep-verified C168 preselection. **Do not stop until C167 is properly complete with >=3 new artifacts and state.yaml synced.**
