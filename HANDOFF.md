# READ THIS FIRST — C144 COMPLETED / C145 NEXT (20261107T100643Z; single durable handoff)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute C145 NOW — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance/results.**

**Readiness re-verified 20261107T100443Z (still valid):** `numpy,scipy,pandas` importable; required caches present (`volume_1h_full.{pkl,meta.json,provenance.json}`, `0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.{pkl,meta.json}`); pytest unavailable (honest, `/usr/bin/python3: No module named pytest`).

## Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation: walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. Nonspot ingest is a hard blocker only if a real nonspot artifact never appears; R-B proceeds on validated `real_quote_volume` family regardless.

## Verified current state (do not rerun unchanged)
- **C104–C144 DONE → `oos_edge_proven=false` (registry lineage). Do NOT rerun.** All campaigns C104–C144 locked; `edge_claim: NONE` throughout.
- **C144 COMPLETED (20261107T100643Z):** `VOLUME_RQA_ENTR_OVER_DET_RATIO_SHOCK_MR` (RQA ratio `RATIO_ENTR_DET = ENTR / %DET`, Shannon entropy of diagonal-line length distribution normalized by diagonal-line determinism, on delay-embedded log-volume returns; `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`; ENTR natural log raw consistent with C130; fail-closed on `%DET<=0`/no qualifying diagonal lines/ENTR undefined/non-finite/offdiag-degenerate/undefined) — `oos_edge_proven=false`, `edge_claim: NONE`.
  - OOS: `reports/real_quote_volume_rqa_entr_over_det_ratio_shock_mr_costed_oos_20261107T100612Z.json` (sha `9753b043b48fe76ef18a2d6e64b1a110ec1ed2dae122dd8af6cf9c8ae3be4ee8`, `real_data_only=true`, `fail_closed=true`, `oos_edge_proven=false`, `any_exposure_oos=true`, `all_cost_slices_positive_oos_net_sum=false`, `all_cost_slices_beat_bh_mean_rule=false`; cross-asset OOS net sums `fee0_slip0=0.04844085279521926`, `fee5_slip5=-0.3805591472047811`, `fee10_slip10=-0.8095591472047813`, `fee20_slip20=-1.6675591472047813`, `fee40_slip40=-3.383559147204781`). Top-level gate fields present; refs C143 registry sha `af23e5d52e...`/C143 OOS sha `c1c0f65c...`; grep-zero `entr_over_det|entr_det_ratio|rqa_ratio_entr_det|ENTR_OVER_DET` verified before implementation/run (self-only after).
  - Ingest: `reports/real_feed_ingest_attempt_20261107T100643Z.json` (sha `7a1973a2f887f429ccde2cd4d61289c9d19a8f999ba524eaf7482c80d90ade0c`, campaign 144, nonspot blocked fail-closed, `rb_unblocked=true`).
  - Script: `scripts/run_real_quote_volume_rqa_entr_over_det_ratio_shock_mr_costed_oos.py` (sha `d4fc4156d8f06d257bbd6b9707f17aec221ec1d6ffc60f6e6650b626632be7fa`).
  - Registry superseding C143: `reports/strategy_edge_registry_20261107T100643Z.json` (sha `7eb9007e55f1610a4eb266488c9e4dc11320b88cc5cc833faefc31393f16a9fb`, supersedes `reports/strategy_edge_registry_20261107T100055Z.json` sha `af23e5d52e5a401f77dc36acdf5aa86d1cd9d5f6f7475fab4593e1b537cb35eb`).
  - Summary: `reports/campaign144_execution_summary_20261107T100643Z.json` (sha `40a8e0b86f6fe0ac5f301c2234a465b20022093a21ec7b48e6be4e65ea10273c`).
  - `research_state/state.yaml` synced: `latest_campaign_done: C144`, `next_campaign: C145`.
- Real data preconditions OK (do not re-scan/fetch): caches present as above.
- Python deps OK: `numpy, scipy, pandas` importable. pytest NOT installed; record honestly.

## Bottlenecks removed (this handoff)
- C104–C144 locked; no reruns unchanged. Carry forward latest registry `strategy_edge_registry_20261107T100643Z.json` (sha `7eb9007e55f1610a4eb266488c9e4dc11320b88cc5cc833faefc31393f16a9fb`).
- C144 completed heavy: ENTR/%DET grep-zero distinctness verified pre-run; OOS/ingest/registry/summary emitted with disk-verified SHAs; state synced.
- C145 primary pre-selected and grep-zero verified (20261107T100643Z): `VOLUME_RQA_TT_OVER_LAM_RATIO_SHOCK_MR` (`TT_mean/%LAM`).
- "No status before >=3 new artifacts" + mandatory run — forces heavy work for C145.
- pytest unavailable recorded honestly — do not fabricate test results.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## NEXT FOCUS CAMPAIGN — C145 (MANDATORY, HEAVY WORK)

