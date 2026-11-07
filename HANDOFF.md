# READ THIS FIRST — SINGLE DURABLE HANDOFF (20261107T155739Z)

Repo: `cryptoquantstatarbstrats` (crypto quant stat arb strategies).
**Prioritization (from repo name):** fail-closed, real-data-only stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. R-B proceeds on validated `real_quote_volume` regardless of nonspot ingest.

## VERIFIED THIS SESSION (20261107T155739Z) — no reruns needed
- `numpy/scipy/pandas` importable. `pytest` unavailable (recorded honestly — do NOT fabricate test results).
- Real caches present + SHA-verified (from bytes): `data/cache/volume_1h_full.pkl` (4365895387de4e542165fd331e39da40d455a3de24c7254eb67ba890053d193c), `data/cache/volume_1h_full.meta.json` (4d321584d3c687ad9956908c0179a1eae7d629c296c491e1e5ad1259a890c616), `data/cache/volume_1h_full.provenance.json` (c7ff2f27ec5a668128e4856f809efde4922563dba87be0648be6d802c6d21c89), spot `0bab5d6a...631fcf7.pkl` (5607573327c089e0ab990ac48f931752a99e6e89f60599cb2557246f0f5f8c9b).
- C163 artifacts on disk with SHAs (verified): OOS `reports/real_quote_volume_rqa_entr_over_trend_ratio_shock_mr_costed_oos_20261107T155629Z.json` (1b2e6778d8087aa2ab133ead93ebde8c2d414077d2905e760b860724a40c1220), ingest `reports/real_feed_ingest_attempt_20261107T155739Z.json` (edfd66e22b2c843d32dd1c5e8c9f9542ec29ba92caf02907d4395b9db14082bd), registry `reports/strategy_edge_registry_20261107T155739Z.json` (b62a71b07e0b34c2ccb348b7163f5debd2ab57e95dbe7a0b42c3dc22558360fe), summary `reports/campaign163_execution_summary_20261107T155739Z.json` (acbd8a5060169ccee23c13d7fa2a4dd428391fba7bcd6dc502b94e502d6898f2), script `scripts/run_real_quote_volume_rqa_entr_over_trend_ratio_shock_mr_costed_oos.py` (125f12f177c74f32e538078304f7858ea45c5da96915ca4ccab9a4c5cc75b724).
- **C164 preselection collision guard verified 0 hits** (20261107T155739Z): `lam_over_trend|lam_trend_ratio|rqa_ratio_lam_trend|LAM_OVER_TREND` over `scripts/ strategies/ backtest/ utils/`. Re-verify again at run time (0 non-self).

## C104–C163 DONE — LOCKED, do NOT rerun unchanged
- **C163 result (locked):** `VOLUME_RQA_ENTR_OVER_TREND_RATIO_SHOCK_MR` (RQA ratio `ENTR/TREND`), `oos_edge_proven:false`, `edge_claim:NONE`. `any_exposure_oos:true`; cross-asset net sums `fee0=-0.5261356557443646, fee5=-0.960135655744365, fee10=-1.394135655744365, fee20=-2.2621356557443653, fee40=-3.998135655744365`; `all_cost_slices_positive_oos_net_sum:false`; `all_cost_slices_beat_bh_mean_rule:false`.
- Latest registry (superseding): `reports/strategy_edge_registry_20261107T155739Z.json` (b62a71b07e0b34c2ccb348b7163f5debd2ab57e95dbe7a0b42c3dc22558360fe, supersedes C162 02309b4b...). Ingest: `reports/real_feed_ingest_attempt_20261107T155739Z.json` (edfd66e2...). No prior campaign reruns; no stale cache re-scans.

## INITIAL TASK FOR NEXT SESSION — C164 (MANDATORY, HEAVY WORK, START IMMEDIATELY)
**Timestamped directive (20261107T155739Z): execute C164 now. No status-only replies. No status summary before >= 3 new concrete C164 report artifacts exist on disk (OOS + ingest + registry/summary), each with SHA256 from bytes.**

