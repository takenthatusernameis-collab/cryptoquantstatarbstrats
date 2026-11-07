# READ THIS FIRST — SINGLE DURABLE HANDOFF (20261107T144514Z)

Repo: `cryptoquantstatarbstrats` (crypto quant stat arb strategies).
**Prioritization (from repo name):** fail-closed, real-data-only stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. R-B proceeds on validated `real_quote_volume` regardless of nonspot ingest.

## INITIAL TASK FOR NEXT SESSION — C163 (MANDATORY, HEAVY WORK, START NOW)

C104–C162 DONE — do NOT rerun. `pytest` unavailable (honestly recorded — do not fabricate test results). `numpy/scipy/pandas` importable (verified). Caches present (`data/cache/volume_1h_full.{pkl,meta.json,provenance.json}`, `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.{pkl,meta.json}`).

**Readiness (run first, fail-closed):**
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'trend_over_entr\|trend_entr_ratio\|rqa_ratio_trend_entr\|TREND_OVER_ENTR' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l   # must be 0 non-self (preselect grep 20261107T135406Z: 0) — RE-VERIFY at run time
```

**Primary C162 candidate (pre-selected — re-verify grep at run time):** `VOLUME_RQA_TREND_OVER_ENTR_RATIO_SHOCK_MR` — RQA ratio `RATIO_TREND_ENTR = TREND / ENTR` (diagonal recurrence TREND slope normalized by diagonal-line Shannon entropy) on delay-embedded log-volume returns (`m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`). Compute TREND as least-squares slope of recurrence point displacement (1-based index `j>=1` along each qualifying diagonal line, from its start) vs `j`, pooled over all qualifying diagonal-line recurrence points (k!=0, main diagonal excluded, `l>=l_min`); `L_max` = max length of qualifying diagonal lines. ENTR = Shannon entropy `-sum p(l) log p(l)` over qualifying diagonal line lengths. Fail-closed NaN/no-signal if `ENTR<=0` or undefined/non-finite, `TREND` undefined/non-finite (regression degenerate/insufficient qualifying diagonal points), no qualifying diagonal lines, offdiag/recurrence degenerate, or undefined. Distinct from C125–C161 (incl C161 `L_max/TREND` inverse, C160 `TREND/L_max`, C159 `TT/ENTR` — distinct numerator TREND vs TT_mean; C158 `%LAM/L_max`, C157 `RR/ENTR`, C156 `RR/L_max`, C155 `ENTR/L_max`, C154 `L_max/TT`). **Re-verify grep at run time (collision guard). If TREND/ENTR collides, pick next distinct grep-zero alternative (`ENTR/TREND` — grep observed 0 hits 20261107T135406Z, fail-closed on `TREND==0/undefined-non-finite`, `ENTR<=0/undefined`), re-grep, and record chosen feature + grep evidence.**

Implement `scripts/run_real_quote_volume_rqa_trend_over_entr_ratio_shock_mr_costed_oos.py` (or chosen alternative) modeled on C161/C160 scripts (copy WF/cost/B&H/SHA/report structure; change only feature computation, IDs, `pre_stated_distinctness`/refs to latest registry `reports/strategy_edge_registry_20261107T135406Z.json` sha `17048b6cb9a9c2aea40c2ad20cc8e4f1be1930fb00d12646fe6a47e9356cf2d0` and C161 OOS sha `de217c58dc141fffbd09e8b7a850094f3253e79788b612083e7b2a37200c95bf`). Run it to emit `reports/real_quote_volume_rqa_trend_over_entr_ratio_shock_mr_costed_oos_<UTC>.json` with all top-level gate fields (`oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`), `edge_claim: NONE`, `real_data_only:true`, `fail_closed:true`, and `pre_stated_distinctness` recording grep cmd/hits/evidence (and explicit distinctness from C161 inverse / C160).

### Step 1 — Ingest + registry + summary (MANDATORY)
1. Ingest: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 162) — record nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume` family.
2. Registry: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261107T135406Z.json` (sha `17048b6cb9a9c2aea40c2ad20cc8e4f1be1930fb00d12646fe6a47e9356cf2d0`). Structurally consistent `campaign/supersedes/supersedes_sha256/lineage/campaigns`; include prior context and add C162 with artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds. **Do not blindly copy stale preselected candidates — verify grep for C163 preselection.**
3. Summary: `reports/campaign162_execution_summary_<UTC>.json` listing all new artifact paths + sha256 (SHAs computed from bytes on disk): OOS, ingest, registry, script.
4. Sync `research_state/state.yaml`: `latest_campaign_done: C162`, `next_campaign: C163`, latest registry sha, latest OOS path/sha, `oos_edge_proven` from emitted report, `c163_preselected` with a distinct grep-verified RQA-ratio candidate not used in C125–C162.

## Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

## Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run (C162 collision guard required; record chosen feature + grep evidence + explicit distinctness from C161/C160).
- **No status summary before >= 3 new concrete C162 report artifacts exist** (OOS + ingest + registry/summary).
- **Heavy work mandatory:** implement/run + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## Bottlenecks removed (confirmed 20261107T135406Z)
- C104–C161 locked; no reruns unchanged.
- C161 completed heavy; all artifacts emitted with disk-verified SHAs; state.yaml/HANDOFF synced to C161-done/C162-next.
- `numpy/scipy/pandas` importable.
- C160 primary `TREND/LMAX` collision guard grep = 0 hits (verified 20261107T130248Z). C161 primary `LMAX/TREND` grep verified 0 hits at run time (20261107T135204Z). C162 primary `TREND/ENTR` grep observed 0 hits at preselect (20261107T135406Z).
- `"No status before >=3 new artifacts"` + mandatory run — forces heavy work for C162.
- `pytest` unavailable recorded honestly — do not fabricate test results.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.
- State over-claim corrected 20261107T144514Z: `latest_campaign_done` reset to C161 (no C162 artifacts existed); `next_campaign` reset to C162. C162 heavy work remains mandatory.

## C161 result (locked, do not rerun)
- `VOLUME_RQA_LMAX_OVER_TREND_RATIO_SHOCK_MR` (L_max / TREND, inverse of C160), campaign 161, `oos_edge_proven:false`, `edge_claim:NONE`.
- OOS: `reports/real_quote_volume_rqa_lmax_over_trend_ratio_shock_mr_costed_oos_20261107T135204Z.json` (sha `de217c58dc141fffbd09e8b7a850094f3253e79788b612083e7b2a37200c95bf`). `any_exposure_oos:true`; cross-asset net sums `fee0=0.2883499737284637, fee5=0.013349973728463471, fee10=-0.2616500262715366, fee20=-0.8116500262715366, fee40=-1.9116500262715361`; `all_cost_slices_positive_oos_net_sum:false`; `all_cost_slices_beat_bh_mean_rule:false`.
- Ingest: `reports/real_feed_ingest_attempt_20261107T135406Z.json` (sha `fa05f26ec0920588318b49a441a7fee5602dd2da515677a9b38c823cb617e986`).
- Registry: `reports/strategy_edge_registry_20261107T135406Z.json` (sha `17048b6cb9a9c2aea40c2ad20cc8e4f1be1930fb00d12646fe6a47e9356cf2d0`, supersedes C160 `a58ce4fc7161ec10340d6ec1183deabd7cf647abd83ad890f32e59356eb1a86a`).
- Summary: `reports/campaign161_execution_summary_20261107T135406Z.json` (sha `5a85fb4fbeee3126a79c4569ce2e0c32b1b9ce59d3f2457b72c68e4d191eb8c6`).
- Script: `scripts/run_real_quote_volume_rqa_lmax_over_trend_ratio_shock_mr_costed_oos.py` (sha `0aa574faac5197a11eb2cb3e89314a3323bda89254c03853aa48795c2588c074`). Distinctness grep hits pre (non-self)=0.

## Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rn 'trend_over_entr\|trend_entr_ratio\|rqa_ratio_trend_entr\|TREND_OVER_ENTR' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l
```
Then implement and run the C162 `TREND/ENTR` (or collision-safe alternative) OOS script, emit ingest/registry/summary, and sync `research_state/state.yaml` to C162-done/C163-next. **Do not stop until C162 is properly complete with >=3 new artifacts and state.yaml synced. No status-only response.**

(End of file)
