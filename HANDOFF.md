# READ THIS FIRST — SINGLE DURABLE HANDOFF (20261107T125332Z)

Repo: `cryptoquantstatarbstrats` (crypto quant stat arb strategies).
**Prioritization (from repo name):** fail-closed, real-data-only stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. R-B proceeds on validated `real_quote_volume` regardless of nonspot ingest.

## INITIAL TASK FOR NEXT SESSION — C158 (MANDATORY, HEAVY WORK, START NOW)

C104–C157 DONE — do NOT rerun. `pytest` unavailable (honestly recorded — do not fabricate test results). `numpy/scipy/pandas` importable (verified 20261107T125332Z). Caches present (`data/cache/volume_1h_full.{pkl,meta.json,provenance.json}`, `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.{pkl,meta.json}`).

**Readiness (run first, fail-closed):**
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'lam_over_lmax|lam_lmax_ratio|rqa_ratio_lam_lmax|LAM_OVER_LMAX' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l   # must be 0 non-self (re-verified 20261107T125332Z: 0)
```

**Primary C158 candidate (pre-selected — re-verify grep at run time):** `VOLUME_RQA_LAM_OVER_LMAX_RATIO_SHOCK_MR` — RQA ratio `RATIO_LAM_LMAX = %LAM / L_max` (laminarity normalized by max diagonal line length) on delay-embedded log-volume returns (`m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2,l_min_v=2`). `%LAM` = laminarity = fraction of recurrence points forming vertical lines of length >= `l_min_v` (off-diagonal context consistent with prior RQA measures). `L_max` = max length of qualifying diagonal lines (`k!=0`, main diagonal excluded, `l>=l_min`). Fail-closed NaN/no-signal if `L_max<=0` or undefined/non-finite, no qualifying diagonal lines, `%LAM` undefined/non-finite, offdiag/recurrence degenerate, or undefined. Distinct from C125–C157 (incl C157 RR/ENTR, C156 RR/L_max, C155 ENTR/L_max, C154 L_max/TT). **Re-verify grep at run time (collision guard). If collision, pick next distinct alternative (`VOLUME_RQA_TT_OVER_ENTR_RATIO_SHOCK_MR` `TT_mean/ENTR`, fail-closed on `ENTR<=0`/undefined/`TT_mean` undefined-no qualifying vertical lines/recurrence degenerate; or `VOLUME_RQA_RR_OVER_TT_RATIO_SHOCK_MR` `RR/TT_mean`, fail-closed on `TT_mean<=0`/undefined/`RR` undefined-non-finite/offdiag-degenerate), re-grep, and record chosen feature + grep evidence.**

Implement `scripts/run_real_quote_volume_rqa_lam_over_lmax_ratio_shock_mr_costed_oos.py` (or chosen alternative) modeled on C156/C157 scripts (copy WF/cost/B&H/SHA/report structure; change only feature computation, IDs, `pre_stated_distinctness`/refs to latest registry `strategy_edge_registry_20261107T125008Z.json` sha `d81d357c87181624d79875d50d7c012c0ed4bdda29f8174e6bd29c9ae8132bfe` and C157 OOS sha `180c48ba89554b1f9be8a0fda710e06d92850cb5bd0a9c331180a28437f84a1d`). Run it to emit `reports/real_quote_volume_rqa_lam_over_lmax_ratio_shock_mr_costed_oos_<UTC>.json` with all top-level gate fields (`oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`), `edge_claim: NONE`, `real_data_only:true`, `fail_closed:true`, and `pre_stated_distinctness` recording grep cmd/hits/evidence.

### Step 1 — Ingest + registry + summary (MANDATORY)
1. Ingest: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 158) — record nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume` family.
2. Registry: `reports/strategy_edge_registry_<UTC>.json` superseding `strategy_edge_registry_20261107T125008Z.json` (sha `d81d357c87181624d79875d50d7c012c0ed4bdda29f8174e6bd29c9ae8132bfe`). Structurally consistent `campaign/supersedes/supersedes_sha256/lineage/campaigns`; include prior context and add C158 with artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds.
3. Summary: `reports/campaign158_execution_summary_<UTC>.json` listing all new artifact paths + sha256 (SHAs computed from bytes on disk): OOS, ingest, registry, script.
4. Sync `research_state/state.yaml`: `latest_campaign_done: C158`, `next_campaign: C159`, latest registry sha, latest OOS path/sha, `oos_edge_proven` from emitted report, `c159_preselected` with a distinct grep-verified RQA-ratio candidate not used in C125–C158.

## Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

## Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run (C158 collision guard required; record chosen feature + grep evidence).
- **No status summary before >= 3 new concrete C158 report artifacts exist** (OOS + ingest + registry/summary).
- **Heavy work mandatory:** implement/run + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## Bottlenecks removed (confirmed 20261107T125332Z)
- C104–C157 locked; no reruns unchanged.
- C157 completed heavy; all artifacts emitted with disk-verified SHAs; state.yaml/HANDOFF synced to C157-done/C158-next.
- `numpy/scipy/pandas` importable (verified 20261107T125332Z).
- C158 primary `%LAM/L_max` collision guard grep = 0 hits (re-verified 20261107T125332Z).
- `"No status before >=3 new artifacts"` + mandatory run — forces heavy work for C158.
- `pytest` unavailable recorded honestly — do not fabricate test results.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## C157 result (locked, do not rerun)
- `VOLUME_RQA_RR_OVER_ENTR_RATIO_SHOCK_MR` (RR/ENTR), campaign 157, `oos_edge_proven:false`, `edge_claim:NONE`.
- OOS: `reports/real_quote_volume_rqa_rr_over_entr_ratio_shock_mr_costed_oos_20261107T124940Z.json` (sha `180c48ba89554b1f9be8a0fda710e06d92850cb5bd0a9c331180a28437f84a1d`). `any_exposure_oos:true`; cross-asset net sums `fee0=-0.28564102255990675, fee5=-0.6926410225599071, fee10=-1.0996410225599074, fee20=-1.9136410225599072, fee40=-3.5416410225599066`; `all_cost_slices_positive_oos_net_sum:false`; `all_cost_slices_beat_bh_mean_rule:false`.
- Ingest: `reports/real_feed_ingest_attempt_20261107T125008Z.json` (sha `2f139c7d025a7b870f84eabfb83e944600fce8654c6ccf73e9620812e119b21b`).
- Registry: `reports/strategy_edge_registry_20261107T125008Z.json` (sha `d81d357c87181624d79875d50d7c012c0ed4bdda29f8174e6bd29c9ae8132bfe`, supersedes C156 `c6248481e3b747d0b2e864c442fcd092a8ed669e364e30a9a9796451a984d8c9`).
- Summary: `reports/campaign157_execution_summary_20261107T125008Z.json` (sha `275a1bb0f9d13fd43f16c228e93de57fd8cf7138a84ac01b7511f5541cedab8a`).
- Script: `scripts/run_real_quote_volume_rqa_rr_over_entr_ratio_shock_mr_costed_oos.py` (sha `6e7689e77a7a4ac43c2cad29f425eff5fea682008698de10bea2b0b59e1db690`). Distinctness grep hits pre (non-self)=0.

## Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rn 'lam_over_lmax|lam_lmax_ratio|rqa_ratio_lam_lmax|LAM_OVER_LMAX' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l
```
Then implement and run the C158 `%LAM/L_max` (or collision-safe alternative) OOS script, emit ingest/registry/summary, and sync `research_state/state.yaml` to C158-done/C159-next. **Do not stop until C158 is properly complete with >=3 new artifacts and state.yaml synced. No status-only response.**

(End of file)
