# READ THIS FIRST — SINGLE DURABLE HANDOFF (20261107T163607Z)

Repo: `cryptoquantstatarbstrats` (crypto quant stat arb strategies).
**Prioritization (from repo name):** fail-closed, real-data-only stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. R-B proceeds on validated `real_quote_volume` regardless of nonspot ingest.

## VERIFIED THIS SESSION (20261107T163607Z) — no reruns needed
- `numpy/scipy/pandas` importable. `pytest` unavailable (recorded honestly — do NOT fabricate test results).
- Real caches present + SHA-verified (from bytes): `data/cache/volume_1h_full.pkl` (4365895387de4e542165fd331e39da40d455a3de24c7254eb67ba890053d193c), `data/cache/volume_1h_full.meta.json` (4d321584d3c687ad9956908c0179a1eae7d629c296c491e1e5ad1259a890c616), `data/cache/volume_1h_full.provenance.json` (c7ff2f27ec5a668128e4856f809efde4922563dba87be0648be6d802c6d21c89), spot `0bab5d6a...631fcf7.pkl` (5607573327c089e0ab990ac48f931752a99e6e89f60599cb2557246f0f5f8c9b).
- C164 artifacts on disk with SHAs (verified): OOS `reports/real_quote_volume_rqa_lam_over_trend_ratio_shock_mr_costed_oos_20261107T163422Z.json` (d0f1e3c286dcac0f131891aa69d844f7d7656afaa2892742abf8b5354632b0e3), ingest `reports/real_feed_ingest_attempt_20261107T163607Z.json` (44ab77a188aa2f3ffd4454a4b32cf94eac59c058dc0af3aa8e4125fac98f23ce), registry `reports/strategy_edge_registry_20261107T163607Z.json` (62b25bde7526b02928df40c1a77bdf0a6930697cc4773640168024a20fa13e98), summary `reports/campaign164_execution_summary_20261107T163607Z.json` (6de78f49e0fb3c754b87112d59d8e87465be8a8f086628b4e3099bd8140d2727), script `scripts/run_real_quote_volume_rqa_lam_over_trend_ratio_shock_mr_costed_oos.py` (6855c2ec0ea2862c040f6524aa3074124b062cbc8f60d301fa6d832fc00aa388).
- **C165 preselection collision guard verified 0 hits** (20261107T163242Z): `trend_over_lam|rqa_ratio_trend_over_lam|TREND_OVER_LAM` over `scripts/ strategies/ backtest/ utils/`. Re-verify again at run time (0 non-self).

## C104–C164 DONE — LOCKED, do NOT rerun unchanged
- **C164 result (locked):** `VOLUME_RQA_LAM_OVER_TREND_RATIO_SHOCK_MR` (RQA ratio `%LAM/TREND`), `oos_edge_proven:false`, `edge_claim:NONE`. `any_exposure_oos:true`; cross-asset net sums `fee0=-0.1235243399224849, fee5=-0.41252433992248516, fee10=-0.7015243399224853, fee20=-1.2795243399224852, fee40=-2.435524339922485`; `all_cost_slices_positive_oos_net_sum:false`; `all_cost_slices_beat_bh_mean_rule:false`.
- Latest registry (superseding): `reports/strategy_edge_registry_20261107T163607Z.json` (62b25bde7526b02928df40c1a77bdf0a6930697cc4773640168024a20fa13e98, supersedes C163 b62a71b07...). Ingest: `reports/real_feed_ingest_attempt_20261107T163607Z.json` (44ab77a1...). No prior campaign reruns; no stale cache re-scans.

## INITIAL TASK FOR NEXT SESSION — C165 (MANDATORY, HEAVY WORK, START IMMEDIATELY)
**Timestamped directive (20261107T163607Z): execute C165 now. No status-only replies. No status summary before >= 3 new concrete C165 report artifacts exist on disk (OOS + ingest + registry/summary), each with SHA256 from bytes.**

