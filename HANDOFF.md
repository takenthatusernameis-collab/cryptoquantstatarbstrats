# READ THIS FIRST — SINGLE DURABLE HANDOFF (20261107T173331Z)

Repo: `cryptoquantstatarbstrats` (crypto quant stat arb strategies).
**Prioritization (from repo name):** fail-closed, real-data-only stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. R-B proceeds on validated `real_quote_volume` regardless of nonspot ingest.

## VERIFIED THIS SESSION (20261107T164010Z) — no reruns needed
- `numpy/scipy/pandas` importable. `pytest` unavailable (recorded honestly — do NOT fabricate test results).
- Real caches present + SHA-verified (from bytes): `data/cache/volume_1h_full.pkl` (4365895387de4e542165fd331e39da40d455a3de24c7254eb67ba890053d193c), `data/cache/volume_1h_full.meta.json` (4d321584d3c687ad9956908c0179a1eae7d629c296c491e1e5ad1259a890c616), `data/cache/volume_1h_full.provenance.json` (c7ff2f27ec5a668128e4856f809efde4922563dba87be0648be6d802c6d21c89), spot `0bab5d6a...631fcf7.pkl` (5607573327c089e0ab990ac48f931752a99e6e89f60599cb2557246f0f5f8c9b).
- **C165 completed (this session)** — artifacts on disk with SHAs (verified): OOS `reports/real_quote_volume_rqa_trend_over_lam_ratio_shock_mr_costed_oos_20261107T163952Z.json` (9815814043ebb33c8b107e3e0a4d01538f8fc9738492850cc9bd6a8411858c6f), ingest `reports/real_feed_ingest_attempt_20261107T164010Z.json` (58ffb38dd33bab1118c6452bb2342dfb522ea83ee096d4d5bf8b53090102dc35), registry `reports/strategy_edge_registry_20261107T164010Z.json` (bc2c0f706547edfc14e38f66343c1fcdcf940b6a434dce530dd290371e6a588f), summary `reports/campaign165_execution_summary_20261107T164010Z.json` (438f292a63dfb48704b1e976e580cdeecd2cf28e58df8a0f272d8c571fd9b7e4), script `scripts/run_real_quote_volume_rqa_trend_over_lam_ratio_shock_mr_costed_oos.py` (21fa326afb1ae4b3ae2570a75023ba07f118bba1f6b68eeabdca59bb2640f047).
- **C165 pre-impl/run collision guard verified 0 hits** (20261107T163835Z): `trend_over_lam|rqa_ratio_trend_over_lam|TREND_OVER_LAM` over `scripts/ strategies/ backtest/ utils/`. **C166 preselection `VMAX_OVER_LAM` verified 0 hits** (20261107T164010Z): `vmax_over_lam|lam_over_vmax|VMAX_OVER_LAM|LAM_OVER_VMAX|rqa_ratio_vmax_over_lam|RQA_VMAX_OVER_LAM`. Re-verify again at run time (0 non-self).

## C104–C165 DONE — LOCKED, do NOT rerun unchanged
- **C165 result (locked):** `VOLUME_RQA_TREND_OVER_LAM_RATIO_SHOCK_MR` (RQA ratio `TREND/%LAM`), `oos_edge_proven:false`, `edge_claim:NONE`. `any_exposure_oos:true`; cross-asset net sums `fee0=0.1927125190268918, fee5=-0.08828748097310846, fee10=-0.36928748097310854, fee20=-0.9312874809731087, fee40=-2.0552874809731083`; `all_cost_slices_positive_oos_net_sum:false`; `all_cost_slices_beat_bh_mean_rule:false`.
- Latest registry (superseding): `reports/strategy_edge_registry_20261107T164010Z.json` (bc2c0f706547edfc14e38f66343c1fcdcf940b6a434dce530dd290371e6a588f, supersedes C164 62b25bde75...). Ingest: `reports/real_feed_ingest_attempt_20261107T164010Z.json` (58ffb38d...). No prior campaign reruns; no stale cache re-scans.

## INITIAL TASK FOR NEXT SESSION — C166 (MANDATORY, HEAVY WORK, START IMMEDIATELY)
**Timestamped directive (20261107T164010Z): execute C166 now. No status-only replies. No status summary before >= 3 new concrete C166 report artifacts exist on disk (OOS + ingest + registry/summary), each with SHA256 from bytes.**

