# READ THIS FIRST — SINGLE DURABLE HANDOFF (20261107T130248Z)

Repo: `cryptoquantstatarbstrats` (crypto quant stat arb strategies).
**Prioritization (from repo name):** fail-closed, real-data-only stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. R-B proceeds on validated `real_quote_volume` regardless of nonspot ingest.

## INITIAL TASK FOR NEXT SESSION — C160 (MANDATORY, HEAVY WORK, START NOW)

C104–C159 DONE — do NOT rerun. `pytest` unavailable (honestly recorded — do not fabricate test results). `numpy/scipy/pandas` importable (verified 20261107T130032Z). Caches present (`data/cache/volume_1h_full.{pkl,meta.json,provenance.json}`, `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.{pkl,meta.json}`).

**Readiness (run first, fail-closed):**
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'trend_over_lmax\|trend_lmax_ratio\|rqa_ratio_trend_lmax\|TREND_OVER_LMAX' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l   # must be 0 non-self (re-verified 20261107T130248Z: 0)
```

**Primary C160 candidate (pre-selected — re-verify grep at run time):** `VOLUME_RQA_TREND_OVER_LMAX_RATIO_SHOCK_MR` — RQA ratio `RATIO_TREND_LMAX = TREND / L_max` (RQA TREND = linear regression slope of recurrence point displacement along diagonals, normalized by max diagonal line length) on delay-embedded log-volume returns (`m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`). Compute TREND over qualifying diagonal-line recurrence points (k!=0, main diagonal excluded) using a standard, causal, well-defined formulation; `L_max` = max length of qualifying diagonal lines (`l>=l_min`). Fail-closed NaN/no-signal if `L_max<=0` or undefined/non-finite, `TREND` undefined/non-finite (insufficient qualifying diagonal points / regression degenerate), no qualifying diagonal lines, offdiag/recurrence degenerate, or undefined. Distinct from C125–C159 (incl C159 `TT/ENTR`, C158 `%LAM/L_max`, C157 `RR/ENTR`, C156 `RR/L_max`, C155 `ENTR/L_max`, C154 `L_max/TT`, C153 `ENTR/TT`). **Re-verify grep at run time (collision guard). `RR/LAM` is NOT a safe primary (C139 script/refs exist). If TREND/LMAX collides, pick next distinct grep-zero alternative (`LMAX/TREND` with fail-closed on `TREND==0/undefined`, or `TREND/ENTR` with fail-closed on `ENTR<=0/undefined/TREND` undefined), re-grep, and record chosen feature + grep evidence.**

Implement `scripts/run_real_quote_volume_rqa_trend_over_lmax_ratio_shock_mr_costed_oos.py` (or chosen alternative) modeled on C159/C158 scripts (copy WF/cost/B&H/SHA/report structure; change only feature computation, IDs, `pre_stated_distinctness`/refs to latest registry `strategy_edge_registry_20261107T130248Z.json` sha `5bbcc636054598db03cb34919db8a6e3e3fad86c73b02d36a90b7c6996176731` and C159 OOS sha `a1c7fdfe6e7f3148103e67a317fafbc9787d9bf4ec017d478fd2b2c30ddfa21a`). Run it to emit `reports/real_quote_volume_rqa_trend_over_lmax_ratio_shock_mr_costed_oos_<UTC>.json` with all top-level gate fields (`oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`), `edge_claim: NONE`, `real_data_only:true`, `fail_closed:true`, and `pre_stated_distinctness` recording grep cmd/hits/evidence.

### Step 1 — Ingest + registry + summary (MANDATORY)
1. Ingest: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 160) — record nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume` family.
2. Registry: `reports/strategy_edge_registry_<UTC>.json` superseding `strategy_edge_registry_20261107T130248Z.json` (sha `5bbcc636054598db03cb34919db8a6e3e3fad86c73b02d36a90b7c6996176731`). Structurally consistent `campaign/supersedes/supersedes_sha256/lineage/campaigns`; include prior context and add C160 with artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds. **Do not blindly copy stale preselected candidates — verify grep for C161 preselection.**
3. Summary: `reports/campaign160_execution_summary_<UTC>.json` listing all new artifact paths + sha256 (SHAs computed from bytes on disk): OOS, ingest, registry, script.
4. Sync `research_state/state.yaml`: `latest_campaign_done: C160`, `next_campaign: C161`, latest registry sha, latest OOS path/sha, `oos_edge_proven` from emitted report, `c161_preselected` with a distinct grep-verified RQA-ratio candidate not used in C125–C160.

## Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

## Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run (C160 collision guard required; record chosen feature + grep evidence). `RR/LAM` has existing collisions — do not reuse.
- **No status summary before >= 3 new concrete C160 report artifacts exist** (OOS + ingest + registry/summary).
- **Heavy work mandatory:** implement/run + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## Bottlenecks removed (confirmed 20261107T130248Z)
- C104–C159 locked; no reruns unchanged.
- C159 completed heavy; all artifacts emitted with disk-verified SHAs; state.yaml/HANDOFF synced to C159-done/C160-next.
- `numpy/scipy/pandas` importable (verified 20261107T130032Z).
- C159 primary `TT/ENTR` collision guard grep = 0 hits (verified 20261107T130032Z). C160 primary `TREND/LMAX` grep = 0 hits (verified 20261107T130248Z). **`RR/LAM` rejected (C139 collisions exist).**
- `"No status before >=3 new artifacts"` + mandatory run — forces heavy work for C160.
- `pytest` unavailable recorded honestly — do not fabricate test results.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## C159 result (locked, do not rerun)
- `VOLUME_RQA_TT_OVER_ENTR_RATIO_SHOCK_MR` (TT_mean/ENTR), campaign 159, `oos_edge_proven:false`, `edge_claim:NONE`.
- OOS: `reports/real_quote_volume_rqa_tt_over_entr_ratio_shock_mr_costed_oos_20261107T130151Z.json` (sha `a1c7fdfe6e7f3148103e67a317fafbc9787d9bf4ec017d478fd2b2c30ddfa21a`). `any_exposure_oos:true`; cross-asset net sums `fee0=-0.006638762007552312, fee5=-0.38763876200755265, fee10=-0.7686387620075528, fee20=-1.5306387620075526, fee40=-3.0546387620075524`; `all_cost_slices_positive_oos_net_sum:false`; `all_cost_slices_beat_bh_mean_rule:false`.
- Ingest: `reports/real_feed_ingest_attempt_20261107T130248Z.json` (sha `d8317398411ffd5f5227f445e20b365ad1c80a6e06593274c4df24bd858277d8`).
- Registry: `reports/strategy_edge_registry_20261107T130248Z.json` (sha `5bbcc636054598db03cb34919db8a6e3e3fad86c73b02d36a90b7c6996176731`, supersedes C158 `3de80723ef0eb0de7834aa45e31bfab358c0b4dfe0c0ea159d2b3fc5f4e913c4`).
- Summary: `reports/campaign159_execution_summary_20261107T130248Z.json` (sha `ca573b975523037abb0d95ab846b806b781a9607e6543deadd3c4a321baf6e8c`).
- Script: `scripts/run_real_quote_volume_rqa_tt_over_entr_ratio_shock_mr_costed_oos.py` (sha `09465a36175790a2fe63b1853ce3e88045145c16915640fc8d23edc9d0ed1318`). Distinctness grep hits pre (non-self)=0.

## Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rn 'trend_over_lmax\|trend_lmax_ratio\|rqa_ratio_trend_lmax\|TREND_OVER_LMAX' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l
```
Then implement and run the C160 `TREND/LMAX` (or collision-safe alternative) OOS script, emit ingest/registry/summary, and sync `research_state/state.yaml` to C160-done/C161-next. **Do not stop until C160 is properly complete with >=3 new artifacts and state.yaml synced. No status-only response.**

(End of file)