**Primary C165 candidate (pre-selected — MUST re-verify grep at run time):** `VOLUME_RQA_TREND_OVER_LAM_RATIO_SHOCK_MR` — RQA ratio `TREND/%LAM` (diagonal recurrence TREND slope normalized by laminarity `%LAM`, fraction of recurrence points forming vertical lines with `l>=l_min`) shock on delay-embedded log-volume returns (`m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`), trailing/causal. Fail-closed NaN/no-signal if `%LAM==0` or undefined/non-finite, `TREND` undefined/non-finite, no qualifying vertical/diagonal lines as applicable, offdiag/recurrence degenerate, or undefined. Distinct from C125–C164 (incl C164 `%LAM/TREND` — inverse ratio, distinct numerator/denominator; C158 `%LAM/L_max` — different denominator; C160 `TREND/L_max` — different denominator `%LAM` vs `L_max`).

**Collision guard (run-time, required):**
```bash
grep -rn 'trend_over_lam|rqa_ratio_trend_over_lam|TREND_OVER_LAM' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l
```
Must be **0 non-self**. Verified 0 this session (20261107T163242Z). If collides, pick next distinct grep-zero alternative (`vmax_over_trend|rr_over_trend` verified 0 at 20261107T163242Z — re-verify), re-grep, and record chosen feature + grep evidence.

### Required C165 deliverables (all on disk, SHA256 from bytes)
1. **Implement/run OOS script** (model on C164): `scripts/run_real_quote_volume_rqa_trend_over_lam_ratio_shock_mr_costed_oos.py` (or collision-safe alternative). Change only feature computation, IDs, `pre_stated_distinctness`, and refs to latest registry `reports/strategy_edge_registry_20261107T163607Z.json` (62b25bde7526b02928df40c1a77bdf0a6930697cc4773640168024a20fa13e98) + C164 OOS sha `d0f1e3c286dcac0f131891aa69d844f7d7656afaa2892742abf8b5354632b0e3`. Emit `reports/real_quote_volume_rqa_trend_over_lam_ratio_shock_mr_costed_oos_<UTC>.json` with `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`, `edge_claim: NONE` unless rule holds, `real_data_only:true`, `fail_closed:true`, and `pre_stated_distinctness` (grep cmd/hits/evidence; explicit distinctness from C164/C160/C158).
2. **Ingest artifact:** `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 165) — nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`; include cache/provenance SHAs.
3. **Registry (superseding):** `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261107T163607Z.json` (62b25bde7526b02928df40c1a77bdf0a6930697cc4773640168024a20fa13e98). Structurally consistent lineage; include prior context + C165 artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds. **Verify grep for C166 preselection; do not copy stale candidates.**
4. **Summary:** `reports/campaign165_execution_summary_<UTC>.json` listing all new artifact paths + sha256 (from bytes on disk): OOS, ingest, registry, script.
5. **Sync state:** `research_state/state.yaml` → `latest_campaign_done: C165`, `next_campaign: C166`, latest registry sha, latest OOS path/sha, `oos_edge_proven` from emitted report, `c166_preselected` (distinct grep-verified RQA-ratio candidate not used in C125–C165, grep evidence recorded).

## Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

## Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run (C165 collision guard required; record evidence).
- **No status summary before >= 3 new concrete C165 report artifacts exist** (OOS + ingest + registry/summary).
- **Heavy work mandatory:** implement/run + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## Bottlenecks removed (confirmed 20261107T163607Z)
- C104–C164 locked; no reruns unchanged. C164 artifacts/SHA integrity verified.
- `numpy/scipy/pandas` importable; caches present. `pytest` unavailable recorded honestly — do not fabricate.
- C165 primary `TREND_OVER_LAM` grep verified **0 hits** this session (20261107T163242Z). Re-verify at run time.
- `"No status before >=3 new artifacts"` + mandatory heavy work enforced.
- Nonspot ingest does **NOT** block R-B on `real_quote_volume`.
- State is truthful (`latest_campaign_done: C164`, `next_campaign: C165`).

## Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'trend_over_lam|rqa_ratio_trend_over_lam|TREND_OVER_LAM' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l   # must be 0 non-self
```
Then implement/run C165 `TREND/%LAM` (or collision-safe alternative), emit ingest+registry+summary, sync `research_state/state.yaml` to C165-done/C166-next with a grep-verified C166 preselection. **Do not stop until C165 is properly complete with >=3 new artifacts and state.yaml synced.**