**Primary C166 candidate (pre-selected — MUST re-verify grep at run time):** `VOLUME_RQA_VMAX_OVER_LAM_RATIO_SHOCK_MR` — RQA ratio `V_max/%LAM` (max vertical line length `V_max` normalized by laminarity `%LAM`, fraction of recurrence points forming vertical lines with `l>=l_min`) shock on delay-embedded log-volume returns (`m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`), trailing/causal. Fail-closed NaN/no-signal if `%LAM==0` or undefined/non-finite, `V_max` undefined/non-finite, no qualifying vertical lines, offdiag/recurrence degenerate, or undefined. Distinct from C125–C165 (incl C158 `%LAM/L_max` — inverse ratio, distinct numerator/denominator/strategy tokens; C157/C161 V_max vs L_max/TREND relations; C165 TREND/%LAM).

**Collision guard (run-time, required):**
```bash
grep -rn 'vmax_over_lam|lam_over_vmax|VMAX_OVER_LAM|LAM_OVER_VMAX|rqa_ratio_vmax_over_lam|RQA_VMAX_OVER_LAM' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l
```
Must be **0 non-self**. Verified 0 this session (20261107T164010Z). If collides, pick next distinct grep-zero alternative (`tt_over_trend` / `rr_over_trend` / `vmax_over_trend` verified 0 at 20261107T164010Z — re-verify), re-grep, and record chosen feature + grep evidence.

### Required C166 deliverables (all on disk, SHA256 from bytes)
1. **Implement/run OOS script** (model on C165): `scripts/run_real_quote_volume_rqa_vmax_over_lam_ratio_shock_mr_costed_oos.py` (or collision-safe alternative). Change only feature computation, IDs, `pre_stated_distinctness`, and refs to latest registry `reports/strategy_edge_registry_20261107T164010Z.json` (bc2c0f706547edfc14e38f66343c1fcdcf940b6a434dce530dd290371e6a588f) + C165 OOS sha `9815814043ebb33c8b107e3e0a4d01538f8fc9738492850cc9bd6a8411858c6f`. Emit `reports/real_quote_volume_rqa_vmax_over_lam_ratio_shock_mr_costed_oos_<UTC>.json` with `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`, `edge_claim: NONE` unless rule holds, `real_data_only:true`, `fail_closed:true`, and `pre_stated_distinctness` (grep cmd/hits/evidence; explicit distinctness from C158/C157/C161/C165 as relevant).
2. **Ingest artifact:** `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 166) — nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`; include cache/provenance SHAs.
3. **Registry (superseding):** `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261107T164010Z.json` (bc2c0f706547edfc14e38f66343c1fcdcf940b6a434dce530dd290371e6a588f). Structurally consistent lineage; include prior context + C166 artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds. **Verify grep for C167 preselection; do not copy stale candidates.**
4. **Summary:** `reports/campaign166_execution_summary_<UTC>.json` listing all new artifact paths + sha256 (from bytes on disk): OOS, ingest, registry, script.
5. **Sync state:** `research_state/state.yaml` → `latest_campaign_done: C166`, `next_campaign: C167`, latest registry sha, latest OOS path/sha, `oos_edge_proven` from emitted report, `c167_preselected` (distinct grep-verified RQA-ratio candidate not used in C125–C166, grep evidence recorded).

## Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

## Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run (C166 collision guard required; record evidence).
- **No status summary before >= 3 new concrete C166 report artifacts exist** (OOS + ingest + registry/summary).
- **Heavy work mandatory:** implement/run + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## Bottlenecks removed (confirmed 20261107T164010Z)
- C104–C165 locked; no reruns unchanged. C165 artifacts/SHA integrity verified.
- `numpy/scipy/pandas` importable; caches present. `pytest` unavailable recorded honestly — do not fabricate.
- C165 `TREND_OVER_LAM` grep verified **0 hits** pre-impl/run (20261107T163835Z). C166 `VMAX_OVER_LAM` grep verified **0 hits** (20261107T164010Z). Re-verify at run time.
- `"No status before >=3 new artifacts"` + mandatory heavy work enforced.
- Nonspot ingest does **NOT** block R-B on `real_quote_volume`.
- State is truthful (`latest_campaign_done: C165`, `next_campaign: C166`).

## Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'vmax_over_lam|lam_over_vmax|VMAX_OVER_LAM|LAM_OVER_VMAX|rqa_ratio_vmax_over_lam|RQA_VMAX_OVER_LAM' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l   # must be 0 non-self
```
Then implement/run C166 `V_max/%LAM` (or collision-safe alternative), emit ingest+registry+summary, sync `research_state/state.yaml` to C166-done/C167-next with a grep-verified C167 preselection. **Do not stop until C166 is properly complete with >=3 new artifacts and state.yaml synced.**
