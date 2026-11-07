# READ THIS FIRST — SINGLE DURABLE HANDOFF (20261107T125747Z)

Repo: `cryptoquantstatarbstrats` (crypto quant stat arb strategies).
**Prioritization (from repo name):** fail-closed, real-data-only stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. R-B proceeds on validated `real_quote_volume` regardless of nonspot ingest.

## INITIAL TASK FOR NEXT SESSION — C159 (MANDATORY, HEAVY WORK, START NOW)

C104–C158 DONE — do NOT rerun. `pytest` unavailable (honestly recorded — do not fabricate test results). `numpy/scipy/pandas` importable (verified 20261107T125747Z). Caches present (`data/cache/volume_1h_full.{pkl,meta.json,provenance.json}`, `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.{pkl,meta.json}`).

**Readiness (run first, fail-closed):**
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'tt_over_entr|tt_entr_ratio|rqa_ratio_tt_entr|TT_OVER_ENTR' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l   # must be 0 non-self (re-verified 20261107T125747Z: 0)
```

**Primary C159 candidate (pre-selected — re-verify grep at run time):** `VOLUME_RQA_TT_OVER_ENTR_RATIO_SHOCK_MR` — RQA ratio `RATIO_TT_ENTR = TT_mean / ENTR` (mean trapping time normalized by diagonal-line Shannon entropy) on delay-embedded log-volume returns (`m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2,l_min_v=2`). `TT_mean` = mean length of qualifying vertical lines (`l>=l_min_v`, off-diagonal context consistent with prior RQA measures). `ENTR` = Shannon entropy (natural log) over qualifying diagonal-line length distribution (`k!=0`, main diagonal excluded, `l>=l_min`), `p(l)=n(l)/N`. Fail-closed NaN/no-signal if `ENTR<=0` or undefined/non-finite, no qualifying diagonal lines/distribution, `TT_mean` undefined/no qualifying vertical lines, offdiag/recurrence degenerate, or undefined. Distinct from C125–C158 (incl C158 `%LAM/L_max`, C157 `RR/ENTR`, C156 `RR/L_max`, C155 `ENTR/L_max`, C154 `L_max/TT`, C153 `ENTR/TT`). **Re-verify grep at run time (collision guard). If collision, pick next distinct alternative (`VOLUME_RQA_RR_OVER_LAM_RATIO_SHOCK_MR` `RR/%LAM`, fail-closed on `%LAM<=0`/undefined/`RR` undefined-non-finite/offdiag-degenerate; or `VOLUME_RQA_ENTR_OVER_LAM_RATIO_SHOCK_MR` `ENTR/%LAM`, fail-closed on `%LAM<=0`/undefined/`ENTR` undefined-no qualifying diagonal lines), re-grep, and record chosen feature + grep evidence.**

Implement `scripts/run_real_quote_volume_rqa_tt_over_entr_ratio_shock_mr_costed_oos.py` (or chosen alternative) modeled on C158/C157 scripts (copy WF/cost/B&H/SHA/report structure; change only feature computation, IDs, `pre_stated_distinctness`/refs to latest registry `strategy_edge_registry_20261107T125747Z.json` sha `3de80723ef0eb0de7834aa45e31bfab358c0b4dfe0c0ea159d2b3fc5f4e913c4` and C158 OOS sha `dafaf02ec2aababedef91c6ef7d6630d1a7857ab3725d7a7b1591d7f28d065f5`). Run it to emit `reports/real_quote_volume_rqa_tt_over_entr_ratio_shock_mr_costed_oos_<UTC>.json` with all top-level gate fields (`oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`), `edge_claim: NONE`, `real_data_only:true`, `fail_closed:true`, and `pre_stated_distinctness` recording grep cmd/hits/evidence.

### Step 1 — Ingest + registry + summary (MANDATORY)
1. Ingest: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 159) — record nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume` family.
2. Registry: `reports/strategy_edge_registry_<UTC>.json` superseding `strategy_edge_registry_20261107T125747Z.json` (sha `3de80723ef0eb0de7834aa45e31bfab358c0b4dfe0c0ea159d2b3fc5f4e913c4`). Structurally consistent `campaign/supersedes/supersedes_sha256/lineage/campaigns`; include prior context and add C159 with artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds.
3. Summary: `reports/campaign159_execution_summary_<UTC>.json` listing all new artifact paths + sha256 (SHAs computed from bytes on disk): OOS, ingest, registry, script.
4. Sync `research_state/state.yaml`: `latest_campaign_done: C159`, `next_campaign: C160`, latest registry sha, latest OOS path/sha, `oos_edge_proven` from emitted report, `c160_preselected` with a distinct grep-verified RQA-ratio candidate not used in C125–C159.

## Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

## Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run (C159 collision guard required; record chosen feature + grep evidence).
- **No status summary before >= 3 new concrete C159 report artifacts exist** (OOS + ingest + registry/summary).
- **Heavy work mandatory:** implement/run + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## Bottlenecks removed (confirmed 20261107T125747Z)
- C104–C158 locked; no reruns unchanged.
- C158 completed heavy; all artifacts emitted with disk-verified SHAs; state.yaml/HANDOFF synced to C158-done/C159-next.
- `numpy/scipy/pandas` importable (verified 20261107T125747Z).
- C159 primary `TT/ENTR` collision guard grep = 0 hits (re-verified 20261107T125747Z). (`RR/TT` and `%LAM/ENTR` have non-zero grep hits in repo — do not use as primary without careful recheck.)
- `"No status before >=3 new artifacts"` + mandatory run — forces heavy work for C159.
- `pytest` unavailable recorded honestly — do not fabricate test results.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## C158 result (locked, do not rerun)
- `VOLUME_RQA_LAM_OVER_LMAX_RATIO_SHOCK_MR` (%LAM/L_max), campaign 158, `oos_edge_proven:false`, `edge_claim:NONE`.
- OOS: `reports/real_quote_volume_rqa_lam_over_lmax_ratio_shock_mr_costed_oos_20261107T125625Z.json` (sha `dafaf02ec2aababedef91c6ef7d6630d1a7857ab3725d7a7b1591d7f28d065f5`). `any_exposure_oos:true`; cross-asset net sums `fee0=-0.6419975574836658, fee5=-0.9869975574836661, fee10=-1.3319975574836662, fee20=-2.021997557483666, fee40=-3.401997557483666`; `all_cost_slices_positive_oos_net_sum:false`; `all_cost_slices_beat_bh_mean_rule:false`.
- Ingest: `reports/real_feed_ingest_attempt_20261107T125747Z.json` (sha `d69c84c9427309f5f8844693660454bbb2a06e2573feb5e5b5c6934015071e12`).
- Registry: `reports/strategy_edge_registry_20261107T125747Z.json` (sha `3de80723ef0eb0de7834aa45e31bfab358c0b4dfe0c0ea159d2b3fc5f4e913c4`, supersedes C157 `d81d357c87181624d79875d50d7c012c0ed4bdda29f8174e6bd29c9ae8132bfe`).
- Summary: `reports/campaign158_execution_summary_20261107T125747Z.json` (sha `ef983b0452e5ce01bebbb1151cf596b50aab8dd67a681ea5dc50f909f4cae067`).
- Script: `scripts/run_real_quote_volume_rqa_lam_over_lmax_ratio_shock_mr_costed_oos.py` (sha `d80cff093c7e1ef86a77d4d8fc02d3411d1f43156a0bb1359fea13e69475c955`). Distinctness grep hits pre (non-self)=0.

## Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rn 'tt_over_entr|tt_entr_ratio|rqa_ratio_tt_entr|TT_OVER_ENTR' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l
```
Then implement and run the C159 `TT/ENTR` (or collision-safe alternative) OOS script, emit ingest/registry/summary, and sync `research_state/state.yaml` to C159-done/C160-next. **Do not stop until C159 is properly complete with >=3 new artifacts and state.yaml synced. No status-only response.**

(End of file)
