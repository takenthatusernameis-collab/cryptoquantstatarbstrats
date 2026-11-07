# READ THIS FIRST — C143 COMPLETED / C144 NEXT (20261107T100055Z; single durable handoff)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute C144 NOW — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance/results.**

**Readiness re-verified 20261107T095311Z (still valid):** `numpy,scipy,pandas` importable; required caches present (`volume_1h_full.{pkl,meta.json,provenance.json}`, `0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.{pkl,meta.json}`); pytest unavailable (honest, `/usr/bin/python3: No module named pytest`).

## Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation: walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. Nonspot ingest is a hard blocker only if a real nonspot artifact never appears; R-B proceeds on validated `real_quote_volume` family regardless.

## Verified current state (do not rerun unchanged)
- **C104–C143 DONE → `oos_edge_proven=false` (registry lineage). Do NOT rerun.** All campaigns C104–C143 locked; `edge_claim: NONE` throughout.
- **C143 COMPLETED (20261107T100055Z):** `VOLUME_RQA_LAM_OVER_TT_RATIO_SHOCK_MR` (RQA ratio `RATIO_LAM_TT = %LAM / TT_mean`, laminarity normalized by trapping time/mean vertical-line length, on delay-embedded log-volume returns; `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`; fail-closed on `TT_mean<=0`/no qualifying vertical lines/`%LAM` undefined/non-finite/offdiag-degenerate/undefined) — `oos_edge_proven=false`, `edge_claim: NONE`.
  - OOS: `reports/real_quote_volume_rqa_lam_over_tt_ratio_shock_mr_costed_oos_20261107T100021Z.json` (sha `c1c0f65ccb1c8c58edd69879ee5eccef5ad05378cb67507286aec5af379848ee`, `real_data_only=true`, `fail_closed=true`, `oos_edge_proven=false`, `any_exposure_oos=true`, `all_cost_slices_positive_oos_net_sum=false`, `all_cost_slices_beat_bh_mean_rule=false`; cross-asset OOS net sums `fee0_slip0=-0.2115488053129173`, `fee5_slip5=-0.5445488053129176`, `fee10_slip10=-0.8775488053129177`, `fee20_slip20=-1.5435488053129176`, `fee40_slip40=-2.875548805312917`). Top-level gate fields present; refs C142 registry sha `adf7d58ad...`/C142 OOS sha `bbdba5d6...`; grep-zero `lam_over_tt|lam_tt_ratio|rqa_ratio_lam_tt|LAM_OVER_TT` verified before implementation/run.
  - Ingest: `reports/real_feed_ingest_attempt_20261107T100055Z.json` (sha `6aad7ec15cd64970474db8c0c68a3e835419acfd69aa2922da413defadb7d782`, campaign 143, nonspot blocked fail-closed, `rb_unblocked=true`).
  - Script: `scripts/run_real_quote_volume_rqa_lam_over_tt_ratio_shock_mr_costed_oos.py` (sha `3e7a9aa048a54baab921edb9884700aca32b67c91d7f90fac13c7fcec88bdc15`).
  - Registry superseding C142: `reports/strategy_edge_registry_20261107T100055Z.json` (sha `af23e5d52e5a401f77dc36acdf5aa86d1cd9d5f6f7475fab4593e1b537cb35eb`, supersedes `reports/strategy_edge_registry_20261107T095654Z.json` sha `adf7d58adb4151dab1769d739d938311131d955bf190221fae4a6afb0e9e2e72`).
  - Summary: `reports/campaign143_execution_summary_20261107T100055Z.json` (sha `deab82d05c4353e53a9a7014c0754b9b39a4b4d623ac0bccd3353abda352e928`).
  - `research_state/state.yaml` synced: `latest_campaign_done: C143`, `next_campaign: C144`.
- Real data preconditions OK (do not re-scan/fetch): caches present as above.
- Python deps OK: `numpy, scipy, pandas` importable. pytest NOT installed; record honestly.

## Bottlenecks removed (this handoff)
- C104–C143 locked; no reruns unchanged. Carry forward latest registry `strategy_edge_registry_20261107T100055Z.json` (sha `af23e5d52e5a401f77dc36acdf5aa86d1cd9d5f6f7475fab4593e1b537cb35eb`).
- C143 completed heavy: LAM/TT grep-zero distinctness verified pre-run; OOS/ingest/registry/summary emitted with disk-verified SHAs; state synced.
- C144 primary pre-selected and grep-zero verified (20261107T100055Z): `VOLUME_RQA_ENTR_OVER_DET_RATIO_SHOCK_MR` (`ENTR/%DET`).
- "No status before >=3 new artifacts" + mandatory run — forces heavy work for C144.
- pytest unavailable recorded honestly — do not fabricate test results.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## NEXT FOCUS CAMPAIGN — C144 (MANDATORY, HEAVY WORK)

