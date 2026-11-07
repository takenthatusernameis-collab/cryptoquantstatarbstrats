# READ THIS FIRST — C145 COMPLETED / C146 NEXT (20261107T101505Z; single durable handoff)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute C146 NOW — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance/results.**

**Readiness re-verified 20261107T101505Z (still valid):** `numpy,scipy,pandas` importable; required caches present (`volume_1h_full.{pkl,meta.json,provenance.json}`, `0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.{pkl,meta.json}`); pytest unavailable (honest, `/usr/bin/python3: No module named pytest`). Grep-zero re-confirmed for C146 primary `DET_OVER_ENTR` (0 hits in scripts/ strategies/ backtest/ utils/). C146 script/artifacts NOT yet present — C146 is NOT started.

## Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation: walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. Nonspot ingest is a hard blocker only if a real nonspot artifact never appears; R-B proceeds on validated `real_quote_volume` family regardless.

## Verified current state (do not rerun unchanged)
- **C104–C145 DONE → `oos_edge_proven=false` (registry lineage). Do NOT rerun.** All campaigns C104–C145 locked; `edge_claim: NONE` throughout.
- **C145 COMPLETED (20261107T101205Z):** `VOLUME_RQA_TT_OVER_LAM_RATIO_SHOCK_MR` (RQA ratio `RATIO_TT_LAM = TT_mean / %LAM`, trapping time / mean vertical-line length normalized by laminarity, on delay-embedded log-volume returns; `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`; fail-closed on `%LAM<=0`/no qualifying vertical lines/TT_mean undefined/non-finite/offdiag-degenerate/undefined) — `oos_edge_proven=false`, `edge_claim: NONE`.
  - OOS: `reports/real_quote_volume_rqa_tt_over_lam_ratio_shock_mr_costed_oos_20261107T101205Z.json` (sha `5d38cc6eb608083cd13c57fadfdab73e75e4e66d61af6ae56d9b93ec2782a263`, `real_data_only=true`, `fail_closed=true`, `oos_edge_proven=false`, `any_exposure_oos=true`, `all_cost_slices_positive_oos_net_sum=false`, `all_cost_slices_beat_bh_mean_rule=false`; cross-asset OOS net sums `fee0_slip0=0.23939876661422843`, `fee5_slip5=-0.05060123338577183`, `fee10_slip10=-0.340601233385772`, `fee20_slip20=-0.9206012333857718`, `fee40_slip40=-2.0806012333857717`). Top-level gate fields present; refs C144 registry sha `7eb9007e55f1610a4eb266488c9e4dc11320b88cc5cc833faefc31393f16a9fb`/C144 OOS sha `9753b043b48fe76ef18a2d6e64b1a110ec1ed2dae122dd8af6cf9c8ae3be4ee8`; grep-zero `tt_over_lam|tt_lam_ratio|rqa_ratio_tt_lam|TT_OVER_LAM` verified before implementation/run (self-only after).
  - Ingest: `reports/real_feed_ingest_attempt_20261107T101205Z.json` (sha `b06810dfab1498b282b4ace853f92fbf7558cdb677672235488a9673c8d57b10`, campaign 145, nonspot blocked fail-closed, `rb_unblocked=true`).
  - Script: `scripts/run_real_quote_volume_rqa_tt_over_lam_ratio_shock_mr_costed_oos.py` (sha `401678c9f333ebb53cc4f5b364d9ead4a4097f8f911999f79e38e03728dcfb4d`).
  - Registry superseding C144: `reports/strategy_edge_registry_20261107T101205Z.json` (sha `7d943c4b8547a978af26af4659ee84d95f4587df007e19a9dbfe1dea940a5d20`, supersedes `reports/strategy_edge_registry_20261107T100643Z.json` sha `7eb9007e55f1610a4eb266488c9e4dc11320b88cc5cc833faefc31393f16a9fb`).
  - Summary: `reports/campaign145_execution_summary_20261107T101205Z.json` (sha `85ab59e6698af05ada5fecfcffe324658e6dc337e70c1c66b4ccc005170c2066`).
  - `research_state/state.yaml` synced: `latest_campaign_done: C145`, `next_campaign: C146`.
- Real data preconditions OK (do not re-scan/fetch): caches present as above.
- Python deps OK: `numpy, scipy, pandas` importable. pytest NOT installed; record honestly.

## Bottlenecks removed (this handoff)
- C104–C145 locked; no reruns unchanged. Carry forward latest registry `strategy_edge_registry_20261107T101205Z.json` (sha `7d943c4b8547a978af26af4659ee84d95f4587df007e19a9dbfe1dea940a5d20`).
- C145 completed heavy: TT_mean/%LAM grep-zero distinctness verified pre-run; OOS/ingest/registry/summary emitted with disk-verified SHAs; state synced.
- C146 primary pre-selected and grep-zero verified (20261107T101205Z): `VOLUME_RQA_DET_OVER_ENTR_RATIO_SHOCK_MR` (`%DET/ENTR`).
- "No status before >=3 new artifacts" + mandatory run — forces heavy work for C146.
- pytest unavailable recorded honestly — do not fabricate test results.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## NEXT FOCUS CAMPAIGN — C146 (MANDATORY, HEAVY WORK)