**Primary C164 candidate (pre-selected — MUST re-verify grep at run time):** `VOLUME_RQA_LAM_OVER_TREND_RATIO_SHOCK_MR` — RQA ratio `%LAM/TREND` (laminarity = fraction of recurrence points forming vertical lines with `l>=l_min`, normalized by diagonal recurrence TREND slope) shock on delay-embedded log-volume returns (`m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`), trailing/causal. Fail-closed NaN/no-signal if `TREND==0` or undefined/non-finite (regression degenerate/insufficient qualifying diagonal points), `%LAM` undefined/non-finite, no qualifying vertical/diagonal lines as applicable, offdiag/recurrence degenerate, or undefined. Distinct from C125–C163 (incl C158 `%LAM/L_max` — different denominator; C162 `TREND/ENTR`, C163 `ENTR/TREND`, C161 `L_max/TREND`, C160 `TREND/L_max` — different numerator `%LAM`).

**Collision guard (run-time, required):**
```bash
grep -rn 'lam_over_trend|lam_trend_ratio|rqa_ratio_lam_trend|LAM_OVER_TREND' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l
```
Must be **0 non-self**. Verified 0 this session (20261107T155739Z). If collides, pick next distinct grep-zero alternative (`vmax_over_trend|rr_over_trend|tt_over_trend` were 0 at 20261107T155739Z — re-verify), re-grep, and record chosen feature + grep evidence.

### Required C164 deliverables (all on disk, SHA256 from bytes)
1. **Implement/run OOS script** (model on C163): `scripts/run_real_quote_volume_rqa_lam_over_trend_ratio_shock_mr_costed_oos.py` (or collision-safe alternative). Change only feature computation, IDs, `pre_stated_distinctness`, and refs to latest registry `reports/strategy_edge_registry_20261107T155739Z.json` (b62a71b07e0b34c2ccb348b7163f5debd2ab57e95dbe7a0b42c3dc22558360fe) + C163 OOS sha `1b2e6778d8087aa2ab133ead93ebde8c2d414077d2905e760b860724a40c1220`. Emit `reports/real_quote_volume_rqa_lam_over_trend_ratio_shock_mr_costed_oos_<UTC>.json` with `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`, `edge_claim: NONE` unless rule holds, `real_data_only:true`, `fail_closed:true`, and `pre_stated_distinctness` (grep cmd/hits/evidence; explicit distinctness from C158/C160–C163).
2. **Ingest artifact:** `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 164) — nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`; include cache/provenance SHAs.
3. **Registry (superseding):** `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261107T155739Z.json` (b62a71b07e0b34c2ccb348b7163f5debd2ab57e95dbe7a0b42c3dc22558360fe). Structurally consistent lineage; include prior context + C164 artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds. **Verify grep for C165 preselection; do not copy stale candidates.**
4. **Summary:** `reports/campaign164_execution_summary_<UTC>.json` listing all new artifact paths + sha256 (from bytes on disk): OOS, ingest, registry, script.
5. **Sync state:** `research_state/state.yaml` → `latest_campaign_done: C164`, `next_campaign: C165`, latest registry sha, latest OOS path/sha, `oos_edge_proven` from emitted report, `c165_preselected` (distinct grep-verified RQA-ratio candidate not used in C125–C164, grep evidence recorded).

## Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

## Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run (C164 collision guard required; record evidence).
- **No status summary before >= 3 new concrete C164 report artifacts exist** (OOS + ingest + registry/summary).
- **Heavy work mandatory:** implement/run + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## Bottlenecks removed (confirmed 20261107T155739Z)
- C104–C163 locked; no reruns unchanged. C163 artifacts/SHA integrity verified.
- `numpy/scipy/pandas` importable; caches present. `pytest` unavailable recorded honestly — do not fabricate.
- C164 primary `LAM_OVER_TREND` grep verified **0 hits** this session (20261107T155739Z). Re-verify at run time.
- `"No status before >=3 new artifacts"` + mandatory heavy work enforced.
- Nonspot ingest does **NOT** block R-B on `real_quote_volume`.
- State is truthful (`latest_campaign_done: C163`, `next_campaign: C164`).

## Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'lam_over_trend|lam_trend_ratio|rqa_ratio_lam_trend|LAM_OVER_TREND' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l   # must be 0 non-self
```
Then implement/run C164 `%LAM/TREND` (or collision-safe alternative), emit ingest+registry+summary, sync `research_state/state.yaml` to C164-done/C165-next with a grep-verified C165 preselection. **Do not stop until C164 is properly complete with >=3 new artifacts and state.yaml synced.**