**Order is non-negotiable.** C104–C143 done — do NOT rerun.

### Step 0 — Readiness + distinctness grep + implement/run (required, fail-closed)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'entr_over_det\|entr_det_ratio\|rqa_ratio_entr_det\|ENTR_OVER_DET' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l
```
Primary C144 candidate (pre-selected, grep-zero verified 20261107T100055Z): **`VOLUME_RQA_ENTR_OVER_DET_RATIO_SHOCK_MR`** — RQA ratio `RATIO_ENTR_DET = ENTR / %DET` (Shannon entropy of diagonal-line length distribution, natural log raw consistent with C130, normalized by diagonal-line determinism) on delay-embedded log-volume returns (`m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`). ENTR = `-sum p(l)*ln(p(l))` over qualifying diagonal lines `l>=l_min` (main diagonal excluded, `k!=0`), `p(l)=n(l)/N`; `%DET` = (sum of diagonal-line points for qualifying diagonal lines) / (offdiag recurrence sum). Fail-closed NaN/no-signal if `%DET<=0`, no qualifying diagonal lines (`N==0`), ENTR undefined/non-finite, offdiag/recurrence degenerate, or undefined. Distinct from C125–C143 (all prior RQA metrics/ratios including C130 ENTR direct, C141 ENTR/%RR, C142 %DET/TT, C143 %LAM/TT). **Re-verify grep at run time (must still be zero non-self). If collision, pick next distinct alternative (`VOLUME_RQA_ENTR_OVER_LAM_RATIO_SHOCK_MR` ENTR/%LAM fail-closed on %LAM<=0/no qualifying vertical lines; or `VOLUME_RQA_TT_OVER_LAM_RATIO_SHOCK_MR` explicit `TT_mean/%LAM` fail-closed on %LAM<=0), re-grep, and record chosen feature + grep evidence.**

Implement script `scripts/run_real_quote_volume_rqa_entr_over_det_ratio_shock_mr_costed_oos.py` (or chosen alternative) modeled on the correct C143/C142 scripts (copy WF/cost/B&H/SHA/report structure; change only feature computation, IDs, and `pre_stated_distinctness`/refs to latest registry `strategy_edge_registry_20261107T100055Z.json` sha `af23e5d52e5a401f77dc36acdf5aa86d1cd9d5f6f7475fab4593e1b537cb35eb` and C143 OOS sha `c1c0f65ccb1c8c58edd69879ee5eccef5ad05378cb67507286aec5af379848ee`). Run it to emit `reports/real_quote_volume_rqa_<chosen>_costed_oos_<UTC>.json` with all top-level gate fields (`oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`), `edge_claim: NONE`, `real_data_only:true`, `fail_closed:true`, and `pre_stated_distinctness` recording grep cmd/hits/evidence.

### Step 1 — Ingest + registry + summary (MANDATORY)
1. Ingest: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 144) — record nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume` family.
2. Registry: `reports/strategy_edge_registry_<UTC>.json` superseding `strategy_edge_registry_20261107T100055Z.json` (sha `af23e5d52e5a401f77dc36acdf5aa86d1cd9d5f6f7475fab4593e1b537cb35eb`). Structurally consistent `campaign/supersedes/supersedes_sha256/lineage/entries/campaigns`; include C138–C143 context/entries and add C144 with artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds.
3. Summary: `reports/campaign144_execution_summary_<UTC>.json` listing all new artifact paths + sha256 (SHAs computed from bytes on disk): OOS, ingest, registry, script.
4. Sync `research_state/state.yaml`: `latest_campaign_done: C144`, `next_campaign: C145`, latest registry sha, latest OOS path/sha, `oos_edge_proven` from emitted report, `c145_preselected` with a distinct grep-verified RQA-ratio candidate not used in C125–C144.

## Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

## Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run (C144 collision guard required; record chosen feature + grep evidence).
- **No status summary before >= 3 new concrete C144 report artifacts exist** (OOS + ingest + registry/summary).
- **Heavy work mandatory:** implement/run + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rn 'entr_over_det\|entr_det_ratio\|rqa_ratio_entr_det\|ENTR_OVER_DET' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l
```
Then implement and run the C144 ENTR/DET (or collision-safe alternative) OOS script, emit ingest/registry/summary, and sync state.yaml to C144-done/C145-next. **Do not stop until C144 is properly complete with >=3 new artifacts and state.yaml synced. No status-only response.**
