# READ THIS FIRST — SINGLE DURABLE HANDOFF (20261107T134529Z)

Repo: `cryptoquantstatarbstrats` (crypto quant stat arb strategies).
**Prioritization (from repo name):** fail-closed, real-data-only stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. R-B proceeds on validated `real_quote_volume` regardless of nonspot ingest.

## INITIAL TASK FOR NEXT SESSION — C161 (MANDATORY, HEAVY WORK, START NOW)

C104–C160 DONE — do NOT rerun. `pytest` unavailable (honestly recorded — do not fabricate test results). `numpy/scipy/pandas` importable (verified). Caches present (`data/cache/volume_1h_full.{pkl,meta.json,provenance.json}`, `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.{pkl,meta.json}`).

**Readiness (run first, fail-closed):**
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'lmax_over_trend\|lmax_trend_ratio\|rqa_ratio_lmax_trend\|LMAX_OVER_TREND' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l   # must be 0 non-self (preselect grep 20261107T134336Z: 0) — RE-VERIFY at run time
```

**Primary C161 candidate (pre-selected — re-verify grep at run time):** `VOLUME_RQA_LMAX_OVER_TREND_RATIO_SHOCK_MR` — RQA ratio `RATIO_LMAX_TREND = L_max / TREND` (max diagonal line length normalized by RQA TREND slope) on delay-embedded log-volume returns (`m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`). Compute TREND as least-squares slope of recurrence point displacement (1-based index `j>=1` along each qualifying diagonal line, from its start) vs `j`, pooled over all qualifying diagonal-line recurrence points (k!=0, main diagonal excluded, `l>=l_min`); `L_max` = max length of qualifying diagonal lines. Fail-closed NaN/no-signal if `TREND==0` or undefined/non-finite (regression degenerate/insufficient qualifying diagonal points), `L_max<=0` or undefined/non-finite, no qualifying diagonal lines, offdiag/recurrence degenerate, or undefined. Distinct from C125–C160 (incl C160 `TREND/L_max` — inverse ratio but distinct feature/id/implementation/hypothesis; record explicit distinctness; C159 `TT/ENTR`, C158 `%LAM/L_max`, C157 `RR/ENTR`). **Re-verify grep at run time (collision guard). If LMAX/TREND collides, pick next distinct grep-zero alternative (`TREND/ENTR` — grep observed 0 hits 20261107T134336Z, fail-closed on `ENTR<=0/undefined/TREND` undefined-non-finite; or `ENTR/TREND` with fail-closed on `TREND==0/undefined-non-finite`, `ENTR<=0/undefined`), re-grep, and record chosen feature + grep evidence.**

Implement `scripts/run_real_quote_volume_rqa_lmax_over_trend_ratio_shock_mr_costed_oos.py` (or chosen alternative) modeled on C160/C159 scripts (copy WF/cost/B&H/SHA/report structure; change only feature computation, IDs, `pre_stated_distinctness`/refs to latest registry `reports/strategy_edge_registry_20261107T134336Z.json` sha `a58ce4fc7161ec10340d6ec1183deabd7cf647abd83ad890f32e59356eb1a86a` and C160 OOS sha `90e7d1b0aa2d41d8d8af2446c4f4d28d80f1d605343318cb612f9740a2a6e3c8`). Run it to emit `reports/real_quote_volume_rqa_lmax_over_trend_ratio_shock_mr_costed_oos_<UTC>.json` with all top-level gate fields (`oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`), `edge_claim: NONE`, `real_data_only:true`, `fail_closed:true`, and `pre_stated_distinctness` recording grep cmd/hits/evidence (and explicit distinctness from C160 inverse).

### Step 1 — Ingest + registry + summary (MANDATORY)
1. Ingest: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 161) — record nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume` family.
2. Registry: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261107T134336Z.json` (sha `a58ce4fc7161ec10340d6ec1183deabd7cf647abd83ad890f32e59356eb1a86a`). Structurally consistent `campaign/supersedes/supersedes_sha256/lineage/campaigns`; include prior context and add C161 with artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds. **Do not blindly copy stale preselected candidates — verify grep for C162 preselection.**
3. Summary: `reports/campaign161_execution_summary_<UTC>.json` listing all new artifact paths + sha256 (SHAs computed from bytes on disk): OOS, ingest, registry, script.
4. Sync `research_state/state.yaml`: `latest_campaign_done: C161`, `next_campaign: C162`, latest registry sha, latest OOS path/sha, `oos_edge_proven` from emitted report, `c162_preselected` with a distinct grep-verified RQA-ratio candidate not used in C125–C161.

## Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

## Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run (C161 collision guard required; record chosen feature + grep evidence + explicit distinctness from C160 inverse).
- **No status summary before >= 3 new concrete C161 report artifacts exist** (OOS + ingest + registry/summary).
- **Heavy work mandatory:** implement/run + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## Bottlenecks removed (confirmed 20261107T134336Z)
- C104–C160 locked; no reruns unchanged.
- C160 completed heavy; all artifacts emitted with disk-verified SHAs; state.yaml/HANDOFF synced to C160-done/C161-next.
- `numpy/scipy/pandas` importable.
- C160 primary `TREND/LMAX` collision guard grep = 0 hits (verified 20261107T130248Z). C161 primary `LMAX/TREND` grep = 0 hits (observed 20261107T134336Z). Alt1 `TREND/ENTR` grep = 0 hits (observed 20261107T134336Z).
- `"No status before >=3 new artifacts"` + mandatory run — forces heavy work for C161.
- `pytest` unavailable recorded honestly — do not fabricate test results.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## C160 result (locked, do not rerun)
- `VOLUME_RQA_TREND_OVER_LMAX_RATIO_SHOCK_MR` (TREND/L_max, diagonal recurrence TREND slope normalized by max diagonal line length), campaign 160, `oos_edge_proven:false`, `edge_claim:NONE`.
- OOS: `reports/real_quote_volume_rqa_trend_over_lmax_ratio_shock_mr_costed_oos_20261107T134222Z.json` (sha `90e7d1b0aa2d41d8d8af2446c4f4d28d80f1d605343318cb612f9740a2a6e3c8`). `any_exposure_oos:true`; cross-asset net sums `fee0=-0.4829222270252581, fee5=-0.7439222270252583, fee10=-1.0049222270252585, fee20=-1.5269222270252585, fee40=-2.5709222270252585`; `all_cost_slices_positive_oos_net_sum:false`; `all_cost_slices_beat_bh_mean_rule:false`.
- Ingest: `reports/real_feed_ingest_attempt_20261107T134336Z.json` (sha `0918bc2118456d1c2c327674e629bed5693bae397f4739c8043a6bc9ce53e94f`).
- Registry: `reports/strategy_edge_registry_20261107T134336Z.json` (sha `a58ce4fc7161ec10340d6ec1183deabd7cf647abd83ad890f32e59356eb1a86a`, supersedes C159 `5bbcc636054598db03cb34919db8a6e3e3fad86c73b02d36a90b7c6996176731`).
- Summary: `reports/campaign160_execution_summary_20261107T134336Z.json` (sha `3acab6893863b2cdf8234c283917f05ccfd428381eda69eb97d36160531ae0e4`).
- Script: `scripts/run_real_quote_volume_rqa_trend_over_lmax_ratio_shock_mr_costed_oos.py` (sha `eef5855fea616065610a2d756fbfa61e54132c1d93d2d42b74cd35a58001d13e`). Distinctness grep hits pre (non-self)=0.

## Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rn 'lmax_over_trend\|lmax_trend_ratio\|rqa_ratio_lmax_trend\|LMAX_OVER_TREND' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l
```
Then implement and run the C161 `LMAX/TREND` (or collision-safe alternative) OOS script, emit ingest/registry/summary, and sync `research_state/state.yaml` to C161-done/C162-next. **Do not stop until C161 is properly complete with >=3 new artifacts and state.yaml synced. No status-only response.**

(End of file)