**Order is non-negotiable.** C104–C144 done — do NOT rerun.

### Step 0 — Readiness + distinctness grep + implement/run (required, fail-closed)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'tt_over_lam\|tt_lam_ratio\|rqa_ratio_tt_lam\|TT_OVER_LAM' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l
```
Primary C145 candidate (pre-selected, grep-zero verified 20261107T100643Z): **`VOLUME_RQA_TT_OVER_LAM_RATIO_SHOCK_MR`** — RQA ratio `RATIO_TT_LAM = TT_mean / %LAM` (trapping time / mean vertical-line length normalized by laminarity) on delay-embedded log-volume returns (`m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`). `%LAM` = (sum of vertical-line points for qualifying vertical lines `l>=l_min`, main diagonal excluded) / (offdiag recurrence sum); `TT_mean` = mean length of qualifying vertical lines. Fail-closed NaN/no-signal if `%LAM<=0`, no qualifying vertical lines, `TT_mean` undefined/non-finite, offdiag/recurrence degenerate, or undefined. Distinct from C125–C144 (all prior RQA metrics/ratios including C127 %LAM direct, C128/C129 TT-family direct, C134 %LAM/%DET, C136 %LAM/%RR, C139 %RR/%LAM, C140 %RR/TT, C143 %LAM/TT; C145 trades inverse `TT_mean/%LAM`). **Re-verify grep at run time (must still be zero non-self). If collision, pick next distinct alternative (`VOLUME_RQA_DET_OVER_ENTR_RATIO_SHOCK_MR` `%DET/ENTR` fail-closed on `ENTR<=0`/no qualifying diagonal lines; or `VOLUME_RQA_LAM_OVER_ENTR_RATIO_SHOCK_MR` `%LAM/ENTR` fail-closed on `ENTR<=0`/no qualifying diagonal lines), re-grep, and record chosen feature + grep evidence.**

Implement script `scripts/run_real_quote_volume_rqa_tt_over_lam_ratio_shock_mr_costed_oos.py` (or chosen alternative) modeled on the correct C144/C143 scripts (copy WF/cost/B&H/SHA/report structure; change only feature computation, IDs, and `pre_stated_distinctness`/refs to latest registry `strategy_edge_registry_20261107T100643Z.json` sha `7eb9007e55f1610a4eb266488c9e4dc11320b88cc5cc833faefc31393f16a9fb` and C144 OOS sha `9753b043b48fe76ef18a2d6e64b1a110ec1ed2dae122dd8af6cf9c8ae3be4ee8`). Run it to emit `reports/real_quote_volume_rqa_<chosen>_costed_oos_<UTC>.json` with all top-level gate fields (`oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`), `edge_claim: NONE`, `real_data_only:true`, `fail_closed:true`, and `pre_stated_distinctness` recording grep cmd/hits/evidence.

### Step 1 — Ingest + registry + summary (MANDATORY)
1. Ingest: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 145) — record nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume` family.
2. Registry: `reports/strategy_edge_registry_<UTC>.json` superseding `strategy_edge_registry_20261107T100643Z.json` (sha `7eb9007e55f1610a4eb266488c9e4dc11320b88cc5cc833faefc31393f16a9fb`). Structurally consistent `campaign/supersedes/supersedes_sha256/lineage/campaigns`; include C138–C144 context/entries and add C145 with artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds.
3. Summary: `reports/campaign145_execution_summary_<UTC>.json` listing all new artifact paths + sha256 (SHAs computed from bytes on disk): OOS, ingest, registry, script.
4. Sync `research_state/state.yaml`: `latest_campaign_done: C145`, `next_campaign: C146`, latest registry sha, latest OOS path/sha, `oos_edge_proven` from emitted report, `c146_preselected` with a distinct grep-verified RQA-ratio candidate not used in C125–C145.

## Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

## Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run (C145 collision guard required; record chosen feature + grep evidence).
- **No status summary before >= 3 new concrete C145 report artifacts exist** (OOS + ingest + registry/summary).
- **Heavy work mandatory:** implement/run + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rn 'tt_over_lam\|tt_lam_ratio\|rqa_ratio_tt_lam\|TT_OVER_LAM' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l
```
Then implement and run the C145 TT/LAM (or collision-safe alternative) OOS script, emit ingest/registry/summary, and sync state.yaml to C145-done/C146-next. **Do not stop until C145 is properly complete with >=3 new artifacts and state.yaml synced. No status-only response.**