**Order is non-negotiable.** C104–C145 done — do NOT rerun.

### Step 0 — Readiness + distinctness grep + implement/run (required, fail-closed)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'det_over_entr\|det_entr_ratio\|rqa_ratio_det_entr\|DET_OVER_ENTR' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l
```
Primary C146 candidate (pre-selected, grep-zero verified 20261107T101205Z): **`VOLUME_RQA_DET_OVER_ENTR_RATIO_SHOCK_MR`** — RQA ratio `RATIO_DET_ENTR = %DET / ENTR` (determinism normalized by diagonal-line Shannon entropy) on delay-embedded log-volume returns (`m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`). `%DET` = (sum of diagonal-line points for qualifying diagonal lines `l>=l_min`, main diagonal excluded) / (offdiag recurrence sum). `ENTR` = -sum p(l)*ln(p(l)) over qualifying diagonal lines (natural log raw, C130-consistent). Fail-closed NaN/no-signal if `ENTR<=0`, no qualifying diagonal lines, `%DET` undefined/non-finite, offdiag/recurrence degenerate, or undefined. Distinct from C125–C145 (all prior RQA metrics/ratios including C130 ENTR direct, C131–C135 DET-family context, C141 ENTR/%RR, C144 ENTR/%DET; C146 trades inverse `%DET/ENTR`). **Re-verify grep at run time (must still be zero non-self). If collision, pick next distinct alternative (`VOLUME_RQA_LAM_OVER_ENTR_RATIO_SHOCK_MR` `%LAM/ENTR` fail-closed on `ENTR<=0`/no qualifying diagonal lines; or `VOLUME_RQA_ENTR_OVER_LAM_RATIO_SHOCK_MR` `ENTR/%LAM` fail-closed on `%LAM<=0`/no qualifying vertical lines), re-grep, and record chosen feature + grep evidence.**

Implement script `scripts/run_real_quote_volume_rqa_det_over_entr_ratio_shock_mr_costed_oos.py` (or chosen alternative) modeled on the correct C145/C144 scripts (copy WF/cost/B&H/SHA/report structure; change only feature computation, IDs, and `pre_stated_distinctness`/refs to latest registry `strategy_edge_registry_20261107T101205Z.json` sha `7d943c4b8547a978af26af4659ee84d95f4587df007e19a9dbfe1dea940a5d20` and C145 OOS sha `5d38cc6eb608083cd13c57fadfdab73e75e4e66d61af6ae56d9b93ec2782a263`). Run it to emit `reports/real_quote_volume_rqa_<chosen>_costed_oos_<UTC>.json` with all top-level gate fields (`oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`), `edge_claim: NONE`, `real_data_only:true`, `fail_closed:true`, and `pre_stated_distinctness` recording grep cmd/hits/evidence.

### Step 1 — Ingest + registry + summary (MANDATORY)
1. Ingest: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 146) — record nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume` family.
2. Registry: `reports/strategy_edge_registry_<UTC>.json` superseding `strategy_edge_registry_20261107T101205Z.json` (sha `7d943c4b8547a978af26af4659ee84d95f4587df007e19a9dbfe1dea940a5d20`). Structurally consistent `campaign/supersedes/supersedes_sha256/lineage/campaigns`; include C139–C145 context/entries and add C146 with artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds.
3. Summary: `reports/campaign146_execution_summary_<UTC>.json` listing all new artifact paths + sha256 (SHAs computed from bytes on disk): OOS, ingest, registry, script.
4. Sync `research_state/state.yaml`: `latest_campaign_done: C146`, `next_campaign: C147`, latest registry sha, latest OOS path/sha, `oos_edge_proven` from emitted report, `c147_preselected` with a distinct grep-verified RQA-ratio candidate not used in C125–C146.

## Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

## Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run (C146 collision guard required; record chosen feature + grep evidence).
- **No status summary before >= 3 new concrete C146 report artifacts exist** (OOS + ingest + registry/summary).
- **Heavy work mandatory:** implement/run + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rn 'det_over_entr\|det_entr_ratio\|rqa_ratio_det_entr\|DET_OVER_ENTR' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l
```
Then implement and run the C146 DET/ENTR (or collision-safe alternative) OOS script, emit ingest/registry/summary, and sync state.yaml to C146-done/C147-next. **Do not stop until C146 is properly complete with >=3 new artifacts and state.yaml synced. No status-only response.**
