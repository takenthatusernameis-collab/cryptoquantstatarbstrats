# READ THIS FIRST — C142 COMPLETION (20261107T095311Z; single durable handoff)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute the next focus campaign NOW — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance/results.**

**Readiness re-verified 20261107T095311Z:** `numpy,scipy,pandas` importable; required caches present (`volume_1h_full.{pkl,meta.json,provenance.json}`, `0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.{pkl,meta.json}`); pytest unavailable (honest, `/usr/bin/python3: No module named pytest`).

## Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation: walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. Nonspot ingest is a hard blocker only if a real nonspot artifact never appears; R-B proceeds on validated `real_quote_volume` family regardless.

## Verified current state (do not rerun unchanged)
- **C104–C141 DONE → `oos_edge_proven=false` (registry lineage). Do NOT rerun.** All 38 campaigns C104–C141 locked; `edge_claim: NONE` throughout. No edge proven yet across C104–C141.
- **C141 DONE (20261107T090342Z):** `VOLUME_RQA_ENTR_OVER_RR_RATIO_SHOCK_MR` (RQA ratio `RATIO_ENTR_RR = ENTR/%RR`) — `oos_edge_proven=false`, `edge_claim: NONE`. OOS: `reports/real_quote_volume_rqa_entr_over_rr_ratio_shock_mr_costed_oos_20261107T090342Z.json` (sha `2c1513ac8bf1142d622f52c5e076fa44706ad728ceb786d9fd99b74f7b66d746`, `real_data_only=true`, `fail_closed=true`, `oos_edge_proven=false`, `any_exposure_oos=true`, `all_cost_slices_positive_oos_net_sum=false`, `all_cost_slices_beat_bh_mean_rule=false`; cross-asset OOS net sums `fee0_slip0=0.45336506664510956`, `fee5_slip5=0.0503650666451092`, `fee10_slip10=-0.3526349333548909`, `fee20_slip20=-1.1586349333548909`, `fee40_slip40=-2.7706349333548905`). Registry superseding C140: `reports/strategy_edge_registry_20261107T090342Z.json` (sha `0fcfc9410fadb171b621a959029dccb4ec891fc8dd2543d3f7c1db8252706fa4`).
- **C142 ATTEMPTED but FLAWED — must be properly completed (THIS SESSION):**
  - Script `scripts/run_real_quote_volume_rqa_det_over_tt_ratio_shock_mr_costed_oos.py` correctly implements `VOLUME_RQA_DET_OVER_TT_RATIO_SHOCK_MR` (RQA ratio `%DET/TT_mean`, `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`, fail-closed on `TT_mean<=0`/no qualifying vertical lines/`%DET` undefined/non-finite/offdiag-degenerate/undefined). Script content is CORRECT — do not rewrite logic.
  - On-disk OOS report `reports/real_quote_volume_rqa_det_over_tt_ratio_shock_mr_costed_oos_20261107T090953Z.json` is **WRONG**: its `candidate`, `feature_definition`, and `pre_stated_distinctness` describe C141's `ENTR/%RR`, not DET/TT, and it is missing top-level gate fields (`oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`). **REGENERATE by running the correct script** — it emits a proper DET/TT report with all top-level gate fields.
  - Ingest report `reports/real_feed_ingest_attempt_20261107T091027Z.json` exists (campaign 142, nonspot blocked, `rb_unblocked=true`).
  - **C142 registry MISSING** — must be created superseding `reports/strategy_edge_registry_20261107T090342Z.json` (sha `0fcfc9410fadb171b621a959029dccb4ec891fc8dd2543d3f7c1db8252706fa4`).
  - Summary `reports/campaign142_execution_summary_20261107T091029Z.json` exists but lists only 2 artifacts (OOS + ingest); must include the registry artifact after creation.
  - `research_state/state.yaml` still says `latest_campaign_done: C141`, `next_campaign: C142` — accurate that C141 is done, but C142 is NOT properly complete. Sync after C142 completion.
- Real data preconditions OK (do not re-scan/fetch): caches present as above.
- Python deps OK: `numpy, scipy, pandas` importable. pytest NOT installed; record honestly.

## Bottlenecks removed (this handoff)
- C104–C141 locked; no reruns unchanged. Carry forward latest registry `strategy_edge_registry_20261107T090342Z.json` (sha `0fcfc9410fadb171b621a959029dccb4ec891fc8dd2543d3f7c1db8252706fa4`).
- **C142 OOS report flaw identified:** on-disk report has C141 ENTR/%RR content and missing top-level gates. Remedy: rerun the existing correct DET/TT script to regenerate the OOS report. No script rewrite needed.
- **C142 registry missing:** create `reports/strategy_edge_registry_<UTC>.json` superseding C141 registry; include C138–C142 context/entries; `edge_claim: NONE` unless fail-closed edge rule holds.
- **state.yaml stale:** sync to `latest_campaign_done: C142`, `next_campaign: C143`, latest registry sha after C142 completion.
- "No status before >=3 new artifacts" + mandatory run — forces heavy work.
- pytest unavailable recorded honestly — do not fabricate test results.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## NEXT FOCUS CAMPAIGN — C142 COMPLETION (MANDATORY, HEAVY WORK)

**Order is non-negotiable.** C104–C141 done — do NOT rerun. C142 must be properly completed.

### Step 0 — Readiness + confirm flaw + regenerate OOS report (required, fail-closed)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
# confirm on-disk C142 OOS report has WRONG C141 ENTR/%RR content (candidate/feature_definition/pre_stated_distinctness) and missing top-level gates
python3 scripts/run_real_quote_volume_rqa_det_over_tt_ratio_shock_mr_costed_oos.py
```
Regenerate `reports/real_quote_volume_rqa_det_over_tt_ratio_shock_mr_costed_oos_<UTC>.json`. The script already emits correct `campaign:142`, `strategy_id: VOLUME_RQA_DET_OVER_TT_RATIO_SHOCK_MR`, correct DET/TT `feature_definition`, correct `pre_stated_distinctness` (grep `det_over_tt|det_tt_ratio|rqa_ratio_det_tt|DET_OVER_TT` zero), and top-level gate fields. Verify emitted JSON has `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`, `edge_claim: NONE`, `references` to C141 registry sha `0fcfc941...` and C141 OOS sha `2c1513ac...`. Record grep-zero in `pre_stated_distinctness`.

### Step 1 — Registry + summary (MANDATORY)
1. Registry: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261107T090342Z.json` (sha `0fcfc9410fadb171b621a959029dccb4ec891fc8dd2543d3f7c1db8252706fa4`). Structurally consistent `campaign/supersedes/supersedes_sha256/lineage/entries/campaigns`; include C138–C141 context/entries and add C142 with artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds.
2. Summary: `reports/campaign142_execution_summary_<UTC>.json` listing all new artifact paths + sha256 (SHAs computed from bytes on disk): OOS report, ingest report, registry, script.
3. Sync `research_state/state.yaml`: `latest_campaign_done: C142`, `next_campaign: C143`, latest registry sha, latest OOS path/sha, `oos_edge_proven` from emitted report.

### Step 2 — C143 pre-selection (after C142 complete; grep-verify before implementation)
After C142 is properly done, C143 is next. Pre-select a distinct RQA-ratio candidate on delay-embedded log-volume returns (e.g. a ratio not yet used among C125–C142: `%DET`,`TT`,`%LAM`,`ENTR`,`%RR`,`%DET/%RR`,`%LAM/%DET`,`%LAM/%RR`,`%RR/%DET`,`%DET/%LAM`,`%RR/%LAM`,`%RR/TT`,`ENTR/%RR`,`%DET/TT_mean`). Grep-verify zero hits in `scripts/ strategies/ backtest/ utils/` before implementation; record chosen feature + grep evidence; justify distinctness in OOS `pre_stated_distinctness`. Fail-closed edge rule identical.

## Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

## Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run (C142 collision guard required; record chosen feature + grep evidence).
- **No status summary before >= 3 new concrete C142 report artifacts exist** (OOS + ingest + registry/summary counting as concrete artifacts).
- **Heavy work mandatory:** run/implement as needed + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
python3 scripts/run_real_quote_volume_rqa_det_over_tt_ratio_shock_mr_costed_oos.py
```
Then create C142 registry superseding C141, update summary, sync state.yaml to C142-done/C143-next. **Do not stop until C142 is properly complete with >=3 new artifacts and state.yaml synced. No status-only response.**
